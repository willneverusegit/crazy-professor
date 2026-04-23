---
title: crazy-professor v0.5.0 Chat-Mode Master-Plan
project_shortname: cp-chat
created: 2026-04-23
status: active
origin: SKILL.md "V2 Extensions" section + user decision 2026-04-23
source_decisions:
  - User wants destillation layer on top of single-runs (not replacement)
  - User wants 20 ideas, 5 per archetype, as hard rule
  - Museum-gate passed 2026-04-23, Radagast activated (v0.3.3)
  - Review 1 rubric (Wert/Umsetzbarkeit/Systemfit) established
supersedes_scope: none
relation_to_v040: v0.4.0 plan (archetype-selector, topic-feeder, output-as-patch) stays independent — these phases are orthogonal to chat-mode and can ship in either order. Current plan assumes v0.5.0 ships AFTER v0.4.0 but can ship before if user reorders.
---

# crazy-professor v0.5.0 — Chat-Mode Master-Plan

## Ausgangsdiagnose

Der crazy-professor produziert in v0.3.3 **einen Archetype pro Run, 10 Provokationen pro Output**. Das Museum-Gate ist gehalten (Runs 1-10, 4 kept + 5 conditional + 1 backlog). Review 1 hat aber eine strukturelle Schwäche offengelegt:

- Single-Runs sind **breit aber nicht tief kreuzend**: Jester-Zerlegung + Librarian-Analogie + Alchemist-Flow + Radagast-Pflege sehen denselben Topic nie *gemeinsam*.
- Der User empfindet einzelne Jester-Runs als "zu viel System zerstören", Radagast-Runs als "zu schön aber nicht anschlussfähig" — die Extrempole sind im V1-Setup ungefiltert.
- Die Destillations-Achse fehlt: aus 40+ Ideen (4 Archetypes × 10 Provokationen) gibt es keinen kuratierten 20er-Output, der überwiegend umsetzbar ist.
- Codex-Juror-Verfahren (Blindtest 2026-04-23) hat gezeigt: externe Bewertung nach Rubrik funktioniert zuverlässig und schneller als User-Review.

Diese vier Befunde haengen kausal zusammen: fehlende Kreuzung → ungefilterte Extreme → keine Destillation → User muss manuell kuratieren. v0.5.0 schliesst diese Schleife durch einen Chat-Mode, der 4 Stimmen dialogisieren lässt und am Ende eine Codex-destillierte 20er-Liste liefert.

## Entschiedene Parameter (2026-04-23, nicht neu verhandeln)

1. **Architektur:** 3-Runden-Dialog (Variante B aus Design-Gespräch). Runde 1 = jeder Archetype 5 Provokationen. Runde 2 = jeder Archetype liest die 15 anderen und schreibt 3 Gegen-Provokationen. Runde 3 = Codex-Destillation.
2. **Destillator:** Codex (externe Stimme, analog zum Radagast-Blindtest-Jurorenverfahren).
3. **Final-Output:** streng 5 Ideen pro Archetype = 20 Ideen. Keine Qualitätsbasierte Schief-Verteilung.
4. **Output-Format:** nur Chat-Datei, keine parallelen V1-Runs.
5. **Trigger:** Argument am bestehenden Skill, `/crazy "topic" --chat`.
6. **Field-Notes:** gemeinsam mit Single-Runs in `field-notes.md`, Marker `mode: chat`.

## Phasen-Tabelle

| Phase | Ziel | Output | Status |
|-------|------|--------|--------|
| Phase-1 | Chat-Mode Flow-Spezifikation. 3-Runden-Ablauf dokumentieren, LLM-Call-Budget, Abbruchbedingungen, Error-Handling. | `docs/chat-mode-flow.md` im Plugin-Repo | ✅ (2026-04-23, F2-F5 Defaults bestaetigt) |
| Phase-2 | Runde-1-Implementierung. 4 parallele Archetype-Gens (5 Provokationen je Archetype, nicht 10). Bestehende Prompt-Templates wiederverwenden, Count im System-Prompt reduzieren. | `skills/crazy-professor/prompt-templates/chat-round-1-wrapper.md` | ✅ (2026-04-23) |
| Phase-3 | Runde-2-Implementierung. Cross-Pollination: jeder Archetype bekommt die 15 Provokationen der anderen drei als Kontext, produziert 3 Gegen-Provokationen. Neue Prompt-Template-Sektion in jedem der 4 Archetype-Templates. | `skills/crazy-professor/prompt-templates/chat-round-2-wrapper.md` | ✅ (2026-04-23) |
| Phase-4 | Runde-3 Codex-Destillation. Codex-Juror-Prompt nach Rubrik (Wert/Umsetzbarkeit/Systemfit) + 5-pro-Archetype-Pflicht. Fallback wenn Codex nicht verfügbar (Claude-Destillation als Ersatz, markiert). | `skills/crazy-professor/prompt-templates/chat-curator.md` | ✅ (2026-04-23) |
| Phase-5 | Output-Template für Chat-Mode. 4 Sektionen (je Archetype), Cross-Pollination-Block, finale 20er-Liste mit Rubrik-Scores, Adoption-Cost-Tags. | `skills/crazy-professor/resources/chat-output-template.md` | ✅ (2026-04-23) |
| Phase-6 | SKILL.md Integration. `--chat`-Argument parsen, Sub-Flow dispatchen, Field-Notes mit `mode: chat` ergänzen. Version-Bump v0.3.3 → v0.5.0 (v0.4.0 bleibt für andere Phasen reserviert) oder nach Entscheidung rename. | SKILL.md Patch + Frontmatter v0.5.0 + File-Layout aktualisiert, Cache/Repo synced | ✅ (2026-04-23) |
| Phase-7 | Erster End-to-End-Chat-Run als Smoke-Test. Topic: User-vorgeschlagenes echtes Thema. Validierung: 20 Ideen mit 5 pro Archetype, kein Format-Bruch, Codex-Call erfolgreich. | `.agent-memory/lab/crazy-professor/chat/2026-04-23-1200-wiki-synthese-pipeline.md` | ✅ (2026-04-23, mit Codex-Fallback zu Claude) |
| Phase-8 | User-Review Phase-7 + Rollback-Kriterium prüfen. Wenn Output < 12 von 20 Ideen rubrik-tauglich: Chat-Mode bleibt, aber Curator-Prompt wird überarbeitet. Wenn Output strukturell bricht: Rollback zu v0.3.3, Chat-Mode pausiert. | Review-Block in field-notes.md + Entscheidung | ✅ (2026-04-23, accepted, v0.5.0 released with Known Issue: Codex prompt fix for v0.5.1) |

## Commit-Message-Konvention

Jeder Phase-Abschluss-Commit folgt: `cp-chat | Phase-{N}: {status}` z.B. `cp-chat | Phase-4: codex-curator prompt + fallback eingebaut`.

## Offene Fragen (bewusst verschoben)

1. ~~v0.4.0 vs. v0.5.0 Reihenfolge.~~ **Entschieden 2026-04-23:** v0.4.0-Plan bleibt unberuehrt (archetype-selector, topic-feeder, output-as-patch). Chat-Mode ist v0.5.0. User-Reihenfolge: **Chat-Mode v0.5.0 zuerst bauen, dann Top-Keeper-Artefakte materialisieren, dann erst v0.4.0**. Die Versionsnummern bleiben wie dokumentiert, die Implementations-Reihenfolge springt v0.3.3 → v0.5.0 → (irgendwann) v0.4.0. Das ist ungewoehnlich aber sauber, weil v0.4.0-Phasen keinen blockierenden Einfluss auf v0.5.0 haben.
2. **Runde-2-Modell.** Soll der Archetype in Runde 2 nur Gegen-Provokationen schreiben (explizit anti), oder darf er auch zustimmen-und-erweitern? Default: beides erlaubt, aber explizit gelabelt `counter:` / `extend:`.
3. **Codex-Budget.** Wenn Codex pro Chat-Run 1 Call kostet (Destillation), ist das 1 Rescue-Call pro Run. Bei täglichem Chat-Mode-Einsatz: 30 Codex-Calls/Monat. Akzeptabel? Alternative: Claude-Destillation mit expliziter Rubrik-Simulation (billiger, aber bias zu Claude-eigener Denkweise). Default: Codex. Fallback wenn nicht verfügbar: Claude, markiert.
4. **Adoption-Cost-Tag in Chat-Output.** Bleibt pro Provokation oder nur in der finalen 20er-Liste? Default: nur in 20er-Liste (in Runde 1/2 ohne Tag, damit Archetype nicht im Stimm-Prompt von Kosten-Kategorien abgelenkt wird).
5. **Abbruchbedingung Runde 2.** Was wenn Archetype X in Runde 2 nur 0-2 Gegen-Provokationen produziert statt 3? Default: Mindestens 2 von 3 Archetypen müssen 3 liefern, sonst bricht der Flow ab und fällt zurück auf Variante A (4× V1, kein Dialog).

## Museum-Klausel für Chat-Mode

Chat-Mode unterliegt einer **eigenen 5-Run-Probe** nach demselben Muster wie V1:

- Nach 5 Chat-Runs: Review durch User + Codex-Juror.
- Erforderliche Keeper: ≥ 3 der 5 Chat-Runs müssen Final-20er-Listen produziert haben, bei denen mindestens 10 Ideen nach Rubrik `kept` oder `conditional` sind.
- Fail-Kriterium: wenn 3+ Chat-Runs strukturell brechen (Format, Codex-Call, 5-pro-Archetype-Regel) oder < 10 tragfähige Ideen, geht Chat-Mode ins Museum (`.agent-memory/museum/crazy-professor-chat/`).

## Rollback-Strategie

Chat-Mode ist ein **neues Flag** am bestehenden Skill, nicht eine Ersetzung. Rollback bei Fehlschlag:

- Phase-1 bis Phase-5 Fehlschlag: nur Plan-Dateien rückbauen, keine Skill-Änderung.
- Phase-6 Fehlschlag: SKILL.md Patch per git revert entfernen, `--chat` wird ungültiges Argument, Single-Runs laufen normal weiter.
- Phase-7 Fehlschlag: Chat-Mode-Code bleibt, wird aber `disabled: true` im Frontmatter markiert. Keine hartcodierte Entfernung.

Rollback ist reversibel ohne Verlust von V1-Funktionalität.

## Phase-8 Review (2026-04-23, user)

**Release decision: accepted, v0.5.0 ships.**

Format: readable and navigable. Round 1/2 are long but useful as audit trail; Round 3 + Top-3 + Next Experiment are strong enough for review use. Leicht übervoll, aber im guten Bereich; Appendix-Modus für spätere Versionen denkbar. Scoring-Werte teilweise zu großzügig (mehrere U=5 bei Ideen, die Workflow-/Template-Arbeit brauchen) — kein Blocker, aber Lehre für künftige Distiller-Prompts: härtere Skala.

Rubric: passed. 8-10 echte Keeper-Kandidaten, 4 sofort umsetzbar. Strongest keepers (User-Ranking):
1. Librarian-5 #1 — Link-Staleness als Synthese-Trigger
2. Radagast-5 #1 — `grafted: false` Frontmatter-Marker
3. Jester-5 #3 — `wiki/komposthaufen.md` statt `wiki/forgotten/`
4. Librarian-5 #3 — Query-Magnitude statt Zählschwelle
5. Alchemist-5 #1 — `wiki/inbox/` mit 72h Sedimentation
6. Jester-5 #2 — Backlink-only Synthese-Stubs
7. Alchemist-5 #3 — Druckventil bei Query-Widerspruch (operationalisierungs-teurer)
8. Radagast-5 #4 — `geraeusche-YYYY-MM.md` Beobachtungs-Notiz

Next Experiment: gut gewählt, aber entschärfen — statt alle 47 Synthesen direkt anfassen, Sample-Rollout (10 Query-Notes + 5 Synthesen) für 7 Tage. Bei Zug: ausrollen, sonst zurücknehmen.

Fallback: Claude-Distiller als Fallback akzeptiert für v0.5.0. Aber Codex-Pfad ist broken: Codex-Rescue-Subagent hat nur ein Input-File vorbereitet statt strukturierte Distillation im erwarteten Format zu liefern. Kein Release-Blocker, aber Known Issue für v0.5.1.

## Known Issues → v0.5.1

1. **Codex-Distiller-Prompt schärfen.** Beim Blindtest (Radagast-Aktivierung) schrieb Codex die Ergebnis-Datei direkt; beim Chat-Mode-Smoke-Test bereitete Codex nur ein Input-File vor. Ursache vermutlich: der Prompt in `chat-curator.md` schließt mit "schreibe NUR das Markdown-Ergebnis zurueck" — Codex hat das als "Vorbereitung via File" interpretiert. Fix-Kandidaten: (a) expliziter machen, dass der Output als Text-Rückgabe erwartet wird, nicht als File; (b) Output-Schema als JSON-Fragment, damit Codex kein File-Write-Tool verwendet; (c) Codex-Subagent-Variante mit expliziter `no-file-write`-Instruktion.
2. **Scoring-Kalibrierung.** Distiller-Prompt sollte härtere U-Skala erzwingen — z.B. "U=5 ist reserviert für Ideen, die in <15 min mit einem einzigen Bash-Befehl testbar sind. U=4 für <1h. U=3 bei Workflow-/Template-Arbeit. U=2 bei Skill-Änderung. U=1 bei Architektur-Änderung."
3. **Round-1/2-Appendix-Option.** `--chat --compact` Flag, der Round 1/2 nur als `<details>`-Toggle rendert und Round 3 plus Top-3 plus Next-Experiment als primäre Leseebene setzt.

## Abschluss-Synthese (nach Release)

Nach erfolgreichem Abschluss (alle 8 Phasen ✅) wird eine Synthese-Datei geschrieben:
`~/wiki/synthesis/crazy-professor-chat-mode-2026-MM.md`

Format analog `vault-hardening-2026-04.md`: Current thesis, Supporting evidence, Counter-evidence, What to investigate next.
