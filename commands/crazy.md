---
description: Invoke the crazy-professor divergence generator on a topic. Default: 10 provocations. With --chat: all four voices and 20 distilled ideas.
argument-hint: [topic] [--chat] [--from-session] [--dry-run]
---

# Crazy Professor -- On-Demand

Activate the `crazy-professor` skill and run it against the following arguments:

**Arguments:** $ARGUMENTS

Topic resolution (uniform contract — see SKILL.md "Operating Instructions" Step 1):

- If `$ARGUMENTS` contains `--chat` and no topic text outside the flag, **reject explicitly** and stop. Return:
  `Chat-mode requires an explicit topic. Run /crazy <topic> --chat or use single-run for ambient topics.`
- If `$ARGUMENTS` is empty (no `--chat`, no topic), run single-run on the most recent concrete task, plan, or problem from the current conversation. If the conversation context is empty, meta, or too vague, ask one clarifying question and stop -- do not fabricate a topic.
- If `$ARGUMENTS` contains a topic and no `--chat`, dispatch to single-run mode: one active archetype, one provocation word, one PO operator, exactly 10 provocations, and one next experiment.
- If `$ARGUMENTS` contains a topic and `--chat`, dispatch to Chat-Mode: all four active archetypes, 3 rounds, final 20-idea distillation, and chat output template.
- If `$ARGUMENTS` contains `--from-session` (since v0.10.0), call run-planner's `session` subcommand to extract 3 topic candidates from the local + Desktop session-summary files. Show them to the user as a numbered list and ask which one (or "own"). On a chosen number, dispatch to single-run mode with that bullet as the topic. On "own" or empty, fall back to the standard single-run-without-topic rule. If `--dry-run` is also set, the chosen topic still goes through the dry-run path below.
- If `$ARGUMENTS` contains `--dry-run` (since v0.10.0, single-run only), parse the topic per the rules above, run the picker, and print the dry-run preview block as defined in operating-instructions Step 2d. Do NOT generate provocations, do NOT write any file, do NOT append to field-notes or telemetry. Combining `--dry-run` with `--chat` is rejected: print `--dry-run is single-run only. Use --chat --dry-run-round1 for chat-mode preview.` and stop.

Follow the skill's full protocol exactly.

All four archetypes are active: first-principles-jester, labyrinth-librarian, systems-alchemist, and radagast-brown. No advice, no softening. Strange but anchored.
