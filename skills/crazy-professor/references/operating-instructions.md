---
title: crazy-professor — Operating Instructions
status: v0.13.0 (Phase 4-8 zurückgebaut)
load_when: any invocation, after parsing the trigger
path_convention: all paths are relative to plugin repo root <repo-root> = crazy-professor/
---

# Operating Instructions

Claude follows these steps on every invocation. Steps 1-5 cover the
default single-run path; Steps C1-C6 cover Chat-Mode (`--chat`); Step
L1 covers `--lab`. All file paths are relative to the plugin repo root
(`<repo-root>` = `crazy-professor/`).

## Single-Run Path

**Step 1: Parse the topic.** Strip to a single sentence.

- If `$ARGUMENTS` contains `--lab`: jump to Step L1 (no topic parsing,
  no generation).
- **Single-run with topic:** proceed.
- **Single-run without topic:** use the most recent concrete task,
  plan, or problem from the current conversation as topic. If the
  conversation context is empty, meta, or too vague ("tell me a
  story", "how does this skill work"), ask one clarifying question
  and stop — do not fabricate a topic.
- **Chat-mode with topic:** proceed (jump to Step C1).
- **Chat-mode without topic** (`--chat` flag but no topic text):
  reject explicitly. Return:
  `Chat-mode requires an explicit topic. Run /crazy <topic> --chat or use single-run for ambient topics.`

**Step 2: Pick stochastic elements (picker call).**

```bash
python <repo-root>/skills/crazy-professor/scripts/picker.py \
  --field-notes <target-project>/.agent-memory/lab/crazy-professor/field-notes.md \
  --words <repo-root>/skills/crazy-professor/resources/provocation-words.txt \
  --retired <repo-root>/skills/crazy-professor/resources/retired-words.txt \
  --mode single
```

Parses one JSON object from stdout: `archetype`, `word`, `operator`,
`re_rolled`, `timestamp`. The variation-guard (3-archetype-streak
re-roll, 10-row word-window dedup) is applied inside the script.

If Python is unavailable, use the prose fallback documented in the
`picker.py` module docstring: `archetype = ARCHETYPES[utc_minute % 4]`,
`operator = OPERATORS[utc_second % 4]`, random word from the active
pool minus retired, then variation-guard manually.

**Step 3: Load the archetype's prompt template.** Read the matching
`<repo-root>/skills/crazy-professor/prompt-templates/<archetype>.md`
file. Its System-Prompt-Kern is the authoritative voice rules.

**Step 4: Generate 10 provocations.** Follow the archetype rules
strictly. Each provocation carries an Adoption-Cost-Tag (`low` |
`medium` | `high` | `system-break`) and a one-phrase anchor. Format
per line:

`<provocation text> -- [cost: <level>] -- anchor: <link>`

The cost tag is honest per provocation. No forced distribution. Pick
ONE of the 10 as the next experiment — the one most testable in under
one hour with tools the user already has.

Write the output file using the frontmatter and body structure
defined in
`<repo-root>/skills/crazy-professor/resources/output-template.md`,
to path
`<target-project>/.agent-memory/lab/crazy-professor/YYYY-MM-DD-HHMM-<topic-slug>.md`.
Create the directory if it does not exist.

**Step 5: Append a row to field-notes.md.** One Markdown table row in
`<target-project>/.agent-memory/lab/crazy-professor/field-notes.md`
matching the existing table columns (see
`<repo-root>/skills/crazy-professor/resources/field-notes-schema.md`).
At minimum: timestamp, archetype, word, operator, topic slug, output
filename, `re-rolled` value. Default review columns to `pending`.

## Chat-Mode Path (`--chat`)

**Step C1: Parse arguments.** Topic mandatory; reject `--chat` without
topic per Step 1 rule. Optional `--chat --dry-run-round1` runs only
round 1 (internal testing, no round 2/3).

**Step C2: Generate 4 picker calls.**

```bash
python <repo-root>/skills/crazy-professor/scripts/picker.py \
  --field-notes <target-project>/.agent-memory/lab/crazy-professor/field-notes.md \
  --words <repo-root>/skills/crazy-professor/resources/provocation-words.txt \
  --retired <repo-root>/skills/crazy-professor/resources/retired-words.txt \
  --mode chat
```

Returns 4 picks (one per archetype) in a single JSON object. Word-guard
runs intra-chat (no duplicate word within the chat-run; if duplicate,
re-roll with marker `re-rolled: intra-chat`).

**Step C3: Round 1 — 4 parallel LLM calls.** Each archetype with its
standard prompt template + `chat-round-1-wrapper.md` override block.
User message: topic + word + operator. Each archetype returns 5
provocations. Collect all 20.

If ≥2 of 4 archetypes return empty/format-broken output, abort
chat-mode and fall back to a single-run with a note in the output file
that chat-mode failed in round 1.

**Step C4: Round 2 — 4 parallel LLM calls.** Each archetype with its
standard prompt template + `chat-round-2-wrapper.md` override block.
User message: topic + the 15 provocations from the OTHER three
archetypes' round 1. Each archetype returns 2-3 provocations with
`counter:`/`extend:` markers.

Degradation: If ≥2 of 4 archetypes return fewer than 2 provocations,
set `round2_status: degraded` in the frontmatter, skip round-2 outputs
entirely, and pass only round-1 data to round 3. NOT an abort.

**Step C5: Round 3 — Codex distillation.** Invoke `codex:codex-rescue`
subagent with `chat-curator.md` prompt. Direct Markdown return: no
scratch file, no path-only response. Output must have exactly 4
sections × 5 ideas, a Top-3 Cross-Pollination block, and a Next
Experiment block.

If Codex fails (timeout/error/rate-limit) or returns broken structure
after one retry: run the identical distillation prompt through Claude
self-call. Mark `distiller: claude (codex-fallback)` in frontmatter
plus a `distiller_reason`.

**Step C6: Write output + append field-notes row.** Output to
`<target-project>/.agent-memory/lab/crazy-professor/chat/YYYY-MM-DD-HHMM-<topic-slug>.md`
using `chat-output-template.md`. Field-notes row marks `mode: chat`,
`archetype: all-4`, `word: multi`, `operator: multi`. Brief
user-facing summary: topic + 4 picks + round-2 status + distiller +
output-file pointer. Do NOT repeat the 20 final ideas in the chat —
the user reads them in the file.

## Lab Path (`--lab`, standalone)

**Step L1: Open the static lab.** Verify
`<repo-root>/skills/crazy-professor/lab/index.html` exists. Open it
via Python `webbrowser.open(...)`. Fallback if that fails: print
`Open this file manually: file://<absolute-path>`. No LLM call, no
file write, no field-notes row, no telemetry. Done.

The lab is paste-only: the user pastes an existing crazy-professor
output, scores ideas, copies one experiment card. Browser-side
JavaScript only.
