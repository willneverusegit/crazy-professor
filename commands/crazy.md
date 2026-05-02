---
description: Invoke the crazy-professor divergence generator on a topic. Default: 10 provocations. With --chat: all four voices and 20 distilled ideas. --lab: open the static review browser.
argument-hint: [topic] [--chat] [--lab]
---

# Crazy Professor -- On-Demand

Activate the `crazy-professor` skill and run it against the following arguments:

**Arguments:** $ARGUMENTS

Topic resolution (single source of truth — the SKILL.md operating-instructions reference is the canonical version):

- If `$ARGUMENTS` contains `--lab`, open the static Ideation Lab at `skills/crazy-professor/lab/index.html` via `webbrowser.open()`. Standalone — no topic, no `--chat`.
- If `$ARGUMENTS` contains `--chat` and no topic text outside the flag, **reject explicitly** and stop. Return: `Chat-mode requires an explicit topic. Run /crazy <topic> --chat or use single-run for ambient topics.`
- If `$ARGUMENTS` is empty (no `--chat`, no `--lab`, no topic), run single-run on the most recent concrete task, plan, or problem from the current conversation. If the conversation context is empty, meta, or too vague, ask one clarifying question and stop.
- If `$ARGUMENTS` contains a topic and no `--chat`, dispatch to single-run mode: one active archetype, one provocation word, one PO operator, exactly 10 provocations, and one next experiment.
- If `$ARGUMENTS` contains a topic and `--chat`, dispatch to Chat-Mode: all four active archetypes, 3 rounds, final 20-idea distillation.

Follow the skill's full protocol exactly. All four archetypes are active: first-principles-jester, labyrinth-librarian, systems-alchemist, radagast-brown. No advice, no softening. Strange but anchored.
