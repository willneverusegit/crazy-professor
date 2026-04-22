---
title: crazy-professor — Usage Patterns
status: user-heuristic, not field-tested
origin: User (domes), 2026-04-22, post-v0.3.0-scaffold
scope: meta-layer; not part of the single-shot skill mechanics
---

# Crazy Professor — Usage Patterns

Dieses Dokument ist die **Meta-Ebene** ueber dem eigentlichen Skill. Es ist
eine empfohlene Heuristik des Users, keine Skill-Regel. Der Skill selbst
ist und bleibt ein Single-Shot-Randomizer: `mod-4` waehlt einen Archetype,
ein Wort, einen Operator, fertig. Die hier beschriebenen Muster gelten
nur, wenn du den Skill **bewusst gerichtet** einsetzt -- z.B. indem du
einen Archetype explizit ansagst oder die unten beschriebene Sequenz
nacheinander ausloest.

**Status:** Entstanden nach dem v0.3.0-Scaffold, bevor Radagast produktiv
geschaltet ist. Noch keine Feldtest-Evidenz dafuer, dass diese Heuristik
mehr Keeper pro Thema produziert als vier unabhaengige Solo-Runs. Genau
das ist der offene Pruefpunkt.

---

## Funktion der vier Archetypes (User-Lesart)

Die vier Stimmen koennen nicht nur nach Ton, sondern nach **Funktion**
sortiert werden. Diese Zuordnung ist nicht in den Prompt-Templates selbst
kodiert -- sie ist eine User-Lesart der Templates.

| Phase | Archetype | Wann einsetzen |
|---|---|---|
| **Exploration (Regelbruch)** | `first-principles-jester` | Wenn ein Thema zu regelhaft, zu axiomatisch, zu "so-macht-man-das" wirkt. Der Jester zerlegt Konventionen in ihre Bausteine und erklaert einen Baustein illegal. |
| **Exploration (Querfeld)** | `labyrinth-librarian` | Wenn ein Thema zu fachfixiert ist und fremde Mechanismen gebraucht werden. Der Librarian holt Loesungen aus Mykologie, Ornithologie, Hydrologie zurueck und uebersetzt sie mit Fremdheits-Rest. |
| **Reframing / Humanisierung** | `radagast-brown` | Wenn ein Thema zu kalt, zu mechanisch, zu funktional geworden ist. Radagast behandelt Akteure als Lebewesen, fragt nach Pflege, Futter, Zeit -- und verteidigt den Teil des Systems, der nuetzlich-nutzlos bleiben darf. |
| **Umbau / Umsetzung** | `systems-alchemist` | Wenn aus einer Beobachtung eine strukturelle Veraenderung entstehen soll. Der Alchemist kartografiert Input/Output/Reststoff/Wand und verlegt ein Element im Flussdiagramm. |

---

## Die Vier-Phasen-Sequenz (empfohlen, nicht vorgeschrieben)

Wenn du ein Thema in einem Zug gruendlich bearbeiten willst -- nicht
destabilisieren, sondern tatsaechlich bewegen -- empfiehlt sich folgende
Reihenfolge:

```
Jester  →  Librarian  →  Alchemist  →  Radagast
```

Die Logik dahinter:

1. **Jester zuerst:** Regeln aufbrechen, Bausteine sichtbar machen. Ohne
   diesen Schritt buersten die folgenden drei Archetypes gegen noch-
   nicht-hinterfragte Axiome.
2. **Librarian als zweiten:** Jetzt, wo die Bausteine nackt sind, kommen
   Mechanismen aus fremden Feldern dazu. Der Jester hat ein Loch gerissen,
   der Librarian fuellt es mit unerwartetem Material.
3. **Alchemist als dritten:** Aus den neu moeglichen Kombinationen wird
   ein Systemumbau abgeleitet. Wer Alchemist zuerst laufen laesst, baut
   oft am alten Flussdiagramm weiter; hier arbeitet er am schon-gelockerten.
4. **Radagast zum Schluss:** Nachdem drei utilitaere Stimmen durch sind,
   prueft Radagast, was in der entstehenden Umstrukturierung **geschuetzt**
   werden sollte. Er ist der einzige Archetype, der gegen Optimierung
   verteidigen kann -- und das funktioniert nur **nach** der Optimierung,
   nicht davor.

### Wann die Sequenz sinnvoll ist

- Thema ist komplex genug, dass vier Perspektiven Mehrwert bringen (nicht
  bloss redundante Variationen).
- Du willst am Ende des Durchlaufs eine konkrete Handlung oder Entscheidung
  haben, nicht nur 10 Provokationen zum Stoebern.
- Du hast mindestens 30 Minuten Zeit und Bereitschaft, alle vier Outputs
  zu lesen.

### Wann die Sequenz **nicht** sinnvoll ist

- Thema ist schmal oder klein (dann reicht Single-Shot).
- Du willst Zufalls-Divergenz -- genau das leistet mod-4 besser.
- Du brauchst nur eine bestimmte Phase (dann gezielt diesen Archetype).

---

## Varianten

- **Drei-Phasen-Sequenz ohne Radagast:** Jester → Librarian → Alchemist.
  Geeignet, wenn das Thema bereits ein "kaltes" Optimierungsproblem ist
  und der Humanisierungs-Schritt unpassend waere (z.B. reine Build-
  Reihenfolge eines Deploy-Skripts).
- **Zwei-Phasen Reframe:** Alchemist → Radagast. Wenn du bereits ein
  System-Umbau-Konzept hast und nur noch pruefen willst, was nicht tot-
  optimiert werden darf.
- **Nur-Radagast:** Fuer Themen, die sich bereits zu mechanisch anfuehlen
  und keine Dekonstruktion mehr brauchen -- nur eine Wiederbelebung.

---

## Pruefpunkte fuer den Feldtest

Die obige Heuristik ist eine **Hypothese**, nicht eine bewiesene Methode.
Sie wird erst dann Skill-Regel, wenn sie im Feld Evidenz sammelt. Konkrete
Pruefpunkte:

1. **Drei Vier-Phasen-Sequenzen** ueber unterschiedliche Themen. Notiere
   im field-notes.md: welche Phase hat die meisten Keeper produziert,
   welche die wenigsten, ob die Reihenfolge Unterschied gemacht hat.
2. **Einen Kontrollversuch:** Dasselbe Thema einmal als Sequenz, einmal
   als vier Solo-Runs. Wurden in der Sequenz andere Provokationen
   erzeugt als in den Solos? Oder ist Keeper-Dichte vergleichbar?
3. **Zeit-vs-Ertrag:** Sequenz kostet viermal so viel Zeit wie Solo. Ist
   der Zugewinn an Keepern proportional?

Wenn nach drei bis fuenf Sequenzen klar wird, dass sie systematisch
mehr Keeper oder bessere Keeper produzieren, dann ist V1.2 ein
`--sequence`-Modus im Skill wert. Solange das nicht belegt ist, bleibt
die Sequenz User-Playbook.

---

## Beziehung zur Skill-Mechanik

- Dieses Dokument aendert **nichts** an SKILL.md, an den Templates, an der
  mod-4-Mechanik oder an der Museum-Clause.
- Der Skill bleibt **Single-Shot**. Jeder Aufruf picked einen Archetype
  per Zufall, produziert 10 Provokationen, benennt ein Experiment.
- Wenn du die Sequenz manuell ausloest, sind das vier voneinander
  unabhaengige Skill-Aufrufe -- die Kette existiert nur in deinem Kopf
  und optional in deinem Notizdokument.
- Die Museum-Clause zaehlt weiterhin pro Invocation, nicht pro Sequenz.

---

## Changelog dieses Dokuments

- **2026-04-22:** Initial-Eintrag nach v0.3.0-Scaffold, vor Review 1 und
  vor Radagasts produktivem Einsatz. Heuristik stammt vom User, nicht
  feldgetestet.
