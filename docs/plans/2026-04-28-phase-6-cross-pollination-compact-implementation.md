# Phase 6 — Cross-Pollination + Kompakt-Modus Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three Chat-Mode extensions to crazy-professor as v0.11.0 — `--chat --compact` (reorder + audit-trail), `--strict-cross-pollination` (deterministic substance heuristic via 4th linter), and the `wishful-thinking` PO operator (configurable share weight).

**Architecture:** 6.1 changes the chat output ordering and adds a `compact` frontmatter branch in `validate_output.py` (no new script). 6.2 adds a new stdlib-only Python helper `lint_cross_pollination.py` plus a stop-words resource; the skill calls it from a new Step C4b and edits R2 lines in-place with `[low-substance: <reason>]` markers (warn-only). 6.3 extends `picker.py` operator list by one entry guarded by a `--wishful-share` CLI flag (default 0.25, relative weight via `random.choices(weights=[1, 1, 1, share*3])`). Three new optional telemetry fields. Three new eval-suite stages (C/D/E). Single MINOR version bump v0.10.0 -> v0.11.0 across 8 frontmatter files.

**Tech Stack:** Python 3 stdlib (argparse, json, pathlib, re, sys, datetime, random). No new deps. Markdown for docs and templates. Git for version-control commits.

**Spec reference:** `docs/specs/2026-04-28-phase-6-cross-pollination-compact-design.md` (commit `9e854ce`).

**Repo paths:**
- Repo root: `C:/Users/domes/Desktop/Claude-Plugins-Skills/crazy-professor`
- All script paths below are relative to that root.

**Commit cadence:** one commit per task at the end of the task. Final phase-completion commit consolidates the version bump + docs (Task 13).

**Implementation order:** 6.1 (Tasks 1-3) -> 6.2 (Tasks 4-7) -> 6.3 (Tasks 8-10) -> Telemetry (Task 11) -> Eval-Suite (Task 12) -> Docs + Version Bump + Push (Task 13).

---

## Task 1: `chat-output-template.md` — add `compact` block

**Files:**
- Modify: `skills/crazy-professor/resources/chat-output-template.md`

- [ ] **Step 1: Add a `compact: <true|false>` field to the frontmatter example**

Open `skills/crazy-professor/resources/chat-output-template.md`. Inside the frontmatter block (between line 11 `---` and line 29 `---`), insert one new line right after the `mode: chat` line:

Find:
```yaml
---
skill: crazy-professor
mode: chat
version: 0.10.0
```

Replace with:
```yaml
---
skill: crazy-professor
mode: chat
compact: <true | false>
version: 0.10.0
```

(The version stays `0.10.0` for now — the version bump happens in Task 13. Don't touch the version field yet.)

- [ ] **Step 2: Append a Compact-Mode body example at the end of the file**

Append this block at the very end of `chat-output-template.md` (after the last existing line). This documents the alternative body order for `compact: true` and is rendered into a synthetic test fixture later:

````markdown

---

## Compact-Mode Body (when `compact: true`)

When `compact: true` is set in the frontmatter, the body uses a different
order: Round 3 + Top-3 + Next-Experiment + Self-Flag come first, and
Round 1 + Round 2 are wrapped in a single `<details>`-block at the bottom
as an audit-trail. The frontmatter is unchanged; only the body order
flips.

```markdown
# Chat: <topic>

**Mode:** chat | **Compact:** true | **Distiller:** <codex|claude-fallback>

> DIVERGENCE WARNING: This output is provocation material, not advice.
> ... (same banner as normal mode)

## Round 3 — Codex Distillation (Final 20)

### Jester-5
1. ...
5. ...

### Librarian-5
### Alchemist-5
### Radagast-5

## Top-3 Cross-Pollination Hits
1. ...
2. ...
3. ...

## Next Experiment (one, only)
...

## Self-Flag (for field-notes.md)
- [ ] kept
- [ ] round2-was-degraded
- [ ] distiller-fallback-used
- [ ] voice-cross-drift

---

<details>
<summary>Audit-Trail — Round 1 + Round 2 (click to expand)</summary>

## Round 1 — Parallel Voices (5 Provocations per Archetype)

### Jester (word: <w>, operator: <op>)
1. ...
5. ...

### Librarian ...
### Alchemist ...
### Radagast ...

## Round 2 — Cross-Pollination (2-3 per Archetype, counter/extend)

### Jester — Runde 2
- counter: <archetype> #<n> — <provokation> — anchor: <link>
...

### Librarian — Runde 2
### Alchemist — Runde 2
### Radagast — Runde 2

</details>
```

### Notes on compact mode

- **`<details>` tag is HTML in Markdown** and renders as a collapsible
  block in GitHub, Obsidian, and VS Code. Plain-text rendering still
  shows the content inline.
- **R2-degraded edge case:** if `round2_status: degraded`, the `<details>`
  block contains only Round 1 plus a "Round 2 — skipped (degraded)" line
  in place of the R2 sub-headings. Mirrors normal-mode behavior.
- **`--strict-cross-pollination` markers** (`[low-substance: <reason>]`)
  appear inside the `<details>` block in compact mode. Codex-distillation
  in Round 3 still sees the markers as part of its R2 input.
````

- [ ] **Step 3: Commit Task 1**

```bash
git add skills/crazy-professor/resources/chat-output-template.md
git commit -m "crazy-professor | Phase-6 Task 1: chat-output-template — add compact-mode body example

Adds compact: <true|false> frontmatter field and appended Compact-Mode body
template (Round 3 first, R1+R2 in <details>-audit-trail). Version stays
0.10.0; bumped in Task 13.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: `commands/crazy.md` — accept and gate `--compact`

**Files:**
- Modify: `commands/crazy.md`

- [ ] **Step 1: Add `--compact` to the argument-hint and add the gate rule**

Open `commands/crazy.md`. Find this frontmatter line:

```yaml
argument-hint: [topic] [--chat] [--from-session] [--dry-run]
```

Replace with:

```yaml
argument-hint: [topic] [--chat] [--from-session] [--dry-run] [--compact] [--strict-cross-pollination]
```

Then in the body, find the bullet list of topic-resolution rules. The last rule today is the `--dry-run` one (line 20). Append two new bullets immediately after that line, before the empty line:

```markdown
- If `$ARGUMENTS` contains `--compact` (since v0.11.0, chat-mode only), the chat output is reordered: Round 3 (Final 20) + Top-3 + Next-Experiment + Self-Flag appear first, Round 1 + Round 2 collapse into a `<details>` audit-trail block at the end. The frontmatter field `compact: true` is set. If `--compact` is given without `--chat`, **reject explicitly** and stop. Return: `--compact requires --chat. Single-run output is already flat.`
- If `$ARGUMENTS` contains `--strict-cross-pollination` (since v0.11.0, chat-mode only), Step C4b runs `lint_cross_pollination.py` against the Round 2 output. Findings appear as `[low-substance: <reason>]` markers in the affected R2 lines (warn-only — no items are filtered or removed). The telemetry field `low_substance_hits` records the count. If given without `--chat`, the flag is silently a no-op (single-run has no Round 2). All other flags compose normally: `--chat --compact --strict-cross-pollination` is the full Phase-6 surface.
```

- [ ] **Step 2: Verify the file**

Run: `cat commands/crazy.md` and confirm the two new bullets are present and the argument-hint line now lists `--compact` and `--strict-cross-pollination`.

- [ ] **Step 3: Commit Task 2**

```bash
git add commands/crazy.md
git commit -m "crazy-professor | Phase-6 Task 2: commands/crazy.md — accept --compact and --strict-cross-pollination

--compact rejected without --chat (mirrors --dry-run --chat reject pattern).
--strict-cross-pollination silent no-op without --chat (single-run has no R2).
Both flags compose with --chat freely.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: `validate_output.py` — branch on `compact: true`

**Files:**
- Modify: `skills/crazy-professor/scripts/validate_output.py`

- [ ] **Step 1: Add a helper that checks the body order**

Open `skills/crazy-professor/scripts/validate_output.py`. Right above the `validate_chat` function (around line 157), insert this new helper function. It returns the indices of the major chat-mode section headers in body order:

```python
def section_order(body: str) -> list[str]:
    """Return the list of major chat-mode section labels in the order they appear.
    Skips section headers that aren't part of the chat-mode flow.
    """
    labels = []
    targets = [
        ("Round 1", r"^Round 1"),
        ("Round 2", r"^Round 2"),
        ("Round 3", r"^Round 3"),
        ("Top-3", r"^Top-3"),
        ("Next Experiment", r"^Next Experiment"),
        ("Self-Flag", r"^Self-Flag"),
    ]
    lines = body.splitlines()
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if not m:
            continue
        text = m.group(2)
        for label, pattern in targets:
            if re.match(pattern, text):
                labels.append(label)
                break
    return labels
```

- [ ] **Step 2: Update `validate_chat` to branch on the `compact` frontmatter field**

Inside `validate_chat` (line 157+), replace the section-presence loop and Round 3 / Top-3 / Next-Experiment checks with a compact-aware version. Find the existing block:

```python
    check_divergence_banner(body, issues)

    # Three rounds present
    for round_name in ("Round 1", "Round 2", "Round 3"):
        start, _ = find_section_lines(body, rf"^{round_name}")
        if start < 0:
            issues.append(f"missing '## {round_name}' section")
```

Replace the entire block from `check_divergence_banner(body, issues)` down through (but NOT including) the existing `# Top-3 Cross-Pollination` comment, with this expanded block. The new block keeps every existing assertion and adds order-validation:

```python
    check_divergence_banner(body, issues)

    compact_str = (fm.get("compact") or "").strip().lower()
    compact = compact_str == "true"

    # Three rounds present (R1+R2 may live inside a <details> in compact mode)
    for round_name in ("Round 1", "Round 2", "Round 3"):
        start, _ = find_section_lines(body, rf"^{round_name}")
        if start < 0:
            issues.append(f"missing '## {round_name}' section")

    # Compact-mode order check: Round 3, Top-3, Next Experiment, Self-Flag
    # come BEFORE Round 1 and Round 2.
    order = section_order(body)
    if compact:
        # in compact: R3 + Top-3 + Next + Self-Flag should all appear before R1
        try:
            r1_idx = order.index("Round 1")
        except ValueError:
            r1_idx = 10**9  # not found — separate issue already raised above
        for primary in ("Round 3", "Top-3", "Next Experiment", "Self-Flag"):
            if primary in order and order.index(primary) > r1_idx:
                issues.append(
                    f"compact-mode order violation: '{primary}' must appear "
                    f"before 'Round 1' but came later"
                )
    else:
        # normal mode: R1 first, R3 after R2, Self-Flag last
        try:
            r1_idx = order.index("Round 1")
            r3_idx = order.index("Round 3")
            if r1_idx > r3_idx:
                issues.append(
                    "normal-mode order violation: 'Round 1' must precede 'Round 3'"
                )
        except ValueError:
            pass  # missing-section issue already raised
```

- [ ] **Step 3: Verify the validator still parses today's outputs**

Pick any existing chat-mode output you have around. If none exists, skip to Step 4.

Run (from repo root): `python skills/crazy-professor/scripts/validate_output.py --mode chat <path-to-existing-chat-output>.md`

Expected: exit code 0 (no errors), nothing on stderr. The new code path treats missing/empty `compact` as `compact: false`, which is the today-mode.

- [ ] **Step 4: Spot-check the new helper with a synthetic input**

Write a small ad-hoc test in a temp file (don't commit this — just verify behavior locally):

```bash
python -c "
import sys
sys.path.insert(0, 'skills/crazy-professor/scripts')
from validate_output import section_order
body = '''
## Round 3
foo
## Top-3 Cross-Pollination Hits
bar
## Next Experiment
baz
## Self-Flag
qux
## Round 1
r1
## Round 2
r2
'''
print(section_order(body))
"
```

Expected output: `['Round 3', 'Top-3', 'Next Experiment', 'Self-Flag', 'Round 1', 'Round 2']`

- [ ] **Step 5: Commit Task 3**

```bash
git add skills/crazy-professor/scripts/validate_output.py
git commit -m "crazy-professor | Phase-6 Task 3: validate_output.py — branch on compact frontmatter

Adds section_order() helper and compact-mode body-order validation in
validate_chat(). Normal mode (no compact field, or compact: false) keeps
identical behavior. Compact mode requires Round 3 + Top-3 + Next-Experiment
+ Self-Flag BEFORE Round 1.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: `resources/stop-words.txt` — new resource for the linter

**Files:**
- Create: `skills/crazy-professor/resources/stop-words.txt`

- [ ] **Step 1: Create the stop-words pool**

Create `skills/crazy-professor/resources/stop-words.txt` with this exact content:

```
# crazy-professor -- stop-word pool for lint_cross_pollination.py
# format: one stop-word per line, lowercased, comments ('#') ignored.
# english + german mix because picker output mixes both languages.
# also includes archetype names so 'counter: jester #2' does not count
# the word 'jester' as token-overlap.

# english common
the
a
an
is
are
was
were
be
been
being
of
in
on
at
to
for
from
by
with
without
into
out
up
down
and
or
but
if
then
else
as
than
that
this
these
those
it
its
he
she
they
we
you
i
me
him
her
them
us
my
your
his
our
their
not
no
yes
all
any
some
every
each
one
two

# german common
der
die
das
den
dem
des
ein
eine
einen
einem
einer
ist
sind
war
waren
sein
gewesen
von
vom
zu
zur
zum
in
im
ins
auf
mit
fuer
und
oder
aber
wenn
dann
sonst
als
dass
das
es
er
sie
wir
ihr
mich
dich
sich
mein
dein
sein
unser
euer
nicht
kein
keine
alle
jeder

# archetype labels (so 'jester #2' overlap is ignored)
jester
librarian
alchemist
radagast
brown
first
principles

# operator labels
counter
extend
reversal
exaggeration
escape
wishful
thinking
```

- [ ] **Step 2: Verify the file**

Run: `wc -l skills/crazy-professor/resources/stop-words.txt`
Expected: somewhere between 100 and 130 lines (file content + comment lines).

Run: `grep -c "^[a-z]" skills/crazy-professor/resources/stop-words.txt`
Expected: ~95-110 actual stop-word entries (lines starting with a lowercase letter, excluding comments + blanks).

- [ ] **Step 3: Stage Task 4**

```bash
git add skills/crazy-professor/resources/stop-words.txt
git commit -m "crazy-professor | Phase-6 Task 4: resources/stop-words.txt — new resource

Stop-word pool for lint_cross_pollination.py token-overlap heuristic.
EN+DE mix plus archetype + operator labels (so 'jester #2' marker tokens
don't artificially boost overlap). ~100 entries.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: `lint_cross_pollination.py` — skeleton + Marker check

**Files:**
- Create: `skills/crazy-professor/scripts/lint_cross_pollination.py`

- [ ] **Step 1: Write the skeleton with parser, CLI, and Marker-check (Check 1 only)**

Create `skills/crazy-professor/scripts/lint_cross_pollination.py` with this initial implementation. Tasks 6 and 7 add Ref-Resolution (Check 2) and Token-Overlap (Check 3):

```python
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
    skill flow (preferred — what Step C4b passes).
  * --r1-md <mdfile> --r2-md <mdfile>: parse the chat output's R1 and R2
    sections from raw markdown. Used by the eval-suite Stage D.

JSON input shape:
  R1: {"jester": {1: "text", 2: "text", ...}, "librarian": {...}, ...}
  R2: {"jester": [{"idx": 1, "marker": "counter", "ref": "alchemist #3",
                   "text": "..."}, ...], "librarian": [...], ...}

Markdown input shape:
  R1: as in chat-output-template, '### Jester ...' subsections with
      numbered '1.' lines.
  R2: '### Jester — Runde 2' subsections with bulleted lines, each
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
    r"(?:[—–-]+)?\s*(.*)$",
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
    sections: dict[str, dict[int, str]] = {a: {} for a in ARCHETYPE_NORMALIZE.values()}
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
    sections: dict[str, list[dict]] = {a: [] for a in ARCHETYPE_NORMALIZE.values()}
    current = None
    heading_re = re.compile(r"^###\s+(\w[\w\- ]*?)\s*(?:[—\-]\s*Runde\s*2.*)?\s*$",
                            re.IGNORECASE)
    bullet_re = re.compile(r"^\s*[-*]\s+(.+?)\s*$")
    next_idx: dict[str, int] = {a: 0 for a in ARCHETYPE_NORMALIZE.values()}
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
            # Check 2 + 3 are added in Tasks 6 and 7. For now, marker-only.

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
```

- [ ] **Step 2: Smoke-test the skeleton with a missing-marker case**

Create a temporary R1+R2 JSON pair, then invoke the linter. Run from repo root:

```bash
python -c "
import json, pathlib, tempfile
tmp = pathlib.Path(tempfile.mkdtemp())
r1 = {'jester': {1: 'a', 2: 'b'}, 'librarian': {}, 'alchemist': {}, 'radagast': {}}
r2 = {'jester': [{'idx': 1, 'marker': None, 'ref': None, 'text': 'no marker here'}],
      'librarian': [], 'alchemist': [], 'radagast': []}
(tmp/'r1.json').write_text(json.dumps(r1))
(tmp/'r2.json').write_text(json.dumps(r2))
print(tmp)
" > /tmp/lint-cp-tmp.txt
TMP=$(cat /tmp/lint-cp-tmp.txt)
python skills/crazy-professor/scripts/lint_cross_pollination.py \
  --r1-input "$TMP/r1.json" --r2-input "$TMP/r2.json"
```

Expected stdout (single JSON line):
```json
{"low_substance_hits": 1, "findings": [{"archetype": "jester", "idx": 1, "ref": null, "severity": "error", "reason": "no counter/extend marker"}], "stats": {"r2_items_total": 1, "r2_items_flagged": 1, "by_severity": {"error": 1}}}
```

Expected exit code: `0` (warn-only).

- [ ] **Step 3: Commit Task 5**

```bash
git add skills/crazy-professor/scripts/lint_cross_pollination.py
git commit -m "crazy-professor | Phase-6 Task 5: lint_cross_pollination.py — skeleton + Marker check

4th linter, stdlib-only. Implements Check 1 (Marker-Existence). Two input
modes (JSON pre-parsed, Markdown block). Exit-code 0 always (warn-only).
Checks 2 (Ref-Resolution) and 3 (Token-Overlap) come in Tasks 6 + 7.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: `lint_cross_pollination.py` — Ref-Resolution (Check 2)

**Files:**
- Modify: `skills/crazy-professor/scripts/lint_cross_pollination.py`

- [ ] **Step 1: Add the Ref-Resolution check function**

Open `skills/crazy-professor/scripts/lint_cross_pollination.py`. Right above the `check_marker` function (around line 165 after Task 5), insert this new function:

```python
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
```

- [ ] **Step 2: Add the function to the main loop**

In `main()`, find this block (added in Task 5):

```python
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
            # Check 2 + 3 are added in Tasks 6 and 7. For now, marker-only.
```

Replace with:

```python
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
```

- [ ] **Step 3: Smoke-test Check 2**

```bash
python -c "
import json, pathlib, tempfile
tmp = pathlib.Path(tempfile.mkdtemp())
r1 = {'jester': {'1': 'foo', '2': 'bar'}, 'librarian': {}, 'alchemist': {}, 'radagast': {}}
# R2 has a counter to alchemist #3, but alchemist has no items -> ref does not resolve.
r2 = {'jester': [], 'librarian': [],
      'alchemist': [],
      'radagast': [{'idx': 1, 'marker': 'counter', 'ref': 'librarian #6',
                    'ref_archetype': 'librarian', 'ref_idx': 6, 'text': 'foo bar'}]}
(tmp/'r1.json').write_text(json.dumps(r1))
(tmp/'r2.json').write_text(json.dumps(r2))
print(tmp)
" > /tmp/lint-cp-t6.txt
TMP=$(cat /tmp/lint-cp-t6.txt)
python skills/crazy-professor/scripts/lint_cross_pollination.py \
  --r1-input "$TMP/r1.json" --r2-input "$TMP/r2.json"
```

Expected stdout: a single JSON line with `low_substance_hits: 1`, the finding has `severity: error` and reason `ref idx 6 out of range 1..5`.

Run a second test where the ref is in range but the R1 archetype is empty:

```bash
python -c "
import json, pathlib, tempfile
tmp = pathlib.Path(tempfile.mkdtemp())
r1 = {'jester': {}, 'librarian': {}, 'alchemist': {}, 'radagast': {}}
r2 = {'jester': [], 'librarian': [],
      'alchemist': [],
      'radagast': [{'idx': 1, 'marker': 'counter', 'ref': 'alchemist #3',
                    'ref_archetype': 'alchemist', 'ref_idx': 3, 'text': 'foo'}]}
(tmp/'r1.json').write_text(json.dumps(r1))
(tmp/'r2.json').write_text(json.dumps(r2))
print(tmp)
" > /tmp/lint-cp-t6b.txt
TMP=$(cat /tmp/lint-cp-t6b.txt)
python skills/crazy-professor/scripts/lint_cross_pollination.py \
  --r1-input "$TMP/r1.json" --r2-input "$TMP/r2.json"
```

Expected: `low_substance_hits: 1`, severity error, reason `ref does not resolve to existing R1 item (alchemist #3 not present)`.

- [ ] **Step 4: Commit Task 6**

```bash
git add skills/crazy-professor/scripts/lint_cross_pollination.py
git commit -m "crazy-professor | Phase-6 Task 6: lint_cross_pollination.py — Ref-Resolution check

Adds check_ref_resolution(): rejects refs with idx outside 1..5 and refs
to non-existent R1 items. Continues warn-only contract (exit code 0).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: `lint_cross_pollination.py` — Token-Overlap (Check 3)

**Files:**
- Modify: `skills/crazy-professor/scripts/lint_cross_pollination.py`

- [ ] **Step 1: Add stop-word loading + tokenization helpers**

Open `skills/crazy-professor/scripts/lint_cross_pollination.py`. Right after the `MARKER_RE` constant near the top of the file (around line 80), insert:

```python
# Default stop-words live next to the script; user can override with --stop-words.
DEFAULT_STOP_WORDS_PATH = (Path(__file__).resolve().parent.parent
                           / "resources" / "stop-words.txt")
TOKEN_RE = re.compile(r"[a-z0-9\-]+")


def load_stop_words(path: Path | None) -> set[str]:
    target = path if path else DEFAULT_STOP_WORDS_PATH
    if not target.exists():
        return set()
    words = set()
    for line in target.read_text(encoding="utf-8").splitlines():
        s = line.strip().lower()
        if s and not s.startswith("#"):
            words.add(s)
    return words


def tokenize(text: str, stop_words: set[str]) -> set[str]:
    tokens = TOKEN_RE.findall(text.lower())
    return {t for t in tokens if len(t) >= 3 and t not in stop_words}
```

- [ ] **Step 2: Add the Token-Overlap check function**

Right above `check_marker`, insert:

```python
def check_token_overlap(item: dict, r1: dict, stop_words: set[str],
                        min_overlap: int) -> tuple[str, str] | None:
    """Check 3: Token-Overlap. Returns (severity, reason) or None.
    Assumes Checks 1 + 2 already passed. Compares R2 item text and the
    referenced R1 item text for non-stopword token overlap.
    """
    arch = item["ref_archetype"]
    idx = item["ref_idx"]
    archetype_section = r1.get(arch, {})
    if isinstance(archetype_section, dict):
        ref_text = archetype_section.get(idx) or archetype_section.get(str(idx)) or ""
    elif isinstance(archetype_section, list):
        ref_text = archetype_section[idx - 1] if 1 <= idx <= len(archetype_section) else ""
    else:
        ref_text = ""
    item_tokens = tokenize(item.get("text", ""), stop_words)
    ref_tokens = tokenize(ref_text, stop_words)
    overlap = item_tokens & ref_tokens
    if len(overlap) < min_overlap:
        return ("warn", f"token overlap with ref < {min_overlap}")
    return None
```

- [ ] **Step 3: Wire Check 3 into the main loop and load stop-words at startup**

Find this block in `main()` (top-of-function area):

```python
    if args.r1_input:
        r1 = load_json_file(args.r1_input)
        r2 = load_json_file(args.r2_input)
    else:
        r1 = parse_r1_md(args.r1_md.read_text(encoding="utf-8"))
        r2 = parse_r2_md(args.r2_md.read_text(encoding="utf-8"))
```

Right after that block, add:

```python
    stop_words = load_stop_words(args.stop_words)
```

Then find the loop in `main()` (added in Task 5 / Task 6):

```python
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
```

Replace the trailing comment line with the actual Check-3 invocation:

```python
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

            check = check_token_overlap(item, r1, stop_words, args.min_overlap)
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
```

- [ ] **Step 4: Smoke-test Check 3**

Test 1 — R2 text shares a non-stopword token with the ref → no finding:

```bash
python -c "
import json, pathlib, tempfile
tmp = pathlib.Path(tempfile.mkdtemp())
r1 = {'jester': {}, 'librarian': {}, 'alchemist': {3: 'the reactor leaks plasma into the overflow tank'},
      'radagast': {}}
r2 = {'jester': [], 'librarian': [],
      'alchemist': [],
      'radagast': [{'idx': 1, 'marker': 'extend', 'ref': 'alchemist #3',
                    'ref_archetype': 'alchemist', 'ref_idx': 3,
                    'text': 'the reactor needs a quiet forest cap'}]}
(tmp/'r1.json').write_text(json.dumps(r1))
(tmp/'r2.json').write_text(json.dumps(r2))
print(tmp)
" > /tmp/lint-cp-t7a.txt
TMP=$(cat /tmp/lint-cp-t7a.txt)
python skills/crazy-professor/scripts/lint_cross_pollination.py \
  --r1-input "$TMP/r1.json" --r2-input "$TMP/r2.json"
```

Expected: `low_substance_hits: 0`, no findings (overlap word: `reactor`).

Test 2 — R2 text shares only stop-words with ref → warn:

```bash
python -c "
import json, pathlib, tempfile
tmp = pathlib.Path(tempfile.mkdtemp())
r1 = {'jester': {}, 'librarian': {}, 'alchemist': {3: 'the system is broken'},
      'radagast': {}}
r2 = {'jester': [], 'librarian': [],
      'alchemist': [],
      'radagast': [{'idx': 1, 'marker': 'extend', 'ref': 'alchemist #3',
                    'ref_archetype': 'alchemist', 'ref_idx': 3,
                    'text': 'the forest hides everything else'}]}
(tmp/'r1.json').write_text(json.dumps(r1))
(tmp/'r2.json').write_text(json.dumps(r2))
print(tmp)
" > /tmp/lint-cp-t7b.txt
TMP=$(cat /tmp/lint-cp-t7b.txt)
python skills/crazy-professor/scripts/lint_cross_pollination.py \
  --r1-input "$TMP/r1.json" --r2-input "$TMP/r2.json"
```

Expected: `low_substance_hits: 1`, severity warn, reason `token overlap with ref < 1`.

(The shared word `the` is a stop-word; `system`, `broken`, `forest`, `hides`, `everything`, `else` are all unique to one side or the other.)

Test 3 — `--min-overlap 0` disables the overlap check:

Re-run Test 2 with `--min-overlap 0`. Expected: `low_substance_hits: 0`.

```bash
python skills/crazy-professor/scripts/lint_cross_pollination.py \
  --r1-input "$TMP/r1.json" --r2-input "$TMP/r2.json" --min-overlap 0
```

- [ ] **Step 5: Commit Task 7**

```bash
git add skills/crazy-professor/scripts/lint_cross_pollination.py
git commit -m "crazy-professor | Phase-6 Task 7: lint_cross_pollination.py — Token-Overlap check

Adds Check 3 (Token-Overlap) with stop-word filter, default min-overlap=1.
load_stop_words() reads resources/stop-words.txt by default,
--stop-words override accepted. tokenize() lowercases, splits on word
boundaries, drops tokens <3 chars, drops stop-words. All three checks
now wired into main() loop.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## CHECKPOINT 1 (after Task 7)

Sub-Feature 6.1 (Tasks 1-3) and 6.2 (Tasks 4-7) are complete. Before continuing to Task 8, verify:

```bash
git log --oneline -7
ls skills/crazy-professor/scripts/lint_cross_pollination.py
ls skills/crazy-professor/resources/stop-words.txt
python skills/crazy-professor/scripts/validate_output.py --help
python skills/crazy-professor/scripts/lint_cross_pollination.py --help
```

Expected: 7 task commits, both new files present, both helpers print usage. If any test in Task 5/6/7 didn't behave as expected, fix before continuing. Re-run the smoke tests if uncertain.

---

## Task 8: `picker.py` — wishful-thinking 4th operator

**Files:**
- Modify: `skills/crazy-professor/scripts/picker.py`

- [ ] **Step 1: Extend the OPERATORS tuple and add `--wishful-share` argument**

Open `skills/crazy-professor/scripts/picker.py`. Find this constant near the top (around line 42):

```python
OPERATORS = ("reversal", "exaggeration", "escape")
```

Replace with:

```python
BASE_OPERATORS = ("reversal", "exaggeration", "escape")
WISHFUL_OPERATOR = "wishful-thinking"
OPERATORS = BASE_OPERATORS  # kept for backward-compat — variation_guard etc. read this name
```

- [ ] **Step 2: Add `random` import and `pick_operator_with_share` function**

Add `import random` to the imports block at the top (between `import re` and `import shutil`):

```python
import random
import re
```

Right above `picker_seed` function (around line 95), add the new helper:

```python
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
```

- [ ] **Step 3: Update `picker_seed` to use the new helper and accept `wishful_share`**

Find the existing `picker_seed` function:

```python
def picker_seed(ts: dt.datetime, offset_seconds: int = 0) -> tuple[str, str, str]:
    """Deterministic mod-based picker for archetype/operator and a word index seed."""
    seed_ts = ts + dt.timedelta(seconds=offset_seconds)
    archetype = ARCHETYPES[seed_ts.minute % 4]
    operator = OPERATORS[seed_ts.second % 3]
    return archetype, operator, seed_ts.isoformat().replace("+00:00", "Z")
```

Replace with:

```python
def picker_seed(ts: dt.datetime, offset_seconds: int = 0,
                wishful_share: float = 0.0) -> tuple[str, str, str]:
    """Deterministic mod-based picker for archetype/operator and a word index seed."""
    seed_ts = ts + dt.timedelta(seconds=offset_seconds)
    archetype = ARCHETYPES[seed_ts.minute % 4]
    operator = pick_operator_with_share(seed_ts, wishful_share)
    return archetype, operator, seed_ts.isoformat().replace("+00:00", "Z")
```

- [ ] **Step 4: Pass `args.wishful_share` through `pick_single` and `pick_chat`**

Find `pick_single`:

```python
def pick_single(args, words: list[str], rows: list[dict], ts: dt.datetime) -> dict:
    archetype, operator, ts_iso = picker_seed(ts)
```

Replace the first line of the body with:

```python
def pick_single(args, words: list[str], rows: list[dict], ts: dt.datetime) -> dict:
    archetype, operator, ts_iso = picker_seed(ts, wishful_share=args.wishful_share)
```

Find `pick_chat`:

```python
def pick_chat(words: list[str], rows: list[dict], ts: dt.datetime) -> dict:
    """Four picks, one per archetype. Word-guard runs across the chat-run."""
    chat_rolled = []
    chat_words: set[str] = set()
    picks = []
    for i, archetype in enumerate(ARCHETYPES):
        offset = i  # one second per archetype to vary operator pick
        _, operator, _ = picker_seed(ts, offset_seconds=offset)
```

Update the function signature and the inner call:

```python
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
```

Then find the call to `pick_chat(words, rows, ts)` near the bottom of `main()`:

```python
    if args.mode == "single":
        result = pick_single(args, words, rows, ts)
    else:
        result = pick_chat(words, rows, ts)
```

Replace with:

```python
    if args.mode == "single":
        result = pick_single(args, words, rows, ts)
    else:
        result = pick_chat(words, rows, ts, wishful_share=args.wishful_share)
```

- [ ] **Step 5: Add `--wishful-share` CLI argument with validation**

Find this block in `main()` (around line 211):

```python
    p.add_argument("--force-archetype", choices=ARCHETYPES, help="bypass mod-4 picker")
    p.add_argument("--force-timestamp", help="ISO-8601 UTC override (testing)")
    args = p.parse_args()
```

Insert the new argument before the `args = p.parse_args()` line:

```python
    p.add_argument("--force-archetype", choices=ARCHETYPES, help="bypass mod-4 picker")
    p.add_argument("--force-timestamp", help="ISO-8601 UTC override (testing)")
    p.add_argument("--wishful-share", type=float, default=0.25,
                   help="relative weight for wishful-thinking operator. "
                        "0.0 = disabled (3-operator legacy), 1.0 = equal 25%% each "
                        "(default 0.25 = ~14%% wishful, ~28.6%% each base operator)")
    args = p.parse_args()
    if args.wishful_share < 0.0 or args.wishful_share > 1.0:
        print(f"error: --wishful-share must be in [0.0, 1.0] (got {args.wishful_share})",
              file=sys.stderr)
        return 1
```

- [ ] **Step 6: Smoke-test the new operator**

Run from a fresh field-notes file (force-timestamp ensures deterministic operator pick):

Test 1 — `--wishful-share 0.0` returns only base operators across many seeds:

```bash
TMP=$(mktemp -d)
mkdir -p "$TMP/lab"
echo "" > "$TMP/lab/field-notes.md"
for sec in 0 7 14 21 28 35 42 49 56; do
  TS="2026-04-29T12:00:${sec}+00:00"
  python skills/crazy-professor/scripts/picker.py \
    --field-notes "$TMP/lab/field-notes.md" \
    --words skills/crazy-professor/resources/provocation-words.txt \
    --retired skills/crazy-professor/resources/retired-words.txt \
    --init-template skills/crazy-professor/resources/field-notes-init.md \
    --mode single \
    --wishful-share 0.0 \
    --force-timestamp "$TS" 2>/dev/null | python -c "import sys,json; print(json.loads(sys.stdin.read())['operator'])"
done
```

Expected: 9 lines, only `reversal`, `exaggeration`, `escape` — never `wishful-thinking`.

Test 2 — `--wishful-share 1.0` returns wishful-thinking at least once over many seeds:

```bash
for sec in $(seq 0 5 60); do
  for ms in 100 250 500 750; do
    TS=$(printf "2026-04-29T12:00:%02d.%03d000+00:00" $sec $ms)
    python skills/crazy-professor/scripts/picker.py \
      --field-notes "$TMP/lab/field-notes.md" \
      --words skills/crazy-professor/resources/provocation-words.txt \
      --retired skills/crazy-professor/resources/retired-words.txt \
      --init-template skills/crazy-professor/resources/field-notes-init.md \
      --mode single \
      --wishful-share 1.0 \
      --force-timestamp "$TS" 2>/dev/null | python -c "import sys,json; print(json.loads(sys.stdin.read())['operator'])"
  done
done | sort | uniq -c
```

Expected: all 4 operator names appear. Counts will be roughly balanced (each ~25% over enough samples).

Test 3 — invalid share → exit 1:

```bash
python skills/crazy-professor/scripts/picker.py \
  --field-notes "$TMP/lab/field-notes.md" \
  --words skills/crazy-professor/resources/provocation-words.txt \
  --retired skills/crazy-professor/resources/retired-words.txt \
  --init-template skills/crazy-professor/resources/field-notes-init.md \
  --mode single --wishful-share -0.5
echo "exit=$?"
```

Expected: stderr message about wishful-share range, exit 1.

- [ ] **Step 7: Commit Task 8**

```bash
git add skills/crazy-professor/scripts/picker.py
git commit -m "crazy-professor | Phase-6 Task 8: picker.py — wishful-thinking 4th operator

Adds --wishful-share <float> CLI argument (default 0.25). At share=0.0 the
picker keeps the v0.10.0 3-operator behavior (regression-safe). At share>0
the operator pool is 4 entries with relative weights [1, 1, 1, share*3]
selected via random.choices seeded by timestamp microseconds for
determinism.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: `validate_output.py` — accept wishful-thinking

**Files:**
- Modify: `skills/crazy-professor/scripts/validate_output.py`

- [ ] **Step 1: Add wishful-thinking to the accepted operators**

Open `skills/crazy-professor/scripts/validate_output.py`. Find this constant (line 28):

```python
PO_OPERATORS = ("reversal", "exaggeration", "escape")
```

Replace with:

```python
PO_OPERATORS = ("reversal", "exaggeration", "escape", "wishful-thinking")
```

- [ ] **Step 2: Verify nothing else in validate_output.py hard-codes the operator list**

Run: `grep -n "reversal" skills/crazy-professor/scripts/validate_output.py`

Expected: only the line in `PO_OPERATORS` constant (line 28). No other hard-coded operator references.

- [ ] **Step 3: Commit Task 9**

```bash
git add skills/crazy-professor/scripts/validate_output.py
git commit -m "crazy-professor | Phase-6 Task 9: validate_output.py — accept wishful-thinking

Adds wishful-thinking to PO_OPERATORS tuple. Frontmatter check now accepts
po_operator: wishful-thinking. No body-level operator validation today,
so this single edit is sufficient.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 10: `po-operators.md` — add Wishful-Thinking section

**Files:**
- Modify: `skills/crazy-professor/resources/po-operators.md`

- [ ] **Step 1: Update the V1/V2 reservation note**

Open `skills/crazy-professor/resources/po-operators.md`. Find lines 6-10:

```markdown
V1 uses three of de Bono's six operators. The remaining three (wishful
thinking, distortion, arising) are reserved for V2 to keep the initial
space focused.
```

Replace with:

```markdown
V1 used three of de Bono's six operators. v0.11.0 activates the 4th
operator (wishful thinking) as a controlled field-test. The remaining two
(distortion, arising) are reserved for V2 to keep the space focused.
```

- [ ] **Step 2: Add the Wishful Thinking section after Escape**

Find the `## Escape` section (lines 31-38). Right after the closing `What if [input] does not exist?` line and BEFORE the `## Rules for All Three` heading, insert this new section:

```markdown
## Wishful Thinking

Postulate something the system explicitly cannot do, then observe what
constraint that breaks. Not for the wish itself -- for what the
impossibility reveals about the boundary. The operator names a desire
that is materially blocked, then forces thinking sideways into "what
if the block were removed".

Example scaffold:
  "Wishful thinking: <X> happens without <prerequisite>."
  "Wishful thinking: <subject> can <verb> without <constraint>."

Distinction from Reversal: reversal swaps an existing relationship.
Wishful thinking removes a precondition that gates the action entirely.
Distinction from Escape: escape removes a feature; wishful thinking
removes a prerequisite that the system normally requires before the
feature can run.
```

- [ ] **Step 3: Update the closing rules-section heading**

Find the heading `## Rules for All Three` (line 39 originally, will be lower after Step 2). Replace with:

```markdown
## Rules for All Four
```

(Inner content of that section stays unchanged — the four bullet rules apply identically.)

- [ ] **Step 4: Commit Task 10**

```bash
git add skills/crazy-professor/resources/po-operators.md
git commit -m "crazy-professor | Phase-6 Task 10: po-operators.md — Wishful Thinking section

Activates wishful-thinking as the 4th PO operator with full Definition,
Scaffold, and Distinction-from-Reversal-and-Escape sections. V2-reservation
note now lists only distortion and arising as remaining-reserved.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## CHECKPOINT 2 (after Task 10)

Sub-Feature 6.3 (Tasks 8-10) complete. Before Task 11, verify:

```bash
git log --oneline -10
python skills/crazy-professor/scripts/picker.py --help | grep wishful
python skills/crazy-professor/scripts/validate_output.py --help
grep -c "Wishful Thinking" skills/crazy-professor/resources/po-operators.md
```

Expected: 10 task commits, picker shows `--wishful-share`, validate_output has `--mode` flag, po-operators.md has at least 1 occurrence of "Wishful Thinking" heading.

---

## Task 11: `telemetry.py` — 3 new optional fields

**Files:**
- Modify: `skills/crazy-professor/scripts/telemetry.py`

- [ ] **Step 1: Add optional fields to the schema docstring**

Open `skills/crazy-professor/scripts/telemetry.py`. Find this block (line 9-22):

```python
Schema (per run, single-mode):
    run_id              str    "<utc-iso>--<archetype>--<slug-or-none>"
    timestamp           str    UTC ISO-8601 ("...Z")
    mode                str    "single" | "chat"
    topic_slug          str    short kebab slug or "" if not provided
    archetype           str    final picked archetype (post-variation-guard)
    word                str    final picked word
    operator            str    "reversal" | "exaggeration" | "escape"
    re_rolled           str    "no" | "archetype" | "word" | "both" | "forced-archetype" | ...
    distiller_used      bool   true if codex round-2 distiller ran
    round2_status       str    "n/a" | "ok" | "skipped" | "failed"
    time_to_finish_ms   int    wall-clock ms from picker to validator-pass
    voice_cross_drift_hits int  count from lint_voice.py FAIL/WARN findings
    lint_pass           bool   true if all linters pass strict-mode
```

Update the `operator` line and append three new optional fields:

```python
Schema (per run, single-mode):
    run_id              str    "<utc-iso>--<archetype>--<slug-or-none>"
    timestamp           str    UTC ISO-8601 ("...Z")
    mode                str    "single" | "chat"
    topic_slug          str    short kebab slug or "" if not provided
    archetype           str    final picked archetype (post-variation-guard)
    word                str    final picked word
    operator            str    "reversal" | "exaggeration" | "escape" | "wishful-thinking"
    re_rolled           str    "no" | "archetype" | "word" | "both" | "forced-archetype" | ...
    distiller_used      bool   true if codex round-2 distiller ran
    round2_status       str    "n/a" | "ok" | "skipped" | "failed"
    time_to_finish_ms   int    wall-clock ms from picker to validator-pass
    voice_cross_drift_hits int  count from lint_voice.py FAIL/WARN findings
    lint_pass           bool   true if all linters pass strict-mode

Optional fields (since v0.11.0; backward-compatible -- readers ignore unknowns):
    compact_mode        bool   true if --chat --compact was active
    low_substance_hits  int    findings count from lint_cross_pollination.py
    wishful_thinking_active  bool  true if any picked operator was wishful-thinking
```

- [ ] **Step 2: Allow operator='wishful-thinking' to pass record validation**

Today `validate_record` does not enforce the operator value (only mode and round2_status are checked). Confirm by reading `validate_record` (line 80-101) — it has no operator check. **Nothing to change here**: the schema is permissive about operator strings, and `wishful-thinking` will pass through fine.

(If you find an operator-tuple check, add `wishful-thinking` to it. Today there isn't one.)

- [ ] **Step 3: Smoke-test backward + forward compat**

Test 1 — Append a record with the 3 new optional fields. Should succeed.

```bash
TMP=$(mktemp)
python skills/crazy-professor/scripts/telemetry.py log --path "$TMP" --json '{
  "run_id": "smoke--first-principles-jester--phase6",
  "timestamp": "2026-04-29T12:00:00Z",
  "mode": "single",
  "topic_slug": "phase6",
  "archetype": "first-principles-jester",
  "word": "smoke",
  "operator": "wishful-thinking",
  "re_rolled": "no",
  "distiller_used": false,
  "round2_status": "n/a",
  "time_to_finish_ms": 0,
  "voice_cross_drift_hits": 0,
  "lint_pass": true,
  "compact_mode": false,
  "low_substance_hits": 0,
  "wishful_thinking_active": true
}'
echo "exit=$?"
cat "$TMP"
```

Expected: exit 0; the JSON line in the file contains all 3 new fields.

Test 2 — Append a record WITHOUT any new optional fields (backward compat).

```bash
TMP=$(mktemp)
python skills/crazy-professor/scripts/telemetry.py log --path "$TMP" --json '{
  "run_id": "smoke--first-principles-jester--legacy",
  "timestamp": "2026-04-29T12:00:00Z",
  "mode": "single",
  "topic_slug": "legacy",
  "archetype": "first-principles-jester",
  "word": "smoke",
  "operator": "reversal",
  "re_rolled": "no",
  "distiller_used": false,
  "round2_status": "n/a",
  "time_to_finish_ms": 0,
  "voice_cross_drift_hits": 0,
  "lint_pass": true
}'
echo "exit=$?"
```

Expected: exit 0 (no required-fields complaint).

- [ ] **Step 4: Commit Task 11**

```bash
git add skills/crazy-professor/scripts/telemetry.py
git commit -m "crazy-professor | Phase-6 Task 11: telemetry.py — 3 new optional fields

Adds compact_mode, low_substance_hits, wishful_thinking_active as optional
fields in the schema docstring. Updates operator-line to mention
wishful-thinking. validate_record stays permissive on operator string and
ignores unknown extra fields, so both forward + backward compat are
preserved.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 12: `eval_suite.py` — Stages C/D/E

**Files:**
- Modify: `skills/crazy-professor/scripts/eval_suite.py`

This is the largest task. It adds three new smoke-test stages to the eval-suite. Each stage has its own helper function and is invoked via a new CLI flag. The implementations follow the Phase-5 pattern (Stage B Run-Planner-Smoke).

- [ ] **Step 1: Add Stage C — Compact-Mode Smoke**

Add this function after `stage_b_run_planner_smoke` (around line 580 of `eval_suite.py`). It fixtures a Compact-mode chat output and a normal-mode chat output, then calls `validate_output.py` on both:

```python
def stage_c_compact_smoke(validator: Path, tmp_dir: Path) -> dict:
    """5-assert smoke test for --chat --compact validator behavior."""
    if not validator.exists():
        return {"available": False,
                "reason": f"validator script not found: {validator}"}

    asserts: list[tuple[str, bool, str]] = []
    normal_chat = """---
skill: crazy-professor
mode: chat
version: 0.11.0
timestamp: 2026-04-29T12:00:00Z
topic: "smoke"
archetypes: [first-principles-jester, labyrinth-librarian, systems-alchemist, radagast-brown]
rounds: 3
distiller: codex
round2_status: full
llm_calls: 10
---

# Chat: smoke

> DIVERGENCE WARNING: smoke test fixture.

## Round 1 — Parallel Voices

### Jester (word: smoke, operator: reversal)
1. one
2. two
3. three
4. four
5. five

### Librarian (word: smoke, operator: reversal)
1. one
2. two
3. three
4. four
5. five

### Alchemist (word: smoke, operator: reversal)
1. one
2. two
3. three
4. four
5. five

### Radagast (word: smoke, operator: reversal)
1. one
2. two
3. three
4. four
5. five

## Round 2 — Cross-Pollination

### Jester
- counter: alchemist #1 — text — anchor: x
- counter: librarian #2 — text — anchor: x

### Librarian
- counter: alchemist #1 — text — anchor: x
- counter: jester #2 — text — anchor: x

### Alchemist
- counter: jester #1 — text — anchor: x
- counter: radagast #2 — text — anchor: x

### Radagast
- counter: jester #1 — text — anchor: x
- counter: alchemist #2 — text — anchor: x

## Round 3 — Codex Distillation (Final 20)

### Jester-5
1. one — [cost: low] — anchor: x — [score: W=3 U=3 S=3]
2. two — [cost: low] — anchor: x — [score: W=3 U=3 S=3]
3. three — [cost: low] — anchor: x — [score: W=3 U=3 S=3]
4. four — [cost: low] — anchor: x — [score: W=3 U=3 S=3]
5. five — [cost: low] — anchor: x — [score: W=3 U=3 S=3]

### Librarian-5
1. one — [cost: low] — anchor: x — [score: W=3 U=3 S=3]
2. two — [cost: low] — anchor: x — [score: W=3 U=3 S=3]
3. three — [cost: low] — anchor: x — [score: W=3 U=3 S=3]
4. four — [cost: low] — anchor: x — [score: W=3 U=3 S=3]
5. five — [cost: low] — anchor: x — [score: W=3 U=3 S=3]

### Alchemist-5
1. one — [cost: low] — anchor: x — [score: W=3 U=3 S=3]
2. two — [cost: low] — anchor: x — [score: W=3 U=3 S=3]
3. three — [cost: low] — anchor: x — [score: W=3 U=3 S=3]
4. four — [cost: low] — anchor: x — [score: W=3 U=3 S=3]
5. five — [cost: low] — anchor: x — [score: W=3 U=3 S=3]

### Radagast-5
1. one — [cost: low] — anchor: x — [score: W=3 U=3 S=3]
2. two — [cost: low] — anchor: x — [score: W=3 U=3 S=3]
3. three — [cost: low] — anchor: x — [score: W=3 U=3 S=3]
4. four — [cost: low] — anchor: x — [score: W=3 U=3 S=3]
5. five — [cost: low] — anchor: x — [score: W=3 U=3 S=3]

## Top-3 Cross-Pollination Hits
1. ref — text
2. ref — text
3. ref — text

## Next Experiment
Description.

## Self-Flag
- [ ] kept
- [ ] round2-was-degraded
- [ ] distiller-fallback-used
- [ ] voice-cross-drift
"""

    # Build the compact-mode body by reordering: R3 + Top-3 + Next + Self-Flag, then <details>R1+R2
    compact_chat = normal_chat.replace(
        "mode: chat\nversion: 0.11.0",
        "mode: chat\ncompact: true\nversion: 0.11.0",
    )
    # Now physically reorder by extracting sections and re-stitching.
    parts = compact_chat.split("## Round 1")
    head = parts[0]
    rest = "## Round 1" + parts[1]  # contains R1, R2, R3, Top-3, Next, Self-Flag
    sections_after_r2 = rest.split("## Round 3")
    r1_r2 = sections_after_r2[0]  # R1 + R2
    r3_plus = "## Round 3" + sections_after_r2[1]  # R3, Top-3, Next, Self-Flag
    compact_body = (
        head
        + r3_plus.rstrip()
        + "\n\n---\n\n<details>\n<summary>Audit-Trail — Round 1 + Round 2 (click to expand)</summary>\n\n"
        + r1_r2.rstrip()
        + "\n\n</details>\n"
    )

    def call_validator(content: str) -> tuple[int, str]:
        f = tmp_dir / f"compact-fixture-{abs(hash(content)) % 10000}.md"
        f.write_text(content, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(validator), "--mode", "chat", str(f)],
            capture_output=True, text=True, timeout=10,
        )
        return proc.returncode, proc.stderr

    # Assert 1: --compact without --chat reject — handled at command layer, not the validator,
    # so we test the documentation existence (commands/crazy.md has the right line).
    cmd_md = (Path(__file__).resolve().parent.parent.parent.parent
              / "commands" / "crazy.md")
    ok_1 = False
    detail_1 = ""
    if cmd_md.exists():
        text = cmd_md.read_text(encoding="utf-8")
        ok_1 = "--compact requires --chat" in text
        if not ok_1:
            detail_1 = "commands/crazy.md does not contain reject message"
    else:
        detail_1 = "commands/crazy.md not found"
    asserts.append(("--compact reject documented", ok_1, detail_1))

    # Assert 2: normal-mode (no compact field) validates clean.
    rc, err = call_validator(normal_chat)
    ok_2 = (rc == 0)
    asserts.append(("normal-mode chat output validates",
                    ok_2, "" if ok_2 else f"rc={rc}, err={err.strip()[:120]}"))

    # Assert 3: compact-mode body validates clean (compact: true frontmatter + reorder)
    rc, err = call_validator(compact_body)
    ok_3 = (rc == 0)
    asserts.append(("compact-mode body validates",
                    ok_3, "" if ok_3 else f"rc={rc}, err={err.strip()[:120]}"))

    # Assert 4: compact: true with NORMAL order should be rejected.
    bad_compact = normal_chat.replace(
        "mode: chat\nversion: 0.11.0",
        "mode: chat\ncompact: true\nversion: 0.11.0",
    )
    rc, err = call_validator(bad_compact)
    ok_4 = (rc != 0 and "compact-mode order violation" in err)
    asserts.append(("compact:true + normal order rejected",
                    ok_4, "" if ok_4 else f"rc={rc}, err={err.strip()[:160]}"))

    # Assert 5: compact body without explicit compact: true (default false) is rejected.
    body_no_flag = compact_body.replace(
        "compact: true\n",
        "",
    )
    rc, err = call_validator(body_no_flag)
    ok_5 = (rc != 0 and "normal-mode order violation" in err)
    asserts.append(("compact body without flag rejected",
                    ok_5, "" if ok_5 else f"rc={rc}, err={err.strip()[:160]}"))

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

- [ ] **Step 2: Add Stage D — Cross-Pollination Linter Smoke**

Add right after `stage_c_compact_smoke`:

```python
def stage_d_cross_pollination_smoke(linter: Path, tmp_dir: Path) -> dict:
    """8-assert smoke test for lint_cross_pollination.py."""
    if not linter.exists():
        return {"available": False,
                "reason": f"linter script not found: {linter}"}

    asserts: list[tuple[str, bool, str]] = []

    def call(r1: dict, r2: dict, extra_args: list[str] | None = None) -> tuple[int, dict]:
        r1_p = tmp_dir / f"r1-{abs(hash(json.dumps(r1, sort_keys=True))) % 10000}.json"
        r2_p = tmp_dir / f"r2-{abs(hash(json.dumps(r2, sort_keys=True))) % 10000}.json"
        r1_p.write_text(json.dumps(r1), encoding="utf-8")
        r2_p.write_text(json.dumps(r2), encoding="utf-8")
        cmd = [sys.executable, str(linter),
               "--r1-input", str(r1_p), "--r2-input", str(r2_p)]
        if extra_args:
            cmd.extend(extra_args)
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        out = json.loads(proc.stdout) if proc.stdout.strip() else {}
        return proc.returncode, out

    base_r1 = {
        "jester": {"1": "the jester sees the assumption as a reactor"},
        "librarian": {"1": "history shows the same pattern"},
        "alchemist": {"1": "the reactor leaks plasma into the overflow tank",
                      "3": "deploy pipeline membrane filters"},
        "radagast": {"1": "the forest still breathes"},
    }

    # 1. Marker missing -> error
    rc, out = call(base_r1, {
        "jester": [], "librarian": [], "alchemist": [],
        "radagast": [{"idx": 1, "marker": None, "ref": None, "text": "no marker here"}],
    })
    ok_1 = (out.get("low_substance_hits") == 1
            and out["findings"][0]["severity"] == "error"
            and "no counter/extend marker" in out["findings"][0]["reason"])
    asserts.append(("marker missing -> error",
                    ok_1, "" if ok_1 else f"got {out}"))

    # 2. Ref idx out of range (idx > 5) -> error
    rc, out = call(base_r1, {
        "jester": [], "librarian": [], "alchemist": [],
        "radagast": [{"idx": 1, "marker": "extend", "ref": "librarian #6",
                      "ref_archetype": "librarian", "ref_idx": 6, "text": "the forest"}],
    })
    ok_2 = (out.get("low_substance_hits") == 1
            and out["findings"][0]["severity"] == "error"
            and "idx 6 out of range" in out["findings"][0]["reason"])
    asserts.append(("ref idx out of range -> error",
                    ok_2, "" if ok_2 else f"got {out}"))

    # 3. Ref to nonexistent R1 item -> error
    rc, out = call(base_r1, {
        "jester": [], "librarian": [], "alchemist": [],
        "radagast": [{"idx": 1, "marker": "counter", "ref": "alchemist #2",
                      "ref_archetype": "alchemist", "ref_idx": 2, "text": "x"}],
    })
    ok_3 = (out.get("low_substance_hits") == 1
            and out["findings"][0]["severity"] == "error"
            and "not present" in out["findings"][0]["reason"])
    asserts.append(("ref to non-existent R1 item -> error",
                    ok_3, "" if ok_3 else f"got {out}"))

    # 4. 0 token overlap with stop-words filter -> warn
    rc, out = call(base_r1, {
        "jester": [], "librarian": [], "alchemist": [],
        "radagast": [{"idx": 1, "marker": "extend", "ref": "alchemist #1",
                      "ref_archetype": "alchemist", "ref_idx": 1,
                      "text": "the forest hides everything else"}],
    })
    ok_4 = (out.get("low_substance_hits") == 1
            and out["findings"][0]["severity"] == "warn"
            and "token overlap" in out["findings"][0]["reason"])
    asserts.append(("0 overlap -> warn",
                    ok_4, "" if ok_4 else f"got {out}"))

    # 5. Token overlap pass (shared 'reactor')
    rc, out = call(base_r1, {
        "jester": [], "librarian": [], "alchemist": [],
        "radagast": [{"idx": 1, "marker": "extend", "ref": "alchemist #1",
                      "ref_archetype": "alchemist", "ref_idx": 1,
                      "text": "the reactor needs a quiet forest cap"}],
    })
    ok_5 = (out.get("low_substance_hits") == 0
            and out["findings"] == [])
    asserts.append(("overlap >= 1 -> pass",
                    ok_5, "" if ok_5 else f"got {out}"))

    # 6. Stop-word-only overlap -> warn (only 'the' shared)
    rc, out = call(base_r1, {
        "jester": [], "librarian": [], "alchemist": [],
        "radagast": [{"idx": 1, "marker": "extend", "ref": "alchemist #1",
                      "ref_archetype": "alchemist", "ref_idx": 1,
                      "text": "the swift cap of the cloud"}],
    })
    ok_6 = (out.get("low_substance_hits") == 1
            and out["findings"][0]["severity"] == "warn")
    asserts.append(("stop-word-only overlap -> warn",
                    ok_6, "" if ok_6 else f"got {out}"))

    # 7. JSON output schema is valid (low_substance_hits, findings, stats present)
    rc, out = call(base_r1, {"jester": [], "librarian": [], "alchemist": [], "radagast": []})
    ok_7 = ("low_substance_hits" in out and "findings" in out
            and "stats" in out and "by_severity" in out["stats"])
    asserts.append(("JSON output schema",
                    ok_7, "" if ok_7 else f"got keys: {list(out.keys())}"))

    # 8. Exit code 0 for both findings and clean.
    rc_a, _ = call(base_r1, {"jester": [], "librarian": [], "alchemist": [], "radagast": []})
    rc_b, _ = call(base_r1, {
        "jester": [], "librarian": [], "alchemist": [],
        "radagast": [{"idx": 1, "marker": None, "ref": None, "text": "x"}],
    })
    ok_8 = (rc_a == 0 and rc_b == 0)
    asserts.append(("exit 0 always",
                    ok_8, "" if ok_8 else f"rc_a={rc_a}, rc_b={rc_b}"))

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

- [ ] **Step 3: Add Stage E — Wishful-Thinking Picker Smoke**

Add right after `stage_d_cross_pollination_smoke`:

```python
def stage_e_wishful_smoke(picker: Path, words: Path, retired: Path,
                          init_template: Path, tmp_dir: Path) -> dict:
    """6-assert smoke test for wishful-thinking operator."""
    if not picker.exists():
        return {"available": False,
                "reason": f"picker script not found: {picker}"}

    asserts: list[tuple[str, bool, str]] = []

    def run_n(share: float, n: int) -> Counter:
        ops: Counter = Counter()
        fn_path = tmp_dir / f"wishful-fn-{share}.md"
        if fn_path.exists():
            fn_path.unlink()
        for i in range(n):
            sec = i % 60
            us = (i * 17) % 999999
            ts = f"2026-04-29T12:00:{sec:02d}.{us:06d}+00:00"
            cmd = [sys.executable, str(picker),
                   "--field-notes", str(fn_path),
                   "--words", str(words),
                   "--retired", str(retired),
                   "--init-template", str(init_template),
                   "--mode", "single",
                   "--wishful-share", str(share),
                   "--force-timestamp", ts]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if proc.returncode == 0:
                try:
                    data = json.loads(proc.stdout)
                    ops[data["operator"]] += 1
                except (json.JSONDecodeError, KeyError):
                    pass
        return ops

    # 1. share=0.0 over 200 runs: only base operators
    ops = run_n(0.0, 200)
    ok_1 = ("wishful-thinking" not in ops
            and sum(ops[k] for k in ("reversal", "exaggeration", "escape")) > 0)
    asserts.append(("share=0.0 -> only base operators",
                    ok_1, "" if ok_1 else f"got {dict(ops)}"))

    # 2. share=0.25 over 200 runs: wishful >= 1, <= 50
    ops = run_n(0.25, 200)
    wt = ops.get("wishful-thinking", 0)
    ok_2 = (1 <= wt <= 50)
    asserts.append(("share=0.25 -> 1..50 wishful",
                    ok_2, "" if ok_2 else f"wt={wt} of {sum(ops.values())}"))

    # 3. share=1.0 over 200 runs: each operator >= 30 and <= 70
    ops = run_n(1.0, 200)
    counts = [ops.get(k, 0) for k in ("reversal", "exaggeration", "escape", "wishful-thinking")]
    ok_3 = all(30 <= c <= 70 for c in counts)
    asserts.append(("share=1.0 -> 30..70 each",
                    ok_3, "" if ok_3 else f"got counts={counts}"))

    # 4. invalid --wishful-share rejected
    fn_path = tmp_dir / "wishful-invalid-fn.md"
    if fn_path.exists():
        fn_path.unlink()
    proc = subprocess.run(
        [sys.executable, str(picker),
         "--field-notes", str(fn_path),
         "--words", str(words),
         "--retired", str(retired),
         "--init-template", str(init_template),
         "--mode", "single",
         "--wishful-share", "-0.5"],
        capture_output=True, text=True, timeout=10,
    )
    ok_4 = (proc.returncode != 0)
    asserts.append(("invalid share rejected",
                    ok_4, "" if ok_4 else f"rc={proc.returncode}"))

    # 5. validator accepts po_operator: wishful-thinking
    fixture = tmp_dir / "wishful-validator-fixture.md"
    fixture.write_text("""---
skill: crazy-professor
mode: single
version: 0.11.0
timestamp: 2026-04-29T12:00:00Z
topic: "smoke"
archetype: first-principles-jester
po_operator: wishful-thinking
provocation_word: smoke
---

# Single: smoke

> DIVERGENCE WARNING: smoke fixture.

## 10 Provocations

1. one — [cost: low] — anchor: x
2. two — [cost: low] — anchor: x
3. three — [cost: low] — anchor: x
4. four — [cost: low] — anchor: x
5. five — [cost: low] — anchor: x
6. six — [cost: low] — anchor: x
7. seven — [cost: low] — anchor: x
8. eight — [cost: low] — anchor: x
9. nine — [cost: low] — anchor: x
10. ten — [cost: low] — anchor: x

## Next Experiment
Run a smoke.

## Self-Flag
- [ ] kept
- [ ] retire-word
- [ ] voice-off
""", encoding="utf-8")
    validator = picker.parent / "validate_output.py"
    proc = subprocess.run(
        [sys.executable, str(validator), "--mode", "single", str(fixture)],
        capture_output=True, text=True, timeout=10,
    )
    ok_5 = (proc.returncode == 0)
    asserts.append(("validator accepts wishful-thinking",
                    ok_5, "" if ok_5 else f"rc={proc.returncode}, err={proc.stderr.strip()[:120]}"))

    # 6. Body that quotes wishful-thinking scaffold is not voice-drift
    # (lint_voice would be needed here; we approximate by checking the validator stays clean
    # when the body uses 'wishful thinking:' as part of a provocation)
    fixture2 = tmp_dir / "wishful-body-fixture.md"
    body = fixture.read_text(encoding="utf-8").replace(
        "1. one — [cost: low] — anchor: x",
        "1. wishful thinking: deploys happen without prerequisites — [cost: low] — anchor: x"
    )
    fixture2.write_text(body, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(validator), "--mode", "single", str(fixture2)],
        capture_output=True, text=True, timeout=10,
    )
    ok_6 = (proc.returncode == 0)
    asserts.append(("body with wishful scaffold validates",
                    ok_6, "" if ok_6 else f"rc={proc.returncode}, err={proc.stderr.strip()[:120]}"))

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

- [ ] **Step 4: Add render functions and CLI flags**

Add render functions right after `render_run_planner_section` (around line 246):

```python
def render_compact_section(stage: dict) -> list[str]:
    return _render_stage_section("Compact-mode smoke (Stage C)", stage)


def render_cross_pollination_section(stage: dict) -> list[str]:
    return _render_stage_section("Cross-pollination linter smoke (Stage D)", stage)


def render_wishful_section(stage: dict) -> list[str]:
    return _render_stage_section("Wishful-thinking picker smoke (Stage E)", stage)


def _render_stage_section(title: str, stage: dict) -> list[str]:
    lines: list[str] = ["", f"## {title}", ""]
    if not stage.get("available"):
        lines.append(f"Skipped: {stage.get('reason', 'not available')}")
        return lines
    if stage.get("passed"):
        lines.append(f"PASS -- {stage['passes']}/{stage['total']} asserts")
    else:
        first = stage.get("first_fail")
        first_label = first[0] if first else "unknown"
        first_detail = first[1] if first else ""
        lines.append(f"FAIL -- {stage['passes']}/{stage['total']} asserts; "
                     f"first failure: {first_label}"
                     + (f" ({first_detail})" if first_detail else ""))
    lines.append("")
    for label, ok in stage.get("asserts", []):
        marker = "ok" if ok else "FAIL"
        lines.append(f"- {marker}: {label}")
    return lines
```

In `render_report`, near the bottom (around line 332 — find where `run_planner_results` is appended), add three new conditional appends. Find:

```python
    if telemetry_results is not None:
        lines.extend(render_telemetry_section(telemetry_results))
    if run_planner_results is not None:
        lines.extend(render_run_planner_section(run_planner_results))

    return "\n".join(lines) + "\n"
```

Replace with (the function signature also gets 3 new optional params):

```python
    if telemetry_results is not None:
        lines.extend(render_telemetry_section(telemetry_results))
    if run_planner_results is not None:
        lines.extend(render_run_planner_section(run_planner_results))
    if compact_results is not None:
        lines.extend(render_compact_section(compact_results))
    if cp_results is not None:
        lines.extend(render_cross_pollination_section(cp_results))
    if wishful_results is not None:
        lines.extend(render_wishful_section(wishful_results))

    return "\n".join(lines) + "\n"
```

And update the function signature of `render_report` (line 249-251). Find:

```python
def render_report(picker_results: dict, corpus_results: dict | None,
                  meta: dict, telemetry_results: dict | None = None,
                  run_planner_results: dict | None = None) -> str:
```

Replace with:

```python
def render_report(picker_results: dict, corpus_results: dict | None,
                  meta: dict, telemetry_results: dict | None = None,
                  run_planner_results: dict | None = None,
                  compact_results: dict | None = None,
                  cp_results: dict | None = None,
                  wishful_results: dict | None = None) -> str:
```

Now find the same fallback section earlier in `render_report` (the "Skipped (no corpus dir)" block around line 286-291) and add the same three appends:

```python
    if corpus_results is None:
        lines.append("")
        lines.append("## Corpus (Stage B linter sweep)")
        lines.append("")
        lines.append("Skipped (no corpus dir).")
        if telemetry_results is not None:
            lines.extend(render_telemetry_section(telemetry_results))
        if run_planner_results is not None:
            lines.extend(render_run_planner_section(run_planner_results))
        if compact_results is not None:
            lines.extend(render_compact_section(compact_results))
        if cp_results is not None:
            lines.extend(render_cross_pollination_section(cp_results))
        if wishful_results is not None:
            lines.extend(render_wishful_section(wishful_results))
        return "\n".join(lines) + "\n"
```

- [ ] **Step 5: Wire the new stages into `main()`**

In `main()`, find the existing `run_planner_results` handling (around line 670-685):

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

Right after that block, add:

```python
    compact_results: dict | None = None
    if args.compact:
        print(f"running compact-mode smoke test...", file=sys.stderr)
        compact_results = stage_c_compact_smoke(args.validator, tmp_dir)

    cp_results: dict | None = None
    if args.cross_pollination:
        if not args.cross_pollination_linter:
            print("error: --cross-pollination-linter is required when --cross-pollination is set",
                  file=sys.stderr)
            return 2
        print(f"running cross-pollination linter smoke test...", file=sys.stderr)
        cp_results = stage_d_cross_pollination_smoke(args.cross_pollination_linter, tmp_dir)

    wishful_results: dict | None = None
    if args.wishful:
        print(f"running wishful-thinking picker smoke test...", file=sys.stderr)
        wishful_results = stage_e_wishful_smoke(
            args.picker, args.words, args.retired,
            args.field_notes_template, tmp_dir,
        )
```

Then update the `render_report` call near line 695:

```python
    report = render_report(picker_results, corpus_results, meta,
                           telemetry_results, run_planner_results)
```

Replace with:

```python
    report = render_report(picker_results, corpus_results, meta,
                           telemetry_results, run_planner_results,
                           compact_results, cp_results, wishful_results)
```

- [ ] **Step 6: Add the new CLI flags**

Find the argument-parser block in `main()` (line 600-625) and add three new arguments. After the `--run-planner-keywords` argument:

```python
    p.add_argument("--cross-pollination-linter", type=Path, default=None,
                   help="path to lint_cross_pollination.py for Stage D smoke")
    p.add_argument("--compact", action="store_true",
                   help="run Stage C (compact-mode validator smoke)")
    p.add_argument("--cross-pollination", action="store_true",
                   help="run Stage D (cross-pollination linter smoke)")
    p.add_argument("--wishful", action="store_true",
                   help="run Stage E (wishful-thinking picker smoke)")
```

- [ ] **Step 7: Add new picker assertion to Stage A**

Find `stage_b_picker` (line 96-128). It runs N picker calls per archetype. Add a wishful-thinking observability check at the bottom of the function before the `return results` line. Find:

```python
        results[arch] = {
            "runs": runs_per_archetype,
            "ok": ok,
            "pass_rate": round(ok / runs_per_archetype, 3) if runs_per_archetype else 0.0,
            "unique_words": len(words_drawn),
            "operator_distribution": dict(ops),
            "fail_reasons": Counter(fail_reasons).most_common(10),
        }
    return results
```

Replace with (adding a `wishful_seen` aggregate check after the loop):

```python
        results[arch] = {
            "runs": runs_per_archetype,
            "ok": ok,
            "pass_rate": round(ok / runs_per_archetype, 3) if runs_per_archetype else 0.0,
            "unique_words": len(words_drawn),
            "operator_distribution": dict(ops),
            "fail_reasons": Counter(fail_reasons).most_common(10),
        }
    # Aggregate operator presence — wishful-thinking should appear at least once
    # over all 200 runs at the default share of 0.25.
    seen_ops = set()
    for arch, r in results.items():
        seen_ops.update(r["operator_distribution"].keys())
    results["__operator_coverage__"] = {
        "all_seen": seen_ops,
        "wishful_seen": "wishful-thinking" in seen_ops,
    }
    return results
```

(Note: the picker is invoked with the default `--wishful-share 0.25` here, so wishful-thinking should appear in the 200 total runs.)

- [ ] **Step 8: Verify the 3 new stages run end-to-end**

Run from repo root (this exercises all of Stage C/D/E together):

```bash
TMP=$(mktemp -d)
mkdir -p "$TMP/corpus"
python skills/crazy-professor/scripts/eval_suite.py \
  --picker skills/crazy-professor/scripts/picker.py \
  --voice-linter skills/crazy-professor/scripts/lint_voice.py \
  --validator skills/crazy-professor/scripts/validate_output.py \
  --templates-dir skills/crazy-professor/prompt-templates \
  --field-notes-template skills/crazy-professor/resources/field-notes-init.md \
  --words skills/crazy-professor/resources/provocation-words.txt \
  --retired skills/crazy-professor/resources/retired-words.txt \
  --corpus "$TMP/corpus" \
  --report-out "$TMP/report.md" \
  --picker-runs 50 \
  --telemetry skills/crazy-professor/scripts/telemetry.py \
  --run-planner skills/crazy-professor/scripts/run_planner.py \
  --run-planner-keywords skills/crazy-professor/resources/archetype-keywords.txt \
  --cross-pollination-linter skills/crazy-professor/scripts/lint_cross_pollination.py \
  --compact \
  --cross-pollination \
  --wishful \
  --skill-version 0.11.0
cat "$TMP/report.md"
```

Expected: report has these new sections each showing PASS:
- `## Compact-mode smoke (Stage C)` — 5/5 PASS
- `## Cross-pollination linter smoke (Stage D)` — 8/8 PASS
- `## Wishful-thinking picker smoke (Stage E)` — 6/6 PASS

Plus the existing sections (Picker Stage A, Corpus, Telemetry, Run Planner) all still PASS.

If any assert fails, fix the failing stage's helper function or the underlying script and re-run before continuing.

- [ ] **Step 9: Save the eval baseline as `docs/eval-baseline-2026-04-29.md`**

Once Step 8 is fully PASS, save the report into `docs/`:

```bash
DATE=$(date +%F)
cp "$TMP/report.md" "docs/eval-baseline-$DATE.md"
git add "docs/eval-baseline-$DATE.md"
```

(Use the actual date your machine returns. Don't commit yet — Task 13 commits docs and version-bump together.)

- [ ] **Step 10: Commit Task 12**

```bash
git add skills/crazy-professor/scripts/eval_suite.py
git commit -m "crazy-professor | Phase-6 Task 12: eval_suite.py — Stages C/D/E

Stage C (compact-mode smoke, 5 asserts), Stage D (cross-pollination linter
smoke, 8 asserts), Stage E (wishful-thinking picker smoke, 6 asserts).
Total 19 new asserts. Plus operator-coverage aggregate in stage_b_picker.
New CLI flags: --compact, --cross-pollination, --cross-pollination-linter,
--wishful.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## CHECKPOINT 3 (after Task 12)

All implementation tasks done. Before Task 13 (docs + bump + push), verify:

```bash
git log --oneline -12
ls skills/crazy-professor/scripts/lint_cross_pollination.py
ls skills/crazy-professor/resources/stop-words.txt
grep -c "Wishful Thinking" skills/crazy-professor/resources/po-operators.md
grep -c "compact_mode" skills/crazy-professor/scripts/telemetry.py
grep -c "stage_c_compact_smoke" skills/crazy-professor/scripts/eval_suite.py
grep -c "stage_d_cross_pollination_smoke" skills/crazy-professor/scripts/eval_suite.py
grep -c "stage_e_wishful_smoke" skills/crazy-professor/scripts/eval_suite.py
```

Expected: 12 task commits, all files exist, all greps return ≥1.

---

## Task 13: Version bump + docs + push

This is a **large multi-file task** that bumps version + updates 4 docs + writes the master-plan-status update + adds the operating-instructions Step C4b + push. One single phase-completion commit at the end.

**Files (all modify):**
- `.claude-plugin/plugin.json`
- `skills/crazy-professor/SKILL.md`
- `skills/crazy-professor/resources/output-template.md`
- `skills/crazy-professor/resources/chat-output-template.md`
- `docs/chat-mode-flow.md`
- `skills/crazy-professor/prompt-templates/chat-curator.md`
- `skills/crazy-professor/prompt-templates/chat-round-1-wrapper.md`
- `skills/crazy-professor/prompt-templates/chat-round-2-wrapper.md`
- `skills/crazy-professor/references/operating-instructions.md`
- `docs/CHANGELOG.md`
- `docs/PROJECT.md`
- `docs/CAPABILITIES.md`
- `docs/ARCHITECTURE.md`
- `docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md`
- `docs/linters.md`

- [ ] **Step 1: Bump version `0.10.0` -> `0.11.0` in 8 files**

Run a `sed`-style replacement across all 8 files. **Important: only the literal `0.10.0` token in the version field gets replaced — don't blanket-replace, since some files mention historical versions in prose.**

For each file, open it and replace:

`.claude-plugin/plugin.json` — find `"version": "0.10.0"` -> `"version": "0.11.0"`.

`skills/crazy-professor/SKILL.md` — find `version: '0.10.0'` -> `version: '0.11.0'` (in the metadata block, around line 25).

`skills/crazy-professor/resources/output-template.md` — find the `version: 0.10.0` line in the embedded frontmatter example, replace with `version: 0.11.0`.

`skills/crazy-professor/resources/chat-output-template.md` — find `version: 0.10.0` in the embedded frontmatter, replace with `version: 0.11.0`.

`docs/chat-mode-flow.md` — find `version: 0.10.0` in own frontmatter (line 3) AND in the documented example frontmatter (search for the second occurrence around line 189). Both -> `0.11.0`.

`skills/crazy-professor/prompt-templates/chat-curator.md` — find `version: 0.10.0` (line 4) -> `version: 0.11.0`.

`skills/crazy-professor/prompt-templates/chat-round-1-wrapper.md` — find `version: 0.10.0` (line 5) -> `version: 0.11.0`.

`skills/crazy-professor/prompt-templates/chat-round-2-wrapper.md` — find `version: 0.10.0` (line 5) -> `version: 0.11.0`.

After all 8 edits, verify nothing else references the old version where it shouldn't:

```bash
grep -rn "0.10.0" skills/ .claude-plugin/ commands/ docs/ \
  | grep -v "CHANGELOG.md" \
  | grep -v "/plans/" \
  | grep -v "eval-baseline"
```

Expected output: empty (no remaining `0.10.0` outside of historical artifacts).

- [ ] **Step 2: Add the operating-instructions Step C4b + flag mentions**

Open `skills/crazy-professor/references/operating-instructions.md`. Find the line with `**Step C4 degradation:**` (around line 369). After the closing block of Step C4 (`This is NOT an abort; the chat-run continues to round 3.`), add a new Step C4b:

````markdown
**Step C4b: Cross-Pollination Substanz-Check (when `--strict-cross-pollination` is set, since v0.11.0).**

If `--strict-cross-pollination` was passed in the invocation, run the
cross-pollination linter on the Round 2 output:

```bash
python <repo-root>/skills/crazy-professor/scripts/lint_cross_pollination.py \
  --r1-input <tmp-r1.json> \
  --r2-input <tmp-r2.json> \
  [--min-overlap 1] \
  [--stop-words <repo-root>/skills/crazy-professor/resources/stop-words.txt]
```

Skill writes the in-memory R1 + R2 sections to two temporary JSON files
in the form documented in the linter's docstring. The linter checks each
R2 item for: (1) `counter:`/`extend:` marker presence, (2) ref idx in
1..5 + ref archetype is in R1, (3) at least `min-overlap` non-stopword
tokens shared between R2 item text and the referenced R1 item text.

Linter writes JSON to stdout: `{low_substance_hits, findings, stats}`.
Exit code is always 0 (warn-only).

For each finding, the skill locates the original R2 item line and
appends `[low-substance: <reason>]` at the end of the line. The
findings count goes into telemetry field `low_substance_hits` in
Step C7b.

Without `--strict-cross-pollination`, this step is skipped entirely.
Round 3 still runs as normal — the linter does NOT filter or remove
items, it only annotates.

If R2 was set to `degraded` in Step C4 (≥2 archetypes < 2 items), this
step is also skipped (no R2 items to lint). Telemetry
`low_substance_hits: 0`, `round2_status: skipped`.
````

Now find the `**Step 7b: Append telemetry record (since v0.9.0).**` block (around line 268) and update the `**New optional fields since v0.10.0**` section. Find:

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

Right after it, append:

```markdown
**New optional fields since v0.11.0** (Phase-6 substrate):

- `compact_mode` (bool): true if `--chat --compact` was active for this
  run. Single-run is always false (the flag is rejected at the command
  layer). Optional: omit for legacy single-runs.
- `low_substance_hits` (int): number of R2 items flagged by
  `lint_cross_pollination.py` when `--strict-cross-pollination` ran. 0
  if the flag was absent. Optional.
- `wishful_thinking_active` (bool): true if any picked operator in this
  run was `wishful-thinking`. In single-run: trivial string compare on
  `operator`. In chat-run: true if ≥1 of the 4 picks was `wishful-thinking`.
  Optional.

All three fields keep the Phase-4 contract: new fields must be optional,
never required. Readers ignore unknown fields.
```

Same for Step C7b — find the `**New optional fields since v0.10.0**`-equivalent block and add Phase-6 fields. (The Step C7b telemetry block does not currently document v0.10.0 optional fields explicitly; if there is no such block, just add a single new one analogous to the above.)

- [ ] **Step 3: Update `docs/CHANGELOG.md`**

Open `docs/CHANGELOG.md`. Add the new entry at the top (just under the title, before the previous v0.10.0 entry):

```markdown
## v0.11.0 — 2026-04-DD (Phase 6)

- New `--chat --compact` flag: reorders chat output so Round 3 (Final 20)
  + Top-3 + Next-Experiment + Self-Flag appear first; Round 1 + Round 2
  collapse into a `<details>` audit-trail block at the end.
- New `--strict-cross-pollination` flag: runs deterministic substance
  heuristic on Round 2 markers via `lint_cross_pollination.py`. Findings
  appear as `[low-substance: <reason>]` markers in R2 items (warn-only,
  no filtering).
- Wishful-thinking PO operator activated as 4th operator. Default
  `--wishful-share 0.25` (relative weight = ~14% wishful, ~28.6% each
  base operator). Set `--wishful-share 0.0` to revert to v0.10.0
  three-operator behavior, or `--wishful-share 1.0` for an even 25%
  split.
- `--compact` without `--chat` is rejected at the command layer.
- 3 new optional telemetry fields: `compact_mode`, `low_substance_hits`,
  `wishful_thinking_active`. Backward-compatible.
- New helper script `lint_cross_pollination.py` (4th linter, ~250 LOC,
  stdlib-only).
- New resource `stop-words.txt` (~100 entries, EN+DE mix + archetype
  labels).
- Eval-suite extended with 3 new smoke stages (Stage C/D/E, +19 asserts).
- `po-operators.md` now contains a full Wishful-Thinking section with
  Definition, Scaffold, and Distinction-from-Reversal-and-Escape.
```

Replace `2026-04-DD` with today's actual date (e.g. `2026-04-29`).

- [ ] **Step 4: Update `docs/PROJECT.md`**

Find the "Aktueller Stand" line. Update it to reference v0.11.0 and Master-Plan 6/8.

If the file currently has a line like `Aktueller Stand: v0.10.0, Master-Plan 5/8`, replace with `Aktueller Stand: v0.11.0, Master-Plan 6/8`. If the format is different, edit in-place to reflect the same content.

- [ ] **Step 5: Update `docs/CAPABILITIES.md`**

Add three new rows in the appropriate Capabilities table (Phase 6 section if it exists, otherwise as new entries). Use the format already established in the file. The three new capabilities:

- `--chat --compact`-flag — Status: active, 2026-04-DD
- `--strict-cross-pollination`-flag — Status: active, 2026-04-DD
- 4. PO-Operator wishful-thinking — Status: active, 2026-04-DD

Replace `2026-04-DD` with today's date.

- [ ] **Step 6: Update `docs/ARCHITECTURE.md`**

Add `lint_cross_pollination.py` to the Skripte-Liste as the 4th linter. If the file has a script-table or a script-list, add a line:

`lint_cross_pollination.py (v0.11.0) — cross-pollination substance heuristic. Marker + Ref-Resolution + Token-Overlap. stdlib-only. Used in Step C4b when --strict-cross-pollination is set. Warn-only (exit 0 always).`

If the file mentions the chat-output template structure, briefly mention the compact-mode reorder + `<details>` audit-trail. One-paragraph note is sufficient.

- [ ] **Step 7: Update Master-Plan**

Open `docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md`. Find the Phase-6 row in the Phasen-Tabelle:

```markdown
| 6     | **Cross-Pollination + Kompakt-Modus**                                | `--chat --compact`; Round-2-Substanz-Check (`--strict-cross-pollination`); 4. PO-Operator aktiviert      | ⏳     |
```

Replace the trailing `⏳` cell with `✅ (2026-04-DD)`. Replace `2026-04-DD` with today's date.

- [ ] **Step 8: Update `docs/linters.md`**

Open `docs/linters.md`. Find the section listing the linters. Add a new entry analogous to `lint_voice.py` and `lint_word_pool.py`:

```markdown
## lint_cross_pollination.py (since v0.11.0)

The cross-pollination substance linter is the 4th member of the Linter-
Trio, activated only when `--strict-cross-pollination` is passed to a
chat-mode invocation. It enforces three deterministic checks per Round 2
item:

1. **Marker existence**: `counter: <ref>` or `extend: <ref>` must be present.
2. **Ref resolution**: `<ref>` must point to an existing R1 item
   (archetype + idx in 1..5).
3. **Token overlap**: at least `--min-overlap` (default 1) non-stopword
   tokens (≥3 chars) must be shared between the R2 item text and the
   referenced R1 item text. Stop-words from
   `resources/stop-words.txt`.

Findings are warn-only — the linter never filters or removes R2 items.
Output is JSON on stdout. Exit code is always 0. The skill ingests the
JSON, locates each flagged R2 line, and appends
`[low-substance: <reason>]` at the end. The total finding count is
recorded in telemetry as `low_substance_hits`.

See operating-instructions Step C4b for invocation details.
```

- [ ] **Step 9: Re-run the full Eval Suite to confirm all stages PASS**

Re-execute the full eval-suite invocation from Task 12 Step 8. Expected: all stages still PASS, `0.11.0` shows as `skill-version` in the report header.

- [ ] **Step 10: Lokale Self-Verification**

Spec calls for self-verification (Codex-Verifier-Pattern is permanent default; do not invoke Codex). Read each modified file once with `git diff --stat`:

```bash
git status
git diff --stat HEAD~12..HEAD
```

Expected: 12 commits between checkpoint, ~13-15 files modified, ~+2000 lines / ~-50 lines net. Spot-check `lint_cross_pollination.py`, `eval_suite.py`, and `picker.py` once more for:
- Hard-coded paths beyond `<repo-root>` (none should exist).
- Imports of non-stdlib modules (none should exist).
- Missing exit-code handling (every CLI returns int).

If any check fails, fix and amend the relevant Task's commit.

- [ ] **Step 11: Stage all docs + commit Task 13**

```bash
git add .claude-plugin/plugin.json
git add skills/crazy-professor/SKILL.md
git add skills/crazy-professor/resources/output-template.md
git add skills/crazy-professor/resources/chat-output-template.md
git add docs/chat-mode-flow.md
git add skills/crazy-professor/prompt-templates/chat-curator.md
git add skills/crazy-professor/prompt-templates/chat-round-1-wrapper.md
git add skills/crazy-professor/prompt-templates/chat-round-2-wrapper.md
git add skills/crazy-professor/references/operating-instructions.md
git add docs/CHANGELOG.md docs/PROJECT.md docs/CAPABILITIES.md docs/ARCHITECTURE.md
git add docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md
git add docs/linters.md
git add docs/eval-baseline-*.md  # the new baseline saved in Task 12 Step 9

git commit -m "crazy-professor | v0.11.0: Phase-6 — Cross-Pollination + Compact-Mode

Phase 6 complete. Master-Plan 6/8 ✅.

User-visible changes:
- --chat --compact: reorder + <details> audit-trail
- --strict-cross-pollination: lint_cross_pollination.py warn-only heuristic
- wishful-thinking 4th PO operator (--wishful-share, default 0.25)
- 3 new optional telemetry fields (compact_mode, low_substance_hits,
  wishful_thinking_active)
- Eval-Suite Stages C/D/E (+19 asserts)

Version bump 0.10.0 -> 0.11.0 across 8 frontmatter files.
Operating-Instructions Step C4b documented.
Docs synced: CHANGELOG, PROJECT, CAPABILITIES, ARCHITECTURE, linters,
Master-Plan-Status.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 12: Push to origin/master**

```bash
git push origin master
```

Expected: 13 new commits pushed (12 task commits + 1 phase-completion commit). Repo on `origin/master` matches local.

---

## Acceptance criteria for Phase 6

- [x] All 13 task commits in `git log --oneline | head -15`.
- [x] `--chat --compact` produces reorder + `<details>` audit-trail (Tasks 1-3).
- [x] `--compact` without `--chat` rejected (Task 2).
- [x] `--strict-cross-pollination` triggers `lint_cross_pollination.py`, R2 items get `[low-substance: <reason>]` markers when flagged (Tasks 4-7).
- [x] `lint_cross_pollination.py` exists, stdlib-only, exit 0 always (Task 5-7).
- [x] `wishful-thinking` is 4th PO operator with configurable share (Task 8). At share=0.0 the picker behaves identically to v0.10.0.
- [x] `po-operators.md` has full Wishful-Thinking section (Task 10).
- [x] 3 new optional telemetry fields in schema (Task 11).
- [x] Eval-Suite Stages C/D/E all PASS (Task 12).
- [x] Version 0.11.0 in all 8 frontmatter files (Task 13 Step 1).
- [x] `docs/CHANGELOG.md` Phase-6 entry with date (Task 13 Step 3).
- [x] Master-Plan status updated to 6/8 ✅ (Task 13 Step 7).
- [x] Local self-verification done (Codex not invoked) (Task 13 Step 10).
- [x] Pushed to `origin/master` (Task 13 Step 12).

If any checkbox cannot be ticked at the end, document the gap in the final commit body and surface it to the user as an open item.
