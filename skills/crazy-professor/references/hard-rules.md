---
title: crazy-professor — Hard Rules
status: extracted from SKILL.md 2026-04-27 (Phase 1, point 1.6)
load_when: any invocation, before generation
---

# Hard Rules

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

## Chat-Mode Museum Clause

Chat-mode has its own 5-run museum gate, independent of the V1 gate:

- After 5 chat-runs: user + codex-juror review.
- Pass: ≥ 3 of 5 chat-runs produced final-20 lists where ≥ 10 ideas
  are `kept` or `conditional` under the rubric.
- Fail: 3+ chat-runs broke structurally (format errors, codex failure,
  5-per-archetype rule violated) OR produced < 10 viable ideas per
  run on average. Chat-mode moves to `.agent-memory/museum/crazy-professor-chat/`,
  single-run remains active.

## Field Test Rule (living artifact)

After a provocation word has produced output in **3 invocations** and
in all 3 cases the user flagged the result as "too close to variations
of previous outputs" (in field-notes.md, in a column marked "retire?"),
the word is moved from `resources/provocation-words.txt` to
`resources/retired-words.txt`. This keeps the word pool alive rather
than frozen.

The list of archetypes is NOT subject to the same rule; archetype changes
require a version bump.

## Radagast-Activation Gate

`radagast-brown` is **ACTIVE** since 2026-04-23. mod-4 is live; all four
archetypes participate at equal 25% probability.

Four binding conditions remain in force for Radagast outputs
(first-sentence vocabulary rule, no foreign-field smuggling,
optimization-under-care flagging, anti-folder-sprawl limit). A lexical
repetition review triggers after 5 live Radagast runs.

For the full activation history, binding conditions, repetition watch
criteria, and draw-frequency rationale, see
`references/radagast-activation.md`.

## Review Rubric

All reviews use three criteria: **Wert** (genuinely new working mode?),
**Umsetzbarkeit** (testable in 1-2 hours?), **Systemfit** (fits
Agentic-OS/Claude/Codex/Wiki without architectural theater?).

Verdicts per run: `kept`, `conditional`, or `backlog`. The old
per-output `kept` checkbox remains for museum-clause mechanics
(14-day artefact-materialization tracking).

For the full rubric, the labyrinth-librarian special rule, and verdict
semantics, see `references/review-rubric.md`.
