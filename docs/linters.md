# Linters

The crazy-professor plugin ships four linters and one evaluation suite,
all stdlib-only Python. They run at three different cadences depending
on what they protect.

## At-a-glance

| Tool | Cadence | Blocks | Purpose |
|---|---|---|---|
| `lint_word_pool.py` | per commit (or manual) | yes | Pool integrity: duplicates, case, multi-word format, whitespace, retired/active overlap. |
| `lint_voice.py` | per skill run (Step 5b) | warns by default, errors on cross-archetype tokens | Per-archetype lexicon. Catches voice drift before write. |
| `lint_cross_pollination.py` | per chat-run (Step C4b, only when `--strict-cross-pollination` is set) | no -- warn-only (exit 0 always) | Cross-pollination substance: marker existence, ref resolution (archetype + idx in 1..5), token overlap with referenced R1 item. Findings appear as `[low-substance: <reason>]` markers in R2 lines. |
| `validate_output.py` | per skill run (Step 6) | yes | Format drift: frontmatter, divergence banner, exact 10-provocation count, line shape, sectioning. Since v0.11.0 also branches on `compact: true` to validate the audit-trail body order. |
| `eval_suite.py` | on demand (or scheduled) | no -- writes a report | Stage B static + corpus baseline. Stage C/D/E smoke tests for compact-mode, cross-pollination linter, wishful-thinking picker (since v0.11.0). |

## Cross-pollination linter (since v0.11.0)

The cross-pollination substance linter is the 4th member of the linter
trio (now quartet), activated only when `--strict-cross-pollination` is
passed to a chat-mode invocation. It enforces three deterministic checks
per Round 2 item:

1. **Marker existence**: `counter: <ref>` or `extend: <ref>` must be present.
2. **Ref resolution**: `<ref>` must point to an existing R1 item
   (archetype + idx in 1..5).
3. **Token overlap**: at least `--min-overlap` (default 1) non-stopword
   tokens (>=3 chars) must be shared between the R2 item text and the
   referenced R1 item text. Stop-words from `resources/stop-words.txt`.

Findings are warn-only — the linter never filters or removes R2 items.
Output is JSON on stdout. Exit code is always 0. The skill ingests the
JSON, locates each flagged R2 line, and appends
`[low-substance: <reason>]` at the end. The total finding count is
recorded in telemetry as `low_substance_hits`.

See operating-instructions Step C4b for invocation details.

## Word-pool linter

```bash
python skills/crazy-professor/scripts/lint_word_pool.py \
  --words skills/crazy-professor/resources/provocation-words.txt \
  --retired skills/crazy-professor/resources/retired-words.txt
```

Exit codes: `0` clean, `1` findings (printed to stderr), `2` usage
error.

Pass `--strict` to promote case-borderline warnings to errors.

The convenience wrapper `scripts/run_linters.sh` runs this linter (and
later: any other commit-time linter we add). Use that as the canonical
entry point so future linter additions are picked up automatically.

### As a pre-commit hook

The plugin does NOT install hooks for you. To enable locally:

```bash
cd <repo-root>
ln -s ../../skills/crazy-professor/scripts/run_linters.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

On Windows (no symlinks), copy the script:

```cmd
copy skills\crazy-professor\scripts\run_linters.sh .git\hooks\pre-commit
```

Skip the hook for an emergency commit with `git commit --no-verify`.
Investigate the underlying issue immediately afterward; do not let
this become routine.

## Voice linter

```bash
python skills/crazy-professor/scripts/lint_voice.py \
  --templates-dir skills/crazy-professor/prompt-templates \
  --mode single <output-file>
```

Two severity levels:

- **warn**: a provocation has fewer than the required minimum of
  archetype vocabulary (Pflicht-Vokabel-Miss). Logged, does not block.
  Pass `--strict` to promote warns to errors.
- **error**: a provocation contains a forbidden cross-archetype token
  (e.g. "Reaktor" in a Radagast output). These indicate genuine voice
  drift and SHOULD trigger a rewrite of the offending provocation.

For chat-mode use `--mode chat`; the linter checks each Round 3
sub-section against its archetype's lexicon. Round 1 + Round 2 are not
checked (they are intermediate scratch material).

The lexicon for each archetype lives in a `## Lexicon-Gate` block at
the bottom of `prompt-templates/<archetype>.md`, as a YAML code fence.
Edit the lexicon there, not in the linter.

### Lexicon-Gate format

```yaml
archetype: <name>
required:
  - token
  - token
required_patterns:        # optional, regex strings (use single quotes)
  - 'pattern \b'
required_min_per_provocation: 2
required_in_first_sentence: true   # OR
required_in_first_chars: 200       # OR neither (matches anywhere)
forbidden:
  - token
```

If `required_in_first_sentence` and `required_in_first_chars` are both
set, `required_in_first_sentence` wins.

## Output validator

```bash
python skills/crazy-professor/scripts/validate_output.py \
  --mode single <output-file>
```

Pre-write check from v0.7.0 onward. Blocks on format drift. See
`scripts/validate_output.py` source for the full rule list.

## Evaluation suite

Stage B (default) runs the static checks plus a corpus sweep:

```bash
python skills/crazy-professor/scripts/eval_suite.py \
  --picker skills/crazy-professor/scripts/picker.py \
  --voice-linter skills/crazy-professor/scripts/lint_voice.py \
  --validator skills/crazy-professor/scripts/validate_output.py \
  --templates-dir skills/crazy-professor/prompt-templates \
  --field-notes-template skills/crazy-professor/resources/field-notes-init.md \
  --words skills/crazy-professor/resources/provocation-words.txt \
  --retired skills/crazy-professor/resources/retired-words.txt \
  --corpus <path/to/lab/crazy-professor> \
  --report-out docs/eval-baseline-$(date +%F).md \
  --picker-runs 50 \
  --skill-version 0.8.0
```

The report lands at the `--report-out` path. It contains:

- **Picker section**: pass-rate per archetype over `--picker-runs`
  invocations, operator distribution, unique words drawn.
- **Corpus section**: per-archetype counts of voice pass / warn / fail
  and validator pass / fail across the corpus directory. Files with
  unknown archetype are listed as skipped.
- **Fail file details**: for each failed file, the first finding from
  the linter that flagged it.

Stage C (`--live --runs N`) is reserved for live skill invocations
(real LLM calls). The current implementation is a stub that prints
the planned invocations and exits 0. Live evaluation requires Claude
or Codex to drive the skill; the plan is documented at the bottom of
`scripts/eval_suite.py`.

### How to use the report as a quality gate

The eval baseline is informational, not blocking. Use it to:

- detect regressions: a pass-rate drop after a prompt-template edit
  is the earliest signal that the edit broke voice or format
- drive prompt edits: the fail-file details name the exact provocation
  and finding -- patch the template, regenerate, re-run the suite
- track progress: bumping the baseline pass-rate target over time is
  a meaningful goal, but only after the corpus is stable

A pass-rate target as a hard release-gate is intentionally NOT
defined here. Add one in a later iteration if and when the corpus is
big enough that a target is meaningful.
