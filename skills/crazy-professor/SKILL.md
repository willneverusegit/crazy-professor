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
  Chat-Mode (`--chat` flag, since v0.5.0): four archetypes in 3-round
  distilled dialog producing curated 20-idea output (5 per archetype)
  with Codex-based scoring. Trigger phrases for Chat-Mode: "chat mode",
  "chat-mode", "alle archetypen", "alle stimmen", "kuratierte ideen",
  "20 ideen", "destilliere", "crazy professor chat", "crazy chat".
metadata:
  author: domes
  version: '0.7.0'
  part-of: crazy-professor
  layer: divergence
  status: V1 + Chat-Mode
  user_invocable: true
---

# Crazy Professor

Divergence generator for creative ideation. Not an advisor. Not a coach.
A deliberately unhinged thinker whose only job is to produce strange but
anchored provocations the user would not have reached on their own.

## German Trigger Phrases (body-level, not in frontmatter)

The plugin catalog enforces English trigger phrases in YAML frontmatter.
The user works primarily in German. The following German phrases should
also activate this skill when the user writes them in chat:

"verrueckter professor", "professor", "spinn herum", "bring mich raus
aus der spur", "gib mir wilde ideen", "steck mich fest", "ideen
ausbrechen", "wilde provokationen", "das ist zu normal", "brauche was
verdrehtes", "zu gerade gedacht", "stoss mich an".

For German trigger phrases, invoke this skill the same way as for the
English triggers.

## Modes

**Single-Run (default, V1):**

```
Skill crazy-professor "<topic>"
```

One archetype, 10 provocations, one next-experiment. ~30s, 1 LLM call.
The fastest mode.

**Chat-Mode (`--chat`):**

```
Skill crazy-professor "<topic>" --chat
```

Four archetypes in a 3-round sequence, producing a curated 20-idea
output (5 per archetype). ~10 LLM calls, ~2-4 min wall-clock, one
Codex-rescue call for distillation (with Claude fallback). Cost the
deliberateness — see `<repo-root>/docs/chat-mode-flow.md` for the
canonical flow spec.

When to use which:

- **Single-Run** for ambient topics, quick single-lens divergence, when
  Codex is unavailable, or when the topic is narrow enough.
- **Chat-Mode** for topics that benefit from multiple lenses, when the
  user wants ranked ideas with rubric scores, and the user is willing
  to spend the calls.

Chat-Mode is NOT a replacement for Single-Run. It sits alongside.

## What It Does (Single-Run, summary)

On each call, the skill:

1. Picks **one of four archetypes** deterministically from a timestamp
   seed: `first-principles-jester`, `labyrinth-librarian`,
   `systems-alchemist`, `radagast-brown`.
2. Picks **one provocation word** from
   `<repo-root>/skills/crazy-professor/resources/provocation-words.txt`
   (single words and 2-3-token phrases both valid).
3. Picks **one De Bono PO-operator**: `reversal`, `exaggeration`, or `escape`.
4. Produces **exactly 10 provocations** to the user's topic, anchored in
   the user's existing infrastructure (agentic-os, devil-advocate-swarms,
   notebooklm, skill-system, todos.db, ISSUES2FIX, Codex/Claude CLI,
   Obsidian-Wiki, .agent-memory).
5. Picks **one** of the 10 provocations as the "next small experiment"
   and names it in a separate final section.
6. Writes the output as a Markdown file to
   `.agent-memory/lab/crazy-professor/YYYY-MM-DD-HHMM-<topic-slug>.md`.
7. Appends a row to `field-notes.md` with picker values and review
   placeholders.

Since v0.7.0, two helper scripts live at
`<repo-root>/skills/crazy-professor/scripts/`:

- `picker.py` — deterministic stochastic-element selection with built-in
  variation-guard. Replaces the prose mod-4 mechanic with a callable
  command. Output is JSON on stdout. Used as the preferred path in
  Step 2/2b.
- `validate_output.py` — format-drift detector for both single and
  chat-mode outputs. Used as a pre-write check in Step 6.

Both scripts are stdlib-only Python and optional. If Python is not
available the prose mechanic still works.

The full step-by-step including Variation-Guard logic, Chat-Mode steps
C1-C8, and the topic-resolution contract lives in
`<repo-root>/skills/crazy-professor/references/operating-instructions.md`.
Load that file before generating any output.

## Hard Rules (load on every invocation)

The full Hard Rules block (output-is-never-advice, warning-banner,
goal-respect, anchor-or-it-doesnt-count, exactly-one-experiment,
no-cross-archetype-contamination), plus Museum-Clause, Chat-Mode
Museum-Clause, Field-Test-Rule, Radagast-Activation-Gate, and Review
Rubric, lives in
`<repo-root>/skills/crazy-professor/references/hard-rules.md`. Load
that file before generating any output.

## Archetypes (V1)

| Archetype | Purpose | Voice |
|---|---|---|
| `first-principles-jester` | Illegalizes conventions. Breaks down a habit into atoms, declares one atom illegal, rebuilds. | Naive, playful, never cynical. |
| `labyrinth-librarian` | Imports mechanisms from distant fields. Opens in mykology/meteorology/ornithology/architecture, translates the mechanism back. | Quiet, learned, never pedantic. |
| `systems-alchemist` | Rewires flows. Maps the topic as input/output/overflow/leak/wall and re-routes one element. | Precise, observational, like a process engineer drawing a flow diagram. |
| `radagast-brown` | Protects the useful-uselessness. Asks what needs care, shelter, slowness -- defends a part of the system against optimization. | Softly distracted but never dumb. Speaks in living creatures and natural time (seasons, weather, dusk). |

See `<repo-root>/skills/crazy-professor/prompt-templates/first-principles-jester.md`,
`<repo-root>/skills/crazy-professor/prompt-templates/labyrinth-librarian.md`,
`<repo-root>/skills/crazy-professor/prompt-templates/systems-alchemist.md`,
`<repo-root>/skills/crazy-professor/prompt-templates/radagast-brown.md`
for the full voice rules and verbotenes Vokabular of each.

For functional guidance on **which archetype to pick deliberately**
(instead of letting mod-4 decide) and an optional four-phase sequence
(`Jester -> Librarian -> Alchemist -> Radagast`), see
`<repo-root>/skills/crazy-professor/references/usage-patterns.md`.
That document is a user heuristic, not a skill rule — the skill itself
stays a single-shot randomized picker.

## Out-of-Scope (deliberate)

- **V1**: no `--deep` debate mode, no multi-agent calls, no model routing.
- **Chat-Mode**: no tmux live-dialog, no Telegram bridge, no model-mix
  routing (Claude rounds 1-2 + Codex round 3 is fixed), no multi-topic
  batches, no auto-schedule.

Design intent for deferred features (stage-magician V1.1, `--deep` V2,
Telegram bridge V3) is preserved in
`<repo-root>/skills/crazy-professor/references/roadmap.md`. None of
these are built. The Erweiterungs-Master-Plan in
`<repo-root>/docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md`
schedules Picker-Skript, Linter-Trio, Eval-Suite, Telemetrie,
Run-Planner, and optional GUI/Telegram as Phases 2-8.

## Path Convention

All file paths in this SKILL.md and in the load-on-demand references
(`<repo-root>/skills/crazy-professor/references/operating-instructions.md`
and `<repo-root>/skills/crazy-professor/references/hard-rules.md`) are
written relative to the **plugin repo root** (`<repo-root>` =
`crazy-professor/`). This makes them resolvable regardless of which
file the reader is currently in.

## File Layout

```
crazy-professor/                              (repo root = plugin root)
|-- .claude-plugin/
|   |-- marketplace.json
|   \-- plugin.json
|-- commands/
|   \-- crazy.md                              (/crazy slash command)
|-- docs/
|   |-- PROJECT.md, CAPABILITIES.md, ARCHITECTURE.md, CHANGELOG.md
|   |-- chat-mode-flow.md                     (canonical flow spec)
|   \-- plans/                                (master plans)
\-- skills/
    \-- crazy-professor/
        |-- SKILL.md                          (this file, ~150 lines)
        |-- prompt-templates/
        |   |-- first-principles-jester.md
        |   |-- labyrinth-librarian.md
        |   |-- systems-alchemist.md
        |   |-- radagast-brown.md
        |   |-- chat-round-1-wrapper.md
        |   |-- chat-round-2-wrapper.md
        |   \-- chat-curator.md
        |-- references/                       (load-on-demand detail docs)
        |   |-- operating-instructions.md     (Steps 1-7 + C1-C8)
        |   |-- hard-rules.md                 (Hard Rules + Museum + Field-Test)
        |   |-- radagast-activation.md
        |   |-- review-rubric.md
        |   |-- roadmap.md
        |   |-- chat-mode-flow.md             (stub → docs/chat-mode-flow.md)
        |   \-- usage-patterns.md
        \-- resources/
            |-- provocation-words.txt
            |-- retired-words.txt
            |-- po-operators.md
            |-- output-template.md
            \-- chat-output-template.md
```

## Output Target

Single + Chat outputs land in the **target project's** `.agent-memory/`
(not the plugin repo):

```
.agent-memory/lab/crazy-professor/
|-- field-notes.md                            (one line per run, single+chat mixed)
|-- YYYY-MM-DD-HHMM-<topic-slug>.md           (single-run output)
\-- chat/
    \-- YYYY-MM-DD-HHMM-<topic-slug>.md       (chat-mode output)
```
