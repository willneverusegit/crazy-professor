---
title: crazy-professor Phase 6 — Cross-Pollination + Kompakt-Modus (Design Spec)
date: 2026-04-28
phase: 6
master_plan: docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md
status: design (brainstorming output, awaiting writing-plans)
target_version: 0.11.0 (MINOR per VERSIONING.md)
implementation_order: 6.1 -> 6.2 -> 6.3
---

# Phase 6 — Cross-Pollination + Kompakt-Modus

## Executive Summary

Phase 6 erweitert den crazy-professor Chat-Mode um zwei optionale User-Flags
(`--compact`, `--strict-cross-pollination`) und aktiviert den 4. PO-Operator
(`wishful-thinking`) als kontrolliertes Feldtest-Set. Drei orthogonale
Sub-Features in einer Phase, jedes mit klarem Scope und ohne LLM-Call-Overhead
(Substanz-Check ist deterministische Heuristik, kein Codex-Critique).
Versions-Bump auf v0.11.0.

## Architektur-Uberblick

| Sub-Feature | Was greift wo ein | Neue Artefakte |
|---|---|---|
| **6.1 `--chat --compact`** | `commands/crazy.md` (Argument-Parsing), `chat-output-template.md` (Reorder + `<details>`), `validate_output.py` (Branch auf `compact: true`) | Frontmatter-Feld `compact`, kein neues Skript |
| **6.2 `--strict-cross-pollination`** | Neues Skript `lint_cross_pollination.py`, Step C4b in Operating-Instructions, R2-Sektion bekommt `[low-substance: <reason>]`-Marker | Neues Linter-Skript (~200-250 LOC), neue Resource `stop-words.txt` |
| **6.3 wishful-thinking aktiv** | `picker.py` (Operator-Liste + `--wishful-share`), `po-operators.md` (Voll-Section), `validate_output.py` (akzeptierte Operator-Werte) | Picker-CLI-Flag, Resource-Update |

**Querschnittsthemen:**

- **Telemetrie-Schema**: 3 neue OPTIONALE Felder (`compact_mode`, `low_substance_hits`, `wishful_thinking_active`). Phase-4-Vertrag eingehalten.
- **Eval-Suite**: 3 neue Smoke-Test-Stages (C/D/E) mit insgesamt 19 deterministischen Asserts.
- **Versions-Bump**: v0.10.0 -> v0.11.0 (MINOR per VERSIONING.md).
- **Workflow**: brainstorming -> spec -> plan -> executing-plans (Pattern aus Phase 5).

## Sub-Feature 6.1: `--chat --compact`

### Command-Layer (`commands/crazy.md`)

Argument-Parsing erweitert:

- `--compact` ohne `--chat` -> Reject mit Fehlermeldung
  `--compact requires --chat. Single-run output is already flat.`
- `--chat --dry-run` bleibt rejected wie heute (Phase-5-Vertrag).
- `--chat --compact --dry-run-round1` -> erlaubt (alle drei orthogonal,
  `--dry-run-round1` betrifft nur den Round-1-Internal-Test).

### Output-Reorder (`chat-output-template.md`)

Heute (Normal-Mode):
Header -> Banner -> R1 -> R2 -> R3 -> Top-3 -> Next-Experiment -> Self-Flag.

Compact-Mode (Reorder + Toggle):

```markdown
---
skill: crazy-professor
mode: chat
compact: true
version: 0.11.0
...
---

# Chat: <topic>

**Mode:** chat | **Compact:** true | **Distiller:** <codex|claude>

> DIVERGENCE WARNING: ...

## Round 3 — Codex Distillation (Final 20)

### Jester-5
1. ...
### Librarian-5 ...
### Alchemist-5 ...
### Radagast-5 ...

## Top-3 Cross-Pollination Hits
1. ...
2. ...
3. ...

## Next Experiment
<one concrete test>

## Self-Flag (for field-notes.md)
- [ ] kept
- [ ] round2-degraded
- [ ] distiller-fallback

---

<details>
<summary>Audit-Trail — Round 1 + Round 2 (click to expand)</summary>

## Round 1 — Parallel Voices

### Jester (word: <w>, op: <op>)
1. ...

### Librarian ...
### Alchemist ...
### Radagast ...

## Round 2 — Cross-Pollination

### Jester (counter/extend)
1. counter: alchemist #3 — <idee>
...

### Librarian ...
### Alchemist ...
### Radagast ...

</details>
```

Normal-Mode bleibt heute exakt wie er ist. Nur wenn `compact: true` im
Frontmatter steht, wird die Audit-Trail-Reihenfolge angewendet.

### Validator-Anpassung (`validate_output.py`)

Branch auf `compact` im Frontmatter:

- `compact: false` (oder fehlt) -> heutige Validierung unverandert.
- `compact: true` -> Reihenfolge geprueft als:
  Header -> Banner -> R3 -> Top-3 -> Next-Experiment -> Self-Flag -> `<details>`-Block mit R1+R2.
- Innerhalb von `<details>` werden R1 und R2 weiter mit derselben Logik geprueft
  (5 pro Archetype in R1, counter/extend-Marker in R2).

Ein neuer Helfer `parse_chat_sections(text, compact: bool)` kapselt die
Reihenfolge-Logik.

### Frontmatter-Schema-Erweiterung

`compact: bool` — neu in `chat-output-template.md` Frontmatter. Optional,
default `false` wenn nicht gesetzt.

### Edge-Case bei degraded-R2

Wenn `round2_status: degraded` (>=2 Archetypes <2 R2-Items), dann gibt es
keine R2-Items — `<details>`-Block enthalt nur R1. Das ist heute schon ein
Edge-Case und bleibt es: Audit-Trail zeigt R1, R2-Header mit "skipped —
degraded" wie heute.

## Sub-Feature 6.2: `--strict-cross-pollination`

### Skript: `lint_cross_pollination.py` (neu)

CLI-Signatur:

```bash
python skills/crazy-professor/scripts/lint_cross_pollination.py \
  --r1-input <r1-json-or-md> \
  --r2-input <r2-json-or-md> \
  [--min-overlap 1] \
  [--stop-words <repo-root>/skills/crazy-professor/resources/stop-words.txt]
```

Stdlib-only, ~200-250 LOC.

**Eingaben** (eines von beidem):

- Direkter Markdown-Block der R2-Sektion + R1-Items separat — oder
- Bereits geparste JSON-Struktur `{archetype: {idx: text, ...}, ...}` fuer R1 und R2.

Default in Step C4b: das Skill ubergibt R1+R2 als bereits geparste
JSON-Struktur (was im Skill-Flow ohnehin in-memory liegt). Ein zweiter
Standalone-Mode mit Markdown-Eingabe macht den Linter testbar via Eval-Suite
mit Corpus-Files.

### Heuristik-Pipeline (3 Checks pro R2-Item)

1. **Marker-Existenz**: R2-Item beginnt oder endet mit `counter: <ref>` oder
   `extend: <ref>` (case-tolerant, separator `:`). Wenn Marker fehlt ->
   `severity: error, reason: "no counter/extend marker"`. Item wird als
   low-substance flagged.

2. **Ref-Aufloesung**: `<ref>` matcht das Pattern `<archetype-name> #<int>`
   mit `archetype-name in {jester, librarian, alchemist, radagast|radagast-brown}`
   (case-tolerant) und `<int>` zwischen 1 und 5. Wenn Ref kein gueltiger
   R1-Index ist -> `severity: error, reason: "ref does not resolve to existing R1 item"`.
   Item flagged.

3. **Token-Overlap**: R2-Item-Text und referenziertes R1-Item-Text werden
   tokenisiert (split auf Whitespace + Punktuation, lowercase, Stop-Words
   rausfiltern, Tokens <3 Zeichen rausfiltern). Set-Intersection berechnet.
   Wenn `len(overlap) < min_overlap` (Default 1) ->
   `severity: warn, reason: "token overlap with ref < {n}"`. Item flagged.

Ein Item kann mehrere Reasons sammeln. Marker-fehlt + Ref-ungueltig
schliessen sich faktisch aus (kein Marker = kein Ref).

### Stop-Words-Resource (`resources/stop-words.txt`) — neu

Eine Datei pro Sprache-Mix (Englisch + Deutsch, weil Picker-Output beides
mischt). ~80-100 Stop-Words. Beispiele: `the, is, of, and, der, die, das,
ist, von, und, in, on, at, mit, auf, fuer, zu, ein, eine`. Plus
archetype-Eigennamen (`jester, librarian, alchemist, radagast`) damit
"counter: jester #2" nicht das Wort "jester" als Overlap zaehlt.

### Output (JSON auf stdout)

```json
{
  "low_substance_hits": 2,
  "findings": [
    {
      "archetype": "jester",
      "idx": 2,
      "ref": "alchemist #3",
      "severity": "warn",
      "reason": "token overlap with ref < 1"
    },
    {
      "archetype": "radagast",
      "idx": 1,
      "ref": null,
      "severity": "error",
      "reason": "no counter/extend marker"
    }
  ],
  "stats": {
    "r2_items_total": 12,
    "r2_items_flagged": 2,
    "by_severity": {"error": 1, "warn": 1}
  }
}
```

Exit-Code: `0` (immer, weil warn-only). Skill liest stdout-JSON, ergaenzt
R2-Sektion mit `[low-substance: <reason>]`-Marker direkt in der Item-Zeile,
schreibt File. Telemetrie-Feld `low_substance_hits` aus dem JSON-Output.

### Operating-Instructions: Step C4b (neu, zwischen C4 und C5)

```
**Step C4b: Cross-Pollination Substanz-Check (when --strict-cross-pollination
is set, since v0.11.0).**

If --strict-cross-pollination is active, run the cross-pollination linter
on R2 output:

[bash-Block analog zu lint_voice]

Parse JSON output. For each finding, locate the R2 item and append
"[low-substance: <reason>]" at the end of the line. The findings count
goes into telemetry field low_substance_hits in Step C7b.

Without --strict-cross-pollination this step is skipped entirely.
```

### Visibility im Output-File

Im Normal-Mode (R2 nicht in `<details>`): Marker direkt sichtbar. Im
Compact-Mode (R2 in `<details>`-Audit-Trail): Marker steht im
Audit-Trail-Block, nicht primaer sichtbar. Round 3 (Codex-Distillation)
bekommt R2 inklusive Marker als Input — Codex sieht die Flags und kann sie
selbst gewichten. Top-3-Hits-Sektion koennte Marker mit-zitieren
(Codex-Verhalten, nicht erzwungen).

### Edge-Cases

- R2 ist `degraded` (Step C4 hat das gesetzt) -> Linter wird gar nicht
  aufgerufen, weil keine R2-Items existieren. Telemetrie
  `low_substance_hits: 0`, `round2_status: skipped`.
- R2 hat ein Item, das ist ein doppeltes counter (z.B. zwei Items mit
  `counter: alchemist #3`) -> kein Linter-Issue, das ist erlaubt.
- R2-Item hat Marker, aber `<ref>` ist `librarian #6` (ausserhalb 1-5) ->
  Ref-Resolution-Fehler.
- Token-Overlap mit `min-overlap=0` -> effektiv deaktiviert die
  Overlap-Pruefung. Default 1 bleibt.

## Sub-Feature 6.3: wishful-thinking PO-Operator

### `po-operators.md` — Voll-Section ergaenzt

V2-Reservierungs-Notiz wird angepasst (von "drei Operatoren reserviert fuer
V2" zu "wishful-thinking aktiviert in v0.11.0, distortion+arising weiter
reserviert"). Neue Section analog zu den drei bestehenden:

```markdown
## Wishful Thinking

Postulate something the system explicitly cannot do, then observe what
constraint that breaks. Not for the wish itself -- for what the
impossibility reveals about the boundary. The operator names a desire
that is materially blocked, then forces thinking sideways into "what
if the block were removed".

Example scaffold:
  "Wishful thinking: <X> happens without <prerequisite>."
  "Wishful thinking: <subject> can <verb> without <constraint>."

Distinction from Reversal: reversal swaps an existing relationship.
Wishful thinking removes a precondition that gates the action entirely.
Distinction from Escape: escape removes a feature; wishful thinking
removes a prerequisite that the system normally requires before the
feature can run.
```

Plus Update der "Rules for All Three" Sektion auf "Rules for All Four" —
Inhalt unverandert.

### `picker.py` — Operator-Liste + Share-Flag

Neue CLI-Option:

```
--wishful-share <float> (default: 0.25, range: 0.0-1.0)
```

Operator-Liste wird dynamisch:

- Default-Operatoren: `["reversal", "exaggeration", "escape"]` (Gewichte je 1).
- Wenn `wishful-share > 0`: Liste wird
  `["reversal", "exaggeration", "escape", "wishful-thinking"]` mit Gewichten
  `[1, 1, 1, share * 3]`. Renormalisierung passiert automatisch durch
  `random.choices`.

  Beispiel `share=0.25`: Gewichte `[1, 1, 1, 0.75]` -> relative Anteile
  ~28.6%/28.6%/28.6%/14.3%. Hinweis: das ist KEIN sauberes 25/25/25/25 —
  der Share-Wert kontrolliert das Verhaltnis, nicht den Absolut-Anteil.
  Bei `share=0.333` waeren es ~25/25/25/25, bei `share=1.0` exakt 25/25/25/25.

  Doku-Note in `picker.py --help`: "Share is the weight relative to one
  default operator (1.0 = equal weight = 25% each, 0.5 = half weight = ~22%,
  0.25 = quarter weight = ~14%)".

- Wenn `wishful-share == 0.0`: Liste bleibt 3-elementig wie heute, kein
  Verhalten-Bruch.

**Default-Konfig**: `0.25` ist Default-CLI-Argument. Der User kann via
`--wishful-share 0.0` zurueck zu 3-Operator-Modus, oder via `--wishful-share 1.0`
auf gleichmaessige 25%/25%/25%/25%-Verteilung.

### Skill-Flow

Die Operating-Instructions in Step 2b und C2 erwaehnen `--wishful-share`
nicht explizit als zu setzen — der Picker nutzt Default 0.25, was ab v0.11.0
das neue Verhalten ist. Ein Hinweis-Bullet in Operating-Instructions Step 2b:
"Picker since v0.11.0 may return `wishful-thinking` as 4th operator
(default share 0.25, relative weight)."

### `validate_output.py` — akzeptierte Operator-Werte

Output-Validator hat heute eine Liste erlaubter Operator-Werte (fuer
Frontmatter-Check und Body-Patterns). Liste wird ergaenzt um
`wishful-thinking`. Kein anderes Validator-Verhalten aendert sich.

### Field-Notes-Schema — keine Aenderung

`Operator`-Spalte akzeptiert heute beliebigen String. `wishful-thinking`
ist ein neuer moeglicher Wert, kein Schema-Bruch.

### `prompt-templates/*.md` — keine Aenderungen

Die Archetype-Templates verweisen auf `po-operators.md` als Quelle, nicht
auf eine eingebettete Operator-Liste. Wenn ein Template dennoch
Operator-Beispiele eingebettet hat (Suche-und-Pruefen-Schritt im Plan),
wird wishful-thinking dort ergaenzt.

### Edge-Case bei der Eval-Suite

Eval-Suite Stage A (`stage_a_picker_smoke()`) macht heute 50 Runs/Archetype
und prueft Pass-Rate. Mit `wishful-thinking` als 4. Operator bleibt das
deterministisch — Random-Seed-basierter Picker, gleiche Logik. Stage A
prueft KEINE Operator-Verteilung pro Archetype, nur dass jeder Operator
irgendwann gepickt wird ueber die 50 Runs. Bei `share=0.25` sollte
`wishful-thinking` in 50 Runs ~7-mal auftauchen — Stage A bekommt einen
neuen Assert: "alle 4 Operatoren mindestens 1x ueber alle 200 Picker-Runs
gesehen".

## Telemetrie-Schema-Erweiterung

3 neue OPTIONALE Felder (Phase-4-Vertrag: keine neuen required fields):

| Feld | Typ | Default | Wann gesetzt |
|---|---|---|---|
| `compact_mode` | `bool` | `false` | `true` wenn `--chat --compact` aktiv war (Single-Run: immer `false`, weil `--compact` dort rejected wird) |
| `low_substance_hits` | `int` | `0` | Aus `lint_cross_pollination.py` Output-JSON. Nur wenn `--strict-cross-pollination` lief — sonst `0` (oder Feld fehlt -> Reader behandelt als `0`) |
| `wishful_thinking_active` | `bool` | `false` | `true` wenn der gepickte Operator des Runs `wishful-thinking` war. Im Single-Run: trivial der String-Vergleich `operator == "wishful-thinking"`. Im Chat-Run: `true` wenn >=1 der 4 Picks `wishful-thinking` war |

### Schema-Doc-Update

Die Schema-Definition lebt im `telemetry.py`-Skript-Header
(Schema-Validation auf Append). Drei neue Felder werden in der
`KNOWN_OPTIONAL_FIELDS`-Liste eingetragen — ein Append mit nur den
Pflichtfeldern bleibt valide, ein Append mit den neuen Feldern ebenfalls.
Reader, die die neuen Felder nicht kennen, ignorieren sie (alle
JSONL-Reader sind Field-by-Name).

### Operating-Instructions Step 7b + C7b — Updates

Beide Steps bekommen einen neuen Bullet-Eintrag im "Optional fields since
v0.11.0":

```
- compact_mode (bool): true if --chat --compact was active. Single-run is always false.
- low_substance_hits (int): from lint_cross_pollination.py output. 0 if --strict-cross-pollination was not active.
- wishful_thinking_active (bool): true if any picked operator was 'wishful-thinking'.
```

### Was NICHT geloggt wird (bewusste Auslassung)

- `low_substance_refs`: die genaue Liste der geflaggten R2-Items. Aus dem
  Output-File rekonstruierbar (steht als `[low-substance: <reason>]`-Marker
  direkt in der R2-Sektion). Telemetrie soll flach bleiben.
- `wishful_thinking_share`: der effektive `--wishful-share`-Wert zur Run-Zeit.
  Aus dem `operator`-Feld empirisch rueckrechenbar (ueber N Runs zaehlen).
  Schema bleibt schmaler.
- Keine Ref-Liste beim Compact-Mode — `compact_mode: bool` reicht aus.

### Backward-Compatibility-Test

Eval-Suite-Stage `stage_telemetry_smoke()` schreibt heute Test-Records mit
den heute existierenden Feldern. Mit Phase-6 wird ein zweiter Test-Case
ergaenzt: ein Append-and-read-back mit den drei neuen Feldern. Beide
Test-Cases muessen passen -> Schema-Forward+Backward-Compatibility ist
gesichert.

## Eval-Suite-Erweiterung

3 neue Smoke-Test-Stages in `eval_suite.py`. Pattern wie Phase 5
(Stage B Run-Planner-Smoke): deterministische Asserts, kein LLM-Call,
Standalone-Aufruf via CLI-Flag.

### Stage C — Compact-Mode Smoke (`stage_c_compact_smoke()`)

5 Asserts:

1. **Reject**: `commands/crazy.md` (oder Skill-Logik) lehnt `--compact` ohne
   `--chat` mit erwarteter Fehlermeldung ab. Test: simuliert
   Argument-Parser-Aufruf, erwartet exit-non-zero + Substring `requires --chat`.
2. **Validator-Branch normal**: ein heutiges Chat-Output-File ohne
   `compact:`-Frontmatter wird vom Validator als gueltig akzeptiert
   (Regression).
3. **Validator-Branch compact**: ein synthetisches Compact-Mode-Output-File
   (Reorder R3 -> Top-3 -> Next-Exp -> Self-Flag -> `<details>`R1+R2) mit
   `compact: true` wird als gueltig akzeptiert.
4. **Validator-Reject falsche Compact-Reihenfolge**: ein File mit
   `compact: true` aber heutiger Reihenfolge (R1 zuerst) wird als ungueltig
   zurueckgewiesen.
5. **Frontmatter-Default**: ein Compact-File ohne explizites `compact: true`
   aber mit Reorder-Reihenfolge -> Validator nimmt Default `false` an und
   erwartet heutige Reihenfolge -> Reject. Sichert Schema-Konsistenz.

### Stage D — Cross-Pollination-Linter Smoke (`stage_d_cross_pollination_smoke()`)

8 Asserts:

1. **Marker-Existenz error**: R2-Item ohne `counter:`/`extend:` Marker ->
   severity `error`.
2. **Ref-Resolution error**: Marker `extend: librarian #6` (idx > 5) ->
   severity `error`.
3. **Ref-Resolution error 2**: Marker `counter: nonexistent #2` ->
   severity `error`.
4. **Token-Overlap warn**: R2-Text und R1-Ref-Text haben 0 Tokens overlap
   nach Stop-Word-Filter -> severity `warn`.
5. **Token-Overlap pass**: R2-Text enthaelt ein nicht-stopword-Token aus
   R1-Ref -> kein Finding.
6. **Stop-Word-Filter wirkt**: R2 + R1-Ref haben nur Stop-Words gemeinsam
   (`the`, `is`, `der`) -> severity `warn` (kein echter Overlap).
7. **JSON-Output-Schema**: Output ist gueltiges JSON mit Feldern
   `low_substance_hits, findings, stats`. Stats-Counts stimmen.
8. **Exit-Code 0 immer**: auch bei findings ist exit-code 0
   (warn-only-Vertrag).

### Stage E — Wishful-Thinking-Picker Smoke (`stage_e_wishful_thinking_smoke()`)

6 Asserts:

1. **Default-Verhalten v0.10.0** (Regression): `picker.py --wishful-share 0.0`
   ueber 200 Runs liefert nur `reversal/exaggeration/escape`, nie
   `wishful-thinking`.
2. **Default v0.11.0**: `picker.py --wishful-share 0.25` ueber 200 Runs
   liefert `wishful-thinking` mindestens 1x, hoechstens ~50 Mal (lockerer
   Rahmen, nicht exakte Verteilung weil deterministisch-aber-timestamp-getrieben).
3. **Vollwertiger 25/25/25/25-Modus**: `--wishful-share 1.0` ueber 200 Runs
   liefert alle 4 Operatoren aehnlich haeufig (jeder >=30, <=70 — lockere
   Schranken).
4. **CLI-Validation**: `--wishful-share -0.5` und `--wishful-share 1.5`
   werden als invalid abgelehnt (exit non-zero).
5. **Validator akzeptiert wishful-thinking**: ein Output-File mit
   `operator: wishful-thinking` im Frontmatter wird vom Validator akzeptiert.
6. **Validator-Body**: ein Output-Body, der einen wishful-thinking-Scaffold
   zitiert, wird nicht als Voice-Drift gewertet.

### Telemetry-Smoke-Erweiterung (`stage_telemetry_smoke()`)

2 neue Asserts angehaengt:

1. Append + read-back eines Records mit allen drei neuen Feldern
   (`compact_mode`, `low_substance_hits`, `wishful_thinking_active`).
2. Append + read-back eines Records OHNE die drei neuen Felder
   (Backward-Compat).

### CLI-Erweiterung in `eval_suite.py`

Neue Flags:

- `--compact` -> laeuft Stage C
- `--cross-pollination` -> laeuft Stage D
- `--wishful` -> laeuft Stage E

Default ohne Flag: alle Stages laufen (heute schon das Verhalten, kein
Bruch).

### Render im Baseline-Report

3 neue Sektionen im `docs/eval-baseline-<date>.md`:

- `## Compact-mode smoke (Stage C)` — 5 Asserts mit PASS/FAIL.
- `## Cross-pollination linter smoke (Stage D)` — 8 Asserts mit PASS/FAIL.
- `## Wishful-thinking picker smoke (Stage E)` — 6 Asserts mit PASS/FAIL.

### Erwartete Eval-Baseline (am Release-Datum)

- Picker (Stage A): 50 runs/archetype x 4 = 200/200 PASS, jetzt mit
  `wishful-thinking` in der Verteilung.
- Telemetry: PASS (heute + 2 neue Asserts).
- Run Planner (Stage B): 8/8 PASS (unveraendert).
- Compact (Stage C): 5/5 PASS.
- Cross-Pollination (Stage D): 8/8 PASS.
- Wishful (Stage E): 6/6 PASS.

**Total: 19 neue Asserts in den neuen Stages, ~227 in der gesamten
Eval-Baseline.**

## Doku, Versions-Bump, Out-of-Scope

### Versions-Bump v0.10.0 -> v0.11.0 (MINOR per VERSIONING.md)

8 Frontmatter-Files zu bumpen:

- `.claude-plugin/plugin.json`
- `skills/crazy-professor/SKILL.md`
- `skills/crazy-professor/resources/output-template.md`
- `skills/crazy-professor/resources/chat-output-template.md`
- `docs/chat-mode-flow.md`
- `skills/crazy-professor/prompt-templates/chat-curator.md`
- `skills/crazy-professor/prompt-templates/chat-round-1-wrapper.md`
- `skills/crazy-professor/prompt-templates/chat-round-2-wrapper.md`

Skripte in `skills/crazy-professor/scripts/` haben kein Frontmatter, nur
Module-Docstrings — kein Bump notwendig.

### `docs/CHANGELOG.md` — Eintrag

```markdown
## v0.11.0 — 2026-04-DD (Phase 6)

- New `--chat --compact` flag: reorders chat output so Round 3 (Final 20)
  + Top-3 + Next-Experiment appear first; Round 1+2 collapse into a
  `<details>` audit-trail block.
- New `--strict-cross-pollination` flag: runs deterministic substance
  heuristic on Round 2 markers. Findings appear as
  `[low-substance: <reason>]` markers in R2 items (warn-only).
- Wishful-thinking PO operator activated as 4th operator. Default
  `--wishful-share 0.25` (relative weight). Set `--wishful-share 0.0`
  to revert to v0.10.0 three-operator behavior.
- `--compact` without `--chat` is rejected at the command layer.
- 3 new optional telemetry fields: `compact_mode`, `low_substance_hits`,
  `wishful_thinking_active`. Backward-compatible.
- New helper script `lint_cross_pollination.py` (4th linter).
- Eval-suite extended with 3 new smoke stages (Stage C/D/E, +19 asserts).
```

### `docs/PROJECT.md`

"Aktueller Stand"-Zeile aktualisiert auf v0.11.0 + Master-Plan 6/8.

### `docs/CAPABILITIES.md`

Neue Zeilen:

- `--chat --compact`-Flag (Status: active, 2026-04-DD)
- `--strict-cross-pollination`-Flag (Status: active, 2026-04-DD)
- 4. PO-Operator wishful-thinking (Status: active, 2026-04-DD)

### `docs/ARCHITECTURE.md`

Kleine Erweiterung in der Skript-Liste: `lint_cross_pollination.py` als 4.
Linter. Output-Template-Reorder-Mechanik in der Output-Pipeline-Sektion
erwaehnt.

### Master-Plan-Update

`docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md`:
Phase-6-Zeile in der Phasen-Tabelle bekommt Status `(2026-04-DD)`.

### Pflicht-Dokus die nicht angefasst werden

- `docs/VERSIONING.md` — bleibt unveraendert (Policy stabil).
- `docs/linters.md` — wird leicht erweitert: 4. Linter mit Hinweis auf
  Step C4b.
- `docs/eval-baseline-2026-04-28.md` — bleibt liegen, neuer Report kommt
  als `docs/eval-baseline-<release-date>.md`.

### Spec + Plan im `docs/`-Verzeichnis (Phase-5-Convention)

- `docs/specs/2026-04-28-phase-6-cross-pollination-compact-design.md` —
  diese Brainstorming-Output-Spec.
- `docs/plans/2026-04-28-phase-6-cross-pollination-compact-implementation.md` —
  kommt aus dem naechsten Skill (writing-plans).

### Out-of-Scope fuer Phase 6 (explizit)

- Kein Codex-Critique-Call (war Approach (a) in Klaerungsfrage 3, verworfen).
- Kein Filtern oder Retry von R2-Items basierend auf Linter-Findings
  (Klaerung 4: warn-only).
- Kein Single-Run-`--compact` (Mikro-Frage: rejected am Command-Layer).
- Keine 5./6. PO-Operatoren (`distortion`, `arising` bleiben fuer
  V2-Reservierung).
- Kein Slow-Roll- oder Manual-Force-only fuer wishful-thinking
  (Klaerung 5: Share-basiert).
- Kein `low_substance_refs` in Telemetrie (Klaerung 6: drei Felder, keine
  Detail-Arrays).
- Kein Doc-Bump fuer `docs/VERSIONING.md` selbst (per Policy: VERSIONING.md
  ist Meta-Doku).

## Risiken & Mitigations

- **Risiko**: `lint_cross_pollination.py` produziert hohe False-Positive-Rate
  auf echten R2-Outputs -> `--strict`-Modus wird unbrauchbar. *Mitigation*:
  warn-only-Vertrag (Klaerung 4) — Findings filtern nichts. Telemetrie
  zeigt `low_substance_hits`-Verteilung ueber die ersten 10-20 Runs, dann
  entscheiden ob Heuristik nachjustiert werden muss (Phase-7-Kandidat).
- **Risiko**: Compact-Mode-Reorder bricht bestehende Markdown-Renderer
  (z.B. Obsidian-Wiki). *Mitigation*: `<details>`-Tag ist HTML in Markdown,
  von allen relevanten Renderern unterstuetzt. Eval-Suite Stage C prueft
  Validator-Verhalten, nicht Render.
- **Risiko**: `wishful-thinking`-Operator ist semantisch zu nah an `escape`
  -> Diversity-Verlust. *Mitigation*: `po-operators.md` hat explizite
  Distinction-Sektion. Nach 20-30 Runs in Telemetrie sichtbar
  (`wishful_thinking_active` + Output-Beobachtung).

## Bekannte offene Fragen, bewusst auf Phase 7+ verschoben

- Soll der Run Planner auch die PO-Operator-Wahl beeinflussen, oder bleibt
  Operator-Wahl zufaellig? (war schon in Phase-5-Master-Plan offen, weiter
  offen).
- Falls Heuristik in Phase 6 zu viele False-Positives produziert:
  Codex-Critique-Eskalation als Phase-7-Erweiterung (Approach C aus
  Klaerungsfrage 3).
- `low_substance_refs` als 4. Telemetrie-Feld nachziehen, falls nach 20
  Runs gewuenscht.

## User-Entscheidungen (Auditierbarkeit)

| # | Frage | Antwort | Wirkung im Spec |
|---|-------|---------|-----------------|
| 1 | Reihenfolge der Sub-Features | (a) — wie im Master-Plan | 6.1 -> 6.2 -> 6.3 |
| 2 | `--compact`-Schema | (b) — Reorder-und-Toggle | R3 primaer, R1+R2 in `<details>` |
| 3 | Substanz-Check-Mechanik | (b) — Lokale Heuristik | `lint_cross_pollination.py`, kein Codex |
| 4 | Verhalten bei low-substance | (a) — Warn-only | `[low-substance: <reason>]`-Marker, kein Filter |
| 5 | wishful-thinking Aktivierung | (b) Share-Wert | `--wishful-share 0.25` Default, relative Gewichte |
| 6 | Telemetrie-Felder | (c) Mittlerer Pfad | 3 Felder: compact_mode, low_substance_hits, wishful_thinking_active |
| Mikro | `--compact` ohne `--chat` | (a) — Reject | Command-Layer Reject mit Fehlermeldung |
| Approach | Code-Org fuer 6.2 | A — Eigenes Skript | `lint_cross_pollination.py` als 4. Linter |

## Annahmen

- **Token-Overlap-Heuristik ist gut genug**: angenommen wird, dass eine
  ehrliche Counter/Extend-Provokation mindestens ein nicht-stopword-Token
  des Referenz-Items aufgreift. Wenn Echteinsatz das widerlegt, wird in
  Phase 7 eine LLM-Critique-Eskalation eingebaut (Approach C aus Klaerung 3).
- **Stop-Word-Liste reicht fuer EN+DE-Mix**: angenommen wird, dass eine
  ~80-100-Wort-Liste den meisten Picker-Output-Mix abdeckt. Bei Bedarf
  erweiterbar als reine Resource-Aenderung.
- **`<details>`-Renderer-Support**: angenommen wird, dass alle relevanten
  Markdown-Renderer (GitHub, Obsidian, VS Code Preview) `<details>`-Tags
  korrekt darstellen. Falls nicht, ist der `<details>`-Block trotzdem
  lesbar als Inline-Block.
- **Picker-Renormalisierung mit `random.choices`**: angenommen wird, dass
  Pythons `random.choices(weights=...)` die korrekte Verteilung liefert.
  Stage E pruft das empirisch ueber 200 Runs.
- **Sprach-Policy**: alle neuen Code-Files in Englisch, Spec/Plan-Doku in
  Deutsch wie hier.

## Akzeptanzkriterien fuer Phase 6

- [ ] `--chat --compact` produziert reorderten Output mit `<details>`-Audit-Trail
- [ ] `--compact` ohne `--chat` wird mit Fehlermeldung abgelehnt
- [ ] `--strict-cross-pollination` ergaenzt R2-Items um `[low-substance: <reason>]`-Marker bei Findings
- [ ] `lint_cross_pollination.py` existiert, ist stdlib-only, exit-code 0 immer
- [ ] `wishful-thinking` ist 4. Operator, Default-Share 0.25, ueber `--wishful-share 0.0` deaktivierbar
- [ ] `po-operators.md` enthaelt Voll-Section fuer wishful-thinking
- [ ] 3 neue optionale Telemetrie-Felder dokumentiert und in eval-suite getestet
- [ ] Eval-Suite Stages C/D/E implementiert, alle Asserts PASS
- [ ] Versions-Bump v0.11.0 in 8 Frontmatter-Files konsistent
- [ ] Master-Plan-Status auf 6/8 aktualisiert
- [ ] `docs/CHANGELOG.md` Phase-6-Eintrag mit Datum
- [ ] Plan-Datei `docs/plans/2026-04-28-phase-6-cross-pollination-compact-implementation.md` erstellt durch writing-plans
- [ ] Lokale Self-Verification (Codex-Verifier-Pattern: weiter nicht aufrufen, 5+ Sessions)
