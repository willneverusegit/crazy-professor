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
OPERATORS = ("reversal", "exaggeration", "escape")
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


def picker_seed(ts: dt.datetime, offset_seconds: int = 0) -> tuple[str, str, str]:
    """Deterministic mod-based picker for archetype/operator and a word index seed."""
    seed_ts = ts + dt.timedelta(seconds=offset_seconds)
    archetype = ARCHETYPES[seed_ts.minute % 4]
    operator = OPERATORS[seed_ts.second % 3]
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
    archetype, operator, ts_iso = picker_seed(ts)
    if args.force_archetype:
        archetype = args.force_archetype
    word = pick_word(words, ts)
    archetype, word, re_rolled = variation_guard(archetype, word, rows, words, ts)
    if args.force_archetype:
        re_rolled = "forced-archetype" if re_rolled == "no" else f"forced-archetype+{re_rolled}"
    return {
        "timestamp": ts_iso,
        "mode": "single",
        "archetype": archetype,
        "word": word,
        "operator": operator,
        "re_rolled": re_rolled,
        "field_notes_rows_read": len(rows),
    }


def pick_chat(words: list[str], rows: list[dict], ts: dt.datetime) -> dict:
    """Four picks, one per archetype. Word-guard runs across the chat-run."""
    chat_rolled = []
    chat_words: set[str] = set()
    picks = []
    for i, archetype in enumerate(ARCHETYPES):
        offset = i  # one second per archetype to vary operator pick
        _, operator, ts_iso_local = picker_seed(ts, offset_seconds=offset)
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
    p.add_argument("--force-timestamp", help="ISO-8601 UTC override (testing)")
    args = p.parse_args()

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
        result = pick_chat(words, rows, ts)

    json.dump(result, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
