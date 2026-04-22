---
title: crazy-professor v0.4.0 Master-Plan (ehemals v0.3.0 Master-Plan)
project_shortname: cp
created: 2026-04-22
renamed: 2026-04-22 (post-Radagast)
status: active
origin: crazy-professor Run 2 Keeper (#1, #2, #4)
source_provocation: .agent-memory/lab/crazy-professor/2026-04-22-0702-skill-creator-ausbau.md
supersedes_scope: target-release-number only (content unchanged, renumbered due to v0.3.0 Radagast release)
---

# crazy-professor v0.4.0 — Master-Plan

> **Versionshinweis (2026-04-22, nachtraeglich):** Dieser Plan wurde
> urspruenglich als v0.3.0-Master-Plan aus den Keepern von Run 2
> extrahiert. Zwischenzeitlich wurde v0.3.0 fuer den Radagast-der-Braune-
> Archetype-Release verwendet (commit `2129d87`, 4. Archetype mit
> Biosphaere/Pflege-Vokabular, Activation-Gate bis 2026-04-29) und v0.3.1
> fuer `docs/USAGE-PATTERNS.md` (commit `c4fcf14`). Die drei hier
> beschriebenen Phasen (archetype-selector, --from-session Topic-Feeder,
> output-als-patch) sind **inhaltlich orthogonal** zu Radagast und
> bleiben gueltig -- sie rutschen nur auf v0.4.0 weiter. Zeile
> "Archetype-Liste bleibt bei 3" ist durch Radagast-Release ueberholt
> und wurde unten entsprechend aktualisiert.

## Ausgangsdiagnose

- crazy-professor v0.3.x laeuft stabil (4 Archetypes jester/librarian/alchemist/radagast-brown, Radagast latent bis 2026-04-29, 3 Runs absolviert, Museum-Klausel bei Gate-Distanz 7).
- Strukturelle Luecken, die in Run 2 sichtbar wurden (und von Radagast NICHT adressiert sind):
  1. **Archetype-Wahl ist blind.** Timestamp-mod-4 (bzw. mod-3 wegen Radagast-Latenz) entscheidet, nicht das Thema. Ein Systemthema kann dem Jester zufallen, ein Mythos-Thema dem Alchemist — beides produziert Drift. Radagast hat das Problem nicht geloest, nur die Anzahl der moeglichen Ziele erhoeht.
  2. **Topic-Input haengt am User.** Der Reaktor startet nur, wenn der User ein Thema tippt. Vorhandener Reststoff (session-summary.md) wird nicht gelesen.
  3. **Output verlaesst das System.** Erkenntnisse aus 10 Provokationen pro Lauf verduften in field-notes, fliessen nie zurueck in die Skill-Templates.
- Diese drei Luecken haengen kausal zusammen: #2 fuettert Topics → #4 waehlt Archetype → #1 schreibt Erkenntnis in Patch. v0.4.0 schliesst die Schleife.

## Phasen-Tabelle

| Phase | Ziel | Output | Status |
|-------|------|--------|--------|
| Phase-1 | Archetype-Selector (Provokation #4) baut Selektor, der aus Topic-Keywords den Archetype waehlt. Timestamp-Seed wird Fallback. | `skills/crazy-professor/prompt-templates/archetype-selector.md` + Patch in SKILL.md Operating Instructions Step 2. | ⏳ |
| Phase-2 | Topic-Feeder (Provokation #2) liest `.agent-memory/session-summary.md` und schlaegt 3 Topic-Kandidaten vor, bevor der User tippt. User waehlt oder overridet. | `commands/crazy.md` erweitert um `--from-session`-Flag + Logik in SKILL.md Step 1. | ⏳ |
| Phase-3 | Output-als-Patch (Provokation #1) schreibt jede 10. Generierung einen Patch-Vorschlag fuer SKILL.md nach `.agent-memory/lab/crazy-professor/patches/` mit Review-Gate. | `patches/`-Verzeichnis + Cron-/Zaehler-Logik in SKILL.md + manuelles Apply-Protokoll. | ⏳ |
| Phase-4 | Release v0.4.0: README, CHANGELOG, marketplace.json-Version-Bump. Museum-Gate-Status in field-notes.md aktualisieren. | Git-Commit + Tag `v0.4.0`. | ⏳ |

Status-Symbole: ✅ done / 🟡 in-progress / ⏳ todo / ❌ blocked

## Bereits getroffene Entscheidungen (nicht neu verhandeln)

- **Reihenfolge Phase-1 → 2 → 3 ist fix.** Selector ist Voraussetzung: ohne ihn ist Topic-Feeder sinnlos (welcher Archetype kriegt das session-summary-Topic?).
- **Timestamp-Seed bleibt als Fallback.** Kein Hard-Replace. Wenn Selector ambig ist (keine Keywords matchen), greift mod-3.
- **Output-als-Patch ist NICHT Auto-Apply.** Jede Patch-Datei braucht manuelle User-Abnahme. Skill patcht Skill = Riskio, Sicherheitsnetz = Review-Gate.
- **Archetype-Liste steht bei 4 (v0.3.0): jester/librarian/alchemist/radagast-brown.** Radagast ist latent bis 2026-04-29. stage-magician bleibt fuer V1.2 geparkt. v0.4.0 addiert keinen weiteren Archetype, sondern Infrastructure (Selector/Feeder/Patch).
- **Hard Rules aus SKILL.md bleiben unveraendert.** Divergence-Warning, 10 Provokationen, ein Next-Experiment, Anchor-Pflicht — alles bleibt.

## Offene Fragen fuer spaetere Phasen

- Wie wird Selector-Ambiguitaet gemessen? Keyword-Count? Embedding-Similarity zum Archetype-Vokabular? (Phase-1 entscheidet.)
- Soll `--from-session` mehrere Themen ziehen oder nur das letzte? (Phase-2 entscheidet nach User-Feedback.)
- Wird die Patch-Datei mit git oder manuell appliziert? (Phase-3 entscheidet.)
- Braucht v0.4.0 einen Migrations-Hinweis fuer bestehende Invocations (field-notes-Format)? (Phase-4 entscheidet.)

## Commit-Message-Konvention

`cp | Phase-{N}: {knapper-status}`

Beispiele:
- `cp | Phase-1: archetype-selector.md + SKILL.md Step-2-Patch`
- `cp | Phase-2: --from-session flag + session-summary reader`
- `cp | Phase-3: patches/ infra + 10th-run hook`
- `cp | Phase-4: v0.4.0 release + museum-gate status update`

## Abbruchbedingungen

- Wenn Phase-1 den Selector nicht unter 50 Zeilen Logik halten kann → auf keyword-count-Minimalversion zurueckfallen.
- Wenn Phase-2 voraussetzt, dass session-summary.md ein festes Format hat → erst in SESSION-WORKFLOW.md verankern, dann bauen.
- Wenn Phase-3 in Review ergibt, dass Patch-Vorschlaege unter 30% sinnvoll sind → Phase-3 streichen, v0.4.0 ohne #1 releasen.

## Referenzen

- Source-Provokationen: `.agent-memory/lab/crazy-professor/2026-04-22-0702-skill-creator-ausbau.md`
- Run-1-Keeper-Log: `.agent-memory/lab/crazy-professor/field-notes.md`
- Hard-Rules: `Claude-Plugins-Skills/crazy-professor/skills/crazy-professor/SKILL.md` Abschnitt "Hard Rules"
- Museum-Klausel: SKILL.md Abschnitt "Museum Clause"
