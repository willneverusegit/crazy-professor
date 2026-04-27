# Faehigkeiten — crazy-professor

## Tools & Integrationen

| Tool / Feature | Status | Seit | Beschreibung |
|----------------|--------|------|--------------|
| Single-Run-Mode | aktiv | 2026-04-22 | 1 Archetype, 10 Provokationen + 1 Next-Experiment, ~30s |
| Chat-Mode (`--chat`) | aktiv | 2026-04-23 (v0.5.0), stabilisiert 2026-04-23 (v0.5.1) | 4 Archetypen, 3 Runden, 20 destillierte Ideen, ~10 LLM-Calls |
| Variation-Guard | aktiv | 2026-04-22 | Anti-Streak-Logik gegen Archetype-Cluster (≥3 in Folge) und Wort-Wiederholung (innerhalb letzter 10 Rows) |
| Field-Notes-Log | aktiv | 2026-04-22 | Markdown-Tabelle in `.agent-memory/lab/crazy-professor/field-notes.md` |
| Museum-Clause | aktiv | 2026-04-22 | Skill zieht sich nach 10 Runs ohne Keeper selbst zurueck |
| Radagast-Brown Archetype | aktiv | 2026-04-23 | Vierter Archetype, schuetzt nuetzlich-nutzlose System-Teile gegen Optimierung |
| Codex-Round-3-Distiller | aktiv | 2026-04-23 | `codex:codex-rescue` als Round-3-Juror in Chat-Mode |
| Claude-Distiller-Fallback | aktiv | 2026-04-23 | Falls Codex nicht erreichbar |
| Picker-Skript (deterministisch) | aktiv | 2026-04-27 (v0.7.0) | Python-Skript `scripts/picker.py` (stdlib-only). Modi: `--mode single` / `--mode chat`. Liest field-notes.md, wendet Variation-Guard an, gibt JSON. Optional als Pre-Tool-Step. |
| field-notes-Schema im Repo | aktiv | 2026-04-27 (v0.7.0) | `resources/field-notes-schema.md` (canonical Spalten-Spec, 12 Spalten, append-only) + `resources/field-notes-init.md` (Init-Template, das Picker bei fehlender field-notes ins Ziel-Projekt kopiert) |
| Output-Validator | aktiv | 2026-04-27 (v0.7.0) | Python-Skript `scripts/validate_output.py` (stdlib-only). Prüft Format-Drift in Single- und Chat-Mode-Output. Pre-Write-Check. |
| Word-Pool-Linter | geplant | — | Phase 3: Doubletten/Whitespace/Case-Inkonsistenzen |
| Pflicht-/Verbots-Vokabel-Linter | geplant | — | Phase 3: pro Archetype, blockiert Voice-Drift |
| Eval-Suite | geplant | — | Phase 3: 50-100 Sample-Runs gegen Pflicht/Verbot/Schema |
| Telemetrie-Layer (JSONL/SQLite) | geplant | — | Phase 4: Run-Log mit Picker-Werten + Round-2-Status + Voice-Drift-Hits |
| Patch-Suggestion-Loop | geplant | — | Phase 4: alle 10 Runs SKILL.md/Word-Pool-Patch-Vorschlag |
| Run-Planner | geplant | — | Phase 5: Archetype-Selector aus Topic + `--from-session` |
| `--chat --compact` | geplant | — | Phase 6: Round 1+2 als `<details>`, Round 3 primaer |
| `--strict-cross-pollination` | geplant | — | Phase 6: semantischer Substanz-Check fuer Round-2 |
| 4. PO-Operator (`wishful thinking`) | geplant | — | Phase 6: kontrollierter Feldtest |
| GUI/Playground | optional, geplant | — | Phase 7: Single-File-HTML, Vorbild `playground` Skill |
| Telegram-Bridge | optional, geplant | — | Phase 8: Security-Audit als Vorbedingung, RISIKO |
| Multi-Provider-Routing | out of scope | — | Codex+Claude reichen |
| Skill-Mesh-Pipeline | out of scope | — | crazy → plan-merger → executing-plans, interessant aber nicht jetzt |
| Stage-Magician-Archetype | out of scope | — | Radagast-Repetition-Watch noch offen, neuer Archetype waere verfrueht |

Status-Werte: `aktiv`, `experimentell`, `geplant`, `optional, geplant`, `out of scope`, `deprecated`, `entfernt`

## Profile / Modi

- **Single-Run** (default): 1 Archetype-Pick via mod-4 + Variation-Guard, 10 Provokationen, 1 Next-Experiment.
- **Chat-Mode** (`--chat`): alle 4 Archetypen parallel in Runde 1 (5 Provokationen je), Cross-Pollination in Runde 2 (counter/extend), Codex-Distillation in Runde 3 (5 Final-Ideen je Archetype = 20 total).
- **Chat-Mode Dry-Run** (`--chat --dry-run-round1`): nur Runde 1, kein Round-2/3, fuer internes Testen.

## MCP-Server

Nicht zutreffend — crazy-professor exponiert keinen MCP-Server. Es nutzt das Codex-Plugin als Subagent fuer Round-3-Distillation, kommuniziert sonst nur ueber Datei-Output.

## Einschraenkungen

- **Lokal nur**: kein Cloud-Sync, kein Multi-Maschinen-State (field-notes liegt pro Projekt)
- **Manuelles Triggering**: kein Auto-Schedule, kein Webhook, kein Bot
- **Single-Topic pro Run**: Chat-Mode kann keinen Multi-Topic-Batch
- **Keine Modell-Mix-Optionen**: Claude fuer Runde 1+2, Codex fuer Runde 3 ist fix
- **Picker-Mechanik aktuell in Prosa**: deterministische Implementierung kommt in Phase 2
- **Keine Telemetrie**: Variation-Guard, Museum-Clause, Repetition-Watch sind aktuell nur in Prosa beobachtbar (Phase 4 schliesst das)
