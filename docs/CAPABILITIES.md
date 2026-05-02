# Faehigkeiten — crazy-professor

## Tools & Integrationen

| Tool / Feature | Status | Seit | Beschreibung |
|----------------|--------|------|--------------|
| Single-Run-Mode | aktiv | 2026-04-22 | 1 Archetype, 10 Provokationen + 1 Next-Experiment, ~30s |
| Chat-Mode (`--chat`) | aktiv | 2026-04-23 | 4 Archetypen, 3 Runden, 20 destillierte Ideen, ~10 LLM-Calls |
| Lab (`--lab`) | aktiv | 2026-04-30 | Standalone Browser für Output-Triage, paste-only, kein LLM-Call |
| Variation-Guard | aktiv | 2026-04-22 | Anti-Streak-Logik in `picker.py` (Archetype-Streak ≥3, Wort-Window 10) |
| Field-Notes-Log | aktiv | 2026-04-22 | Markdown-Tabelle in `.agent-memory/lab/crazy-professor/field-notes.md` |
| Museum-Clause | aktiv | 2026-04-22 | Skill zieht sich nach 10 Runs ohne Keeper selbst zurueck |
| Codex-Round-3-Distiller | aktiv | 2026-04-23 | `codex:codex-rescue` als Round-3-Juror in Chat-Mode |
| Claude-Distiller-Fallback | aktiv | 2026-04-23 | Falls Codex nicht erreichbar |
| Picker-Skript | aktiv | 2026-04-27 | `picker.py` (stdlib-only): mod-4 archetype, mod-4 operator, microsecond-seeded word, JSON-Output. Force-Flags + wishful-share v0.13.0 entfernt. |
| Output-Template + Field-Notes-Schema | aktiv | 2026-04-27 | Marker-Pattern + Tabellen-Spec, Format ist Soll-Vertrag im Prompt (kein Linter mehr) |

Status-Werte: `aktiv`, `experimentell`, `geplant`, `out of scope`, `deprecated`, `entfernt`

## Profile / Modi

- **Single-Run** (default): 1 Archetype-Pick via mod-4 + Variation-Guard, 10 Provokationen, 1 Next-Experiment.
- **Chat-Mode** (`--chat`): alle 4 Archetypen parallel in Runde 1 (5 Provokationen je), Cross-Pollination in Runde 2 (counter/extend), Codex-Distillation in Runde 3 (5 Final-Ideen je Archetype = 20 total).
- **Chat-Mode Dry-Run** (`--chat --dry-run-round1`): nur Runde 1, kein Round-2/3, fuer internes Testen.
- **Lab** (`--lab`): standalone Browser, paste-only, kein LLM-Call.

## MCP-Server

Nicht zutreffend — crazy-professor exponiert keinen MCP-Server. Es nutzt das Codex-Plugin als Subagent fuer Round-3-Distillation, kommuniziert sonst nur ueber Datei-Output.

## Einschraenkungen

- **Lokal nur**: kein Cloud-Sync, kein Multi-Maschinen-State (field-notes liegt pro Projekt)
- **Manuelles Triggering**: kein Auto-Schedule, kein Webhook, kein Bot
- **Single-Topic pro Run**: Chat-Mode kann keinen Multi-Topic-Batch
- **Keine Modell-Mix-Optionen**: Claude fuer Runde 1+2, Codex fuer Runde 3 ist fix
- **Format-Vertrag ist Soll**: kein Pre-Write-Validator mehr (v0.13.0 zurückgebaut). Format-Drift wird beim Lesen sichtbar.
- **Picker-Skript ist optional**: Plugin laeuft auch ohne Python (Fallback-Prosa-Mechanik in operating-instructions Step 2 / picker.py docstring)

## Entfernte Funktionen (v0.13.0, 2026-05-02)

Phase-4-8-Funktionalität entfernt — siehe `docs/CHANGELOG.md` v0.13.0 Eintrag. Wenn etwas davon zurückkommen soll: git-Historie als Archiv.
