---
title: crazy-professor v0.5.1 — Codex-Distiller-Prompt Fix
project_shortname: cp-codex
created: 2026-04-23
status: implemented
origin: v0.5.0 Phase-8 Review Known Issue #1
priority: medium
---

# v0.5.1 — Codex-Distiller-Prompt Fix

## Problem

Im ersten Chat-Mode End-to-End-Run (2026-04-23T12:00Z) hat der
`codex:codex-rescue`-Subagent die Destillations-Aufgabe **nicht im
erwarteten Format** zurueckgegeben. Statt direkt Markdown-Output zu
produzieren, hat er nur eine Eingabe-Datei (`_codex_input.md`, ~17KB)
vorbereitet und zurueckgemeldet "prepared distillation input".

Der Fallback zu Claude-Destillation (spezifiziert in `chat-curator.md`
Step C5) hat gegriffen und ein valides Ergebnis produziert. Aber der
Codex-Pfad ist de facto broken.

Beim Radagast-Activation-Blindtest (2026-04-23T10:53Z) hatte Codex das
Ergebnis noch direkt in eine Datei geschrieben (`draft-v2/blindtest-
codex-juror-2.md`). Unterschied: dort war Write-to-File das explizit
gewuenschte Output-Format. Beim Chat-Mode ist es nicht.

## Ursachen-Hypothesen

1. **Prompt-Ambiguitaet.** `chat-curator.md` schliesst mit "schreibe NUR
   das Markdown-Ergebnis zurueck" — Codex interpretiert das als
   "bereite das Markdown vor, liefer mir den Pfad", nicht als "gib mir
   das Markdown als Text-Antwort".
2. **Codex-Tool-Routine.** Codex hat starke Praeferenz zum File-Write
   (es ist in seinem agent-typischen Pattern). Bei grossen
   strukturierten Outputs greift es automatisch zu einem Scratch-File.
3. **Prompt-Groesse.** Der Destillations-Prompt mit 32 Provokationen ist
   gross (~17KB). Codex sieht das als File-Bearbeitung, nicht als
   Dialog-Antwort.

## Fix-Optionen (nicht alle umsetzen — eine oder zwei waehlen)

### Option A: Expliziter Antwort-Kanal

Am Ende des Codex-Prompts einen klaren Return-Contract:

> **Rueckgabe-Format:** Dein komplettes Ergebnis erscheint als
> Text-Antwort im Chat, NICHT als File. Schreibe keine Datei, kein
> Scratch-Input, kein Zwischen-Artefakt. Der aufrufende Agent nimmt
> deine Text-Antwort wortwoertlich und fuegt sie in sein Output-File
> ein. Wenn du ein File schreibst, geht dein Output verloren.

**Aufwand:** 1 Text-Edit in `chat-curator.md`. 10 min.

### Option B: JSON-Schema erzwingen

Output als JSON statt Markdown:

```json
{
  "jester_5": [...],
  "librarian_5": [...],
  "alchemist_5": [...],
  "radagast_5": [...],
  "top_3_cross_pollination": [...],
  "next_experiment": {...}
}
```

Hauptprogramm parst JSON und rendert Markdown. JSON ist fuer Codex eher
als "Antwort" erkannt, weniger als "File-Entwurf".

**Aufwand:** JSON-Schema + Parser + Markdown-Renderer. ~2h.

### Option C: Codex-Subagent-Variante mit `no-file-write`

Neuer Subagent-Typ, der beim Spawn explizit mit `--no-file-write`-Flag
oder equivalent arbeitet. Wuerde sicherstellen, dass Codex physisch
kein File schreiben kann.

**Aufwand:** Unklar — haengt davon ab ob codex-rescue das unterstuetzt.
Muss erst gecheckt werden.

### Option D: Struktur-Validierung + Auto-Retry

Beim Parsen der Codex-Antwort pruefen: ist es strukturierte Markdown
(vier Sektionen, Top-3, Next-Experiment)? Falls nein: ein Retry mit
Hinweis "Letzter Versuch lieferte nur Dateipfad, nicht Markdown-Text.
Gib das Ergebnis als direkte Antwort zurueck." Wenn auch das
fehlschlaegt: Claude-Fallback (bereits eingebaut).

**Aufwand:** ~30 min. Ist teilweise schon in Spec Step C5
dokumentiert ("einmal re-invoke mit Hinweis"), aber nicht
implementiert.

## Empfehlung

**Option A + D kombinieren.** A reduziert die Wahrscheinlichkeit des
Problems, D fuhrt eine erkennbare Self-Correction ein. Beides zusammen
~40 min Aufwand und deutlich robuster als Single-Fix.

B ist saubere Langfrist-Loesung, aber zu teuer fuer v0.5.1. Fuer
v0.6.x merken.

C nur pruefen falls A+D nicht reichen (wenn mehrere Chat-Runs trotz
Option A weiter File-Writes zeigen).

## Zusatz-Fix: Scoring-Kalibrierung

Im selben Release: hartere U-Skala in `chat-curator.md` verankern:

```
Umsetzbarkeit (U)-Skala:
- U=5: in <15 min mit einem einzigen Bash-Befehl testbar
- U=4: in <1h testbar, ohne Workflow-/Template-Aenderung
- U=3: Workflow-/Template-Arbeit noetig
- U=2: Skill-Aenderung noetig
- U=1: Architektur-Aenderung noetig
```

Die ungepruefte U=5-Inflation im Smoke-Test-Output (mehrere Ideen mit
U=5, die de facto U=3-Arbeit sind) war direkte Folge der fehlenden
Kalibrierung.

## Phasen

| Phase | Ziel | Aufwand | Status |
|-------|------|---------|--------|
| Phase-1 | Option A (Return-Contract) in `chat-curator.md` einbauen | 10 min | ⏳ |
| Phase-2 | U-Skala-Kalibrierung in `chat-curator.md` | 10 min | ⏳ |
| Phase-3 | Option D (Struktur-Validierung + Retry) implementieren | 30 min | ⏳ |
| Phase-4 | Smoke-Test: neuer Chat-Run, pruefen ob Codex jetzt strukturierte Antwort liefert | 5 min | ⏳ |
| Phase-5 | SKILL.md Version-Bump v0.5.0 → v0.5.1 + Changelog-Eintrag | 5 min | ⏳ |

**Gesamt-Aufwand:** ~1h, weit unterhalb Master-Plan-Schwelle.

## Trigger

v0.5.1 wird gebaut, sobald:
- Mindestens einer der 5 Chat-Mode-Museum-Probe-Runs ansteht UND
- Codex-Fallback wurde ≥ 2× in Folge ausgeloest (wuerde bedeuten:
  Problem ist systemisch, nicht One-off).

Oder auf explizite User-Anforderung.

## Implementation Status (2026-04-23)

Implemented:
- Direct text-return contract added to `chat-curator.md`.
- U-scale calibration added to `chat-curator.md`.
- Retry semantics now treat path-only/file-prep Codex responses as structure failures.
- `SKILL.md`, plugin manifest, marketplace metadata, README, command docs, and output templates bumped/synchronized to v0.5.1.
- Repo hygiene added via `.gitignore`.

Still pending:
- A real Chat-Mode smoke test with Codex available to verify that the direct text-return contract changes runtime behavior.
