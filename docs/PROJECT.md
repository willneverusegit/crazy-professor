---
project: crazy-professor
status: active
started: 2026-04
stack: [Markdown, Claude-Code-Plugin, Codex-Subagent]
repo: C:\Users\domes\Desktop\Claude-Plugins-Skills\crazy-professor
wiki_entity: "[[crazy-professor]]"
---
# crazy-professor

## Einzeiler

Divergence-Generator als Claude-Code-Plugin: vier Archetypen produzieren strange-aber-anchored Provokationen, niemals Ratschlaege.

## Aktueller Stand

v0.12.0 released 2026-04-28. Single-Run, Chat-Mode und Browser-Playground aktiv. Master-Plan-Phasen 1-7 abgeschlossen: 1 (Vertragsbereinigung), 2 (Picker-Skript + field-notes-Schema + Output-Validator), 3 (Linter-Trio + Eval-Suite), 4 (Telemetrie + Patch-Suggestion-Loop), 5 (Run-Planner: topic-aware Archetype-Selector + `--from-session` + `--dry-run`), 6 (Cross-Pollination Substanz-Check + Compact-Mode + 4. PO-Operator), 7 (Single-File-HTML-Playground via `/crazy --playground`). Vollständige stdlib-only Python-Toolchain in `scripts/`: picker, validate_output, lint_voice, lint_word_pool, lint_cross_pollination, eval_suite, telemetry, patch_suggester, run_planner, build_playground. Phase 7 hat das Browser-Playground hinzugefügt: Cockpit-Layout mit Topic-Input + 3-Element-Picker, Live-Prompt-Output mit Copy-Button, field-notes-Streak-Warnung. Pure-Static, `file://`-tauglich, kein Server. `picker.py` bekam `--force-word` + `--force-operator` als zwei neue Force-Flags. Phase 8 (Telegram-Bridge, optional, RISIKO) bleibt out-of-scope. Versions-Policy in `docs/VERSIONING.md`.

## Kernfaehigkeiten

Siehe [CAPABILITIES.md](CAPABILITIES.md) fuer die vollstaendige Liste.

Kurzfassung:
- Single-Run: 1 Archetype, 10 Provokationen, 1 Next-Experiment, ~30s
- Chat-Mode (`--chat`): alle 4 Archetypen, 3 Runden, 20 destillierte Ideen, 2-4 min
- Variation-Guard: Anti-Streak-Logik gegen Archetype-/Wort-Wiederholungen
- Field-Notes-Log: jeder Run wird in `.agent-memory/lab/crazy-professor/field-notes.md` protokolliert
- Museum-Clause: Skill zieht sich nach 10 Runs ohne Keeper selbst zurueck

## Offene Baustellen

- [x] Phase 2: Picker als Skript + field-notes-Schema (✅ v0.7.0)
- [x] Phase 3: Linter-Trio (Word-Pool + Pflicht/Verbots-Vokabular pro Archetype) + Eval-Suite (✅ v0.8.0)
- [x] Phase 4: Telemetrie + Patch-Suggestion-Loop alle 10 Runs (✅ v0.9.0)
- [x] Phase 5: Run-Planner (Archetype-Selector + `--from-session` + `--dry-run`) (✅ v0.10.0)
- [x] Phase 6: `--chat --compact`, `--strict-cross-pollination`, 4. PO-Operator (`wishful thinking`) (✅ v0.11.0)
- [x] Phase 7: Single-File-HTML-Playground (`/crazy --playground`) (✅ v0.12.0)
- [ ] Phase 8 (optional, RISIKO): Telegram-Bridge

## Abhaengigkeiten

- Claude Code CLI (Plugin-Host)
- Codex-Subagent (`codex:codex-rescue`) fuer Chat-Mode Round-3-Distillation, Claude-Fallback verfuegbar
- Eigene Repo-interne Resources (`provocation-words.txt`, `po-operators.md`, `prompt-templates/`)

## Beziehungen zu anderen Projekten

- **Nutzt:** Codex-Plugin (Round-3-Destillator), agentic-os (Field-Notes liegen in `.agent-memory/lab/`), playground-Skill (Vorbild fuer Phase 7 GUI)
- **Wird genutzt von:** plan-merger Skill nutzt crazy-professor als Beispiel fuer Auto-Mode-Tests; Master-Plan-Generator-Vorbild
