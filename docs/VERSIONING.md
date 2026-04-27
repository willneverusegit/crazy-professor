# Versioning Policy — crazy-professor

**Adopted:** 2026-04-27 (Phase 1 wrap-up)
**Scheme:** SemVer-adjusted for the 0.x phase

## Where the version lives

The single source of truth is `.claude-plugin/plugin.json`. The following files mirror it and must be bumped together:

- `.claude-plugin/plugin.json` — `version` field
- `skills/crazy-professor/SKILL.md` — `metadata.version` in frontmatter
- `skills/crazy-professor/resources/output-template.md` — `version` in the embedded frontmatter that gets copied into every single-run output
- `skills/crazy-professor/resources/chat-output-template.md` — `version` in the embedded frontmatter that gets copied into every chat-run output
- `docs/chat-mode-flow.md` — `version` in own frontmatter and in the documented output frontmatter example
- `skills/crazy-professor/prompt-templates/chat-curator.md`, `chat-round-1-wrapper.md`, `chat-round-2-wrapper.md` — `version` in frontmatter

Historical statements in CHANGELOG.md, plans, and CAPABILITIES.md (e.g. "stabilized 2026-04-23 (v0.5.1)") are facts about the past and are NOT updated on a bump.

## When to bump

While the project is in the `0.x` range, SemVer is interpreted as follows:

| Bump | When | Examples |
|---|---|---|
| **MINOR** (`0.x.0` → `0.{x+1}.0`) | Any user-visible behavioral change, new feature, structural reorganization that changes how the skill loads, or a breaking change. The 0.x range allows breaking changes inside MINOR. | New mode, new flag, contract change (e.g. `--chat` without topic now rejected), new archetype, new picker mechanic. Also: completion of a Master-Plan phase that delivers user-facing capability. |
| **PATCH** (`0.x.y` → `0.x.{y+1}`) | Bugfix without behavioral change for users following the documented contract; internal hardening; documentation correction; non-functional refactor. | Codex-distiller hardening (v0.5.1), cross-reference path fix after extraction, prompt-template wording tightening. |
| **MAJOR** (`0.x.y` → `1.0.0`) | First production-stable release. Reserved for when the skill has passed Museum-Clause review and core mechanics are settled. | Not yet planned. |

## Mapping to the Erweiterungs-Master-Plan

The plan in `docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md` has 8 phases. Default mapping (override on a phase-by-phase basis if a phase is purely internal):

| Phase | Default bump | Reason |
|---|---|---|
| Phase 1 — Vertragsbereinigung & Quick-Wins | **MINOR** (0.6.0) | Topic-resolution contract changed (`--chat` without topic now rejected) → user-visible behavior change. |
| Phase 2 — Picker als Skript + field-notes-Schema | **MINOR** | Pre-tool-step changes how every run produces its picks. |
| Phase 3 — Linter-Trio + Eval-Suite | **PATCH** or **MINOR** | If linters only protect existing behavior → PATCH. If eval-suite changes the prompt-edit workflow visibly → MINOR. |
| Phase 4 — Telemetrie & Lernschleife | **MINOR** | Patch-suggestion-loop is user-visible (a new artifact appears every 10 runs). |
| Phase 5 — Run Planner | **MINOR** | New `--from-session`, `--dry-run`, archetype-selector flags. |
| Phase 6 — Cross-Pollination + Kompakt-Modus | **MINOR** | New `--chat --compact` and `--strict-cross-pollination` flags; 4th PO-operator activated. |
| Phase 7 — GUI/Playground (optional) | **MINOR** | New surface area; possibly its own subfolder version. |
| Phase 8 — Telegram-Bridge (optional) | **MINOR** | Major surface area + security implications. |

Within a phase, additional fixes/iterations bump **PATCH** until the phase ships.

## How to bump

1. Pick the new version per the table above.
2. Update `.claude-plugin/plugin.json` first (single source of truth).
3. Run a search for the old version string and update each frontmatter occurrence listed in "Where the version lives".
4. Add a CHANGELOG.md entry with the new version, the date, and a 1-3 line description per bullet of what changed for users.
5. Update PROJECT.md "Aktueller Stand" line if the user-visible state changed.
6. Tag the git commit with the new version when pushing (so marketplace updates can pick it up): the commit message should start with `crazy-professor | vX.Y.Z: ...`.

## What does NOT trigger a bump

- Adding/editing internal `.agent-memory/` artifacts (field-notes, lab outputs, working notes).
- Changes to `docs/plans/...` (planning docs are not the artifact).
- README.md cosmetic edits.
- Updating this VERSIONING.md itself.
- Updating CHANGELOG.md or PROJECT.md retroactively.

If unsure: check whether a user running `claude plugin update crazy-professor` would see different behavior or a different output frontmatter version. If yes → bump. If no → no bump.
