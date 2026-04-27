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

v0.5.1 released. Single-Run und Chat-Mode aktiv. Codex-Smoke-Test 2026-04-26 sauber. Phase 1 des Erweiterungs-Master-Plans (`docs/plans/2026-04-26-...`) startet — Vertragsbereinigung + Quick-Wins. Picker, Telemetrie, Linter, Run-Planner kommen in Phase 2-5.

## Kernfaehigkeiten

Siehe [CAPABILITIES.md](CAPABILITIES.md) fuer die vollstaendige Liste.

Kurzfassung:
- Single-Run: 1 Archetype, 10 Provokationen, 1 Next-Experiment, ~30s
- Chat-Mode (`--chat`): alle 4 Archetypen, 3 Runden, 20 destillierte Ideen, 2-4 min
- Variation-Guard: Anti-Streak-Logik gegen Archetype-/Wort-Wiederholungen
- Field-Notes-Log: jeder Run wird in `.agent-memory/lab/crazy-professor/field-notes.md` protokolliert
- Museum-Clause: Skill zieht sich nach 10 Runs ohne Keeper selbst zurueck

## Offene Baustellen

- [ ] Phase 2: Picker als Skript + field-notes-Schema
- [ ] Phase 3: Linter-Trio (Word-Pool + Pflicht/Verbots-Vokabular pro Archetype) + Eval-Suite
- [ ] Phase 4: Telemetrie + Patch-Suggestion-Loop alle 10 Runs
- [ ] Phase 5: Run-Planner (Archetype-Selector + `--from-session` + `--dry-run`)
- [ ] Phase 6: `--chat --compact`, `--strict-cross-pollination`, 4. PO-Operator (`wishful thinking`)
- [ ] Phase 7 (optional): Single-File-HTML-Playground
- [ ] Phase 8 (optional, RISIKO): Telegram-Bridge

## Abhaengigkeiten

- Claude Code CLI (Plugin-Host)
- Codex-Subagent (`codex:codex-rescue`) fuer Chat-Mode Round-3-Distillation, Claude-Fallback verfuegbar
- Eigene Repo-interne Resources (`provocation-words.txt`, `po-operators.md`, `prompt-templates/`)

## Beziehungen zu anderen Projekten

- **Nutzt:** Codex-Plugin (Round-3-Destillator), agentic-os (Field-Notes liegen in `.agent-memory/lab/`), playground-Skill (Vorbild fuer Phase 7 GUI)
- **Wird genutzt von:** plan-merger Skill nutzt crazy-professor als Beispiel fuer Auto-Mode-Tests; Master-Plan-Generator-Vorbild
