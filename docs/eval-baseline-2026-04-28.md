# Eval Baseline 2026-04-28

- skill version: 0.10.0
- picker runs per archetype: 50
- corpus dir: `(none)`
- voice strict mode: False

## Picker (Stage B static)

| Archetype | Runs | OK | Pass-Rate | Unique Words | Operator Dist |
|---|---|---|---|---|---|
| first-principles-jester | 50 | 50 | 100.0% | 43 | escape=17, exaggeration=17, reversal=16 |
| labyrinth-librarian | 50 | 50 | 100.0% | 42 | escape=20, exaggeration=14, reversal=16 |
| systems-alchemist | 50 | 50 | 100.0% | 43 | escape=16, exaggeration=18, reversal=16 |
| radagast-brown | 50 | 50 | 100.0% | 46 | escape=13, exaggeration=17, reversal=20 |

All picker runs returned valid JSON with expected schema.

## Corpus (Stage B linter sweep)

Skipped (no corpus dir).

## Telemetry smoke (Stage B)

PASS -- append + round-trip + summary (summary OK)
- temp file: `C:\Users\domes\Desktop\Claude-Plugins-Skills\crazy-professor\docs\.eval-tmp-a1y04lek\telemetry-smoke.jsonl`

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
