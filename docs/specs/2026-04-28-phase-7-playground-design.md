---
title: crazy-professor Phase 7 — Single-File-HTML-Playground (Design Spec)
date: 2026-04-28
phase: 7
master_plan: docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md
status: design (brainstorming output, awaiting writing-plans)
target_version: 0.12.0 (MINOR per VERSIONING.md)
---

# Phase 7 — Single-File-HTML-Playground

## Executive Summary

Phase 7 fuegt eine visuelle Schicht zum CLI-only-Plugin hinzu. Browser-
Playground ist ein **Picker + Prompt-Builder + Copy-Helper** — kein
LLM-Call, kein File-System-Access, kein HTTP-Server. User triggert via
`/crazy --playground`, Build-Skript generiert frisches HTML mit inlined
Daten aus den Source-Resources, Browser oeffnet via OS-Default-Handler.
Cockpit-Layout mit 3 Status-Zellen (Archetype/Word/Operator), Roll-All
und per-Element-Re-Roll-Buttons. `picker.py` bekommt zwei neue Force-
Flags (`--force-word`, `--force-operator`). Eval-Suite-Stage F als
Quality-Gate. Versions-Bump v0.11.0 -> v0.12.0.

## Architektur-Ueberblick

| Komponente | Was | Single-Source |
|---|---|---|
| **Browser-Playground** | `skills/crazy-professor/playground/index.html` (gebaut, eingecheckt) -- Single-File, inlined JSON-Daten + JS, Cockpit-Layout, Topic-Input + 3-Element-Picker + Re-Roll-Buttons + field-notes-Status + Prompt-Builder + Copy-Button | aus Build generiert |
| **Build-Skript** | `scripts/build_playground.py` (~250 LOC, stdlib-only): liest Resources (`provocation-words.txt`, `retired-words.txt`, `po-operators.md`, archetype-Liste, optional `field-notes.md` last 10 rows), generiert HTML mit inlined Daten + JS-Logic, schreibt nach `playground/index.html` | Source-Resources |
| **Slash-Command** | `/crazy --playground` triggert Build + oeffnet HTML via `webbrowser.open()` (oder gibt Pfad-Hinweis) | `commands/crazy.md` |

**Browser-Boundary** (Klaerung 1-(a)):
- Browser ist Picker + Prompt-Builder + Copy-Helper. Kein LLM-Call, kein
  File-System-Access, kein Server.
- Output-Datei landet via Standard-CLI-Pfad (User pastet Prompt im
  Terminal -> Claude rendert + persistiert wie heute).

**Picker-Erweiterung** (Mikro-Frage A-(a)):
- `picker.py` bekommt `--force-word` und `--force-operator` analog zu
  `--force-archetype`. Variation-Guard schlaegt Force konsistent
  (Mikro-Frage B-(b)).

**Quality-Gate** (Klaerung 7-(c)):
- Eval-Suite Stage F (`stage_f_playground_build_smoke`): Build-Skript +
  JSON-Resource-Konsistenz gegen Source-Files. Drift-Detection via
  Counts-Match + Schema-Validation.

**Versions-Bump**: v0.11.0 -> v0.12.0 (MINOR per VERSIONING.md, neue
user-visible Surface).

**Was NICHT in Phase 7 ist**:
- Kein Chat-Mode-Surface im Browser (Phase-7.1-Kandidat).
- Kein LLM-Call aus dem Browser (kein API-Key, kein Stream).
- Kein lokaler HTTP-Server, keine WebSockets/SSE.
- Keine Self-Flag-Checkboxes im Browser (semantisch falsch -- Self-Flags sind nach-Run).
- Kein neues Telemetrie-Feld `triggered_via`.
- Kein File-System-Access-API, kein File-Save-Dialog im Browser.

## Browser-Playground UI (Cockpit-Layout)

Wireframe (Klaerung 4-(c)):

```
+----------------------------------------------------------+
|  crazy-professor -- Playground                  v0.12.0  |
|  ------------------------------------------------------  |
|                                                          |
|  Topic: [______________________________________________] |
|                                                          |
|  +--------------+  +--------------+  +--------------+    |
|  |  ARCHETYPE   |  |     WORD     |  |   OPERATOR   |    |
|  |              |  |              |  |              |    |
|  |   jester     |  |    smoke     |  |   reversal   |    |
|  |              |  |              |  |              |    |
|  +--------------+  +--------------+  +--------------+    |
|                                                          |
|       +---------------------------------+                |
|       |       Roll All                  |                |
|       +---------------------------------+                |
|                                                          |
|  [Re-Roll Word]  [Re-Roll Op]  [Pick Archetype v]        |
|                                                          |
|  +----------------------------------------------------+  |
|  |  /crazy "<topic>" --force-archetype jester ...     |  |
|  +----------------------------------------------------+  |
|                                                          |
|       +---------------------------------+                |
|       |       Copy Prompt               |  Copied!       |
|       +---------------------------------+                |
|                                                          |
|  ---------------------------------------------------     |
|  field-notes context (last 10 rows):                     |
|  - last archetype: jester (streak: 1)                    |
|  - last word: smoke                                      |
|  - jester-streak warning shown when next pick = 4th      |
+----------------------------------------------------------+
```

### Komponenten im Detail

1. **Header**: Plugin-Name + Version (aus inlined `VERSION` JS-Constant).
   Single Header-Zeile, dezent.

2. **Topic-Input** (full-width): One-Line-Input. Auto-Focus on Page-Load.
   Triggers nichts beim Tippen -- Topic wird erst beim Prompt-Generation
   gelesen.

3. **Cockpit (3 Status-Zellen)**:
   - Jede Zelle zeigt Label (oben, klein, uppercase) + Pick (zentriert,
     monospace, akzent-coloured).
   - Color-Coding: archetype = blue (#7ec0ee), word = green (#9ec587),
     operator = orange (#e0af68).
   - **Initial-State**: alle drei zeigen `(roll to pick)` placeholder,
     gedimmt.
   - Klick auf eine Zelle = nichts (Re-Roll-Buttons sind separat).

4. **Roll-All-Button** (primary, breit): Wuerfelt alle 3 Picks neu.
   `Math.random()` ueber die inlined Pools (Klaerung 5-(b): kein
   Variation-Guard im Browser).

5. **Per-Element-Re-Roll-Buttons** (drei kleine Buttons unter dem
   Cockpit):
   - `Re-Roll Word`: wuerfelt nur das Word neu.
   - `Re-Roll Op`: wuerfelt nur den Operator neu.
   - `Pick Archetype v`: Dropdown mit den 4 Archetypen, User waehlt
     manuell. (Anders als die anderen -- Archetype-Auswahl ist
     deterministischer Akt, nicht random.)

6. **Prompt-Output-Block** (monospace, pre-formatiert, scrollable wenn
   lang): Live-aktualisiert bei jeder Pick-Aenderung. Format:
   ```
   /crazy "<topic-from-input>" --force-archetype <a> --force-word <w> --force-operator <o>
   ```
   Wenn Topic leer -> Block zeigt `(enter a topic above)` als gedimmten
   Hint statt eines invaliden Prompts.

7. **Copy-Button** (primary): Kopiert den aktuellen Prompt-String in die
   Clipboard (Clipboard-API). Bei Erfolg "Copied!" fuer 1.5s daneben
   einblenden.

8. **field-notes-Context-Footer** (kompakt, klein, gedimmt):
   - `last archetype: <name> (streak: <n>)` -- aus inlined
     `FIELD_NOTES_RECENT` Daten.
   - `last word: <word>`.
   - **Streak-Warning** (Klaerung 5-(b)): wenn aktueller Picker-State
     einen 4. Streak produzieren wuerde, zeigt eine
     `jester would be streak 4 -- CLI variation-guard will re-roll` Zeile
     in orange.

### Theme

Dark, monospace fuer Picks/Prompt, system-font fuer UI-Elements.
Konsistent zum `playground`-Skill-Vorbild aus claude-plugins-official.

### Responsive

Cockpit kann auf schmaleren Viewports vertikal stapeln (3 Zellen
untereinander statt nebeneinander). Mobile-second-priority.

### No-JS-Fallback

HTML zeigt eine erklaerende Zeile "JavaScript required for the picker.
Use `/crazy <topic>` directly in your terminal as fallback." -- Single-
File, kein graceful-degradation darueber hinaus.

## Build-Skript `build_playground.py`

### CLI-Signatur

```bash
python skills/crazy-professor/scripts/build_playground.py \
  --output skills/crazy-professor/playground/index.html \
  --words skills/crazy-professor/resources/provocation-words.txt \
  --retired skills/crazy-professor/resources/retired-words.txt \
  --po-operators skills/crazy-professor/resources/po-operators.md \
  [--field-notes <target-project>/.agent-memory/lab/crazy-professor/field-notes.md] \
  [--version 0.12.0]
```

Stdlib-only, ~250 LOC. Liest Source-Resources, generiert eine HTML-Datei
mit inlined JS-Constanten und Body-Markup.

### Source-Reads

1. **`--words` + `--retired`**: gleiche Logik wie
   `picker.py:read_word_pool()` -- read pool, filter by retired set.
   Output: Liste aktiver Woerter (~150-200 Strings).

2. **`--po-operators`**: parse `## <Operator-Name>`-Headings, extrahiere
   die 4 Operator-Namen aus der Markdown-Datei. Output: `["reversal",
   "exaggeration", "escape", "wishful-thinking"]`. Hardcoded-Fallback
   wenn Parse fehlschlaegt: dieselbe Liste. (Wir haben in Phase 6 4
   Operatoren etabliert.)

3. **Archetype-Liste**: Hardcoded-Konstante im Build-Skript:
   `["first-principles-jester", "labyrinth-librarian",
   "systems-alchemist", "radagast-brown"]`. Diese 4 sind seit Phase 1
   stabil; ein neuer Archetype waere Master-Plan-Phase-Item.

4. **`--field-notes`** (optional): wenn gesetzt, parse die letzten 10
   Log-Rows analog `picker.py:read_last_log_rows()`. Output:
   `[{"archetype": "jester", "word": "smoke", "operator": "reversal"}, ...]`.
   Wenn Flag fehlt oder File nicht existiert -> leeres Array, Browser
   zeigt Footer "field-notes context: (no recent runs)".

5. **`--version`** (optional, default `"unknown"`): wird in den Header
   eingebettet. Skill ruft das mit aktueller `plugin.json`-Version auf.

### Output-Format (HTML-Template-Struktur)

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>crazy-professor -- Playground</title>
<style>
  /* ~150 lines of inlined CSS, dark theme, mono-font for picks */
</style>
</head>
<body>
<div class="header">crazy-professor -- Playground <span class="version">v0.12.0</span></div>
<div class="container">
  <input id="topic" placeholder="Topic..." autofocus>
  <div class="cockpit">
    <div class="cell" id="archetype-cell">...</div>
    <div class="cell" id="word-cell">...</div>
    <div class="cell" id="op-cell">...</div>
  </div>
  <button id="roll-all">Roll All</button>
  <div class="reroll-row">
    <button id="reroll-word">Re-Roll Word</button>
    <button id="reroll-op">Re-Roll Op</button>
    <select id="archetype-pick">...</select>
  </div>
  <pre id="prompt-output">...</pre>
  <button id="copy">Copy Prompt</button>
  <span id="copy-feedback"></span>
  <div class="field-notes-footer">...</div>
</div>
<script>
const VERSION = "0.12.0";
const ARCHETYPES = ["first-principles-jester", "labyrinth-librarian", "systems-alchemist", "radagast-brown"];
const OPERATORS = ["reversal", "exaggeration", "escape", "wishful-thinking"];
const WORDS = [...];  // ~150-200 strings inlined
const FIELD_NOTES_RECENT = [...];  // up to 10 rows, may be empty

// State + render logic, ~150 LOC
const state = { topic: "", archetype: null, word: null, operator: null };
function rollAll() { ... }
function rerollWord() { ... }
function rerollOp() { ... }
function pickArchetype(value) { ... }
function updatePrompt() { ... }
function copyPrompt() { ... }
function renderFieldNotesFooter() { ... }
function streakWarning() { ... }
// Wire up all listeners on DOMContentLoaded.
</script>
</body>
</html>
```

### JS-Logic-Highlights

- `rollAll()`: random pick from each pool, write to `state`, call
  `updateAll()`.
- `updateAll()`: re-render cockpit cells + prompt + footer +
  streak-warning.
- `streakWarning()`: zaehlt aufeinanderfolgende same-archetype rows in
  `FIELD_NOTES_RECENT` (von oben). Wenn Count >= 3 UND
  `state.archetype === last`, zeige Warning.
- `updatePrompt()`: baut den Prompt-String. Wenn `state.topic === ""`,
  zeige `(enter a topic above)` placeholder. Sonst:
  ```
  /crazy "<escaped-topic>" --force-archetype <a> --force-word <w> --force-operator <o>
  ```
  Topic wird via simple-quote-escape behandelt (`"` -> `\"`). Newlines
  im Topic werden gestripped.
- `copyPrompt()`: `navigator.clipboard.writeText(...)`, dann
  `copy-feedback` fuer 1.5s einblenden via `setTimeout`. Fallback wenn
  Clipboard-API fehlschlaegt: alert mit Anleitung "Copy manually".

### Edge-Cases

- **Empty word pool** (alle Woerter retired): Build schlaegt mit exit 2
  fehl, gleiche Logik wie `picker.py`.
- **Missing po-operators.md**: Build schlaegt mit exit 2 fehl.
- **Field-notes file path nicht existent**: warn auf stderr, leeres
  Array fuer `FIELD_NOTES_RECENT`, Build geht durch.
- **Build-Skript wird mehrmals aufgerufen**: idempotent -- ueberschreibt
  Output-File jedes Mal.

### Exit-Codes

- `0`: HTML written.
- `1`: Usage error (missing required args).
- `2`: Source-Resource fehlt oder unparseable.

## Slash-Command-Erweiterung

`commands/crazy.md` bekommt ein neues Argument-Pattern. Operating-
Instructions Step 1 wird um eine neue Zeile erweitert.

### Argument-Hint-Update

```yaml
argument-hint: [topic] [--chat] [--from-session] [--dry-run] [--compact] [--strict-cross-pollination] [--playground]
```

### Neue Bullet in commands/crazy.md

```markdown
- If `$ARGUMENTS` contains `--playground` (since v0.12.0, single-run only), run the build script and open the HTML playground in the user's browser. The skill: (1) calls `python <repo-root>/skills/crazy-professor/scripts/build_playground.py` with the current resource files and the local `.agent-memory/lab/crazy-professor/field-notes.md` (Desktop-fallback if local missing) as `--field-notes` source, (2) prints the absolute path of `<repo-root>/skills/crazy-professor/playground/index.html`, (3) opens the file via `webbrowser.open()` (or prints a `start file:///<path>` hint on Windows-Bash environments where `webbrowser.open()` is unreliable). The playground is browser-side only -- no LLM calls, no file writes from the browser. The user copies the generated prompt and runs it as a normal `/crazy <topic> --force-archetype X --force-word Y --force-operator Z` invocation in the terminal. `--playground` cannot combine with `--chat`, `--from-session`, or `--dry-run` -- these are rejected at the command layer with `--playground is single-run only and standalone (no --chat/--from-session/--dry-run combinations).`
```

### Operating-Instructions Step 1 Update

```markdown
- **`--playground` (since v0.12.0, single-run only):** instead of parsing a topic and generating provocations, run `python <repo-root>/skills/crazy-professor/scripts/build_playground.py` with the active resource files and the field-notes path. The script writes/refreshes `<repo-root>/skills/crazy-professor/playground/index.html`. The skill then opens the HTML file via the OS's default browser handler (Python `webbrowser.open()`). No topic is required -- the playground itself accepts the topic via its input field. Combining `--playground` with `--chat`, `--from-session`, or `--dry-run` is rejected with the message above.
```

### Reject-Matrix

| Combination | Action |
|---|---|
| `--playground` allein | Build + Open |
| `--playground --chat` | Reject (cross-mode) |
| `--playground --from-session` | Reject (cross-mode) |
| `--playground --dry-run` | Reject (cross-mode) |
| `--playground --compact` | Reject (`--compact` requires `--chat`, das wiederum mit `--playground` rejected ist) |
| `--playground --strict-cross-pollination` | Reject (gleiche Begruendung) |

Implementierung der Reject-Matrix: ein `if-Block` in der Skill-Logik
(nicht im Build-Skript, sondern im Step-1-Argument-Parsing).

### Skill-Output-Beispiel

```
Building playground from current resources...
Wrote: <abs-path>/skills/crazy-professor/playground/index.html
Opening in browser...

The playground is now open. Enter a topic, roll the picker, copy the prompt,
then paste it back here as a `/crazy <topic> --force-archetype X --force-word Y --force-operator Z` command.

Field-notes context: 7 recent rows loaded.
```

### Edge-Cases

- **Build schlaegt fehl** (z.B. `provocation-words.txt` fehlt): Skill
  druckt Fehler von `build_playground.py` (auf stderr), Skill-Step
  bricht ab. Keine Browser-Open-Attempt.
- **`webbrowser.open()` schlaegt fehl** (kein default browser
  konfiguriert, headless env): Skill druckt Pfad-Hinweis und sagt
  "Open this file manually: `file://<absolute-path>`". Kein Crash.
- **field-notes.md nicht existent** (frisches Projekt): Build geht durch
  mit leerem `FIELD_NOTES_RECENT`-Array. Browser-Footer zeigt "no recent
  runs".
- **Stale playground/index.html** (Resources im Repo wurden geaendert
  seit letztem Build): jeder `--playground`-Aufruf macht einen frischen
  Build. Stale ist nur moeglich wenn User das HTML-File direkt aufruft,
  ohne Slash-Command.

## Picker-Erweiterung

`picker.py` bekommt zwei neue Force-Flags analog zu `--force-archetype`
(Mikro-Frage A-(a)). Variation-Guard schlaegt Force konsistent
(Mikro-Frage B-(b)).

### Neue CLI-Args

```python
p.add_argument("--force-word", help="bypass word random pick (variation-guard still applies)")
p.add_argument("--force-operator",
               choices=("reversal", "exaggeration", "escape", "wishful-thinking"),
               help="bypass operator random pick (variation-guard still applies)")
```

### Logic in `pick_single()`

```python
def pick_single(args, words: list[str], rows: list[dict], ts: dt.datetime) -> dict:
    archetype, operator, ts_iso = picker_seed(ts, wishful_share=args.wishful_share)
    if args.force_archetype:
        archetype = args.force_archetype
    if args.force_operator:
        operator = args.force_operator
    word = pick_word(words, ts)
    if args.force_word:
        if args.force_word in words:
            word = args.force_word
        else:
            print(f"warning: --force-word {args.force_word!r} not in active pool "
                  f"(retired or unknown), falling back to random pick",
                  file=sys.stderr)
    archetype, word, re_rolled = variation_guard(archetype, word, rows, words, ts)
    forced_markers = []
    if args.force_archetype:
        forced_markers.append("forced-archetype")
    if args.force_word:
        forced_markers.append("forced-word")
    if args.force_operator:
        forced_markers.append("forced-operator")
    if forced_markers:
        prefix = "+".join(forced_markers)
        re_rolled = prefix if re_rolled == "no" else f"{prefix}+{re_rolled}"
    return {
        "timestamp": ts_iso,
        "mode": "single",
        "archetype": archetype,
        "word": word,
        "operator": operator,
        "re_rolled": re_rolled,
        "field_notes_rows_read": len(rows),
    }
```

### Variation-Guard-Verhalten bei Force

- `--force-archetype X` + 3-streak X -> Variation-Guard rolled archetype
  neu, `re_rolled` enthaelt `forced-archetype+archetype`.
- `--force-word smoke` + smoke in last 10 rows -> Variation-Guard rolled
  word neu, `re_rolled` enthaelt `forced-word+word`.
- `--force-operator reversal` -> Variation-Guard hat keinen Operator-
  Guard heute (`picker.py` heute nicht), also Force gilt immer.
  `re_rolled` enthaelt `forced-operator`.
- Browser-State + Streak-Warning hat User bereits gewarnt -- Diskrepanz
  ist also dokumentiert und vorausgesehen.

### Konsistenz mit Phase-2-Pattern

Heute existiert `forced-archetype` als `re_rolled`-Wert; das wird nicht
gebrochen. Neue Werte:
- `forced-word` (neu, allein)
- `forced-operator` (neu, allein)
- `forced-archetype+forced-word` (neu, kombiniert)
- `forced-archetype+forced-word+forced-operator` (neu, alle drei)
- `forced-word+word` (neu, mit guard-trigger)
- `forced-operator+forced-word+word` (neu, kombiniert mit guard)
- usw.

`telemetry.py:validate_record` ist permissive bei `re_rolled` (kein
Enum-Check) -- neue Werte fliessen ungestoppt durch.

`eval_suite.py:run_picker_once` validiert `re_rolled` mit Pattern-Match
-- `re_rolled.split("+", 1)[0]` muss in `VALID_RE_ROLLED` oder mit
`forced-` starten:

```python
VALID_RE_ROLLED = {"no", "archetype", "word", "both"}
```

Diese Logik (siehe heutigen Code) erlaubt schon `forced-archetype`
durch die `startswith("forced-")`-Klausel. Neue Force-Marker
(`forced-word`, `forced-operator`) starten ebenfalls mit `forced-` ->
Eval-Suite passt automatisch durch. **Kein Edit an Stage A noetig** fuer
die `re_rolled`-Validation.

### `pick_chat()`-Verhalten

Chat-Mode bekommt KEINE Force-Flags (Klaerung 3-(a): Chat-Mode bleibt
out-of-scope fuer Phase-7-Browser). `pick_chat()` bleibt unveraendert.

### Edge-Cases

- **`--force-word smoke` mit smoke in retired-words.txt**: warn auf
  stderr, fallback zu random. (Wenn User explizit retired-Wort forcen
  will, ist das Datenintegritaets-Problem beim User -- wir warnen nur.)
- **`--force-operator wishful-thinking` mit `--wishful-share 0.0`**:
  Force gewinnt. Operator-Liste wird ohnehin nur fuer Random-Picks
  gebraucht. Kein Konflikt.
- **`--force-archetype X --force-archetype Y`** (Argparse erlaubt nur
  ein Wert): zweites ueberschreibt erstes (Standard-argparse-Verhalten).
  Nicht unser Problem, kein Edge-Case-Code.

## Eval-Suite Stage F

Klaerung 7-(c): Telemetrie unveraendert, Eval-Suite bekommt eine neue
Stage F als Quality-Gate fuer Build-Skript + Daten-Konsistenz.

### Stage F — 8 Asserts

1. **Build runs clean**: `build_playground.py` mit gueltigen Args
   laeuft mit exit 0 und schreibt eine output-Datei.
2. **HTML is well-formed**: Output beginnt mit `<!DOCTYPE html>`, hat
   `<head>`, `<body>`, schliesst sauber. Simple Regex-Check (kein
   voller Parser).
3. **VERSION-Constant matches**: HTML enthaelt
   `const VERSION = "<expected-version>"` genau wie via `--version`
   uebergeben.
4. **WORDS-Konsistenz**: HTML enthaelt `const WORDS = [...]` mit der
   genau erwarteten Anzahl Strings -- verglichen mit
   `read_word_pool(words, retired)` der Source-Files. Drift-Detection.
5. **OPERATORS-Konsistenz**: HTML enthaelt genau `["reversal",
   "exaggeration", "escape", "wishful-thinking"]` als
   `const OPERATORS`. Phase-6-konsistent.
6. **ARCHETYPES-Konsistenz**: HTML enthaelt genau die 4 erwarteten
   Archetypen als `const ARCHETYPES`.
7. **FIELD_NOTES_RECENT inlined**: bei `--field-notes <empty-file>`
   ist `FIELD_NOTES_RECENT = []`. Bei `--field-notes
   <synthetic-with-3-rows>` enthaelt die Konstante 3 Objekte mit
   `archetype`, `word`, `operator`-Keys.
8. **Build-Skript-Reject ohne `--output`**: ohne required arg -> exit 1.

### CLI-Erweiterung in `eval_suite.py`

```python
p.add_argument("--build-playground", type=Path, default=None,
               help="path to build_playground.py for Stage F smoke")
p.add_argument("--po-operators", type=Path, default=None,
               help="path to po-operators.md (required for Stage F)")
p.add_argument("--playground", action="store_true",
               help="run Stage F (playground build smoke)")
```

### Wire-up in `main()`

```python
playground_results: dict | None = None
if args.playground:
    if not args.build_playground:
        print("error: --build-playground is required when --playground is set",
              file=sys.stderr)
        return 2
    if not args.po_operators:
        print("error: --po-operators is required when --playground is set",
              file=sys.stderr)
        return 2
    playground_results = stage_f_playground_build_smoke(
        args.build_playground, args.words, args.retired,
        args.po_operators, tmp_dir,
    )
```

### Render-Funktion

```python
def render_playground_section(stage: dict) -> list[str]:
    return _render_stage_section("Playground build smoke (Stage F)", stage)
```

Aufrufe in `render_report` an beiden Stellen (corpus-None-branch +
main-branch) analog zu Stage C/D/E.

### Erwartete Eval-Baseline nach Phase 7

- Stage A Picker: 200/200 PASS (now also tests `--force-word` and
  `--force-operator` indirectly via `forced-` re_rolled values -- kein
  neuer Assert noetig).
- Stage B Telemetry + Run-Planner: PASS unveraendert.
- Stage C Compact: 5/5 PASS unveraendert.
- Stage D Cross-Pollination: 8/8 PASS unveraendert.
- Stage E Wishful: 6/6 PASS unveraendert.
- **Stage F Playground (NEU)**: 8/8 PASS.

Total **27 Asserts in den new-stages**, ~235 Asserts in der gesamten
Eval-Baseline.

## Telemetrie

**Keine Aenderung** (Klaerung 7-(c)). Schema bleibt v0.11.0-Stand. Kein
neues optionales Feld. Kein `triggered_via`-Flag.

Begruendung-Reminder: Phase-6-Active-Warning sagt "erst Daten beobachten
bevor weitere Erweiterungen". Browser-getriggerte Runs sind aus
Telemetrie-Sicht ununterscheidbar von direkten CLI-Runs (Klaerung
1-(a): Browser ist nur Picker, finaler Run im Terminal).

## Versions-Bump v0.11.0 -> v0.12.0

MINOR per VERSIONING.md, neue user-visible Surface.

8 Frontmatter-Files zu bumpen:

- `.claude-plugin/plugin.json`
- `skills/crazy-professor/SKILL.md`
- `skills/crazy-professor/resources/output-template.md`
- `skills/crazy-professor/resources/chat-output-template.md`
- `docs/chat-mode-flow.md`
- `skills/crazy-professor/prompt-templates/chat-curator.md`
- `skills/crazy-professor/prompt-templates/chat-round-1-wrapper.md`
- `skills/crazy-professor/prompt-templates/chat-round-2-wrapper.md`

`build_playground.py`-Script bekommt kein eigenes Frontmatter
(Module-Docstring reicht).

## Doku-Updates

### `docs/CHANGELOG.md`

Neuer Eintrag oben:

```markdown
## [v0.12.0] [2026-04-DD] Phase 7 — Single-File-HTML-Playground

**Versions-Bump-Begruendung (per VERSIONING.md):** MINOR-Bump weil ein
neues user-visible Subsystem (HTML-Playground + Slash-Command-Flag)
hinzukommt. Master-Plan-Phase 7 abgeschlossen (6/8 -> 7/8 Phasen).

- 7.1 `/crazy --playground`-Flag: triggert das neue Build-Skript
  scripts/build_playground.py, schreibt frisches HTML nach
  playground/index.html, oeffnet via webbrowser.open(). Reject-Matrix
  gegen --chat / --from-session / --dry-run / --compact /
  --strict-cross-pollination.
- 7.2 Browser-Playground (Single-File-HTML): Cockpit-Layout mit Topic-
  Input + 3-Element-Picker (Archetype/Word/Operator), Roll-All und per-
  Element-Re-Roll-Buttons, Live-Prompt-Output mit Copy-Button. Field-
  notes-Footer zeigt letzten Archetype + Streak-Warnung. Pure-Static
  (inlined Daten + JS), file://-tauglich, kein Server.
- 7.3 picker.py --force-word und --force-operator: zwei neue Flags
  analog zu --force-archetype. Variation-Guard schlaegt Force konsistent.
  Neue re_rolled-Werte (forced-word, forced-operator, kombinierte Marker
  mit +).
- 7.4 Build-Skript build_playground.py (~250 LOC, stdlib-only): liest
  Resources, parsed po-operators.md fuer die 4 Operator-Namen, liest
  optional die letzten 10 field-notes-Rows, generiert HTML mit inlined
  JS-Constants. Idempotent.
- Eval-Suite Stage F (neu) mit 8 deterministischen Asserts: Build-
  Skript-Smoke, HTML-Wohlgeformtheit, VERSION/WORDS/OPERATORS/ARCHETYPES-
  Konsistenz, FIELD_NOTES_RECENT-Inlining, Reject-ohne-required-Args.
- Telemetrie: keine Aenderung (Klaerung 7-(c) -- Schema-Pause respektiert
  Phase-6-Active-Warning).
- Workflow-Pattern: brainstorming -> spec -> plan -> executing-plans
  (inline) -- dritte vollstaendige Anwendung nach Phase 5+6.
```

### `docs/PROJECT.md`

"Aktueller Stand"-Zeile auf v0.12.0, Master-Plan 7/8.

### `docs/CAPABILITIES.md`

Neue Zeilen:

- `/crazy --playground`-Flag (aktiv, 2026-04-DD)
- Browser-Playground (Single-File-HTML, aktiv, 2026-04-DD)
- `picker.py --force-word` und `--force-operator` (aktiv, 2026-04-DD)
- `build_playground.py` als 9. Skript (aktiv, 2026-04-DD)

### `docs/ARCHITECTURE.md`

Komponentendiagramm-Erweiterung um Browser-Playground-Box (parallel zum
Single-Run-Path, mit Pfeil zurueck zum Slash-Command). Skripte-Liste um
`build_playground.py` erweitert.

### Master-Plan-Status

`docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md`:

```markdown
| 7     | **Visionaere Erweiterung — GUI/Playground**                          | Single-File-HTML-Playground analog zur `playground` Skill; Browse/Compare/Keep/Retire UI                | (2026-04-DD)     |
```

### `docs/linters.md`

Keine Aenderung (Stage F testet Build-Skript, nicht einen Linter).

### Pflicht-Dokus die nicht angefasst werden

- `docs/VERSIONING.md` -- Policy stabil.
- `docs/eval-baseline-2026-04-28.md` -- bleibt liegen, neuer Report
  kommt als `docs/eval-baseline-<release-date>.md`.
- `skills/crazy-professor/scripts/lint_voice.py`, `lint_word_pool.py`,
  `lint_cross_pollination.py`, `validate_output.py`, `telemetry.py` --
  unveraendert.
- `commands/crazy.md` -- minimal-erweitert (Argument-Hint + 1 neuer
  Bullet), keine andere Logik beruehrt.

### Spec + Plan im `docs/`-Verzeichnis (Phase-5-Convention)

- `docs/specs/2026-04-28-phase-7-playground-design.md` -- diese Spec.
- `docs/plans/2026-04-28-phase-7-playground-implementation.md` -- kommt
  aus dem naechsten Skill (writing-plans).

## Out-of-Scope, Risiken, offene Fragen

### Out-of-Scope fuer Phase 7 (explizit)

- Kein LLM-Call aus dem Browser (Klaerung 1-(a)).
- Kein lokaler HTTP-Server (Approach C).
- Kein Chat-Mode-Surface im Browser (Klaerung 3-(a)).
- Keine Self-Flag-Checkboxes im Browser (Klaerung 6-(a)).
- Kein File-System-Access aus dem Browser.
- Kein Variation-Guard im Browser-Picker (Klaerung 5-(b)).
- Kein neues Telemetrie-Feld (Klaerung 7-(c)).
- Kein Field-Notes-Update aus Browser (Klaerung 6-(a)).
- Keine Multi-Topic-Batches, kein Auto-Schedule, kein Webhook, kein Bot.
- Keine `--force-bypass-guard`-Flag im Picker (Mikro-Frage B-(b)).

### Risiken & Mitigations

- **Risiko**: `webbrowser.open()` schlaegt in Headless-Environments oder
  bei missing-default-browser fehl. *Mitigation*: Skill druckt Pfad-
  Hinweis als Fallback (`Open this file manually: file://<path>`).
  Eval-Suite-Stage F testet das nicht (nur Build), aber Skill-Logik
  handelt es ohne Crash.
- **Risiko**: Daten-Drift zwischen `provocation-words.txt` und inlined
  `WORDS` in `playground/index.html`, wenn User das HTML direkt oeffnet
  ohne `--playground`-Trigger. *Mitigation*: Slash-Command `--playground`
  MACHT immer einen frischen Build. Stage F prueft Drift-Szenario via
  Counts-Match. Wenn User das HTML manuell statt via Slash-Command
  oeffnet, ist Drift moeglich -- Doku in `playground/README.md` (klein,
  ~10 Zeilen) erklaert "always open via `/crazy --playground`".
- **Risiko**: `build_playground.py` parsed `po-operators.md` mit
  Markdown-Heading-Regex; wenn Markdown-Format zukuenftig aendert, bricht
  Parse. *Mitigation*: Hardcoded-Fallback in Build-Skript fuer die 4
  bekannten Operatoren. Build geht mit Warning durch wenn Parse
  fehlschlaegt.
- **Risiko**: Browser-Playground wird genutzt, aber Telemetrie hat keine
  Sicht (kein `triggered_via`-Feld). User kann nicht aus Daten
  zurueckrechnen, ob Browser den Use-Case verbessert. *Mitigation*:
  Phase-7-Beobachtungs-Phase. Wenn nach 2-4 Wochen Browser-Use-Case
  sichtbar relevant wird, ist Phase-9-Erweiterung mit `triggered_via`
  machbar (analog Phase-6-Pattern).
- **Risiko**: User vergisst Topic einzugeben, kopiert leeren Prompt-
  Template. *Mitigation*: Browser-Prompt-Output zeigt placeholder
  `(enter a topic above)` statt invalidem Prompt. Copy-Button kopiert
  dann den Placeholder-String, was im Terminal als invalides Argument
  scheitert (klare Fehlermeldung).
- **Risiko**: Inlined `FIELD_NOTES_RECENT` ist im HTML stale, wenn User
  zwischen Browser-Open und Copy-Paste mehrere CLI-Runs gemacht hat.
  *Mitigation*: Streak-Warnung kann underschaetzen, aber CLI-Variation-
  Guard liest immer fresh field-notes.md -> Final-Output ist niemals
  falsch, nur die Browser-Vorschau ist evtl. veraltet. User triggert ggf.
  neuen `--playground`-Run fuer aktuelle Daten.

### Bekannte offene Fragen, bewusst auf Phase 8+ verschoben

- **Chat-Mode-Browser-Surface** (Phase-7.1-Kandidat): nach 2-4 Wochen
  Single-Run-Browser-Use kann entschieden werden, ob Chat-Mode ebenfalls
  Browser-Schicht braucht.
- **`triggered_via`-Telemetrie-Feld** (Phase-9-Kandidat): falls
  Daten-Auswertung relevant wird.
- **Field-Notes-Browser-Review-Surface** (Phase-9-Kandidat): falls User
  Self-Flags retrospektiv im Browser setzen wollen statt im Output-File.
- **Telegram-Bridge** (Phase 8): bleibt out-of-scope laut Master-Plan,
  Security-Audit als Vorbedingung.
- **`build_playground.py` Auto-Run**: aktuell nur via
  `/crazy --playground` getriggert. Ob ein Pre-Commit-Hook den Build
  automatisch refresht (analog `lint_word_pool.py` als Pre-Commit) ist
  Phase-9-Kandidat.

## User-Entscheidungen (Auditierbarkeit)

| # | Frage | Antwort | Wirkung im Spec |
|---|-------|---------|-----------------|
| 1 | LLM-Call vs. Pure-Playground | (a) Pure-Playground | Browser ist nur Picker + Prompt-Builder + Copy-Helper |
| 2 | Daten-Sync Mechanik | (b) JSON daneben -- revidiert via Approach C zu inlined JSON | Build-Skript baut Single-File-HTML mit eingebetteten Daten |
| 3 | Single + Chat oder nur Single | (a) nur Single | Chat-Mode bleibt Slash-Command-only |
| 4 | UI-Layout | (c) Cockpit | 3 Status-Zellen oben, Roll-All + per-Element-Re-Rolls |
| 5 | Variation-Guard im Browser | (b) Status zeigen, kein Guard | Footer mit field-notes-Context, Streak-Warnung, CLI bleibt Boss |
| 6 | Output-Mechanik | (a) Nur Prompt-Copy | Standard-CLI-Pfad rendert + persistiert |
| 7 | Telemetrie + Eval | (c) Build-Smoke nur | Stage F mit 8 Asserts, Telemetrie-Schema unveraendert |
| Mikro A | `picker.py` Force-Flags | (a) `--force-word` + `--force-operator` hinzufuegen | Picker bekommt 2 neue CLI-Flags, Variation-Guard greift weiterhin |
| Mikro B | Force vs. Guard | (b) Guard schlaegt Force | Konsistent zu `--force-archetype` heute |
| Approach | Distribution | C — Build-Only + File-Open | Inlined JSON im HTML, kein HTTP-Server, `file://` reicht |

## Annahmen

- **`webbrowser.open()` funktioniert auf macOS/Linux/Windows-Default-
  Setups** fuer `file://`-URIs. Falls nicht: Pfad-Hinweis-Fallback.
- **Inlined-Daten-Groesse (~5-10 KB fuer WORDS) ist akzeptabel** im
  HTML-File. HTML wird ~30-50 KB total -- gut handhabbar im Browser.
- **`po-operators.md` parse via Markdown-Heading-Regex bleibt stabil**:
  die Datei hat seit Phase 6 ein konsistentes `## <Name>`-Pattern. Falls
  future-edit das bricht, Hardcoded-Fallback faengt es ab.
- **User hat einen Default-Browser konfiguriert**: in ueber 99% der
  Desktop-Setups gegeben. Headless-Env (z.B. SSH-Sessions ohne
  X-Forwarding) ist nicht der Use-Case fuer Phase 7.
- **Sprach-Policy**: alle neuen Code-Files (HTML, JS, Python) in
  Englisch. Spec/Plan-Doku in Deutsch wie hier.

## Akzeptanzkriterien fuer Phase 7

- [ ] `/crazy --playground` triggert Build + Open
- [ ] `build_playground.py` produziert valide HTML mit inlined Daten
- [ ] Browser-Playground hat Topic-Input + 3-Element-Cockpit + Roll-All
      + Re-Roll-Buttons + Prompt-Output + Copy-Button + field-notes-
      Footer
- [ ] `picker.py --force-word` und `--force-operator` funktionieren
      analog zu `--force-archetype`
- [ ] Variation-Guard schlaegt Force konsistent (Mikro-Frage B-(b))
- [ ] Eval-Suite Stage F implementiert, alle 8 Asserts PASS
- [ ] Versions-Bump v0.12.0 in 8 Frontmatter-Files konsistent
- [ ] Master-Plan-Status auf 7/8 aktualisiert
- [ ] `docs/CHANGELOG.md` Phase-7-Eintrag mit Datum
- [ ] Plan-Datei
      `docs/plans/2026-04-28-phase-7-playground-implementation.md`
      erstellt durch writing-plans
- [ ] Lokale Self-Verification (Codex-Verifier-Pattern: 6+ Sessions in
      Folge nicht aufgerufen)
- [ ] Reject-Matrix fuer `--playground`-Kombinationen mit anderen Flags
