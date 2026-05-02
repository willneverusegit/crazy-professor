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

v0.13.0 released 2026-05-02. Single-Run, Chat-Mode und statisches Lab-HTML aktiv. Master-Plan-Phasen 1-3 belassen, Phasen 4-8 zurückgebaut. Kein Voice-/Word-Pool-/Cross-Pollination-Linter, keine Telemetrie, kein Patch-Suggester, kein Run-Planner, kein Telegram-Scaffold, kein Browser-Playground. Skill-Kern: ein Python-Helper (`picker.py`), 4 Archetype-Templates, Single-Run + Chat-Mode-Distillation via Codex-Subagent. Anlass des Rückbaus: 18 Runs total in field-notes, 0 Telemetrie-Records, 0 Patch-Suggestions, 0 Telegram-Dialoge — Phase 4-8 wurde gebaut bevor Phase 1-3 einen Datenstrom produziert hatte. Versions-Policy in `docs/VERSIONING.md`.

## Kernfaehigkeiten

Siehe [CAPABILITIES.md](CAPABILITIES.md) fuer die vollstaendige Liste.

Kurzfassung:
- Single-Run: 1 Archetype, 10 Provokationen, 1 Next-Experiment, ~30s
- Chat-Mode (`--chat`): alle 4 Archetypen, 3 Runden, 20 destillierte Ideen, 2-4 min
- Lab (`--lab`): statisches HTML zum Reviewen gepasteter Outputs, kein LLM-Call
- Variation-Guard: Anti-Streak-Logik gegen Archetype-/Wort-Wiederholungen
- Field-Notes-Log: jeder Run wird in `.agent-memory/lab/crazy-professor/field-notes.md` protokolliert
- Museum-Clause: Skill zieht sich nach 10 Runs ohne Keeper selbst zurueck

## Offene Baustellen

- [x] Phase 1: Vertragsbereinigung & Quick-Wins (✅ v0.6.0)
- [x] Phase 2: Picker als Skript + field-notes-Schema (✅ v0.7.0)
- [x] Phase 3: Linter-Trio + Eval-Suite (✅ v0.8.0 → in v0.13.0 zurückgebaut)
- [x] Phase 4: Telemetrie + Patch-Suggestion-Loop (✅ v0.9.0 → in v0.13.0 zurückgebaut)
- [x] Phase 5: Run-Planner (✅ v0.10.0 → in v0.13.0 zurückgebaut)
- [x] Phase 6: Cross-Pollination + Compact-Mode + 4. PO-Operator (✅ v0.11.0 → teilweise in v0.13.0 zurückgebaut, 4. Operator bleibt)
- [x] Phase 7: Single-File-HTML-Playground (✅ v0.12.0 → in v0.13.0 zurückgebaut)
- [x] v0.13.0 (2026-05-02): Phasen 4-8 zurückgebaut, Skill auf Kern reduziert

## Abhaengigkeiten

- Claude Code CLI (Plugin-Host)
- Codex-Subagent (`codex:codex-rescue`) fuer Chat-Mode Round-3-Distillation, Claude-Fallback verfuegbar
- Eigene Repo-interne Resources (`provocation-words.txt`, `po-operators.md`, `prompt-templates/`)

## Beziehungen zu anderen Projekten

- **Nutzt:** Codex-Plugin (Round-3-Destillator), agentic-os (Field-Notes liegen in `.agent-memory/lab/`)
- **Wird genutzt von:** plan-merger Skill nutzt crazy-professor als Beispiel fuer Auto-Mode-Tests
