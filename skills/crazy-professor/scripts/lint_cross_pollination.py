#!/usr/bin/env python3
"""
crazy-professor cross-pollination substance linter (since v0.11.0).

Used by Step C4b in operating-instructions when --strict-cross-pollination
is set. Reads R1 and R2 chat-mode content and runs three deterministic
checks per R2 item:

  1. Marker-Existence: R2 item begins or ends with `counter: <ref>` or
     `extend: <ref>` (case-tolerant). Missing marker -> error.
  2. Ref-Resolution: <ref> matches '<archetype> #<int>' with archetype in
     {jester, librarian, alchemist, radagast, radagast-brown} and int in
     1..5. Missing R1 item -> error.
  3. Token-Overlap: R2 item text and the referenced R1 item text share at
     least <min-overlap> non-stopword tokens (>=3 chars). Below threshold
     -> warn.

Output: one JSON object on stdout. Exit code is always 0 (warn-only).

Two input modes:
  * --r1-input <jsonfile> --r2-input <jsonfile>: pre-parsed JSON from the
    skill flow (preferred -- what Step C4b passes).
  * --r1-md <mdfile> --r2-md <mdfile>: parse the chat output's R1 and R2
    sections from raw markdown. Used by the eval-suite Stage D.

JSON input shape:
  R1: {"jester": {1: "text", 2: "text", ...}, "librarian": {...}, ...}
  R2: {"jester": [{"idx": 1, "marker": "counter", "ref": "alchemist #3",
                   "text": "..."}, ...], "librarian": [...], ...}

Markdown input shape:
  R1: as in chat-output-template, '### Jester ...' subsections with
      numbered '1.' lines.
  R2: '### Jester -- Runde 2' subsections with bulleted lines, each
      starting with 'counter:' or 'extend:'.

Usage:
  lint_cross_pollination.py --r1-input r1.json --r2-input r2.json
                            [--min-overlap 1]
                            [--stop-words <path>]
  lint_cross_pollination.py --r1-md r1.md --r2-md r2.md
                            [--min-overlap 1]
                            [--stop-words <path>]

Exit codes:
  0  always (findings or no findings; this is a warn-only linter)
  1  usage error / unreadable input
  2  unparseable JSON or markdown (structural error)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ARCHETYPES = ("jester", "librarian", "alchemist", "radagast", "radagast-brown",
              "first-principles-jester", "labyrinth-librarian", "systems-alchemist")
# canonical short labels used in marker references
ARCHETYPE_NORMALIZE = {
    "jester": "jester",
    "first-principles-jester": "jester",
    "librarian": "librarian",
    "labyrinth-librarian": "librarian",
    "alchemist": "alchemist",
    "systems-alchemist": "alchemist",
    "radagast": "radagast",
    "radagast-brown": "radagast",
}
MARKER_RE = re.compile(
    r"^\s*(counter|extend)\s*:\s*"
    r"([a-z][a-z\-]*)\s*"
    r"#\s*(\d+)\s*"
    r"(?:[—–\-]+)?\s*(.*)$",
    re.IGNORECASE,
)


def normalize_archetype(name: str) -> str | None:
    """Return canonical short label or None if not a known archetype."""
    return ARCHETYPE_NORMALIZE.get(name.lower().strip())


def load_json_file(path: Path) -> dict:
    if not path.exists():
        print(f"error: not a file: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(2)


def parse_r1_md(text: str) -> dict[str, dict[int, str]]:
    """Parse a chat-output Round-1 markdown block into {archetype: {idx: text}}."""
    sections: dict[str, dict[int, str]] = {a: {} for a in set(ARCHETYPE_NORMALIZE.values())}
    current = None
    heading_re = re.compile(r"^###\s+(\w[\w\- ]*?)\s*(?:\(.*\))?\s*$")
    item_re = re.compile(r"^\s*(\d+)\.\s+(.+?)\s*$")
    for line in text.splitlines():
        m = heading_re.match(line)
        if m:
            label = m.group(1).strip().lower()
            current = normalize_archetype(label)
            continue
        if current is None:
            continue
        im = item_re.match(line)
        if im:
            sections[current][int(im.group(1))] = im.group(2).strip()
    return sections


def parse_r2_md(text: str) -> dict[str, list[dict]]:
    """Parse a chat-output Round-2 markdown block into per-archetype list of items."""
    sections: dict[str, list[dict]] = {a: [] for a in set(ARCHETYPE_NORMALIZE.values())}
    current = None
    heading_re = re.compile(r"^###\s+(\w[\w\- ]*?)\s*(?:[—\-]\s*Runde\s*2.*)?\s*$",
                            re.IGNORECASE)
    bullet_re = re.compile(r"^\s*[-*]\s+(.+?)\s*$")
    next_idx: dict[str, int] = {a: 0 for a in set(ARCHETYPE_NORMALIZE.values())}
    for line in text.splitlines():
        m = heading_re.match(line)
        if m:
            label = m.group(1).strip().lower()
            current = normalize_archetype(label)
            continue
        if current is None:
            continue
        bm = bullet_re.match(line)
        if not bm:
            continue
        body = bm.group(1)
        item: dict = {"idx": next_idx[current] + 1, "raw": body}
        next_idx[current] += 1
        mm = MARKER_RE.match(body)
        if mm:
            item["marker"] = mm.group(1).lower()
            ref_arch = normalize_archetype(mm.group(2))
            ref_idx = int(mm.group(3))
            item["ref"] = (f"{ref_arch} #{ref_idx}"
                           if ref_arch and 1 <= ref_idx <= 5
                           else f"{mm.group(2)} #{mm.group(3)}")
            item["ref_archetype"] = ref_arch
            item["ref_idx"] = ref_idx
            item["text"] = mm.group(4).strip()
        else:
            item["marker"] = None
            item["ref"] = None
            item["ref_archetype"] = None
            item["ref_idx"] = None
            item["text"] = body
        sections[current].append(item)
    return sections


def check_ref_resolution(item: dict, r1: dict) -> tuple[str, str] | None:
    """Check 2: Ref-Resolution. Returns (severity, reason) or None.
    Assumes Check 1 already passed (marker is set). Verifies the marker's
    archetype + idx points to an existing R1 item.
    """
    arch = item.get("ref_archetype")
    idx = item.get("ref_idx")
    if arch is None or idx is None:
        return ("error",
                "ref does not match '<archetype> #<int>' format")
    if not (1 <= idx <= 5):
        return ("error",
                f"ref idx {idx} out of range 1..5")
    archetype_section = r1.get(arch, {})
    if isinstance(archetype_section, dict):
        if idx not in archetype_section and str(idx) not in archetype_section:
            return ("error",
                    f"ref does not resolve to existing R1 item ({arch} #{idx} not present)")
    elif isinstance(archetype_section, list):
        if idx > len(archetype_section):
            return ("error",
                    f"ref does not resolve to existing R1 item ({arch} #{idx} not present)")
    return None


def check_marker(item: dict) -> tuple[str, str] | None:
    """Check 1: Marker-Existence. Return (severity, reason) or None."""
    if not item.get("marker"):
        return ("error", "no counter/extend marker")
    return None


def main() -> int:
    p = argparse.ArgumentParser(description="crazy-professor cross-pollination linter")
    grp = p.add_mutually_exclusive_group(required=True)
    grp.add_argument("--r1-input", type=Path, help="JSON file with R1 sections")
    grp.add_argument("--r1-md", type=Path, help="Markdown file with R1 block")
    p.add_argument("--r2-input", type=Path, help="JSON file with R2 items")
    p.add_argument("--r2-md", type=Path, help="Markdown file with R2 block")
    p.add_argument("--min-overlap", type=int, default=1,
                   help="minimum non-stopword token overlap (default 1)")
    p.add_argument("--stop-words", type=Path,
                   help="optional stop-words file (one word per line)")
    args = p.parse_args()

    if args.r1_input and not args.r2_input:
        print("error: --r1-input requires --r2-input", file=sys.stderr)
        return 1
    if args.r1_md and not args.r2_md:
        print("error: --r1-md requires --r2-md", file=sys.stderr)
        return 1

    if args.r1_input:
        r1 = load_json_file(args.r1_input)
        r2 = load_json_file(args.r2_input)
    else:
        r1 = parse_r1_md(args.r1_md.read_text(encoding="utf-8"))
        r2 = parse_r2_md(args.r2_md.read_text(encoding="utf-8"))

    findings: list[dict] = []
    items_total = 0
    for archetype, items in r2.items():
        for item in items:
            items_total += 1
            check = check_marker(item)
            if check:
                severity, reason = check
                findings.append({
                    "archetype": archetype,
                    "idx": item.get("idx"),
                    "ref": item.get("ref"),
                    "severity": severity,
                    "reason": reason,
                })
                continue

            check = check_ref_resolution(item, r1)
            if check:
                severity, reason = check
                findings.append({
                    "archetype": archetype,
                    "idx": item.get("idx"),
                    "ref": item.get("ref"),
                    "severity": severity,
                    "reason": reason,
                })
                continue
            # Check 3 (Token-Overlap) is added in Task 7. For now, marker + ref-resolution.

    by_severity: dict[str, int] = {}
    for f in findings:
        by_severity[f["severity"]] = by_severity.get(f["severity"], 0) + 1

    out = {
        "low_substance_hits": len(findings),
        "findings": findings,
        "stats": {
            "r2_items_total": items_total,
            "r2_items_flagged": len(findings),
            "by_severity": by_severity,
        },
    }
    json.dump(out, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
