# Crazy Professor -- Field Notes

One line per invocation. The skill appends here automatically on each run.
The user ticks the checkboxes on the output file after reviewing; the
skill reads this file to trigger the field-test rule and the museum
clause.

Schema definition: `<repo-root>/skills/crazy-professor/resources/field-notes-schema.md`.

The skill (Step 2b of the operating instructions) reads the last 10 rows
of the Log table BEFORE the stochastic picker runs. Archetype guard
re-rolls when the same archetype would be 4th in a row; word guard
re-rolls when the word appears anywhere in the last 10 rows. The
`Re-rolled` column records the outcome (`no`, `archetype`, `word`,
`both`, etc.).

## Log

| # | Timestamp | Archetype | Word | Operator | Topic slug | Output file | Re-rolled | Kept | Retire-word | Voice-off | Review1-Votum |
|---|-----------|-----------|------|----------|------------|-------------|-----------|------|-------------|-----------|---------------|

## Field Test Status

- Total invocations so far: 0
- Kept outputs: 0
- Review1-Votum: 0 pending
- Words under retirement watch (2 of 3 flags): []
- Words retired: []

## Museum Clause Status

Gate fires at invocation 10. Not yet reached.

## Review Schedule

**Review 1** triggers at Run 10 completion (earliest) or 14 days after
the first run (fallback).

## How to Use This File

After the skill generates an output in
`.agent-memory/lab/crazy-professor/<timestamp>-<slug>.md`:

1. Read the output.
2. Pick the one provocation that you would actually test or that opened
   a space you had not seen. If none qualify, that is a signal; check
   "voice-off" if the archetype felt wrong, leave "kept" unchecked.
3. If the provocation word produced only near-variations of earlier
   output (pattern you recognize from previous runs), tick "retire-word".
4. Tick "kept" IF within 14 days the output landed in:
   - `~/wiki/inbox/`
   - `ISSUES2FIX`
   - `.agent-memory/skills-backlog/`
   - or was implemented.
5. Transcribe the ticks into this file under the corresponding row.

If this file stays blank, the museum clause defaults to "not kept" at
invocation 10 and the skill archives itself. That is the correct
behavior; a skill without feedback is a skill without evidence of value.
