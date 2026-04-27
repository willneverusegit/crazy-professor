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

Runs the divergence generator on `<topic>`. Add `--chat` when the topic needs all four voices and a curated 20-idea output.

**Topic resolution:**

- **Single-run with topic** — runs normally.
- **Single-run without topic** — uses the most recent concrete task, plan, or problem from the current conversation as topic. If the conversation context is empty, meta, or too vague (e.g. "tell me a story", "how does this skill work"), the skill asks one clarifying question and stops instead of fabricating a topic.
- **Chat-mode with topic** — runs normally.
- **Chat-mode without topic** — explicitly rejected. Chat-mode costs ~10 LLM calls and 2-4 min wall-clock; the user must name the topic deliberately. The skill returns: `Chat-mode requires an explicit topic. Run /crazy <topic> --chat or use single-run for ambient topics.`

### Trigger phrases

- "crazy professor"
- "provoke me"
- "break my thinking"
- "give me weird ideas"
- "shake this up"
- "too normal"

## Status

Local-only. Default single-run and Chat-Mode are active. Telegram bridge explicitly out of scope.
