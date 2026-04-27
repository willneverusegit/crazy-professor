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

v0.9.0 released 2026-04-27. Single-Run und Chat-Mode aktiv. Master-Plan-Phasen 1 (Vertragsbereinigung), 2 (Picker-Skript + field-notes-Schema + Output-Validator), 3 (Linter-Trio + Eval-Suite) und 4 (Telemetrie + Patch-Suggestion-Loop) abgeschlossen. Vollständige stdlib-only Python-Toolchain in `scripts/`: picker, validate_output, lint_voice, lint_word_pool, eval_suite, telemetry, patch_suggester. Lexicon-Gate-Block in jedem Archetype-Template macht Voice-Drift-Erkennung maschinenlesbar. Telemetrie-JSONL liegt neben `field-notes.md` in `.agent-memory/lab/crazy-professor/telemetry.jsonl`. Patch-Suggestion-Loop läuft alle 10 Single-Mode-Runs und schreibt Vorschläge nach `lab/.../patches/` (nicht-automatisch, Review-Gate). Phase 5 (Run-Planner), Phase 6 (Cross-Pollination + Compact) stehen an. Versions-Policy in `docs/VERSIONING.md`.

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
