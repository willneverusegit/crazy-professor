#!/usr/bin/env bash
# crazy-professor: run all repo-level linters in sequence.
#
# Intended usage:
#   - manual sanity check before committing
#   - .git/hooks/pre-commit (symlink or invocation, see docs/linters.md)
#   - CI step (when/if CI is added)
#
# Exits non-zero on the first failure. Prints which linter failed.
#
# Currently runs:
#   - lint_word_pool.py    (provocation-words.txt + retired-words.txt)
#
# NOT run here (per Phase 3.4 wiring decision):
#   - lint_voice.py        runs per skill invocation (Step 5b), not per commit
#   - validate_output.py   runs per skill invocation (Step 6), not per commit
#   - eval_suite.py        long-running, run on demand

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

PYTHON="${PYTHON:-python}"

echo "[run_linters] word pool..."
"${PYTHON}" "${SCRIPT_DIR}/lint_word_pool.py" \
  --words "${SKILL_DIR}/resources/provocation-words.txt" \
  --retired "${SKILL_DIR}/resources/retired-words.txt"

echo "[run_linters] all green."
