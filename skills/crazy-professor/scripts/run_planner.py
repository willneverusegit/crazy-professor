#!/usr/bin/env python3
"""
crazy-professor run planner -- topic-aware archetype selector and
session topic suggester.

Three subcommands. All write a single JSON object to stdout.

  archetype   --topic "..." --keywords <path>
              -> {topic, selected_archetype, selection_reason,
                  matched_keywords, fallback_used, topic_candidates: null}

  session     --session-path <path> [--session-path <path> ...]
              -> {topic: null, selected_archetype: null, ...,
                  topic_candidates: [{topic, source, rank}, ...]}

  plan        --topic "..." --keywords <path>
              --session-path <p1> [--session-path <p2> ...]
              -> archetype-fields + topic_candidates combined.

Exit codes:
    0  success -- JSON written to stdout
    1  usage error / unreadable input
    2  keywords file unreadable or malformed
    3  no session paths readable

Compose with picker.py: when archetype-subcommand returns
selection_reason == "keyword_match" with a non-null selected_archetype,
operating-instructions calls picker with --force-archetype <selected>.
Picker's variation-guard always wins (a 3-in-a-row streak overrides the
selector). When fallback_used == true, picker runs without
--force-archetype and timestamp-mod takes over.
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

PUNCT_STRIP = str.maketrans({c: " " for c in ".,!?;:()[]\"'"})

# Headlines we accept as "next steps" / "open items" sections.
# Case-insensitive, hyphen/underscore tolerant.
SECTION_PATTERNS = (
    re.compile(r"^##+\s*naechste[\s_-]+schritte\s*$", re.IGNORECASE),
    re.compile(r"^##+\s*nächste[\s_-]+schritte\s*$", re.IGNORECASE),
    re.compile(r"^##+\s*next[\s_-]+steps\s*$", re.IGNORECASE),
    re.compile(r"^##+\s*open[\s_-]+items\s*$", re.IGNORECASE),
)
BULLET_RE = re.compile(r"^\s*(?:[-*]|\d+\.)\s+(.*\S)\s*$")


def parse_keywords_file(path: Path) -> dict[str, list[str]]:
    """Return {archetype: [keywords]}. Raises ValueError on malformed input."""
    if not path.exists():
        raise FileNotFoundError(f"keywords file not found: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError(f"cannot read keywords file: {exc}") from exc
    pool: dict[str, list[str]] = {a: [] for a in ARCHETYPES}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"malformed line (no colon): {raw_line!r}")
        arch, kws = line.split(":", 1)
        arch = arch.strip()
        if arch not in ARCHETYPES:
            raise ValueError(f"unknown archetype: {arch!r}")
        kw_list = [k.strip().lower() for k in kws.split(",") if k.strip()]
        pool[arch] = kw_list
    return pool


def tokenize_topic(topic: str) -> str:
    """Return a normalized, lowercased, whitespace-collapsed topic string."""
    lowered = topic.lower().translate(PUNCT_STRIP)
    return " ".join(lowered.split())


def score_archetypes(topic_norm: str, pool: dict[str, list[str]]) -> dict[str, list[str]]:
    """Return {archetype: [matched_keywords]}, substring matching."""
    matches: dict[str, list[str]] = {a: [] for a in ARCHETYPES}
    for arch, kws in pool.items():
        for kw in kws:
            if kw and kw in topic_norm:
                matches[arch].append(kw)
    return matches


def select_archetype(topic: str, pool: dict[str, list[str]]) -> dict:
    """Score-based selection. Tie at position 1 -> fallback."""
    topic_norm = tokenize_topic(topic)
    matches = score_archetypes(topic_norm, pool)
    scored = [(arch, len(kws)) for arch, kws in matches.items()]
    max_score = max((s for _, s in scored), default=0)
    if max_score == 0:
        return {
            "topic": topic,
            "selected_archetype": None,
            "selection_reason": None,
            "matched_keywords": [],
            "fallback_used": True,
            "topic_candidates": None,
        }
    leaders = [arch for arch, s in scored if s == max_score]
    if len(leaders) > 1:
        return {
            "topic": topic,
            "selected_archetype": None,
            "selection_reason": None,
            "matched_keywords": [],
            "fallback_used": True,
            "topic_candidates": None,
        }
    winner = leaders[0]
    return {
        "topic": topic,
        "selected_archetype": winner,
        "selection_reason": "keyword_match",
        "matched_keywords": matches[winner],
        "fallback_used": False,
        "topic_candidates": None,
    }


def read_section_bullets(text: str) -> list[tuple[str, str]]:
    """Walk the markdown text. For each section that matches one of
    SECTION_PATTERNS, collect bullets until the next ## heading. Returns
    a list of (section_label, bullet_text) tuples in document order.
    section_label is the literal heading text without ## prefix."""
    out: list[tuple[str, str]] = []
    current_section: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("##"):
            stripped_for_match = line.lstrip("#").strip()
            if any(p.match(line) for p in SECTION_PATTERNS):
                current_section = stripped_for_match
                continue
            current_section = None
            continue
        if current_section is None:
            continue
        m = BULLET_RE.match(raw_line)
        if m:
            text_part = m.group(1).strip()
            if text_part:
                out.append((current_section, text_part))
    return out


def read_session_file(path: Path) -> list[tuple[str, str]]:
    """Return [(section, bullet), ...] for a single session file. Empty
    list if file unreadable or no matching sections."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    return read_section_bullets(text)


def extract_topic_candidates(paths: list[Path], limit: int = 3) -> tuple[list[dict], int]:
    """Read all paths in order, dedup bullets by exact text match, return
    (candidates, n_paths_read). n_paths_read counts paths that were
    successfully opened (regardless of whether they yielded bullets)."""
    seen: set[str] = set()
    candidates: list[dict] = []
    n_read = 0
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        n_read += 1
        for section, bullet in read_section_bullets(text):
            if bullet in seen:
                continue
            seen.add(bullet)
            candidates.append({
                "topic": bullet,
                "source": section,
                "rank": len(candidates) + 1,
            })
            if len(candidates) >= limit:
                return candidates, n_read
    return candidates, n_read


def cmd_session(args) -> int:
    paths: list[Path] = list(args.session_path or [])
    if not paths:
        print("error: at least one --session-path is required", file=sys.stderr)
        return 1
    candidates, n_read = extract_topic_candidates(paths, limit=3)
    if n_read == 0:
        print(f"error: none of the {len(paths)} session paths were readable",
              file=sys.stderr)
        return 3
    result = {
        "topic": None,
        "selected_archetype": None,
        "selection_reason": None,
        "matched_keywords": [],
        "fallback_used": None,
        "topic_candidates": candidates,
    }
    json.dump(result, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def cmd_plan(args) -> int:
    if not args.topic or not args.topic.strip():
        print("error: --topic is required and must not be empty", file=sys.stderr)
        return 1
    try:
        pool = parse_keywords_file(args.keywords)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    archetype_result = select_archetype(args.topic, pool)
    paths: list[Path] = list(args.session_path or [])
    if paths:
        candidates, n_read = extract_topic_candidates(paths, limit=3)
        if n_read == 0:
            archetype_result["topic_candidates"] = None
        else:
            archetype_result["topic_candidates"] = candidates
    else:
        archetype_result["topic_candidates"] = None
    json.dump(archetype_result, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def cmd_archetype(args) -> int:
    if not args.topic or not args.topic.strip():
        print("error: --topic is required and must not be empty", file=sys.stderr)
        return 1
    try:
        pool = parse_keywords_file(args.keywords)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    result = select_archetype(args.topic, pool)
    json.dump(result, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    # Ensure UTF-8 stdout on Windows (session-summary.md may contain →, –, etc.)
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass

    p = argparse.ArgumentParser(description="crazy-professor run planner")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("archetype", help="select archetype from topic keywords")
    a.add_argument("--topic", required=True)
    a.add_argument("--keywords", required=True, type=Path)

    s = sub.add_parser("session", help="extract topic candidates from session-summary files")
    s.add_argument("--session-path", action="append", required=True, type=Path,
                   metavar="PATH", help="repeatable; first listed has priority for dedup")

    pl = sub.add_parser("plan", help="archetype + session combined")
    pl.add_argument("--topic", required=True)
    pl.add_argument("--keywords", required=True, type=Path)
    pl.add_argument("--session-path", action="append", required=True, type=Path,
                    metavar="PATH", help="repeatable")

    args = p.parse_args()
    if args.cmd == "archetype":
        return cmd_archetype(args)
    if args.cmd == "session":
        return cmd_session(args)
    if args.cmd == "plan":
        return cmd_plan(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
