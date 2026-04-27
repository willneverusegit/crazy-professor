# Eval Baseline 2026-04-27

- skill version: 0.8.0
- picker runs per archetype: 10
- corpus dir: `C:\Users\domes\Desktop\.agent-memory\lab\crazy-professor`
- voice strict mode: False

## Picker (Stage B static)

| Archetype | Runs | OK | Pass-Rate | Unique Words | Operator Dist |
|---|---|---|---|---|---|
| first-principles-jester | 10 | 10 | 100.0% | 10 | escape=4, exaggeration=6 |
| labyrinth-librarian | 10 | 10 | 100.0% | 10 | escape=4, reversal=6 |
| systems-alchemist | 10 | 10 | 100.0% | 9 | exaggeration=7, reversal=3 |
| radagast-brown | 10 | 10 | 100.0% | 10 | escape=9, exaggeration=1 |

All picker runs returned valid JSON with expected schema.

## Corpus (Stage B linter sweep) -- 18 files

| Archetype | Files | Voice Pass | Voice Warn | Voice Fail | Validator Pass | Validator Fail |
|---|---|---|---|---|---|---|
| first-principles-jester | 4 | 4 | 0 | 0 | 1 | 3 |
| labyrinth-librarian | 4 | 2 | 2 | 0 | 3 | 1 |
| systems-alchemist | 3 | 0 | 2 | 1 | 0 | 3 |
| radagast-brown | 5 | 1 | 2 | 2 | 4 | 1 |

Skipped 2 file(s) with unknown/missing archetype or unsafe path: briefing-skill-creator-phase1.md, inbox-2026-04-22.md

### Fail file details

- **first-principles-jester** / `2026-04-22-0036-agentic-os-kreativimpulse.md` (validator):
  - provocation #1 does not match format '<n>. <text> -- [cost: <level>] -- anchor: <text>': '1. Agentic-OS besteht aus Gedaechtnis, Ausfuehrung und Bewertung. Warum entscheidet immer die Bewertung, ob da
- **first-principles-jester** / `2026-04-22-2104-plugin-creations.md` (validator):
  - provocation #1 does not match format '<n>. <text> -- [cost: <level>] -- anchor: <text>': '1. Ein Plugin besteht aus: plugin.json, einem Namen, Commands, Skills, Hooks, einem Zweck. Warum muss der Zwec
- **first-principles-jester** / `2026-04-23-0952-memory-system-von-claude.md` (validator):
  - provocation #1 does not match format '<n>. <text> -- [cost: <level>] -- anchor: <text>': '1. Ein Memory besteht aus Trigger, Inhalt und Abruf. Warum schreibt immer der, der das Memory erzeugt, auch de
- **labyrinth-librarian** / `2026-04-22-1954-mcp.md` (validator):
  - provocation #1 does not match format '<n>. <text> -- [cost: <level>] -- anchor: <text>': '1. In der Meteorologie unterscheidet die Weltorganisation zwischen Wetter (Stunden, Tage) und Klima (Jahrzehnt
- **systems-alchemist** / `2026-04-22-0702-skill-creator-ausbau.md` (voice):
  - provocation #8 (systems-alchemist): forbidden token(s) present: ['rinde'] (these belong to a different archetype)
- **systems-alchemist** / `2026-04-22-0702-skill-creator-ausbau.md` (validator):
  - provocation #1 does not match format '<n>. <text> -- [cost: <level>] -- anchor: <text>': '1. Inputs des crazy-professor-Reaktors sind Topic, Timestamp, Wortliste; Output sind 10 Provokationen; zwische
- **systems-alchemist** / `2026-04-22-1314-zauberer-in-der-ui.md` (validator):
  - provocation #1 does not match format '<n>. <text> -- [cost: <level>] -- anchor: <text>': '1. Inputs eines UI-Zauberers: ein User-Ziel, ein Kontext-Reststoff vom Vorschritt, eine Wand aus unsichtbarer 
- **systems-alchemist** / `2026-04-22-1850-crazy-professor-meta.md` (validator):
  - provocation #1 does not match format '<n>. <text> -- [cost: <level>] -- anchor: <text>': '1. Inputs des Skills: Topic, Timestamp, Wortliste. Outputs: 10 Provokationen + ein Experiment. Reststoff: die 
- **radagast-brown** / `2026-04-23-1054-blindtest-wiki-inbox-ernte.md` (voice):
  - provocation #5 (radagast-brown): forbidden token(s) present: ['seefahrer haben'] (these belong to a different archetype)
- **radagast-brown** / `2026-04-23-2219-agentic-os-handoff-quality.md` (validator):
  - provocation #1 does not match format '<n>. <text> -- [cost: <level>] -- anchor: <text>': '1. Dein Handoff ist ein Gast im Nest, und die `session-summary.md` ist nur Futter, nicht das Tier. Was darf au
- **radagast-brown** / `2026-04-24-0011-agentic-os-handoff-quality.md` (voice):
  - provocation #8 (radagast-brown): forbidden token(s) present: ['output'] (these belong to a different archetype)
