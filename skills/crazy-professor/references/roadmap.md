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
  first; dramaturgic/sensory stays open if Radagast proves itself but
  a further distinct voice is still missing.

## V2 Extensions

- **`--deep` mode.** Calls `devil-advocate-swarms:swarm-orchestrator`
  on the V1 quick output to pressure-test the 10 provocations and
  cluster them into 3 fleshed-out outliers.
- ~~`--chat` mode~~ — shipped as v0.5.0, 2026-04-23. Synchronous flow
  (rounds 1-2 parallel calls, round 3 Codex distillation), ~10 LLM
  calls total. Canonical spec: `<repo-root>/docs/chat-mode-flow.md`.

## V3 Bridge

- **Telegram bridge.** Mobile trigger via ductor or Anthropic's
  external_plugins/telegram. Decision deferred. Security gate:
  full security-audit + codex:rescue security-review pass required
  before any Telegram adoption. The Phase-8 Telegram solution-dialogue
  scaffold from 2026-04-30 was rolled back in v0.13.0 on 2026-05-02
  (never used). When this is reconsidered, start fresh from the
  security-audit step.

## Rolled-Back in v0.13.0

The following Phase 4-8 subsystems were removed on 2026-05-02:
telemetry layer, patch-suggester loop, run-planner (`--from-session`,
`--dry-run`), voice/word-pool/cross-pollination linters, eval-suite,
browser playground (`--playground`), telegram-dialogue scaffold,
ideation-lab-v2 design. See `<repo-root>/docs/CHANGELOG.md` v0.13.0
entry. If any of these are needed again, retrieve from git history
rather than rebuilding from the spec files (the specs are also
deleted).
