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
| Word-Pool-Linter | aktiv | 2026-04-27 (v0.8.0) | `scripts/lint_word_pool.py` (stdlib-only): Duplicates, Case, 1-3-Token-Form, Whitespace, retired/active Overlap. Pre-Commit (via `scripts/run_linters.sh`). |
| Voice-Linter (Pflicht-/Verbots-Vokabel pro Archetype) | aktiv | 2026-04-27 (v0.8.0) | `scripts/lint_voice.py` (stdlib-only): liest Lexicon-Gate aus jedem Template, prüft per-Provocation. Warn-only by default für required-Misses, error für forbidden Cross-Tokens. Pre-Write Step 5b. |
| Lexicon-Gate in Archetype-Templates | aktiv | 2026-04-27 (v0.8.0) | YAML-Block am Ende jedes `prompt-templates/<archetype>.md`. Source-of-Truth für required/forbidden Tokens + Patterns. |
| Eval-Suite | aktiv | 2026-04-27 (v0.8.0) | `scripts/eval_suite.py` (stdlib-only): Stage B (default) 50 Picker-Runs/Archetype + Lint+Validate-Sweep über Corpus. Stage C (`--live`) Stub. Output: `docs/eval-baseline-<date>.md`. Seit v0.9.0 zusätzlich Telemetrie-Smoke-Test (`--telemetry`). |
| Telemetrie-Layer (JSONL) | aktiv | 2026-04-27 (v0.9.0) | `scripts/telemetry.py` (stdlib-only): append-only JSONL pro Run mit `picker_values, re_rolled, distiller_used, round2_status, time_to_finish_ms, voice_cross_drift_hits, lint_pass`. Schema-validiert (single + chat). Subcommands: `log`, `summary`, `default-path`. Default-Pfad: `~/Desktop/.agent-memory/lab/crazy-professor/telemetry.jsonl` (override mit `--path`). 50-MB Hard-Cap. |
| Patch-Suggestion-Loop | aktiv | 2026-04-27 (v0.9.0) | `scripts/patch_suggester.py` (stdlib-only): liest field-notes.md (`kept`/`retire`/`voice-off`-Marker), triggert alle 10 single-Mode-Runs (modulo-Gate, `--force` für manuell), schreibt Vorschlag nach `lab/.../patches/YYYY-MM-DD-suggestion-N.md`. NIE automatisch angewandt — Review-Gate. Step 7c in operating-instructions. |
| Run-Planner | aktiv | 2026-04-28 (v0.10.0) | `scripts/run_planner.py` (stdlib-only): Subcommands `archetype` (Score-Match Topic→Archetype gegen `resources/archetype-keywords.txt`, Tie/no-match → fallback), `session` (extrahiert bis zu 3 Topic-Kandidaten aus `Naechste Schritte`/`Open Items` Sections beliebig vieler `--session-path`-Files, dedup), `plan` (kombiniert beides). Picker bleibt unangetastet; Variation-Guard gewinnt bei Streak. Step 2a in operating-instructions. |
| `--from-session` Flag | aktiv | 2026-04-28 (v0.10.0) | Skill ruft Run-Planner `session`-Subcommand auf, schlaegt User 3 Topic-Kandidaten aus lokaler + Desktop session-summary vor. Bei keinen Kandidaten Fallback auf Standard-Single-Run-without-topic. |
| `--dry-run` Flag (single-run) | aktiv | 2026-04-28 (v0.10.0) | Run-Planner + Picker laufen, Markdown-Preview-Block auf stdout, Abort vor Step 3. Komplett side-effect-frei (kein Output-File, kein field-notes-Append, keine Telemetrie). Nicht mit `--chat` kombinierbar (Reject am Command-Layer). |
| `--chat --compact` | aktiv | 2026-04-28 (v0.11.0) | Phase 6: reordert Chat-Output. R3 (Final 20) + Top-3 + Next-Experiment + Self-Flag primaer; R1+R2 in `<details>`-Audit-Trail. Frontmatter-Feld `compact: true`. Reject am Command-Layer ohne `--chat`. |
| `--strict-cross-pollination` | aktiv | 2026-04-28 (v0.11.0) | Phase 6: deterministische Substanz-Heuristik via 4. Linter `lint_cross_pollination.py`. Findings als `[low-substance: <reason>]`-Marker in R2-Zeilen. Warn-only (kein Filter). Operating-Instructions Step C4b. |
| Cross-Pollination-Linter | aktiv | 2026-04-28 (v0.11.0) | `scripts/lint_cross_pollination.py` (stdlib-only, ~330 LOC): drei Checks pro R2-Item — Marker-Existenz, Ref-Auflösung (archetype + idx in 1..5), Token-Overlap (>= `--min-overlap`, default 1, mit Stop-Word-Filter aus `resources/stop-words.txt`). JSON-Output, exit-code immer 0. |
| 4. PO-Operator (`wishful-thinking`) | aktiv | 2026-04-28 (v0.11.0) | Phase 6: `picker.py --wishful-share <float>` Default 0.25. Operator-Liste dynamisch 4-elementig mit Gewichten `[1, 1, 1, share*3]`. `share=0.0` Regression auf 3-Operator, `share=0.333` exakt 25%/25%/25%/25%, `share=1.0` wishful ~50%. po-operators.md hat volle Section. |
| Telemetrie-Felder Phase 6 | aktiv | 2026-04-28 (v0.11.0) | 3 neue optionale Felder: `compact_mode` (bool), `low_substance_hits` (int), `wishful_thinking_active` (bool). Backward-compatible. |
| `/crazy --playground`-Flag | aktiv | 2026-04-28 (v0.12.0) | Phase 7: triggert `build_playground.py` + oeffnet HTML via `webbrowser.open()`. Single-Run-only, standalone (Reject gegen `--chat`/`--from-session`/`--dry-run`/`--compact`/`--strict-cross-pollination`). |
| Browser-Playground (Single-File-HTML) | aktiv | 2026-04-28 (v0.12.0) | Phase 7: Cockpit-Layout. Topic-Input + 3-Element-Picker (Archetype/Word/Operator) mit Roll-All und per-Element-Re-Roll. Live-Prompt-Output mit Copy-Button. Field-notes-Footer mit Streak-Warnung. Pure-Static, `file://`-tauglich. |
| `picker.py --force-word` und `--force-operator` | aktiv | 2026-04-28 (v0.12.0) | Phase 7: zwei neue Force-Flags analog zu `--force-archetype`. Variation-Guard schlaegt Force konsistent. Neue `re_rolled`-Werte mit `forced-`-Praefix und `+`-Kombinationen. |
| Build-Skript `build_playground.py` | aktiv | 2026-04-28 (v0.12.0) | `scripts/build_playground.py` (stdlib-only): liest Resources (provocation-words, retired-words, po-operators, optional field-notes), generiert Single-File-HTML mit inlined JS-Constants. Idempotent. 9. stdlib-Skript. |
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
- **Picker-Skript ist optional**: Plugin laeuft auch ohne Python (Fallback-Prosa-Mechanik in operating-instructions Step 2)
- **Telemetrie hat 50-MB-Hard-Cap**: bei Überlauf manuelle Rotation/Archivierung notwendig (kein Auto-Rotate)
