#!/usr/bin/env python3
"""
crazy-professor word-pool linter -- pool integrity checks.

Validates provocation-words.txt and retired-words.txt for the rules
agreed in Phase 1 (1.5) and locked in resources/output-template.md:

  - lowercase only
  - 1 to 3 tokens, separator is space or hyphen (no underscores, no slashes)
  - no leading/trailing whitespace
  - no tabs anywhere
  - no duplicates within a single file
  - no overlap between provocation pool and retired list
  - blank lines must be truly blank (whitespace-only is rejected)
  - comment lines start with '#'

Designed to run as a pre-commit hook or manually. stdlib-only.

Usage:
    lint_word_pool.py --words <path> --retired <path> [--strict]

Exits:
    0  pool passes all checks
    1  one or more findings (printed to stderr)
    2  usage error / unreadable input

--strict promotes warnings to errors (currently: case-borderline tokens
where a single uppercase letter slipped in get warned in default mode).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# A pool entry: 1-3 tokens, each token is [a-z0-9]+ optionally connected
# by a single hyphen inside a token. Tokens are separated by single spaces.
# Examples that pass: "museum", "paradox tax", "false-bottom", "ghost protocol".
# Examples that fail: "Museum", "paradox  tax" (double space), "false_bottom",
# "paradox/tax", "a b c d" (4 tokens).
TOKEN_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_FILE_BYTES = 1024 * 1024


def read_lines(path: Path) -> list[tuple[int, str]]:
    if not path.exists() or not path.is_file():
        print(f"error: not a file: {path}", file=sys.stderr)
        sys.exit(2)
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        print(
            f"error: file too large for lint_word_pool.py: {path} "
            f"({size} bytes > {MAX_FILE_BYTES} bytes)",
            file=sys.stderr,
        )
        sys.exit(2)
    return list(enumerate(path.read_text(encoding="utf-8").splitlines(), start=1))


def classify(raw: str) -> str:
    """Return 'comment', 'blank', or 'entry'. 'blank' includes whitespace-only."""
    if not raw:
        return "blank"
    stripped = raw.strip()
    if not stripped:
        return "blank-whitespace"
    if stripped.startswith("#"):
        return "comment"
    return "entry"


def lint_entry(raw: str, lineno: int, source: str, strict: bool) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for a single non-blank, non-comment line."""
    errors: list[str] = []
    warnings: list[str] = []

    if "\t" in raw:
        errors.append(f"{source}:{lineno}: tab character in line ({raw!r})")
    if raw != raw.strip():
        errors.append(f"{source}:{lineno}: leading or trailing whitespace ({raw!r})")

    word = raw.strip()
    if word != word.lower():
        msg = f"{source}:{lineno}: not lowercase ({word!r})"
        if strict:
            errors.append(msg)
        else:
            warnings.append(msg)

    tokens = word.split(" ")
    if len(tokens) > 3:
        errors.append(
            f"{source}:{lineno}: more than 3 tokens ({word!r}); pool rule is 1-3 tokens"
        )
    elif any(not t for t in tokens):
        errors.append(f"{source}:{lineno}: empty token (double space?) in {word!r}")
    else:
        for tok in tokens:
            if not TOKEN_RE.match(tok):
                errors.append(
                    f"{source}:{lineno}: token {tok!r} in {word!r} violates "
                    f"[a-z0-9]+(-[a-z0-9]+)* rule (no underscores, no slashes, "
                    f"no symbols, only single internal hyphens)"
                )

    return errors, warnings


def lint_file(path: Path, strict: bool) -> tuple[list[str], list[str], list[str]]:
    """Return (errors, warnings, normalized_entries)."""
    errors: list[str] = []
    warnings: list[str] = []
    entries: list[str] = []
    seen_at: dict[str, int] = {}
    source = path.name

    for lineno, raw in read_lines(path):
        kind = classify(raw)
        if kind == "comment" or kind == "blank":
            continue
        if kind == "blank-whitespace":
            errors.append(f"{source}:{lineno}: whitespace-only line (use truly blank)")
            continue

        line_errors, line_warnings = lint_entry(raw, lineno, source, strict)
        errors.extend(line_errors)
        warnings.extend(line_warnings)

        word = raw.strip().lower()
        if word in seen_at:
            errors.append(
                f"{source}:{lineno}: duplicate of {source}:{seen_at[word]} ({word!r})"
            )
        else:
            seen_at[word] = lineno
            entries.append(word)

    return errors, warnings, entries


def main() -> int:
    p = argparse.ArgumentParser(description="crazy-professor word-pool linter")
    p.add_argument("--words", required=True, type=Path, help="provocation-words.txt")
    p.add_argument("--retired", required=True, type=Path, help="retired-words.txt")
    p.add_argument(
        "--strict",
        action="store_true",
        help="promote warnings (e.g. case borderline) to errors",
    )
    args = p.parse_args()

    all_errors: list[str] = []
    all_warnings: list[str] = []

    pool_errors, pool_warnings, pool_entries = lint_file(args.words, args.strict)
    retired_errors, retired_warnings, retired_entries = lint_file(args.retired, args.strict)
    all_errors.extend(pool_errors)
    all_errors.extend(retired_errors)
    all_warnings.extend(pool_warnings)
    all_warnings.extend(retired_warnings)

    pool_set = set(pool_entries)
    retired_set = set(retired_entries)
    overlap = sorted(pool_set & retired_set)
    if overlap:
        all_errors.append(
            f"overlap between {args.words.name} and {args.retired.name}: "
            f"{', '.join(repr(w) for w in overlap)} "
            f"(retired words must not appear in the active pool)"
        )

    for w in all_warnings:
        print(f"warning: {w}", file=sys.stderr)

    if all_errors:
        print(
            f"word-pool linter: {len(all_errors)} error(s), "
            f"{len(all_warnings)} warning(s)",
            file=sys.stderr,
        )
        for e in all_errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(
        f"word-pool linter: ok "
        f"({len(pool_entries)} pool, {len(retired_entries)} retired, "
        f"{len(all_warnings)} warning(s))"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
