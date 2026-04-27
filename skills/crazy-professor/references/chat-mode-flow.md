---
title: crazy-professor Chat-Mode Flow Specification
status: stub — see canonical source
canonical_source: docs/chat-mode-flow.md
created: 2026-04-23
deduplicated: 2026-04-27
---

# Chat-Mode Flow Specification — Stub

The full and authoritative chat-mode flow specification lives in
`<repo-root>/docs/chat-mode-flow.md` (where `<repo-root>` =
`crazy-professor/`, the plugin repo root). Resolved from this stub's
location: [`../../../docs/chat-mode-flow.md`](../../../docs/chat-mode-flow.md).

This file is a stub maintained for backward compatibility — older SKILL.md
references and load-on-demand patterns may still point at this path. The
content was de-duplicated 2026-04-27 (Phase 1, point 1.3 of the
Erweiterungs-Master-Plan) to prevent drift between two identical copies.

## Why a stub instead of removal

The Claude Code plugin spec encourages skills to reference detail files
under `skills/<skill>/references/`. Removing this file outright would
require updating every SKILL.md cross-reference simultaneously and would
break any external doc that linked to `references/chat-mode-flow.md` as
the path. The stub keeps the path functional while making `docs/`
unambiguously the single source of truth.

## What lives in the canonical file

- Aktivierung syntax and semantics for `--chat` and `--chat --dry-run-round1`.
- Call-Budget table (Round 1: 4, Round 2: 4, Round 3: 1 Codex, Summary: 1 = 10 LLM calls per chat-run).
- Round-1 picker rules, parallel-call structure, abort condition.
- Round-2 cross-pollination semantics (counter / extend), abort/degrade condition.
- Round-3 Codex distillation prompt, output format, Claude fallback.
- Output structure (chat output template, `.agent-memory/lab/crazy-professor/chat/...`).
- Field-Notes-Integration with `mode: chat` marker.
- F2-F5 decisions (taken 2026-04-23, all defaults).
- Error-handling for each round.
- Performance expectations.
- Out-of-scope list for v0.5.x.
- Phase-1 acceptance criteria.

If a future change to the flow is needed, edit only `docs/chat-mode-flow.md`
and bump its version. This stub stays as it is.
