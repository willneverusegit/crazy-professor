#!/usr/bin/env python3
"""
crazy-professor evaluation suite -- pass-rate baseline + linter sweep.

Two modes:

  Stage B (default): static + corpus
    - Run picker.py 50 times per archetype with --force-archetype, check
      that every invocation returns valid JSON with the expected keys
      and that the variation guard does not return malformed re_rolled
      values.
    - Walk a corpus directory of existing single-mode outputs and run
      lint_voice + validate_output against each.
    - Aggregate pass-rate per archetype + fail-reason histogram.
    - Write the report to docs/eval-baseline-<date>.md.

  Stage C (--live): hook only
    - Reserved for live skill invocations (LLM calls). Implemented as a
      stub in this iteration -- it prints the planned invocations and
      exits 0 without calling out, because triggering the actual skill
      requires Claude/Codex orchestration outside this script's scope.
    - Spec lives in docs/eval-suite.md (added in Phase 3.4).

Usage:
    eval_suite.py --picker <path> --voice-linter <path> --validator <path>
                  --templates-dir <path> --field-notes-template <path>
                  --words <path> --retired <path>
                  --corpus <dir> --report-out <file>
                  [--picker-runs N] [--strict-voice] [--live --runs N]

Exits:
    0  evaluation completed (report written; non-zero pass rates do
       not change exit code -- the report is the output)
    1  one of the static checks crashed in a way that breaks the
       suite itself (e.g. picker raised, files missing)
    2  usage error
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

ARCHETYPES = ("first-principles-jester", "labyrinth-librarian",
              "systems-alchemist", "radagast-brown")

EXPECTED_PICKER_KEYS = {"timestamp", "mode", "archetype", "word", "operator",
                        "re_rolled", "field_notes_rows_read"}
VALID_RE_ROLLED = {"no", "archetype", "word", "both"}


def run_picker_once(picker: Path, field_notes: Path, words: Path,
                    retired: Path, archetype: str,
                    init_template: Path) -> tuple[bool, str, dict | None]:
    """Return (ok, reason, parsed_json_or_None)."""
    cmd = [
        sys.executable, str(picker),
        "--field-notes", str(field_notes),
        "--words", str(words),
        "--retired", str(retired),
        "--init-template", str(init_template),
        "--mode", "single",
        "--force-archetype", archetype,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    if proc.returncode != 0:
        return False, f"picker exit {proc.returncode}: {proc.stderr.strip()[:120]}", None
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return False, f"non-json stdout: {exc}", None
    missing = EXPECTED_PICKER_KEYS - set(data)
    if missing:
        return False, f"missing keys: {sorted(missing)}", data
    if data["archetype"] != archetype:
        # forced-archetype + variation-guard may add suffix; tolerate
        re_rolled = data.get("re_rolled", "")
        if not re_rolled.startswith("forced-archetype"):
            return False, f"archetype mismatch: got {data['archetype']!r}", data
    if data["operator"] not in ("reversal", "exaggeration", "escape"):
        return False, f"bad operator {data['operator']!r}", data
    if not data["word"]:
        return False, "empty word", data
    rr = data["re_rolled"].split("+", 1)[0]
    if rr not in VALID_RE_ROLLED and not rr.startswith("forced-archetype"):
        return False, f"invalid re_rolled {data['re_rolled']!r}", data
    return True, "ok", data


def stage_b_picker(picker: Path, words: Path, retired: Path,
                   init_template: Path, runs_per_archetype: int,
                   tmp_dir: Path) -> dict:
    """Run picker N times per archetype against a fresh field-notes file."""
    results: dict[str, dict] = {}
    for arch in ARCHETYPES:
        ok = 0
        fail_reasons: list[str] = []
        words_drawn: Counter = Counter()
        ops: Counter = Counter()
        # one fresh field-notes per archetype to avoid cross-pollution
        fn_path = tmp_dir / f"field-notes-{arch}.md"
        if fn_path.exists():
            fn_path.unlink()
        for _ in range(runs_per_archetype):
            success, reason, data = run_picker_once(
                picker, fn_path, words, retired, arch, init_template
            )
            if success and data is not None:
                ok += 1
                words_drawn[data["word"]] += 1
                ops[data["operator"]] += 1
            else:
                fail_reasons.append(reason)
        results[arch] = {
            "runs": runs_per_archetype,
            "ok": ok,
            "pass_rate": round(ok / runs_per_archetype, 3) if runs_per_archetype else 0.0,
            "unique_words": len(words_drawn),
            "operator_distribution": dict(ops),
            "fail_reasons": Counter(fail_reasons).most_common(10),
        }
    return results


def stage_b_corpus(voice_linter: Path, validator: Path,
                   templates_dir: Path, corpus_dir: Path,
                   strict_voice: bool) -> dict:
    """Lint + validate every *.md file under corpus_dir (single-mode)."""
    corpus_root = corpus_dir.resolve()
    files = sorted(
        p for p in corpus_dir.glob("*.md")
        if p.is_file() and not p.name.startswith("field-notes")
    )
    per_archetype: dict[str, dict] = {a: {"files": 0, "voice_pass": 0,
                                          "voice_warn": 0, "voice_fail": 0,
                                          "validator_pass": 0,
                                          "validator_fail": 0,
                                          "fail_files": []}
                                       for a in ARCHETYPES}
    untyped = {"files": 0, "skipped_unknown_archetype": 0,
               "skipped_unsafe_path": 0,
               "skipped_paths": []}
    voice_args = ["--templates-dir", str(templates_dir), "--mode", "single"]
    if strict_voice:
        voice_args.append("--strict")
    for f in files:
        resolved = f.resolve()
        if f.is_symlink() or (resolved != corpus_root and corpus_root not in resolved.parents):
            untyped["files"] += 1
            untyped["skipped_unsafe_path"] += 1
            untyped["skipped_paths"].append(str(f.name))
            continue
        text = f.read_text(encoding="utf-8")
        arch = ""
        for line in text.splitlines()[:40]:
            if line.startswith("archetype:"):
                arch = line.split(":", 1)[1].strip().strip('"').strip("'")
                break
        if arch not in ARCHETYPES:
            untyped["files"] += 1
            untyped["skipped_unknown_archetype"] += 1
            untyped["skipped_paths"].append(str(f.name))
            continue
        per_archetype[arch]["files"] += 1
        # voice
        v_proc = subprocess.run(
            [sys.executable, str(voice_linter), *voice_args, str(f)],
            capture_output=True, text=True, timeout=15,
        )
        if v_proc.returncode == 0:
            if "warn:" in v_proc.stderr:
                per_archetype[arch]["voice_warn"] += 1
            else:
                per_archetype[arch]["voice_pass"] += 1
        else:
            per_archetype[arch]["voice_fail"] += 1
            per_archetype[arch]["fail_files"].append({
                "file": f.name,
                "kind": "voice",
                "first_finding": _first_finding_line(v_proc.stderr),
            })
        # validator
        val_proc = subprocess.run(
            [sys.executable, str(validator), "--mode", "single", str(f)],
            capture_output=True, text=True, timeout=15,
        )
        if val_proc.returncode == 0:
            per_archetype[arch]["validator_pass"] += 1
        else:
            per_archetype[arch]["validator_fail"] += 1
            per_archetype[arch]["fail_files"].append({
                "file": f.name,
                "kind": "validator",
                "first_finding": _first_finding_line(val_proc.stderr),
            })
    return {"per_archetype": per_archetype, "untyped": untyped,
            "total_files": len(files)}


def _first_finding_line(stderr: str) -> str:
    for line in stderr.splitlines():
        s = line.strip()
        if s.startswith("- "):
            return s[2:][:200]
    return stderr.strip().splitlines()[0][:200] if stderr.strip() else ""


def render_report(picker_results: dict, corpus_results: dict | None,
                  meta: dict) -> str:
    lines: list[str] = []
    lines.append(f"# Eval Baseline {meta['date']}")
    lines.append("")
    lines.append(f"- skill version: {meta.get('skill_version', 'unknown')}")
    lines.append(f"- picker runs per archetype: {meta['picker_runs']}")
    lines.append(f"- corpus dir: `{meta['corpus_dir']}`")
    lines.append(f"- voice strict mode: {meta['strict_voice']}")
    lines.append("")
    lines.append("## Picker (Stage B static)")
    lines.append("")
    lines.append("| Archetype | Runs | OK | Pass-Rate | Unique Words | Operator Dist |")
    lines.append("|---|---|---|---|---|---|")
    for arch, r in picker_results.items():
        ops = ", ".join(f"{k}={v}" for k, v in sorted(r["operator_distribution"].items()))
        lines.append(
            f"| {arch} | {r['runs']} | {r['ok']} | {r['pass_rate']*100:.1f}% | "
            f"{r['unique_words']} | {ops or '-'} |"
        )
    any_picker_fails = False
    for arch, r in picker_results.items():
        if r["fail_reasons"]:
            any_picker_fails = True
            lines.append("")
            lines.append(f"### Picker fail reasons -- {arch}")
            for reason, count in r["fail_reasons"]:
                lines.append(f"- {count}x: {reason}")
    if not any_picker_fails:
        lines.append("")
        lines.append("All picker runs returned valid JSON with expected schema.")

    if corpus_results is None:
        lines.append("")
        lines.append("## Corpus (Stage B linter sweep)")
        lines.append("")
        lines.append("Skipped (no corpus dir).")
        return "\n".join(lines) + "\n"

    lines.append("")
    lines.append(
        f"## Corpus (Stage B linter sweep) -- {corpus_results['total_files']} files"
    )
    lines.append("")
    lines.append(
        "| Archetype | Files | Voice Pass | Voice Warn | Voice Fail | "
        "Validator Pass | Validator Fail |"
    )
    lines.append("|---|---|---|---|---|---|---|")
    for arch, c in corpus_results["per_archetype"].items():
        lines.append(
            f"| {arch} | {c['files']} | {c['voice_pass']} | {c['voice_warn']} | "
            f"{c['voice_fail']} | {c['validator_pass']} | {c['validator_fail']} |"
        )
    untyped = corpus_results["untyped"]
    if untyped["files"]:
        lines.append("")
        lines.append(
            f"Skipped {untyped['files']} file(s) with unknown/missing archetype "
            f"or unsafe path: "
            f"{', '.join(untyped['skipped_paths'][:10])}"
        )

    fail_records = []
    for arch, c in corpus_results["per_archetype"].items():
        for rec in c["fail_files"]:
            fail_records.append((arch, rec))
    if fail_records:
        lines.append("")
        lines.append("### Fail file details")
        lines.append("")
        for arch, rec in fail_records:
            lines.append(f"- **{arch}** / `{rec['file']}` ({rec['kind']}):")
            lines.append(f"  - {rec['first_finding']}")

    return "\n".join(lines) + "\n"


def stage_c_live_stub(runs: int) -> int:
    print(
        f"[stage C / live mode] Planned {runs} live skill invocations per "
        f"archetype.\n"
        f"This script does NOT trigger live LLM calls -- live runs require\n"
        f"orchestration via Claude or Codex. See docs/eval-suite.md for the\n"
        f"contract:\n"
        f"  1. invoke /crazy <topic> with each of the eval-topics.txt items\n"
        f"  2. write outputs to a fresh corpus dir\n"
        f"  3. re-run eval_suite.py without --live against that corpus\n"
        f"\n"
        f"Exiting 0 without action.",
        file=sys.stderr,
    )
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="crazy-professor eval suite")
    p.add_argument("--picker", required=True, type=Path)
    p.add_argument("--voice-linter", required=True, type=Path)
    p.add_argument("--validator", required=True, type=Path)
    p.add_argument("--templates-dir", required=True, type=Path)
    p.add_argument("--field-notes-template", required=True, type=Path)
    p.add_argument("--words", required=True, type=Path)
    p.add_argument("--retired", required=True, type=Path)
    p.add_argument("--corpus", type=Path, help="dir of single-mode outputs to lint")
    p.add_argument("--report-out", required=True, type=Path)
    p.add_argument("--picker-runs", type=int, default=50)
    p.add_argument("--strict-voice", action="store_true")
    p.add_argument("--skill-version", default="unknown")
    p.add_argument("--live", action="store_true",
                   help="Stage C hook (currently a stub)")
    p.add_argument("--runs", type=int, default=5,
                   help="(Stage C only) live runs per archetype")
    args = p.parse_args()

    if args.live:
        if args.runs < 0:
            print("error: --runs must be >= 0", file=sys.stderr)
            return 2
        return stage_c_live_stub(args.runs)
    if args.picker_runs < 0:
        print("error: --picker-runs must be >= 0", file=sys.stderr)
        return 2

    for needed in (args.picker, args.voice_linter, args.validator,
                   args.field_notes_template, args.words, args.retired):
        if not needed.exists():
            print(f"error: missing input {needed}", file=sys.stderr)
            return 2
    if not args.templates_dir.is_dir():
        print(f"error: not a dir: {args.templates_dir}", file=sys.stderr)
        return 2

    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = Path(tempfile.mkdtemp(prefix=".eval-tmp-", dir=args.report_out.parent))

    print(
        f"running stage B: {args.picker_runs} picker runs per archetype "
        f"({len(ARCHETYPES) * args.picker_runs} total)...",
        file=sys.stderr,
    )
    picker_results = stage_b_picker(
        args.picker, args.words, args.retired,
        args.field_notes_template, args.picker_runs, tmp_dir,
    )

    corpus_results: dict | None = None
    if args.corpus and args.corpus.is_dir():
        print(f"running stage B corpus sweep on {args.corpus}...",
              file=sys.stderr)
        corpus_results = stage_b_corpus(
            args.voice_linter, args.validator, args.templates_dir,
            args.corpus, args.strict_voice,
        )
    elif args.corpus:
        print(f"warning: corpus dir not found: {args.corpus}",
              file=sys.stderr)

    meta = {
        "date": dt.date.today().isoformat(),
        "picker_runs": args.picker_runs,
        "corpus_dir": str(args.corpus) if args.corpus else "(none)",
        "strict_voice": args.strict_voice,
        "skill_version": args.skill_version,
    }
    report = render_report(picker_results, corpus_results, meta)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(report, encoding="utf-8")
    print(f"report written: {args.report_out}", file=sys.stderr)

    # cleanup only the temp dir owned by this run
    for fn in tmp_dir.iterdir():
        try:
            fn.unlink()
        except OSError:
            pass
    try:
        tmp_dir.rmdir()
    except OSError:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
