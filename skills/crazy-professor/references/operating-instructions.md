---
title: crazy-professor — Operating Instructions
status: extracted from SKILL.md 2026-04-27 (Phase 1, point 1.6)
load_when: any invocation, after parsing the trigger
path_convention: all paths are relative to plugin repo root <repo-root> = crazy-professor/
---

# Operating Instructions

Claude follows these steps on every invocation. Steps 1-7 cover the
default single-run path; Steps C1-C8 cover Chat-Mode (`--chat`). All
file paths below are relative to the plugin repo root (`<repo-root>` =
`crazy-professor/`); resolve them from there, not from this file's
location.

## Single-Run Path

**Step 1: Parse the topic.** Strip to a single sentence. Topic-resolution
contract (uniform across README.md, commands/crazy.md, and SKILL.md):

- **Single-run with topic:** proceed.
- **Single-run without topic:** use the most recent concrete task, plan,
  or problem from the current conversation as topic. If the conversation
  context is empty, meta, or too vague ("tell me a story", "how does this
  skill work"), ask one clarifying question and stop -- do not fabricate
  a topic.
- **Chat-mode with topic:** proceed.
- **Chat-mode without topic** (`--chat` flag but no topic text): reject
  explicitly. Return:
  `Chat-mode requires an explicit topic. Run /crazy <topic> --chat or use single-run for ambient topics.`
  Rationale: chat-mode costs ~10 LLM calls and 2-4 min wall-clock and
  must be deliberate. Single-run is the right tool for ambient topics.

**Step 2: Pick stochastic elements.**

- Archetype: take current UTC timestamp minute mod 4 (0=jester, 1=librarian,
  2=alchemist, 3=radagast-brown). This is deterministic-within-minute,
  random-across-minutes. All four archetypes active since 2026-04-23
  (Radagast activation passed, see
  `<repo-root>/skills/crazy-professor/references/radagast-activation.md`).
- Provocation word: pick one random line from
  `<repo-root>/skills/crazy-professor/resources/provocation-words.txt`.
  Filter out any word that also appears in
  `<repo-root>/skills/crazy-professor/resources/retired-words.txt`.
  The pool contains both single words and 2-3-token phrases (e.g.
  `paradox tax`, `false-bottom`) — both formats are valid.
- PO-operator: take timestamp second mod 3 (0=reversal, 1=exaggeration,
  2=escape).

**Step 2b: Variation guard (field-notes.md as forced input).**

Before accepting the Step 2 picks, read the last 10 rows of the "Log"
table in `.agent-memory/lab/crazy-professor/field-notes.md` (fewer if
the log is shorter). Apply these two rules in order:

- Archetype guard: if the same archetype appears in the last 3
  consecutive rows AND the Step 2 pick would make it a 4th, discard the
  pick and choose one of the other three archetypes (respecting the
  Radagast latency — if radagast-brown is still gated, choose from the
  remaining two). Tie-break: whichever of the candidates appeared least
  recently in the log, then alphabetical.
- Word guard: if the Step 2 word appears anywhere in the last 10 rows,
  draw another word from `provocation-words.txt` (still filtering against
  `retired-words.txt`). Repeat until a word is found that is not in the
  last 10 rows. If the pool is exhausted (every remaining word is in the
  window), accept the least-recently-used word.

Record the guard outcome for Step 7: one of `no`, `archetype`, `word`,
or `both`. This value goes into the `re-rolled` column in
field-notes.md.

Rationale: field-notes.md is otherwise write-only. Reading it before the
picker turns the log into backpressure that prevents archetype/word
clustering across sessions. Not total prohibition — just anti-streak.

**Step 3: Load the archetype's prompt template.** Read the matching
`<repo-root>/skills/crazy-professor/prompt-templates/*.md` file. Its
"System-Prompt-Kern" section is the authoritative voice rules.

**Step 4: Generate 10 provocations.** Follow the archetype rules strictly.
Each provocation carries two trailing metadata items: an Adoption-Cost-Tag
(`low` | `medium` | `high` | `system-break`) and a one-phrase anchor to
the user's infrastructure. Format per line:

`<provocation text> -- [cost: <level>] -- anchor: <link>`

The cost tag is assigned honestly per provocation. No forced distribution.
If all 10 are `system-break`, that is the truth about the run. If all 10
are `low`, the topic was too tame. Scale defined in
`<repo-root>/skills/crazy-professor/resources/output-template.md`.

**Step 5: Pick ONE as the next experiment.** The one that is most
testable in under one hour with tools the user already has.

**Step 6: Write the output file** using the frontmatter and body
structure defined in
`<repo-root>/skills/crazy-professor/resources/output-template.md`.
Create the directory `.agent-memory/lab/crazy-professor/` (in the target
project, not the plugin repo) if it does not exist.

**Step 7: Append a line to `.agent-memory/lab/crazy-professor/field-notes.md`**
as one Markdown table row that matches the existing table columns.
At minimum, the row must record: timestamp, archetype, provocation word,
PO-operator, topic slug, output file, and the `re-rolled` value from
Step 2b (one of `no`, `archetype`, `word`, `both`).

Default the review columns to `pending`:
`Kept`, `Retire-word`, `Voice-off`, and `Review1-Votum`.

Rationale: this log is the fieldtest memory. The `Re-rolled` column
makes Step 2b observable and is reviewed at Review 1 (triggered when Run
10 completes, earliest; 2026-04-29 is the hard fallback date) to decide
whether the guard thresholds (3 consecutive / last 10) need adjusting.

## Chat-Mode Path (`--chat`)

When the invocation includes `--chat`, the single-run flow above is
replaced by the 3-round chat-mode flow. The canonical specification with
call-budget, error-handling, and degradation paths is
`<repo-root>/docs/chat-mode-flow.md`.

**Step C1: Parse arguments.** Topic is mandatory; `--chat` flags chat
mode. Reject `--chat` without topic per Step 1 contract above. Optional
`--chat --dry-run-round1` runs only round 1 (internal testing, no
round 2/3).

**Step C2: Generate 4 archetype picks.** For each of the 4 archetypes
(jester, librarian, alchemist, radagast), generate an independent
(word, operator) pick using the Step 2/2b logic. Apply word-guard
across the round (no duplicate word within the chat-run itself; if
duplicate, re-roll with marker `re-rolled: intra-chat`).

**Step C3: Round 1.** Spawn 4 parallel LLM calls (one per archetype).
Each call uses:

- The archetype's standard prompt template (unchanged).
- Plus the `chat-round-1-wrapper.md` override block appended to the
  system prompt.
- User message: topic, word, operator.

Each archetype returns 5 provocations. Collect all 20.

**Step C3 abort:** If ≥ 2 of 4 archetypes return empty or
format-broken output, abort chat-mode and fall back to a single-run
(any archetype) with a note in the output file that chat-mode failed
in round 1.

**Step C4: Round 2.** Spawn 4 parallel LLM calls. Each archetype
receives:

- Its standard prompt template.
- Plus the `chat-round-2-wrapper.md` override block.
- User message: topic + the 15 provocations produced by the OTHER three
  archetypes in round 1 (not its own round-1 output).
- Each archetype returns 2-3 provocations with `counter:` or `extend:`
  markers.

**Step C4 degradation:** If ≥ 2 of 4 archetypes return fewer than 2
provocations, set `round2_status: degraded` in the frontmatter and
skip round-2 outputs entirely — round 3 receives only round-1 data.
This is NOT an abort; the chat-run continues to round 3.

**Step C5: Round 3 — Codex distillation.** Invoke `codex:codex-rescue`
subagent (run_in_background=false) with the prompt from
`<repo-root>/skills/crazy-professor/prompt-templates/chat-curator.md`.
Supply all round-1 + round-2 provocations. The Codex return contract is
direct Markdown text only: no scratch file, no prepared input file, no
path-only response.

**Step C5 fallback:** If Codex invocation fails (timeout, error,
rate-limit), run the identical distillation prompt through Claude
(main-model self-call). Mark `distiller: claude (codex-fallback)` in
frontmatter and record `distiller_reason`.

**Step C5 validation:** The Codex/Claude output must have exactly 4
sections × 5 ideas, a Top-3 Cross-Pollination block, and a Next
Experiment block. If the structure is broken or Codex returns only a
file path / prepared-input note: one retry with the specific error hint
and the direct-text return contract repeated. If that also fails, run
Claude-fallback.

**Step C6: Write output file** using
`<repo-root>/skills/crazy-professor/resources/chat-output-template.md`
at path `.agent-memory/lab/crazy-professor/chat/YYYY-MM-DD-HHMM-<topic-slug>.md`
(in the target project, not the plugin repo). Create directory if it
does not exist.

**Step C7: Append field-notes row.** Same `field-notes.md` as
single-runs, but with `mode: chat` marker, `archetype: all-4`, `word:
multi`, `operator: multi`, `re-rolled` as aggregate.

**Step C8: Summary to user.** Main-model writes a brief user-facing
summary: the topic, the 4 archetype picks, round-2 status, the distiller
used, and a pointer to the output file. Do NOT repeat the 20 final
ideas in the chat — the user reads them in the file.
