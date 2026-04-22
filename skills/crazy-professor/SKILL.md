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
metadata:
  author: domes
  version: '0.3.0'
  part-of: crazy-professor
  layer: divergence
  status: V1 local-only
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

## V1 Behavior (local burst)

**Single invocation pattern:**

```
Skill crazy-professor "<topic>"
```

**Out of scope for V1 (deliberate):**
- No `--deep` debate mode (devil-advocate-swarms integration).
- No `--chat` bridge mode (tmux, telegram, ductor).
- No multi-agent calls.
- No model routing.

These are documented as future extensions below, not built.

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
  random-across-minutes. NOTE: radagast-brown is latent until the
  Radagast-Activation Gate (see below) is passed -- until then, treat
  mod-4 result 3 as a re-roll to mod-3.
- Provocation word: pick one random line from `resources/provocation-words.txt`.
  Filter out any word that also appears in `resources/retired-words.txt`.
- PO-operator: take timestamp second mod 3 (0=reversal, 1=exaggeration,
  2=escape).

**Step 3: Load the archetype's prompt template.** Read the matching
`prompt-templates/*.md` file. Its "System-Prompt-Kern" section is the
authoritative voice rules.

**Step 4: Generate 10 provocations.** Follow the archetype rules strictly.
Each provocation ends with a one-phrase anchor to the user's infrastructure.

**Step 5: Pick ONE as the next experiment.** The one that is most
testable in under one hour with tools the user already has.

**Step 6: Write the output file** using the frontmatter and body
structure defined in `resources/output-template.md`. Create the directory
`.agent-memory/lab/crazy-professor/` if it does not exist.

**Step 7: Append a line to `.agent-memory/lab/crazy-professor/field-notes.md`**
with: timestamp, archetype, provocation word, PO-operator, topic slug, and
output file path. One line per invocation. This is the feldtest-log.

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
until Review 1 (2026-04-29) confirms the three original V1 archetypes
earned at least their minimum keeper-count in the Feldtest. Until then,
the stochastic picker treats timestamp-mod-4 result `3` as a re-roll to
mod-3 (so jester/librarian/alchemist split the probability space).

If Review 1 fails the museum pre-check (< 3 keepers across the first
runs), `radagast-brown.md` stays in the repo as an unused asset but is
not added to the active pool. Rationale: adding breadth to a skill that
has not yet earned depth is the exact adoption-is-the-risk pattern the
museum clause was written to prevent.

On Review 1 success, the re-roll rule is removed from Step 2 and mod-4
becomes live. This is a one-line change in this file and requires a
version-bump commit.

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
- **`--chat` mode.** Opens a tmux session with Claude (one archetype)
  and Codex (another archetype) arguing for 3 rounds, filesystem
  scratch space. Costly (~20 LLM calls per session), only worth
  building if V1 earns museum-clause survival.

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
        |   \-- radagast-brown.md
        \-- resources/
            |-- provocation-words.txt         (100 curated words)
            |-- retired-words.txt             (starts empty)
            |-- po-operators.md
            \-- output-template.md
```

Output target (target project's memory, not plugin):
```
.agent-memory/lab/crazy-professor/
|-- field-notes.md                            (one line per run)
\-- YYYY-MM-DD-HHMM-<topic-slug>.md           (one per invocation)
```
