---
title: Chat-Mode Runde-3 Codex-Destillator Prompt
purpose: Codex bekommt alle Runde-1- und Runde-2-Provokationen und destilliert auf exakt 20 Ideen, 5 pro Archetype.
version: 0.6.0
---

# Codex-Destillator Prompt (Runde 3)

Dieses File enthaelt den Prompt, den Main-Model an `codex:codex-rescue`
schickt, um die finale 20er-Liste zu erzeugen. Der Prompt ist so
geschrieben, dass er von Codex ohne Claude-Code-Kontext verstanden
werden kann.

## Versand an Codex

```
Rolle: Du bist Destillator-Juror fuer den crazy-professor Chat-Mode.
4 Archetypes (first-principles-jester, labyrinth-librarian,
systems-alchemist, radagast-brown) haben zu einem Topic zusammen bis
zu 32 Provokationen produziert. Deine Aufgabe: destilliere auf
**exakt 20 Ideen**, **genau 5 pro Archetype**. Nicht mehr, nicht
weniger.

---

Topic: <topic>

Runde 1 Outputs (5 pro Archetype):

### Jester (word: <word>, operator: <op>)
1. <provocation> — anchor: <link>
2. ...
5.

### Librarian (word: <word>, operator: <op>)
1. ...
5.

### Alchemist (word: <word>, operator: <op>)
1. ...
5.

### Radagast (word: <word>, operator: <op>)
1. ...
5.

Runde 2 Outputs (Cross-Pollination, bis zu 3 pro Archetype,
counter/extend gelabelt):

### Jester Runde 2
counter: alchemist #3 — <provocation> — anchor: <link>
extend: radagast #2 — <provocation> — anchor: <link>
...

### Librarian Runde 2
...

### Alchemist Runde 2
...

### Radagast Runde 2
...

---

Bewertungs-Rubrik (pro Idee, 1-5 Skala):

1. **Wert (W)**: oeffnet die Provokation einen neuen Arbeitsmodus,
   oder ist sie eine Near-Variation des bereits bekannten?
2. **Umsetzbarkeit (U)**: in 1-2 Stunden testbar oder als kleines
   Backlog-Artefakt materialisierbar?
3. **Systemfit (S)**: passt zu Agentic-OS / Claude Code / Wiki-
   Workflow ohne Architekturtheater?

Zusaetzlich: Adoption-Cost-Tag pro Idee:
- `low` = neue Datei, neuer Frontmatter-Key, neues Script <50 Zeilen.
- `medium` = bestehende Struktur erweitert.
- `high` = Architektur-Eingriff, mehrere Plugins betroffen.
- `system-break` = greift Grundfunktion an.

U-Skala hart kalibrieren:
- U=5: in <15 Minuten mit einem einzigen Shell-Befehl oder einer
  einzelnen Datei-/Notiz-Aktion testbar.
- U=4: in <1 Stunde testbar, ohne Workflow-, Template- oder
  Skill-Aenderung.
- U=3: braucht kleine Workflow- oder Template-Arbeit.
- U=2: braucht Skill-Aenderung oder mehrere koordinierte Dateien.
- U=1: braucht Architektur-Aenderung oder mehrere Plugins.

Output-Format (Markdown):

## Final 20 — Codex Distillation

### Jester-5
1. <idee> — [cost: X] — anchor: Y — [score: W=n U=n S=n]
2. ...
5. ...

### Librarian-5
1. ...
5. ...

### Alchemist-5
1. ...
5. ...

### Radagast-5
1. ...
5. ...

## Top-3 Cross-Pollination Hits

Nenne die drei wertvollsten counter/extend-Provokationen aus Runde 2
mit kurzer Begruendung, warum die Kreuzung substantielle neue Einsicht
brachte.

1. <ref z.B. "jester counter: alchemist #4"> — <1 Satz Begruendung>
2. ...
3. ...

## Next Experiment (eine, nur)

Nenne die EINE Idee aus den 20, die in der naechsten Stunde mit
Tools des Users testbar ist. Format analog Single-Run: konkrete
Handlungen, beobachtbares Kriterium, was als "war es wert" zaehlt.

Provocation-Nummer: <Archetype-Name #n, z.B. "Librarian-5 #2">

<ein Absatz: Test-Beschreibung>

---

Regeln fuer die Destillation:

1. **Exakt 5 pro Archetype.** Auch wenn Alchemist 8 brauchbare Ideen
   hat und Radagast 3 — jeder Archetype bekommt genau 5. Wenn ein
   Archetype weniger als 5 brauchbare Ideen hatte, fuelle mit den
   naechst-staerksten Kandidaten auf und schreibe im Sektions-Header:
   "Hinweis: nur <n> klar starke Ideen verfuegbar, <5-n> schwaechere
   Kandidaten ergaenzt."

2. **Kein Archetype-Umlagern.** Eine Idee bleibt bei dem Archetype,
   der sie produziert hat. Eine Counter-Provokation aus Runde 2, die
   der Jester auf einen Alchemist-Output geschrieben hat, landet in
   **Jester-5**, nicht in Alchemist-5. Der Zielmarker
   (`counter: alchemist #3`) bleibt aber in der Output-Zeile erhalten.

3. **Scoring transparent.** Jede der 20 Ideen hat `[score: W=n U=n S=n]`
   mit Zahlen 1-5. Kein Gesamtscore — der User soll die drei Achsen
   einzeln sehen.

4. **Cost-Tag ehrlich.** Nicht kuenstlich auf `low` druecken. Wenn
   eine Idee `system-break` ist, sag es. Die Verteilung der Tags ueber
   die 20 Ideen ist diagnostisch — rein `low` deutet auf zu zahmes
   Topic oder schwache Provokationen hin.

5. **Counter-/Extend-Marker behalten.** Wenn eine Runde-2-Provokation
   in die Final-20 wandert, behaelt sie ihren Marker in der Output-
   Zeile: `counter: alchemist #3 — <idee> — ...`.

6. **Kein Rewriting.** Wenn du eine Idee so gut findest, wie sie ist,
   uebernimm sie woertlich. Kein Stil-Glaetten, kein Umformulieren,
   kein "Verbessern". Die Stimme des Archetypes ist wertvoll in der
   Rohform. Nur wenn eine Provokation unverstaendlich oder abgebrochen
   ist, darfst du sie aussortieren (nicht rewriten).

7. **Top-3 Cross-Pollination-Hits muessen aus Runde 2 kommen.** Keine
   Ideen aus Runde 1 in diesem Block. Wenn Runde 2 degradiert war
   (siehe `round2_status: degraded` im Frontmatter des Inputs),
   schreibe: "Keine Cross-Pollination-Hits verfuegbar, Runde 2
   degradiert."

8. **Next Experiment: klein, testbar, reversibel.** Keine
   Architekturarbeit. Kein Experiment, das mehrere Sessions oder
   einen Sprint braucht. Der Test muss in der naechsten Stunde
   beginnen und in unter einem Tag ablaufen.

---

Rueckgabe-Format:

Schreibe dein komplettes Ergebnis als direkte Text-Antwort im Chat.
Schreibe KEINE Datei. Erzeuge KEIN Scratch-File. Bereite KEIN
Input-File vor. Antworte NICHT nur mit einem Pfad. Der aufrufende
Agent nimmt deine Text-Antwort wortwoertlich und fuegt sie in sein
Output-File ein. Wenn du eine Datei schreibst oder nur einen Pfad
zurueckgibst, gilt der Distiller-Run als fehlgeschlagen.

Wenn du die 20er-Liste fertig hast, schreibe NUR das Markdown-Ergebnis
zurueck. Kein Prolog, kein Meta-Kommentar, keine Bitte um Feedback.
Der Main-Flow nimmt deinen Output und packt ihn direkt ins
Chat-Output-File unter der Sektion "Round 3 — Codex Distillation".
```

## Fallback: Claude-Destillation

Wenn Codex nicht verfuegbar ist (Subagent-Timeout, Sandbox-Fehler,
Rate-Limit), uebernimmt Main-Model selbst die Destillation mit
IDENTISCHEM Prompt wie oben (ohne "Rolle: Du bist Codex..." Zeile).

Das Chat-Output-Frontmatter markiert das:

```
distiller: claude (codex-fallback)
distiller_reason: "codex subagent returned error <xyz>"
```

Das ist kein Qualitaets-Downgrade-Urteil — Claude kann die Rubrik
gleich gut anwenden. Aber es ist transparent, damit der User weiss,
dass die externe Stimme fehlte.

## Invocation

Main-Model spawnt den Codex-Call via `codex:codex-rescue`-Subagent
(analog zum Radagast-Blindtest-Protokoll vom 2026-04-23), run_in_
background = false (Runde 3 muss fertig sein bevor Summary entsteht),
description = "Chat-Mode distillation: <topic-slug>".

Bei Codex-Return: Main-Model parst das Markdown, validiert die
Struktur (4 Sektionen × 5 Ideen, Cross-Pollination-Block, Next-
Experiment), und fuegt es ins Output-File ein.

Bei Struktur-Fehler: einmal re-invoke mit Hinweis "Deine vorherige
Antwort hatte Format-Fehler: <spezifischer Hinweis>. Korrigiere nach
Spec." Wenn auch das fehlschlaegt → Claude-Fallback.

Wenn Codex nur einen Dateipfad, eine "prepared input"-Meldung oder
ein Scratch-Artefakt statt direktem Markdown-Text liefert, zaehlt das
als Struktur-Fehler. Der Retry wiederholt explizit: keine Datei, keine
Pfad-Antwort, nur direkte Markdown-Textantwort.

## Abnahme-Kriterien fuer Phase 4

- [x] Codex-Prompt selbst-enthalten (verstaendlich ohne Claude-Code-Kontext).
- [x] Rubrik (Wert/Umsetzbarkeit/Systemfit) explizit.
- [x] 5-pro-Archetype-Regel als harte Regel (nicht verhandelbar).
- [x] Counter/Extend-Marker bleiben beim Umzug erhalten.
- [x] Fallback-Pfad zu Claude beschrieben.
- [x] Struktur-Validierung + Single-Retry dokumentiert.
