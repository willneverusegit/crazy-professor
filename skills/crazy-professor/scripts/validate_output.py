#!/usr/bin/env python3
"""
crazy-professor output validator â€” format-drift detection.

Reads a generated output file (single-run or chat-mode) and verifies the
mandatory structure: frontmatter, divergence banner, provocation count
and shape, sectioning, self-flags. Exit 0 if format clean, exit 1 with
issue list on stderr if drifted.

Usage:
    validate_output.py --mode <single|chat> <output-file>

Exits:
    0  output passes all checks
    1  format drift detected (stderr lists issues)
    2  usage error / unreadable input
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ARCHETYPES = ("first-principles-jester", "labyrinth-librarian",
              "systems-alchemist", "radagast-brown")
PO_OPERATORS = ("reversal", "exaggeration", "escape")

# Single-run provocation line shape:
# <n>. <text> -- [cost: <level>] -- anchor: <text>
# Accepts ASCII double-hyphen (--) or unicode dashes (em U+2014, en U+2013).
SEP = r"(?:--|\u2014|\u2013)"
PROVOCATION_RE = re.compile(
    rf"^\s*(\d+)\.\s+(.+?)\s+{SEP}\s+\[cost:\s*(low|medium|high|system-break)\]\s+{SEP}\s+anchor:\s+(.+?)\s*$"
)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def read_text(path: Path) -> str:
    if not path.exists() or not path.is_file():
        print(f"error: not a file: {path}", file=sys.stderr)
        sys.exit(2)
    return path.read_text(encoding="utf-8")


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Return (frontmatter_dict, body). Empty dict if no valid frontmatter."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    fm_text = text[4:end]
    body = text[end + 5:]
    fm: dict[str, str] = {}
    for line in fm_text.splitlines():
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, body


def find_section_lines(body: str, heading_pattern: str) -> tuple[int, int]:
    """Return (start_line_idx, next_heading_line_idx) for a section. (-1, -1) if not found."""
    lines = body.splitlines()
    pattern = re.compile(heading_pattern)
    start = -1
    same_or_higher_level = -1
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if m and start < 0 and pattern.match(m.group(2)):
            start = i
            depth = len(m.group(1))
            for j in range(i + 1, len(lines)):
                m2 = HEADING_RE.match(lines[j])
                if m2 and len(m2.group(1)) <= depth:
                    same_or_higher_level = j
                    break
            return start, same_or_higher_level if same_or_higher_level > 0 else len(lines)
    return -1, -1


def check_divergence_banner(body: str, issues: list[str]) -> None:
    if "DIVERGENCE WARNING" not in body:
        issues.append("missing divergence warning banner ('DIVERGENCE WARNING' string)")


def validate_single(text: str) -> list[str]:
    issues: list[str] = []
    fm, body = split_frontmatter(text)

    if not fm:
        issues.append("missing or unparseable YAML frontmatter")
    else:
        if fm.get("skill") != "crazy-professor":
            issues.append(f"frontmatter.skill != 'crazy-professor' (got {fm.get('skill')!r})")
        if fm.get("mode", "single") != "single":
            issues.append(f"frontmatter.mode != 'single' (got {fm.get('mode')!r})")
        arch = fm.get("archetype", "")
        if arch not in ARCHETYPES:
            issues.append(f"frontmatter.archetype not in {ARCHETYPES} (got {arch!r})")
        op = fm.get("po_operator", "")
        if op not in PO_OPERATORS:
            issues.append(f"frontmatter.po_operator not in {PO_OPERATORS} (got {op!r})")
        if not fm.get("provocation_word"):
            issues.append("frontmatter.provocation_word is empty")

    check_divergence_banner(body, issues)

    # Section: ## 10 Provocations
    start, end = find_section_lines(body, r"^10 Provocations\s*$")
    if start < 0:
        issues.append("missing '## 10 Provocations' section header")
    else:
        section_lines = body.splitlines()[start + 1:end]
        provocations = []
        for line in section_lines:
            if re.match(r"^\s*\d+\.\s", line):
                provocations.append(line)
        if len(provocations) != 10:
            issues.append(f"expected exactly 10 provocations, found {len(provocations)}")
        for i, line in enumerate(provocations, start=1):
            m = PROVOCATION_RE.match(line)
            if not m:
                issues.append(
                    f"provocation #{i} does not match format "
                    f"'<n>. <text> -- [cost: <level>] -- anchor: <text>': {line!r}"
                )
            else:
                if int(m.group(1)) != i:
                    issues.append(
                        f"provocation numbering off: expected {i}, got {m.group(1)}"
                    )

    # Section: ## Next Experiment
    next_exp_start, _ = find_section_lines(body, r"^Next Experiment")
    if next_exp_start < 0:
        issues.append("missing '## Next Experiment' section header")

    # Section: ## Self-Flag
    self_flag_start, self_flag_end = find_section_lines(body, r"^Self-Flag")
    if self_flag_start < 0:
        issues.append("missing '## Self-Flag' section header")
    else:
        flag_lines = body.splitlines()[self_flag_start + 1:self_flag_end]
        checkboxes = [l for l in flag_lines if re.match(r"^\s*-\s+\[[ xX]\]", l)]
        if len(checkboxes) < 3:
            issues.append(
                f"Self-Flag section needs at least 3 checkboxes (kept, retire-word, voice-off), "
                f"found {len(checkboxes)}"
            )

    return issues


def validate_chat(text: str) -> list[str]:
    issues: list[str] = []
    fm, body = split_frontmatter(text)

    if not fm:
        issues.append("missing or unparseable YAML frontmatter")
    else:
        if fm.get("skill") != "crazy-professor":
            issues.append(f"frontmatter.skill != 'crazy-professor' (got {fm.get('skill')!r})")
        if fm.get("mode") != "chat":
            issues.append(f"frontmatter.mode != 'chat' (got {fm.get('mode')!r})")
        distiller = fm.get("distiller", "")
        if not (distiller.startswith("codex") or distiller.startswith("claude")):
            issues.append(f"frontmatter.distiller missing or unrecognized (got {distiller!r})")

    check_divergence_banner(body, issues)

    # Three rounds present
    for round_name in ("Round 1", "Round 2", "Round 3"):
        start, _ = find_section_lines(body, rf"^{round_name}")
        if start < 0:
            issues.append(f"missing '## {round_name}' section")

    # Round 3: each archetype subsection has exactly 5 numbered items
    r3_start, r3_end = find_section_lines(body, r"^Round 3")
    if r3_start >= 0:
        r3_lines = body.splitlines()[r3_start:r3_end]
        for archetype_label in ("Jester-5", "Librarian-5", "Alchemist-5", "Radagast-5"):
            sub_start = -1
            sub_end = len(r3_lines)
            for i, line in enumerate(r3_lines):
                m = HEADING_RE.match(line)
                if m and archetype_label in m.group(2):
                    sub_start = i
                    depth = len(m.group(1))
                    for j in range(i + 1, len(r3_lines)):
                        m2 = HEADING_RE.match(r3_lines[j])
                        if m2 and len(m2.group(1)) <= depth:
                            sub_end = j
                            break
                    break
            if sub_start < 0:
                issues.append(f"Round 3: missing '{archetype_label}' subsection")
                continue
            sub_lines = r3_lines[sub_start + 1:sub_end]
            count = sum(1 for line in sub_lines if re.match(r"^\s*\d+\.\s", line))
            if count != 5:
                issues.append(
                    f"Round 3 / {archetype_label}: expected exactly 5 numbered items, found {count}"
                )

    # Top-3 Cross-Pollination
    top3_start, top3_end = find_section_lines(body, r"^Top-3 Cross-Pollination")
    if top3_start < 0:
        issues.append("missing 'Top-3 Cross-Pollination Hits' section")
    else:
        top3_lines = body.splitlines()[top3_start + 1:top3_end]
        items = sum(1 for line in top3_lines if re.match(r"^\s*\d+\.\s", line))
        if items != 3:
            issues.append(f"Top-3 section: expected exactly 3 items, found {items}")

    # Next Experiment
    if find_section_lines(body, r"^Next Experiment")[0] < 0:
        issues.append("missing 'Next Experiment' section")

    return issues


def main() -> int:
    p = argparse.ArgumentParser(description="crazy-professor output validator")
    p.add_argument("--mode", choices=("single", "chat"), required=True)
    p.add_argument("file", type=Path)
    args = p.parse_args()

    text = read_text(args.file)
    issues = validate_single(text) if args.mode == "single" else validate_chat(text)

    if not issues:
        return 0
    print(f"format-drift in {args.file} ({args.mode}-mode):", file=sys.stderr)
    for issue in issues:
        print(f"  - {issue}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
