# Superplan: crazy-professor — Erweiterungs-Master-Plan

**Datum**: 2026-04-26
**Quelle**: Codex+Claude (Auto-Mode, identische Prompts)
**Ausgangsfrage**: Wie kann der crazy-professor Skill substantiell erweitert werden — inkrementell, substantiell, visionär?
**Iteration**: v1
**Erstellt durch**: plan-merger Skill (Erst-Anwendung, dient gleichzeitig als Skill-Test)

---

## Executive Summary

Der crazy-professor ist konzeptuell stark, dokumentationstechnisch dicht, aber **operativ fragil**: zentrale Mechanik (Picker, Variation-Guard, Museum-Clause, Telemetrie) ist in Prosa beschrieben, nicht in Code abgebildet. Beide Reviewer (Codex + Claude) zeigen hohe Übereinstimmung bei den kritischen Punkten und differieren primär in der Frage der Reihenfolge: **Vertrag bereinigen → Picker bauen → Telemetrie einziehen → dann erst lernen oder erweitern**. Visionäre Erweiterungen (GUI, Telegram) sind explizit ge-scoped, alles andere visionäre (Multi-Provider, Skill-Mesh, Persona-Studio) ist absichtlich ausgeklammert. v0.4.0-Plan wird nicht „abgearbeitet" sondern in den neuen Plan überführt — die Lessons sind drin, ohne den Schuldbegriff fortzuschreiben.

---

## Phasen-Tabelle

| Phase | Ziel                                                                 | Output                                                                                                  | Status |
|-------|----------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|--------|
| 1     | **Vertragsbereinigung & Quick-Wins**                                 | Eindeutige Input-/Trigger-Spec; PROJECT.md+CHANGELOG.md angelegt; chat-mode-flow.md dedupliziert; Mehrwort-Words geklärt | ✅ (2026-04-27)     |
| 2     | **Picker als Skript + field-notes-Schema**                           | Deterministisches Picker-Skript; field-notes.md-Schema im Repo; Init-Header-Helper; Output-Validator    | ✅ (2026-04-27)     |
| 3     | **Linter-Trio + Eval-Suite**                                         | Word-Pool-Linter; Pflicht-/Verbotenes-Vokabel-Linter pro Archetype; Eval-Suite (Pass-Rate-Gate)         | ✅ (2026-04-27)     |
| 4     | **Telemetrie & Lernschleife**                                        | JSONL/SQLite-Run-Log; Variation-Guard-/Museum-Clause-Beobachtbarkeit; Patch-Suggestion-Loop alle 10 Runs | ✅ (2026-04-27)     |
| 5     | **Run Planner**                                                      | Archetype-Selector + `--from-session` als gemeinsame Schicht; `--dry-run` für Picker-Vorschau           | ⏳     |
| 6     | **Cross-Pollination + Kompakt-Modus**                                | `--chat --compact`; Round-2-Substanz-Check (`--strict-cross-pollination`); 4. PO-Operator aktiviert      | ⏳     |
| 7     | **Visionäre Erweiterung — GUI/Playground** (optional, später)        | Single-File-HTML-Playground analog zur `playground` Skill; Browse/Compare/Keep/Retire UI                | ⏳     |
| 8     | **Visionäre Erweiterung — Telegram-Bridge** (optional, später, RISIKO) | Bot-Adapter für mobile Trigger; Security-Audit als Vorbedingung                                         | ⏳     |

Status-Symbole: ✅ erledigt / 🟡 in Arbeit / ⏳ geplant / ❌ blockiert

---

## Bereits getroffene Entscheidungen (nicht neu verhandeln)

- **Codex-Smoke-Test**: durchgeführt 2026-04-26, lief sauber → Codex-Pfad in Chat-Mode ist verifiziert. v0.5.1-Fix ausreichend.
- **v0.4.0-Plan-Status**: NICHT als „abzuarbeitende Schuld" weiterführen. Inhalte (Archetype-Selector, --from-session, Output-as-Patch) gehen in Phase 4 + 5 dieses Plans als Run Planner und Patch-Suggestion-Loop ein.
- **Multi-Provider-Routing**: out of scope. Codex+Claude reichen, marginaler Nutzen rechtfertigt Wartungslast nicht.
- **Stage-Magician-Archetype**: out of scope für diesen Plan. Radagast-Repetition-Watch ist nicht abgeschlossen, neuer Archetype wäre verfrüht.
- **Skill-Mesh-Pipeline** (crazy → plan-merger → executing): out of scope. Interessant, aber nicht jetzt.
- **field-notes.md-Scope**: bleibt pro-Projekt (im jeweiligen `.agent-memory/lab/`). Globaler State unter `~/.claude/state/` ist Spätphase, nicht jetzt.

---

## Punkte-Liste (konsolidiert)

### Phase 1 — Vertragsbereinigung & Quick-Wins (S, 1-2 Tage)

| # | Punkt | Klasse | Provenance | Priorität |
|---|-------|--------|------------|-----------|
| 1.1 | Input-/Trigger-Vertrag vereinheitlichen: `README.md:41`, `commands/crazy.md:12-17` und `SKILL.md:173-176, 253-255` auf eine einzige Semantik bringen für leeres Topic und `--chat` ohne Topic | Konflikt-aufgelöst | Codex (Original D1) | hoch |
| 1.2 | `--chat` ohne Topic explizit ablehnen mit klarer Fehlermeldung | Konsens | Codex+Claude | hoch |
| 1.3 | `docs/chat-mode-flow.md` und `references/chat-mode-flow.md` auf einen Single-Source-of-Truth zusammenführen (Symlink, Generierung oder Streichung) | Konsens | Codex+Claude | mittel |
| 1.4 | `docs/PROJECT.md` + `docs/CAPABILITIES.md` + `docs/ARCHITECTURE.md` + `docs/CHANGELOG.md` aus globalem Template (`~/wiki/templates/project-docs/`) anlegen | Konsens | Codex+Claude | mittel |
| 1.5 | Mehrwort-Provocation-Words (`provocation-words.txt:25, 27, 41`: „ritual debt", „shadow pricing", „smoke test" etc.) klären: entweder explizit erlauben und `output-template.md:15-17` anpassen, oder Pool auf echte Einzelwörter reduzieren | Synthese | Codex+Claude | mittel |
| 1.6 | SKILL.md von 451 auf ~150 Zeilen trimmen: Operating-Instructions + Hard Rules nach `references/operating-instructions.md` und `references/hard-rules.md` extrahieren | Ergänzung | Claude (V8) | mittel |

### Phase 2 — Picker als Skript + field-notes-Schema (M, 3-4 Tage)

| # | Punkt | Klasse | Provenance | Priorität |
|---|-------|--------|------------|-----------|
| 2.1 | **Picker-Skript** (Python oder Bash, ~50 Zeilen): liest `field-notes.md`, würfelt deterministisch (echter UTC-Timestamp), wendet Anti-Streak-Logik an, gibt JSON `{archetype, word, operator, re-rolled}` zurück. Wird als Pre-Tool-Step in SKILL.md verdrahtet. Schließt Schwäche 1.1 (kritisch). | Konsens | Codex+Claude (V12) | kritisch |
| 2.2 | **field-notes.md-Schema** im Repo (Beispieldatei + Spalten-Definition + Init-Header-Helper). Macht Variation-Guard, Museum-Clause und Chat-Aggregation testbar. | Konsens | Codex+Claude (V4) | hoch |
| 2.3 | **Output-Validator**: Regex-/Parser-Check für Single-Run-Format (10 Provokationen, `--[cost: ...] -- anchor: ...`) und Chat-Mode-Round-3-Schema (exakt 5 pro Archetype). Vor Write ausgeführt, blockiert Format-Drift. | Ergänzung | Claude (V2/E1) | hoch |

### Phase 3 — Linter-Trio + Eval-Suite (S+M, 3-4 Tage)

| # | Punkt | Klasse | Provenance | Priorität |
|---|-------|--------|------------|-----------|
| 3.1 | **Provocation-Word-Pool-Linter** (~30 Zeilen): Doubletten, Whitespace, Case-Inkonsistenzen, Mehrwort-Konformität gegen Schema-Entscheidung aus 1.5. Als Pre-Commit-Hook verdrahten. | Ergänzung | Claude (V1/E3) | mittel |
| 3.2 | **Pflicht-/Verbotenes-Vokabel-Linter pro Archetype** (statische Prüfung): scant Output gegen `prompt-templates/<archetype>.md`-Pflicht-Liste (z.B. Radagast: ≥2 Pflicht-Vokabeln in den ersten 10 Sätzen) und gegen Verbotsliste pro Archetype. Stoppt Voice-Drift vor Output. | Ergänzung | Claude (V3/E2) | hoch |
| 3.3 | **Eval-Suite** (50-100 Sample-Runs pro Archetype, automatisch gegen Pflicht/Verbot/Schema gechecked, Pass-Rate als Gate für Prompt-Edits). Macht jeden Prompt-Edit zu einer überprüfbaren Operation. | Konsens | Codex+Claude (V17) | hoch |

### Phase 4 — Telemetrie & Lernschleife (M, 4-5 Tage)

| # | Punkt | Klasse | Provenance | Priorität |
|---|-------|--------|------------|-----------|
| 4.1 | **Telemetrie-Layer**: lokale JSONL (oder SQLite) pro Run mit `picker_values, re_rolled, distiller_used, round2_status, time_to_finish, voice_cross_drift_hits`. Macht Museum-Clause, Repetition-Watch, Variation-Guard messbar. | Konsens | Codex+Claude (V13) | hoch |
| 4.2 | **Patch-Suggestion-Loop** (war v0.4.0 Phase-3): jede 10. Generierung schlägt einen SKILL.md-Patch oder Word-Pool-Patch vor (auf Basis der `kept`-Markierungen in field-notes.md), schreibt nach `lab/.../patches/` mit Review-Gate. Schließt die Erkenntnis-Schleife. | Synthese | Codex+Claude (V19) | mittel |

### Phase 5 — Run Planner (M, 3-4 Tage)

| # | Punkt | Klasse | Provenance | Priorität |
|---|-------|--------|------------|-----------|
| 5.1 | **Run Planner** als gemeinsame Schicht für Archetype-Selector und `--from-session` (NICHT als zwei lose Features, wie Codex es korrekt gesehen hat). Selector wählt Archetype aus Topic-Keywords (Fallback: Timestamp-Mod). `--from-session` liest `.agent-memory/session-summary.md` (oder Desktop-Equivalent) und schlägt 3 Topic-Kandidaten vor. | Synthese | Codex (D3) + Claude (V14+V15) | hoch |
| 5.2 | **`--dry-run`** für Single-Run zeigt Picker-Output (Archetype + Wort + Operator) ohne Generation. Hilft beim Debug der Variation-Guard und Run-Planner-Logik. | Ergänzung | Claude (V7/E4) | mittel |

### Phase 6 — Cross-Pollination + Kompakt-Modus (M, 2-3 Tage)

| # | Punkt | Klasse | Provenance | Priorität |
|---|-------|--------|------------|-----------|
| 6.1 | **`--chat --compact`**: Round 1+2 nur als `<details>`-Toggle, Round 3 als primäre Ebene. Reduziert Cognitive Load bei Review-Nutzung. | Konsens | Codex+Claude (V20) | mittel |
| 6.2 | **Round-2-Substanz-Check** als optionaler `--strict-cross-pollination`-Flag: semantischer Check (z.B. zweite Codex-Round oder LLM-Critique), ob counter/extend-Marker mit Substanz gefüllt sind, nicht nur quantitativ. | Ergänzung | Claude (V23) | mittel |
| 6.3 | 4. PO-Operator aktivieren („wishful thinking" aus `resources/po-operators.md:7-9`) als kontrolliertes Feldtest-Set. | Konsens | Codex+Claude (V11) | niedrig |

### Phase 7 — Visionär: GUI/Playground (L, optional)

| # | Punkt | Klasse | Provenance | Priorität |
|---|-------|--------|------------|-----------|
| 7.1 | **Single-File-HTML-Playground** (analog `playground` Skill): Topic eingeben, Archetype rollen oder wählen, Word/Operator sehen, Provokationen live streamen, Self-Flag-Checkboxes direkt im Browser, Output landet als File im Lab. Visuelle Schicht für die heute rein textuelle Mechanik. | Konsens (User-bestätigt) | Codex+Claude+User | später |

### Phase 8 — Visionär: Telegram-Bridge (L, optional, RISIKO)

| # | Punkt | Klasse | Provenance | Priorität |
|---|-------|--------|------------|-----------|
| 8.1 | **Telegram-Bridge** (V3 aus `references/roadmap.md:27-31`): Ductor-Integration, mobiler Trigger via Telegram-Bot. **RISIKO**: Auth/Input-Validation-Surface, externe Channels, Security-Audit als Vorbedingung. Nur sinnvoll, wenn der Skill produktiv genug genutzt wird, dass mobiler Zugang Wert hat. | Konsens (User-bestätigt) | Codex+Claude+User | später |

---

## Konflikt-Log

**Bewertungs-Formel**: Score = Impact − Risiko − (Aufwand/2). Bei R/A/I-Notation `R/A/I` ist `R` = Risiko (1-5, niedrig=sicher), `A` = Aufwand (1-5, niedrig=schnell), `I` = Impact (1-5, hoch=viel Effekt). Score ist nur eine Vorschau, kein Urteil — Entscheidungen sind User-bestätigt.

| # | Thema | Codex sagt | Claude sagt | Bewertung (R/A/I → Score) | Entscheidung |
|---|-------|-----------|-------------|----------------------------|--------------|
| K1 | Phase-1-Anchor: Vertrag oder Picker zuerst | Vertrag zuerst | Picker zuerst | Codex: 1/1/4 → 4−1−0.5=**2.5**; Claude: 2/3/5 → 5−2−1.5=**1.5** | **Codex' Linie. Vertrag in Phase 1, Picker in Phase 2.** Vertrag ist billig, niedriges Risiko, Voraussetzung für saubere Picker-Spezifikation. |
| K2 | Codex-Smoke-Test in Chat-Mode | „RISIKO, ausstehend" | „RISIKO, eigene Phase" | n/a | **Resolved**: User hat Test 2026-04-26 durchgeführt, lief sauber. Kein Phase-0-Prereq nötig. |
| K3 | field-notes.md pro-Projekt vs. global | implizit pro-Projekt | global unter `~/.claude/state/` | Codex: 2/2/2 → 2−2−1=**-1**; Claude: 3/3/4 → 4−3−1.5=**-0.5** | **Pro-Projekt belassen. Globaler Toggle als Spätphase.** |
| K4 | Stage-Magician-Archetype | unter Persona-Studio L | M-Feature nach Radagast-Watch | Beide: 3/3/2 → 2−3−1.5=**-2.5** | **Out of scope (Frage 5: nur GUI+Telegram).** |
| K5 | Multi-Provider-Routing | L, hohes Risiko | wenig Mehrwert | Beide: 4/5/2 → 2−4−2.5=**-4.5** | **Out of scope.** |
| K6 | Skill-Mesh-Pipeline | nicht erwähnt | L, Visionär | Claude: 3/5/4 → 4−3−2.5=**-1.5** | **Out of scope (Frage 5).** |
| K7 | docs/-Pflichtdateien | als Kontext-Lücke | als V6 Quick-Win | Beide: 1/1/2 → 2−1−0.5=**0.5** | **Beide drin, in Phase 1 als Quick-Win.** |
| K8 | 4. PO-Operator | inkrementell, Feldtest | inkrementell V11 | Beide: 2/1/2 → 2−2−0.5=**-0.5** | **Beide drin, in Phase 6 nach Vertragsbereinigung.** Negativer Score reflektiert: niedrige Dringlichkeit, aber Feldtest-Wert da. |

---

## Lücken (was beide übersehen haben — User-Input)

- **GUI/Playground** als Visionär ist gewollt (User-Frage 5) → in Plan als Phase 7
- **Telegram-Bridge** als Visionär ist gewollt (User-Frage 5) → in Plan als Phase 8
- **v0.4.0-Plan nicht weiterführen als Schuld**, sondern Lessons in Phase 4+5 absorbieren (User-Frage 3c)

---

## User-Entscheidungen (Auditierbarkeit)

Diese Entscheidungen wurden in der Klärungsphase des plan-merger Skills explizit getroffen und steuern die Plan-Struktur:

| # | Frage | Antwort | Wirkung im Plan |
|---|-------|---------|-----------------|
| F1 | Zielhorizont (Roadmap / Sprint / beides) | **(c) Beides** — Roadmap mit konkreten Phasen | 8-Phasen-Tabelle mit Status, plus Punkte-Liste pro Phase |
| F2 | Picker-Skript vs. Vertragsbereinigung als Anchor | **(c)** — Skill bewertet, User genehmigt | K1 mit R/A/I; Vertrag (Phase 1) gewinnt vor Picker (Phase 2) |
| F3 | v0.4.0-Plan-Schuld | **(c) absichtlich überspringen** — Lessons drin, neuer Plan ohne Schuldbegriff | v0.4.0-Inhalte in Phase 4+5 absorbiert, alter Plan-Status nicht referenziert |
| F4 | Codex-Smoke-Test | **(a) bereits gemacht, lief sauber** | K2 als „resolved 2026-04-26"; kein Phase-0-Prereq |
| F5 | Visionäre Items (was ist ernst gemeint?) | **GUI/Playground + Telegram-Bridge** | Phase 7+8; Multi-Provider, Skill-Mesh, Stage-Magician, Persona-Studio explizit out-of-scope |

---

## Annahmen

- **Picker-Skript-Sprache**: Python wird angenommen, weil das Repo Python-affin wirkt (`notebooklm-py` Geschwister-Plugin) und weil JSON-Output trivial ist. Bash wäre Alternative bei Hard-Constraint „kein Python im Plugin".
- **Eval-Suite-Runner**: angenommen wird ein eigenes kleines Python-Script (kein pytest-Setup), weil das Plugin keine Test-Infrastruktur hat. Bei Phase 3 entscheiden, ob pytest aufgesetzt werden soll oder Standalone-Runner reicht.
- **Telemetrie-Format**: angenommen JSONL als Default, weil append-safe und ohne Schema-Migration. SQLite nur, wenn zur Phase 4 die Aggregation komplex genug wird, dass JSONL nicht reicht.
- **Plan-Reihenfolge ist linear**: Phase 1-6 sequenziell. GUI (7) und Telegram (8) parallel zu späteren Phasen möglich, sobald Phase 1-3 stabil laufen.
- **Sprach-Policy**: alle neuen Code-Files in Englisch (gemäß CLAUDE.md auf Desktop), Plan-Doku in Deutsch wie hier.

---

## Offene Fragen (bewusst verschoben)

- **Nach Phase 3 entscheiden**: Eval-Suite mit pytest oder Standalone-Runner?
- **Nach Phase 4 entscheiden**: Aggregations-Format JSONL oder SQLite?
- **Nach Phase 5 entscheiden**: Soll der Run Planner auch die Wahl des PO-Operators beeinflussen, oder bleibt Operator-Wahl rein zufällig?
- **Vor Phase 7**: Soll GUI in den crazy-professor Plugin-Repo oder als separates `crazy-professor-playground` Plugin?
- **Vor Phase 8**: Telegram-Bridge nur lesend (Bot fragt, User antwortet) oder bidirektional (Bot kann auch User-Trigger empfangen)? Beeinflusst Auth-Aufwand massiv.

---

## Quell-Reports

- **Codex-Report**: erstellt 2026-04-26 via `codex:codex-rescue` Subagent (agentId a5e2b2aa97afdf72f), inline in Klärungs-Phase des plan-merger
- **Claude-Report**: erstellt 2026-04-26 via Claude-Subagent (agentId acf942e776cbd12a1), inline in Klärungs-Phase des plan-merger

Beide Reports waren die Rohdaten dieses Merges. Bei Unklarheit dort nachschauen.

---

## Commit-Message-Konvention

Für Phase-Commits dieses Plans empfohlen:

```
crazy-professor | Phase-{N}: {knapper-status}
```

Beispiele:
- `crazy-professor | Phase-1: Input-Vertrag vereinheitlicht (--chat ohne Topic abgelehnt)`
- `crazy-professor | Phase-2: Picker-Skript implementiert + field-notes-Schema im Repo`
- `crazy-professor | Phase-3: Linter-Trio aktiv, Eval-Suite mit 92% Pass-Rate`

So wird `git log` zum Handoff-Index, falls eine Phase auf mehrere Sessions verteilt werden muss.
