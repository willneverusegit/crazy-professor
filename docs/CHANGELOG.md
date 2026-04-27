# Changelog — crazy-professor

Neueste Eintraege oben. Format: `## [vX.Y.Z] [YYYY-MM-DD] Kurztitel` für Versions-Bumps, sonst `## [YYYY-MM-DD] Kurztitel`. Versions-Policy in `docs/VERSIONING.md`.

---

## [v0.7.0] [2026-04-27] Phase 2 — Picker-Skript + field-notes-Schema + Output-Validator

**Versions-Bump-Begründung (per VERSIONING.md):** MINOR-Bump weil Picker-Skript als Pre-Tool-Step die Skill-Mechanik strukturell ändert. Master-Plan-Phase 2 abgeschlossen.

- **2.2 field-notes-Schema**: `resources/field-notes-schema.md` legt die canonical Spalten-Spec fest (12 Spalten, append-only Log-Tabelle, Status-Block-Konventionen). `resources/field-notes-init.md` ist das Init-Template, das der Picker bei fehlender field-notes.md ins Ziel-Projekt kopiert.
- **2.1 Picker-Skript** (`scripts/picker.py`, 252 Zeilen, stdlib-only Python): liest die letzten 10 Log-Zeilen von field-notes.md, führt Picker (mod-4 archetype, microsecond-based word, mod-3 operator) aus, wendet die Variation-Guard-Logik aus Step 2b an (archetype-streak ≥3 re-roll, word-window dedup), gibt JSON `{archetype, word, operator, re_rolled, timestamp, mode}` auf stdout. Modi: `--mode single` (default), `--mode chat` (4 parallele Picks). Optionen: `--init-template`, `--force-archetype`, `--force-timestamp`. Smoke-getestet gegen die echte Desktop-field-notes (10 Rows, korrekte Anti-Streak-Erkennung), Chat-Mode (4 unterschiedliche Worte/Operatoren), Force-Archetype, Init-on-missing-file.
- **2.3 Output-Validator** (`scripts/validate_output.py`, ~200 Zeilen, stdlib-only Python): prüft Single-Run- und Chat-Mode-Output auf Format-Drift. Single: Frontmatter, Divergence-Banner, exakt 10 Provokationen mit Pattern `<text> -- [cost: <level>] -- anchor: <text>` (akzeptiert `--`, em-dash `—`, en-dash `–`), Next-Experiment, Self-Flag mit ≥3 Checkboxes. Chat: Round 1/2/3 vorhanden, Round 3 mit exakt 5 Items pro Archetype-Subsection, Top-3 mit genau 3 Items. Smoke-getestet gegen 4 echte Output-Files: pass auf 2026-04-23-Outputs (post-Format-Stabilisierung) und Chat-Mode-Output, fail (korrekt) auf 2026-04-22-Outputs (vor Format-Stabilisierung — diese hatten das Anchor-Pattern noch nicht).
- **SKILL.md + operating-instructions verdrahtet**: Step 2 dokumentiert Picker als preferred Path (Python-Call mit JSON-Parse), Fallback-Path (Prosa-Mechanik) bleibt für Python-fehlt-Umgebungen erhalten. Step 6 dokumentiert Validator als Pre-Write-Check.
- Skripte sind optional. Plugin-Repo bleibt vollständig nutzbar ohne Python.

---

## [v0.6.0] [2026-04-27] Phase 1 — Vertragsbereinigung & Quick-Wins

**Versions-Bump-Begründung (per VERSIONING.md):** MINOR-Bump weil Topic-Resolution-Vertrag breaking change ist (`--chat` ohne Topic wird jetzt explizit abgelehnt; vorher implizites Verhalten). Master-Plan-Phase 1 abgeschlossen.

- `docs/PROJECT.md`, `docs/CAPABILITIES.md`, `docs/ARCHITECTURE.md`, `docs/CHANGELOG.md` aus globalem Template angelegt
- Input-/Trigger-Vertrag in `README.md`, `commands/crazy.md`, `SKILL.md` vereinheitlicht — eine Semantik fuer leeres Topic und `--chat` ohne Topic
- `--chat` ohne Topic wird explizit abgelehnt mit Fehlermeldung
- `docs/chat-mode-flow.md` und `references/chat-mode-flow.md` auf Single-Source-of-Truth zusammengefuehrt
- Mehrwort-Provocation-Words geklaert (Entscheidung: Pool auf Einzel- und 2-Wort-Phrasen erlaubt, `output-template.md` Marker-Format akzeptiert das)
- `SKILL.md` von 464 auf 206 Zeilen getrimmt (-56%) — Operating-Instructions (Steps 1-7 + C1-C8) nach `skills/crazy-professor/references/operating-instructions.md` und Hard Rules (inkl. Museum-Clause, Field-Test-Rule, Radagast-Gate, Review-Rubric) nach `skills/crazy-professor/references/hard-rules.md` extrahiert. Plan-Ziel war ~150 Zeilen; bei 206 belassen, weil Frontmatter (28) + Trigger-Phrases-Block + Archetype-Tabelle + File-Layout-Diagramm zur Skill-Discoverability beim Loaden gebraucht werden — der echte Body-Inhalt ist 166 Zeilen.
- Pfad-Konvention etabliert: alle inter-File-Pfade in SKILL.md, operating-instructions.md, hard-rules.md verwenden `<repo-root>/...` Notation, damit sie aus jedem File konsistent auflösbar sind.
- `docs/VERSIONING.md` angelegt — explizite Versions-Policy für die 0.x-Phase, Bump-Trigger nach Master-Plan-Phasen-Mapping.
- Versions-Bump auf `0.6.0` in `plugin.json`, `SKILL.md` Frontmatter, `output-template.md`, `chat-output-template.md`, `chat-mode-flow.md` (Frontmatter + Output-Beispiel), drei `prompt-templates/chat-*.md`. SKILL.md-Body-Texte entkoppelt (statt "v0.5.1" jetzt "since v0.5.0" für historische Aussagen).

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
