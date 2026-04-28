#!/usr/bin/env python3
"""
crazy-professor picker — deterministic stochastic element selection.

Reads field-notes.md (last 10 Log table rows), applies anti-streak guards,
emits one JSON object on stdout per invocation.

Usage:
    picker.py --field-notes <path> --words <path> --retired <path> [options]

Modes:
    --mode single         (default) one archetype/word/operator pick
    --mode chat           four parallel picks (one per archetype)

Options:
    --init-template <path>    if field-notes file is missing, copy this template there first
    --force-archetype <name>  bypass the mod-4 picker (sets re_rolled=forced-archetype)
    --force-timestamp <iso>   override UTC timestamp (testing only)

Exit codes:
    0  success — JSON written to stdout
    1  usage error / unreadable input
    2  empty word pool (all words filtered by retired list)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import re
import shutil
import sys
from pathlib import Path

ARCHETYPES = (
    "first-principles-jester",
    "labyrinth-librarian",
    "systems-alchemist",
    "radagast-brown",
)
BASE_OPERATORS = ("reversal", "exaggeration", "escape")
WISHFUL_OPERATOR = "wishful-thinking"
OPERATORS = BASE_OPERATORS  # kept for backward-compat -- variation_guard etc. read this name
LOG_TABLE_HEADER_RE = re.compile(r"^\|\s*#\s*\|\s*Timestamp", re.IGNORECASE)
LOG_TABLE_ROW_RE = re.compile(r"^\|\s*\d+\s*\|")


def read_word_pool(words_path: Path, retired_path: Path) -> list[str]:
    """Return active provocation words (pool minus retired)."""
    pool = [
        line.strip()
        for line in words_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    retired: set[str] = set()
    if retired_path.exists():
        retired = {
            line.strip()
            for line in retired_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        }
    return [w for w in pool if w not in retired]


def read_last_log_rows(field_notes: Path, n: int = 10) -> list[dict]:
    """Parse the last n rows of the Log table into dicts. Empty list if no table."""
    if not field_notes.exists():
        return []
    text = field_notes.read_text(encoding="utf-8")
    in_log = False
    rows: list[list[str]] = []
    for line in text.splitlines():
        if not in_log and LOG_TABLE_HEADER_RE.match(line):
            in_log = True
            continue
        if in_log and LOG_TABLE_ROW_RE.match(line):
            cells = [c.strip() for c in line.strip("|").split("|")]
            rows.append(cells)
        elif in_log and line.startswith("##"):
            break
    columns = ("num", "timestamp", "archetype", "word", "operator", "slug",
               "output", "re_rolled", "kept", "retire", "voice_off", "votum")
    parsed = []
    for row in rows[-n:]:
        cells = (row + [""] * len(columns))[: len(columns)]
        parsed.append(dict(zip(columns, cells)))
    return parsed


def normalize_archetype(raw: str) -> str:
    """Strip suffixes like ' (forced)' and 'all-4 (chat-mode)' wrappers."""
    raw = raw.split(" (")[0].strip()
    return raw


def pick_operator_with_share(seed_ts: dt.datetime, wishful_share: float) -> str:
    """Pick a PO operator using random.choices with relative weights.

    wishful_share semantics:
      - 0.0 (or below): only the 3 base operators (reversal/exaggeration/escape).
      - >0.0: 4 operators with weights [1, 1, 1, share*3].
        At share=0.333 each operator is ~25%. At share=1.0 each is exactly 25%.
        At share=0.25 (default since v0.11.0) wishful is ~14%, others ~28.6%.

    Determinism: random.choices is seeded with the timestamp microseconds
    so the same timestamp produces the same operator pick (matches the
    rest of the picker's mod-based determinism).
    """
    if wishful_share <= 0.0:
        idx = seed_ts.second % 3
        return BASE_OPERATORS[idx]
    rng = random.Random(seed_ts.microsecond + seed_ts.second * 1000)
    operators = list(BASE_OPERATORS) + [WISHFUL_OPERATOR]
    weights = [1.0, 1.0, 1.0, wishful_share * 3.0]
    return rng.choices(operators, weights=weights, k=1)[0]


def picker_seed(ts: dt.datetime, offset_seconds: int = 0,
                wishful_share: float = 0.0) -> tuple[str, str, str]:
    """Deterministic mod-based picker for archetype/operator and a word index seed."""
    seed_ts = ts + dt.timedelta(seconds=offset_seconds)
    archetype = ARCHETYPES[seed_ts.minute % 4]
    operator = pick_operator_with_share(seed_ts, wishful_share)
    return archetype, operator, seed_ts.isoformat().replace("+00:00", "Z")


def variation_guard(
    archetype: str,
    word: str,
    last_rows: list[dict],
    available_words: list[str],
    seed_ts: dt.datetime,
) -> tuple[str, str, str]:
    """Apply anti-streak rules. Returns (archetype, word, re_rolled)."""
    re_rolled = "no"
    last_archetypes = [normalize_archetype(r["archetype"]) for r in last_rows]
    if last_archetypes[-3:] == [archetype] * 3 and len(last_archetypes) >= 3:
        candidates = [a for a in ARCHETYPES if a != archetype]
        # tie-break: least recently seen, then alphabetical
        seen_recency = {a: -1 for a in candidates}
        for i, prev in enumerate(reversed(last_archetypes)):
            if prev in seen_recency and seen_recency[prev] == -1:
                seen_recency[prev] = i
        candidates.sort(key=lambda a: (seen_recency[a] if seen_recency[a] >= 0 else 1e9, a))
        archetype = candidates[0]
        re_rolled = "archetype"

    last_words = {r["word"].split(" (")[0] for r in last_rows}
    if word in last_words:
        remaining = [w for w in available_words if w not in last_words and w != word]
        if remaining:
            idx = (seed_ts.microsecond + len(last_rows)) % len(remaining)
            word = remaining[idx]
            re_rolled = "both" if re_rolled == "archetype" else "word"
        # else: pool exhausted, accept original word; re_rolled stays as-is

    return archetype, word, re_rolled


def pick_word(available_words: list[str], seed_ts: dt.datetime, offset: int = 0) -> str:
    """Deterministic word pick from microseconds + offset."""
    idx = (seed_ts.microsecond + offset) % len(available_words)
    return available_words[idx]


def pick_single(args, words: list[str], rows: list[dict], ts: dt.datetime) -> dict:
    archetype, operator, ts_iso = picker_seed(ts, wishful_share=args.wishful_share)
    if args.force_archetype:
        archetype = args.force_archetype
    if args.force_operator:
        operator = args.force_operator
    word = pick_word(words, ts)
    if args.force_word:
        if args.force_word in words:
            word = args.force_word
        else:
            print(f"warning: --force-word {args.force_word!r} not in active pool "
                  f"(retired or unknown), falling back to random pick",
                  file=sys.stderr)
    archetype, word, re_rolled = variation_guard(archetype, word, rows, words, ts)
    forced_markers = []
    if args.force_archetype:
        forced_markers.append("forced-archetype")
    if args.force_word:
        forced_markers.append("forced-word")
    if args.force_operator:
        forced_markers.append("forced-operator")
    if forced_markers:
        prefix = "+".join(forced_markers)
        re_rolled = prefix if re_rolled == "no" else f"{prefix}+{re_rolled}"
    return {
        "timestamp": ts_iso,
        "mode": "single",
        "archetype": archetype,
        "word": word,
        "operator": operator,
        "re_rolled": re_rolled,
        "field_notes_rows_read": len(rows),
    }


def pick_chat(words: list[str], rows: list[dict], ts: dt.datetime,
              wishful_share: float = 0.0) -> dict:
    """Four picks, one per archetype. Word-guard runs across the chat-run."""
    chat_rolled = []
    chat_words: set[str] = set()
    picks = []
    for i, archetype in enumerate(ARCHETYPES):
        offset = i  # one second per archetype to vary operator pick
        _, operator, _ = picker_seed(ts, offset_seconds=offset,
                                     wishful_share=wishful_share)
        word = pick_word(words, ts, offset=i * 7)  # spread word picks
        intra_chat = "no"
        if word in chat_words:
            for candidate in words:
                if candidate not in chat_words:
                    word = candidate
                    intra_chat = "intra-chat"
                    break
        chat_words.add(word)
        # Per-archetype variation guard against historical rows
        archetype_kept, word_kept, re_rolled = variation_guard(
            archetype, word, rows, [w for w in words if w not in chat_words or w == word], ts
        )
        # In chat we never re-roll the archetype itself (one of each)
        archetype_kept = archetype
        if re_rolled == "archetype":
            re_rolled = "no"
        elif re_rolled == "both":
            re_rolled = "word"
        if intra_chat == "intra-chat":
            re_rolled = "intra-chat" if re_rolled == "no" else f"{re_rolled}+intra-chat"
        picks.append({
            "archetype": archetype_kept,
            "word": word_kept,
            "operator": operator,
            "re_rolled": re_rolled,
        })
        chat_rolled.append(re_rolled)
    aggregate = "no" if all(r == "no" for r in chat_rolled) else "/".join(chat_rolled)
    return {
        "timestamp": ts.isoformat().replace("+00:00", "Z"),
        "mode": "chat",
        "picks": picks,
        "re_rolled_aggregate": aggregate,
        "field_notes_rows_read": len(rows),
    }


def main() -> int:
    p = argparse.ArgumentParser(description="crazy-professor picker")
    p.add_argument("--field-notes", required=True, type=Path)
    p.add_argument("--words", required=True, type=Path)
    p.add_argument("--retired", required=True, type=Path)
    p.add_argument("--mode", choices=("single", "chat"), default="single")
    p.add_argument("--init-template", type=Path, help="copy this file to --field-notes if missing")
    p.add_argument("--force-archetype", choices=ARCHETYPES, help="bypass mod-4 picker")
    p.add_argument("--force-word", help="bypass word random pick (variation-guard still applies)")
    p.add_argument("--force-operator",
                   choices=("reversal", "exaggeration", "escape", "wishful-thinking"),
                   help="bypass operator random pick (variation-guard still applies)")
    p.add_argument("--force-timestamp", help="ISO-8601 UTC override (testing)")
    p.add_argument("--wishful-share", type=float, default=0.25,
                   help="relative weight for wishful-thinking operator (weights = "
                        "[1, 1, 1, share*3]). 0.0 = disabled (3-operator legacy). "
                        "0.333 = equal 25%% each. 1.0 = wishful ~50%% (weights [1,1,1,3]). "
                        "Default 0.25 = ~14%% wishful, ~28.6%% each base operator.")
    args = p.parse_args()
    if args.wishful_share < 0.0 or args.wishful_share > 1.0:
        print(f"error: --wishful-share must be in [0.0, 1.0] (got {args.wishful_share})",
              file=sys.stderr)
        return 1

    # Initialization
    if not args.field_notes.exists():
        if args.init_template and args.init_template.exists():
            args.field_notes.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(args.init_template, args.field_notes)
        else:
            args.field_notes.parent.mkdir(parents=True, exist_ok=True)
            args.field_notes.write_text(
                "# Crazy Professor -- Field Notes\n\n## Log\n\n"
                "| # | Timestamp | Archetype | Word | Operator | Topic slug | Output file | "
                "Re-rolled | Kept | Retire-word | Voice-off | Review1-Votum |\n"
                "|---|-----------|-----------|------|----------|------------|"
                "-------------|-----------|------|-------------|-----------|---------------|\n",
                encoding="utf-8",
            )

    if args.force_timestamp:
        ts = dt.datetime.fromisoformat(args.force_timestamp.replace("Z", "+00:00"))
    else:
        ts = dt.datetime.now(dt.timezone.utc)

    words = read_word_pool(args.words, args.retired)
    if not words:
        print("error: empty word pool (all words filtered by retired list)", file=sys.stderr)
        return 2
    rows = read_last_log_rows(args.field_notes, n=10)

    if args.mode == "single":
        result = pick_single(args, words, rows, ts)
    else:
        result = pick_chat(words, rows, ts, wishful_share=args.wishful_share)

    json.dump(result, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
