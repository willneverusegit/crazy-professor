#!/usr/bin/env python3
"""
crazy-professor telemetry layer -- append-only JSONL run log.

Writes one JSON object per line to a telemetry file (default lives next
to field-notes.md in the lab corpus). Schema is intentionally flat and
stable: any new field added later must be optional, never required.

Schema (per run, single-mode):
    run_id              str    "<utc-iso>--<archetype>--<slug-or-none>"
    timestamp           str    UTC ISO-8601 ("...Z")
    mode                str    "single" | "chat"
    topic_slug          str    short kebab slug or "" if not provided
    archetype           str    final picked archetype (post-variation-guard)
    word                str    final picked word
    operator            str    "reversal" | "exaggeration" | "escape"
    re_rolled           str    "no" | "archetype" | "word" | "both" | "forced-archetype" | ...
    distiller_used      bool   true if codex round-2 distiller ran
    round2_status       str    "n/a" | "ok" | "skipped" | "failed"
    time_to_finish_ms   int    wall-clock ms from picker to validator-pass
    voice_cross_drift_hits int  count from lint_voice.py FAIL/WARN findings
    lint_pass           bool   true if all linters pass strict-mode

Schema (per run, chat-mode):
    run_id              str    "<utc-iso>--chat--<slug>"
    timestamp           str
    mode                "chat"
    topic_slug          str
    picks               list   [{archetype, word, operator, re_rolled}, ...]  (4 entries)
    distiller_used      bool
    round2_status       str
    time_to_finish_ms   int
    voice_cross_drift_hits int
    lint_pass           bool

Usage:
    telemetry.py log --path <jsonl> --json '{...}'
    telemetry.py log --path <jsonl> --stdin           # read JSON from stdin
    telemetry.py summary --path <jsonl> [--last N]    # default --last 50
    telemetry.py default-path                          # print default telemetry path

Default path: $XDG_DATA_HOME or
  Desktop/.agent-memory/lab/crazy-professor/telemetry.jsonl

Exit codes:
    0  ok
    1  usage error / unwritable path / unparseable JSON
    2  schema-violation (unknown mode, missing required field)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

REQUIRED_FIELDS_COMMON = (
    "run_id", "timestamp", "mode", "topic_slug",
    "distiller_used", "round2_status", "time_to_finish_ms",
    "voice_cross_drift_hits", "lint_pass",
)
REQUIRED_FIELDS_SINGLE = REQUIRED_FIELDS_COMMON + (
    "archetype", "word", "operator", "re_rolled",
)
REQUIRED_FIELDS_CHAT = REQUIRED_FIELDS_COMMON + ("picks",)
VALID_MODES = ("single", "chat")
VALID_ROUND2 = ("n/a", "ok", "skipped", "failed")
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB hard cap; rotation is manual


def default_path() -> Path:
    """Default telemetry path: lab corpus next to field-notes.md."""
    home = Path(os.path.expanduser("~"))
    return home / "Desktop" / ".agent-memory" / "lab" / "crazy-professor" / "telemetry.jsonl"


def validate_record(rec: dict) -> tuple[bool, str]:
    """Return (ok, error_message). ok=True means schema accepted."""
    if not isinstance(rec, dict):
        return False, "record is not a JSON object"
    mode = rec.get("mode")
    if mode not in VALID_MODES:
        return False, f"unknown mode: {mode!r} (expected one of {VALID_MODES})"
    required = REQUIRED_FIELDS_SINGLE if mode == "single" else REQUIRED_FIELDS_CHAT
    missing = [f for f in required if f not in rec]
    if missing:
        return False, f"missing required fields: {missing}"
    if rec.get("round2_status") not in VALID_ROUND2:
        return False, f"invalid round2_status: {rec.get('round2_status')!r}"
    if mode == "chat":
        picks = rec.get("picks")
        if not isinstance(picks, list) or len(picks) != 4:
            return False, "chat mode requires picks list of length 4"
        for i, p in enumerate(picks):
            for k in ("archetype", "word", "operator", "re_rolled"):
                if k not in p:
                    return False, f"chat picks[{i}] missing field {k!r}"
    return True, ""


def cmd_log(args) -> int:
    if args.json and args.stdin:
        print("error: --json and --stdin are mutually exclusive", file=sys.stderr)
        return 1
    if args.stdin:
        raw = sys.stdin.read()
    elif args.json is not None:
        raw = args.json
    else:
        print("error: provide either --json or --stdin", file=sys.stderr)
        return 1
    try:
        rec = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 1
    ok, msg = validate_record(rec)
    if not ok:
        print(f"error: schema violation: {msg}", file=sys.stderr)
        return 2

    path = Path(args.path) if args.path else default_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > MAX_FILE_SIZE_BYTES:
        print(
            f"error: telemetry file exceeds {MAX_FILE_SIZE_BYTES} bytes; "
            f"rotate or archive before logging more.",
            file=sys.stderr,
        )
        return 1

    line = json.dumps(rec, ensure_ascii=False, sort_keys=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    if args.verbose:
        print(f"appended 1 record to {path}", file=sys.stderr)
    return 0


def cmd_summary(args) -> int:
    path = Path(args.path) if args.path else default_path()
    if not path.exists():
        print(f"no telemetry file at {path}")
        return 0
    records: list[dict] = []
    bad_lines = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                bad_lines += 1
    if not records:
        print(f"telemetry file empty: {path}")
        return 0

    last_n = records[-args.last:] if args.last > 0 else records
    total = len(last_n)
    modes = Counter(r.get("mode", "?") for r in last_n)
    re_rolled = Counter()
    archetypes = Counter()
    operators = Counter()
    distiller_runs = 0
    voice_hits_total = 0
    lint_pass_count = 0
    time_total_ms = 0
    time_count = 0
    for r in last_n:
        if r.get("distiller_used"):
            distiller_runs += 1
        voice_hits_total += int(r.get("voice_cross_drift_hits", 0) or 0)
        if r.get("lint_pass"):
            lint_pass_count += 1
        t = r.get("time_to_finish_ms")
        if isinstance(t, (int, float)) and t >= 0:
            time_total_ms += int(t)
            time_count += 1
        if r.get("mode") == "single":
            re_rolled[r.get("re_rolled", "?")] += 1
            archetypes[r.get("archetype", "?")] += 1
            operators[r.get("operator", "?")] += 1
        elif r.get("mode") == "chat":
            for pick in r.get("picks", []):
                re_rolled[pick.get("re_rolled", "?")] += 1
                archetypes[pick.get("archetype", "?")] += 1
                operators[pick.get("operator", "?")] += 1

    avg_ms = round(time_total_ms / time_count) if time_count else 0
    print(f"telemetry summary: {path}")
    print(f"  records analyzed: {total} (last {args.last}, total in file: {len(records)})")
    if bad_lines:
        print(f"  WARN: {bad_lines} malformed lines skipped")
    print(f"  modes: {dict(modes)}")
    print(f"  archetypes: {dict(archetypes.most_common())}")
    print(f"  operators: {dict(operators.most_common())}")
    print(f"  re_rolled: {dict(re_rolled.most_common())}")
    print(f"  distiller_used: {distiller_runs}/{total}")
    print(f"  lint_pass: {lint_pass_count}/{total}")
    print(f"  voice_cross_drift_hits (sum): {voice_hits_total}")
    print(f"  avg time_to_finish_ms: {avg_ms} (n={time_count})")
    return 0


def cmd_default_path(_args) -> int:
    print(default_path())
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="crazy-professor telemetry layer")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_log = sub.add_parser("log", help="append one JSON record to the telemetry file")
    p_log.add_argument("--path", help="telemetry JSONL path (default: lab corpus)")
    p_log.add_argument("--json", help="JSON record as a string")
    p_log.add_argument("--stdin", action="store_true", help="read JSON record from stdin")
    p_log.add_argument("--verbose", action="store_true")
    p_log.set_defaults(func=cmd_log)

    p_sum = sub.add_parser("summary", help="aggregate the last N records")
    p_sum.add_argument("--path", help="telemetry JSONL path (default: lab corpus)")
    p_sum.add_argument("--last", type=int, default=50, help="how many recent records (default 50, 0=all)")
    p_sum.set_defaults(func=cmd_summary)

    p_dp = sub.add_parser("default-path", help="print the default telemetry path")
    p_dp.set_defaults(func=cmd_default_path)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
