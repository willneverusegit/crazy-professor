---
description: Invoke the crazy-professor divergence generator on a topic. Default: 10 provocations. With --chat: all four voices and 20 distilled ideas.
argument-hint: [topic] [--chat]
---

# Crazy Professor -- On-Demand

Activate the `crazy-professor` skill and run it against the following arguments:

**Arguments:** $ARGUMENTS

If `$ARGUMENTS` is empty, run the skill on whatever the user was just working on in the current conversation. Use the most recent task, plan, or problem as the topic.

Follow the skill's full protocol exactly.

- If `$ARGUMENTS` contains `--chat`, dispatch to Chat-Mode: all four active archetypes, 3 rounds, final 20-idea distillation, and chat output template.
- Otherwise dispatch to default single-run mode: one active archetype, one provocation word, one PO operator, exactly 10 provocations, and one next experiment.

All four archetypes are active: first-principles-jester, labyrinth-librarian, systems-alchemist, and radagast-brown. No advice, no softening. Strange but anchored.
