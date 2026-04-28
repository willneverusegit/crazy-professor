---
title: crazy-professor Chat-Mode Flow Specification
version: 0.11.0
status: in v0.10.0 (no flow change since v0.5.1; embedded version mirrors plugin version)
created: 2026-04-23
related_plan: docs/plans/2026-04-23-crazy-professor-v050-chat-mode-master-plan.md
---

# Chat-Mode Flow Specification (v0.5.0)

Diese Datei ist die autoritative Flow-Spezifikation fuer `--chat`. Alle
Implementierungs-Phasen (2-7) referenzieren hier. Aenderungen an diesem
Dokument brauchen einen Version-Bump.

## Aktivierung

```
Skill crazy-professor "<topic>" --chat
```

Semantik:
- `<topic>`: eine Zeile, identisch zu Single-Run.
- `--chat`: flaggt den neuen Flow. Ohne Flag lauft Single-Run wie bisher.
- `--chat --dry-run-round1`: nur Runde 1, keine Cross-Pollination, kein
  Codex-Call. Dient dem internen Testen einzelner Phasen.

## Call-Budget

Ein Chat-Run verbraucht **10 LLM-Calls im Idealfall**:

| Runde | Calls | Zweck |
|-------|-------|-------|
| 1 | 4 | Je ein Archetype-Call, 5 Provokationen je Archetype, parallel. |
| 2 | 4 | Je ein Archetype-Call mit 15 fremden Provokationen als Kontext, 3 Gegen/Extend-Provokationen. |
| 3 | 1 | Codex-Destillation (extern via `codex:codex-rescue`). |
| Summary | 1 | Main-Model verfasst User-facing Summary aus Codex-Output + Rohdaten. |

Total: **10 Calls pro Chat-Run.** Bei Codex-Ausfall: Fallback-Call durch
Claude-Destillation → 10 Calls bleiben.

SKILL.md-Dokumentation sprach von "~20 LLM calls per session" als
Warnung — unser Flow liegt mit 10 Calls deutlich darunter, weil wir
keine Debatte zwischen zwei Agenten laufen lassen (das war die
urspruengliche `tmux`-Annahme), sondern synchrone Runden.

## Runde 1: parallele Generation

**Input:** Topic, 4 Archetype-Prompt-Templates, stochastische Picks fuer
Provocation-Word und PO-Operator (identisch zu Single-Run, aber pro
Archetype ein eigener Pick).

**Picker-Regeln in Runde 1:**
- Pro Archetype: ein eigenes Wort, ein eigener Operator.
- Variation-Guard (field-notes letzte 10 Rows) gilt pro Archetype
  separat.
- Timestamp-Seed: Main-Run-Timestamp + Archetype-Index (0-3) als
  Sub-Sekunden-Offset, damit die 4 Archetypes nicht alle dasselbe Wort
  ziehen.

**Call-Struktur** (pro Archetype):
```
[Standard-System-Prompt aus Archetype-Template]
+ Override: "Produziere exakt 5 Provokationen, nicht 10."
+ Override: "Kein Adoption-Cost-Tag in dieser Runde."
+ Override: "Kein Next-Experiment-Pick."
+ Input: <topic>, <provocation_word>, <po_operator>
```

**Output pro Archetype:** 5 Provokationen, jeweils mit Anker zur
User-Infrastruktur. Format identisch zu Single-Run, aber gekuerzt.

**Parallelisierung:** Die 4 Archetype-Calls laufen parallel (gleiches
Message mit 4 Agent-Aufrufen, nach Claude-Code-Best-Practice).

**Abbruchbedingung Runde 1:** Wenn ≥ 2 von 4 Archetypes leere Outputs
oder Format-Verletzungen liefern → Flow bricht ab, fällt zurueck auf
Single-Run-Modus mit Hinweis im Output-File.

## Runde 2: Cross-Pollination

**Input:** die 20 Provokationen aus Runde 1 (4 Archetypes × 5).

**Call-Struktur** (pro Archetype):
```
[Standard-System-Prompt aus Archetype-Template]
+ Kontext: "Die anderen drei Archetypen haben zum selben Topic
  folgende Provokationen produziert: <15 Provokationen der 3 anderen>"
+ Aufgabe: "Produziere 3 Provokationen, die:
  - entweder eine Luecke in den 15 anderen benennen (counter:)
  - oder eine der 15 anderen aus deiner Stimme erweitern (extend:)
  Jede deiner Provokationen traegt am Zeilenende einen expliziten
  Marker: `counter: <ref>` oder `extend: <ref>`."
+ Override: "Bleib in deiner Stimme. Kein Archetype-Wechsel."
```

**Wichtig:** Die Archetypes sehen in Runde 2 explizit die anderen
Outputs — das ist die Quelle der Kreuzung. Der Archetype antwortet
nicht "der andere hatte Recht", sondern zieht aus seiner eigenen
Stimm-Lage heraus eine Gegen- oder Erweiterungs-Bewegung.

**Counter vs. Extend Semantik:**
- `counter: alchemist #3` = "Alchemist's Provokation #3 hat eine
  Luecke, ich fuelle sie aus meiner Stimme."
- `extend: radagast #2` = "Radagast's Provokation #2 ist richtig, ich
  ziehe sie in meine Stimm-Lage weiter."

Beide erlaubt. Kein Zwang zu 50/50. Der Archetype entscheidet per
Provokation.

**Parallelisierung:** wieder 4 parallele Calls.

**Abbruchbedingung Runde 2:** Wenn ≥ 2 von 4 Archetypes weniger als 2
Gegen/Extend-Provokationen liefern (sollte 3 sein) → Flow degradiert
auf **Variante A** (kein echter Dialog, nur 4×5 Provokationen aus
Runde 1 gehen in Runde 3). Chat-Output-File dokumentiert die
Degradierung explizit.

**Rationale:** Cross-Pollination ist das Herzstueck von Chat-Mode.
Wenn die Archetypes in Runde 2 schwaechen, ist das Tool nicht besser
als 4× Single-Run. Statt zu luegen, wird es als "dialog-nicht-zustande-
gekommen" dokumentiert und der User sieht das Symptom.

## Runde 3: Codex-Destillation

**Input:** Alle Provokationen aus Runde 1 (20 Stueck) + Runde 2 (max.
12 Stueck) = bis zu 32 Provokationen.

**Call-Struktur** (an Codex via `codex:codex-rescue`-Subagent):
```
Rolle: Destillator-Juror fuer crazy-professor Chat-Mode.

Kontext: 4 Archetypes haben zu einem Topic zusammen bis zu 32
Provokationen produziert. Deine Aufgabe: destilliere auf exakt 20
Ideen, **genau 5 pro Archetype**.

Eingaben:
- Topic: <topic>
- Runde 1 Outputs (5 pro Archetype, gelabelt):
  <jester 1-5> <librarian 1-5> <alchemist 1-5> <radagast 1-5>
- Runde 2 Outputs (bis zu 3 pro Archetype, gelabelt counter/extend):
  <jester r2 1-3> <librarian r2 1-3> ...

Kriterien pro Idee:
1. Wert: oeffnet neuer Arbeitsmodus?
2. Umsetzbarkeit: in 1-2h testbar / kleines Backlog-Artefakt?
3. Systemfit: passt zu Agentic-OS / Wiki ohne Architekturtheater?

Output-Format:
## Jester-5
1. <idee> — [cost: X] — anchor: Y — [score: W/U/S]
2. ...
## Librarian-5
...
## Alchemist-5
...
## Radagast-5
...

Regeln:
- Exakt 5 pro Archetype. Kein Umlagern zwischen Archetypen.
- Keine Stimm-Vermischung: eine Idee behaelt den Archetype, der sie
  produziert hat.
- Counter/Extend-Ideen aus Runde 2 sind gleich-gewichtet mit Runde-1-
  Ideen — der Marker `counter:`/`extend:` bleibt in der Output-Zeile
  erhalten zur Nachvollziehbarkeit.
- Wenn ein Archetype < 5 brauchbare Ideen produziert hat, schreibe
  das explizit in den Sektion-Header ("nur 3 brauchbare verfuegbar,
  2 gefuellt aus schwaecheren Kandidaten") — nicht kaschieren.

Zusaetzlich:
- Top-3 Cross-Pollination-Hits: welche counter/extend-Provokationen
  aus Runde 2 waren die wertvollsten?
- Ein konkretes Next-Experiment (analog zu Single-Run).
```

**Fallback wenn Codex nicht verfuegbar:** Claude-Destillation mit
identischem Prompt, aber Ausgabe-Header markiert als `distiller: claude
(codex-fallback)`.

## Output-Struktur

Pro Chat-Run eine Datei unter
`.agent-memory/lab/crazy-professor/chat/YYYY-MM-DD-HHMM-<topic-slug>.md`:

```markdown
---
skill: crazy-professor
mode: chat
version: 0.11.0
timestamp: <ISO>
topic: "<topic>"
archetypes: [jester, librarian, alchemist, radagast-brown]
rounds: 3
distiller: codex | claude-fallback
llm_calls: 10
round2_status: full | degraded | failed
---

# Chat: <topic>

**Mode:** chat | **Distiller:** <codex|claude>

> DIVERGENCE WARNING: ...

## Round 1 — Parallel Voices

### Jester (word: <w>, op: <op>)
1. ...
2. ...
...5 Stueck

### Librarian (word: <w>, op: <op>)
...

### Alchemist (word: <w>, op: <op>)
...

### Radagast (word: <w>, op: <op>)
...

## Round 2 — Cross-Pollination

### Jester (counter/extend)
1. counter: alchemist #3 — <idee>
...

### Librarian ...
### Alchemist ...
### Radagast ...

## Round 3 — Codex Distillation (Final 20)

### Jester-5
1. <idee> — [cost: ...] — anchor: ... — [score: W/U/S]
2. ...
5.

### Librarian-5 ...
### Alchemist-5 ...
### Radagast-5 ...

## Top-3 Cross-Pollination Hits
1. ...
2. ...
3. ...

## Next Experiment
<one concrete test>

## Self-Flag (for field-notes.md)
- [ ] kept
- [ ] round2-degraded (track if degradation was triggered)
- [ ] distiller-fallback (Codex was unavailable)
```

## Field-Notes-Integration

Chat-Runs landen im selben `field-notes.md` wie Single-Runs. Neue
Spalte `mode` in der Log-Tabelle (Wert: `single` | `chat`). Bei
Chat-Runs:

- `Archetype`-Spalte zeigt `all-4` statt einzelnem Archetype.
- `Word`-Spalte zeigt `multi` (die vier Woerter stehen im Output-File).
- `Operator`-Spalte zeigt `multi`.
- `Re-rolled`-Spalte zeigt Aggregat (`no` wenn kein Archetype re-gerollt
  hat, sonst Liste).
- `Review1-Votum`-Spalte gefuellt nach Review wie Single-Runs.

Die Museum-Clause-Counts (Total invocations) mischen Single + Chat.
Museum-Clause-Gate (Run 20 Review) betrachtet beide zusammen.

## Offene Fragen — Decision-Block fuer User

Vor Phase 2 muessen diese entschieden sein:

### F2: Runde-2-Modus (counter / extend / beides)

**Default:** beides erlaubt, jede Provokation selbst gelabelt.

**Alternativen:**
- Nur `counter:` → Archetype muss Luecken finden, kann nicht
  zustimmen-und-erweitern. Schaerfer, aber evtl. kuenstlich.
- Nur `extend:` → keine Gegenbewegung, nur Vertiefung. Milder, aber
  verliert die eigentliche Kreuzung.
- Beides + Pflicht 50/50 → gezwungen zu mindestens 1 Counter + 1
  Extend. Sichert Balance, aber verletzt Archetype-Freiheit.

**Empfehlung:** Default.

### F3: Codex-Budget-Akzeptanz

1 Codex-Call pro Chat-Run. Bei 5 Chat-Runs/Woche: ~20 Calls/Monat.
Akzeptabel, oder Claude-Destillation als permanenter Default mit
Codex nur als Optional-Upgrade?

**Empfehlung:** Codex als Default (entspricht v0.3.3-Blindtest-Protokoll).

### F4: Adoption-Cost-Tag in Runde 1/2?

**Default:** Kein Tag in Runde 1/2. Nur in Runde-3-Final-20er-Liste.

**Alternative:** Tag in allen Runden. Macht Kreuzungs-Kontext reicher,
aber belastet den Archetype-Prompt in Runde 1/2 mit Kosten-Denken, das
die Provokations-Scharfe daempft.

**Empfehlung:** Default (nur in Runde 3).

### F5: Runde-2-Abbruchbedingung

**Default:** Wenn ≥ 2 Archetypes < 2 Provokationen liefern → Variante A
(kein Runde-2-Output, direkt zu Codex mit nur Runde-1-Daten).

**Alternative:** Strenger (1 Archetype schwach → Abbruch) oder milder
(3 Archetypes schwach → Abbruch). Strenger schuetzt Qualitaet, milder
schuetzt Durchlauf-Quote.

**Empfehlung:** Default.

## Error-Handling

- **LLM-Call-Fehler Runde 1:** Retry 1× pro Archetype, dann mit
  `archetype-x: skipped` markieren. Wenn ≥ 2 skipped → Abbruch.
- **Codex-Fehler Runde 3:** Automatisch Claude-Fallback, markiert.
- **Output-File-Schreibfehler:** Throw. Kein Recovery — der Run ist
  verloren, aber Single-Run-Funktionalitaet bleibt intakt.
- **Topic-Parsing-Fehler:** Identisch zu Single-Run (Clarifying Question,
  keine Fabrication).

## Performance-Erwartung

- Runde 1: parallele 4 Calls, ~20-40s total.
- Runde 2: parallele 4 Calls, ~30-60s total.
- Runde 3: Codex-Call, ~60-120s (Codex braucht laenger als Claude).
- Summary + Write: ~5s.

**Total pro Chat-Run:** 2-4 Minuten. Single-Run liegt bei ~30s —
Chat-Mode ist 4-8× so teuer in Wall-Clock-Zeit, aber produziert 20
kuratierte Ideen statt 10 Roh-Provokationen.

## Was NICHT Teil von Chat-Mode v0.5.0 ist

- Kein `tmux`-Dialog. Kein Telegram-Bridge. Kein Live-Chat mit User
  zwischen den Runden.
- Keine Archetype-Wahl (alle 4 sind immer dabei).
- Keine Multi-Topic-Batches (ein Topic pro Run).
- Kein Auto-Schedule (User triggert manuell).
- Keine Model-Routing-Logik (Claude fuer Runde 1/2, Codex nur fuer
  Runde 3 — keine Modell-Mix-Optionen).

Diese sind dokumentiert als **v0.6.0+ Kandidaten**, nicht gebaut.

## Abnahme-Kriterien fuer Phase-1

- [x] Flow-Diagramm in Worten vollstaendig (3 Runden, Input/Output pro Runde).
- [x] Call-Budget dokumentiert.
- [x] Field-Notes-Integration spezifiziert.
- [x] Offene Fragen als Decision-Block markiert.
- [x] Error-Handling-Pfade beschrieben.
- [x] Out-of-Scope-Liste gepflegt.

Phase-1 ist **komplett** sobald User die 4 offenen Fragen (F2-F5)
entschieden hat. Dann Phase-2 Start.

## Decisions 2026-04-23 (F2-F5)

- F2 Runde-2-Modus: **Default** (beides erlaubt, Archetype waehlt selbst counter: oder extend:).
- F3 Destillator: **Default** (Codex primaer, Claude-Fallback bei Nichtverfuegbarkeit).
- F4 Adoption-Cost-Tag Runde 1/2: **Default** (nein, nur Runde 3 Final-20er-Liste).
- F5 Runde-2-Abbruchbedingung: **Default** (>=2 Archetypes schwach → Variante A Degradierung, nicht Abbruch).

Phase-1 **komplett** 2026-04-23.
