# Architektur — crazy-professor

## Ueberblick

crazy-professor ist ein Claude-Code-Plugin mit einer SKILL.md als Haupt-Logik und einem Slash-Command (`/crazy`) als Trigger. Bei Invocation laeuft eine Picker-Phase (Archetype + Wort + Operator), eine Generations-Phase (LLM-Call mit Archetype-spezifischem Prompt-Template), und eine Persistenz-Phase (Output-Datei + field-notes-Logging). Chat-Mode skaliert das auf 4 parallele Archetypen plus eine Codex-Subagent-Distillation.

## Komponentendiagramm

```
User Prompt / "crazy professor" / /crazy <topic>
       |
       v
  Slash-Command commands/crazy.md
       |  (parses $ARGUMENTS, dispatches by --chat flag)
       v
  +----------------------+         +---------------------------+
  | Single-Run-Path      |         | Chat-Mode-Path (--chat)   |
  | (default)            |         |                           |
  +----------+-----------+         +-------------+-------------+
             |                                   |
             v                                   v
  Picker (mod-4 timestamp)            Picker x4 (timestamp + offset)
  + Variation-Guard                   + Variation-Guard pro Archetype
             |                                   |
             v                                   v
  Archetype-Prompt-Template           Round 1: 4 parallele Calls (5 Provokationen je)
  (one of four)                       Round 2: 4 parallele Calls (counter/extend, 3 je)
             |                        Round 3: codex:codex-rescue (Distillation auf 20)
             v                                   v
  10 Provokationen                    20 Final-Ideen
  + 1 Next-Experiment                 + Top-3 Cross-Pollination
             |                        + Next-Experiment
             v                                   |
  Output-File:                                   v
  .agent-memory/lab/crazy-professor/   Output-File:
  YYYY-MM-DD-HHMM-<topic>.md           .agent-memory/lab/crazy-professor/chat/
             |                        YYYY-MM-DD-HHMM-<topic>.md
             v                                   |
  +-----------------------------+----------------+
                                |
                                v
                      field-notes.md (gemeinsamer Log)
```

## Kernkomponenten

### Slash-Command
- **Datei(en):** `commands/crazy.md`
- **Aufgabe:** Trigger via `/crazy <topic> [--chat]`. Parst `$ARGUMENTS`, weicht bei leerem Topic auf den letzten Konversations-Kontext aus. Dispatcht zwischen Single-Run und Chat-Mode.
- **Abhaengigkeiten:** `skills/crazy-professor/SKILL.md`

### SKILL.md
- **Datei(en):** `skills/crazy-professor/SKILL.md`
- **Aufgabe:** Operative Vorschrift fuer Claude. Definiert Schritte 1-7 fuer Single-Run und C1-C8 fuer Chat-Mode. Enthaelt Hard-Rules, Museum-Clause, Field-Test-Rule.
- **Abhaengigkeiten:** prompt-templates/, references/, resources/

### Prompt-Templates
- **Datei(en):** `skills/crazy-professor/prompt-templates/{first-principles-jester,labyrinth-librarian,systems-alchemist,radagast-brown}.md` + Chat-Mode-Wrapper (`chat-round-1-wrapper.md`, `chat-round-2-wrapper.md`, `chat-curator.md`)
- **Aufgabe:** Die "System-Prompt-Kern"-Bloecke pro Archetype. Definieren Stimme, Pflicht- und Verbots-Vokabular.
- **Abhaengigkeiten:** —

### References (Load-on-Demand)
- **Datei(en):** `skills/crazy-professor/references/`
- **Aufgabe:** Detail-Dokumente, die Claude erst lesen muss, wenn der Kontext es verlangt: Radagast-Aktivierung, Review-Rubric, Roadmap, Chat-Mode-Flow, Usage-Patterns.
- **Abhaengigkeiten:** —

### Resources
- **Datei(en):** `skills/crazy-professor/resources/`
- **Aufgabe:** Statische Daten: `provocation-words.txt` (Pool), `retired-words.txt` (Schwarze Liste), `po-operators.md` (4 Operatoren seit v0.11.0), `output-template.md`, `chat-output-template.md` (mit Compact-Mode-Body-Beispiel seit v0.11.0), `archetype-keywords.txt`, `field-notes-init.md`, `field-notes-schema.md`, `stop-words.txt` (seit v0.11.0, fuer Cross-Pollination-Linter Token-Overlap-Filter).
- **Abhaengigkeiten:** —

### Linter-Skripte (4 seit v0.11.0)
- **Datei(en):** `skills/crazy-professor/scripts/lint_voice.py`, `lint_word_pool.py`, `lint_cross_pollination.py` (4. Linter, Phase 6), und der Validator `validate_output.py`.
- **Aufgabe:** Pre-Write-Quality-Gates. `lint_voice` prueft Lexicon-Gate pro Archetype. `lint_word_pool` prueft Wort-Pool-Integritaet. `lint_cross_pollination` prueft R2-Items in Chat-Mode-Output auf Marker-Existenz, Ref-Aufloesung und Token-Overlap mit Ref (warn-only, exit 0 immer). Aktiviert nur via `--strict-cross-pollination`. `validate_output` prueft Format-Drift und seit v0.11.0 die Compact-Mode-Reihenfolge.
- **Abhaengigkeiten:** Stdlib-only. `lint_cross_pollination` liest `resources/stop-words.txt`.

### Codex-Subagent (extern)
- **Datei(en):** Plugin `codex` mit `codex:codex-rescue` Skill
- **Aufgabe:** Round-3-Distillation in Chat-Mode. Bekommt bis zu 32 Provokationen, gibt 20 Final-Ideen + Top-3 Cross-Pollination + Next-Experiment zurueck.
- **Abhaengigkeiten:** Codex CLI installiert + lauffaehig

## Datenfluss

1. User triggert `/crazy <topic>` oder Trigger-Phrase ("crazy professor", "verrueckter professor", ...).
2. Slash-Command parst `$ARGUMENTS`, dispatched. Bei leerem Topic in Single-Run: Letzten Konversations-Kontext nehmen.
3. SKILL.md fuehrt Picker-Phase aus (Archetype mod-4 aus UTC-Minute, Wort aus pool, PO-Operator mod-3 aus UTC-Sekunde).
4. Variation-Guard liest letzte 10 Rows von `field-notes.md`, blockiert/re-rolled bei Archetype-Streak (≥3) oder Wort-Wiederholung.
5. Archetype-Prompt-Template wird geladen, LLM-Call erzeugt 10 Provokationen mit Adoption-Cost-Tag + Anchor.
6. Output-Datei in `.agent-memory/lab/crazy-professor/YYYY-MM-DD-HHMM-<topic-slug>.md`.
7. Field-Notes-Row in `field-notes.md` angehaengt mit Timestamp, Archetype, Wort, Operator, Topic-Slug, Output-Pfad, `re-rolled`-Wert.

Chat-Mode-Variante:
- Schritt 3: 4 Picker-Aufrufe parallel mit Timestamp-Offset, Variation-Guard pro Archetype.
- Schritt 5 ersetzt durch Round-1 (4 parallele Calls, 5 Provokationen je), Round-2 (4 parallele Cross-Pollination-Calls), Round-3 (Codex-Distiller-Call).
- Output-Datei in `.agent-memory/lab/crazy-professor/chat/YYYY-MM-DD-HHMM-<topic-slug>.md` mit `mode: chat`-Frontmatter.
- Field-Notes-Row markiert `mode: chat`, `archetype: all-4`, `word: multi`.

## Persistenz

| Speicher | Typ | Pfad | Inhalt |
|----------|-----|------|--------|
| Output-Files Single | Markdown | `.agent-memory/lab/crazy-professor/YYYY-MM-DD-HHMM-<topic-slug>.md` | Pro Single-Run: 10 Provokationen + Next-Experiment + Self-Flag-Checkboxes |
| Output-Files Chat | Markdown | `.agent-memory/lab/crazy-professor/chat/YYYY-MM-DD-HHMM-<topic-slug>.md` | Pro Chat-Run: 3 Runden + 20 Final-Ideen + Top-3 + Next-Experiment |
| Field-Notes-Log | Markdown-Tabelle | `.agent-memory/lab/crazy-professor/field-notes.md` | Eine Row pro Run, Single + Chat gemischt |
| Provocation-Words-Pool | TXT | `skills/crazy-professor/resources/provocation-words.txt` | Aktive Wort-Liste, eine Zeile je Eintrag |
| Retired-Words | TXT | `skills/crazy-professor/resources/retired-words.txt` | Schwarze Liste fuer 3-mal-monoton-geflaggt-Worte |

Persistenz aktuell ohne strukturiertes Schema und ohne Telemetrie. Phase 2 fuehrt ein field-notes-Schema mit Init-Header-Helper ein, Phase 4 fuehrt ein JSONL/SQLite-Telemetrie-Log parallel zur Markdown-Tabelle ein.

## Sicherheit

- **Persona-Drift-Risiko**: Persona-Prompting kann auf wissensschweren Tasks bis zu 30pp Genauigkeit kosten (Search Engine Journal 2024). Hard Rule "Output is never advice" + Warning-Banner im Output-Template adressieren das. Phase-3-Linter erzwingt Pflicht/Verbots-Vokabular pro Archetype und schliesst Voice-Drift weiter ab.
- **Adoption-Risiko**: Museum-Clause limitiert Adoption-ohne-Evidenz: nach 10 Runs ohne Keeper zieht der Skill sich selbst zurueck.
- **Telegram-Bridge** (Phase 8): Security-Audit als Vorbedingung. Auth/Input-Validation-Surface, externer Channel.
- Keine Secrets im Repo. Keine Netzwerk-Calls aus dem Skill ausser ueber Codex-Subagent (Round-3) und das Standard-Claude-Code-LLM-API.

## Deployment

- **Lokal nur**: Plugin in `~/.claude/plugins/` (oder `~/.claude/skills/<name>/` fuer Standalone-Form).
- **Marketplace**: aktuell nicht im offiziellen Anthropic-Marketplace. Local-Install via `claude plugin install crazy-professor --scope user`. README beschreibt Marketplace-Variante mit `claude plugin marketplace add willneverusegit/crazy-professor`.
- **Update**: `claude plugin update crazy-professor`. Marketplace-Cache wird neu gezogen — Quelle muss als Tag/Release veroeffentlicht sein.
- **Trigger**: Slash-Command `/crazy <topic> [--chat]` oder Trigger-Phrasen aus SKILL.md (deutsch + englisch).
