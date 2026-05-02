# Architektur — crazy-professor

## Ueberblick

crazy-professor ist ein Claude-Code-Plugin mit einer SKILL.md als Haupt-Logik und einem Slash-Command (`/crazy`) als Trigger. Bei Invocation laeuft eine Picker-Phase (Archetype + Wort + Operator), eine Generations-Phase (LLM-Call mit Archetype-spezifischem Prompt-Template), und eine Persistenz-Phase (Output-Datei + field-notes-Logging). Chat-Mode skaliert das auf 4 parallele Archetypen plus eine Codex-Subagent-Distillation. `--lab` öffnet ein statisches HTML zum Triagen bestehender Outputs ohne LLM-Call.

## Komponentendiagramm

```
User Prompt / "crazy professor" / /crazy <topic>
       |
       v
  Slash-Command commands/crazy.md
       |  (parses $ARGUMENTS, dispatches by --chat / --lab flags)
       v
  +---------------------+   +-------------------------+   +----------------+
  | Single-Run-Path     |   | Chat-Mode-Path (--chat) |   | Lab (--lab)    |
  | (default)           |   |                         |   | standalone     |
  +---------+-----------+   +------------+------------+   +-------+--------+
            |                            |                        |
            v                            v                        v
  Picker (mod-4 timestamp)    Picker x4 (timestamp + offset)    webbrowser.open()
  + Variation-Guard           + Variation-Guard pro Archetype     |
            |                            |                        v
            v                            v                lab/index.html
  Archetype-Prompt-Template   Round 1: 4 parallele Calls    (browser-only)
  (one of four)               Round 2: 4 parallele Calls
            |                 Round 3: codex:codex-rescue
            v                            v
  10 Provokationen            20 Final-Ideen
  + 1 Next-Experiment         + Top-3 Cross-Pollination
            |                 + Next-Experiment
            v                            |
  Output-File:                           v
  .agent-memory/lab/crazy-professor/   Output-File:
  YYYY-MM-DD-HHMM-<topic>.md           .agent-memory/lab/crazy-professor/chat/
            |                          YYYY-MM-DD-HHMM-<topic>.md
            v                                   |
  +-----------------------------+----------------+
                                |
                                v
                      field-notes.md (gemeinsamer Log)
```

## Kernkomponenten

### Slash-Command
- **Datei(en):** `commands/crazy.md`
- **Aufgabe:** Trigger via `/crazy <topic> [--chat] [--lab]`. Parst `$ARGUMENTS`, dispatcht zwischen Single-Run, Chat-Mode und Lab.
- **Abhaengigkeiten:** `skills/crazy-professor/SKILL.md`

### SKILL.md
- **Datei(en):** `skills/crazy-professor/SKILL.md`
- **Aufgabe:** Operative Vorschrift fuer Claude. Definiert Schritte 1-5 fuer Single-Run, C1-C6 fuer Chat-Mode, L1 fuer Lab. Verweist auf Hard-Rules (Museum-Clause, Field-Test-Rule).
- **Abhaengigkeiten:** prompt-templates/, references/, resources/

### Prompt-Templates
- **Datei(en):** `skills/crazy-professor/prompt-templates/{first-principles-jester,labyrinth-librarian,systems-alchemist,radagast-brown}.md` + Chat-Mode-Wrapper (`chat-round-1-wrapper.md`, `chat-round-2-wrapper.md`, `chat-curator.md`)
- **Aufgabe:** Die "System-Prompt-Kern"-Bloecke pro Archetype. Definieren Stimme, Pflicht- und Verbots-Vokabular. Radagast-Template enthaelt zusaetzlich die "Activation Amendments" mit den 4 binding conditions.
- **Abhaengigkeiten:** —

### References (Load-on-Demand)
- **Datei(en):** `skills/crazy-professor/references/`
- **Aufgabe:** 3 Detail-Dokumente: `operating-instructions.md` (Steps 1-5, C1-C6, L1), `hard-rules.md` (Hard Rules + Museum + Review-Rubric), `roadmap.md` (Out-of-Scope-Design-Intent + Rolled-Back-Section).
- **Abhaengigkeiten:** —

### Resources
- **Datei(en):** `skills/crazy-professor/resources/`
- **Aufgabe:** Statische Daten: `provocation-words.txt` (Pool), `retired-words.txt` (Schwarze Liste), `po-operators.md` (4 Operatoren), `output-template.md`, `chat-output-template.md`, `field-notes-schema.md`.
- **Abhaengigkeiten:** —

### Picker-Skript
- **Datei(en):** `skills/crazy-professor/scripts/picker.py`
- **Aufgabe:** Deterministische stochastische Auswahl mit Variation-Guard. Liest `field-notes.md` (letzte 10 Rows), wendet Anti-Streak-Logik an, schreibt JSON auf stdout. Modi: `--mode single` (default), `--mode chat`. Stdlib-only.
- **Abhaengigkeiten:** Python 3 (optional — Fallback-Prosa-Mechanik im Modul-Docstring fuer python-lose Umgebungen).

### Lab (statisches HTML)
- **Datei(en):** `skills/crazy-professor/lab/index.html`
- **Aufgabe:** Browser-Triage-Surface. User paste'd einen vorhandenen crazy-professor-Output, scored Ideen nach Wert/Umsetzbarkeit/Systemfit, kopiert eine Experiment-Card raus. Pure-Static, `file://`-tauglich, kein LLM-Call, kein File-Write von Browser-JavaScript.
- **Abhaengigkeiten:** HTML5 + vanilla JavaScript (Clipboard API).

### Codex-Subagent (extern)
- **Datei(en):** Plugin `codex` mit `codex:codex-rescue` Skill
- **Aufgabe:** Round-3-Distillation in Chat-Mode. Bekommt bis zu 32 Provokationen, gibt 20 Final-Ideen + Top-3 Cross-Pollination + Next-Experiment zurueck.
- **Abhaengigkeiten:** Codex CLI installiert + lauffaehig. Bei Ausfall: Claude-Fallback im selben Prompt.

## Datenfluss

1. User triggert `/crazy <topic>` oder Trigger-Phrase ("crazy professor", "verrueckter professor", ...).
2. Slash-Command parst `$ARGUMENTS`, dispatched. Bei leerem Topic in Single-Run: Letzten Konversations-Kontext nehmen. Bei `--chat` ohne Topic: Reject.
3. SKILL.md ruft Picker-Skript auf (Archetype mod-4 aus UTC-Minute, Operator mod-4 aus UTC-Sekunde, Wort microsecond-seeded aus aktivem Pool minus retired).
4. Variation-Guard im Picker-Skript liest letzte 10 Rows von `field-notes.md`, blockiert/re-rolled bei Archetype-Streak (≥3) oder Wort-Wiederholung.
5. Archetype-Prompt-Template wird geladen, LLM-Call erzeugt 10 Provokationen mit Adoption-Cost-Tag + Anchor.
6. Output-Datei in `.agent-memory/lab/crazy-professor/YYYY-MM-DD-HHMM-<topic-slug>.md`.
7. Field-Notes-Row in `field-notes.md` angehaengt mit Timestamp, Archetype, Wort, Operator, Topic-Slug, Output-Pfad, `re-rolled`-Wert.

Chat-Mode-Variante:
- Schritt 3: 4 Picker-Aufrufe parallel mit Timestamp-Offset, Variation-Guard pro Archetype.
- Schritt 5 ersetzt durch Round-1 (4 parallele Calls, 5 Provokationen je), Round-2 (4 parallele Cross-Pollination-Calls), Round-3 (Codex-Distiller-Call).
- Output-Datei in `.agent-memory/lab/crazy-professor/chat/YYYY-MM-DD-HHMM-<topic-slug>.md` mit `mode: chat`-Frontmatter.
- Field-Notes-Row markiert `mode: chat`, `archetype: all-4`, `word: multi`.

Lab-Variante:
- Schritt 1+2 reduziert auf `webbrowser.open(...)` mit dem statischen HTML-Pfad.
- Keine Schritte 3-7. Kein LLM-Call, kein File-Write, keine Field-Notes-Row.

## Persistenz

| Speicher | Typ | Pfad | Inhalt |
|----------|-----|------|--------|
| Output-Files Single | Markdown | `.agent-memory/lab/crazy-professor/YYYY-MM-DD-HHMM-<topic-slug>.md` | Pro Single-Run: 10 Provokationen + Next-Experiment + Self-Flag-Checkboxes |
| Output-Files Chat | Markdown | `.agent-memory/lab/crazy-professor/chat/YYYY-MM-DD-HHMM-<topic-slug>.md` | Pro Chat-Run: 3 Runden + 20 Final-Ideen + Top-3 + Next-Experiment |
| Field-Notes-Log | Markdown-Tabelle | `.agent-memory/lab/crazy-professor/field-notes.md` | Eine Row pro Run, Single + Chat gemischt |
| Provocation-Words-Pool | TXT | `skills/crazy-professor/resources/provocation-words.txt` | Aktive Wort-Liste, eine Zeile je Eintrag |
| Retired-Words | TXT | `skills/crazy-professor/resources/retired-words.txt` | Schwarze Liste fuer 3-mal-monoton-geflaggt-Worte |

Persistenz ist ohne Telemetrie-Layer (in v0.13.0 zurueckgebaut). Field-Notes-Markdown-Tabelle ist die einzige maschinenlesbare Run-Persistenz.

## Sicherheit

- **Persona-Drift-Risiko**: Persona-Prompting kann auf wissensschweren Tasks bis zu 30pp Genauigkeit kosten (Search Engine Journal 2024). Hard Rule "Output is never advice" + Warning-Banner im Output-Template adressieren das. Verbotenes Vokabular pro Archetype lebt als Prosa in den Prompt-Templates (Voice-Linter wurde in v0.13.0 zurueckgebaut, ist Soll-Vertrag im Prompt).
- **Adoption-Risiko**: Museum-Clause limitiert Adoption-ohne-Evidenz: nach 10 Runs ohne Keeper zieht der Skill sich selbst zurueck.
- Keine Secrets im Repo. Keine Netzwerk-Calls aus dem Skill ausser ueber Codex-Subagent (Round-3) und das Standard-Claude-Code-LLM-API.

## Deployment

- **Lokal nur**: Plugin in `~/.claude/plugins/` (oder `~/.claude/skills/<name>/` fuer Standalone-Form).
- **Marketplace**: aktuell nicht im offiziellen Anthropic-Marketplace. Local-Install via `claude plugin install crazy-professor --scope user`. README beschreibt Marketplace-Variante mit `claude plugin marketplace add willneverusegit/crazy-professor`.
- **Update**: `claude plugin update crazy-professor`. Marketplace-Cache wird neu gezogen — Quelle muss als Tag/Release veroeffentlicht sein.
- **Trigger**: Slash-Command `/crazy <topic> [--chat]` / `/crazy --lab` oder Trigger-Phrasen aus SKILL.md (deutsch + englisch).

## Was in v0.13.0 entfernt wurde

Phasen 4-8 (Telemetrie, Patch-Suggester, Run-Planner, Voice/Word-Pool/Cross-Pollination-Linter, Eval-Suite, Telegram-Dialogue, Browser-Playground, Ideation-Lab-v2-Design) wurden am 2026-05-02 zurueckgebaut. Detail in `docs/CHANGELOG.md` v0.13.0 Eintrag.
