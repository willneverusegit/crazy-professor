---
title: crazy-professor — Hard Rules
status: v0.13.0 (Phase 4-8 zurückgebaut, Inhalte konsolidiert)
load_when: any invocation, before generation
path_convention: all paths are relative to plugin repo root <repo-root> = crazy-professor/
---

# Hard Rules

These rules override helpfulness-tuning. Persona prompting without
guardrails can degrade factual accuracy by up to 30 percentage points
on knowledge-heavy tasks (Search Engine Journal, 2024). The skill is a
divergence tool, not an advisor.

1. **Output is never advice.** Every provocation is framed as
   hypothesis, provocation, or "what if" — never as recommendation.
2. **The warning banner is always present.** The output template
   (`<repo-root>/skills/crazy-professor/resources/output-template.md`)
   includes the divergence warning verbatim.
3. **The goal of the topic is respected.** Conventions are attacked,
   goals are not.
4. **Anchor or it doesn't count.** Every provocation names at least
   one existing structure in the user's infrastructure. "Adapt this in
   agentic-os iterations.jsonl" beats "adapt this somehow."
5. **Exactly one concrete next experiment.** The final section names
   ONE of the 10 provocations as testable in the next hour and nothing
   more. This is the anti-adoption safety mechanism.
6. **No cross-archetype contamination.** Each archetype has a
   verbotenes Vokabular block in its prompt template. Honor those bans
   as prose rules — there is no automated linter as of v0.13.0.

## Museum Clause (hard gate)

After the **10th invocation**, check field-notes.md. If fewer than 3
invocations produced an output that the user flagged as "kept" (landed
in `wiki/inbox/`, ISSUES2FIX, or .agent-memory/skills-backlog/ within
14 days), the skill is moved to `.agent-memory/museum/crazy-professor/`
with a short post-mortem noting what was learned. The gap in the
pipeline stays visible rather than being papered over with a bad tool.

**Adoption is the risk, not build.** The skill earns its continued
existence through use, not through existence.

## Chat-Mode Museum Clause

Chat-mode has its own 5-run museum gate, independent of the V1 gate:

- After 5 chat-runs: user review.
- Pass: ≥ 3 of 5 chat-runs produced final-20 lists where ≥ 10 ideas
  are `kept` or `conditional` under the rubric.
- Fail: 3+ chat-runs broke structurally (format errors, codex failure,
  5-per-archetype rule violated) OR produced < 10 viable ideas per
  run on average. Chat-mode moves to
  `.agent-memory/museum/crazy-professor-chat/`, single-run remains
  active.

## Field Test Rule (living artifact)

After a provocation word has produced output in **3 invocations** and
in all 3 cases the user flagged the result as "too close to variations
of previous outputs" (in field-notes.md, in a column marked "retire?"),
the word is moved from
`<repo-root>/skills/crazy-professor/resources/provocation-words.txt`
to `<repo-root>/skills/crazy-professor/resources/retired-words.txt`.
This keeps the word pool alive rather than frozen.

The list of archetypes is NOT subject to the same rule; archetype
changes require a version bump.

## Radagast-Activation Status

`radagast-brown` is **ACTIVE** since 2026-04-23. mod-4 is live; all
four archetypes participate at equal 25% probability.

The four binding conditions for Radagast outputs (first-sentence
vocabulary rule, no foreign-field smuggling, optimization-under-care
flagging, anti-folder-sprawl limit) live as the "Activation
Amendments" prose section at the bottom of
`<repo-root>/skills/crazy-professor/prompt-templates/radagast-brown.md`.

## Review Rubric

All reviews use three criteria:

- **Wert (Value)** — Does the provocation open a genuinely new
  working mode, or is it a near-variation of something already present?
- **Umsetzbarkeit (Feasibility)** — Testable in under 1-2 hours, or
  materializable as a small backlog artefact? The Adoption-Cost-Tag
  (`low` / `medium` / `high` / `system-break`) is the first signal,
  but the rubric overrides the tag.
- **Systemfit** — Fits into Agentic-OS / Claude / Codex / Wiki workflow
  without architectural theater?

**Verdict levels:** `kept` (durable value), `conditional` (kept iff a
named artefact materializes within deadline), `backlog` (strong concept
but too heavy for immediate adoption).

**Special rule for labyrinth-librarian:** Do not evaluate the
historical/scientific analogies as facts. Only the transferred
mechanism is rated. An analogy that turns out to be fictional is not a
mark against the provocation if the mechanism translates cleanly.

The old per-output `kept` checkbox in the output template remains for
museum-clause mechanics (14-day artefact-materialization tracking).
The verdict above is run-level.
