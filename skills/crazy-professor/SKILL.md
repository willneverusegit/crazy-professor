---
name: crazy-professor
description: >
  Divergence generator. Produces 10 unhinged provocations for any topic
  using random archetype + random provocation word + random PO operator
  (De Bono's Provocation Operation). Four voices: first-principles-jester,
  labyrinth-librarian, systems-alchemist, radagast-brown (a warm, forest-
  dwelling caretaker archetype that asks what needs shelter rather than
  optimization). Output is never advice, always a deliberately strange
  nudge away from the obvious. Use when feeling stuck, when the first
  idea feels too normal, when a feature needs a weirder starting point,
  when a brainstorm needs a destabilizer, or when a plan feels like it
  converged too fast. Trigger phrases: "crazy professor", "provoke me",
  "break my thinking", "give me weird ideas", "divergence", "shake this
  up", "destabilize", "unstick me", "too normal", "weirder starting
  point", "unhinged thinker", "nudge away from obvious", "radagast",
  "radagast der braune", "cozy provocation", "gentler nudge", "waldhaft".
  Chat-Mode (v0.5.0, `--chat` flag): four archetypes in 3-round
  distilled dialog producing curated 20-idea output (5 per archetype)
  with Codex-based scoring. Trigger phrases for Chat-Mode: "chat mode",
  "chat-mode", "alle archetypen", "alle stimmen", "kuratierte ideen",
  "20 ideen", "destilliere", "crazy professor chat", "crazy chat".
metadata:
  author: domes
  version: '0.5.0'
  part-of: crazy-professor
  layer: divergence
  status: V1 + Chat-Mode
  user_invocable: true
---

# Crazy Professor

Divergence generator for creative ideation. Not an advisor. Not a coach.
A deliberately unhinged thinker whose only job is to produce strange but
anchored provocations that you would not have come to on your own.

## German Trigger Phrases (body-level, not in frontmatter)

The plugin catalog enforces English trigger phrases in YAML frontmatter.
The user works primarily in German. The following German phrases should
also activate this skill when the user writes them in chat:

"verrueckter professor", "professor", "spinn herum", "bring mich raus
aus der spur", "gib mir wilde ideen", "steck mich fest", "ideen
ausbrechen", "wilde provokationen", "das ist zu normal", "brauche was
verdrehtes", "zu gerade gedacht", "stoss mich an".

Claude Code: if the user types any of the above in German, invoke this
skill the same way as for the English triggers.

## V1 Behavior (local burst) — default mode

**Single invocation pattern:**

```
Skill crazy-professor "<topic>"
```

One archetype, 10 provocations, one next-experiment. V1 is the
fastest mode (~30s, 1 LLM call). For the deeper multi-archetype
distillation flow, see Chat-Mode below.

**Out of scope for V1 (deliberate):**
- No `--deep` debate mode (devil-advocate-swarms integration).
- No multi-agent calls in V1 (Chat-Mode handles that — still not
  a tmux/telegram/ductor bridge).
- No model routing.

## Chat-Mode (v0.5.0, new)

**Invocation:**

```
Skill crazy-professor "<topic>" --chat
```

Four archetypes run in a 3-round sequence, producing a curated 20-idea
output (5 per archetype). See `docs/chat-mode-flow.md` for the
authoritative flow specification.

**Cost:** ~10 LLM calls, ~2-4 min wall-clock, one Codex-rescue call
for distillation (with Claude fallback).

**When to use Chat-Mode instead of V1:**
- Topic benefits from multiple lenses (e.g., infrastructure questions
  where systems-alchemist and radagast-brown have opposing takes).
- User wants curated, ranked ideas with rubric scores (Wert/
  Umsetzbarkeit/Systemfit), not 10 raw provocations.
- Willingness to spend 2-4 min and one Codex-call for the distillation.

**When to stick with V1:**
- Quick single-lens divergence ("I just need one unhinged angle").
- Codex unavailable and Claude-fallback-distillation not wanted.
- Topic is narrow enough that one archetype suffices.

Chat-Mode is NOT a replacement for V1. It sits alongside.

**Out of scope for Chat-Mode (deliberate):**
- No tmux live-dialog, no Telegram bridge.
- No model-mix routing (Claude for rounds 1-2, Codex for round 3 is fixed).
- No multi-topic batches (one topic per chat-run).
- No auto-schedule.

These are V2+ candidates, not built.

## What It Does

On each call, the skill:

1. Picks **one of four archetypes** (deterministic from timestamp seed):
   `first-principles-jester`, `labyrinth-librarian`, `systems-alchemist`,
   `radagast-brown`.
2. Picks **one provocation word** from `resources/provocation-words.txt`.
3. Picks **one De Bono PO-operator**: `reversal`, `exaggeration`, or `escape`.
4. Produces **exactly 10 provocations** to the user's topic, anchored in
   the user's existing infrastructure (agentic-os, devil-advocate-swarms,
   notebooklm, skill-system, todos.db, ISSUES2FIX, Codex/Claude CLI,
   Obsidian-Wiki, .agent-memory).
5. Picks **one** of the 10 provocations as the "next small experiment" and
   names it in a separate final section.
6. Writes the output as a Markdown file to
   `.agent-memory/lab/crazy-professor/YYYY-MM-DD-HHMM-<topic-slug>.md`.

## Hard Rules

These rules override helpfulness-tuning. They exist because persona
prompting without guardrails can degrade factual accuracy by up to 30
percentage points on knowledge-heavy tasks (see Search Engine Journal,
2024). The skill is a divergence tool, not an advisor.

1. **Output is never advice.** Every provocation is framed as hypothesis,
   provocation, or "what if" -- never as recommendation.
2. **The warning banner is always present.** The output template
   (`resources/output-template.md`) must include the divergence warning
   verbatim.
3. **The goal of the topic is respected.** Conventions are attacked, goals
   are not.
4. **Anchor or it doesn't count.** Every provocation names at least one
   existing structure in the user's infrastructure. "Adapt this in
   agentic-os iterations.jsonl" beats "adapt this somehow."
5. **Exactly one concrete next experiment.** The final section names ONE
   of the 10 provocations as testable in the next hour and nothing more.
   This is the anti-adoption safety mechanism: every run ends with a
   single experiment, not a menu.
6. **No cross-archetype contamination.** Each archetype has a verbotenes
   Vokabular list (see prompt templates). Violating it kills the
   differentiation between voices and makes the skill pointless.

## Archetypes (V1)

| Archetype | Purpose | Voice |
|---|---|---|
| `first-principles-jester` | Illegalizes conventions. Breaks down a habit into atoms, declares one atom illegal, rebuilds. | Naive, playful, never cynical. |
| `labyrinth-librarian` | Imports mechanisms from distant fields. Opens in mykology/meteorology/ornithology/architecture, translates the mechanism back. | Quiet, learned, never pedantic. |
| `systems-alchemist` | Rewires flows. Maps the topic as input/output/overflow/leak/wall and re-routes one element. | Precise, observational, like a process engineer drawing a flow diagram. |
| `radagast-brown` | Protects the useful-uselessness. Asks what needs care, shelter, slowness -- defends a part of the system against optimization. | Softly distracted but never dumb. Speaks in living creatures and natural time (seasons, weather, dusk). |

See `prompt-templates/first-principles-jester.md`,
`prompt-templates/labyrinth-librarian.md`,
`prompt-templates/systems-alchemist.md`,
`prompt-templates/radagast-brown.md` for the full voice rules and
verbotenes Vokabular of each.

For functional guidance on **which archetype to pick deliberately**
(instead of letting mod-4 decide) and an optional four-phase sequence
(`Jester -> Librarian -> Alchemist -> Radagast`), see
`docs/USAGE-PATTERNS.md`. That document is a user heuristic, not a
skill rule — the skill itself stays a single-shot randomized picker.

## Operating Instructions (Claude follows this on invocation)

**Step 1: Parse the topic.** Strip to a single sentence. If the input is
empty, ambiguous, or meta ("tell me a story", "how does this skill work"),
ask one clarifying question and stop -- do not fabricate a topic.

**Step 2: Pick stochastic elements.**
- Archetype: take current UTC timestamp minute mod 4 (0=jester, 1=librarian,
  2=alchemist, 3=radagast-brown). This is deterministic-within-minute,
  random-across-minutes. All four archetypes active since 2026-04-23
  (Radagast activation passed, see Activation Outcome section below).
- Provocation word: pick one random line from `resources/provocation-words.txt`.
  Filter out any word that also appears in `resources/retired-words.txt`.
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
or `both`. This value goes into the new `re-rolled` column in
field-notes.md.

Rationale: field-notes.md is otherwise write-only. Reading it before the
picker turns the log into backpressure that prevents archetype/word
clustering across sessions. Not total prohibition — just anti-streak.

**Step 3: Load the archetype's prompt template.** Read the matching
`prompt-templates/*.md` file. Its "System-Prompt-Kern" section is the
authoritative voice rules.

**Step 4: Generate 10 provocations.** Follow the archetype rules strictly.
Each provocation carries two trailing metadata items: an Adoption-Cost-Tag
(`low` | `medium` | `high` | `system-break`) and a one-phrase anchor to
the user's infrastructure. Format per line:

`<provocation text> -- [cost: <level>] -- anchor: <link>`

The cost tag is assigned honestly per provocation. No forced distribution.
If all 10 are `system-break`, that is the truth about the run. If all 10
are `low`, the topic was too tame. Scale defined in `resources/output-template.md`.

**Step 5: Pick ONE as the next experiment.** The one that is most
testable in under one hour with tools the user already has.

**Step 6: Write the output file** using the frontmatter and body
structure defined in `resources/output-template.md`. Create the directory
`.agent-memory/lab/crazy-professor/` if it does not exist.

**Step 7: Append a line to `.agent-memory/lab/crazy-professor/field-notes.md`**
with: timestamp, archetype, provocation word, PO-operator, topic slug,
output file path, and the `re-rolled` value from Step 2b (one of `no`,
`archetype`, `word`, `both`). One line per invocation. This is the
feldtest-log. The `re-rolled` column makes Step 2b observable and is
reviewed at Review 1 (triggered when Run 10 completes, earliest; 2026-04-29 is the hard fallback date) to decide whether the guard thresholds
(3 consecutive / last 10) need adjusting.

## Operating Instructions — Chat-Mode (`--chat`)

When the invocation includes `--chat`, the single-run flow above is
replaced by the 3-round chat-mode flow.

**Step C1: Parse arguments.** Topic is mandatory; `--chat` flags chat
mode. Optional `--chat --dry-run-round1` runs only round 1 (internal
testing, no round 2/3).

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
`prompt-templates/chat-curator.md`. Supply all round-1 + round-2
provocations.

**Step C5 fallback:** If Codex invocation fails (timeout, error,
rate-limit), run the identical distillation prompt through Claude
(main-model self-call). Mark `distiller: claude (codex-fallback)` in
frontmatter and record `distiller_reason`.

**Step C5 validation:** The Codex/Claude output must have exactly 4
sections × 5 ideas, a Top-3 Cross-Pollination block, and a Next
Experiment block. If the structure is broken: one retry with specific
error hint; if that also fails, run Claude-fallback.

**Step C6: Write output file** using `resources/chat-output-template.md`
at path `.agent-memory/lab/crazy-professor/chat/YYYY-MM-DD-HHMM-<topic-slug>.md`.
Create directory if it does not exist.

**Step C7: Append field-notes row.** Same `field-notes.md` as
single-runs, but with `mode: chat` marker, `archetype: all-4`, `word:
multi`, `operator: multi`, `re-rolled` as aggregate.

**Step C8: Summary to user.** Main-model writes a brief user-facing
summary: the topic, the 4 archetype picks, round-2 status, the distiller
used, and a pointer to the output file. Do NOT repeat the 20 final
ideas in the chat — the user reads them in the file.

## Chat-Mode Museum Clause

Chat-mode has its own 5-run museum gate, independent of the V1 gate:

- After 5 chat-runs: user + codex-juror review.
- Pass: ≥ 3 of 5 chat-runs produced final-20 lists where ≥ 10 ideas
  are `kept` or `conditional` under the rubric.
- Fail: 3+ chat-runs broke structurally (format errors, codex failure,
  5-per-archetype rule violated) OR produced < 10 viable ideas per
  run on average. Chat-mode moves to `.agent-memory/museum/crazy-
  professor-chat/`, single-run remains active.

## Field Test Rule (living artifact)

After a provocation word has produced output in **3 invocations** and
in all 3 cases the user flagged the result as "too close to variations
of previous outputs" (in field-notes.md, in a column marked "retire?"),
the word is moved from `resources/provocation-words.txt` to
`resources/retired-words.txt`. This keeps the word pool alive rather
than frozen.

The list of archetypes is NOT subject to the same rule; archetype changes
require a version bump.

## Museum Clause (hard gate)

After the **10th invocation**, check field-notes.md. If fewer than 3
invocations produced an output that the user flagged as "kept" (landed in
`wiki/inbox/`, ISSUES2FIX, or .agent-memory/skills-backlog/ within 14
days), the skill is moved to `.agent-memory/museum/crazy-professor/` with
a short post-mortem noting what was learned. No `--deep`, `--chat`, or
telegram extensions are built at that point. The gap in the pipeline
stays visible rather than being papered over with a bad tool.

This is the Codex-review addition: **adoption is the risk, not build.**
The skill earns its continued existence through use, not through existence.

## Radagast-Activation Gate

`radagast-brown` is built and present in the repo, but stays **latent**
until Review 1 (triggered when Run 10 completes, earliest; 2026-04-29 is the hard fallback date) confirms the three original V1 archetypes
earned at least their minimum keeper-count in the Feldtest. Until then,
the stochastic picker treats timestamp-mod-4 result `3` as a re-roll to
mod-3 (so jester/librarian/alchemist split the probability space).

If Review 1 fails the museum pre-check (< 3 keepers across the first
runs), `radagast-brown.md` stays in the repo as an unused asset but is
not added to the active pool. Rationale: adding breadth to a skill that
has not yet earned depth is the exact adoption-is-the-risk pattern the
museum clause was written to prevent.

**Activation sub-gate (added 2026-04-23):** Review 1 success is
necessary but not sufficient. Before the re-roll rule is removed, a
forced Radagast blindtest runs over three recent topics (typically the
last three single-runs before Review 1). The three Radagast outputs are
scored against the same Wert/Umsetzbarkeit/Systemfit rubric as Review 1.
Pass condition: at least 2 of 3 forced Radagast runs score as `kept` or
`conditional` under the rubric. Fail condition: Radagast stays latent,
`radagast-brown.md` prompt template gets a revision pass before the next
activation attempt.

### Activation Outcome (2026-04-23)

**Radagast is ACTIVE.** mod-4 is live; the re-roll-to-mod-3 rule is
removed from Step 2.

Sub-gate passed under three independent votes (user, Codex Juror 1,
Codex Juror 2) with Runs 11/12/13 scoring kept/conditional each, no
grove voice-off.

Activation carries four binding conditions that the prompt template and
review process must honor:

1. **First-sentence vocabulary rule strictly enforced.** The first
   sentence of every provocation MUST contain >=2 items from the
   Pflicht-Vokabular list in `radagast-brown.md`. Grace in the second
   sentence no longer counts. Reviewers flag violations in field-notes.
2. **No foreign-field smuggling.** Half-quotes like "Seefahrer haben
   ihn an den Horizont verbannt" or "Imker beobachten..." are forbidden,
   even without an explicit "In der X-Lehre" preface. That phrasing
   belongs to labyrinth-librarian.
3. **Optimization-under-care-disguise gets flagged.** Provocations whose
   anchor is a new schema field, a new hook, a new time-window, or a
   new frontmatter key count as voice-drift-light even if the text
   sounds like care. The rubric reviewer marks these with a yellow dot.
4. **Anti-folder-sprawl meta-rule.** Per single run, Radagast may
   propose AT MOST ONE new folder convention. If the run's 10
   provocations together name multiple new folders (`scrapyard/`,
   `longhouse/`, `unsortiert/`, `empty-nests/`, etc.), reviewer
   collapses them to the strongest one in the Top-3.

### Repetition Watch (added 2026-04-23)

Radagast's imagery pool (Unterholz, Daemmerung, Nest, Winterruhe, Fell,
Kreatur, Rhythmus, Gast, atmen, pflegen, Wetter) is small and prone to
formulaic repetition across runs. After **5 live Radagast runs**
(counting from Run 14 forward, not the blindtest), a lexical-repetition
review is triggered. Checkpoint criterion: do the 5 runs together show
>=20 distinct lead images, or are the same 5-7 recycling?

If lexical concentration is too high: prompt template gets a
diversification pass (expanded Pflicht-Vokabular list, explicit
rotation rule, or bans on the top-3 most-used images for the next
batch).

### Draw-Frequency Note

Radagast occupies 1 of 4 archetype slots with equal stochastic
probability (25% per draw). The activation review explicitly notes that
Radagast is not a stronger archetype than the other three — he opens a
different axis (protection/rhythm/non-harvest) that the others cannot.
Over-drawing Radagast would soften the skill. The natural 25% cap is
considered adequate; no special suppression rule needed at this time.
Re-evaluated at Review 2 (Run 20 or 2026-05-21).

## Review Rubric (added 2026-04-23, post-Review-1)

All future reviews use these three criteria per provocation and per run:

1. **Wert (Value)** — Does the provocation open a genuinely new working
   mode, or is it a near-variation of something already present?
2. **Umsetzbarkeit (Feasibility)** — Testable in under 1-2 hours, or
   materializable as a small backlog artefact? The Adoption-Cost-Tag
   (`low` / `medium` / `high` / `system-break`) is the first signal
   here, but the rubric overrides the tag.
3. **Systemfit** — Fits into Agentic-OS / Claude / Codex / Wiki workflow
   without requiring architectural theater?

**Special rule for labyrinth-librarian runs:** Do not evaluate the
historical/scientific analogies as facts. Only the transferred
mechanism is rated. An analogy that turns out to be fictional is not a
mark against the provocation if the mechanism translates cleanly.

**Verdict levels per run** (new semantics, replaces old binary kept/not-kept):

- `kept` — Run produced durable value, keeper independent of artefact tracking.
- `conditional` — Run becomes `kept` when a named artefact materializes
  within its deadline. The Review block lists the exact artefact and
  deadline per conditional run.
- `backlog` — Run contains strong concepts but is too heavy for
  immediate adoption. Moved to design backlog, not discarded.

The old per-output `kept` checkbox remains for museum-clause mechanics
(it tracks whether the output materialized into wiki/inbox, ISSUES2FIX,
or skills-backlog within 14 days). The new run-level verdict is
additional, not a replacement.

## Future Behavior (deliberately out of scope for V1)

The following are documented to preserve design intent and prevent
ad-hoc reimplementation. None of them are built in V1.

### V1.1 Candidates

- **stage-magician** archetype. Purpose: sensory/dramaturgic
  provocations using stage, prop, reveal, audience, timing. Originally
  tagged as the V1.1 sensory slot. **Parked in v0.3.0** because
  `radagast-brown` took the adjacent slot (biosphere/care axis)
  first; dramaturgic/sensory stays open for V1.2 if Radagast proves
  itself but a further distinct voice is still missing.

### V2 Extensions

- **`--deep` mode.** Calls `devil-advocate-swarms:swarm-orchestrator`
  on the V1 quick output to pressure-test the 10 provocations and
  cluster them into 3 fleshed-out outliers.
- ~~`--chat` mode~~ — shipped as v0.5.0, 2026-04-23. See Chat-Mode
  section above. The originally envisioned tmux/costly-debate version
  was NOT built; instead the flow is synchronous (rounds 1-2 parallel
  calls, round 3 Codex distillation), ~10 LLM calls total.

### V3 Bridge

- **Telegram bridge.** ductor (github.com/PleasePrompto/ductor) or
  Anthropic's official external_plugins/telegram. Decision deferred
  to 2 weeks of V1 usage. Security gate: full security-audit and
  codex:rescue security-review pass required before any Telegram
  adoption.

## File Layout

```
crazy-professor/                              (repo root = plugin root)
|-- .claude-plugin/
|   |-- marketplace.json
|   \-- plugin.json
|-- commands/
|   \-- crazy.md                              (/crazy slash command)
\-- skills/
    \-- crazy-professor/
        |-- SKILL.md                          (this file)
        |-- prompt-templates/
        |   |-- first-principles-jester.md
        |   |-- labyrinth-librarian.md
        |   |-- systems-alchemist.md
        |   |-- radagast-brown.md
        |   |-- chat-round-1-wrapper.md       (v0.5.0 Chat-Mode)
        |   |-- chat-round-2-wrapper.md       (v0.5.0 Chat-Mode)
        |   \-- chat-curator.md               (v0.5.0 Codex distillation prompt)
        \-- resources/
            |-- provocation-words.txt         (100 curated words)
            |-- retired-words.txt             (starts empty)
            |-- po-operators.md
            |-- output-template.md            (single-run format)
            \-- chat-output-template.md       (v0.5.0 Chat-Mode format)
```

Output target (target project's memory, not plugin):
```
.agent-memory/lab/crazy-professor/
|-- field-notes.md                            (one line per run, single+chat mixed)
|-- YYYY-MM-DD-HHMM-<topic-slug>.md           (single-run output)
\-- chat/
    \-- YYYY-MM-DD-HHMM-<topic-slug>.md       (chat-mode output, v0.5.0)
```
