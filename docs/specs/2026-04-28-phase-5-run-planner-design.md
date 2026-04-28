---
title: Phase 5 — Run Planner + --dry-run (Design Spec)
date: 2026-04-28
phase: 5
target_version: v0.10.0
plan_reference: docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md
status: approved-design
---

# Phase 5 — Run Planner + `--dry-run`

Design spec for crazy-professor Master-Plan Phase 5. Approved 2026-04-28
through brainstorming session (5 clarifying questions, 5 design sections,
all confirmed).

## Goals

Master-Plan Phase 5 has two points:

- **5.1 Run Planner** as a shared layer for archetype-selector and
  `--from-session` (NOT two loose features). The selector picks the
  archetype from topic keywords; timestamp-mod stays as fallback.
  `--from-session` reads `.agent-memory/session-summary.md` (local) and
  the Desktop equivalent and proposes 3 topic candidates.
- **5.2 `--dry-run`** for single-run shows picker output (archetype +
  word + operator) without generation. Helps debug variation-guard and
  run-planner logic.

Default version bump per VERSIONING.md: **MINOR → v0.10.0** (new flags
visible to users).

## Decisions made during brainstorming

| # | Question | Answer |
|---|----------|--------|
| 1 | Topic→archetype mapping mechanic | (a) Hardcoded keyword lists in `archetype-keywords.txt`. Score-match, tie/no-match → timestamp-mod fallback. No threshold, no weights (Phase 6+ topics). |
| 2 | `--from-session` source path | (b) Repeatable `--session-path` arg; default in operating-instructions: local `<cwd>/.agent-memory/session-summary.md` first, then Desktop `~/Desktop/.agent-memory/session-summary.md`. |
| 2b | Topic-extraction heuristic | (iii) Parse only "Naechste Schritte" + "Open Items" sections, take first 3 bullets. Case-tolerant headline matching. |
| 3 | Code location | (a) New script `run_planner.py`. Picker stays unchanged. Pattern matches telemetry.py / patch_suggester.py (each phase its own helper). |
| 4a | `--dry-run` flag location | (α) Single-run command flag in `commands/crazy.md`. Chat-mode keeps `--chat --dry-run-round1` unchanged. |
| 4b | `--dry-run` output form | (ii) Commented Markdown block on stdout with picker-JSON + run-planner reasoning. Includes which keywords matched and what the timestamp-mod fallback would have been. |
| 4c | `--dry-run` side-effects | (α) None. No output file, no field-notes append, no telemetry append. Pure preview. |
| 5 | Variation-guard vs. selector conflict | (a) Variation-guard wins. Selector is recommendation; streak-avoidance is hard constraint. `re_rolled` reflects streak honestly. |

## Architecture

### New script: `skills/crazy-professor/scripts/run_planner.py`

Stdlib-only Python. ~250 lines expected. Three subcommands.

```
run_planner.py archetype  --topic "..." --keywords <path>
                          → JSON: {topic, selected_archetype, selection_reason,
                                   matched_keywords, fallback_used,
                                   topic_candidates: null}

run_planner.py session    --session-path <path> [--session-path <path> ...]
                          → JSON: {topic: null, selected_archetype: null, ...,
                                   topic_candidates: [{topic, source, rank}, ...]}

run_planner.py plan       --topic "..." --keywords <path>
                          --session-path <p1> [--session-path <p2> ...]
                          → JSON: archetype-fields + topic_candidates combined
```

### New resource: `skills/crazy-professor/resources/archetype-keywords.txt`

Versioned alongside `provocation-words.txt`. Format:

```
# crazy-professor — archetype keyword pool
# format: <archetype>: kw1, kw2, kw3, ...
# matched case-insensitive as substring against lowercased topic
first-principles-jester: assumption, why, basic, naive, simple, ...
labyrinth-librarian:    history, reference, archive, doc, ...
systems-alchemist:      pipeline, infra, system, flow, deploy, ...
radagast-brown:         forest, shelter, slow, care, repair, ...
```

Initial: 15-25 keywords per archetype, ~80-100 total. Sourced from the
existing Pflicht-Vokabel lists in `prompt-templates/<archetype>.md`
Lexicon-Gates plus generic domain words.

### Composition with picker.py

Picker stays **unchanged**. Run Planner produces a recommendation;
operating-instructions calls picker with `--force-archetype <selected>`
when the selector hits, or without `--force-archetype` when the selector
falls back. Picker's variation-guard remains the final word — if the
recommended archetype is in a 3-in-a-row streak, the variation-guard
overrides it. `re_rolled` column logs the streak honestly.

### Tie definition

A **tie** in the score-match logic means: two or more archetypes share
the same `max_score` at position 1. Ties at lower positions are
irrelevant. A tie at position 1 → `fallback_used: true`,
`selected_archetype: null`. No artificial tie-break (alphabetical,
recency, etc.) — fallback is the honest answer.

### New command flag: `--dry-run`

Single-run only. Documented in `commands/crazy.md` and operating-
instructions Step 1. Aborts before Step 3 (generation). Side-effect-free.

### Files touched

- **New:** `skills/crazy-professor/scripts/run_planner.py`
- **New:** `skills/crazy-professor/resources/archetype-keywords.txt`
- **New:** `docs/specs/2026-04-28-phase-5-run-planner-design.md` (this file)
- **Modified:** `skills/crazy-professor/references/operating-instructions.md` (Step 1, Step 2 split into 2a/2b, Step 7b telemetry schema)
- **Modified:** `commands/crazy.md` (`--from-session` and `--dry-run` flags)
- **Modified:** `README.md` (trigger section)
- **Modified:** `scripts/eval_suite.py` (new `stage_b_run_planner_smoke()` and reporting)
- **Modified:** 8 frontmatter files for v0.9.0 → v0.10.0 bump (per VERSIONING.md)
- **Modified:** `docs/PROJECT.md`, `docs/CAPABILITIES.md`, `docs/CHANGELOG.md`
- **Modified:** `docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md` (Phase 5 status)

## Data flow

### Single-run with topic (standard case after Phase 5)

```
User: /crazy "deploy pipeline simplification"
  ↓
operating-instructions Step 1: topic parsed.
  ↓
operating-instructions Step 2a (NEW): Run Planner archetype subcommand
  python run_planner.py archetype \
    --topic "deploy pipeline simplification" \
    --keywords <repo>/resources/archetype-keywords.txt
  ↓
  stdout: {"selected_archetype": "systems-alchemist",
           "matched_keywords": ["deploy", "pipeline"],
           "fallback_used": false, ...}
  ↓
operating-instructions Step 2b: Picker (today's Step 2)
  python picker.py ... --force-archetype systems-alchemist
  ↓
  Picker applies variation-guard:
    - If systems-alchemist 3x in a row → re-roll archetype
    - Otherwise → systems-alchemist stays
  ↓
Steps 3-7 unchanged.
Step 7b telemetry adds two new OPTIONAL fields (Phase-5 substrate):
  "archetype_selector_used": true | false,
  "archetype_selector_matched_kw": ["deploy", "pipeline"] | []

Schema-extension rationale: the active-warnings note "schema extension
only after Phase-5 data observation" refers to schema *re-design*, not
"never extend". These two fields ARE the Phase-5 data we want to
observe (how often the selector fires, which keywords win). Both are
optional and break no existing readers (Phase-4 contract: new fields
must be optional, never required).
```

### Single-run without topic, with `--from-session`

```
User: /crazy --from-session
  ↓
operating-instructions Step 1: --from-session detected
  python run_planner.py session \
    --session-path <cwd>/.agent-memory/session-summary.md \
    --session-path ~/Desktop/.agent-memory/session-summary.md
  ↓
  stdout: {"topic_candidates": [
            {"topic": "...", "source": "Naechste Schritte", "rank": 1},
            ...
          ]}
  ↓
Skill shows user 3 candidates, asks: "Which? [1/2/3 or own]"
User picks → topic set → continue with Step 2a above.
If file missing or sections empty:
  → topic_candidates = [], skill asks user per Step 1 contract.
```

### Single-run with `--dry-run`

```
User: /crazy "topic" --dry-run
  ↓
operating-instructions Step 1: dry-run path
  Parse topic.
  Step 2a (run_planner archetype) — as above.
  Step 2b (picker) — as above with --force-archetype.
  ↓
Skill prints Markdown block:

  ### Crazy Professor — Dry Run

  Topic: "topic"
  Run Planner:
    Archetype: systems-alchemist (selector matched: deploy, pipeline)
    Fallback: false
  Picker:
    Word: "ritual debt"
    Operator: reversal
    Re-rolled: no
    Last 10 archetypes seen: [...]
  Variation Guard: no streak detected.

  ABORT before generation. No file written, no telemetry, no field-notes.
  ↓
Skill stops. Steps 3-7 NOT executed.
```

### `--from-session` + `--dry-run` combined

Skill lists topic candidates, user picks, then dry-run on the chosen
topic. Standard composition, no special case.

### No-match behavior

- `archetype-keywords.txt` matches 0 keywords in topic →
  `fallback_used: true`, `selected_archetype: null`. Picker runs without
  `--force-archetype`, timestamp-mod takes over. **Behaviorally identical
  to v0.9.0 for topics without match.**
- `--from-session`: no readable file or empty "Naechste Schritte" +
  "Open Items" sections → `topic_candidates: []`. Skill falls back to
  Step-1 contract (asks user for topic).

## Error handling

### Exit codes (analogous to picker.py / telemetry.py)

```
0   success — JSON written to stdout
1   usage error / unreadable input
2   keywords file unreadable or malformed
3   no session paths readable
```

### Per-subcommand rules

- **`archetype`**: needs `--topic` AND `--keywords`. Empty topic → 1.
  Missing keywords file → 2. Unknown archetype name in keywords file
  left-hand side → 2.
- **`session`**: needs ≥ 1 `--session-path`. 0 paths → 1. All paths
  unreadable → 3. Some readable / some not → continue with readable
  ones. All readable but no matching sections → `topic_candidates: []`,
  exit 0.
- **`plan`**: combines both. `archetype` failure → exit 2.
  `session` failure → archetype fields output, `topic_candidates: null`,
  exit 0. (Strict-mode `--require-session` is Phase-6+ deferred.)

### Robustness rules

- UTF-8 only on all reads. BOM/codec error → exit 2.
- Empty keyword pool for one archetype: not an error; that archetype
  can win only via timestamp-mod fallback.
- Tokenization: lowercase + strip `[.,!?;:()\[\]"']` + split on
  whitespace. No stemming. Substring match `kw in topic_lower` (so
  "deploys" / "deployment" match keyword "deploy").
- Whitespace in keywords (e.g. "ritual debt"): substring-match on the
  full keyword as-is, no internal split.

### Session-parser robustness

- Headline matching is case-tolerant: matches "## Naechste Schritte",
  "## naechste schritte", "## Next Steps", "## Open Items" and near
  variants (whitespace/hyphen/underscore tolerant). Concrete list
  documented at the top of `run_planner.py`.
- Bullets are lines starting with `- ` or `* ` or `N. ` (numbered).
- For numbered bullets like
  `1. **Phase 5 starten** in crazy-professor — 5.1 Run Planner ...`:
  full bullet text after the marker is taken; markdown markup is not
  stripped (the generator handles cleanup later).

### Skill behavior on run-planner failures

- Run-planner exit ≠ 0 → operating-instructions falls back to v0.9.0
  behavior (no `--force-archetype`, timestamp-mod, no topic suggestion).
  Skill prints `[run-planner: skipped — exit code N]` once-line in the
  output but does not abort the run.
- `--from-session` with exit 3: skill informs user "No session data
  found, please name a topic" and falls back to Step-1 contract.

### Explicitly NOT robustified

- No retry loops on read failures.
- No auto-repair of malformed `archetype-keywords.txt`.
- No internationalization. Tokenization is ASCII-/Latin-1-tolerant but
  not Unicode-aware. German topics work because the keyword file can
  contain German words.

## Tests

### eval_suite.py extension

New function `stage_b_run_planner_smoke()` with eight deterministic
asserts:

1. **archetype — keyword match**: topic `"deploy pipeline simplification"`
   against test keyword file → `selected_archetype == "systems-alchemist"`,
   `matched_keywords` contains `"deploy"` and `"pipeline"`,
   `fallback_used == false`.
2. **archetype — no match**: topic `"xyzqrt foo bar"` → `fallback_used:
   true`, `selected_archetype: null`, `matched_keywords: []`.
3. **archetype — tie**: topic `"forest deploy"` (1 kw per 2 archetypes)
   → `fallback_used: true`.
4. **archetype — case-insensitive substring**: topic `"DEPLOYS the
   SYSTEMS"` → matched_keywords contains `"deploy"` and `"system"`.
5. **archetype — empty topic**: exit 1.
6. **archetype — missing keywords file**: exit 2.
7. **session — extracts from "Naechste Schritte"**: feed test summary,
   first 3 bullets in `topic_candidates`, correct `source` and rank.
8. **session — multiple paths, dedup**: two paths, second contains a
   bullet from the first → no duplicate in `topic_candidates`.

### Eval-report rendering

`render_run_planner_section()` outputs a "## Run Planner smoke (Stage B)"
block in the baseline report. Format mirrors the telemetry section:
`pass: 8/8` or `fail: <N>/8 — first failure: <which>`.

### `--dry-run` testing

The eval-suite does not test `--dry-run` directly (it's a skill-flow
flag, not a script behavior). End-to-end skill testing isn't in the
eval-suite scope today. `--dry-run` gets:

- **Manual smoke test in implementation session**: real call against a
  topic, observable that no file appears in `lab/crazy-professor/`.
- **Documented in CHANGELOG** as part of v0.10.0.

### Manual smoke tests during implementation

- `run_planner.py archetype --topic "phase 5 starten run planner" --keywords <real>` → JSON parse, fields check.
- `run_planner.py session --session-path <repo>/.agent-memory/session-summary.md --session-path ~/Desktop/.agent-memory/session-summary.md` → 3 real topic candidates from real summaries.
- `run_planner.py plan --topic "..." --session-path ... --session-path ...` → combined JSON.
- `/crazy "concrete topic" --dry-run` → markdown output, no file in `lab/crazy-professor/`.
- `/crazy "topic that triggers selector"` → real run, field-notes-append shows correctly forced archetype, `re_rolled` correct.

### Linter updates

None. lint_voice.py and lint_word_pool.py operate on output files; run
planner writes no output files. validate_output.py also unaffected.

## Implementation sequence

Twelve steps. Each is standalone-testable before the next.

1. **Resource file**: create `archetype-keywords.txt` with initial
   80-100 keywords sourced from prompt-templates Lexicon-Gates.
2. **`run_planner.py archetype` subcommand**: tokenize, score, tie-break,
   output JSON.
3. **`run_planner.py session` subcommand**: section parser, bullet
   extractor, dedup across paths.
4. **`run_planner.py plan` subcommand**: composition layer.
5. **eval_suite.py extension**: `stage_b_run_planner_smoke()` +
   `render_run_planner_section()` + `--run-planner-keywords` CLI arg.
6. **operating-instructions.md**: Step 2 → Step 2a + 2b. New Step 1
   variants for `--from-session` and `--dry-run`. Telemetry schema
   extension in Step 7b (two optional fields).
7. **commands/crazy.md**: `argument-hint` updated, topic-resolution
   contract extended for `--from-session` and `--dry-run`.
8. **README.md**: trigger section gains `--from-session` and `--dry-run`.
9. **Version bump v0.9.0 → v0.10.0**: 8 frontmatter files per
   VERSIONING.md, plugin.json first.
10. **docs/ sync**: PROJECT.md, CAPABILITIES.md, CHANGELOG.md,
    master-plan.md (Phase 5 ✅).
11. **Self-verification**: local checklist (frontmatter bumps,
    operating-instructions step structure, CHANGELOG entry, master-plan
    status, scripts importable, --help works, exit codes correct,
    eval-suite passes 8/8). Codex-Verifier deferred per
    Phase-4-pattern (4 sessions in a row of hangs).
12. **Commit + push**: tag `crazy-professor | v0.10.0: Phase-5 — Run
    Planner + --dry-run`. Push to `origin/master`.

### Out of scope (deferred to Phase 6+)

- LLM-based archetype selector
- Keyword weighting
- Min-score threshold for selector win
- Topic-based operator selection (master-plan open question)
- Global `~/.claude/state/` topic pool
- `--from-session` for chat-mode
- `--require-session` strict mode
- End-to-end `--dry-run` test in eval-suite

## Open questions deliberately deferred

- After Phase 5 baseline data exists: should the run planner also
  influence operator choice, or stay archetype-only? (Master-plan open
  question, post-Phase-5 decision.)
- Threshold tuning for selector confidence (1-keyword match vs. 2+) —
  Phase 6+ once we have telemetry data showing how often selector vs.
  fallback fires.
