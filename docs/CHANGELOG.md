# Changelog — crazy-professor

Neueste Eintraege oben. Format: `## [vX.Y.Z] [YYYY-MM-DD] Kurztitel` für Versions-Bumps, sonst `## [YYYY-MM-DD] Kurztitel`. Versions-Policy in `docs/VERSIONING.md`.

---

## [v0.11.0] [2026-04-28] Phase 6 — Cross-Pollination + Kompakt-Modus

**Versions-Bump-Begründung (per VERSIONING.md):** MINOR-Bump weil zwei neue user-facing Flags (`--chat --compact`, `--strict-cross-pollination`) und ein 4. PO-Operator (`wishful-thinking`) als kontrolliertes Feldtest-Set aktiviert werden. Master-Plan-Phase 6 abgeschlossen (5/8 → 6/8 Phasen).

- **6.1 `--chat --compact`-Flag**: reordert Chat-Output. Round 3 (Final 20) + Top-3 + Next-Experiment + Self-Flag erscheinen primär; Round 1 + Round 2 in einem `<details>`-Audit-Trail-Block am Ende. Frontmatter bekommt neues optionales Feld `compact: true`. Validator branched auf das Feld und prüft die geforderte Reihenfolge. `--compact` ohne `--chat` wird am Command-Layer mit Fehlermeldung `--compact requires --chat. Single-run output is already flat.` abgelehnt.
- **6.2 `--strict-cross-pollination`-Flag**: deterministische Substanz-Heuristik via neuem 4. Linter `lint_cross_pollination.py` (~330 LOC, stdlib-only). Drei Checks pro R2-Item: (1) Marker-Existenz `counter:`/`extend:`, (2) Ref-Auflösung archetype + idx in 1..5, (3) Token-Overlap mit Ref >= `--min-overlap` (default 1) nach Stop-Word-Filter. Findings erscheinen als `[low-substance: <reason>]`-Marker direkt in den R2-Zeilen. Exit-Code immer 0 (warn-only — keine Items werden gefiltert). Operating-Instructions Step C4b dokumentiert.
- **6.3 4. PO-Operator `wishful-thinking` aktiviert**: `picker.py` bekommt `--wishful-share <float>` Default `0.25`. Operator-Liste wird dynamisch 4-elementig mit Gewichten `[1, 1, 1, share*3]`. Bei `share=0.0` Regression auf v0.10.0-3-Operator-Verhalten, bei `share=0.333` exakt 25%/25%/25%/25%, bei `share=1.0` ~50% wishful (Gewichte `[1,1,1,3]`). `random.choices` mit Mikrosekunden-Seed für Determinismus. `po-operators.md` enthält volle Wishful-Thinking-Section mit Definition, Scaffold und Distinction-from-Reversal-and-Escape.
- **3 neue optionale Telemetrie-Felder** (Phase-4-Vertrag eingehalten): `compact_mode` (bool), `low_substance_hits` (int), `wishful_thinking_active` (bool). Backward-compatible — alte Reader ignorieren unbekannte Felder.
- **Neue Resource** `skills/crazy-professor/resources/stop-words.txt` (~130 Zeilen, EN+DE-Mix + Archetype-/Operator-Labels).
- **Eval-Suite erweitert** um drei neue Smoke-Test-Stages: Stage C (Compact-Mode, 5 Asserts), Stage D (Cross-Pollination Linter, 8 Asserts), Stage E (Wishful-Thinking Picker, 6 Asserts). Plus Operator-Coverage-Aggregate in Stage A. Total +19 Asserts. Stage A `run_picker_once` akzeptiert jetzt `wishful-thinking` als gültigen Operator.
- **Eval-Baseline 2026-04-28** (Phase 6) vollständig PASS: Stage A 200/200 (alle 4 Operatoren in Distribution sichtbar), Stage B Telemetry+Run-Planner PASS, Stage C 5/5, Stage D 8/8, Stage E 6/6.
- **Inline-Plan-Korrekturen während Execution**: (a) `picker.py --help`-Text korrigiert (`share=1.0` ist NICHT 25/25/25/25, sondern wishful ~50%; korrekt: `share=0.333` ist gleichverteilt). (b) Stage E share=1.0-Assert-Schranken angepasst auf reale Verteilung statt 30-70-Annahme.
- **Workflow-Pattern**: brainstorming → spec → plan → executing-plans (inline) — zweite vollständige Anwendung nach Phase 5, weiter bewährt.

---

## [v0.10.0] [2026-04-28] Phase 5 — Run Planner + `--dry-run`

**Versions-Bump-Begründung (per VERSIONING.md):** MINOR-Bump weil zwei neue user-facing Flags (`--from-session`, `--dry-run`) hinzukommen und der Topic→Archetype-Selector eine neue Run-Mechanik etabliert. Master-Plan-Phase 5 abgeschlossen (4/8 → 5/8 Phasen).

- **5.1 Run Planner** (`scripts/run_planner.py`, ~305 Zeilen, stdlib-only): topic-aware Archetype-Selector + Session-Topic-Suggester als gemeinsame Schicht. Drei Subcommands:
  - `archetype --topic ... --keywords ...`: Score-Match gegen `resources/archetype-keywords.txt`. Substring-match case-insensitive auf lowercased+punct-stripped Topic. Tie an Position 1 oder Score=0 → `fallback_used: true`, `selected_archetype: null`. Sonst `selection_reason: "keyword_match"` + `matched_keywords` Liste.
  - `session --session-path <p1> [--session-path <p2> ...]`: parst Markdown-Sections "Naechste Schritte" / "Open Items" (case-tolerant) aus beliebig vielen Files, dedup über alle Pfade, cap auf 3 Topic-Kandidaten. Failure-Modes: keine Pfade → exit 1, alle Pfade unlesbar → exit 3.
  - `plan --topic ... --keywords ... --session-path ...`: kombiniert beides. Archetype-Fail → exit 2; Session-Fail → `topic_candidates: null` + exit 0.
  - Stdout-UTF-8-Reconfigure am Anfang von `main()` (Windows cp1252-Workaround für Unicode in session-summary).
- **5.2 `--dry-run` Flag** (single-run only): Run Planner + Picker laufen, Skill druckt Markdown-Preview-Block (Topic, Archetype mit Selector-Reason und Matched-Keywords, Picker-Output, Field-Notes-Kontext, Variation-Guard-Status), Abort vor Step 3. Komplett side-effect-frei: kein Output-File, kein field-notes-Append, keine Telemetrie. Combination `--chat --dry-run` rejected am Command-Layer.
- **5.3 `--from-session` Flag**: Skill ruft `run_planner.py session` mit lokalem (`<cwd>/.agent-memory/session-summary.md`) und Desktop-Pfad (`~/Desktop/.agent-memory/session-summary.md`) auf, zeigt User 3 Topic-Kandidaten als nummerierte Liste, fragt "Which? [1/2/3 or own]". User-Wahl wird Topic; bei leerer Antwort Fallback auf Standard-Single-Run-without-topic.
- **5.4 Resource `archetype-keywords.txt`** (~80 Keywords): one line per archetype, comma-separated keywords. Initial pool gesourced aus den Pflicht-Vokabeln der `prompt-templates/<archetype>.md` Lexicon-Gates plus generische Domain-Wörter (Englisch + Deutsch).
- **5.5 operating-instructions.md erweitert**: Step 1 bekommt zwei neue Bullets für `--from-session` und `--dry-run`. Step 2 split: Step 2a (Run Planner Archetype-Empfehlung), Step 2b (Picker mit optionalem `--force-archetype`), Step 2c (Variation-Guard, vorher 2b), Step 2d (Dry-Run-Output). Variation-Guard-Konflikt-Resolution dokumentiert: Selector ist Empfehlung, Variation-Guard hartes Constraint, Streak gewinnt.
- **5.6 Telemetrie-Schema-Erweiterung** (Phase-5-Substrate): zwei neue OPTIONALE Felder `archetype_selector_used` (bool) und `archetype_selector_matched_kw` (list[str]). Phase-4-Vertrag eingehalten (neue Felder müssen optional sein, nie required). Patch-Suggester wird diese Felder lesen sobald genug Daten da sind.
- **5.7 Eval-Suite-Erweiterung** (`eval_suite.py`): neue Funktion `stage_b_run_planner_smoke()` mit 8 deterministischen Asserts (keyword-match, no-match, tie→fallback, case-insensitive substring, empty topic→exit 1, missing keywords→exit 2, naechste-schritte-extraction, multi-path-dedup). Neue CLI-Args `--run-planner` und `--run-planner-keywords`. Render-Section `## Run Planner smoke (Stage B)` im Baseline-Report. Smoke-getestet: PASS 8/8.
- **Versions-Bump auf 0.10.0** in 8 Frontmatter-Files (plugin.json, SKILL.md, output-template, chat-output-template, chat-mode-flow.md frontmatter+example+status-line, chat-curator, chat-round-1-wrapper, chat-round-2-wrapper). PROJECT.md "Aktueller Stand" + Roadmap-Checkbox updated. CAPABILITIES.md "Run-Planner" von geplant auf aktiv, plus zwei neue Zeilen für `--from-session` und `--dry-run`. Master-Plan Phase 5 Status ⏳ → ✅ (2026-04-28).

---

## [v0.9.0] [2026-04-27] Phase 4 — Telemetrie-Layer + Patch-Suggestion-Loop

**Versions-Bump-Begründung (per VERSIONING.md):** MINOR-Bump weil der Patch-Suggestion-Loop user-visible ist (alle 10 Runs erscheint ein neuer Vorschlags-File im Lab) und der Telemetrie-Layer eine neue maschinenlesbare Schicht hinzufügt, auf der zukünftige Phasen aufbauen. Master-Plan-Phase 4 abgeschlossen.

- **4.1 Telemetrie-Layer** (`scripts/telemetry.py`, ~190 Zeilen, stdlib-only): append-only JSONL pro Run. Schema flat + stabil: `run_id, timestamp, mode, topic_slug, archetype/word/operator/re_rolled (single) oder picks[4] (chat), distiller_used, round2_status, time_to_finish_ms, voice_cross_drift_hits, lint_pass`. Schema-Validation gegen ungültige Modes/Round2-Status/picks-Länge. Subcommands `log` (mit `--json` oder `--stdin`), `summary` (`--last N`, default 50), `default-path`. Default-Pfad lebt neben `field-notes.md` im Lab-Corpus (`~/Desktop/.agent-memory/lab/crazy-professor/telemetry.jsonl`), override mit `--path`. 50-MB Hard-Cap (Rotation manuell). Smoke-Test: 2 Records (single + chat), Round-Trip + Aggregat OK; 4 Schema-Violation-Pfade fangen je richtig.
- **4.2 Patch-Suggestion-Loop** (`scripts/patch_suggester.py`, ~230 Zeilen, stdlib-only): liest komplette field-notes.md Log-Tabelle, normalisiert Archetype/Word, identifiziert proven Words (`kept >=2`), retire candidates (`retire=yes >=1`), voice-drift hot spots und archetype-word-affinity. Modulo-Gate: triggert nur bei `single_runs % --every == 0` (default 10), `--force` für manuell. Schreibt Vorschlag nach `<field-notes-parent>/patches/YYYY-MM-DD-suggestion-N.md` (auto-incrementing seq). Vorschläge sind NIE automatisch angewandt — User reviewt und applied manuell. Smoke-Test gegen echte field-notes (15 single-runs): Modulo-Gate korrekt nicht-getriggert ohne Force; mit `--force` schreibt Vorschlag mit 3 voice-drift hot spots gefunden (alle 3 Blindtest-Faelle korrekt erkannt).
- **4.3 SKILL.md + operating-instructions verdrahtet**: Helper-Skripte-Block in SKILL.md von 5 auf 7 erweitert mit Versionen + File-Layout-Diagram. Step 7b (Telemetry log) und Step 7c (optional patch-suggester) in operating-instructions.md eingebaut, jeweils mit Bash-Beispiel. Step C7b für Chat-Mode mit picks-Liste + round2_status-Mapping (`ok|skipped|failed`).
- **4.4 Eval-Suite Telemetrie-Smoke-Test**: `eval_suite.py --telemetry <path>` führt Append+Round-Trip+Summary-Test durch und reportet im Baseline-Markdown unter "## Telemetry smoke (Stage B)". Smoke-getestet: PASS bei 5 Picker-Runs/Archetype + Telemetry-Test.
- **4.5 lint_voice.py docstring-Drift behoben** (Quality-Fixer-Carry aus v0.8.0): "ASCII-only normalization" Claim präzisiert auf "no diacritic transliteration is performed" mit Hinweis, dass bei zukünftigen non-ASCII-Tokens eine Transliteration ergänzt werden muss.
- **Versions-Bump auf 0.9.0** in 8 frontmatter Files (`plugin.json`, SKILL.md, output-template.md, chat-output-template.md, chat-mode-flow.md frontmatter+example, chat-curator.md, chat-round-1-wrapper.md, chat-round-2-wrapper.md). PROJECT.md "Aktueller Stand" + "Offene Baustellen" updated. CAPABILITIES.md 2 Items von "geplant" auf "aktiv" umgestellt.

---

## [v0.8.0] [2026-04-27] Phase 3 — Linter-Trio + Eval-Suite + Lexicon-Gates

**Versions-Bump-Begründung (per VERSIONING.md):** MINOR-Bump weil die Eval-Suite Pass-Rate als Gate für Prompt-Edits etabliert (workflow-changing) und das Lexicon-Gate-Block in jedem Template ein neues maschinenlesbares Vertragselement ist. Master-Plan-Phase 3 abgeschlossen.

- **3.1 Word-Pool-Linter** (`scripts/lint_word_pool.py`, ~150 Zeilen, stdlib-only): prüft `provocation-words.txt` und `retired-words.txt` auf Duplicates innerhalb und über beide Files, lowercase-Konformität, 1-3-Token-Form mit Single-Hyphen, kein Whitespace-Drift, kein Tab, kein Symbol außer `[a-z0-9]+(-[a-z0-9]+)*`. Pre-Commit-tauglich (siehe `scripts/run_linters.sh`). Default warnt bei Case-Borderlines, `--strict` promotet zu Error. Smoke-getestet: 176 reale Pool-Entries clean, synthetisches bad-pool fängt 11 Verstöße + Overlap.
- **3.2 Voice-Linter** (`scripts/lint_voice.py`, ~270 Zeilen, stdlib-only): liest Lexicon-Gate-Block aus jedem `prompt-templates/<archetype>.md`, parst alle Provocations, prüft per Provocation: required tokens (warn bei Miss), required_patterns (regex), forbidden tokens (error). Mini-YAML-Parser im Skript für den genutzten Subset. Substring-Match case-insensitive auf normalized text. Pre-Write Step 5b in operating-instructions verdrahtet. Smoke-getestet gegen 15 echte Outputs auf Desktop: 7 PASS, 6 WARN-only (legitime Style-Varianten), 2 FAIL — beide FAILs sind echte Voice-Drift-Funde (Cross-Archetype-Vokabel).
- **3.2a Lexicon-Gate-Block in jedem Template**: YAML-Code-Block am Ende von `first-principles-jester.md`, `labyrinth-librarian.md`, `systems-alchemist.md`, `radagast-brown.md`. Konservativ extrahiert aus den existierenden "Pflicht-Eroeffnung"/"Verbotenes Vokabular"-Blöcken in den System-Prompt-Kernen. Pro Archetype: required-Liste + required_min_per_provocation + (optional) required_in_first_sentence/required_in_first_chars + forbidden-Liste mit Cross-Archetype-Schmuggel-Detection. Librarian zusätzlich required_patterns für die offene Klasse "in der/im X-(kunde|ologie|...)" + Praktiker-Substantive.
- **3.3 Eval-Suite** (`scripts/eval_suite.py`, ~310 Zeilen, stdlib-only): Stage B (default) 50 Picker-Aufrufe pro Archetype mit `--force-archetype` + Lint+Validate-Sweep über `--corpus`-Verzeichnis. Stage C (`--live --runs N`) als Hook-Stub für Live-Skill-Aufrufe (echte LLM-Calls erfordern Claude/Codex-Orchestrierung außerhalb des Skripts). Output: `docs/eval-baseline-<date>.md` mit Picker-Pass-Rate, Operator-Distribution, Unique Words und Per-Archetype Voice/Validator-Counts + Fail-File-Details. Erste Baseline `docs/eval-baseline-2026-04-27.md`: Picker 100% / 200 Runs, Validator findet 8 Legacy-Format-Files (pre-v0.7.0), Voice findet 3 echte Cross-Drifts.
- **3.4 SKILL.md + operating-instructions verdrahtet**: Helper-Skripte-Block in SKILL.md von 2 auf 5 erweitert mit Versionen, File-Layout-Diagram um `scripts/` ergänzt. Step 5b "Voice lint" zwischen Step 5 und Step 6 in operating-instructions.md eingebaut mit warn/error-Severity-Erklärung.
- **3.5 Pre-Commit-Wrapper + docs/linters.md**: `scripts/run_linters.sh` als convenience wrapper (ruft aktuell nur lint_word_pool, future-proof). `docs/linters.md` mit At-a-glance-Tabelle aller 4 Tools, Pre-Commit-Hook-Anleitung Linux+Windows, Lexicon-Gate-Format-Spec, Eval-Suite-Aufruf-Beispiel + Interpretations-Hinweise.
- **Versions-Bump auf 0.8.0** in 9 frontmatter Files (`plugin.json`, SKILL.md, output-template.md, chat-output-template.md, chat-mode-flow.md frontmatter+example, chat-curator.md, chat-round-1-wrapper.md, chat-round-2-wrapper.md). PROJECT.md "Aktueller Stand" und "Offene Baustellen" updated. CAPABILITIES.md 3 Items von "geplant" auf "aktiv" umgestellt + Lexicon-Gate als neue Capability.

---

## [v0.7.0] [2026-04-27] Phase 2 — Picker-Skript + field-notes-Schema + Output-Validator

**Versions-Bump-Begründung (per VERSIONING.md):** MINOR-Bump weil Picker-Skript als Pre-Tool-Step die Skill-Mechanik strukturell ändert. Master-Plan-Phase 2 abgeschlossen.

- **2.2 field-notes-Schema**: `resources/field-notes-schema.md` legt die canonical Spalten-Spec fest (12 Spalten, append-only Log-Tabelle, Status-Block-Konventionen). `resources/field-notes-init.md` ist das Init-Template, das der Picker bei fehlender field-notes.md ins Ziel-Projekt kopiert.
- **2.1 Picker-Skript** (`scripts/picker.py`, 252 Zeilen, stdlib-only Python): liest die letzten 10 Log-Zeilen von field-notes.md, führt Picker (mod-4 archetype, microsecond-based word, mod-3 operator) aus, wendet die Variation-Guard-Logik aus Step 2b an (archetype-streak ≥3 re-roll, word-window dedup), gibt JSON `{archetype, word, operator, re_rolled, timestamp, mode}` auf stdout. Modi: `--mode single` (default), `--mode chat` (4 parallele Picks). Optionen: `--init-template`, `--force-archetype`, `--force-timestamp`. Smoke-getestet gegen die echte Desktop-field-notes (10 Rows, korrekte Anti-Streak-Erkennung), Chat-Mode (4 unterschiedliche Worte/Operatoren), Force-Archetype, Init-on-missing-file.
- **2.3 Output-Validator** (`scripts/validate_output.py`, ~200 Zeilen, stdlib-only Python): prüft Single-Run- und Chat-Mode-Output auf Format-Drift. Single: Frontmatter, Divergence-Banner, exakt 10 Provokationen mit Pattern `<text> -- [cost: <level>] -- anchor: <text>` (akzeptiert `--`, em-dash `—`, en-dash `–`), Next-Experiment, Self-Flag mit ≥3 Checkboxes. Chat: Round 1/2/3 vorhanden, Round 3 mit exakt 5 Items pro Archetype-Subsection, Top-3 mit genau 3 Items. Smoke-getestet gegen 4 echte Output-Files: pass auf 2026-04-23-Outputs (post-Format-Stabilisierung) und Chat-Mode-Output, fail (korrekt) auf 2026-04-22-Outputs (vor Format-Stabilisierung — diese hatten das Anchor-Pattern noch nicht).
- **SKILL.md + operating-instructions verdrahtet**: Step 2 dokumentiert Picker als preferred Path (Python-Call mit JSON-Parse), Fallback-Path (Prosa-Mechanik) bleibt für Python-fehlt-Umgebungen erhalten. Step 6 dokumentiert Validator als Pre-Write-Check.
- Skripte sind optional. Plugin-Repo bleibt vollständig nutzbar ohne Python.

---

## [v0.6.0] [2026-04-27] Phase 1 — Vertragsbereinigung & Quick-Wins

**Versions-Bump-Begründung (per VERSIONING.md):** MINOR-Bump weil Topic-Resolution-Vertrag breaking change ist (`--chat` ohne Topic wird jetzt explizit abgelehnt; vorher implizites Verhalten). Master-Plan-Phase 1 abgeschlossen.

- `docs/PROJECT.md`, `docs/CAPABILITIES.md`, `docs/ARCHITECTURE.md`, `docs/CHANGELOG.md` aus globalem Template angelegt
- Input-/Trigger-Vertrag in `README.md`, `commands/crazy.md`, `SKILL.md` vereinheitlicht — eine Semantik fuer leeres Topic und `--chat` ohne Topic
- `--chat` ohne Topic wird explizit abgelehnt mit Fehlermeldung
- `docs/chat-mode-flow.md` und `references/chat-mode-flow.md` auf Single-Source-of-Truth zusammengefuehrt
- Mehrwort-Provocation-Words geklaert (Entscheidung: Pool auf Einzel- und 2-Wort-Phrasen erlaubt, `output-template.md` Marker-Format akzeptiert das)
- `SKILL.md` von 464 auf 206 Zeilen getrimmt (-56%) — Operating-Instructions (Steps 1-7 + C1-C8) nach `skills/crazy-professor/references/operating-instructions.md` und Hard Rules (inkl. Museum-Clause, Field-Test-Rule, Radagast-Gate, Review-Rubric) nach `skills/crazy-professor/references/hard-rules.md` extrahiert. Plan-Ziel war ~150 Zeilen; bei 206 belassen, weil Frontmatter (28) + Trigger-Phrases-Block + Archetype-Tabelle + File-Layout-Diagramm zur Skill-Discoverability beim Loaden gebraucht werden — der echte Body-Inhalt ist 166 Zeilen.
- Pfad-Konvention etabliert: alle inter-File-Pfade in SKILL.md, operating-instructions.md, hard-rules.md verwenden `<repo-root>/...` Notation, damit sie aus jedem File konsistent auflösbar sind.
- `docs/VERSIONING.md` angelegt — explizite Versions-Policy für die 0.x-Phase, Bump-Trigger nach Master-Plan-Phasen-Mapping.
- Versions-Bump auf `0.6.0` in `plugin.json`, `SKILL.md` Frontmatter, `output-template.md`, `chat-output-template.md`, `chat-mode-flow.md` (Frontmatter + Output-Beispiel), drei `prompt-templates/chat-*.md`. SKILL.md-Body-Texte entkoppelt (statt "v0.5.1" jetzt "since v0.5.0" für historische Aussagen).

## [2026-04-26] Erweiterungs-Master-Plan via plan-merger Skill

- 8-Phasen-Master-Plan in `docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md` erstellt
- Codex+Claude Auto-Mode mit identischen Prompts → 8 Konflikte mit R/A/I-Bewertung, alle User-bestaetigt
- Codex-Verifier-Run: 7 Findings (3 Codex-Aufruf-Inkonsistenzen, 4 Score-Berechnungsfehler), alle behoben

## [2026-04-23] v0.5.1 — Codex-Prompt-Fix

- Chat-Mode Round-3 Distillation: Direct-Markdown-Return-Contract eingefuehrt (kein Scratch-File, kein Path-only-Response)
- Codex-Smoke-Test 2026-04-26 sauber

## [2026-04-23] v0.5.0 — Chat-Mode

- `--chat` Flag fuer 4-Archetypen-Modus, 3 Runden, ~10 LLM-Calls
- Round-1: parallele 4 Calls, 5 Provokationen je Archetype
- Round-2: Cross-Pollination, counter/extend-Marker
- Round-3: Codex-Distillation auf 5-pro-Archetype = 20 Final-Ideen
- Claude-Fallback bei Codex-Ausfall
- F2-F5 als Defaults bestaetigt

## [2026-04-23] Radagast-Brown Aktivierung

- Vierter Archetype `radagast-brown` produktiv geschaltet
- mod-4-Picker live, alle vier Archetypen mit 25% Wahrscheinlichkeit
- 4 Bindungs-Bedingungen aktiv (Vokabel-Regel, kein Foreign-Field-Smuggling, Optimization-under-Care-Flagging, Folder-Sprawl-Limit)

## [2026-04-22] v0.3.0 — Initial-Scaffold

- Single-Run-Mode mit 3 Archetypen (Jester, Librarian, Alchemist)
- Picker (mod-4 Timestamp), Variation-Guard, Field-Notes-Log, Museum-Clause
- Output-Template mit Adoption-Cost-Tags und Self-Flag-Checkboxes
- Hard Rules + Museum-Clause + Field-Test-Rule etabliert
