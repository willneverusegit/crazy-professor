#!/usr/bin/env python3
"""
crazy-professor patch-suggestion-loop -- read kept/retire markers from
field-notes.md, propose word-pool or SKILL.md patches.

Triggered every Nth run (default N=10). The skill counts runs from the
Log table length: when (rows % N == 0), it invokes this script. The
script writes ONE markdown file with a proposed patch to:

    <patches-dir>/YYYY-MM-DD-suggestion-<seq>.md

It does NOT modify any source file. The user reviews the suggestion
and applies (or discards) it manually. This is intentional: the
loop closes the learning cycle without sneaking edits into the repo.

The suggestion has 4 sections:
    1. Summary -- run count, which trigger fired
    2. Proven words -- words that appeared >=2 times with kept=yes
    3. Retire candidates -- words with retire-word=yes
    4. Voice-drift hot spots -- (word, archetype) pairs where voice-off was non-empty

Each section is a copy-pasteable diff hint, not an automatic patch.

Usage:
    patch_suggester.py --field-notes <path> [--patches-dir <path>]
                       [--every N] [--force] [--out <path>] [--quiet]

Behavior:
    --every N   default 10. Suggestion only runs if log row count is a
                non-zero multiple of N, unless --force is given.
    --force     bypass the modulo gate (useful for testing or manual run).
    --out       write to a specific file path instead of computing one.
    --quiet     suppress stdout summary (still writes file).

Exit codes:
    0  suggestion written
    1  usage error / unreadable input
    2  no field-notes log table found
    3  modulo gate not satisfied (no suggestion needed) -- not an error
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

LOG_TABLE_HEADER_RE = re.compile(r"^\|\s*#\s*\|\s*Timestamp", re.IGNORECASE)
LOG_TABLE_ROW_RE = re.compile(r"^\|\s*\d+\s*\|")


def read_all_log_rows(field_notes: Path) -> list[dict]:
    """Parse all log rows of field-notes.md into dicts."""
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
    for row in rows:
        cells = (row + [""] * len(columns))[: len(columns)]
        parsed.append(dict(zip(columns, cells)))
    return parsed


def normalize_archetype(raw: str) -> str:
    return raw.split(" (")[0].strip()


def normalize_word(raw: str) -> str:
    """Strip multi-word chat-mode wrappers and parenthetical metadata."""
    raw = raw.split(" (")[0].strip()
    return raw


def is_kept(cell: str) -> bool:
    """Heuristic: 'kept' anywhere in the cell, but not 'pending' or 'no'."""
    c = cell.lower()
    if not c or c == "pending" or c.startswith("no "):
        return False
    return "kept" in c or c.startswith("yes")


def is_retire(cell: str) -> bool:
    c = cell.lower()
    return c.startswith("yes") or c == "retire" or c.startswith("retire ")


def has_voice_off(cell: str) -> bool:
    c = cell.lower()
    return bool(c) and c not in ("no", "pending", "n/a")


def analyze(rows: list[dict]) -> dict:
    """Aggregate insights from rows."""
    word_counts: Counter[str] = Counter()
    word_kept: Counter[str] = Counter()
    word_retire: Counter[str] = Counter()
    archetype_word_kept: Counter[tuple[str, str]] = Counter()
    voice_drift_pairs: list[tuple[str, str, str]] = []
    chat_runs = 0
    single_runs = 0

    for r in rows:
        archetype = normalize_archetype(r["archetype"])
        word = normalize_word(r["word"])
        if archetype == "all-4":
            chat_runs += 1
            continue
        single_runs += 1
        word_counts[word] += 1
        if is_kept(r["kept"]):
            word_kept[word] += 1
            archetype_word_kept[(archetype, word)] += 1
        if is_retire(r["retire"]):
            word_retire[word] += 1
        if has_voice_off(r["voice_off"]):
            voice_drift_pairs.append((archetype, word, r["voice_off"]))

    proven = [(w, c) for w, c in word_kept.most_common() if c >= 2]
    retire = [(w, c) for w, c in word_retire.most_common() if c >= 1]
    return {
        "single_runs": single_runs,
        "chat_runs": chat_runs,
        "total_log_rows": len(rows),
        "unique_words": len(word_counts),
        "proven": proven,
        "retire_candidates": retire,
        "voice_drift_pairs": voice_drift_pairs,
        "archetype_word_kept": archetype_word_kept.most_common(10),
    }


def render_suggestion(analysis: dict, run_count: int, every: int) -> str:
    today = dt.date.today().isoformat()
    lines: list[str] = []
    lines.append(f"# Patch Suggestion -- {today}")
    lines.append("")
    lines.append("**Trigger:** patch-suggestion-loop (every "
                 f"{every} runs); current single-mode count = "
                 f"{run_count}")
    lines.append("")
    lines.append("This is a NON-AUTOMATIC suggestion. Review each section")
    lines.append("and apply manually if it looks right. Discard otherwise.")
    lines.append("")

    lines.append("## 1. Summary")
    lines.append("")
    lines.append(f"- Total log rows: {analysis['total_log_rows']}")
    lines.append(f"- Single-mode runs: {analysis['single_runs']}")
    lines.append(f"- Chat-mode runs: {analysis['chat_runs']}")
    lines.append(f"- Unique words used (single-mode): {analysis['unique_words']}")
    lines.append("")

    lines.append("## 2. Proven words (kept >= 2 times)")
    lines.append("")
    if analysis["proven"]:
        lines.append("These words have been marked `kept` at least twice. Consider")
        lines.append("flagging them in the pool comment as proven (or accepting them")
        lines.append("as 'core' if a tier exists later).")
        lines.append("")
        for word, count in analysis["proven"]:
            lines.append(f"- `{word}` ({count} kept)")
    else:
        lines.append("_No word has been kept >= 2 times yet. Need more reviewed runs._")
    lines.append("")

    lines.append("## 3. Retire candidates")
    lines.append("")
    if analysis["retire_candidates"]:
        lines.append("These words were flagged `retire` in field-notes. If you agree,")
        lines.append("append to `skills/crazy-professor/resources/retired-words.txt`:")
        lines.append("")
        lines.append("```diff")
        for word, count in analysis["retire_candidates"]:
            lines.append(f"+ {word}    # marked retire {count}x in field-notes")
        lines.append("```")
    else:
        lines.append("_No retire flags in field-notes._")
    lines.append("")

    lines.append("## 4. Voice-drift hot spots")
    lines.append("")
    if analysis["voice_drift_pairs"]:
        lines.append("Past voice-off observations. Consider whether the per-archetype")
        lines.append("Lexicon-Gate forbidden-list in `prompt-templates/<archetype>.md`")
        lines.append("needs an entry, or whether a required token should be added:")
        lines.append("")
        for archetype, word, note in analysis["voice_drift_pairs"]:
            lines.append(f"- {archetype} on `{word}`: {note}")
    else:
        lines.append("_No voice-off observations recorded._")
    lines.append("")

    lines.append("## 5. Archetype-word affinity (top 10)")
    lines.append("")
    if analysis["archetype_word_kept"]:
        lines.append("Pairs that scored `kept` more than once. Useful as evidence")
        lines.append("when tightening required-tokens in a Lexicon-Gate.")
        lines.append("")
        for (arch, word), count in analysis["archetype_word_kept"]:
            lines.append(f"- {arch} + `{word}` ({count}x kept)")
    else:
        lines.append("_No archetype-word pair scored `kept` more than once yet._")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("**Discard if:** any section feels like premature pattern-fitting.")
    lines.append("Field notes are noisy by design; only act when the signal is clear.")
    return "\n".join(lines) + "\n"


def next_seq_filename(patches_dir: Path) -> Path:
    today = dt.date.today().isoformat()
    existing = sorted(patches_dir.glob(f"{today}-suggestion-*.md"))
    seq = len(existing) + 1
    return patches_dir / f"{today}-suggestion-{seq}.md"


def cmd_main(args) -> int:
    rows = read_all_log_rows(args.field_notes)
    if not rows:
        print(f"error: no log table rows found in {args.field_notes}", file=sys.stderr)
        return 2

    analysis = analyze(rows)
    run_count = analysis["single_runs"]
    if not args.force and (run_count == 0 or run_count % args.every != 0):
        if not args.quiet:
            print(f"no suggestion: single-mode runs = {run_count} "
                  f"(needs multiple of {args.every}). Use --force to override.",
                  file=sys.stderr)
        return 3

    patches_dir = args.patches_dir or args.field_notes.parent / "patches"
    patches_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.out if args.out else next_seq_filename(patches_dir)
    text = render_suggestion(analysis, run_count, args.every)
    out_path.write_text(text, encoding="utf-8")

    if not args.quiet:
        print(f"wrote suggestion: {out_path}")
        print(f"  single_runs={run_count} proven={len(analysis['proven'])} "
              f"retire={len(analysis['retire_candidates'])} "
              f"voice_drift={len(analysis['voice_drift_pairs'])}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="crazy-professor patch-suggestion-loop")
    p.add_argument("--field-notes", required=True, type=Path,
                   help="path to field-notes.md")
    p.add_argument("--patches-dir", type=Path, default=None,
                   help="output directory (default: field-notes-parent/patches/)")
    p.add_argument("--every", type=int, default=10,
                   help="trigger every N single-mode runs (default 10)")
    p.add_argument("--force", action="store_true",
                   help="bypass modulo gate")
    p.add_argument("--out", type=Path, default=None,
                   help="explicit output file path")
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args()
    if args.every < 1:
        print("error: --every must be >= 1", file=sys.stderr)
        return 1
    return cmd_main(args)


if __name__ == "__main__":
    sys.exit(main())
