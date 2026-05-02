---
title: crazy-professor v0.13.0 — Rückbau auf Single-Run + Chat-Mode + Lab
status: design (approved 2026-05-02)
related_master_plan: docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md
follow_up_plan: docs/plans/2026-05-02-v013-rueckbau-implementation.md (TBD)
---

# Spec — crazy-professor v0.13.0 (Rückbau)

## Motivation

Stand 2026-05-02: 18 Runs total in field-notes, 0 telemetry records,
0 patch suggestions, 0 telegram dialogues. Die Phasen 4-8 wurden gebaut,
ohne dass die Phasen 1-3 jemals einen Datenstrom produziert haben, gegen
den die Phasen 4-8 sich rechtfertigen konnten. Master-Plan-Drift mit
geplanter Phasen-Erfüllung als Selbstzweck.

Diagnose vom 2026-05-02 (in dieser Session):
- 4684 Zeilen Python in 11 Skripten — der Großteil hat nie einen realen
  Datensatz produziert.
- 494 Zeilen Pflicht-Lektüre in `operating-instructions.md` vor jeder
  Skill-Invocation.
- 7 User-Flags + Reject-Matrix dreifach dokumentiert.
- field-notes mit 18 Rows als die einzige reale Datengrundlage.

Konsequenz: zurückbauen auf den Skill-Kern (Single-Run + Chat-Mode +
statisches Lab-HTML), git-Historie als Archiv, ehrliche Lerngeschichte
im CHANGELOG.

## Was bleibt (User-Surface)

| Flag | Mode | Output |
|---|---|---|
| `/crazy <topic>` | Single-Run | 10 Provokationen + 1 Next Experiment |
| `/crazy <topic> --chat` | Chat-Mode | 4×5 destillierte Ideen + Top-3 + Next Experiment |
| `/crazy --lab` | Standalone-Browser | Statische HTML zum Review gepasteter Outputs |

## Was bleibt (Skill-Komponenten)

- `commands/crazy.md` (gekürzt auf ~12 Zeilen)
- `skills/crazy-professor/SKILL.md` (~120 Zeilen statt 273)
- `skills/crazy-professor/scripts/picker.py` (gekürzt um Force-Flags
  und `--wishful-share`)
- `skills/crazy-professor/lab/` (Ordner, enthält `index.html` —
  statisch, unverändert)
- 4 Archetype-Templates: `first-principles-jester.md`,
  `labyrinth-librarian.md`, `systems-alchemist.md`, `radagast-brown.md`
- 3 Chat-Wrapper: `chat-round-1-wrapper.md`,
  `chat-round-2-wrapper.md`, `chat-curator.md`
- `output-template.md`, `chat-output-template.md`
- `provocation-words.txt`, `retired-words.txt`, `po-operators.md`
- 1 vereinfachte `field-notes-schema.md`
- `references/operating-instructions.md` (~80 Zeilen statt 494)
- `references/hard-rules.md` (~80 Zeilen statt 106)
- `references/roadmap.md` (gekürzt, kein Phase 8 mehr)

## Was wird gelöscht (hart, git-Historie als Archiv)

**10 Python-Skripte + 1 Shell-Wrapper:**
- `validate_output.py`
- `lint_voice.py`
- `lint_word_pool.py`
- `lint_cross_pollination.py`
- `eval_suite.py`
- `telemetry.py`
- `patch_suggester.py`
- `run_planner.py`
- `telegram_dialogue.py`
- `build_playground.py`
- `run_linters.sh` (Shell-Wrapper)

**1 Ordner:**
- `playground/`

**4 References:**
- `chat-mode-flow.md` (Stub, Inhalt lebt nur in `docs/chat-mode-flow.md`
  — auch das wird gekürzt)
- `radagast-activation.md` (4 binding conditions wandern in
  `radagast-brown.md` als Prosa-Bullets)
- `review-rubric.md` (3-Achsen-Rubrik wandert in `hard-rules.md`)
- `usage-patterns.md` (Doppel von `docs/USAGE-PATTERNS.md`)

**3 Resources:**
- `archetype-keywords.txt` (war run_planner-Daten)
- `stop-words.txt` (war lint_cross_pollination-Daten)
- `field-notes-init.md` (Init-Logik wandert in `picker.py`-Docstring)

**4 Lexicon-Gate-YAML-Blöcke** am Ende der 4 Archetype-Templates.
Verbotenes Vokabular bleibt als Prosa-Bullet erhalten.

**Plan-/Spec-Files:**
- `docs/specs/2026-04-28-phase-5-run-planner-design.md`
- `docs/specs/2026-04-28-phase-6-cross-pollination-compact-design.md`
- `docs/specs/2026-04-28-phase-7-playground-design.md`
- `docs/specs/2026-04-30-phase-8-telegram-solution-dialogue.md`
- `docs/specs/2026-04-30-ideation-lab-v2.md`
- `docs/plans/2026-04-30-ideation-lab-v2-implementation.md`
- `docs/eval-baseline-2026-04-27.md`
- `docs/eval-baseline-2026-04-28.md`
- `docs/USAGE-PATTERNS.md` (Doppel)
- `docs/linters.md`

(Bemerkung: die Phase-2/3/4-Plan-Files bleiben als historische Belege
liegen, weil sie tatsächlich gebaut wurden und der Plan ein Plan war.
Es geht nicht um Geschichts-Klitterung, sondern um aktuelle Skill-
Lesbarkeit.)

## User-Flags die wegfallen

- `--from-session`
- `--dry-run`
- `--compact`
- `--strict-cross-pollination`
- `--playground`

## Datenfluss nach Rückbau

### Single-Run (5 Steps statt 7+3+6)

1. **Topic parsen.** Topic-Text vorhanden → weiter. Kein Topic, keine
   Flags → letzten Konversations-Kontext nehmen oder eine
   Klarstellungs-Frage stellen. `--chat` ohne Topic → ablehnen mit
   fester Fehlermeldung.
2. **Picker aufrufen.**
   `python picker.py --field-notes <path> --words <path>
   --retired <path>`. Skript liefert JSON mit `archetype`, `word`,
   `operator`, `re_rolled`, `timestamp`. Variation-Guard ist im Skript
   drin (Archetype-Streak ≥3 → re-roll, Wort in den letzten 10 Rows
   → re-roll). Fallback wenn Python fehlt: Prosa-Mechanik aus dem
   Picker-Skript-Docstring.
3. **Archetype-Template laden.** Eines von vier Files in
   `prompt-templates/`. Voice-Regeln befolgen.
4. **10 Provokationen schreiben.** Jede Zeile:
   `<text> -- [cost: <level>] -- anchor: <link>`. Eine als
   "Next Experiment" markieren. Output schreiben nach
   `<target>/.agent-memory/lab/crazy-professor/YYYY-MM-DD-HHMM-<topic-slug>.md`.
   Kein Pre-Write-Check — das Format ist Soll-Vertrag im Prompt-
   Template.
5. **Field-Notes-Row anhängen.** Eine Markdown-Tabellen-Zeile in
   `field-notes.md` mit den Picker-Werten und `pending`-Defaults
   für Review-Spalten.

### Chat-Mode (C1–C6 statt C1–C8)

C1. **Topic + Flag parsen.** `--chat` ohne Topic → ablehnen.
C2. **4 Picker-Aufrufe.** `picker.py --mode chat` liefert 4 Picks
    (eine je Archetype). Word-Guard läuft auch innerhalb des Chat-Runs
    (kein Wort doppelt in den 4 Picks).
C3. **Round 1 — 4 parallele Calls.** Jeder Archetype mit Standard-
    Template + `chat-round-1-wrapper.md`. Jeder liefert 5 Provokationen.
    Insgesamt 20.
C4. **Round 2 — 4 parallele Calls.** Jeder Archetype mit Standard-
    Template + `chat-round-2-wrapper.md`. Bekommt die 15 Provokationen
    der anderen 3 als Input. Liefert 2-3 Cross-Pollination-Items mit
    `counter:`/`extend:`-Markern. Wenn ≥2 Archetypen unter 2 Items
    liefern: `round2_status: degraded` im Frontmatter, R2-Output
    verworfen, R3 bekommt nur R1.
C5. **Round 3 — Codex-Distillation.** `codex:codex-rescue` Subagent mit
    `chat-curator.md`-Prompt. Liefert 4×5 Final-Ideen + Top-3
    Cross-Pollination + Next Experiment direkt als Markdown. Wenn Codex
    versagt: identischer Prompt durch Claude selbst, Frontmatter-Marker
    `distiller: claude (codex-fallback)`.
C6. **Output schreiben + Field-Notes-Row anhängen.** Output nach
    `<target>/.agent-memory/lab/crazy-professor/chat/YYYY-MM-DD-HHMM-<topic-slug>.md`.
    Field-Notes-Row mit `mode: chat`, `archetype: all-4`,
    `word: multi`, `operator: multi`.

### --lab (Standalone)

L1. **Datei prüfen + öffnen.**
    `webbrowser.open('skills/crazy-professor/lab/index.html')`. Fallback
    wenn das fehlschlägt: `Open this file manually: file://<absolute-path>`
    ausgeben. Fertig — kein LLM-Call, kein File-Write, keine
    Field-Notes-Row.

### Was rausfällt aus dem Datenfluss

- Step 2a (Run Planner Archetype-Selector)
- Step 2d (Dry-Run-Output)
- Step 5b (Voice-Lint)
- Pre-Write-Validator-Check in Step 6
- Step 7b (Telemetry-Append)
- Step 7c (Patch-Suggester alle 10 Runs)
- Step C4b (Cross-Pollination-Substanz-Check)
- Step C7b (Telemetry-Append im Chat-Mode)

## Hard Rules nach Rückbau

Die 11 Hard-Rules-Sätze bleiben. Was wegfällt sind nur die Verweise auf
gelöschte Files:

- Regel 6 (No cross-archetype contamination) wird wieder Prosa-only —
  kein Verweis auf Voice-Linter, kein Verweis auf Lexicon-Gate.
- Verweis auf `references/radagast-activation.md` weg — die 4 binding
  conditions wandern in `radagast-brown.md` als Prosa-Bullets.
- Verweis auf `references/review-rubric.md` weg — die 3 Achsen passen
  in 5 Zeilen direkt in `hard-rules.md`.

## PO-Operatoren

Alle 4 bleiben, gleichverteilt:
1. `reversal`
2. `exaggeration`
3. `escape`
4. `wishful-thinking`

`picker.py --wishful-share` wird entfernt — Würfel ist gleichverteilt.

## Picker-Skript: Force-Flags

Die drei Force-Flags `--force-archetype`, `--force-word`,
`--force-operator` waren ausschließlich für die `--playground`-
Browser-Roundtrip-Mechanik gedacht. Mit dem Wegfall des Playgrounds
fallen auch die Flags weg. Picker-Skript bleibt deterministisch über
den Timestamp-Seed.

## Migrationsplan (Implementation-Plan-Vorlage)

11 Schritte, ein Commit pro logischem Schritt:

1. Branch + Commit-Strategie. Direkt auf `master`, ein Commit pro Step.
2. Plan-Dokumente + Specs aufräumen. (10 Files aus dem
   Plan-/Spec-Files-Block in "Was wird gelöscht")
3. Skripte löschen. (10 Python-Files + 1 Shell-Wrapper)
4. Resources aufräumen. (3 Files)
5. `playground/`-Ordner löschen.
6. References aufräumen. (4 Files)
7. `picker.py` schlanker machen (Force-Flags + `--wishful-share` raus).
8. Archetype-Templates aufräumen (Lexicon-Gate-YAML-Blöcke raus).
9. `SKILL.md` + `commands/crazy.md` + `operating-instructions.md` +
   `hard-rules.md` neu schreiben.
10. `docs/PROJECT.md` + `docs/CAPABILITIES.md` + `docs/ARCHITECTURE.md`
    + `docs/CHANGELOG.md` aktualisieren. v0.13.0 in `plugin.json` + 8
    Frontmatter-Files.
11. Smoke-Test (manuell, kein Commit).

## Risiken

- **Format-Drift ohne Validator.** Wenn Claude einmal einen Output
  schreibt der nur 9 statt 10 Provokationen hat oder das anchor-Pattern
  verfehlt, gibt es kein Hard-Gate mehr. Mitigation: das Pattern bleibt
  im `output-template.md` und im Archetype-Template-Schluss als
  ausführliches Beispiel. Wird beim Lesen sichtbar.
- **Variation-Guard hängt an Field-Notes-Schema.** Wenn das Schema
  kaputt geht (z.B. ein manuell editierter Run mit anderer Spalten-
  Zahl), kann der Picker fehlschlagen. Mitigation: Picker-Skript hat
  Fallback "wenn Parse fehlschlägt, weiter ohne Guard" + warnt auf
  stderr.
- **Chat-Mode bleibt teuer.** ~10 LLM-Calls + Codex-Subagent — das
  ist nach dem Rückbau weiterhin der teuerste Pfad. Bewusste
  Entscheidung beim Brainstorming.
- **Lab-HTML könnte verwaisen.** Wenn der Output-Format sich in
  Zukunft ändert, muss das Lab seine Parser anpassen. Mitigation: Lab
  parst aktuell nachsichtig.
- **Reverse-Risiko: zu viel zurückgebaut.** Wenn in 4 Wochen z.B. der
  Voice-Linter vermisst wird — git-Historie ist Archiv:
  `git show <commit>:skills/crazy-professor/scripts/lint_voice.py
   > scripts/lint_voice.py` holt es zurück.

## Versionierung

**v0.13.0** — MINOR-Bump trotz starker Reduktion. Begründung:
SemVer-pre-1 erlaubt das. Die User-Surface ändert sich (5 Flags weg),
nicht aber der Skill-Kern. Ein MAJOR-Bump auf v1.0.0 wäre möglich,
aber der Skill war noch nie als "1.0" gedacht. Bleibt in 0.x bis das
field-notes-Volumen stabil zeigt dass der Skill genutzt wird.

## Smoke-Test Akzeptanzkriterien

- Single-Run liefert Markdown-File mit 10 Zeilen
  `<text> -- [cost: X] -- anchor: Y` + Next-Experiment-Section.
- Chat-Mode liefert Markdown-File mit Round 1, Round 2 (oder
  degraded-Marker), Round 3 mit 4×5 Items, Top-3, Next Experiment.
- `/crazy --lab` öffnet einen Browser-Tab.
- Field-Notes-Tabelle hat 2 neue Rows (1 single, 1 chat).
- Keine Reste von `--playground`, `--from-session`, `--dry-run`,
  `--compact`, `--strict-cross-pollination` im Code (`grep` über
  `commands/`, `skills/`, `docs/` ist clean).

## CHANGELOG-Eintrag (vorbereitet)

```markdown
## [v0.13.0] [2026-05-02] Rückbau auf Single-Run + Chat-Mode + Lab

**Versions-Bump-Begründung (per VERSIONING.md):** MINOR-Bump weil die
User-Flag-Surface schrumpft (`--playground`, `--from-session`,
`--dry-run`, `--compact`, `--strict-cross-pollination` entfernt) und
~3000 Zeilen Tooling stillgelegt werden, der Skill-Kern (4 Archetypen,
Picker, Chat-Mode-Distillation) aber unverändert bleibt.

**Lerngeschichte:** Stand 2026-05-02 hatte der Skill 18 Runs total in
field-notes, 0 telemetry records, 0 patch suggestions, 0 telegram
dialogues. Die Phasen 4-8 (Telemetrie, Patch-Suggester, Run-Planner,
Cross-Pollination-Linter, Voice-Linter, Word-Pool-Linter, Eval-Suite,
Telegram-Dialogue, Playground, Lab v2) wurden gebaut, ohne dass die
Phasen 1-3 jemals einen Datenstrom produziert haben, gegen den die
späteren Phasen sich rechtfertigen konnten. Master-Plan-Drift mit
geplanter Phasen-Erfüllung als Selbstzweck. Rückbau ist die Konsequenz:
weniger Maschinerie, sodass die Frage "wird der Skill wirklich genutzt"
überhaupt sauber beantwortbar wird.

- 10 Python-Skripte + 1 Shell-Wrapper gelöscht (validate_output,
  lint_voice, lint_word_pool, lint_cross_pollination, eval_suite,
  telemetry, patch_suggester, run_planner, telegram_dialogue,
  build_playground, run_linters.sh).
- `playground/`-Ordner gelöscht.
- 4 Reference-Files gelöscht (chat-mode-flow stub, radagast-activation,
  review-rubric, usage-patterns).
- 3 Resources gelöscht (archetype-keywords, stop-words,
  field-notes-init).
- 4 Lexicon-Gate-YAML-Blöcke aus den Archetype-Templates entfernt.
- 5 User-Flags entfernt (`--playground`, `--from-session`, `--dry-run`,
  `--compact`, `--strict-cross-pollination`).
- `picker.py` schlanker (Force-Flags + `--wishful-share` raus).
- `SKILL.md` von 273 auf ~120 Zeilen.
- `operating-instructions.md` von 494 auf ~80 Zeilen.
- `hard-rules.md` von 106 auf ~80 Zeilen.
- `commands/crazy.md` von 30 auf ~12 Zeilen.
- 6 Plan-/Spec-Files gelöscht (Phase 5/6/7/8 Specs + Plans, 2
  eval-baselines).
- 2 Doku-Doppel weg (`docs/USAGE-PATTERNS.md`, `docs/linters.md`).
```
