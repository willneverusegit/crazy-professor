---
title: Chat-Mode Runde-1 Prompt-Wrapper
purpose: Wird um den Standard-Archetype-Prompt herum gelegt, wenn Chat-Mode Runde 1 laeuft.
applies_to: [first-principles-jester, labyrinth-librarian, systems-alchemist, radagast-brown]
version: 0.5.1
---

# Runde-1 Wrapper (Chat-Mode)

In Runde 1 von Chat-Mode produziert jeder Archetype unabhaengig. Dieser
Wrapper wird an den Standard-Archetype-System-Prompt ANGEHAENGT (nicht
ersetzt), damit die Stimm-Regeln des Archetypes intakt bleiben.

## Overrides fuer Runde 1

```
## CHAT-MODE RUNDE 1 — OVERRIDES

Du laeufst in Chat-Mode Runde 1. Drei weitere Archetypen produzieren
parallel dieselbe Aufgabe. Du siehst sie nicht.

Count: Produziere exakt **5 Provokationen**, nicht 10.

Kein Cost-Tag: Verzichte in Runde 1 auf den `[cost: ...]`-Marker. Er
wird in Runde 3 beim Destillations-Schritt angelegt.

Kein Next-Experiment-Pick: Runde 1 endet mit der 5. Provokation. Kein
Auswaehlen einer Provokation als Experiment. Das passiert spaeter am
Gesamt-Output.

Kein Self-Flag-Block: Runde 1 schreibt keine Self-Flag-Checkboxes.

Format pro Provokation (wie Single-Run, aber ohne cost-Tag):
<provocation text> — anchor: <one-phrase link to user infrastructure>

Deine Stimm-Regeln (Archetype-Template oben) bleiben unveraendert. Die
5 Provokationen muessen dieselbe Stimm-Disziplin halten wie in einem
Single-Run mit 10 Provokationen — nicht weicher, nicht schaerfer, nur
weniger.

Der Output dieser Runde geht spaeter an die drei anderen Archetypen
als Kontext fuer Runde 2, und an einen Codex-Destillator fuer Runde 3.
Schreibe so, dass deine Provokationen von einem fremden Leser in 5
Zeilen erfasst werden koennen — kein privates Vokabular, keine
internen Referenzen ohne Begruendung.
```

## Wie wird der Wrapper angewendet

Main-Model baut den finalen System-Prompt pro Archetype-Call so:

```
[Standard-Archetype-Template-Inhalt, unveraendert]
[Leerzeile]
[Inhalt dieses Wrappers, Override-Block zwischen den ``` Zeichen]
```

Dann die User-Message:

```
Topic: <topic>
Provocation Word: <word>
PO-Operator: <operator>
```

Bei Radagast-Calls: zusaetzlich die Activation-Amendments aus
`radagast-brown.md` bleiben aktiv (strikte Pflicht-Vokabel-Regel,
`[opt-care]`-Marker fuer Schemas, max. 1 Ordner pro Run — letzteres
gilt trotz reduzierter Provokations-Zahl weiterhin).

## Picker-Parameter fuer Runde 1

Die stochastischen Picks (Wort + Operator) werden pro Archetype
separat gezogen, mit Timestamp-Offset um Kollision zu vermeiden:

- Archetype 0 (jester): Sekunde = main_seed
- Archetype 1 (librarian): Sekunde = main_seed + 1
- Archetype 2 (alchemist): Sekunde = main_seed + 2
- Archetype 3 (radagast): Sekunde = main_seed + 3

Variation-Guard (field-notes letzte 10 Rows) gilt pro Archetype eigen:
ein Wort das bei Jester schon gezogen wurde, blockt nicht den
Librarian. Aber innerhalb desselben Runs duerfen sich die 4 Woerter
nicht wiederholen — falls mod die gleichen Woerter zieht, zweites
Archetype bekommt Re-Roll (loggt `re-rolled: intra-chat`).

## Abnahme-Kriterien fuer Phase 2

- [x] Wrapper-Text fertig (dieses File).
- [x] Override-Semantik dokumentiert (Count, kein Tag, kein Experiment, kein Flag).
- [x] Picker-Regeln fuer Parallel-Gen spezifiziert.
- [x] Activation-Amendments fuer Radagast bleiben aktiv.
