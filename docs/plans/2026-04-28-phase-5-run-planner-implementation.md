# Phase 5 — Run Planner + `--dry-run` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a topic-aware archetype selector and a `--from-session` topic-suggestion mechanism to the crazy-professor skill, plus a side-effect-free `--dry-run` preview, shipped as v0.10.0.

**Architecture:** New stdlib-only Python helper `run_planner.py` with three subcommands (`archetype`, `session`, `plan`), composing with the existing `picker.py` via `--force-archetype`. New resource file `archetype-keywords.txt`. The picker stays unchanged; its variation-guard remains the final word over the selector's recommendation. `--dry-run` is a single-run command flag handled in operating-instructions Step 1.

**Tech Stack:** Python 3 stdlib (argparse, json, pathlib, re, sys, datetime). No new deps. Markdown for docs and templates. Bash for the picker shell wrapper. Git for version-control commit at the end.

**Spec reference:** `docs/specs/2026-04-28-phase-5-run-planner-design.md` (commit `12cc598`).

**Repo paths:**
- Repo root: `C:/Users/domes/Desktop/Claude-Plugins-Skills/crazy-professor`
- All script paths below are relative to that root.

---

## Task 1: Resource file `archetype-keywords.txt`

**Files:**
- Create: `skills/crazy-professor/resources/archetype-keywords.txt`

- [ ] **Step 1: Create the keyword resource file**

The keyword pool seeds Topic→Archetype matching. Format: one archetype per line, `<archetype>: kw1, kw2, ...`. Lines starting with `#` are comments. Sourced from each archetype's prompt-template Lexicon-Gate (the *real* archetype-specific tokens, not the cross-drift forbidden ones) plus generic English/German domain words. Initial size: 15-25 keywords per archetype, ~80 total. Mix of single words and short phrases.

Write `skills/crazy-professor/resources/archetype-keywords.txt` with:

```
# crazy-professor -- archetype keyword pool
# format: <archetype>: kw1, kw2, kw3, ...
# matched case-insensitive as substring against the lowercased topic.
# update via patch-suggester recommendations or manual edits; bump skill
# version on changes.

first-principles-jester: warum, why, assumption, annahme, naive, basic, simple, ursprung, root, core, zerleg, illegal, verboten, was waere, what if, axiom, primitive, original, plain, clean
labyrinth-librarian: history, geschichte, archive, archiv, doc, documentation, taxonomy, taxonomie, lineage, herkunft, classification, catalog, katalog, reference, lexikon, ontology, mythos, ueberlieferung, antike, mittelalter, library
systems-alchemist: pipeline, infra, infrastructure, system, flow, fluss, deploy, integration, transform, reactor, reaktor, ueberlauf, leck, membran, katalysator, substrat, abfluss, stau, druck, throughput, queue, schicht, layer
radagast-brown: forest, wald, shelter, schutz, slow, langsam, care, pflege, repair, reparatur, garden, garten, mend, tend, soft, gentle, ruhe, winter, mondphase, unterholz, nest, futter, rinde, kreatur, gast, geraeusch
```

- [ ] **Step 2: Verify the file is parsable by eye**

Run: `head -10 skills/crazy-professor/resources/archetype-keywords.txt`
Expected: comment lines, then 4 archetype lines. No blank lines mid-block.

Run: `wc -l skills/crazy-professor/resources/archetype-keywords.txt`
Expected: between 6 and 10 lines (4 archetype + 2-6 comment lines).

- [ ] **Step 3: Stage the file (do NOT commit yet — single commit at end)**

Run: `git add skills/crazy-professor/resources/archetype-keywords.txt && git status --short`
Expected: `A  skills/crazy-professor/resources/archetype-keywords.txt` and no other staged changes.

---

## Task 2: `run_planner.py` skeleton + `archetype` subcommand

**Files:**
- Create: `skills/crazy-professor/scripts/run_planner.py`

- [ ] **Step 1: Write the skeleton with shared helpers and the `archetype` subcommand**

Create `skills/crazy-professor/scripts/run_planner.py`:

```python
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
    p = argparse.ArgumentParser(description="crazy-professor run planner")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("archetype", help="select archetype from topic keywords")
    a.add_argument("--topic", required=True)
    a.add_argument("--keywords", required=True, type=Path)

    args = p.parse_args()
    if args.cmd == "archetype":
        return cmd_archetype(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Verify the script is syntactically valid and `--help` works**

Run: `python skills/crazy-professor/scripts/run_planner.py --help`
Expected: usage line listing `archetype` subcommand, exit 0.

Run: `python skills/crazy-professor/scripts/run_planner.py archetype --help`
Expected: shows `--topic` and `--keywords` args, exit 0.

- [ ] **Step 3: Smoke-test the `archetype` subcommand against the real keywords file**

Run:
```bash
python skills/crazy-professor/scripts/run_planner.py archetype \
  --topic "deploy pipeline simplification" \
  --keywords skills/crazy-professor/resources/archetype-keywords.txt
```
Expected stdout (single line JSON, ensure_ascii false, exit 0):
```json
{"topic": "deploy pipeline simplification", "selected_archetype": "systems-alchemist", "selection_reason": "keyword_match", "matched_keywords": ["pipeline", "deploy"], "fallback_used": false, "topic_candidates": null}
```
(Order of `matched_keywords` may vary; `pipeline` and `deploy` both must be present.)

Run:
```bash
python skills/crazy-professor/scripts/run_planner.py archetype \
  --topic "xyzqrt foo bar" \
  --keywords skills/crazy-professor/resources/archetype-keywords.txt
```
Expected: `"fallback_used": true`, `"selected_archetype": null`, `"matched_keywords": []`, exit 0.

Run:
```bash
python skills/crazy-professor/scripts/run_planner.py archetype \
  --topic "" \
  --keywords skills/crazy-professor/resources/archetype-keywords.txt
```
Expected: `error: --topic is required and must not be empty` on stderr, exit 1.

Run:
```bash
python skills/crazy-professor/scripts/run_planner.py archetype \
  --topic "test" \
  --keywords /tmp/does-not-exist.txt
```
Expected: error mentioning the missing file on stderr, exit 2.

- [ ] **Step 4: Stage the file**

Run: `git add skills/crazy-professor/scripts/run_planner.py && git status --short`
Expected: `A  skills/crazy-professor/scripts/run_planner.py` plus the staged keywords file from Task 1.

---

## Task 3: `session` subcommand

**Files:**
- Modify: `skills/crazy-professor/scripts/run_planner.py`

- [ ] **Step 1: Add the `session`-subcommand parser registration in `main()`**

Edit `skills/crazy-professor/scripts/run_planner.py`. In `main()`, after the `archetype` subparser registration and before `args = p.parse_args()`, add:

```python
    s = sub.add_parser("session", help="extract topic candidates from session-summary files")
    s.add_argument("--session-path", action="append", required=True, type=Path,
                   metavar="PATH", help="repeatable; first listed has priority for dedup")
```

And in the dispatch block after the archetype branch, add:

```python
    if args.cmd == "session":
        return cmd_session(args)
```

- [ ] **Step 2: Add `extract_topic_candidates`, `read_session_file`, `cmd_session` functions**

Add the following functions to `run_planner.py`, after `select_archetype` and before `cmd_archetype`:

```python
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
```

- [ ] **Step 3: Smoke-test against the real session-summary files**

Run:
```bash
python skills/crazy-professor/scripts/run_planner.py session \
  --session-path .agent-memory/session-summary.md \
  --session-path ~/Desktop/.agent-memory/session-summary.md
```
Expected: JSON with `topic_candidates` containing 3 entries from the local + Desktop summaries. Each entry has `topic`, `source`, `rank` keys. Exit 0.

Verify by eye: at least one `topic` should match a bullet from the "Naechste Schritte" or "Open Items" section in the actual summary files.

- [ ] **Step 4: Smoke-test failure modes**

Run:
```bash
python skills/crazy-professor/scripts/run_planner.py session \
  --session-path /tmp/nope1.md \
  --session-path /tmp/nope2.md
```
Expected: `error: none of the 2 session paths were readable`, exit 3.

Run: `python skills/crazy-professor/scripts/run_planner.py session`
Expected: argparse error about missing required `--session-path`, exit 2 (argparse default).

- [ ] **Step 5: Stage the modified file**

Run: `git add skills/crazy-professor/scripts/run_planner.py && git diff --cached --stat`
Expected: `run_planner.py` now ~210 lines, increase from previous task.

---

## Task 4: `plan` subcommand

**Files:**
- Modify: `skills/crazy-professor/scripts/run_planner.py`

- [ ] **Step 1: Register the `plan` subcommand and dispatch**

In `main()` of `run_planner.py`, after the `session` subparser registration:

```python
    pl = sub.add_parser("plan", help="archetype + session combined")
    pl.add_argument("--topic", required=True)
    pl.add_argument("--keywords", required=True, type=Path)
    pl.add_argument("--session-path", action="append", required=True, type=Path,
                    metavar="PATH", help="repeatable")
```

In the dispatch block:

```python
    if args.cmd == "plan":
        return cmd_plan(args)
```

- [ ] **Step 2: Add `cmd_plan` function**

Add to `run_planner.py`, after `cmd_session`:

```python
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
```

- [ ] **Step 3: Smoke-test the combined subcommand**

Run:
```bash
python skills/crazy-professor/scripts/run_planner.py plan \
  --topic "deploy pipeline simplification" \
  --keywords skills/crazy-professor/resources/archetype-keywords.txt \
  --session-path .agent-memory/session-summary.md \
  --session-path ~/Desktop/.agent-memory/session-summary.md
```
Expected: JSON with `selected_archetype: "systems-alchemist"` AND `topic_candidates` populated with 3 entries. Exit 0.

- [ ] **Step 4: Smoke-test session-failure-with-archetype-success**

Run:
```bash
python skills/crazy-professor/scripts/run_planner.py plan \
  --topic "deploy pipeline" \
  --keywords skills/crazy-professor/resources/archetype-keywords.txt \
  --session-path /tmp/nope.md
```
Expected: archetype fields populated correctly (`selected_archetype: "systems-alchemist"`), `topic_candidates: null`, exit 0. (Per spec: session-failure does NOT fail `plan`; archetype-failure does.)

- [ ] **Step 5: Smoke-test archetype-failure-aborts**

Run:
```bash
python skills/crazy-professor/scripts/run_planner.py plan \
  --topic "test" \
  --keywords /tmp/does-not-exist.txt \
  --session-path .agent-memory/session-summary.md
```
Expected: error on stderr, exit 2. No JSON on stdout.

- [ ] **Step 6: Stage the file**

Run: `git add skills/crazy-professor/scripts/run_planner.py && git diff --cached --stat`
Expected: ~250 line file shown.

---

## Task 5: Eval-suite extension

**Files:**
- Modify: `skills/crazy-professor/scripts/eval_suite.py`

- [ ] **Step 1: Add `stage_b_run_planner_smoke` function**

Edit `skills/crazy-professor/scripts/eval_suite.py`. After `stage_b_telemetry_smoke` (around line 360, before `stage_c_live_stub`), add:

```python
def stage_b_run_planner_smoke(run_planner_script: Path,
                              keywords_path: Path,
                              tmp_dir: Path) -> dict:
    """Eight-assert smoke test for run_planner.py (since v0.10.0)."""
    if not run_planner_script.exists():
        return {"available": False,
                "reason": f"run_planner script not found: {run_planner_script}"}
    if not keywords_path.exists():
        return {"available": False,
                "reason": f"keywords file not found: {keywords_path}"}

    asserts: list[tuple[str, bool, str]] = []

    def call(args: list[str]) -> tuple[int, str, str]:
        proc = subprocess.run(
            [sys.executable, str(run_planner_script), *args],
            capture_output=True, text=True, timeout=10,
        )
        return proc.returncode, proc.stdout, proc.stderr

    # 1. archetype -- keyword match (deploy + pipeline -> systems-alchemist)
    rc, out, err = call(["archetype", "--topic",
                         "deploy pipeline simplification",
                         "--keywords", str(keywords_path)])
    ok_1 = False
    detail_1 = ""
    try:
        data = json.loads(out)
        ok_1 = (rc == 0
                and data.get("selected_archetype") == "systems-alchemist"
                and data.get("fallback_used") is False
                and "deploy" in data.get("matched_keywords", [])
                and "pipeline" in data.get("matched_keywords", []))
        if not ok_1:
            detail_1 = f"got rc={rc}, archetype={data.get('selected_archetype')!r}, matches={data.get('matched_keywords')}"
    except (json.JSONDecodeError, AttributeError) as exc:
        detail_1 = f"non-JSON stdout: {exc} / stderr={err.strip()[:120]}"
    asserts.append(("archetype keyword match", ok_1, detail_1))

    # 2. archetype -- no match
    rc, out, _ = call(["archetype", "--topic", "xyzqrt foo bar",
                       "--keywords", str(keywords_path)])
    ok_2 = False
    detail_2 = ""
    try:
        data = json.loads(out)
        ok_2 = (rc == 0
                and data.get("fallback_used") is True
                and data.get("selected_archetype") is None
                and data.get("matched_keywords") == [])
        if not ok_2:
            detail_2 = f"got rc={rc}, archetype={data.get('selected_archetype')!r}, fallback={data.get('fallback_used')}"
    except (json.JSONDecodeError, AttributeError) as exc:
        detail_2 = f"non-JSON stdout: {exc}"
    asserts.append(("archetype no match", ok_2, detail_2))

    # 3. archetype -- tie at position 1 -> fallback
    # Build a temp keywords file with a deliberate tie.
    tie_kw = tmp_dir / "tie-keywords.txt"
    tie_kw.write_text(
        "first-principles-jester: foo\n"
        "labyrinth-librarian: bar\n"
        "systems-alchemist: deploy\n"
        "radagast-brown: forest\n",
        encoding="utf-8",
    )
    rc, out, _ = call(["archetype", "--topic", "forest deploy",
                       "--keywords", str(tie_kw)])
    ok_3 = False
    detail_3 = ""
    try:
        data = json.loads(out)
        ok_3 = (rc == 0
                and data.get("fallback_used") is True
                and data.get("selected_archetype") is None)
        if not ok_3:
            detail_3 = f"got rc={rc}, archetype={data.get('selected_archetype')!r}"
    except (json.JSONDecodeError, AttributeError) as exc:
        detail_3 = f"non-JSON stdout: {exc}"
    asserts.append(("archetype tie -> fallback", ok_3, detail_3))

    # 4. archetype -- case-insensitive substring
    rc, out, _ = call(["archetype", "--topic", "DEPLOYS the SYSTEMS",
                       "--keywords", str(keywords_path)])
    ok_4 = False
    detail_4 = ""
    try:
        data = json.loads(out)
        matches = data.get("matched_keywords", [])
        ok_4 = (rc == 0
                and "deploy" in matches
                and "system" in matches)
        if not ok_4:
            detail_4 = f"got matches={matches}"
    except (json.JSONDecodeError, AttributeError) as exc:
        detail_4 = f"non-JSON stdout: {exc}"
    asserts.append(("archetype case-insensitive substring", ok_4, detail_4))

    # 5. archetype -- empty topic -> exit 1
    rc, _, _ = call(["archetype", "--topic", "",
                     "--keywords", str(keywords_path)])
    ok_5 = (rc == 1)
    detail_5 = "" if ok_5 else f"got rc={rc} expected 1"
    asserts.append(("archetype empty topic -> exit 1", ok_5, detail_5))

    # 6. archetype -- missing keywords file -> exit 2
    rc, _, _ = call(["archetype", "--topic", "deploy",
                     "--keywords", str(tmp_dir / "does-not-exist.txt")])
    ok_6 = (rc == 2)
    detail_6 = "" if ok_6 else f"got rc={rc} expected 2"
    asserts.append(("archetype missing keywords -> exit 2", ok_6, detail_6))

    # 7. session -- extract from "Naechste Schritte"
    sess_a = tmp_dir / "sess-a.md"
    sess_a.write_text(
        "# Test Session\n\n"
        "## Aktueller Stand\n\n- not me\n\n"
        "## Naechste Schritte\n\n"
        "1. **Phase 5 starten** in crazy-professor\n"
        "2. PR reviewen wenn er ankommt\n"
        "3. Codex hat letzte Session gehangen\n"
        "4. fourth bullet should not appear\n\n"
        "## Wichtige Pfade\n\n- ignored\n",
        encoding="utf-8",
    )
    rc, out, _ = call(["session", "--session-path", str(sess_a)])
    ok_7 = False
    detail_7 = ""
    try:
        data = json.loads(out)
        cands = data.get("topic_candidates", [])
        ok_7 = (rc == 0
                and len(cands) == 3
                and "Phase 5 starten" in cands[0]["topic"]
                and cands[0]["rank"] == 1
                and cands[0]["source"].lower().startswith("naechste")
                and cands[2]["rank"] == 3)
        if not ok_7:
            detail_7 = f"got rc={rc}, candidates={cands}"
    except (json.JSONDecodeError, AttributeError) as exc:
        detail_7 = f"non-JSON stdout: {exc}"
    asserts.append(("session naechste schritte extraction", ok_7, detail_7))

    # 8. session -- multiple paths, dedup
    sess_b = tmp_dir / "sess-b.md"
    sess_b.write_text(
        "## Open Items\n\n"
        "- duplicate bullet\n"
        "- new bullet from second file\n"
        "- another new one\n",
        encoding="utf-8",
    )
    sess_a_overlap = tmp_dir / "sess-a-overlap.md"
    sess_a_overlap.write_text(
        "## Naechste Schritte\n\n"
        "1. duplicate bullet\n"
        "2. unique-from-a\n",
        encoding="utf-8",
    )
    rc, out, _ = call(["session",
                       "--session-path", str(sess_a_overlap),
                       "--session-path", str(sess_b)])
    ok_8 = False
    detail_8 = ""
    try:
        data = json.loads(out)
        cands = data.get("topic_candidates", [])
        topics = [c["topic"] for c in cands]
        # First path provides "duplicate bullet" + "unique-from-a", second
        # path adds "new bullet from second file" (we cap at 3, dedup
        # drops the repeated "duplicate bullet" from the second file).
        ok_8 = (rc == 0
                and len(cands) == 3
                and topics.count("duplicate bullet") == 1
                and "unique-from-a" in topics
                and "new bullet from second file" in topics)
        if not ok_8:
            detail_8 = f"got rc={rc}, topics={topics}"
    except (json.JSONDecodeError, AttributeError) as exc:
        detail_8 = f"non-JSON stdout: {exc}"
    asserts.append(("session multi-path dedup", ok_8, detail_8))

    passed = sum(1 for _, ok, _ in asserts if ok)
    total = len(asserts)
    first_fail = next(((label, detail) for label, ok, detail in asserts if not ok), None)
    return {
        "available": True,
        "passed": passed == total,
        "passes": passed,
        "total": total,
        "asserts": [(label, ok) for label, ok, _ in asserts],
        "first_fail": first_fail,
    }
```

- [ ] **Step 2: Add `render_run_planner_section` for the report**

Add to `eval_suite.py`, after `render_telemetry_section` (around line 226):

```python
def render_run_planner_section(rp: dict) -> list[str]:
    lines: list[str] = ["", "## Run Planner smoke (Stage B)", ""]
    if not rp.get("available"):
        lines.append(f"Skipped: {rp.get('reason', 'run_planner script not available')}")
        return lines
    if rp.get("passed"):
        lines.append(f"PASS -- {rp['passes']}/{rp['total']} asserts")
    else:
        first = rp.get("first_fail")
        first_label = first[0] if first else "unknown"
        first_detail = first[1] if first else ""
        lines.append(f"FAIL -- {rp['passes']}/{rp['total']} asserts; "
                     f"first failure: {first_label}"
                     + (f" ({first_detail})" if first_detail else ""))
    lines.append("")
    for label, ok in rp.get("asserts", []):
        marker = "ok" if ok else "FAIL"
        lines.append(f"- {marker}: {label}")
    return lines
```

- [ ] **Step 3: Wire `--run-planner` and `--run-planner-keywords` into `main()` and `render_report()`**

Edit `eval_suite.py`. In `main()`, in the argparse block (after `--telemetry`):

```python
    p.add_argument("--run-planner", type=Path, default=None,
                   help="path to run_planner.py for the smoke test (default: skip)")
    p.add_argument("--run-planner-keywords", type=Path, default=None,
                   help="path to archetype-keywords.txt (required if --run-planner)")
```

After the telemetry-smoke block (before the `meta = {...}` line), add:

```python
    run_planner_results: dict | None = None
    if args.run_planner:
        if not args.run_planner_keywords:
            print("error: --run-planner-keywords is required when --run-planner is set",
                  file=sys.stderr)
            return 2
        print(f"running run_planner smoke test against {args.run_planner}...",
              file=sys.stderr)
        run_planner_results = stage_b_run_planner_smoke(
            args.run_planner, args.run_planner_keywords, tmp_dir,
        )
```

Update the `render_report` call to pass it:

```python
    report = render_report(picker_results, corpus_results, meta,
                           telemetry_results, run_planner_results)
```

Update `render_report` signature and body. Find the function and change the signature:

```python
def render_report(picker_results: dict, corpus_results: dict | None,
                  meta: dict, telemetry_results: dict | None = None,
                  run_planner_results: dict | None = None) -> str:
```

At the end of `render_report`, **before** the final `return "\n".join(lines) + "\n"`, add:

```python
    if run_planner_results is not None:
        lines.extend(render_run_planner_section(run_planner_results))
```

And in the early-return branch where `corpus_results is None`, add the same call before the `return`:

```python
        if telemetry_results is not None:
            lines.extend(render_telemetry_section(telemetry_results))
        if run_planner_results is not None:
            lines.extend(render_run_planner_section(run_planner_results))
        return "\n".join(lines) + "\n"
```

- [ ] **Step 4: Smoke-test eval-suite with the new run-planner block**

Run from repo root:
```bash
python skills/crazy-professor/scripts/eval_suite.py \
  --picker skills/crazy-professor/scripts/picker.py \
  --voice-linter skills/crazy-professor/scripts/lint_voice.py \
  --validator skills/crazy-professor/scripts/validate_output.py \
  --templates-dir skills/crazy-professor/prompt-templates \
  --field-notes-template skills/crazy-professor/resources/field-notes-init.md \
  --words skills/crazy-professor/resources/provocation-words.txt \
  --retired skills/crazy-professor/resources/retired-words.txt \
  --report-out /tmp/eval-test.md \
  --picker-runs 5 \
  --run-planner skills/crazy-professor/scripts/run_planner.py \
  --run-planner-keywords skills/crazy-professor/resources/archetype-keywords.txt
```
Expected: stderr shows "running run_planner smoke test...". Exit 0.

Run: `cat /tmp/eval-test.md | grep -A 20 "Run Planner smoke"`
Expected: section header `## Run Planner smoke (Stage B)`, then `PASS -- 8/8 asserts`, then 8 `- ok: <label>` lines.

If any assert fails: open `/tmp/eval-test.md`, read the first-fail detail, fix `run_planner.py`, re-run.

- [ ] **Step 5: Stage eval_suite.py**

Run: `git add skills/crazy-professor/scripts/eval_suite.py && git diff --cached --stat`
Expected: eval_suite.py shown as modified (+~150 lines).

---

## Task 6: operating-instructions.md update

**Files:**
- Modify: `skills/crazy-professor/references/operating-instructions.md`

- [ ] **Step 1: Read the current file to find the exact insertion points**

Run: `grep -n "^\\*\\*Step " skills/crazy-professor/references/operating-instructions.md`
Expected: list of step numbers. Note line numbers for Step 1, Step 2 (header), Step 7b.

- [ ] **Step 2: Add `--from-session` and `--dry-run` rules to Step 1**

Find the "Step 1: Parse the topic" block (around line 18). After the existing four-bullet topic-resolution contract (single/single-no-topic/chat/chat-no-topic), append two NEW bullets:

```markdown
- **Single-run with `--from-session` (since v0.10.0):** instead of
  parsing a literal topic, call the run-planner session subcommand to
  read `<cwd>/.agent-memory/session-summary.md` (and the Desktop
  equivalent as fallback) and extract 3 topic candidates from the
  "Naechste Schritte" + "Open Items" sections. Show them to the user as
  a numbered list and ask "Which? [1/2/3 or own]". The user's choice
  becomes the topic. If `topic_candidates` is empty (no readable file
  or no matching sections), fall back to the "single-run without topic"
  rule above.
- **Single-run with `--dry-run` (since v0.10.0):** the topic is parsed
  as usual, but Steps 3-7 are NOT executed. Steps 2a + 2b run
  (run-planner + picker), and the result is printed as a Markdown block
  on stdout (see Step 2c below). No file is written, no field-notes
  append, no telemetry append. Aborts before generation. Chat-mode
  retains its own `--chat --dry-run-round1` flag (different mechanism,
  unaffected).
```

- [ ] **Step 3: Replace Step 2 with Step 2a + 2b + 2c**

Find the "Step 2: Pick stochastic elements" block. The current block describes the picker call. Replace the whole Step 2 + Step 2b section (down to the end of "Rationale: field-notes.md is otherwise write-only..." at around line 99) with:

```markdown
**Step 2a: Run Planner -- archetype recommendation (since v0.10.0).**

Before calling the picker, ask the run-planner which archetype the
topic-keywords suggest:

```bash
python <repo-root>/skills/crazy-professor/scripts/run_planner.py archetype \
  --topic "<the parsed topic>" \
  --keywords <repo-root>/skills/crazy-professor/resources/archetype-keywords.txt
```

The script writes one JSON object to stdout. Parse it. Two outcomes:

- `selection_reason == "keyword_match"` AND `fallback_used == false` AND
  `selected_archetype` non-null: the selector hit. Pass
  `--force-archetype <selected_archetype>` to picker.py in Step 2b.
  `matched_keywords` is informational (used by Step 7b telemetry).
- `fallback_used == true`: no clear winner (zero matches OR tie at
  position 1). Call picker.py without `--force-archetype` -- the
  timestamp-mod fallback inside the picker takes over (the v0.9.0
  behavior).

If run_planner exits non-zero, print
`[run-planner: skipped -- exit code N]` once on stderr and proceed
WITHOUT `--force-archetype`. Run-planner is an optional layer; the
picker is the hard default.

**Step 2b: Pick stochastic elements (picker call).**

Preferred path (since v0.7.0): call the picker script. It encapsulates
the mod-4 archetype pick (or honors `--force-archetype`), the word
draw, the operator pick, AND the variation-guard from Step 2c (formerly
2b) in one deterministic call:

```bash
python <repo-root>/skills/crazy-professor/scripts/picker.py \
  --field-notes <target-project>/.agent-memory/lab/crazy-professor/field-notes.md \
  --words <repo-root>/skills/crazy-professor/resources/provocation-words.txt \
  --retired <repo-root>/skills/crazy-professor/resources/retired-words.txt \
  --init-template <repo-root>/skills/crazy-professor/resources/field-notes-init.md \
  --mode single \
  [--force-archetype <selected_archetype-from-step-2a-if-any>]
```

For chat-mode: `--mode chat` returns four picks (one per archetype) in
a single JSON object. (Chat-mode does NOT use Step 2a's
archetype-selector since all four archetypes run; the Run Planner is
single-run only in v0.10.0.)

The script writes one JSON object to stdout containing `archetype`,
`word`, `operator`, `re_rolled`, `timestamp`, `mode`. Parse it and
proceed with Step 3. The variation-guard from Step 2c is already
applied inside the script.

**Variation-guard vs. selector conflict:** if Step 2a recommended an
archetype that is in a 3-in-a-row streak in the last 10 field-notes
rows, the picker will override the recommendation
(`re_rolled: archetype` or `forced-archetype+archetype`). The
variation-guard always wins. The selector is a recommendation, the
guard is a hard constraint. This is the documented behavior.

**Fallback path (if Python is unavailable):**

- Archetype: take current UTC timestamp minute mod 4 (0=jester,
  1=librarian, 2=alchemist, 3=radagast-brown). Skip Step 2a entirely in
  this path. All four archetypes active since 2026-04-23.
- Provocation word: pick one random line from
  `<repo-root>/skills/crazy-professor/resources/provocation-words.txt`.
  Filter out words that appear in `retired-words.txt`.
- PO-operator: take timestamp second mod 3 (0=reversal,
  1=exaggeration, 2=escape).
- Then apply Step 2c manually.

**Step 2c: Variation guard (field-notes.md as forced input).**

Before accepting the Step 2b picks, read the last 10 rows of the "Log"
table in `.agent-memory/lab/crazy-professor/field-notes.md` (fewer if
the log is shorter). Apply these two rules in order:

- Archetype guard: if the same archetype appears in the last 3
  consecutive rows AND the Step 2b pick would make it a 4th, discard
  the pick and choose one of the other three archetypes (respecting
  the Radagast latency -- if radagast-brown is still gated, choose
  from the remaining two). Tie-break: whichever of the candidates
  appeared least recently in the log, then alphabetical.
- Word guard: if the Step 2b word appears anywhere in the last 10
  rows, draw another word from `provocation-words.txt` (still
  filtering against `retired-words.txt`). Repeat until a word is found
  that is not in the last 10 rows. If the pool is exhausted (every
  remaining word is in the window), accept the least-recently-used
  word.

Record the guard outcome for Step 7: one of `no`, `archetype`, `word`,
`both`, `forced-archetype`, or `forced-archetype+<other>`. This value
goes into the `re-rolled` column in field-notes.md.

Rationale: field-notes.md is otherwise write-only. Reading it before
the picker turns the log into backpressure that prevents
archetype/word clustering across sessions. Not total prohibition --
just anti-streak.
```

(Note: the previous Step 2b becomes Step 2c. The previous Step 2 split into Step 2a + Step 2b. Subsequent steps 3-7 keep their numbers.)

- [ ] **Step 4: Add Step 2d for the dry-run path**

Immediately after the Step 2c block, insert:

```markdown
**Step 2d: Dry-run output (when `--dry-run` is set, since v0.10.0).**

If the user invoked `/crazy <topic> --dry-run`, do NOT proceed to
Step 3. Instead, print the following Markdown block on stdout and stop:

```
### Crazy Professor -- Dry Run

Topic: "<the parsed topic>"

Run Planner:
  Archetype: <selected_archetype or "(fallback)">
    Selector reason: <"keyword_match" or "fallback (no match)" or "fallback (tie)">
    Matched keywords: [<keywords> or "(none)"]

Picker:
  Word: <picked word>
  Operator: <picked operator>
  Re-rolled: <re_rolled value>
  Timestamp: <picker timestamp>

Field-notes context:
  Rows read: <field_notes_rows_read>
  Last 10 archetypes: [<archetype list, oldest first>]

Variation Guard: <"streak detected -> override" or "no streak">

ABORT before generation. No file written, no telemetry, no field-notes.
```

This block is the ONLY output for a dry-run invocation. Do not run
Steps 3-7.
```

- [ ] **Step 5: Update Step 7b telemetry schema for new optional fields**

Find the Step 7b block. After the example JSON template, add:

```markdown
**New optional fields since v0.10.0** (Phase-5 substrate):

- `archetype_selector_used` (bool): true if Step 2a's run-planner
  selector recommended an archetype (`selection_reason ==
  "keyword_match"`). False if `fallback_used == true` or run-planner
  was skipped. Optional: omit if main-model has no signal.
- `archetype_selector_matched_kw` (list[str]): the `matched_keywords`
  array from run-planner output. Empty list when fallback was used or
  when the field above is false. Optional.

Both fields break no existing readers (Phase-4 contract: new fields
must be optional, never required). The patch-suggester will read these
fields once enough data accumulates.
```

- [ ] **Step 6: Smoke-check the file is still well-formed Markdown**

Run: `wc -l skills/crazy-professor/references/operating-instructions.md`
Expected: file grew by ~80-100 lines from previous ~330 to ~410-430.

Run: `grep -c "^\\*\\*Step " skills/crazy-professor/references/operating-instructions.md`
Expected: count grew by 3 (Step 2a, Step 2c re-numbering, Step 2d). Was 14, now ~17.

- [ ] **Step 7: Stage the file**

Run: `git add skills/crazy-professor/references/operating-instructions.md`

---

## Task 7: commands/crazy.md update

**Files:**
- Modify: `commands/crazy.md`

- [ ] **Step 1: Update `argument-hint` and topic-resolution contract**

Read `commands/crazy.md`. Replace the frontmatter line `argument-hint: [topic] [--chat]` with:

```yaml
argument-hint: [topic] [--chat] [--from-session] [--dry-run]
```

In the "Topic resolution" block, after the existing four bullets (empty, topic, chat, chat-no-topic), add two new bullets:

```markdown
- If `$ARGUMENTS` contains `--from-session` (since v0.10.0), call run-planner's `session` subcommand to extract 3 topic candidates from the local + Desktop session-summary files. Show them to the user as a numbered list and ask which one (or "own"). On a chosen number, dispatch to single-run mode with that bullet as the topic. On "own" or empty, fall back to the standard single-run-without-topic rule. If `--dry-run` is also set, the chosen topic still goes through the dry-run path below.
- If `$ARGUMENTS` contains `--dry-run` (since v0.10.0, single-run only), parse the topic per the rules above, run the picker, and print the dry-run preview block as defined in operating-instructions Step 2d. Do NOT generate provocations, do NOT write any file, do NOT append to field-notes or telemetry. Combining `--dry-run` with `--chat` is rejected: print `--dry-run is single-run only. Use --chat --dry-run-round1 for chat-mode preview.` and stop.
```

- [ ] **Step 2: Smoke-check the file**

Run: `head -15 commands/crazy.md`
Expected: frontmatter still valid YAML, `argument-hint` line shows all four flags.

- [ ] **Step 3: Stage**

Run: `git add commands/crazy.md`

---

## Task 8: README.md update

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add `--from-session` and `--dry-run` to the trigger section**

Read `README.md`. Find the slash-command code-block (around line 30):

```text
/crazy <topic>
/crazy <topic> --chat
```

Replace with:

```text
/crazy <topic>
/crazy <topic> --chat
/crazy <topic> --dry-run
/crazy --from-session
```

In the "Topic resolution" bullet list directly below, after the chat-mode-without-topic bullet, append:

```markdown
- **`--from-session`** -- skill reads `<cwd>/.agent-memory/session-summary.md` (and the Desktop session-summary as fallback), extracts 3 topic candidates from the "Naechste Schritte" / "Open Items" sections, and asks the user which to use.
- **`--dry-run`** (single-run only) -- skill runs the run-planner + picker but stops before generation. Prints the chosen archetype, word, operator, and the variation-guard state. Useful for debugging the run-planner logic without producing an output file.
```

- [ ] **Step 2: Stage**

Run: `git add README.md`

---

## Task 9: Version bump v0.9.0 → v0.10.0

**Files (8 frontmatter files per VERSIONING.md):**
- Modify: `.claude-plugin/plugin.json`
- Modify: `skills/crazy-professor/SKILL.md`
- Modify: `skills/crazy-professor/resources/output-template.md`
- Modify: `skills/crazy-professor/resources/chat-output-template.md`
- Modify: `docs/chat-mode-flow.md` (frontmatter + embedded example)
- Modify: `skills/crazy-professor/prompt-templates/chat-curator.md`
- Modify: `skills/crazy-professor/prompt-templates/chat-round-1-wrapper.md`
- Modify: `skills/crazy-professor/prompt-templates/chat-round-2-wrapper.md`

- [ ] **Step 1: Bump plugin.json (single source of truth)**

Read `.claude-plugin/plugin.json`. Edit the `"version"` field from `"0.9.0"` to `"0.10.0"`. Description string stays unchanged.

- [ ] **Step 2: Bump SKILL.md frontmatter**

Read `skills/crazy-professor/SKILL.md`. In the YAML frontmatter at the top, find `version: 0.9.0` (in the metadata block) and change to `version: 0.10.0`.

- [ ] **Step 3: Bump output-template.md and chat-output-template.md**

For each: read the file, locate the embedded `version: 0.9.0` field in the frontmatter, change to `version: 0.10.0`. There are two instances (one per file).

- [ ] **Step 4: Bump docs/chat-mode-flow.md**

Read `docs/chat-mode-flow.md`. There are TWO version mentions:
1. The file's own frontmatter `version: 0.9.0` -> `version: 0.10.0`.
2. An embedded example showing the chat-mode output frontmatter (around line 189 per the v0.9.0 wrap-up). Change `version: 0.9.0` -> `version: 0.10.0` there too.

- [ ] **Step 5: Bump three prompt-template files**

For each of `chat-curator.md`, `chat-round-1-wrapper.md`, `chat-round-2-wrapper.md` in `skills/crazy-professor/prompt-templates/`: read the frontmatter, change `version: 0.9.0` -> `version: 0.10.0`.

- [ ] **Step 6: Verify no stragglers**

Run:
```bash
grep -rn "version: 0.9.0\|\"version\": \"0.9.0\"" \
  skills/crazy-professor/ \
  .claude-plugin/ \
  docs/chat-mode-flow.md \
  README.md
```
Expected: zero matches in active files. Historical mentions in CHANGELOG.md, plans, and CAPABILITIES.md (e.g. "stabilized 2026-04-23 (v0.5.1)" or "v0.9.0 released 2026-04-27") are FACTS about the past per VERSIONING.md and MUST stay unchanged. The grep above intentionally excludes those paths.

Also verify v0.10.0 appears in the right files:
```bash
grep -rn "version: 0.10.0\|\"version\": \"0.10.0\"" \
  skills/crazy-professor/ \
  .claude-plugin/ \
  docs/chat-mode-flow.md
```
Expected: 9 matches (1 plugin.json + 1 SKILL.md + 2 output templates + 2 in chat-mode-flow.md + 3 prompt templates).

- [ ] **Step 7: Stage all eight files**

Run:
```bash
git add .claude-plugin/plugin.json \
  skills/crazy-professor/SKILL.md \
  skills/crazy-professor/resources/output-template.md \
  skills/crazy-professor/resources/chat-output-template.md \
  docs/chat-mode-flow.md \
  skills/crazy-professor/prompt-templates/chat-curator.md \
  skills/crazy-professor/prompt-templates/chat-round-1-wrapper.md \
  skills/crazy-professor/prompt-templates/chat-round-2-wrapper.md
git diff --cached --stat
```
Expected: 8 files in the diff stat.

---

## Task 10: docs/ sync (PROJECT, CAPABILITIES, CHANGELOG, master-plan)

**Files:**
- Modify: `docs/PROJECT.md`
- Modify: `docs/CAPABILITIES.md`
- Modify: `docs/CHANGELOG.md`
- Modify: `docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md`

- [ ] **Step 1: Update docs/PROJECT.md**

Read `docs/PROJECT.md`. Find the roadmap checkbox list (around line 35). Change:
```markdown
- [ ] Phase 5: Run-Planner (Archetype-Selector + `--from-session` + `--dry-run`)
```
to:
```markdown
- [x] Phase 5: Run-Planner (Archetype-Selector + `--from-session` + `--dry-run`) -- 2026-04-28 (v0.10.0)
```

Also find the "Aktueller Stand" line (or equivalent latest-version status indicator). If it mentions v0.9.0, update to v0.10.0.

- [ ] **Step 2: Update docs/CAPABILITIES.md**

Read `docs/CAPABILITIES.md`. Find the Run-Planner row (around line 24). Change:
```markdown
| Run-Planner | geplant | — | Phase 5: Archetype-Selector aus Topic + `--from-session` |
```
to:
```markdown
| Run-Planner | aktiv (v0.10.0) | 2026-04-28 | Archetype-Selector aus Topic-Keywords + `--from-session` Topic-Vorschlag aus session-summary + `--dry-run` Picker-Preview |
```

- [ ] **Step 3: Append CHANGELOG entry**

Read `docs/CHANGELOG.md`. The most recent entry is v0.9.0 (Phase 4). Prepend a NEW v0.10.0 entry (CHANGELOG is reverse-chronological, newest on top, after the file header):

```markdown
## v0.10.0 -- 2026-04-28

**Phase 5: Run Planner + `--dry-run`**

- New helper script `skills/crazy-professor/scripts/run_planner.py` (stdlib-only) with three subcommands:
  - `archetype` -- topic-keyword score-match -> archetype recommendation. Tie / no-match -> fallback flag.
  - `session` -- reads one or more session-summary.md files, extracts up to 3 topic candidates from "Naechste Schritte" / "Open Items" sections.
  - `plan` -- both combined.
- New resource `skills/crazy-professor/resources/archetype-keywords.txt` (~80 keywords across the four archetypes).
- New command flag `--from-session`: skill suggests 3 topic candidates from the local + Desktop session-summary; user picks one.
- New command flag `--dry-run` (single-run only): runs run-planner + picker, prints Markdown preview block, aborts before generation. Side-effect-free (no output file, no field-notes append, no telemetry append).
- operating-instructions.md: Step 2 split into Step 2a (run-planner archetype recommendation) + Step 2b (picker call) + Step 2c (variation guard, formerly 2b) + Step 2d (dry-run output). Variation-guard always wins over the selector.
- Telemetry schema gets two new OPTIONAL fields: `archetype_selector_used` (bool), `archetype_selector_matched_kw` (list[str]). Phase-4 contract honored (new fields must be optional).
- eval_suite.py: new `stage_b_run_planner_smoke()` with 8 deterministic asserts; new `--run-planner` and `--run-planner-keywords` CLI args; new "Run Planner smoke (Stage B)" report section.

```

- [ ] **Step 4: Update master-plan status**

Read `docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md`. Find the Phasen-Tabelle row for Phase 5 (around line 25):

```markdown
| 5     | **Run Planner**                                                      | Archetype-Selector + `--from-session` als gemeinsame Schicht; `--dry-run` für Picker-Vorschau           | ⏳     |
```

Change the status cell from `⏳` to `✅ (2026-04-28)`.

- [ ] **Step 5: Stage docs**

Run:
```bash
git add docs/PROJECT.md docs/CAPABILITIES.md docs/CHANGELOG.md \
  docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md
git diff --cached --stat
```
Expected: 4 files in the stat.

---

## Task 11: Self-verification

**Files:** none (read-only checks)

- [ ] **Step 1: Run the eval-suite end-to-end**

Run:
```bash
python skills/crazy-professor/scripts/eval_suite.py \
  --picker skills/crazy-professor/scripts/picker.py \
  --voice-linter skills/crazy-professor/scripts/lint_voice.py \
  --validator skills/crazy-professor/scripts/validate_output.py \
  --templates-dir skills/crazy-professor/prompt-templates \
  --field-notes-template skills/crazy-professor/resources/field-notes-init.md \
  --words skills/crazy-professor/resources/provocation-words.txt \
  --retired skills/crazy-professor/resources/retired-words.txt \
  --report-out docs/eval-baseline-2026-04-28.md \
  --picker-runs 50 \
  --telemetry skills/crazy-professor/scripts/telemetry.py \
  --run-planner skills/crazy-professor/scripts/run_planner.py \
  --run-planner-keywords skills/crazy-professor/resources/archetype-keywords.txt \
  --skill-version 0.10.0
```
Expected: stderr shows picker, telemetry, and run_planner phases. Exit 0. Report file written to `docs/eval-baseline-2026-04-28.md`.

Run: `grep "PASS\|FAIL\|pass:\|fail:" docs/eval-baseline-2026-04-28.md`
Expected: every block shows PASS. Specifically: `## Run Planner smoke (Stage B)` followed by `PASS -- 8/8 asserts`.

If the eval-baseline shows any FAIL: stop, fix the underlying issue, re-run.

- [ ] **Step 2: Manual smoke -- dry-run preview**

Read the operating-instructions Step 2d block and confirm it matches the markdown the skill is expected to print. (No script call here -- this is a doc-cross-check.) The skill is invoked through Claude/Codex; for verification, run the underlying scripts directly:

```bash
python skills/crazy-professor/scripts/run_planner.py archetype \
  --topic "deploy pipeline simplification" \
  --keywords skills/crazy-professor/resources/archetype-keywords.txt
```
Expected: JSON, `selected_archetype: "systems-alchemist"`, `matched_keywords` includes `deploy` + `pipeline`.

```bash
python skills/crazy-professor/scripts/picker.py \
  --field-notes /tmp/test-field-notes.md \
  --words skills/crazy-professor/resources/provocation-words.txt \
  --retired skills/crazy-professor/resources/retired-words.txt \
  --init-template skills/crazy-professor/resources/field-notes-init.md \
  --mode single \
  --force-archetype systems-alchemist
```
Expected: JSON with `archetype: "systems-alchemist"`, valid word and operator. Verify `/tmp/test-field-notes.md` was created (init-template path).

- [ ] **Step 3: Verify the version bump is consistent**

Run:
```bash
grep -rn "version: 0.9.0\|\"version\": \"0.9.0\"" \
  skills/crazy-professor/ .claude-plugin/ docs/chat-mode-flow.md README.md
```
Expected: zero matches.

```bash
grep -rn "0.10.0" .claude-plugin/plugin.json skills/crazy-professor/SKILL.md
```
Expected: each file shows the v0.10.0 string in the frontmatter.

- [ ] **Step 4: Verify the master-plan status changed**

Run: `grep "Phase 5\|Run Planner" docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md | head -5`
Expected: `✅ (2026-04-28)` next to "Run Planner".

- [ ] **Step 5: Verify all 8 frontmatter files + 4 docs are staged**

Run: `git diff --cached --stat`
Expected: roughly 16-18 files staged. List should include:
- 1x archetype-keywords.txt (Task 1)
- 1x run_planner.py (Tasks 2-4)
- 1x eval_suite.py (Task 5)
- 1x operating-instructions.md (Task 6)
- 1x commands/crazy.md (Task 7)
- 1x README.md (Task 8)
- 8x version-bump files (Task 9)
- 4x docs (Task 10)
- 1x docs/eval-baseline-2026-04-28.md (Task 11 step 1)

Also no unstaged files that should be staged:
```bash
git status --short
```
Expected: only `M` (modified-staged) and `A` (added-staged) lines, no `??` (untracked) lines for repo content.

- [ ] **Step 6: Verify the spec file referenced in CHANGELOG and the actual spec match**

Run: `head -10 docs/specs/2026-04-28-phase-5-run-planner-design.md`
Expected: frontmatter `target_version: v0.10.0` matches what we just shipped.

(Note: Codex-Verifier subagent is deferred per Phase-4 pattern -- 4 sessions in a row of subagent hangs. Self-verification above replaces the Codex-Verifier role for this phase.)

- [ ] **Step 7: Stage the eval-baseline file**

Run: `git add docs/eval-baseline-2026-04-28.md`

---

## Task 12: Single commit + push

**Files:** all staged from Tasks 1-11.

- [ ] **Step 1: Final review of staged content**

Run: `git diff --cached --stat`
Expected: ~16-18 files. No surprise files. Roughly:

```
 .claude-plugin/plugin.json                                                   |  2 +-
 README.md                                                                    |  ~6 ++-
 commands/crazy.md                                                            |  ~6 ++-
 docs/CAPABILITIES.md                                                         |  ~2 +-
 docs/CHANGELOG.md                                                            | ~20 +++++++
 docs/PROJECT.md                                                              |  ~4 +-
 docs/chat-mode-flow.md                                                       |  ~4 +-
 docs/eval-baseline-2026-04-28.md                                             | ~80 ++++++
 docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md            |  ~2 +-
 skills/crazy-professor/SKILL.md                                              |  ~2 +-
 skills/crazy-professor/prompt-templates/chat-curator.md                      |  ~2 +-
 skills/crazy-professor/prompt-templates/chat-round-1-wrapper.md              |  ~2 +-
 skills/crazy-professor/prompt-templates/chat-round-2-wrapper.md              |  ~2 +-
 skills/crazy-professor/references/operating-instructions.md                  | ~100 ++++
 skills/crazy-professor/resources/archetype-keywords.txt                      |  ~8 ++++
 skills/crazy-professor/resources/chat-output-template.md                     |  ~2 +-
 skills/crazy-professor/resources/output-template.md                          |  ~2 +-
 skills/crazy-professor/scripts/eval_suite.py                                 | ~150 +++++++
 skills/crazy-professor/scripts/run_planner.py                                | ~280 +++++++
```

- [ ] **Step 2: Create the commit**

Run:
```bash
git commit -m "$(cat <<'EOF'
crazy-professor | v0.10.0: Phase-5 — Run Planner + --dry-run

Run Planner is a topic-aware archetype selector (substring match against
archetype-keywords.txt) plus a session-summary topic suggester. New
script run_planner.py with subcommands: archetype, session, plan.
Picker stays unchanged; variation-guard always wins over selector.

--from-session reads <cwd>/.agent-memory/session-summary.md and the
Desktop equivalent, extracts up to 3 candidates from "Naechste
Schritte" + "Open Items" sections.

--dry-run prints a Markdown preview block (run-planner + picker output)
and aborts before generation. Side-effect-free.

Operating-instructions Step 2 split into 2a (selector) + 2b (picker) +
2c (variation guard, was 2b) + 2d (dry-run output). Telemetry schema
extended with two optional fields: archetype_selector_used,
archetype_selector_matched_kw.

eval_suite.py: stage_b_run_planner_smoke (8 asserts) +
render_run_planner_section + --run-planner / --run-planner-keywords
CLI args.

Master-Plan Phase 5 -> ✅ (2026-04-28). 4/8 -> 5/8 phases complete.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```
Expected: commit succeeds. Output shows ~16-18 files, ~600+ insertions.

- [ ] **Step 3: Verify commit**

Run: `git log --oneline -3`
Expected: top-of-log shows `crazy-professor | v0.10.0: Phase-5 — Run Planner + --dry-run`.

Run: `git status`
Expected: `working tree clean` and `Your branch is ahead of 'origin/master' by 1 commit`.

- [ ] **Step 4: Push to origin/master**

Run: `git push origin master`
Expected: push succeeds, no force-flag needed.

Run: `git status`
Expected: `working tree clean` and `Your branch is up to date with 'origin/master'`.

---

## Out of scope (deferred to Phase 6+)

- LLM-based archetype selector
- Keyword weighting in archetype-keywords.txt
- Min-score threshold for selector confidence
- Topic-driven operator selection (master-plan open question)
- Global `~/.claude/state/` topic pool
- `--from-session` for chat-mode
- `--require-session` strict-mode flag
- End-to-end `--dry-run` test inside eval_suite.py (skill-flow flag, not script behavior)

These are documented in the spec under "Open questions deliberately deferred". Do not pull them into this plan.
