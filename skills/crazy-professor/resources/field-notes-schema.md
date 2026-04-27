---
title: field-notes.md Schema
status: canonical (v0.7.0, Phase 2 point 2.2)
applies_to: .agent-memory/lab/crazy-professor/field-notes.md (in target project)
---

# field-notes.md Schema

This document defines the canonical structure of `field-notes.md` — the
per-project log that crazy-professor appends to on every run. The
Variation-Guard (Step 2b), the Museum-Clause (Run 10 / Run 20 reviews),
and the Field-Test-Rule (3-flag word retirement) all read this file.
Without a stable schema none of them are testable.

## Location

`<target-project>/.agent-memory/lab/crazy-professor/field-notes.md`

The file is **per target project**, not per plugin install. Each project
where the skill runs has its own field-notes log.

## Top-level structure

```
# Crazy Professor -- Field Notes
<short prose paragraph explaining the file>

## Log
<the Markdown table with one row per run — see "Log Table" below>

## Field Test Status
<short summary block — see "Status Block" below>

## Museum Clause Status
<short summary block — see "Status Block" below>

## Review Schedule
<plain prose section, free-form>

## How to Use This File
<plain prose, instructions for the user>
```

Optional sections (free-form, between Log and Field Test Status):

- `### Review Run N` — review notes per museum-clause checkpoint
- `### Beobachtungen` — observations not yet acted on
- `### Radagast Activation Blindtest` — once-only event log

These free-form sections are documentation only; the picker and validator
do not read them.

## Log Table

The Log table is the only machine-readable section. Columns are fixed:

| Column | Type | Required | Notes |
|---|---|---|---|
| `#` | int | yes | Run number; monotonically increasing. Chat-mode counts as one row, not four. |
| `Timestamp` | ISO-8601 UTC | yes | Format: `YYYY-MM-DDTHH:MM:SSZ`. The picker writes the exact timestamp it used as seed. |
| `Archetype` | string | yes | One of: `first-principles-jester`, `labyrinth-librarian`, `systems-alchemist`, `radagast-brown`, `all-4 (chat-mode)`. Suffix `(forced)` allowed when manually overridden. |
| `Word` | string | yes | Single word or 1-3-token phrase from `provocation-words.txt`. For chat-mode: `multi (w1/w2/w3/w4)`. |
| `Operator` | string | yes | One of: `reversal`, `exaggeration`, `escape`. For chat-mode: `multi (op1/op2/op3/op4)`. |
| `Topic slug` | string | yes | Kebab-case slug of the topic, no spaces. Matches the output filename. |
| `Output file` | string | yes | Filename relative to `.agent-memory/lab/crazy-professor/` (single) or with `chat/` prefix (chat). |
| `Re-rolled` | enum | yes | One of: `no`, `archetype`, `word`, `both`, `intra-chat` (chat-mode internal duplicate), `forced-archetype`, `forced-archetype+word`, `n/a (pre-guard)` (only for pre-2026-04-22 rows). |
| `Kept` | enum | yes | `pending`, `yes`, `no`. Default `pending` until 14-day artefact-tracking resolves. |
| `Retire-word` | enum | yes | `pending`, `yes`, `no`. Set `yes` when the user flagged the run as "too close to variations of previous outputs". |
| `Voice-off` | enum / free | yes | `pending`, `no`, or a short string describing the drift (e.g. `light-voice-drift (juror-2 #8 System-Verstoss)`). |
| `Review1-Votum` | enum / free | yes | One of: `pending`, `kept`, `conditional`, `backlog`. May carry a parenthetical (e.g. `kept (2 of 3 voters)`). |

### Markdown table format

Standard GitHub-flavored Markdown. Header row + alignment row + data rows.
Pipes `|` are the column separator. Cells must not contain raw pipes — if
a value would, escape it as `\|` or replace with `/`.

### Append rule

The picker (and the SKILL.md operating instructions) only ever **append**
rows to the Log table. Existing rows are never edited by automation. The
user may edit `Kept`, `Retire-word`, `Voice-off`, `Review1-Votum`
manually after a review.

## Status Block

`## Field Test Status` and `## Museum Clause Status` are short prose
blocks. The picker does not parse them; they are written by the user
during reviews. Format is free-form but the convention is:

```
## Field Test Status

- Total invocations so far: <N> (<breakdown if relevant>)
- Kept outputs: <count> <status notes>
- Review1-Votum: <count> kept · <count> conditional · <count> backlog · <count> pending
- Words under retirement watch (2 of 3 flags): []
- Words retired: [] (see `<repo-root>/skills/crazy-professor/resources/retired-words.txt`)

## Museum Clause Status

Gate fired at invocation <N> (<timestamp>). **Gate <passed|failed>.**
Review <N> completed <date>, <verdict summary>.
Next museum checkpoint: Run <N+10> completion.
```

## What the picker reads

Step 2b of the operating instructions reads the **last 10 rows** of the
Log table (or fewer if the table is shorter). For each row it extracts
`Archetype` and `Word`. The picker uses these for the archetype-streak
guard and the word-window guard. It ignores all other columns.

The picker counts from the **bottom** of the table. If the table has
both single and chat rows, both count toward the 10-row window.

## What the validator reads

Validator (point 2.3) does NOT read field-notes.md — it reads the
output files in `.agent-memory/lab/crazy-professor/` (single) and
`.agent-memory/lab/crazy-professor/chat/` (chat).

## What automation must NEVER do

- Reorder or delete existing rows (audit trail).
- Edit user-facing review columns (`Kept`, `Retire-word`, `Voice-off`,
  `Review1-Votum`) — those are user input.
- Truncate or rotate the file. Field-notes is append-only; archival is
  manual at museum-clause checkpoints if it ever becomes too long.

## Initialization

If `field-notes.md` does not exist when a run starts, the picker copies
the contents of
`<repo-root>/skills/crazy-professor/resources/field-notes-init.md` to
the target location, then proceeds with Step 2/2b on the (empty) Log
table.

Initialization is idempotent: if the file already exists, the picker
does nothing to it during init.
