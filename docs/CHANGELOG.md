# Changelog — crazy-professor

Neueste Eintraege oben. Format: `## [YYYY-MM-DD] Kurztitel`

---

## [2026-04-27] Phase 1 — Vertragsbereinigung & Quick-Wins

- `docs/PROJECT.md`, `docs/CAPABILITIES.md`, `docs/ARCHITECTURE.md`, `docs/CHANGELOG.md` aus globalem Template angelegt
- Input-/Trigger-Vertrag in `README.md`, `commands/crazy.md`, `SKILL.md` vereinheitlicht — eine Semantik fuer leeres Topic und `--chat` ohne Topic
- `--chat` ohne Topic wird explizit abgelehnt mit Fehlermeldung
- `docs/chat-mode-flow.md` und `references/chat-mode-flow.md` auf Single-Source-of-Truth zusammengefuehrt
- Mehrwort-Provocation-Words geklaert (Entscheidung: Pool auf Einzel- und 2-Wort-Phrasen erlaubt, `output-template.md` Marker-Format akzeptiert das)
- `SKILL.md` von 464 auf 206 Zeilen getrimmt (-56%) — Operating-Instructions (Steps 1-7 + C1-C8) nach `skills/crazy-professor/references/operating-instructions.md` und Hard Rules (inkl. Museum-Clause, Field-Test-Rule, Radagast-Gate, Review-Rubric) nach `skills/crazy-professor/references/hard-rules.md` extrahiert. Plan-Ziel war ~150 Zeilen; bei 206 belassen, weil Frontmatter (28) + Trigger-Phrases-Block + Archetype-Tabelle + File-Layout-Diagramm zur Skill-Discoverability beim Loaden gebraucht werden — der echte Body-Inhalt ist 166 Zeilen.
- Pfad-Konvention etabliert: alle inter-File-Pfade in SKILL.md, operating-instructions.md, hard-rules.md verwenden `<repo-root>/...` Notation, damit sie aus jedem File konsistent auflösbar sind.

## [2026-04-26] Erweiterungs-Master-Plan via plan-merger Skill

- 8-Phasen-Master-Plan in `docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md` erstellt
- Codex+Claude Auto-Mode mit identischen Prompts → 8 Konflikte mit R/A/I-Bewertung, alle User-bestaetigt
- Codex-Verifier-Run: 7 Findings (3 Codex-Aufruf-Inkonsistenzen, 4 Score-Berechnungsfehler), alle behoben

## [2026-04-23] v0.5.1 — Codex-Prompt-Fix

- Chat-Mode Round-3 Distillation: Direct-Markdown-Return-Contract eingefuehrt (kein Scratch-File, kein Path-only-Response)
- Codex-Smoke-Test 2026-04-26 sauber

## [2026-04-23] v0.5.0 — Chat-Mode

- `--chat` Flag fuer 4-Archetypen-Modus, 3 Runden, ~10 LLM-Calls
- Round-1: parallele 4 Calls, 5 Provokationen je Archetype
- Round-2: Cross-Pollination, counter/extend-Marker
- Round-3: Codex-Distillation auf 5-pro-Archetype = 20 Final-Ideen
- Claude-Fallback bei Codex-Ausfall
- F2-F5 als Defaults bestaetigt

## [2026-04-23] Radagast-Brown Aktivierung

- Vierter Archetype `radagast-brown` produktiv geschaltet
- mod-4-Picker live, alle vier Archetypen mit 25% Wahrscheinlichkeit
- 4 Bindungs-Bedingungen aktiv (Vokabel-Regel, kein Foreign-Field-Smuggling, Optimization-under-Care-Flagging, Folder-Sprawl-Limit)

## [2026-04-22] v0.3.0 — Initial-Scaffold

- Single-Run-Mode mit 3 Archetypen (Jester, Librarian, Alchemist)
- Picker (mod-4 Timestamp), Variation-Guard, Field-Notes-Log, Museum-Clause
- Output-Template mit Adoption-Cost-Tags und Self-Flag-Checkboxes
- Hard Rules + Museum-Clause + Field-Test-Rule etabliert
