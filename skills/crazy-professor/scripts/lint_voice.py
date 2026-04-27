#!/usr/bin/env python3
"""
crazy-professor voice linter -- per-archetype lexicon enforcement.

Reads the Lexicon-Gate YAML block at the bottom of each
prompt-templates/<archetype>.md, parses every numbered provocation in
the output file, and checks per provocation:

  - at least N required tokens appear (within first sentence /
    first N chars / anywhere, depending on the gate config)
  - zero forbidden tokens appear anywhere in the provocation

Designed to run BEFORE the format validator (validate_output.py) as a
soft gate: warns by default, blocks with --strict.

Substring matching is case-insensitive on the lowercased provocation
text. No diacritic transliteration is performed: the templates are
written ASCII-only by convention (no umlauts), so "daemmerung" in a
template matches "daemmerung" / "Daemmerung" in the output but does
NOT match "Dammerung" or "Dämmerung". If a future template introduces
non-ASCII tokens, this linter will need a transliteration step.

Usage:
    lint_voice.py --templates-dir <path> --mode <single|chat> [--strict] <output-file>

Exits:
    0  voice passes (no findings, or only warnings in non-strict mode)
    1  voice findings detected (printed to stderr); also exit 1 in
       strict mode if any warnings turned into errors
    2  usage error / unreadable input / unparseable lexicon

Implementation notes:
  - The YAML parser is a tiny stdlib-only subset that handles the
    block scalar shape used in our Lexicon-Gates. It is not a general
    YAML parser. Keep the gate format simple.
  - For chat-mode, every Round 3 archetype subsection (Jester-5,
    Librarian-5, Alchemist-5, Radagast-5) is checked against its
    matching archetype's lexicon. Round 1 / Round 2 are not checked
    by this linter (they are intermediate scratch material).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ARCHETYPES = ("first-principles-jester", "labyrinth-librarian",
              "systems-alchemist", "radagast-brown")

CHAT_LABEL_TO_ARCHETYPE = {
    "Jester-5": "first-principles-jester",
    "Librarian-5": "labyrinth-librarian",
    "Alchemist-5": "systems-alchemist",
    "Radagast-5": "radagast-brown",
}

LEXICON_GATE_BLOCK_RE = re.compile(
    r"## Lexicon-Gate.*?```yaml\s*\n(.*?)```",
    re.DOTALL,
)
PROVOCATION_NUMBER_RE = re.compile(r"^\s*(\d+)\.\s+(.*)$")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ])")


def parse_lexicon_yaml(text: str) -> dict:
    """Parse the small YAML subset used in our Lexicon-Gate blocks.

    Supported:
      key: value
      key: true / false
      key: 123
      key:
        - item
        - item
    Comments (# ...) and blank lines are skipped.
    """
    result: dict = {}
    current_list_key: str | None = None
    for raw_line in text.splitlines():
        stripped = raw_line.split("#", 1)[0].rstrip()
        if not stripped.strip():
            continue
        if stripped.startswith("  - ") or stripped.startswith("- "):
            item = stripped.split("- ", 1)[1].strip().strip('"').strip("'")
            if current_list_key is None:
                continue
            result[current_list_key].append(item)
            continue
        if ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            if value == "":
                result[key] = []
                current_list_key = key
            else:
                current_list_key = None
                v = value.strip().strip('"').strip("'")
                if v.lower() == "true":
                    result[key] = True
                elif v.lower() == "false":
                    result[key] = False
                else:
                    try:
                        result[key] = int(v)
                    except ValueError:
                        result[key] = v
    return result


def load_lexicons(templates_dir: Path) -> dict[str, dict]:
    """Return {archetype-name: gate-dict} for all 4 archetypes.

    Errors out (sys.exit 2) if any archetype is missing or unparseable
    -- the linter must have a complete lexicon picture to be safe.
    """
    lexicons: dict[str, dict] = {}
    for arch in ARCHETYPES:
        path = templates_dir / f"{arch}.md"
        if not path.exists():
            print(f"error: missing template {path}", file=sys.stderr)
            sys.exit(2)
        text = path.read_text(encoding="utf-8")
        m = LEXICON_GATE_BLOCK_RE.search(text)
        if not m:
            print(f"error: no Lexicon-Gate yaml block in {path}", file=sys.stderr)
            sys.exit(2)
        gate = parse_lexicon_yaml(m.group(1))
        if gate.get("archetype") != arch:
            print(
                f"error: lexicon archetype mismatch in {path}: "
                f"got {gate.get('archetype')!r}, expected {arch!r}",
                file=sys.stderr,
            )
            sys.exit(2)
        lexicons[arch] = gate
    return lexicons


def first_sentence(text: str) -> str:
    """Return the first sentence-ish chunk. Falls back to whole text."""
    parts = SENTENCE_SPLIT_RE.split(text, maxsplit=1)
    return parts[0] if parts else text


def normalize(text: str) -> str:
    """Lowercase and collapse whitespace. ASCII-friendly substring matching."""
    return re.sub(r"\s+", " ", text.lower())


def check_provocation(
    n: int,
    body: str,
    lexicon: dict,
    archetype: str,
) -> list[tuple[str, str]]:
    """Return list of (severity, message) tuples. severity is 'warn' or 'error'."""
    findings: list[tuple[str, str]] = []
    norm_full = normalize(body)
    required = [r.lower() for r in lexicon.get("required", [])]
    required_patterns_raw = lexicon.get("required_patterns", [])
    forbidden = [f.lower() for f in lexicon.get("forbidden", [])]
    min_required = int(lexicon.get("required_min_per_provocation", 1))
    in_first_sentence = bool(lexicon.get("required_in_first_sentence", False))
    in_first_chars = int(lexicon.get("required_in_first_chars", 0) or 0)

    if in_first_sentence:
        haystack = normalize(first_sentence(body))
        scope = "first sentence"
    elif in_first_chars > 0:
        haystack = norm_full[:in_first_chars]
        scope = f"first {in_first_chars} chars"
    else:
        haystack = norm_full
        scope = "anywhere"

    token_hits = sorted({tok for tok in required if tok in haystack})
    pattern_hits: list[str] = []
    for pat in required_patterns_raw:
        try:
            if re.search(pat.lower(), haystack):
                pattern_hits.append(pat)
        except re.error as exc:
            findings.append((
                "error",
                f"required_patterns regex {pat!r} for {archetype} is invalid: {exc}",
            ))
    total_hits = len(token_hits) + len(pattern_hits)
    # Required-misses are warnings (style guidance, may have legitimate
    # archetype-flavored exceptions). Forbidden hits are errors (cross-
    # archetype contamination is a clear voice-drift signal).
    if total_hits < min_required:
        findings.append((
            "warn",
            f"provocation #{n} ({archetype}): only {total_hits} required marker(s) "
            f"in {scope} (need >={min_required}); tokens: {token_hits or 'none'}, "
            f"patterns: {pattern_hits or 'none'}"
        ))

    forbidden_hits = sorted({tok for tok in forbidden if tok in norm_full})
    if forbidden_hits:
        findings.append((
            "error",
            f"provocation #{n} ({archetype}): forbidden token(s) present: "
            f"{forbidden_hits} (these belong to a different archetype)"
        ))

    return findings


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
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


def extract_section(body: str, heading_pattern: str) -> str | None:
    """Return text under the matching ## heading, until the next ## heading."""
    lines = body.splitlines()
    pat = re.compile(heading_pattern)
    start = -1
    depth = 2
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if m and pat.match(m.group(2)):
            start = i + 1
            depth = len(m.group(1))
            break
    if start < 0:
        return None
    end = len(lines)
    for j in range(start, len(lines)):
        m = re.match(r"^(#{1,6})\s+", lines[j])
        if m and len(m.group(1).split("#")[0] or m.group(1)) <= depth:
            end = j
            break
    return "\n".join(lines[start:end])


def collect_provocations(section_text: str) -> list[tuple[int, str]]:
    """Parse '<n>. <text>' lines from a section. Returns [(n, text), ...].

    Supports the canonical line format:
      <n>. <text> -- [cost: <level>] -- anchor: <text>
    We strip the trailing ' -- [cost: ...]' part so the lexicon check
    runs on the provocation prose only, not on the cost/anchor metadata.
    """
    out: list[tuple[int, str]] = []
    sep = r"(?:\s+--\s+|\s+—\s+|\s+–\s+)"
    cost_re = re.compile(rf"{sep}\[cost:.+$", re.DOTALL)
    for line in section_text.splitlines():
        m = PROVOCATION_NUMBER_RE.match(line)
        if not m:
            continue
        n = int(m.group(1))
        body = m.group(2)
        body = cost_re.sub("", body).strip()
        if body:
            out.append((n, body))
    return out


def check_single(text: str, lexicons: dict[str, dict]) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    fm, body = split_frontmatter(text)
    arch = fm.get("archetype", "")
    if arch not in ARCHETYPES:
        findings.append((
            "error",
            f"frontmatter.archetype not in {ARCHETYPES} (got {arch!r}); "
            f"cannot pick lexicon"
        ))
        return findings

    section = extract_section(body, r"^10 Provocations\s*$")
    if section is None:
        findings.append(("error", "missing '## 10 Provocations' section"))
        return findings

    provs = collect_provocations(section)
    if not provs:
        findings.append(("error", "no numbered provocations found in section"))
        return findings

    for n, prov in provs:
        findings.extend(check_provocation(n, prov, lexicons[arch], arch))
    return findings


def check_chat(text: str, lexicons: dict[str, dict]) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    _, body = split_frontmatter(text)

    r3 = extract_section(body, r"^Round 3")
    if r3 is None:
        findings.append(("error", "missing '## Round 3' section"))
        return findings

    for label, arch in CHAT_LABEL_TO_ARCHETYPE.items():
        sub = extract_section(r3, rf".*{re.escape(label)}.*")
        if sub is None:
            findings.append(("error", f"Round 3: missing '{label}' subsection"))
            continue
        provs = collect_provocations(sub)
        if not provs:
            findings.append((
                "error",
                f"Round 3 / {label}: no numbered items found",
            ))
            continue
        for n, prov in provs:
            findings.extend(check_provocation(n, prov, lexicons[arch], arch))
    return findings


def main() -> int:
    p = argparse.ArgumentParser(description="crazy-professor voice linter")
    p.add_argument("--templates-dir", required=True, type=Path,
                   help="prompt-templates/ directory")
    p.add_argument("--mode", choices=("single", "chat"), required=True)
    p.add_argument("--strict", action="store_true",
                   help="exit 1 on any finding (default: exit 1 only on errors)")
    p.add_argument("file", type=Path, help="output file to lint")
    args = p.parse_args()

    if not args.file.exists() or not args.file.is_file():
        print(f"error: not a file: {args.file}", file=sys.stderr)
        return 2
    if not args.templates_dir.is_dir():
        print(f"error: not a directory: {args.templates_dir}", file=sys.stderr)
        return 2

    lexicons = load_lexicons(args.templates_dir)
    text = args.file.read_text(encoding="utf-8")
    findings = (check_single(text, lexicons) if args.mode == "single"
                else check_chat(text, lexicons))

    errors = [m for sev, m in findings if sev == "error"]
    warnings = [m for sev, m in findings if sev == "warn"]

    if not findings:
        print(f"voice linter: ok ({args.file.name}, {args.mode}-mode)")
        return 0

    print(
        f"voice findings in {args.file.name} ({args.mode}-mode): "
        f"{len(errors)} error(s), {len(warnings)} warning(s)",
        file=sys.stderr,
    )
    for w in warnings:
        print(f"  warn: {w}", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)

    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
