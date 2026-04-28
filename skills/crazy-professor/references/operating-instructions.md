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
  on stdout (see Step 2d below). No file is written, no field-notes
  append, no telemetry append. Aborts before generation. Chat-mode
  retains its own `--chat --dry-run-round1` flag (different mechanism,
  unaffected). Combining `--chat --dry-run` is rejected at the command
  layer (commands/crazy.md).
- **Single-run with `--playground` (since v0.12.0, single-run only and standalone):** instead of parsing a topic and generating provocations, run `python <repo-root>/skills/crazy-professor/scripts/build_playground.py` with the active resource files (`provocation-words.txt`, `retired-words.txt`, `po-operators.md`) and the field-notes path (local `.agent-memory/lab/crazy-professor/field-notes.md` first, Desktop-fallback `~/Desktop/.agent-memory/lab/crazy-professor/field-notes.md` if local missing). Pass `--version` from `.claude-plugin/plugin.json`. The script writes/refreshes `<repo-root>/skills/crazy-professor/playground/index.html`. Then open the HTML file via the OS's default browser handler (Python `webbrowser.open()`, fallback: print `Open this file manually: file://<absolute-path>`). No topic argument is parsed — the playground accepts the topic via its input field. The reject-matrix is: `--playground` rejects in combination with `--chat`, `--from-session`, `--dry-run`, `--compact`, or `--strict-cross-pollination`. Reject message: `--playground is single-run only and standalone (no --chat/--from-session/--dry-run/--compact/--strict-cross-pollination combinations).`

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

**Step 5b: Voice lint (since v0.8.0).** Before format validation, run
the per-archetype voice linter on the draft. It enforces the Lexicon-
Gate block at the bottom of `prompt-templates/<archetype>.md`:

```bash
python <repo-root>/skills/crazy-professor/scripts/lint_voice.py \
  --templates-dir <repo-root>/skills/crazy-professor/prompt-templates \
  --mode single <output-file>
```

The linter has two severity levels:

- **warn**: a provocation has fewer than the required minimum of
  archetype vocabulary (Pflicht-Vokabel-Miss). Default behavior is to
  log the warning and continue -- legitimate provocations sometimes
  rephrase outside the standard lexicon.
- **error**: a provocation contains a forbidden cross-archetype token
  (e.g. "Reaktor" in a Radagast output, "Unterholz" in an Alchemist
  output). Errors indicate genuine voice drift and SHOULD trigger a
  rewrite of the offending provocation before Step 6.

For chat-mode use `--mode chat`; the linter checks each Round 3
sub-section against its archetype's lexicon. Pass `--strict` if you
want warns to block too (used by the eval suite when generating a
strict-mode baseline).

**Step 6: Write the output file** using the frontmatter and body
structure defined in
`<repo-root>/skills/crazy-professor/resources/output-template.md`.
Create the directory `.agent-memory/lab/crazy-professor/` (in the target
project, not the plugin repo) if it does not exist.

**Pre-write check (since v0.7.0):** before persisting, run the validator
on the in-memory text. If it exits non-zero, fix the format drift and
retry. Do NOT write a drifted output to disk.

```bash
python <repo-root>/skills/crazy-professor/scripts/validate_output.py \
  --mode single <output-file>
```

For chat-mode use `--mode chat`. Validator checks: frontmatter
completeness, divergence-warning banner, exact 10-provocation count
with the canonical line shape (`<text> -- [cost: <level>] -- anchor:
<text>`, supporting `--`, `—`, or `–`), Next-Experiment section, and
Self-Flag checkboxes. For chat: all three rounds present, exactly 5
items per archetype in Round 3, exactly 3 Top-3 items, Next-Experiment
section.

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

**Step 7b: Append telemetry record (since v0.9.0).** After Step 7,
append one JSONL record to the run-telemetry log via the helper:

```bash
python <repo-root>/skills/crazy-professor/scripts/telemetry.py log --json '{
  "run_id": "<utc-iso>--<archetype>--<topic-slug>",
  "timestamp": "<utc-iso>",
  "mode": "single",
  "topic_slug": "<topic-slug>",
  "archetype": "<picked-archetype>",
  "word": "<picked-word>",
  "operator": "<picked-operator>",
  "re_rolled": "<from-step-2b>",
  "distiller_used": false,
  "round2_status": "n/a",
  "time_to_finish_ms": <wall-clock-ms-from-step-2-to-step-7>,
  "voice_cross_drift_hits": <count-from-lint-voice-step-5b>,
  "lint_pass": <true-if-validate-output-ok>
}'
```

Default path: `~/Desktop/.agent-memory/lab/crazy-professor/telemetry.jsonl`
(override with `--path`). Schema and helper are stdlib-only Python.
Telemetry is the substrate for Museum-Clause / Variation-Guard /
Repetition-Watch evaluation. Skip silently if Python is unavailable;
the field-notes row from Step 7 remains the authoritative log.

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

**Phase 7 (since v0.12.0):** No new telemetry fields. Browser-triggered
runs from `/crazy --playground` produce a normal terminal `/crazy <topic>
--force-archetype X --force-word Y --force-operator Z` invocation;
telemetry sees them as standard single-runs with `forced-` markers in
the `re_rolled` field. Distinguishing browser-vs-direct-CLI is
intentionally out of scope (Phase-9 candidate if data analysis later
needs the distinction).

**Step 7c: Optional patch-suggestion-loop (since v0.9.0).** If the
single-mode run count is a non-zero multiple of 10 (count rows in
field-notes.md Log table where `archetype != all-4 (chat-mode)`), call:

```bash
python <repo-root>/skills/crazy-professor/scripts/patch_suggester.py \
  --field-notes <target-project>/.agent-memory/lab/crazy-professor/field-notes.md
```

The script writes a non-automatic suggestion file to
`<target-project>/.agent-memory/lab/crazy-professor/patches/YYYY-MM-DD-suggestion-N.md`
listing proven words, retire candidates, and voice-drift hot spots.
The suggestion is NEVER applied automatically. Mention the file in the
user-facing summary so the user can review it.

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

**Step C7b: Append telemetry record (since v0.9.0).** Like Step 7b, but
with `mode: "chat"` and the four picks as a list:

```bash
python <repo-root>/skills/crazy-professor/scripts/telemetry.py log --json '{
  "run_id": "<utc-iso>--chat--<topic-slug>",
  "timestamp": "<utc-iso>",
  "mode": "chat",
  "topic_slug": "<topic-slug>",
  "picks": [
    {"archetype": "first-principles-jester", "word": "...", "operator": "...", "re_rolled": "..."},
    {"archetype": "labyrinth-librarian",     "word": "...", "operator": "...", "re_rolled": "..."},
    {"archetype": "systems-alchemist",       "word": "...", "operator": "...", "re_rolled": "..."},
    {"archetype": "radagast-brown",          "word": "...", "operator": "...", "re_rolled": "..."}
  ],
  "distiller_used": <true-if-codex-or-claude-distiller-ran>,
  "round2_status": "<n/a|ok|skipped|failed>",
  "time_to_finish_ms": <wall-clock-ms>,
  "voice_cross_drift_hits": <sum-across-archetypes>,
  "lint_pass": <true-if-validator-passed>
}'
```

`round2_status` mapping: `ok` if all four archetypes returned >= 2
provocations, `skipped` if Step C4 set `round2_status: degraded`,
`failed` if Step C3 abort fired.

**Step C8: Summary to user.** Main-model writes a brief user-facing
summary: the topic, the 4 archetype picks, round-2 status, the distiller
used, and a pointer to the output file. Do NOT repeat the 20 final
ideas in the chat — the user reads them in the file.
