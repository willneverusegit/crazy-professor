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
    if data["operator"] not in ("reversal", "exaggeration", "escape", "wishful-thinking"):
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
    seen_ops = set()
    for arch, r in results.items():
        seen_ops.update(r["operator_distribution"].keys())
    results["__operator_coverage__"] = {
        "all_seen": sorted(seen_ops),
        "wishful_seen": "wishful-thinking" in seen_ops,
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


def render_telemetry_section(tele: dict) -> list[str]:
    lines: list[str] = ["", "## Telemetry smoke (Stage B)", ""]
    if not tele.get("available"):
        lines.append(f"Skipped: {tele.get('reason', 'telemetry script not available')}")
        return lines
    if tele.get("passed"):
        lines.append(f"PASS -- append + round-trip + summary "
                     f"({'summary OK' if tele.get('summary_ok') else 'summary MISMATCH'})")
        lines.append(f"- temp file: `{tele.get('tele_path')}`")
    else:
        lines.append(f"FAIL -- {tele.get('reason')}")
    return lines


def render_run_planner_section(rp: dict) -> list[str]:
    lines: list[str] = ["", "## Run Planner smoke (Stage B)", ""]
    if not rp.get("available"):
        lines.append(f"Skipped: {rp.get('reason', 'run_planner script not available')}")
        return lines
    if rp.get("passed"):
        lines.append(f"PASS -- {rp['passes']}/{rp['total']} asserts")
    else:
        first = rp.get("first_fail")
        first_label = first[0] if first else "unknown"
        first_detail = first[1] if first else ""
        lines.append(f"FAIL -- {rp['passes']}/{rp['total']} asserts; "
                     f"first failure: {first_label}"
                     + (f" ({first_detail})" if first_detail else ""))
    lines.append("")
    for label, ok in rp.get("asserts", []):
        marker = "ok" if ok else "FAIL"
        lines.append(f"- {marker}: {label}")
    return lines


def _render_stage_section(title: str, stage: dict) -> list[str]:
    lines: list[str] = ["", f"## {title}", ""]
    if not stage.get("available"):
        lines.append(f"Skipped: {stage.get('reason', 'not available')}")
        return lines
    if stage.get("passed"):
        lines.append(f"PASS -- {stage['passes']}/{stage['total']} asserts")
    else:
        first = stage.get("first_fail")
        first_label = first[0] if first else "unknown"
        first_detail = first[1] if first else ""
        lines.append(f"FAIL -- {stage['passes']}/{stage['total']} asserts; "
                     f"first failure: {first_label}"
                     + (f" ({first_detail})" if first_detail else ""))
    lines.append("")
    for label, ok in stage.get("asserts", []):
        marker = "ok" if ok else "FAIL"
        lines.append(f"- {marker}: {label}")
    return lines


def render_compact_section(stage: dict) -> list[str]:
    return _render_stage_section("Compact-mode smoke (Stage C)", stage)


def render_cross_pollination_section(stage: dict) -> list[str]:
    return _render_stage_section("Cross-pollination linter smoke (Stage D)", stage)


def render_wishful_section(stage: dict) -> list[str]:
    return _render_stage_section("Wishful-thinking picker smoke (Stage E)", stage)


def render_report(picker_results: dict, corpus_results: dict | None,
                  meta: dict, telemetry_results: dict | None = None,
                  run_planner_results: dict | None = None,
                  compact_results: dict | None = None,
                  cp_results: dict | None = None,
                  wishful_results: dict | None = None) -> str:
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
    archetype_results = {k: v for k, v in picker_results.items() if not k.startswith("__")}
    coverage = picker_results.get("__operator_coverage__", {})
    for arch, r in archetype_results.items():
        ops = ", ".join(f"{k}={v}" for k, v in sorted(r["operator_distribution"].items()))
        lines.append(
            f"| {arch} | {r['runs']} | {r['ok']} | {r['pass_rate']*100:.1f}% | "
            f"{r['unique_words']} | {ops or '-'} |"
        )
    any_picker_fails = False
    for arch, r in archetype_results.items():
        if r["fail_reasons"]:
            any_picker_fails = True
            lines.append("")
            lines.append(f"### Picker fail reasons -- {arch}")
            for reason, count in r["fail_reasons"]:
                lines.append(f"- {count}x: {reason}")
    if not any_picker_fails:
        lines.append("")
        lines.append("All picker runs returned valid JSON with expected schema.")
    if coverage:
        lines.append("")
        lines.append(
            f"Operator coverage across all archetypes: {coverage.get('all_seen', [])} "
            f"(wishful-thinking seen: {coverage.get('wishful_seen', False)})"
        )

    if corpus_results is None:
        lines.append("")
        lines.append("## Corpus (Stage B linter sweep)")
        lines.append("")
        lines.append("Skipped (no corpus dir).")
        if telemetry_results is not None:
            lines.extend(render_telemetry_section(telemetry_results))
        if run_planner_results is not None:
            lines.extend(render_run_planner_section(run_planner_results))
        if compact_results is not None:
            lines.extend(render_compact_section(compact_results))
        if cp_results is not None:
            lines.extend(render_cross_pollination_section(cp_results))
        if wishful_results is not None:
            lines.extend(render_wishful_section(wishful_results))
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

    if telemetry_results is not None:
        lines.extend(render_telemetry_section(telemetry_results))
    if run_planner_results is not None:
        lines.extend(render_run_planner_section(run_planner_results))
    if compact_results is not None:
        lines.extend(render_compact_section(compact_results))
    if cp_results is not None:
        lines.extend(render_cross_pollination_section(cp_results))
    if wishful_results is not None:
        lines.extend(render_wishful_section(wishful_results))

    return "\n".join(lines) + "\n"


def stage_b_telemetry_smoke(telemetry_script: Path, tmp_dir: Path) -> dict:
    """Append + read-back smoke test for telemetry.py (since v0.9.0)."""
    if not telemetry_script.exists():
        return {"available": False, "reason": f"telemetry script not found: {telemetry_script}"}
    tele_path = tmp_dir / "telemetry-smoke.jsonl"
    payload = {
        "run_id": "eval-smoke--first-principles-jester--smoke",
        "timestamp": "2026-04-27T00:00:00Z",
        "mode": "single",
        "topic_slug": "smoke",
        "archetype": "first-principles-jester",
        "word": "smoke",
        "operator": "reversal",
        "re_rolled": "no",
        "distiller_used": False,
        "round2_status": "n/a",
        "time_to_finish_ms": 0,
        "voice_cross_drift_hits": 0,
        "lint_pass": True,
    }
    proc = subprocess.run(
        [sys.executable, str(telemetry_script), "log",
         "--path", str(tele_path),
         "--json", json.dumps(payload)],
        capture_output=True, text=True, timeout=10,
    )
    if proc.returncode != 0:
        return {"available": True, "passed": False,
                "reason": f"log exit {proc.returncode}: {proc.stderr.strip()[:160]}"}
    if not tele_path.exists():
        return {"available": True, "passed": False,
                "reason": "telemetry file was not created"}
    line = tele_path.read_text(encoding="utf-8").strip()
    try:
        rec = json.loads(line)
    except json.JSONDecodeError as e:
        return {"available": True, "passed": False,
                "reason": f"appended line is not JSON: {e}"}
    if rec.get("run_id") != payload["run_id"]:
        return {"available": True, "passed": False,
                "reason": "round-trip mismatch on run_id"}
    sum_proc = subprocess.run(
        [sys.executable, str(telemetry_script), "summary",
         "--path", str(tele_path), "--last", "10"],
        capture_output=True, text=True, timeout=10,
    )
    summary_ok = sum_proc.returncode == 0 and "records analyzed: 1" in sum_proc.stdout
    return {"available": True, "passed": True, "summary_ok": summary_ok,
            "tele_path": str(tele_path)}


def stage_b_run_planner_smoke(run_planner_script: Path,
                              keywords_path: Path,
                              tmp_dir: Path) -> dict:
    """Eight-assert smoke test for run_planner.py (since v0.10.0)."""
    if not run_planner_script.exists():
        return {"available": False,
                "reason": f"run_planner script not found: {run_planner_script}"}
    if not keywords_path.exists():
        return {"available": False,
                "reason": f"keywords file not found: {keywords_path}"}

    asserts: list[tuple[str, bool, str]] = []

    def call(args: list[str]) -> tuple[int, str, str]:
        proc = subprocess.run(
            [sys.executable, str(run_planner_script), *args],
            capture_output=True, text=True, timeout=10,
        )
        return proc.returncode, proc.stdout, proc.stderr

    # 1. archetype -- keyword match (deploy + pipeline -> systems-alchemist)
    rc, out, err = call(["archetype", "--topic",
                         "deploy pipeline simplification",
                         "--keywords", str(keywords_path)])
    ok_1 = False
    detail_1 = ""
    try:
        data = json.loads(out)
        ok_1 = (rc == 0
                and data.get("selected_archetype") == "systems-alchemist"
                and data.get("fallback_used") is False
                and "deploy" in data.get("matched_keywords", [])
                and "pipeline" in data.get("matched_keywords", []))
        if not ok_1:
            detail_1 = f"got rc={rc}, archetype={data.get('selected_archetype')!r}, matches={data.get('matched_keywords')}"
    except (json.JSONDecodeError, AttributeError) as exc:
        detail_1 = f"non-JSON stdout: {exc} / stderr={err.strip()[:120]}"
    asserts.append(("archetype keyword match", ok_1, detail_1))

    # 2. archetype -- no match
    rc, out, _ = call(["archetype", "--topic", "xyzqrt foo bar",
                       "--keywords", str(keywords_path)])
    ok_2 = False
    detail_2 = ""
    try:
        data = json.loads(out)
        ok_2 = (rc == 0
                and data.get("fallback_used") is True
                and data.get("selected_archetype") is None
                and data.get("matched_keywords") == [])
        if not ok_2:
            detail_2 = f"got rc={rc}, archetype={data.get('selected_archetype')!r}, fallback={data.get('fallback_used')}"
    except (json.JSONDecodeError, AttributeError) as exc:
        detail_2 = f"non-JSON stdout: {exc}"
    asserts.append(("archetype no match", ok_2, detail_2))

    # 3. archetype -- tie at position 1 -> fallback
    # Build a temp keywords file with a deliberate tie.
    tie_kw = tmp_dir / "tie-keywords.txt"
    tie_kw.write_text(
        "first-principles-jester: foo\n"
        "labyrinth-librarian: bar\n"
        "systems-alchemist: deploy\n"
        "radagast-brown: forest\n",
        encoding="utf-8",
    )
    rc, out, _ = call(["archetype", "--topic", "forest deploy",
                       "--keywords", str(tie_kw)])
    ok_3 = False
    detail_3 = ""
    try:
        data = json.loads(out)
        ok_3 = (rc == 0
                and data.get("fallback_used") is True
                and data.get("selected_archetype") is None)
        if not ok_3:
            detail_3 = f"got rc={rc}, archetype={data.get('selected_archetype')!r}"
    except (json.JSONDecodeError, AttributeError) as exc:
        detail_3 = f"non-JSON stdout: {exc}"
    asserts.append(("archetype tie -> fallback", ok_3, detail_3))

    # 4. archetype -- case-insensitive substring
    rc, out, _ = call(["archetype", "--topic", "DEPLOYS the SYSTEMS",
                       "--keywords", str(keywords_path)])
    ok_4 = False
    detail_4 = ""
    try:
        data = json.loads(out)
        matches = data.get("matched_keywords", [])
        ok_4 = (rc == 0
                and "deploy" in matches
                and "system" in matches)
        if not ok_4:
            detail_4 = f"got matches={matches}"
    except (json.JSONDecodeError, AttributeError) as exc:
        detail_4 = f"non-JSON stdout: {exc}"
    asserts.append(("archetype case-insensitive substring", ok_4, detail_4))

    # 5. archetype -- empty topic -> exit 1
    rc, _, _ = call(["archetype", "--topic", "",
                     "--keywords", str(keywords_path)])
    ok_5 = (rc == 1)
    detail_5 = "" if ok_5 else f"got rc={rc} expected 1"
    asserts.append(("archetype empty topic -> exit 1", ok_5, detail_5))

    # 6. archetype -- missing keywords file -> exit 2
    rc, _, _ = call(["archetype", "--topic", "deploy",
                     "--keywords", str(tmp_dir / "does-not-exist.txt")])
    ok_6 = (rc == 2)
    detail_6 = "" if ok_6 else f"got rc={rc} expected 2"
    asserts.append(("archetype missing keywords -> exit 2", ok_6, detail_6))

    # 7. session -- extract from "Naechste Schritte"
    sess_a = tmp_dir / "sess-a.md"
    sess_a.write_text(
        "# Test Session\n\n"
        "## Aktueller Stand\n\n- not me\n\n"
        "## Naechste Schritte\n\n"
        "1. **Phase 5 starten** in crazy-professor\n"
        "2. PR reviewen wenn er ankommt\n"
        "3. Codex hat letzte Session gehangen\n"
        "4. fourth bullet should not appear\n\n"
        "## Wichtige Pfade\n\n- ignored\n",
        encoding="utf-8",
    )
    rc, out, _ = call(["session", "--session-path", str(sess_a)])
    ok_7 = False
    detail_7 = ""
    try:
        data = json.loads(out)
        cands = data.get("topic_candidates", [])
        ok_7 = (rc == 0
                and len(cands) == 3
                and "Phase 5 starten" in cands[0]["topic"]
                and cands[0]["rank"] == 1
                and cands[0]["source"].lower().startswith("naechste")
                and cands[2]["rank"] == 3)
        if not ok_7:
            detail_7 = f"got rc={rc}, candidates={cands}"
    except (json.JSONDecodeError, AttributeError) as exc:
        detail_7 = f"non-JSON stdout: {exc}"
    asserts.append(("session naechste schritte extraction", ok_7, detail_7))

    # 8. session -- multiple paths, dedup
    sess_b = tmp_dir / "sess-b.md"
    sess_b.write_text(
        "## Open Items\n\n"
        "- duplicate bullet\n"
        "- new bullet from second file\n"
        "- another new one\n",
        encoding="utf-8",
    )
    sess_a_overlap = tmp_dir / "sess-a-overlap.md"
    sess_a_overlap.write_text(
        "## Naechste Schritte\n\n"
        "1. duplicate bullet\n"
        "2. unique-from-a\n",
        encoding="utf-8",
    )
    rc, out, _ = call(["session",
                       "--session-path", str(sess_a_overlap),
                       "--session-path", str(sess_b)])
    ok_8 = False
    detail_8 = ""
    try:
        data = json.loads(out)
        cands = data.get("topic_candidates", [])
        topics = [c["topic"] for c in cands]
        # First path provides "duplicate bullet" + "unique-from-a", second
        # path adds "new bullet from second file" (we cap at 3, dedup
        # drops the repeated "duplicate bullet" from the second file).
        ok_8 = (rc == 0
                and len(cands) == 3
                and topics.count("duplicate bullet") == 1
                and "unique-from-a" in topics
                and "new bullet from second file" in topics)
        if not ok_8:
            detail_8 = f"got rc={rc}, topics={topics}"
    except (json.JSONDecodeError, AttributeError) as exc:
        detail_8 = f"non-JSON stdout: {exc}"
    asserts.append(("session multi-path dedup", ok_8, detail_8))

    passed = sum(1 for _, ok, _ in asserts if ok)
    total = len(asserts)
    first_fail = next(((label, detail) for label, ok, detail in asserts if not ok), None)
    return {
        "available": True,
        "passed": passed == total,
        "passes": passed,
        "total": total,
        "asserts": [(label, ok) for label, ok, _ in asserts],
        "first_fail": first_fail,
    }


def stage_c_compact_smoke(validator: Path, tmp_dir: Path) -> dict:
    """5-assert smoke test for --chat --compact validator behavior."""
    if not validator.exists():
        return {"available": False,
                "reason": f"validator script not found: {validator}"}

    asserts: list[tuple[str, bool, str]] = []
    normal_chat = """---
skill: crazy-professor
mode: chat
version: 0.11.0
timestamp: 2026-04-29T12:00:00Z
topic: "smoke"
archetypes: [first-principles-jester, labyrinth-librarian, systems-alchemist, radagast-brown]
rounds: 3
distiller: codex
round2_status: full
llm_calls: 10
---

# Chat: smoke

> DIVERGENCE WARNING: smoke test fixture.

## Round 1 -- Parallel Voices

### Jester (word: smoke, operator: reversal)
1. one
2. two
3. three
4. four
5. five

### Librarian (word: smoke, operator: reversal)
1. one
2. two
3. three
4. four
5. five

### Alchemist (word: smoke, operator: reversal)
1. one
2. two
3. three
4. four
5. five

### Radagast (word: smoke, operator: reversal)
1. one
2. two
3. three
4. four
5. five

## Round 2 -- Cross-Pollination

### Jester
- counter: alchemist #1 -- text -- anchor: x
- counter: librarian #2 -- text -- anchor: x

### Librarian
- counter: alchemist #1 -- text -- anchor: x
- counter: jester #2 -- text -- anchor: x

### Alchemist
- counter: jester #1 -- text -- anchor: x
- counter: radagast #2 -- text -- anchor: x

### Radagast
- counter: jester #1 -- text -- anchor: x
- counter: alchemist #2 -- text -- anchor: x

## Round 3 -- Codex Distillation (Final 20)

### Jester-5
1. one -- [cost: low] -- anchor: x -- [score: W=3 U=3 S=3]
2. two -- [cost: low] -- anchor: x -- [score: W=3 U=3 S=3]
3. three -- [cost: low] -- anchor: x -- [score: W=3 U=3 S=3]
4. four -- [cost: low] -- anchor: x -- [score: W=3 U=3 S=3]
5. five -- [cost: low] -- anchor: x -- [score: W=3 U=3 S=3]

### Librarian-5
1. one -- [cost: low] -- anchor: x -- [score: W=3 U=3 S=3]
2. two -- [cost: low] -- anchor: x -- [score: W=3 U=3 S=3]
3. three -- [cost: low] -- anchor: x -- [score: W=3 U=3 S=3]
4. four -- [cost: low] -- anchor: x -- [score: W=3 U=3 S=3]
5. five -- [cost: low] -- anchor: x -- [score: W=3 U=3 S=3]

### Alchemist-5
1. one -- [cost: low] -- anchor: x -- [score: W=3 U=3 S=3]
2. two -- [cost: low] -- anchor: x -- [score: W=3 U=3 S=3]
3. three -- [cost: low] -- anchor: x -- [score: W=3 U=3 S=3]
4. four -- [cost: low] -- anchor: x -- [score: W=3 U=3 S=3]
5. five -- [cost: low] -- anchor: x -- [score: W=3 U=3 S=3]

### Radagast-5
1. one -- [cost: low] -- anchor: x -- [score: W=3 U=3 S=3]
2. two -- [cost: low] -- anchor: x -- [score: W=3 U=3 S=3]
3. three -- [cost: low] -- anchor: x -- [score: W=3 U=3 S=3]
4. four -- [cost: low] -- anchor: x -- [score: W=3 U=3 S=3]
5. five -- [cost: low] -- anchor: x -- [score: W=3 U=3 S=3]

## Top-3 Cross-Pollination Hits
1. ref -- text
2. ref -- text
3. ref -- text

## Next Experiment
Description.

## Self-Flag
- [ ] kept
- [ ] round2-was-degraded
- [ ] distiller-fallback-used
- [ ] voice-cross-drift
"""

    compact_chat = normal_chat.replace(
        "mode: chat\nversion: 0.11.0",
        "mode: chat\ncompact: true\nversion: 0.11.0",
    )
    parts = compact_chat.split("## Round 1")
    head = parts[0]
    rest = "## Round 1" + parts[1]
    sections_after_r2 = rest.split("## Round 3")
    r1_r2 = sections_after_r2[0]
    r3_plus = "## Round 3" + sections_after_r2[1]
    compact_body = (
        head
        + r3_plus.rstrip()
        + "\n\n---\n\n<details>\n<summary>Audit-Trail -- Round 1 + Round 2 (click to expand)</summary>\n\n"
        + r1_r2.rstrip()
        + "\n\n</details>\n"
    )

    def call_validator(content: str) -> tuple[int, str]:
        f = tmp_dir / f"compact-fixture-{abs(hash(content)) % 10000}.md"
        f.write_text(content, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(validator), "--mode", "chat", str(f)],
            capture_output=True, text=True, timeout=10,
        )
        return proc.returncode, proc.stderr

    cmd_md = (Path(__file__).resolve().parent.parent.parent.parent
              / "commands" / "crazy.md")
    ok_1 = False
    detail_1 = ""
    if cmd_md.exists():
        text = cmd_md.read_text(encoding="utf-8")
        ok_1 = "--compact requires --chat" in text
        if not ok_1:
            detail_1 = "commands/crazy.md does not contain reject message"
    else:
        detail_1 = f"commands/crazy.md not found at {cmd_md}"
    asserts.append(("--compact reject documented", ok_1, detail_1))

    rc, err = call_validator(normal_chat)
    ok_2 = (rc == 0)
    asserts.append(("normal-mode chat output validates",
                    ok_2, "" if ok_2 else f"rc={rc}, err={err.strip()[:120]}"))

    rc, err = call_validator(compact_body)
    ok_3 = (rc == 0)
    asserts.append(("compact-mode body validates",
                    ok_3, "" if ok_3 else f"rc={rc}, err={err.strip()[:120]}"))

    bad_compact = normal_chat.replace(
        "mode: chat\nversion: 0.11.0",
        "mode: chat\ncompact: true\nversion: 0.11.0",
    )
    rc, err = call_validator(bad_compact)
    ok_4 = (rc != 0 and "compact-mode order violation" in err)
    asserts.append(("compact:true + normal order rejected",
                    ok_4, "" if ok_4 else f"rc={rc}, err={err.strip()[:160]}"))

    body_no_flag = compact_body.replace(
        "compact: true\n",
        "",
    )
    rc, err = call_validator(body_no_flag)
    ok_5 = (rc != 0 and "normal-mode order violation" in err)
    asserts.append(("compact body without flag rejected",
                    ok_5, "" if ok_5 else f"rc={rc}, err={err.strip()[:160]}"))

    passed = sum(1 for _, ok, _ in asserts if ok)
    total = len(asserts)
    first_fail = next(((label, detail) for label, ok, detail in asserts if not ok), None)
    return {
        "available": True,
        "passed": passed == total,
        "passes": passed,
        "total": total,
        "asserts": [(label, ok) for label, ok, _ in asserts],
        "first_fail": first_fail,
    }


def stage_d_cross_pollination_smoke(linter: Path, tmp_dir: Path) -> dict:
    """8-assert smoke test for lint_cross_pollination.py."""
    if not linter.exists():
        return {"available": False,
                "reason": f"linter script not found: {linter}"}

    asserts: list[tuple[str, bool, str]] = []

    def call(r1: dict, r2: dict, extra_args: list[str] | None = None) -> tuple[int, dict]:
        r1_p = tmp_dir / f"r1-{abs(hash(json.dumps(r1, sort_keys=True))) % 10000}.json"
        r2_p = tmp_dir / f"r2-{abs(hash(json.dumps(r2, sort_keys=True))) % 10000}.json"
        r1_p.write_text(json.dumps(r1), encoding="utf-8")
        r2_p.write_text(json.dumps(r2), encoding="utf-8")
        cmd = [sys.executable, str(linter),
               "--r1-input", str(r1_p), "--r2-input", str(r2_p)]
        if extra_args:
            cmd.extend(extra_args)
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        out = json.loads(proc.stdout) if proc.stdout.strip() else {}
        return proc.returncode, out

    base_r1 = {
        "jester": {"1": "the jester sees the assumption as a reactor"},
        "librarian": {"1": "history shows the same pattern"},
        "alchemist": {"1": "the reactor leaks plasma into the overflow tank",
                      "3": "deploy pipeline membrane filters"},
        "radagast": {"1": "the forest still breathes"},
    }

    rc, out = call(base_r1, {
        "jester": [], "librarian": [], "alchemist": [],
        "radagast": [{"idx": 1, "marker": None, "ref": None, "text": "no marker here"}],
    })
    ok_1 = (out.get("low_substance_hits") == 1
            and out["findings"][0]["severity"] == "error"
            and "no counter/extend marker" in out["findings"][0]["reason"])
    asserts.append(("marker missing -> error",
                    ok_1, "" if ok_1 else f"got {out}"))

    rc, out = call(base_r1, {
        "jester": [], "librarian": [], "alchemist": [],
        "radagast": [{"idx": 1, "marker": "extend", "ref": "librarian #6",
                      "ref_archetype": "librarian", "ref_idx": 6, "text": "the forest"}],
    })
    ok_2 = (out.get("low_substance_hits") == 1
            and out["findings"][0]["severity"] == "error"
            and "idx 6 out of range" in out["findings"][0]["reason"])
    asserts.append(("ref idx out of range -> error",
                    ok_2, "" if ok_2 else f"got {out}"))

    rc, out = call(base_r1, {
        "jester": [], "librarian": [], "alchemist": [],
        "radagast": [{"idx": 1, "marker": "counter", "ref": "alchemist #2",
                      "ref_archetype": "alchemist", "ref_idx": 2, "text": "x"}],
    })
    ok_3 = (out.get("low_substance_hits") == 1
            and out["findings"][0]["severity"] == "error"
            and "not present" in out["findings"][0]["reason"])
    asserts.append(("ref to non-existent R1 item -> error",
                    ok_3, "" if ok_3 else f"got {out}"))

    rc, out = call(base_r1, {
        "jester": [], "librarian": [], "alchemist": [],
        "radagast": [{"idx": 1, "marker": "extend", "ref": "alchemist #1",
                      "ref_archetype": "alchemist", "ref_idx": 1,
                      "text": "the forest hides everything else"}],
    })
    ok_4 = (out.get("low_substance_hits") == 1
            and out["findings"][0]["severity"] == "warn"
            and "token overlap" in out["findings"][0]["reason"])
    asserts.append(("0 overlap -> warn",
                    ok_4, "" if ok_4 else f"got {out}"))

    rc, out = call(base_r1, {
        "jester": [], "librarian": [], "alchemist": [],
        "radagast": [{"idx": 1, "marker": "extend", "ref": "alchemist #1",
                      "ref_archetype": "alchemist", "ref_idx": 1,
                      "text": "the reactor needs a quiet forest cap"}],
    })
    ok_5 = (out.get("low_substance_hits") == 0
            and out["findings"] == [])
    asserts.append(("overlap >= 1 -> pass",
                    ok_5, "" if ok_5 else f"got {out}"))

    rc, out = call(base_r1, {
        "jester": [], "librarian": [], "alchemist": [],
        "radagast": [{"idx": 1, "marker": "extend", "ref": "alchemist #1",
                      "ref_archetype": "alchemist", "ref_idx": 1,
                      "text": "the swift cap of the cloud"}],
    })
    ok_6 = (out.get("low_substance_hits") == 1
            and out["findings"][0]["severity"] == "warn")
    asserts.append(("stop-word-only overlap -> warn",
                    ok_6, "" if ok_6 else f"got {out}"))

    rc, out = call(base_r1, {"jester": [], "librarian": [], "alchemist": [], "radagast": []})
    ok_7 = ("low_substance_hits" in out and "findings" in out
            and "stats" in out and "by_severity" in out["stats"])
    asserts.append(("JSON output schema",
                    ok_7, "" if ok_7 else f"got keys: {list(out.keys())}"))

    rc_a, _ = call(base_r1, {"jester": [], "librarian": [], "alchemist": [], "radagast": []})
    rc_b, _ = call(base_r1, {
        "jester": [], "librarian": [], "alchemist": [],
        "radagast": [{"idx": 1, "marker": None, "ref": None, "text": "x"}],
    })
    ok_8 = (rc_a == 0 and rc_b == 0)
    asserts.append(("exit 0 always",
                    ok_8, "" if ok_8 else f"rc_a={rc_a}, rc_b={rc_b}"))

    passed = sum(1 for _, ok, _ in asserts if ok)
    total = len(asserts)
    first_fail = next(((label, detail) for label, ok, detail in asserts if not ok), None)
    return {
        "available": True,
        "passed": passed == total,
        "passes": passed,
        "total": total,
        "asserts": [(label, ok) for label, ok, _ in asserts],
        "first_fail": first_fail,
    }


def stage_e_wishful_smoke(picker: Path, words: Path, retired: Path,
                          init_template: Path, tmp_dir: Path) -> dict:
    """6-assert smoke test for wishful-thinking operator."""
    if not picker.exists():
        return {"available": False,
                "reason": f"picker script not found: {picker}"}

    asserts: list[tuple[str, bool, str]] = []

    def run_n(share: float, n: int) -> Counter:
        ops: Counter = Counter()
        fn_path = tmp_dir / f"wishful-fn-{share}.md"
        if fn_path.exists():
            fn_path.unlink()
        for i in range(n):
            sec = i % 60
            us = (i * 17) % 999999
            ts = f"2026-04-29T12:00:{sec:02d}.{us:06d}+00:00"
            cmd = [sys.executable, str(picker),
                   "--field-notes", str(fn_path),
                   "--words", str(words),
                   "--retired", str(retired),
                   "--init-template", str(init_template),
                   "--mode", "single",
                   "--wishful-share", str(share),
                   "--force-timestamp", ts]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if proc.returncode == 0:
                try:
                    data = json.loads(proc.stdout)
                    ops[data["operator"]] += 1
                except (json.JSONDecodeError, KeyError):
                    pass
        return ops

    ops = run_n(0.0, 200)
    ok_1 = ("wishful-thinking" not in ops
            and sum(ops[k] for k in ("reversal", "exaggeration", "escape")) > 0)
    asserts.append(("share=0.0 -> only base operators",
                    ok_1, "" if ok_1 else f"got {dict(ops)}"))

    ops = run_n(0.25, 200)
    wt = ops.get("wishful-thinking", 0)
    ok_2 = (1 <= wt <= 50)
    asserts.append(("share=0.25 -> 1..50 wishful",
                    ok_2, "" if ok_2 else f"wt={wt} of {sum(ops.values())}"))

    ops = run_n(1.0, 200)
    counts = [ops.get(k, 0) for k in ("reversal", "exaggeration", "escape", "wishful-thinking")]
    # At share=1.0 weights are [1,1,1,3] -> wishful ~50%, others ~16.7% each.
    # Loose bounds because timestamps are not perfectly uniform: each base
    # operator >= 10 (well below expected 33), wishful in [60, 140].
    base_min_ok = all(c >= 10 for c in counts[:3])
    wishful_ok = 60 <= counts[3] <= 140
    ok_3 = base_min_ok and wishful_ok
    asserts.append(("share=1.0 -> all 4 present, wishful ~50%",
                    ok_3, "" if ok_3 else f"got counts={counts}"))

    fn_path = tmp_dir / "wishful-invalid-fn.md"
    if fn_path.exists():
        fn_path.unlink()
    proc = subprocess.run(
        [sys.executable, str(picker),
         "--field-notes", str(fn_path),
         "--words", str(words),
         "--retired", str(retired),
         "--init-template", str(init_template),
         "--mode", "single",
         "--wishful-share", "-0.5"],
        capture_output=True, text=True, timeout=10,
    )
    ok_4 = (proc.returncode != 0)
    asserts.append(("invalid share rejected",
                    ok_4, "" if ok_4 else f"rc={proc.returncode}"))

    fixture = tmp_dir / "wishful-validator-fixture.md"
    fixture.write_text("""---
skill: crazy-professor
mode: single
version: 0.11.0
timestamp: 2026-04-29T12:00:00Z
topic: "smoke"
archetype: first-principles-jester
po_operator: wishful-thinking
provocation_word: smoke
---

# Single: smoke

> DIVERGENCE WARNING: smoke fixture.

## 10 Provocations

1. one -- [cost: low] -- anchor: x
2. two -- [cost: low] -- anchor: x
3. three -- [cost: low] -- anchor: x
4. four -- [cost: low] -- anchor: x
5. five -- [cost: low] -- anchor: x
6. six -- [cost: low] -- anchor: x
7. seven -- [cost: low] -- anchor: x
8. eight -- [cost: low] -- anchor: x
9. nine -- [cost: low] -- anchor: x
10. ten -- [cost: low] -- anchor: x

## Next Experiment
Run a smoke.

## Self-Flag
- [ ] kept
- [ ] retire-word
- [ ] voice-off
""", encoding="utf-8")
    validator = picker.parent / "validate_output.py"
    proc = subprocess.run(
        [sys.executable, str(validator), "--mode", "single", str(fixture)],
        capture_output=True, text=True, timeout=10,
    )
    ok_5 = (proc.returncode == 0)
    asserts.append(("validator accepts wishful-thinking",
                    ok_5, "" if ok_5 else f"rc={proc.returncode}, err={proc.stderr.strip()[:120]}"))

    fixture2 = tmp_dir / "wishful-body-fixture.md"
    body = fixture.read_text(encoding="utf-8").replace(
        "1. one -- [cost: low] -- anchor: x",
        "1. wishful thinking: deploys happen without prerequisites -- [cost: low] -- anchor: x"
    )
    fixture2.write_text(body, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(validator), "--mode", "single", str(fixture2)],
        capture_output=True, text=True, timeout=10,
    )
    ok_6 = (proc.returncode == 0)
    asserts.append(("body with wishful scaffold validates",
                    ok_6, "" if ok_6 else f"rc={proc.returncode}, err={proc.stderr.strip()[:120]}"))

    passed = sum(1 for _, ok, _ in asserts if ok)
    total = len(asserts)
    first_fail = next(((label, detail) for label, ok, detail in asserts if not ok), None)
    return {
        "available": True,
        "passed": passed == total,
        "passes": passed,
        "total": total,
        "asserts": [(label, ok) for label, ok, _ in asserts],
        "first_fail": first_fail,
    }


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
    p.add_argument("--telemetry", type=Path, default=None,
                   help="path to telemetry.py for the smoke test (default: skip)")
    p.add_argument("--run-planner", type=Path, default=None,
                   help="path to run_planner.py for the smoke test (default: skip)")
    p.add_argument("--run-planner-keywords", type=Path, default=None,
                   help="path to archetype-keywords.txt (required if --run-planner)")
    p.add_argument("--cross-pollination-linter", type=Path, default=None,
                   help="path to lint_cross_pollination.py for Stage D smoke")
    p.add_argument("--compact", action="store_true",
                   help="run Stage C (compact-mode validator smoke)")
    p.add_argument("--cross-pollination", action="store_true",
                   help="run Stage D (cross-pollination linter smoke)")
    p.add_argument("--wishful", action="store_true",
                   help="run Stage E (wishful-thinking picker smoke)")
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

    telemetry_results: dict | None = None
    if args.telemetry:
        print(f"running telemetry smoke test against {args.telemetry}...",
              file=sys.stderr)
        telemetry_results = stage_b_telemetry_smoke(args.telemetry, tmp_dir)

    run_planner_results: dict | None = None
    if args.run_planner:
        if not args.run_planner_keywords:
            print("error: --run-planner-keywords is required when --run-planner is set",
                  file=sys.stderr)
            return 2
        print(f"running run_planner smoke test against {args.run_planner}...",
              file=sys.stderr)
        run_planner_results = stage_b_run_planner_smoke(
            args.run_planner, args.run_planner_keywords, tmp_dir,
        )

    compact_results: dict | None = None
    if args.compact:
        print(f"running compact-mode smoke test...", file=sys.stderr)
        compact_results = stage_c_compact_smoke(args.validator, tmp_dir)

    cp_results: dict | None = None
    if args.cross_pollination:
        if not args.cross_pollination_linter:
            print("error: --cross-pollination-linter is required when --cross-pollination is set",
                  file=sys.stderr)
            return 2
        print(f"running cross-pollination linter smoke test...", file=sys.stderr)
        cp_results = stage_d_cross_pollination_smoke(args.cross_pollination_linter, tmp_dir)

    wishful_results: dict | None = None
    if args.wishful:
        print(f"running wishful-thinking picker smoke test...", file=sys.stderr)
        wishful_results = stage_e_wishful_smoke(
            args.picker, args.words, args.retired,
            args.field_notes_template, tmp_dir,
        )

    meta = {
        "date": dt.date.today().isoformat(),
        "picker_runs": args.picker_runs,
        "corpus_dir": str(args.corpus) if args.corpus else "(none)",
        "strict_voice": args.strict_voice,
        "skill_version": args.skill_version,
    }
    report = render_report(picker_results, corpus_results, meta,
                           telemetry_results, run_planner_results,
                           compact_results, cp_results, wishful_results)
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
