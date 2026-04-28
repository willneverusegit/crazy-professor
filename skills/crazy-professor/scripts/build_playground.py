#!/usr/bin/env python3
"""
crazy-professor playground build script (since v0.12.0).

Reads source resource files (provocation-words, retired-words,
po-operators, optional field-notes) and emits a single-file HTML
playground with inlined data + JS at the --output path. The HTML is
self-contained (no external CDN) and works with file:// (no HTTP
server needed).

Used by /crazy --playground in operating-instructions: skill calls
this script then opens the output via webbrowser.open().

Usage:
    build_playground.py --output <path> --words <path> --retired <path>
                        --po-operators <path>
                        [--field-notes <path>] [--version 0.12.0]

Exit codes:
    0  HTML written
    1  usage error / missing required args (argparse may use 2 here)
    2  source resource missing or unparseable
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ARCHETYPES = (
    "first-principles-jester",
    "labyrinth-librarian",
    "systems-alchemist",
    "radagast-brown",
)
DEFAULT_OPERATORS = ("reversal", "exaggeration", "escape", "wishful-thinking")


def read_word_pool(words_path: Path, retired_path: Path) -> list[str]:
    """Mirror picker.py:read_word_pool() exactly. Active = pool minus retired."""
    if not words_path.exists():
        print(f"error: words file not found: {words_path}", file=sys.stderr)
        sys.exit(2)
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


def parse_po_operators(po_path: Path) -> list[str]:
    """Parse '## <Name>' headings from po-operators.md. Hardcoded fallback on failure."""
    if not po_path.exists():
        print(f"error: po-operators file not found: {po_path}", file=sys.stderr)
        sys.exit(2)
    text = po_path.read_text(encoding="utf-8")
    heading_re = re.compile(r"^##\s+([A-Za-z][A-Za-z\s\-]*?)\s*$", re.MULTILINE)
    parsed = []
    for m in heading_re.finditer(text):
        name = m.group(1).strip().lower().replace(" ", "-")
        if name not in ("rules-for-all-three", "rules-for-all-four"):
            parsed.append(name)
    if len(parsed) >= 4:
        return parsed[:4]
    print(f"warning: po-operators parse yielded {len(parsed)} items, "
          f"using hardcoded fallback {DEFAULT_OPERATORS}", file=sys.stderr)
    return list(DEFAULT_OPERATORS)


def read_field_notes_recent(fn_path: Path | None, n: int = 10) -> list[dict]:
    """Mirror picker.py:read_last_log_rows() but emit a slimmer record set."""
    if fn_path is None or not fn_path.exists():
        return []
    text = fn_path.read_text(encoding="utf-8")
    log_header_re = re.compile(r"^\|\s*#\s*\|\s*Timestamp", re.IGNORECASE)
    log_row_re = re.compile(r"^\|\s*\d+\s*\|")
    in_log = False
    rows: list[list[str]] = []
    for line in text.splitlines():
        if not in_log and log_header_re.match(line):
            in_log = True
            continue
        if in_log and log_row_re.match(line):
            cells = [c.strip() for c in line.strip("|").split("|")]
            rows.append(cells)
        elif in_log and line.startswith("##"):
            break
    parsed = []
    for row in rows[-n:]:
        cells = (row + [""] * 12)[:12]
        parsed.append({
            "archetype": cells[2].split(" (")[0],
            "word": cells[3].split(" (")[0],
            "operator": cells[4],
        })
    return parsed


def build_html(version: str, words: list[str], operators: list[str],
               field_notes: list[dict]) -> str:
    """Stub: returns minimal placeholder. Tasks 4 + 5 fill this in."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>crazy-professor playground (stub)</title></head>
<body>
<p>Stub. Tasks 4 + 5 build the real HTML.</p>
<script>
const VERSION = "{version}";
const ARCHETYPES = {json.dumps(list(ARCHETYPES))};
const OPERATORS = {json.dumps(operators)};
const WORDS = {json.dumps(words)};
const FIELD_NOTES_RECENT = {json.dumps(field_notes)};
</script>
</body>
</html>
"""


def main() -> int:
    p = argparse.ArgumentParser(description="crazy-professor playground builder")
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--words", required=True, type=Path)
    p.add_argument("--retired", required=True, type=Path)
    p.add_argument("--po-operators", required=True, type=Path)
    p.add_argument("--field-notes", type=Path, default=None)
    p.add_argument("--version", default="unknown")
    args = p.parse_args()

    words = read_word_pool(args.words, args.retired)
    if not words:
        print("error: empty word pool (all words filtered by retired list)",
              file=sys.stderr)
        return 2
    operators = parse_po_operators(args.po_operators)
    field_notes = read_field_notes_recent(args.field_notes)

    html = build_html(args.version, words, operators, field_notes)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")
    print(f"wrote: {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
