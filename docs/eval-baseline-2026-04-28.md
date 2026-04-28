# Eval Baseline 2026-04-28

- skill version: 0.12.0
- picker runs per archetype: 50
- corpus dir: `C:\Users\domes\AppData\Local\Temp\tmpacq0oikw\corpus`
- voice strict mode: False

## Picker (Stage B static)

| Archetype | Runs | OK | Pass-Rate | Unique Words | Operator Dist |
|---|---|---|---|---|---|
| first-principles-jester | 50 | 50 | 100.0% | 43 | escape=11, exaggeration=12, reversal=14, wishful-thinking=13 |
| labyrinth-librarian | 50 | 50 | 100.0% | 43 | escape=12, exaggeration=11, reversal=18, wishful-thinking=9 |
| systems-alchemist | 50 | 50 | 100.0% | 41 | escape=15, exaggeration=17, reversal=9, wishful-thinking=9 |
| radagast-brown | 50 | 50 | 100.0% | 40 | escape=15, exaggeration=11, reversal=13, wishful-thinking=11 |

All picker runs returned valid JSON with expected schema.

Operator coverage across all archetypes: ['escape', 'exaggeration', 'reversal', 'wishful-thinking'] (wishful-thinking seen: True)

## Corpus (Stage B linter sweep) -- 0 files

| Archetype | Files | Voice Pass | Voice Warn | Voice Fail | Validator Pass | Validator Fail |
|---|---|---|---|---|---|---|
| first-principles-jester | 0 | 0 | 0 | 0 | 0 | 0 |
| labyrinth-librarian | 0 | 0 | 0 | 0 | 0 | 0 |
| systems-alchemist | 0 | 0 | 0 | 0 | 0 | 0 |
| radagast-brown | 0 | 0 | 0 | 0 | 0 | 0 |

## Telemetry smoke (Stage B)

PASS -- append + round-trip + summary (summary OK)
- temp file: `C:\Users\domes\AppData\Local\Temp\tmpacq0oikw\.eval-tmp-n27mraqu\telemetry-smoke.jsonl`

## Run Planner smoke (Stage B)

PASS -- 8/8 asserts

- ok: archetype keyword match
- ok: archetype no match
- ok: archetype tie -> fallback
- ok: archetype case-insensitive substring
- ok: archetype empty topic -> exit 1
- ok: archetype missing keywords -> exit 2
- ok: session naechste schritte extraction
- ok: session multi-path dedup

## Compact-mode smoke (Stage C)

PASS -- 5/5 asserts

- ok: --compact reject documented
- ok: normal-mode chat output validates
- ok: compact-mode body validates
- ok: compact:true + normal order rejected
- ok: compact body without flag rejected

## Cross-pollination linter smoke (Stage D)

PASS -- 8/8 asserts

- ok: marker missing -> error
- ok: ref idx out of range -> error
- ok: ref to non-existent R1 item -> error
- ok: 0 overlap -> warn
- ok: overlap >= 1 -> pass
- ok: stop-word-only overlap -> warn
- ok: JSON output schema
- ok: exit 0 always

## Wishful-thinking picker smoke (Stage E)

PASS -- 6/6 asserts

- ok: share=0.0 -> only base operators
- ok: share=0.25 -> 1..50 wishful
- ok: share=1.0 -> all 4 present, wishful ~50%
- ok: invalid share rejected
- ok: validator accepts wishful-thinking
- ok: body with wishful scaffold validates

## Playground build smoke (Stage F)

PASS -- 8/8 asserts

- ok: build runs clean with required args
- ok: HTML well-formed
- ok: VERSION constant matches --version arg
- ok: WORDS count matches active pool
- ok: OPERATORS = 4 Phase-6 operators
- ok: ARCHETYPES = 4 active archetypes
- ok: FIELD_NOTES_RECENT = [] for empty field-notes
- ok: missing --output rejected
