# crazy-professor

A Claude Code plugin that delivers a divergence generator for creative ideation.

Four active voices -- **first-principles-jester**, **labyrinth-librarian**, **systems-alchemist**, and **radagast-brown** -- produce strange but anchored provocations. Never advice. Each default run combines an archetype, a provocation word, and a PO operator (De Bono's Provocation Operation) to deliberately nudge your thinking away from the obvious.

Default mode returns 10 provocations from one voice. `--chat` mode runs all four voices through a 3-round flow and distills a final 20-idea list.

## Use when

- You feel stuck on a problem
- The first idea feels too normal
- A brainstorm needs a destabilizer
- A plan converged too fast
- A feature needs a weirder starting point

## Install

```bash
claude plugin marketplace add willneverusegit/crazy-professor
claude plugin install crazy-professor --scope user
```

## Update

```bash
claude plugin update crazy-professor
```

Marketplace installs are cached under Claude Code's plugin cache. Source-repo changes become visible after commit, push, version bump, and plugin update.

## Trigger

### Slash command

```text
/crazy <topic>
/crazy <topic> --chat
```

Runs the divergence generator on `<topic>`. If no topic is given, it uses whatever the conversation was just about. Add `--chat` when the topic needs all four voices and a curated 20-idea output.

### Trigger phrases

- "crazy professor"
- "provoke me"
- "break my thinking"
- "give me weird ideas"
- "shake this up"
- "too normal"

## Status

Local-only. Default single-run and Chat-Mode are active. Telegram bridge explicitly out of scope.
