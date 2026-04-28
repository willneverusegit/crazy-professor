# Phase 7 — Single-File-HTML-Playground Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a browser-based playground to crazy-professor as v0.12.0 — `/crazy --playground` triggers a stdlib-only build script that generates a single-file HTML playground (Cockpit-Layout: topic input + 3-element picker + roll/re-roll buttons + live prompt-output + copy button + field-notes footer), opened via the OS default browser. Plus `picker.py --force-word` and `--force-operator`, plus eval-suite Stage F.

**Architecture:** Browser stays a pure picker + prompt-builder + copy-helper — no LLM calls, no HTTP server, no file-system writes from JS. Distribution is single-file HTML with inlined JSON data (built from source resources by `build_playground.py`). Slash-command runs build then `webbrowser.open()`; user copies the prompt back into the terminal as a normal `/crazy <topic> --force-archetype X --force-word Y --force-operator Z` invocation. Stage F asserts build determinism + data-drift detection.

**Tech Stack:** Python 3 stdlib (argparse, json, pathlib, re, sys, webbrowser, html). HTML5 + vanilla JavaScript (Clipboard API, no external CDN). Markdown for docs. Git for version control.

**Spec reference:** `docs/specs/2026-04-28-phase-7-playground-design.md` (commit `d7f822f`).

**Repo paths:**
- Repo root: `C:/Users/domes/Desktop/Claude-Plugins-Skills/crazy-professor`
- All script paths below are relative to that root.

**Commit cadence:** one commit per task at the end of the task. Final phase-completion commit consolidates the version bump + docs (Task 12).

**Implementation order:** picker first (Task 1), build skript skeleton + body (Tasks 2-5), HTML CSS + JS (Tasks 6-7), slash-command (Task 8), eval-stage (Task 9), then docs + bump + push (Task 10-12).

---

## Task 1: `picker.py` — `--force-word` and `--force-operator`

**Files:**
- Modify: `skills/crazy-professor/scripts/picker.py`

- [ ] **Step 1: Add the two new CLI flags**

Open `skills/crazy-professor/scripts/picker.py`. Find the existing `--force-archetype` and `--force-timestamp` block in `main()` (around line 215):

```python
    p.add_argument("--force-archetype", choices=ARCHETYPES, help="bypass mod-4 picker")
    p.add_argument("--force-timestamp", help="ISO-8601 UTC override (testing)")
    p.add_argument("--wishful-share", type=float, default=0.25,
                   help="relative weight for wishful-thinking operator (weights = "
                        "[1, 1, 1, share*3]). 0.0 = disabled (3-operator legacy). "
                        "0.333 = equal 25%% each. 1.0 = wishful ~50%% (weights [1,1,1,3]). "
                        "Default 0.25 = ~14%% wishful, ~28.6%% each base operator.")
```

Insert two new arguments right after `--force-archetype`:

```python
    p.add_argument("--force-archetype", choices=ARCHETYPES, help="bypass mod-4 picker")
    p.add_argument("--force-word", help="bypass word random pick (variation-guard still applies)")
    p.add_argument("--force-operator",
                   choices=("reversal", "exaggeration", "escape", "wishful-thinking"),
                   help="bypass operator random pick (variation-guard still applies)")
    p.add_argument("--force-timestamp", help="ISO-8601 UTC override (testing)")
    p.add_argument("--wishful-share", type=float, default=0.25,
                   help="relative weight for wishful-thinking operator (weights = "
                        "[1, 1, 1, share*3]). 0.0 = disabled (3-operator legacy). "
                        "0.333 = equal 25%% each. 1.0 = wishful ~50%% (weights [1,1,1,3]). "
                        "Default 0.25 = ~14%% wishful, ~28.6%% each base operator.")
```

- [ ] **Step 2: Update `pick_single()` to apply force flags + accumulate forced-markers**

Find the existing `pick_single()` function (around line 142):

```python
def pick_single(args, words: list[str], rows: list[dict], ts: dt.datetime) -> dict:
    archetype, operator, ts_iso = picker_seed(ts, wishful_share=args.wishful_share)
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
```

Replace it entirely with:

```python
def pick_single(args, words: list[str], rows: list[dict], ts: dt.datetime) -> dict:
    archetype, operator, ts_iso = picker_seed(ts, wishful_share=args.wishful_share)
    if args.force_archetype:
        archetype = args.force_archetype
    if args.force_operator:
        operator = args.force_operator
    word = pick_word(words, ts)
    if args.force_word:
        if args.force_word in words:
            word = args.force_word
        else:
            print(f"warning: --force-word {args.force_word!r} not in active pool "
                  f"(retired or unknown), falling back to random pick",
                  file=sys.stderr)
    archetype, word, re_rolled = variation_guard(archetype, word, rows, words, ts)
    forced_markers = []
    if args.force_archetype:
        forced_markers.append("forced-archetype")
    if args.force_word:
        forced_markers.append("forced-word")
    if args.force_operator:
        forced_markers.append("forced-operator")
    if forced_markers:
        prefix = "+".join(forced_markers)
        re_rolled = prefix if re_rolled == "no" else f"{prefix}+{re_rolled}"
    return {
        "timestamp": ts_iso,
        "mode": "single",
        "archetype": archetype,
        "word": word,
        "operator": operator,
        "re_rolled": re_rolled,
        "field_notes_rows_read": len(rows),
    }
```

- [ ] **Step 3: Smoke-test all three force-flag combinations**

Run from repo root (Windows-Bash; uses Python helper for robustness):

```bash
cd C:/Users/domes/Desktop/Claude-Plugins-Skills/crazy-professor
python -c "
import json, pathlib, tempfile, subprocess, sys
tmp = pathlib.Path(tempfile.mkdtemp())
fn = tmp/'field-notes.md'
fn.write_text('')

# Test 1: --force-word with valid word
proc = subprocess.run([
    sys.executable, 'skills/crazy-professor/scripts/picker.py',
    '--field-notes', str(fn),
    '--words', 'skills/crazy-professor/resources/provocation-words.txt',
    '--retired', 'skills/crazy-professor/resources/retired-words.txt',
    '--init-template', 'skills/crazy-professor/resources/field-notes-init.md',
    '--mode', 'single',
    '--force-word', 'smoke',
    '--force-timestamp', '2026-04-29T12:00:00+00:00'
], capture_output=True, text=True)
data = json.loads(proc.stdout)
print('Test 1 (--force-word smoke):')
print(f'  word={data[\"word\"]}, re_rolled={data[\"re_rolled\"]}')
assert data['word'] == 'smoke', f'expected smoke, got {data[\"word\"]}'
assert 'forced-word' in data['re_rolled']
print('  OK')

# Test 2: --force-operator wishful-thinking
proc = subprocess.run([
    sys.executable, 'skills/crazy-professor/scripts/picker.py',
    '--field-notes', str(fn),
    '--words', 'skills/crazy-professor/resources/provocation-words.txt',
    '--retired', 'skills/crazy-professor/resources/retired-words.txt',
    '--init-template', 'skills/crazy-professor/resources/field-notes-init.md',
    '--mode', 'single',
    '--force-operator', 'wishful-thinking',
    '--force-timestamp', '2026-04-29T12:00:00+00:00'
], capture_output=True, text=True)
data = json.loads(proc.stdout)
print()
print('Test 2 (--force-operator wishful-thinking):')
print(f'  operator={data[\"operator\"]}, re_rolled={data[\"re_rolled\"]}')
assert data['operator'] == 'wishful-thinking'
assert 'forced-operator' in data['re_rolled']
print('  OK')

# Test 3: all three forces combined
proc = subprocess.run([
    sys.executable, 'skills/crazy-professor/scripts/picker.py',
    '--field-notes', str(fn),
    '--words', 'skills/crazy-professor/resources/provocation-words.txt',
    '--retired', 'skills/crazy-professor/resources/retired-words.txt',
    '--init-template', 'skills/crazy-professor/resources/field-notes-init.md',
    '--mode', 'single',
    '--force-archetype', 'first-principles-jester',
    '--force-word', 'smoke',
    '--force-operator', 'reversal',
    '--force-timestamp', '2026-04-29T12:00:00+00:00'
], capture_output=True, text=True)
data = json.loads(proc.stdout)
print()
print('Test 3 (all three forces):')
print(f'  archetype={data[\"archetype\"]}, word={data[\"word\"]}, operator={data[\"operator\"]}')
print(f'  re_rolled={data[\"re_rolled\"]}')
assert data['archetype'] == 'first-principles-jester'
assert data['word'] == 'smoke'
assert data['operator'] == 'reversal'
assert all(m in data['re_rolled'] for m in ('forced-archetype', 'forced-word', 'forced-operator'))
print('  OK')

# Test 4: --force-word with retired word -> warning + fallback
fake_retired = tmp/'fake-retired.txt'
fake_retired.write_text('smoke\n')
proc = subprocess.run([
    sys.executable, 'skills/crazy-professor/scripts/picker.py',
    '--field-notes', str(fn),
    '--words', 'skills/crazy-professor/resources/provocation-words.txt',
    '--retired', str(fake_retired),
    '--init-template', 'skills/crazy-professor/resources/field-notes-init.md',
    '--mode', 'single',
    '--force-word', 'smoke',
    '--force-timestamp', '2026-04-29T12:00:00+00:00'
], capture_output=True, text=True)
print()
print('Test 4 (--force-word with retired word):')
print(f'  stderr: {proc.stderr.strip()[:120]}')
assert 'warning' in proc.stderr.lower()
print('  OK -- warning emitted on stderr')
"
```

Expected output: 4 PASS lines (`OK` each), no failures.

- [ ] **Step 4: Verify Stage A still passes (regression)**

Run the eval-suite Stage A picker block to confirm no regression. Use a fresh tmp dir:

```bash
python -c "
import tempfile, pathlib
tmp = pathlib.Path(tempfile.mkdtemp())
corpus = tmp / 'corpus'
corpus.mkdir()
print(tmp)
" > /tmp/eval-tmp-t1.txt
TMP=$(cat /tmp/eval-tmp-t1.txt)
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
  --skill-version 0.12.0-test 2>&1 | tail -3
grep "Pass-Rate" "$TMP/report.md"
```

Expected: 4 lines `| <archetype> | 50 | 50 | 100.0% | ...` showing all four archetypes at 100% pass-rate. If any archetype shows < 100%, investigate the picker change before continuing.

- [ ] **Step 5: Commit Task 1**

```bash
git add skills/crazy-professor/scripts/picker.py
git commit -m "$(cat <<'EOF'
crazy-professor | Phase-7 Task 1: picker.py — --force-word and --force-operator

Two new CLI flags analog zu --force-archetype. Force is applied before
variation_guard, which can override (forced-word + word in last 10 rows
-> re_rolled becomes 'forced-word+word'). Forced markers accumulate via
'+' join. --force-word with retired word warns on stderr and falls back
to random.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: `build_playground.py` — skeleton + arg parser

**Files:**
- Create: `skills/crazy-professor/scripts/build_playground.py`

- [ ] **Step 1: Write the skeleton with imports, constants, and arg parser**

Create `skills/crazy-professor/scripts/build_playground.py` with this initial content. Tasks 3-5 add the actual build logic:

```python
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
    1  usage error / missing required args
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
```

- [ ] **Step 2: Smoke-test the skeleton**

```bash
cd C:/Users/domes/Desktop/Claude-Plugins-Skills/crazy-professor
TMP_OUT=$(python -c "import tempfile, pathlib; print(pathlib.Path(tempfile.mkdtemp()) / 'pg.html')")
python skills/crazy-professor/scripts/build_playground.py \
  --output "$TMP_OUT" \
  --words skills/crazy-professor/resources/provocation-words.txt \
  --retired skills/crazy-professor/resources/retired-words.txt \
  --po-operators skills/crazy-professor/resources/po-operators.md \
  --version 0.12.0-test
echo "exit=$?"
test -f "$TMP_OUT" && echo "file exists, $(wc -l < "$TMP_OUT") lines"
grep -c "const VERSION" "$TMP_OUT"
grep -c "const WORDS" "$TMP_OUT"
grep -c "const OPERATORS" "$TMP_OUT"
grep -c "const ARCHETYPES" "$TMP_OUT"
grep -c "const FIELD_NOTES_RECENT" "$TMP_OUT"
```

Expected: exit=0, file exists with at least 5 lines, each `grep -c` returns `1`.

- [ ] **Step 3: Test missing required arg**

```bash
python skills/crazy-professor/scripts/build_playground.py \
  --output /tmp/x.html
echo "exit=$?"
```

Expected: argparse error, exit code 2 (argparse uses exit code 2 for missing required args, NOT 1 as the docstring says — that's normal Python behavior; `sys.exit(2)` is reserved for source-file errors which we explicitly raise).

**Note**: The docstring says "exit 1 = usage error", but argparse uses exit 2 for missing args. This is a documentation-vs-reality detail; treat both 1 and 2 as "user error" exits. Stage F Assert 8 will use `proc.returncode != 0` (any non-zero), avoiding the discrepancy.

- [ ] **Step 4: Commit Task 2**

```bash
git add skills/crazy-professor/scripts/build_playground.py
git commit -m "$(cat <<'EOF'
crazy-professor | Phase-7 Task 2: build_playground.py — skeleton + arg parser

Stdlib-only Python helper. Reads source resources (provocation-words,
retired-words, po-operators, optional field-notes), emits stub HTML
with inlined VERSION/ARCHETYPES/OPERATORS/WORDS/FIELD_NOTES_RECENT
constants. Tasks 3-5 fill in CSS, body markup, and JS logic.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: `build_playground.py` — CSS string

**Files:**
- Modify: `skills/crazy-professor/scripts/build_playground.py`

- [ ] **Step 1: Add CSS_BLOCK module-level constant**

Open `skills/crazy-professor/scripts/build_playground.py`. Right after the `DEFAULT_OPERATORS` tuple (around line 30), insert this constant:

```python
CSS_BLOCK = """
:root {
  --bg: #0a0a0a;
  --bg-card: #161616;
  --border: rgba(255, 255, 255, 0.1);
  --text: #d4d4d4;
  --text-dim: #888;
  --accent-archetype: #7ec0ee;
  --accent-word: #9ec587;
  --accent-operator: #e0af68;
  --accent-warn: #ff9a3c;
  --button: #2a2a2a;
  --button-hover: #383838;
  --button-primary: #7ec0ee;
  --button-primary-text: #0a0a0a;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 14px;
  min-height: 100vh;
}

.header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-weight: 600;
}

.header .version {
  font-size: 12px;
  color: var(--text-dim);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}

.container {
  max-width: 720px;
  margin: 0 auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

#topic {
  width: 100%;
  padding: 12px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  font-family: inherit;
  font-size: 15px;
}

#topic:focus {
  outline: none;
  border-color: var(--accent-archetype);
}

.cockpit {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

@media (max-width: 540px) {
  .cockpit { grid-template-columns: 1fr; }
}

.cell {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 16px 12px;
  text-align: center;
}

.cell .label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-dim);
  margin-bottom: 8px;
}

.cell .pick {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 16px;
  font-weight: 600;
}

.cell.archetype { border-color: rgba(126, 192, 238, 0.3); }
.cell.archetype .pick { color: var(--accent-archetype); }

.cell.word { border-color: rgba(158, 197, 135, 0.3); }
.cell.word .pick { color: var(--accent-word); }

.cell.operator { border-color: rgba(224, 175, 104, 0.3); }
.cell.operator .pick { color: var(--accent-operator); }

.cell.empty .pick {
  color: var(--text-dim);
  font-style: italic;
  font-weight: 400;
}

button, select {
  background: var(--button);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 10px 14px;
  font-family: inherit;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.1s;
}

button:hover, select:hover { background: var(--button-hover); }

button.primary {
  background: var(--button-primary);
  color: var(--button-primary-text);
  font-weight: 600;
  font-size: 14px;
  padding: 12px 16px;
}

button.primary:hover { background: #95cef0; }

#roll-all { width: 100%; }

.reroll-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
}

.reroll-row button, .reroll-row select { font-size: 12px; padding: 8px 10px; }

#prompt-output {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 14px 16px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
  color: var(--text-dim);
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
  min-height: 64px;
}

#prompt-output.has-prompt { color: var(--text); }

#copy-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

#copy { flex: 1; }

#copy-feedback {
  color: var(--accent-word);
  font-size: 13px;
  opacity: 0;
  transition: opacity 0.2s;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}

#copy-feedback.show { opacity: 1; }

.field-notes-footer {
  border-top: 1px solid var(--border);
  padding-top: 16px;
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-dim);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  line-height: 1.6;
}

.field-notes-footer .label {
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 10px;
  margin-bottom: 6px;
  color: var(--text-dim);
}

.field-notes-footer .row { display: block; }

.field-notes-footer .warn {
  color: var(--accent-warn);
  margin-top: 4px;
}

noscript {
  display: block;
  background: rgba(255, 154, 60, 0.1);
  border: 1px solid var(--accent-warn);
  border-radius: 6px;
  padding: 12px 16px;
  margin: 16px 24px;
  color: var(--accent-warn);
  font-size: 13px;
}
"""
```

- [ ] **Step 2: Verify the constant has no syntax errors**

```bash
python -c "
from importlib.util import spec_from_file_location, module_from_spec
spec = spec_from_file_location('bp', 'skills/crazy-professor/scripts/build_playground.py')
m = module_from_spec(spec)
spec.loader.exec_module(m)
print(f'CSS_BLOCK length: {len(m.CSS_BLOCK)} chars')
"
```

Expected: a length around 3500-4500 chars, no exception.

- [ ] **Step 3: Commit Task 3**

```bash
git add skills/crazy-professor/scripts/build_playground.py
git commit -m "$(cat <<'EOF'
crazy-professor | Phase-7 Task 3: build_playground.py — CSS string

Adds CSS_BLOCK module-level constant: dark theme, monospace for picks
and prompt, system font for UI. Cockpit grid responsive (3 cols
desktop, 1 col mobile). Color-coding: archetype=blue, word=green,
operator=orange, warn=amber. Used by build_html() in Task 5.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: `build_playground.py` — JavaScript string

**Files:**
- Modify: `skills/crazy-professor/scripts/build_playground.py`

- [ ] **Step 1: Add JS_BLOCK module-level constant**

Open `skills/crazy-professor/scripts/build_playground.py`. Right after `CSS_BLOCK` (the closing `"""`), insert this constant:

```python
JS_BLOCK = """
const state = {
  topic: "",
  archetype: null,
  word: null,
  operator: null,
};

function pickRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function rollAll() {
  state.archetype = pickRandom(ARCHETYPES);
  state.word = pickRandom(WORDS);
  state.operator = pickRandom(OPERATORS);
  updateAll();
}

function rerollWord() {
  state.word = pickRandom(WORDS);
  updateAll();
}

function rerollOp() {
  state.operator = pickRandom(OPERATORS);
  updateAll();
}

function pickArchetype(value) {
  if (value) {
    state.archetype = value;
    updateAll();
  }
}

function escapeTopic(t) {
  return t.replace(/\\\\/g, "\\\\\\\\").replace(/"/g, '\\\\"').replace(/\\n/g, " ").trim();
}

function updatePrompt() {
  const out = document.getElementById("prompt-output");
  const t = state.topic.trim();
  if (!t || !state.archetype || !state.word || !state.operator) {
    out.textContent = "(enter a topic above and roll the picker)";
    out.classList.remove("has-prompt");
    return;
  }
  const escaped = escapeTopic(t);
  out.textContent = `/crazy "${escaped}" --force-archetype ${state.archetype} --force-word ${state.word} --force-operator ${state.operator}`;
  out.classList.add("has-prompt");
}

function renderCockpit() {
  const archCell = document.getElementById("archetype-cell");
  const wordCell = document.getElementById("word-cell");
  const opCell = document.getElementById("op-cell");
  archCell.querySelector(".pick").textContent = state.archetype || "(roll to pick)";
  archCell.classList.toggle("empty", !state.archetype);
  wordCell.querySelector(".pick").textContent = state.word || "(roll to pick)";
  wordCell.classList.toggle("empty", !state.word);
  opCell.querySelector(".pick").textContent = state.operator || "(roll to pick)";
  opCell.classList.toggle("empty", !state.operator);
}

function streakInfo() {
  if (!FIELD_NOTES_RECENT.length) {
    return { lastArchetype: null, lastWord: null, streak: 0 };
  }
  const reversed = [...FIELD_NOTES_RECENT].reverse();
  const lastArchetype = reversed[0].archetype;
  const lastWord = reversed[0].word;
  let streak = 0;
  for (const r of reversed) {
    if (r.archetype === lastArchetype) streak++;
    else break;
  }
  return { lastArchetype, lastWord, streak };
}

function renderFooter() {
  const footer = document.getElementById("field-notes-footer");
  if (!FIELD_NOTES_RECENT.length) {
    footer.innerHTML = '<div class="label">field-notes context</div><div class="row">(no recent runs)</div>';
    return;
  }
  const { lastArchetype, lastWord, streak } = streakInfo();
  let html = '<div class="label">field-notes context (last ' + FIELD_NOTES_RECENT.length + ' rows)</div>';
  html += '<div class="row">last archetype: ' + lastArchetype + ' (streak: ' + streak + ')</div>';
  html += '<div class="row">last word: ' + lastWord + '</div>';
  if (streak >= 3 && state.archetype === lastArchetype) {
    html += '<div class="row warn">' + state.archetype + ' would be streak ' + (streak + 1) + ' -- CLI variation-guard will re-roll</div>';
  }
  footer.innerHTML = html;
}

function updateAll() {
  renderCockpit();
  updatePrompt();
  renderFooter();
}

async function copyPrompt() {
  const out = document.getElementById("prompt-output");
  if (!out.classList.contains("has-prompt")) return;
  const fb = document.getElementById("copy-feedback");
  try {
    await navigator.clipboard.writeText(out.textContent);
    fb.textContent = "Copied!";
    fb.classList.add("show");
    setTimeout(function () { fb.classList.remove("show"); }, 1500);
  } catch (err) {
    alert("Clipboard unavailable -- copy the prompt above manually.");
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const topicInput = document.getElementById("topic");
  topicInput.addEventListener("input", function (e) {
    state.topic = e.target.value;
    updatePrompt();
  });
  document.getElementById("roll-all").addEventListener("click", rollAll);
  document.getElementById("reroll-word").addEventListener("click", rerollWord);
  document.getElementById("reroll-op").addEventListener("click", rerollOp);
  const archSelect = document.getElementById("archetype-pick");
  archSelect.addEventListener("change", function (e) {
    pickArchetype(e.target.value);
    e.target.value = "";
  });
  document.getElementById("copy").addEventListener("click", copyPrompt);
  topicInput.focus();
  updateAll();
});
"""
```

- [ ] **Step 2: Verify the constant**

```bash
python -c "
from importlib.util import spec_from_file_location, module_from_spec
spec = spec_from_file_location('bp', 'skills/crazy-professor/scripts/build_playground.py')
m = module_from_spec(spec)
spec.loader.exec_module(m)
print(f'JS_BLOCK length: {len(m.JS_BLOCK)} chars')
print('contains rollAll:', 'function rollAll' in m.JS_BLOCK)
print('contains streakInfo:', 'function streakInfo' in m.JS_BLOCK)
print('contains DOMContentLoaded:', 'DOMContentLoaded' in m.JS_BLOCK)
"
```

Expected: length ~3000-3500 chars, all three checks `True`.

- [ ] **Step 3: Commit Task 4**

```bash
git add skills/crazy-professor/scripts/build_playground.py
git commit -m "$(cat <<'EOF'
crazy-professor | Phase-7 Task 4: build_playground.py — JavaScript string

Adds JS_BLOCK module-level constant: state object, pickRandom helper,
rollAll/rerollWord/rerollOp/pickArchetype, prompt-builder with quote+
backslash escape, render functions for cockpit cells + footer +
streak-warning, copyPrompt with clipboard fallback. DOMContentLoaded
wires all listeners. Auto-focuses topic input on load.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: `build_playground.py` — full HTML body builder

**Files:**
- Modify: `skills/crazy-professor/scripts/build_playground.py`

- [ ] **Step 1: Replace the stub `build_html()` with a full builder**

Open `skills/crazy-professor/scripts/build_playground.py`. Find the existing stub:

```python
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
```

Replace it entirely with:

```python
def build_html(version: str, words: list[str], operators: list[str],
               field_notes: list[dict]) -> str:
    """Build the complete single-file HTML playground."""
    archetype_options = "".join(
        f'<option value="{a}">{a}</option>' for a in ARCHETYPES
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>crazy-professor playground</title>
<style>{CSS_BLOCK}</style>
</head>
<body>
<noscript>JavaScript required for the picker. Use <code>/crazy &lt;topic&gt;</code> directly in your terminal as fallback.</noscript>
<div class="header">
  <span>crazy-professor &mdash; Playground</span>
  <span class="version">v{version}</span>
</div>
<div class="container">
  <input id="topic" type="text" placeholder="Topic..." autocomplete="off">
  <div class="cockpit">
    <div class="cell archetype empty" id="archetype-cell">
      <div class="label">Archetype</div>
      <div class="pick">(roll to pick)</div>
    </div>
    <div class="cell word empty" id="word-cell">
      <div class="label">Word</div>
      <div class="pick">(roll to pick)</div>
    </div>
    <div class="cell operator empty" id="op-cell">
      <div class="label">Operator</div>
      <div class="pick">(roll to pick)</div>
    </div>
  </div>
  <button id="roll-all" class="primary">Roll All</button>
  <div class="reroll-row">
    <button id="reroll-word">Re-Roll Word</button>
    <button id="reroll-op">Re-Roll Op</button>
    <select id="archetype-pick">
      <option value="">Pick Archetype...</option>
      {archetype_options}
    </select>
  </div>
  <pre id="prompt-output">(enter a topic above and roll the picker)</pre>
  <div id="copy-row">
    <button id="copy" class="primary">Copy Prompt</button>
    <span id="copy-feedback"></span>
  </div>
  <div class="field-notes-footer" id="field-notes-footer"></div>
</div>
<script>
const VERSION = "{version}";
const ARCHETYPES = {json.dumps(list(ARCHETYPES))};
const OPERATORS = {json.dumps(operators)};
const WORDS = {json.dumps(words)};
const FIELD_NOTES_RECENT = {json.dumps(field_notes)};
{JS_BLOCK}
</script>
</body>
</html>
"""
```

- [ ] **Step 2: Smoke-test the full build**

```bash
cd C:/Users/domes/Desktop/Claude-Plugins-Skills/crazy-professor
TMP_OUT=$(python -c "import tempfile, pathlib; print(pathlib.Path(tempfile.mkdtemp()) / 'pg.html')")
python skills/crazy-professor/scripts/build_playground.py \
  --output "$TMP_OUT" \
  --words skills/crazy-professor/resources/provocation-words.txt \
  --retired skills/crazy-professor/resources/retired-words.txt \
  --po-operators skills/crazy-professor/resources/po-operators.md \
  --version 0.12.0-test
echo "exit=$?"
test -f "$TMP_OUT" && echo "lines: $(wc -l < "$TMP_OUT")"
grep -c '<input id="topic"' "$TMP_OUT"
grep -c 'id="archetype-cell"' "$TMP_OUT"
grep -c 'id="word-cell"' "$TMP_OUT"
grep -c 'id="op-cell"' "$TMP_OUT"
grep -c 'id="roll-all"' "$TMP_OUT"
grep -c 'id="prompt-output"' "$TMP_OUT"
grep -c 'id="copy"' "$TMP_OUT"
grep -c 'function rollAll' "$TMP_OUT"
```

Expected: exit=0, file >100 lines, every `grep -c` returns `1`.

- [ ] **Step 3: Visually open the file once to confirm it works**

```bash
echo "Open this file in your browser to verify it renders:"
echo "  file:///$TMP_OUT" | sed 's|\\|/|g'
```

Optional manual check: open the file, type a topic, click Roll All, verify the prompt updates with the picks, click Copy. (This is not part of the automated test gate; it's a one-time visual sanity check.)

- [ ] **Step 4: Build the live playground file at the canonical path**

```bash
mkdir -p skills/crazy-professor/playground
python skills/crazy-professor/scripts/build_playground.py \
  --output skills/crazy-professor/playground/index.html \
  --words skills/crazy-professor/resources/provocation-words.txt \
  --retired skills/crazy-professor/resources/retired-words.txt \
  --po-operators skills/crazy-professor/resources/po-operators.md \
  --version 0.12.0
test -f skills/crazy-professor/playground/index.html && echo "playground ready"
```

Expected: `playground ready` printed.

- [ ] **Step 5: Commit Task 5**

```bash
git add skills/crazy-professor/scripts/build_playground.py skills/crazy-professor/playground/index.html
git commit -m "$(cat <<'EOF'
crazy-professor | Phase-7 Task 5: build_playground.py — full HTML body builder

Replaces the Task-2 stub. build_html() now emits a complete single-file
playground: noscript fallback, header with version, container with
topic input, 3-cell cockpit (archetype/word/op), roll-all + reroll-row
(reroll word, reroll op, archetype picker dropdown), prompt-output pre,
copy button + feedback span, field-notes footer. Inlines CSS_BLOCK,
JS_BLOCK, and the 5 data constants (VERSION, ARCHETYPES, OPERATORS,
WORDS, FIELD_NOTES_RECENT).

Initial playground/index.html committed for v0.12.0.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## CHECKPOINT 1 (after Task 5)

Sub-Features 7.3 (picker) and 7.4 (build script + initial HTML) complete. Verify:

```bash
git log --oneline -5
ls skills/crazy-professor/scripts/build_playground.py
ls skills/crazy-professor/playground/index.html
python skills/crazy-professor/scripts/build_playground.py --help | head -3
python skills/crazy-professor/scripts/picker.py --help | grep -E "(force-word|force-operator)"
```

Expected: 5 task commits, both files exist, both helpers print usage. picker --help shows the two new force flags.

---

## Task 6: `build_playground.py` — pre-existing playground/index.html drift check

**Files:**
- (No new file modifications — this is a verification task)

- [ ] **Step 1: Run a fresh build, diff against current**

The built file from Task 5 is at `skills/crazy-professor/playground/index.html`. To verify the build is reproducible (idempotent), run again to a temp file and diff:

```bash
cd C:/Users/domes/Desktop/Claude-Plugins-Skills/crazy-professor
TMP_OUT=$(python -c "import tempfile, pathlib; print(pathlib.Path(tempfile.mkdtemp()) / 'pg2.html')")
python skills/crazy-professor/scripts/build_playground.py \
  --output "$TMP_OUT" \
  --words skills/crazy-professor/resources/provocation-words.txt \
  --retired skills/crazy-professor/resources/retired-words.txt \
  --po-operators skills/crazy-professor/resources/po-operators.md \
  --version 0.12.0
diff -q "$TMP_OUT" skills/crazy-professor/playground/index.html
echo "diff-exit=$?"
```

Expected: `diff-exit=0` (files identical).

- [ ] **Step 2: Test field-notes integration**

Build with the Desktop field-notes path (if it exists) to confirm the footer data is inlined:

```bash
FN_PATH="$HOME/Desktop/.agent-memory/lab/crazy-professor/field-notes.md"
if [ -f "$FN_PATH" ]; then
  TMP_OUT=$(python -c "import tempfile, pathlib; print(pathlib.Path(tempfile.mkdtemp()) / 'pg-with-fn.html')")
  python skills/crazy-professor/scripts/build_playground.py \
    --output "$TMP_OUT" \
    --words skills/crazy-professor/resources/provocation-words.txt \
    --retired skills/crazy-professor/resources/retired-words.txt \
    --po-operators skills/crazy-professor/resources/po-operators.md \
    --field-notes "$FN_PATH" \
    --version 0.12.0-fn-test
  python -c "
import re
text = open(r'$TMP_OUT', encoding='utf-8').read()
m = re.search(r'const FIELD_NOTES_RECENT = (\\[.*?\\]);', text, re.DOTALL)
print('FIELD_NOTES_RECENT match:', bool(m))
if m:
    print('snippet:', m.group(1)[:200])
"
else
  echo "No Desktop field-notes file found (skipping integration test)"
fi
```

Expected: if Desktop field-notes exists, the constant should be a JSON array (possibly empty `[]` if no Log section, otherwise `[{"archetype": ..., "word": ..., "operator": ...}, ...]`).

- [ ] **Step 3: No commit (verification-only task)**

This task confirms idempotency and field-notes integration. Nothing to commit unless a defect was found.

---

## Task 7: `commands/crazy.md` — accept `--playground`

**Files:**
- Modify: `commands/crazy.md`

- [ ] **Step 1: Update the argument-hint frontmatter**

Open `commands/crazy.md`. Find the frontmatter line:

```yaml
argument-hint: [topic] [--chat] [--from-session] [--dry-run] [--compact] [--strict-cross-pollination]
```

Replace with:

```yaml
argument-hint: [topic] [--chat] [--from-session] [--dry-run] [--compact] [--strict-cross-pollination] [--playground]
```

- [ ] **Step 2: Add the new bullet**

In the body, find the bullet that starts `- If \`$ARGUMENTS\` contains \`--strict-cross-pollination\`` (added in Phase 6). Append a new bullet immediately after it:

```markdown
- If `$ARGUMENTS` contains `--playground` (since v0.12.0, single-run only), run the build script and open the HTML playground in the user's browser. The skill: (1) calls `python <repo-root>/skills/crazy-professor/scripts/build_playground.py` with the current resource files and the local `.agent-memory/lab/crazy-professor/field-notes.md` (Desktop-fallback if local missing) as `--field-notes` source, (2) prints the absolute path of `<repo-root>/skills/crazy-professor/playground/index.html`, (3) opens the file via `webbrowser.open()` (or prints a `start file:///<path>` hint on environments where `webbrowser.open()` is unreliable). The playground is browser-side only — no LLM calls, no file writes from the browser. The user copies the generated prompt and runs it as a normal `/crazy <topic> --force-archetype X --force-word Y --force-operator Z` invocation in the terminal. `--playground` cannot combine with `--chat`, `--from-session`, `--dry-run`, `--compact`, or `--strict-cross-pollination` — these are rejected at the command layer with `--playground is single-run only and standalone (no --chat/--from-session/--dry-run/--compact/--strict-cross-pollination combinations).`
```

- [ ] **Step 3: Verify**

```bash
grep -c "playground" commands/crazy.md
grep -c "playground is single-run only" commands/crazy.md
```

Expected: both `>= 1`.

- [ ] **Step 4: Commit Task 7**

```bash
git add commands/crazy.md
git commit -m "$(cat <<'EOF'
crazy-professor | Phase-7 Task 7: commands/crazy.md — accept --playground

--playground triggers build_playground.py + webbrowser.open() and is
single-run-only-and-standalone. Reject-Matrix: cannot combine with
--chat, --from-session, --dry-run, --compact, --strict-cross-pollination.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Operating-Instructions Step 1 — `--playground` rules

**Files:**
- Modify: `skills/crazy-professor/references/operating-instructions.md`

- [ ] **Step 1: Add the new topic-resolution bullet**

Open `skills/crazy-professor/references/operating-instructions.md`. Find the existing `--dry-run` bullet block in Step 1 (around line 42, the one that ends with `Combining --chat --dry-run is rejected at the command layer (commands/crazy.md).`). Append a new bullet immediately after it (still inside Step 1):

```markdown
- **Single-run with `--playground` (since v0.12.0, single-run only and standalone):** instead of parsing a topic and generating provocations, run `python <repo-root>/skills/crazy-professor/scripts/build_playground.py` with the active resource files (`provocation-words.txt`, `retired-words.txt`, `po-operators.md`) and the field-notes path (local `.agent-memory/lab/crazy-professor/field-notes.md` first, Desktop-fallback `~/Desktop/.agent-memory/lab/crazy-professor/field-notes.md` if local missing). Pass `--version` from `.claude-plugin/plugin.json`. The script writes/refreshes `<repo-root>/skills/crazy-professor/playground/index.html`. Then open the HTML file via the OS's default browser handler (Python `webbrowser.open()`, fallback: print `Open this file manually: file://<absolute-path>`). No topic argument is parsed — the playground accepts the topic via its input field. The reject-matrix is: `--playground` rejects in combination with `--chat`, `--from-session`, `--dry-run`, `--compact`, or `--strict-cross-pollination`. Reject message: `--playground is single-run only and standalone (no --chat/--from-session/--dry-run/--compact/--strict-cross-pollination combinations).`
```

- [ ] **Step 2: Verify**

```bash
grep -c "Single-run with --playground" skills/crazy-professor/references/operating-instructions.md
grep -c "playground is single-run only and standalone" skills/crazy-professor/references/operating-instructions.md
```

Expected: both `>= 1`.

- [ ] **Step 3: Commit Task 8**

```bash
git add skills/crazy-professor/references/operating-instructions.md
git commit -m "$(cat <<'EOF'
crazy-professor | Phase-7 Task 8: operating-instructions Step 1 — --playground rules

Adds the topic-resolution bullet for --playground: build script call,
field-notes-path resolution (local + Desktop fallback), browser open
via webbrowser.open() with manual-open fallback, complete reject-matrix
message.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: `eval_suite.py` — Stage F (playground build smoke)

**Files:**
- Modify: `skills/crazy-professor/scripts/eval_suite.py`

- [ ] **Step 1: Add `stage_f_playground_build_smoke` function**

Open `skills/crazy-professor/scripts/eval_suite.py`. Right after `stage_e_wishful_smoke()` (search for `def stage_e_wishful_smoke`), find the end of that function (it returns a dict). Insert this new function right after it:

```python
def stage_f_playground_build_smoke(build_script: Path, words: Path,
                                   retired: Path, po_operators: Path,
                                   tmp_dir: Path) -> dict:
    """8-assert smoke test for build_playground.py."""
    if not build_script.exists():
        return {"available": False,
                "reason": f"build script not found: {build_script}"}
    if not po_operators.exists():
        return {"available": False,
                "reason": f"po-operators file not found: {po_operators}"}

    asserts: list[tuple[str, bool, str]] = []

    out_html = tmp_dir / "playground-stagef.html"
    proc = subprocess.run(
        [sys.executable, str(build_script),
         "--output", str(out_html),
         "--words", str(words),
         "--retired", str(retired),
         "--po-operators", str(po_operators),
         "--version", "0.12.0-test"],
        capture_output=True, text=True, timeout=10,
    )
    ok_1 = (proc.returncode == 0 and out_html.exists())
    asserts.append(("build runs clean with required args",
                    ok_1, "" if ok_1 else f"rc={proc.returncode}, err={proc.stderr.strip()[:120]}"))

    if not out_html.exists():
        for label in ("HTML well-formed",
                      "VERSION constant matches --version arg",
                      "WORDS count matches active pool",
                      "OPERATORS = 4 Phase-6 operators",
                      "ARCHETYPES = 4 active archetypes",
                      "FIELD_NOTES_RECENT = [] for empty field-notes",
                      "missing --output rejected"):
            asserts.append((label, False, "build did not produce file"))
        passed = sum(1 for _, ok, _ in asserts if ok)
        total = len(asserts)
        first_fail = next(((label, detail) for label, ok, detail in asserts if not ok), None)
        return {
            "available": True,
            "passed": False,
            "passes": passed,
            "total": total,
            "asserts": [(label, ok) for label, ok, _ in asserts],
            "first_fail": first_fail,
        }

    text = out_html.read_text(encoding="utf-8")

    ok_2 = (text.startswith("<!DOCTYPE html>")
            and "<head>" in text and "<body>" in text
            and "</body>" in text and "</html>" in text)
    asserts.append(("HTML well-formed", ok_2, ""))

    ok_3 = 'const VERSION = "0.12.0-test"' in text
    asserts.append(("VERSION constant matches --version arg", ok_3, ""))

    expected_pool = [
        line.strip()
        for line in words.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    retired_set: set[str] = set()
    if retired.exists():
        retired_set = {
            line.strip()
            for line in retired.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        }
    expected_active = [w for w in expected_pool if w not in retired_set]
    import re as re_mod
    words_match = re_mod.search(r"const WORDS = (\[.*?\]);", text, re_mod.DOTALL)
    ok_4 = False
    detail_4 = ""
    if words_match:
        try:
            inlined_words = json.loads(words_match.group(1))
            ok_4 = (len(inlined_words) == len(expected_active))
            if not ok_4:
                detail_4 = f"expected {len(expected_active)}, found {len(inlined_words)}"
        except json.JSONDecodeError as exc:
            detail_4 = f"WORDS JSON parse failed: {exc}"
    else:
        detail_4 = "WORDS const not found in output"
    asserts.append(("WORDS count matches active pool", ok_4, detail_4))

    ok_5 = ('"reversal"' in text and '"exaggeration"' in text
            and '"escape"' in text and '"wishful-thinking"' in text
            and 'const OPERATORS = [' in text)
    asserts.append(("OPERATORS = 4 Phase-6 operators", ok_5, ""))

    ok_6 = all(a in text for a in (
        '"first-principles-jester"', '"labyrinth-librarian"',
        '"systems-alchemist"', '"radagast-brown"'))
    asserts.append(("ARCHETYPES = 4 active archetypes", ok_6, ""))

    empty_fn = tmp_dir / "empty-fn.md"
    empty_fn.write_text(
        "# Empty\n\n## Log\n\n"
        "| # | Timestamp | Archetype | Word | Operator | Topic slug | Output file | "
        "Re-rolled | Kept | Retire-word | Voice-off | Review1-Votum |\n"
        "|---|-----------|-----------|------|----------|------------|"
        "-------------|-----------|------|-------------|-----------|---------------|\n",
        encoding="utf-8",
    )
    out_empty = tmp_dir / "playground-empty-fn.html"
    subprocess.run(
        [sys.executable, str(build_script),
         "--output", str(out_empty),
         "--words", str(words), "--retired", str(retired),
         "--po-operators", str(po_operators),
         "--field-notes", str(empty_fn),
         "--version", "0.12.0-test"],
        capture_output=True, text=True, timeout=10,
    )
    text_empty = out_empty.read_text(encoding="utf-8") if out_empty.exists() else ""
    ok_7 = "const FIELD_NOTES_RECENT = []" in text_empty
    asserts.append(("FIELD_NOTES_RECENT = [] for empty field-notes",
                    ok_7, "" if ok_7 else "expected empty array"))

    proc = subprocess.run(
        [sys.executable, str(build_script),
         "--words", str(words), "--retired", str(retired),
         "--po-operators", str(po_operators)],
        capture_output=True, text=True, timeout=10,
    )
    ok_8 = (proc.returncode != 0)
    asserts.append(("missing --output rejected",
                    ok_8, "" if ok_8 else f"rc={proc.returncode}"))

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

- [ ] **Step 2: Add render function**

Find `render_wishful_section` near the top of the render functions (around line 270). Right after it, add:

```python
def render_playground_section(stage: dict) -> list[str]:
    return _render_stage_section("Playground build smoke (Stage F)", stage)
```

- [ ] **Step 3: Update `render_report` signature + add appends**

Find the `render_report` signature:

```python
def render_report(picker_results: dict, corpus_results: dict | None,
                  meta: dict, telemetry_results: dict | None = None,
                  run_planner_results: dict | None = None,
                  compact_results: dict | None = None,
                  cp_results: dict | None = None,
                  wishful_results: dict | None = None) -> str:
```

Replace with:

```python
def render_report(picker_results: dict, corpus_results: dict | None,
                  meta: dict, telemetry_results: dict | None = None,
                  run_planner_results: dict | None = None,
                  compact_results: dict | None = None,
                  cp_results: dict | None = None,
                  wishful_results: dict | None = None,
                  playground_results: dict | None = None) -> str:
```

Then find the **two** places where the optional-stage sections are appended. The first is in the `if corpus_results is None:` early-return branch (search for `if compact_results is not None:`). Find:

```python
        if compact_results is not None:
            lines.extend(render_compact_section(compact_results))
        if cp_results is not None:
            lines.extend(render_cross_pollination_section(cp_results))
        if wishful_results is not None:
            lines.extend(render_wishful_section(wishful_results))
        return "\n".join(lines) + "\n"
```

Replace with:

```python
        if compact_results is not None:
            lines.extend(render_compact_section(compact_results))
        if cp_results is not None:
            lines.extend(render_cross_pollination_section(cp_results))
        if wishful_results is not None:
            lines.extend(render_wishful_section(wishful_results))
        if playground_results is not None:
            lines.extend(render_playground_section(playground_results))
        return "\n".join(lines) + "\n"
```

The second place is at the bottom of `render_report` (search for the second occurrence of `if wishful_results is not None`). Find:

```python
    if compact_results is not None:
        lines.extend(render_compact_section(compact_results))
    if cp_results is not None:
        lines.extend(render_cross_pollination_section(cp_results))
    if wishful_results is not None:
        lines.extend(render_wishful_section(wishful_results))

    return "\n".join(lines) + "\n"
```

Replace with:

```python
    if compact_results is not None:
        lines.extend(render_compact_section(compact_results))
    if cp_results is not None:
        lines.extend(render_cross_pollination_section(cp_results))
    if wishful_results is not None:
        lines.extend(render_wishful_section(wishful_results))
    if playground_results is not None:
        lines.extend(render_playground_section(playground_results))

    return "\n".join(lines) + "\n"
```

- [ ] **Step 4: Add new CLI arguments**

Find the argparse block in `main()` (search for `--cross-pollination-linter`). Right after `--wishful` (or wherever the stage flags end), add:

```python
    p.add_argument("--build-playground", type=Path, default=None,
                   help="path to build_playground.py for Stage F smoke")
    p.add_argument("--po-operators", type=Path, default=None,
                   help="path to po-operators.md (required for Stage F)")
    p.add_argument("--playground", action="store_true",
                   help="run Stage F (playground build smoke)")
```

- [ ] **Step 5: Wire Stage F into `main()`**

Find the existing wishful-smoke block in `main()` (search for `wishful_results = stage_e_wishful_smoke(`). Right after the assignment to `wishful_results`, add:

```python
    playground_results: dict | None = None
    if args.playground:
        if not args.build_playground:
            print("error: --build-playground is required when --playground is set",
                  file=sys.stderr)
            return 2
        if not args.po_operators:
            print("error: --po-operators is required when --playground is set",
                  file=sys.stderr)
            return 2
        print("running playground build smoke test...", file=sys.stderr)
        playground_results = stage_f_playground_build_smoke(
            args.build_playground, args.words, args.retired,
            args.po_operators, tmp_dir,
        )
```

Then find the `render_report` call near the end of `main()`:

```python
    report = render_report(picker_results, corpus_results, meta,
                           telemetry_results, run_planner_results,
                           compact_results, cp_results, wishful_results)
```

Replace with:

```python
    report = render_report(picker_results, corpus_results, meta,
                           telemetry_results, run_planner_results,
                           compact_results, cp_results, wishful_results,
                           playground_results)
```

- [ ] **Step 6: Run the full eval suite with all stages**

```bash
cd C:/Users/domes/Desktop/Claude-Plugins-Skills/crazy-professor
TMP=$(python -c "import tempfile, pathlib; tmp = pathlib.Path(tempfile.mkdtemp()); (tmp/'corpus').mkdir(); print(tmp)")
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
  --build-playground skills/crazy-professor/scripts/build_playground.py \
  --po-operators skills/crazy-professor/resources/po-operators.md \
  --compact \
  --cross-pollination \
  --wishful \
  --playground \
  --skill-version 0.12.0 2>&1 | tail -3
echo "---PASS-Counts---"
grep -E "PASS --|FAIL --" "$TMP/report.md"
```

Expected: 6 PASS lines (Telemetry, Run Planner, Compact 5/5, Cross-Pollination 8/8, Wishful 6/6, Playground 8/8). No FAIL lines.

- [ ] **Step 7: Save the new eval baseline**

```bash
cp "$TMP/report.md" docs/eval-baseline-2026-04-28.md
```

(Same date as Phase 6, since we're still on 2026-04-28. Phase-7 update overwrites the Phase-6 baseline.)

- [ ] **Step 8: Commit Task 9**

```bash
git add skills/crazy-professor/scripts/eval_suite.py docs/eval-baseline-2026-04-28.md
git commit -m "$(cat <<'EOF'
crazy-professor | Phase-7 Task 9: eval_suite.py — Stage F (playground build smoke)

8 deterministic asserts for build_playground.py:
1. build runs clean with required args
2. HTML well-formed (DOCTYPE/head/body/closing tags)
3. VERSION constant matches --version arg
4. WORDS count matches active pool (drift-detection)
5. OPERATORS = 4 Phase-6 operators
6. ARCHETYPES = 4 active archetypes
7. FIELD_NOTES_RECENT = [] for empty-Log field-notes
8. missing --output rejected (exit non-zero)

CLI: --build-playground <path>, --po-operators <path>, --playground (run).
render_report extended with playground_results parameter (and 2 append
sites). Eval-Baseline updated with Stage F PASS.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## CHECKPOINT 2 (after Task 9)

All implementation tasks done (picker, build script, HTML, slash-command, operating-instructions, eval-stage). Verify:

```bash
git log --oneline -9
ls skills/crazy-professor/scripts/build_playground.py
ls skills/crazy-professor/playground/index.html
grep -c "stage_f_playground_build_smoke" skills/crazy-professor/scripts/eval_suite.py
grep -c "force-word\|force-operator" skills/crazy-professor/scripts/picker.py
grep -c "playground" commands/crazy.md
```

Expected: 9 task commits, both files exist, all greps return ≥1.

---

## Task 10: Version bump v0.11.0 → v0.12.0

**Files (8 frontmatter files to bump):**
- `.claude-plugin/plugin.json`
- `skills/crazy-professor/SKILL.md`
- `skills/crazy-professor/resources/output-template.md`
- `skills/crazy-professor/resources/chat-output-template.md`
- `docs/chat-mode-flow.md`
- `skills/crazy-professor/prompt-templates/chat-curator.md`
- `skills/crazy-professor/prompt-templates/chat-round-1-wrapper.md`
- `skills/crazy-professor/prompt-templates/chat-round-2-wrapper.md`

- [ ] **Step 1: Bump `.claude-plugin/plugin.json`**

Find: `"version": "0.11.0"` → Replace with: `"version": "0.12.0"`.

- [ ] **Step 2: Bump `skills/crazy-professor/SKILL.md`**

Find: `version: '0.11.0'` (in metadata block, around line 25) → Replace with: `version: '0.12.0'`.

- [ ] **Step 3: Bump `skills/crazy-professor/resources/output-template.md`**

Find: `version: 0.11.0` (in embedded frontmatter example) → Replace with: `version: 0.12.0`.

- [ ] **Step 4: Bump `skills/crazy-professor/resources/chat-output-template.md`**

Find: `version: 0.11.0` (in embedded frontmatter example) → Replace with: `version: 0.12.0`.

- [ ] **Step 5: Bump `docs/chat-mode-flow.md`**

There are two occurrences (own frontmatter + documented example). Replace both `version: 0.11.0` → `version: 0.12.0`.

- [ ] **Step 6: Bump three prompt-template wrappers**

For each of `chat-curator.md`, `chat-round-1-wrapper.md`, `chat-round-2-wrapper.md`: find `version: 0.11.0` → replace with `version: 0.12.0`.

- [ ] **Step 7: Verify no leftover 0.11.0 (excluding historical)**

```bash
cd C:/Users/domes/Desktop/Claude-Plugins-Skills/crazy-professor
grep -rn "0.11.0" skills/ .claude-plugin/ commands/ docs/ 2>/dev/null \
  | grep -v "CHANGELOG.md" \
  | grep -v "/plans/" \
  | grep -v "/specs/" \
  | grep -v "eval-baseline" \
  | grep -v "v0.11.0" \
  | grep -v "since v0.11.0"
```

Expected: empty output.

- [ ] **Step 8: Rebuild playground/index.html with new version**

```bash
python skills/crazy-professor/scripts/build_playground.py \
  --output skills/crazy-professor/playground/index.html \
  --words skills/crazy-professor/resources/provocation-words.txt \
  --retired skills/crazy-professor/resources/retired-words.txt \
  --po-operators skills/crazy-professor/resources/po-operators.md \
  --version 0.12.0
grep -c 'const VERSION = "0.12.0"' skills/crazy-professor/playground/index.html
```

Expected: `1`.

- [ ] **Step 9: No commit yet** (Task 12 commits all version-bump + docs together)

---

## Task 11: Operating-Instructions — Step 7b/C7b update for telemetry note

**Files:**
- Modify: `skills/crazy-professor/references/operating-instructions.md`

Telemetry schema is unchanged in Phase 7 (Klärung 7-(c)). But the operating-instructions Step 7b/C7b currently lists "v0.11.0 optional fields" — Phase-7 doesn't add fields, but we add a clarifying note.

- [ ] **Step 1: Add a Phase-7 note**

Find the existing Phase-6 optional fields block (Step 7b — around the line with `**New optional fields since v0.11.0** (Phase-6 substrate):`). Right after the closing of that block, append:

```markdown
**Phase 7 (since v0.12.0):** No new telemetry fields. Browser-triggered
runs from `/crazy --playground` produce a normal terminal `/crazy <topic>
--force-archetype X --force-word Y --force-operator Z` invocation;
telemetry sees them as standard single-runs with `forced-` markers in
the `re_rolled` field. Distinguishing browser-vs-direct-CLI is
intentionally out of scope (Phase-9 candidate if data analysis later
needs the distinction).
```

- [ ] **Step 2: Verify**

```bash
grep -c "Phase 7 (since v0.12.0)" skills/crazy-professor/references/operating-instructions.md
```

Expected: `1`.

- [ ] **Step 3: No commit yet** (Task 12 commits everything)

---

## Task 12: Docs sync + final commit + push

**Files:**
- `docs/CHANGELOG.md`, `docs/PROJECT.md`, `docs/CAPABILITIES.md`, `docs/ARCHITECTURE.md`
- `docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md`

- [ ] **Step 1: Update `docs/CHANGELOG.md`**

Open `docs/CHANGELOG.md`. Right after the title block / `---` separator (above the existing `## [v0.11.0]` entry), insert this new entry:

```markdown
## [v0.12.0] [2026-04-28] Phase 7 — Single-File-HTML-Playground

**Versions-Bump-Begründung (per VERSIONING.md):** MINOR-Bump weil ein neues user-visible Subsystem (HTML-Playground + Slash-Command-Flag) hinzukommt. Master-Plan-Phase 7 abgeschlossen (6/8 → 7/8 Phasen).

- **7.1 `/crazy --playground`-Flag**: triggert das neue Build-Skript `scripts/build_playground.py`, schreibt frisches HTML nach `playground/index.html`, oeffnet via `webbrowser.open()`. Reject-Matrix gegen `--chat`/`--from-session`/`--dry-run`/`--compact`/`--strict-cross-pollination`.
- **7.2 Browser-Playground (Single-File-HTML)**: Cockpit-Layout mit Topic-Input + 3-Element-Picker (Archetype/Word/Operator), Roll-All und per-Element-Re-Roll-Buttons, Live-Prompt-Output mit Copy-Button. Field-notes-Footer zeigt letzten Archetype + Streak-Warnung. Pure-Static (inlined Daten + JS), `file://`-tauglich, kein Server.
- **7.3 `picker.py --force-word` und `--force-operator`**: zwei neue Flags analog zu `--force-archetype`. Variation-Guard schlaegt Force konsistent. Neue `re_rolled`-Werte (`forced-word`, `forced-operator`, kombinierte Marker mit `+`).
- **7.4 Build-Skript `build_playground.py`** (~330 LOC, stdlib-only): liest Resources, parsed `po-operators.md` fuer die 4 Operator-Namen, liest optional die letzten 10 field-notes-Rows, generiert HTML mit inlined JS-Constants (CSS_BLOCK + JS_BLOCK module-level constants). Idempotent.
- **Eval-Suite Stage F (neu)** mit 8 deterministischen Asserts: Build-Skript-Smoke, HTML-Wohlgeformtheit, VERSION/WORDS/OPERATORS/ARCHETYPES-Konsistenz, FIELD_NOTES_RECENT-Inlining, Reject-ohne-required-Args.
- **Telemetrie**: keine Aenderung (Klaerung 7-(c) — Schema-Pause respektiert Phase-6-Active-Warning). Browser-Runs erscheinen in Telemetrie als normale CLI-Runs mit `forced-`-Markern.
- **Workflow-Pattern**: brainstorming → spec → plan → executing-plans (inline) — dritte vollstaendige Anwendung nach Phase 5+6.
```

- [ ] **Step 2: Update `docs/PROJECT.md`**

Open `docs/PROJECT.md`. Find the "Aktueller Stand" line (currently mentioning v0.11.0 + Master-Plan 6/8). Replace its text to mention v0.12.0 + 7/8 + the playground:

Find:

```markdown
v0.11.0 released 2026-04-28. Single-Run und Chat-Mode aktiv. Master-Plan-Phasen 1-6 abgeschlossen
```

Replace with:

```markdown
v0.12.0 released 2026-04-28. Single-Run, Chat-Mode und Browser-Playground aktiv. Master-Plan-Phasen 1-7 abgeschlossen
```

Then find the Phase-6 line in the Master-Plan-progress narrative (somewhere mentioning "Phase 7 (Cross-Pollination..." or "Phase 6 (Cross-Pollination..."). The exact text is:

```markdown
6 (Cross-Pollination Substanz-Check + Compact-Mode + 4. PO-Operator)
```

Append after that phrase, in the same sentence: `, 7 (Single-File-HTML-Playground via /crazy --playground)`.

Also update the offene Baustellen list. Find:

```markdown
- [x] Phase 6: `--chat --compact`, `--strict-cross-pollination`, 4. PO-Operator (`wishful thinking`) (✅ v0.11.0)
- [ ] Phase 7 (optional): Single-File-HTML-Playground
- [ ] Phase 8 (optional, RISIKO): Telegram-Bridge
```

Replace with:

```markdown
- [x] Phase 6: `--chat --compact`, `--strict-cross-pollination`, 4. PO-Operator (`wishful thinking`) (✅ v0.11.0)
- [x] Phase 7: Single-File-HTML-Playground (`/crazy --playground`) (✅ v0.12.0)
- [ ] Phase 8 (optional, RISIKO): Telegram-Bridge
```

- [ ] **Step 3: Update `docs/CAPABILITIES.md`**

Open `docs/CAPABILITIES.md`. Find the row that mentions `Telemetrie-Felder Phase 6` (Phase-6 v0.11.0 entry, the last "aktiv" row). Right after that row, insert these new rows:

```markdown
| `/crazy --playground`-Flag | aktiv | 2026-04-28 (v0.12.0) | Phase 7: triggert `build_playground.py` + oeffnet HTML via `webbrowser.open()`. Single-Run-only, standalone (Reject gegen `--chat`/`--from-session`/`--dry-run`/`--compact`/`--strict-cross-pollination`). |
| Browser-Playground (Single-File-HTML) | aktiv | 2026-04-28 (v0.12.0) | Phase 7: Cockpit-Layout. Topic-Input + 3-Element-Picker (Archetype/Word/Operator) mit Roll-All und per-Element-Re-Roll. Live-Prompt-Output mit Copy-Button. Field-notes-Footer mit Streak-Warnung. Pure-Static, `file://`-tauglich. |
| `picker.py --force-word` und `--force-operator` | aktiv | 2026-04-28 (v0.12.0) | Phase 7: zwei neue Force-Flags analog zu `--force-archetype`. Variation-Guard schlaegt Force konsistent. Neue `re_rolled`-Werte mit `forced-`-Praefix und `+`-Kombinationen. |
| Build-Skript `build_playground.py` | aktiv | 2026-04-28 (v0.12.0) | `scripts/build_playground.py` (stdlib-only): liest Resources (provocation-words, retired-words, po-operators, optional field-notes), generiert Single-File-HTML mit inlined JS-Constants. Idempotent. 9. stdlib-Skript. |
```

- [ ] **Step 4: Update `docs/ARCHITECTURE.md`**

Open `docs/ARCHITECTURE.md`. Find the Linter-Skripte-Sektion (heading `### Linter-Skripte (4 seit v0.11.0)`). Right after that section, insert a new section:

```markdown
### Browser-Playground (seit v0.12.0)
- **Datei(en):** `skills/crazy-professor/scripts/build_playground.py` (Build-Skript) + `skills/crazy-professor/playground/index.html` (gebautes Output) + Cockpit-Layout (CSS_BLOCK + JS_BLOCK module-level constants).
- **Aufgabe:** Browser-Playground als visuelle Schicht fuer den Picker. Build-Skript liest Resources zur Build-Zeit, generiert single-file HTML mit inlined Daten (kein HTTP-Server, `file://`-tauglich). Browser ist Pure-Picker + Prompt-Builder + Copy-Helper -- kein LLM-Call, kein File-System-Access. User kopiert generierten Prompt zurueck ins Terminal als normaler `/crazy <topic> --force-archetype X --force-word Y --force-operator Z`-Aufruf.
- **Abhaengigkeiten:** Stdlib-only Python fuer den Build. HTML5 + vanilla JavaScript (Clipboard API) fuer den Browser-Teil. Picker-Force-Flags (Phase 7) machen den Browser-Output validierbar gegen den CLI-Picker.
```

- [ ] **Step 5: Update Master-Plan**

Open `docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md`. Find the Phase-7 row in the Phasen-Tabelle:

```markdown
| 7     | **Visionäre Erweiterung — GUI/Playground** (optional, später)        | Single-File-HTML-Playground analog zur `playground` Skill; Browse/Compare/Keep/Retire UI                | ⏳     |
```

Replace the trailing `⏳` with `✅ (2026-04-28)`.

- [ ] **Step 6: Re-run the eval suite to confirm Phase-7 baseline still passes**

```bash
cd C:/Users/domes/Desktop/Claude-Plugins-Skills/crazy-professor
TMP=$(python -c "import tempfile, pathlib; tmp = pathlib.Path(tempfile.mkdtemp()); (tmp/'corpus').mkdir(); print(tmp)")
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
  --build-playground skills/crazy-professor/scripts/build_playground.py \
  --po-operators skills/crazy-professor/resources/po-operators.md \
  --compact \
  --cross-pollination \
  --wishful \
  --playground \
  --skill-version 0.12.0 2>&1 | tail -3
grep -E "PASS --|FAIL --" "$TMP/report.md"
cp "$TMP/report.md" docs/eval-baseline-2026-04-28.md
```

Expected: 6 PASS lines (Telemetry, Run Planner, Compact, Cross-Pollination, Wishful, Playground), 0 FAIL.

- [ ] **Step 7: Local self-verification**

```bash
git status
git diff --stat HEAD~9..HEAD | tail -20
```

Expected: ~13-15 modified files staged or modified, +1500 to +2500 line net diff. Spot-check `picker.py`, `build_playground.py`, `eval_suite.py` for any non-stdlib imports (none should exist) and exit-code completeness.

- [ ] **Step 8: Stage all docs + final commit**

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
git add skills/crazy-professor/playground/index.html
git add docs/CHANGELOG.md docs/PROJECT.md docs/CAPABILITIES.md docs/ARCHITECTURE.md
git add docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md
git add docs/eval-baseline-2026-04-28.md

git commit -m "$(cat <<'EOF'
crazy-professor | v0.12.0: Phase-7 — Single-File-HTML-Playground

Phase 7 complete. Master-Plan 7/8 ✅.

User-visible changes:
- /crazy --playground: build + open browser via webbrowser.open()
- Browser-Playground (Cockpit-Layout): Topic + 3-element picker +
  Roll-All + Re-Roll buttons + prompt-output + Copy-button + field-
  notes footer with streak-warning
- picker.py --force-word + --force-operator (variation-guard wins
  consistently with --force-archetype)
- New helper script build_playground.py (~330 LOC, stdlib-only)
- Eval-Suite Stage F (+8 asserts)

Version bump 0.11.0 -> 0.12.0 across 8 frontmatter files.
playground/index.html committed (rebuilt with v0.12.0 in inlined
VERSION constant).
Operating-Instructions Step 1 + Step 7b updated.
Docs synced: CHANGELOG, PROJECT, CAPABILITIES, ARCHITECTURE,
Master-Plan-Status. Eval-Baseline 2026-04-28 updated to Phase 7.

Telemetry schema unchanged (Phase-6 active-warning respected).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 9: Push (with explicit user OK)**

```bash
git status
echo "Ready to push. Confirm with user before running 'git push origin master'."
```

Push only after the user confirms.

```bash
git push origin master
```

---

## Acceptance criteria for Phase 7

- [x] All ~12 task commits in `git log --oneline | head -15`.
- [x] `/crazy --playground` wired into `commands/crazy.md` + Operating-Instructions Step 1 (Tasks 7-8).
- [x] `build_playground.py` exists, stdlib-only, generates a single-file HTML with inlined VERSION/ARCHETYPES/OPERATORS/WORDS/FIELD_NOTES_RECENT (Tasks 2-5).
- [x] `playground/index.html` committed, opens cleanly with `file://` (Task 5 + Task 10 rebuild).
- [x] Cockpit-Layout: 3 cells + Roll-All + per-Element-Re-Roll + dropdown + prompt-output + copy + footer (Task 4 JS + Task 5 body).
- [x] `picker.py --force-word` and `--force-operator` work analog to `--force-archetype`, variation-guard wins consistently (Task 1).
- [x] `re_rolled` field correctly emits `forced-word`, `forced-operator`, and combined markers like `forced-archetype+forced-word+word` (Task 1).
- [x] Eval-Suite Stage F implemented, 8/8 asserts PASS (Task 9).
- [x] Version 0.12.0 in all 8 frontmatter files (Task 10).
- [x] `docs/CHANGELOG.md` Phase-7 entry with date (Task 12 Step 1).
- [x] Master-Plan status updated to 7/8 ✅ (Task 12 Step 5).
- [x] Local self-verification done (Codex not invoked) (Task 12 Step 7).
- [x] Pushed to `origin/master` (Task 12 Step 9, after user OK).

If any checkbox cannot be ticked at the end, document the gap in the final commit body and surface it to the user as an open item.
