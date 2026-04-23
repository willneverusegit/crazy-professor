# Roadmap & Out-of-Scope Design Intent

This file preserves design intent for deliberately-deferred features.
None of the items below are built. They are documented to prevent
ad-hoc reimplementation and to anchor decisions when a feature is
eventually reconsidered.

## V1.1 Candidates

- **stage-magician** archetype. Purpose: sensory/dramaturgic
  provocations using stage, prop, reveal, audience, timing. Originally
  tagged as the V1.1 sensory slot. **Parked in v0.3.0** because
  `radagast-brown` took the adjacent slot (biosphere/care axis)
  first; dramaturgic/sensory stays open for V1.2 if Radagast proves
  itself but a further distinct voice is still missing.

## V2 Extensions

- **`--deep` mode.** Calls `devil-advocate-swarms:swarm-orchestrator`
  on the V1 quick output to pressure-test the 10 provocations and
  cluster them into 3 fleshed-out outliers.
- ~~`--chat` mode~~ — shipped as v0.5.0, 2026-04-23. See Chat-Mode
  section in SKILL.md. The originally envisioned tmux/costly-debate
  version was NOT built; instead the flow is synchronous (rounds 1-2
  parallel calls, round 3 Codex distillation), ~10 LLM calls total.

## V3 Bridge

- **Telegram bridge.** ductor (github.com/PleasePrompto/ductor) or
  Anthropic's official external_plugins/telegram. Decision deferred
  to 2 weeks of V1 usage. Security gate: full security-audit and
  codex:rescue security-review pass required before any Telegram
  adoption.
