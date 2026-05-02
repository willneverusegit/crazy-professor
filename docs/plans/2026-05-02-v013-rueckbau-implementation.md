# crazy-professor v0.13.0 Rückbau — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** crazy-professor von 11 Skripten / 7 Flags / 494-Zeilen-Pflichtlektüre auf 1 Skript (`picker.py`) / 3 Flags / ~80-Zeilen-Operating-Instructions zurückbauen. Single-Run + Chat-Mode + `/crazy --lab` bleiben funktional. Lerngeschichte im CHANGELOG dokumentiert.

**Architecture:** Hard-Delete-Strategie: Files weg, git-Historie als Archiv. Direkt auf `master`, ein Commit pro logischem Schritt (10 Code-Commits + Smoke-Test). Reihenfolge so gewählt, dass jeder Commit ein lauffähiges Repo hinterlässt.

**Tech Stack:** Markdown, Python 3 stdlib (`picker.py` only), kein Test-Framework (Smoke-Test ist manuell — der Skill ist Prompt-Material, kein klassischer Code).

**Spec:** `docs/specs/2026-05-02-v013-rueckbau-design.md` (Commit `e80996c`)

---

## File Structure

Jeder Task macht entweder Löschungen oder kleinteilige Edits an genau bezeichneten Stellen. Keine Files werden neu erstellt außer dem CHANGELOG-Eintrag (der wird in Task 10 in den existierenden CHANGELOG appended). Die folgenden Files werden ausschließlich gelesen/referenziert (nicht modifiziert): `provocation-words.txt`, `retired-words.txt`, `po-operators.md`, alle 4 Archetype-Templates *außer* den letzten YAML-Block.

---

## Vorab — Pre-Flight-Check (kein Commit)

- [ ] **Pre-Flight Step 1: Repo-Stand verifizieren**

```bash
cd C:/Users/domes/Desktop/Claude-Plugins-Skills/crazy-professor
git status --short
git log --oneline -3
```

Erwartet: HEAD ist `e80996c` (Spec-Commit), 11 modified Files (mit `M`-Marker) + 5 untracked Files plus dieser Plan (mit `??`-Marker). Der Plan selbst (`docs/plans/2026-05-02-v013-rueckbau-implementation.md`) ist als untracked sichtbar bevor er in Task 1 committet wird.

Falls HEAD NICHT auf dem Spec-Commit ist: STOP, klären mit User.

- [ ] **Pre-Flight Step 2: Spec lesen**

Lies das Spec-File einmal komplett:
- `docs/specs/2026-05-02-v013-rueckbau-design.md`

Stelle sicher, dass jede Bullet-Liste in der Spec eine entsprechende Aktion in einem der Tasks hat. Falls Lücke gefunden: STOP, dem User berichten.

---

## Task 1: Implementation-Plan committen

**Files:**
- Modify (add): `docs/plans/2026-05-02-v013-rueckbau-implementation.md` (dieser Plan, aktuell untracked)

- [ ] **Step 1: Status prüfen**

```bash
cd C:/Users/domes/Desktop/Claude-Plugins-Skills/crazy-professor
git status --short docs/plans/2026-05-02-v013-rueckbau-implementation.md
```

Erwartet: `?? docs/plans/2026-05-02-v013-rueckbau-implementation.md`

- [ ] **Step 2: Plan committen**

```bash
git add docs/plans/2026-05-02-v013-rueckbau-implementation.md
git commit -m "$(cat <<'EOF'
crazy-professor | plan v0.13.0 — Rückbau-Implementation-Plan

Schrittweiser Rückbau-Plan zur Spec e80996c. 10 Code-Commits +
manueller Smoke-Test. Hard-Delete-Strategie, direkt auf master.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 3: Commit verifizieren**

```bash
git log --oneline -1
```

Erwartet: `<hash> crazy-professor | plan v0.13.0 — Rückbau-Implementation-Plan`

---

## Task 2: Plan-/Spec-Dokumente löschen

**Files:**
- Delete: `docs/specs/2026-04-28-phase-5-run-planner-design.md`
- Delete: `docs/specs/2026-04-28-phase-6-cross-pollination-compact-design.md`
- Delete: `docs/specs/2026-04-28-phase-7-playground-design.md`
- Delete: `docs/specs/2026-04-30-phase-8-telegram-solution-dialogue.md` (untracked)
- Delete: `docs/specs/2026-04-30-ideation-lab-v2.md` (untracked)
- Delete: `docs/plans/2026-04-30-ideation-lab-v2-implementation.md` (untracked)
- Delete: `docs/eval-baseline-2026-04-27.md`
- Delete: `docs/eval-baseline-2026-04-28.md`
- Delete: `docs/USAGE-PATTERNS.md`
- Delete: `docs/linters.md`

(Note: Phase-2/3/4-Plans bleiben, weil sie historische Belege gebauter Phasen sind — siehe Spec.)

- [ ] **Step 1: Existenz prüfen**

```bash
ls docs/specs/2026-04-28-phase-5-run-planner-design.md \
   docs/specs/2026-04-28-phase-6-cross-pollination-compact-design.md \
   docs/specs/2026-04-28-phase-7-playground-design.md \
   docs/specs/2026-04-30-phase-8-telegram-solution-dialogue.md \
   docs/specs/2026-04-30-ideation-lab-v2.md \
   docs/plans/2026-04-30-ideation-lab-v2-implementation.md \
   docs/eval-baseline-2026-04-27.md \
   docs/eval-baseline-2026-04-28.md \
   docs/USAGE-PATTERNS.md \
   docs/linters.md
```

Erwartet: alle 10 existieren.

- [ ] **Step 2: Tracked Files löschen via git rm**

```bash
git rm docs/specs/2026-04-28-phase-5-run-planner-design.md
git rm docs/specs/2026-04-28-phase-6-cross-pollination-compact-design.md
git rm docs/specs/2026-04-28-phase-7-playground-design.md
git rm docs/eval-baseline-2026-04-27.md
git rm docs/eval-baseline-2026-04-28.md
git rm docs/USAGE-PATTERNS.md
git rm docs/linters.md
```

Erwartet: 7 "rm" Bestätigungen.

- [ ] **Step 3: Untracked Files löschen via plain rm**

```bash
rm docs/specs/2026-04-30-phase-8-telegram-solution-dialogue.md
rm docs/specs/2026-04-30-ideation-lab-v2.md
rm docs/plans/2026-04-30-ideation-lab-v2-implementation.md
```

- [ ] **Step 4: Verifizieren — kein File übrig**

```bash
ls docs/specs/ docs/plans/ docs/eval-baseline-*.md docs/USAGE-PATTERNS.md docs/linters.md 2>&1
```

Erwartet (in `docs/specs/` und `docs/plans/`):
- `docs/specs/` enthält nur noch `2026-05-02-v013-rueckbau-design.md`
- `docs/plans/` enthält die historischen Phase-2/3/4-Plans (`2026-04-22-crazy-professor-v040-master-plan.md`, `2026-04-23-crazy-professor-v050-chat-mode-master-plan.md`, `2026-04-23-crazy-professor-v051-codex-prompt-fix.md`, `2026-04-26-crazy-professor-erweiterungs-master-plan.md`, `2026-04-28-phase-5-run-planner-implementation.md`, `2026-04-28-phase-6-cross-pollination-compact-implementation.md`, `2026-04-28-phase-7-playground-implementation.md`) plus diesen neuen Plan (`2026-05-02-v013-rueckbau-implementation.md`)
- `docs/eval-baseline-*.md`, `docs/USAGE-PATTERNS.md`, `docs/linters.md`: alle "No such file" Fehler

Wichtige Korrektur: Phase 5/6/7-Implementation-Plans (2026-04-28-phase-*-implementation.md) bleiben als historische Belege gebauter Phasen, parallel zu Phase-2/3/4 (siehe Spec-Klausel "Phase-2/3/4-Plans bleiben"). Nur die Specs/Designs der Phasen 5/6/7 wurden gelöscht.

- [ ] **Step 5: Commit**

```bash
git add -A docs/
git commit -m "$(cat <<'EOF'
crazy-professor | rueckbau 2/10 — Plan-/Spec-Files aufgeräumt

10 Plan-/Spec-Files gelöscht (Phase 5/6/7-Designs, Phase-8-Spec,
Ideation-Lab-v2, eval-baselines, USAGE-PATTERNS-Doppel, linters.md).
Phase-2/3/4 + Phase-5/6/7-Implementation-Plans bleiben als historische
Belege.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 6: Status prüfen**

```bash
git status --short docs/
git log --oneline -1
```

Erwartet: `docs/` clean (außer evtl. CHANGELOG.md / PROJECT.md / etc., die kommen erst in Task 10). HEAD-Commit ist der neue.

---

## Task 3: Skripte löschen (10 Python-Files + 1 Shell-Wrapper)

**Files:**
- Delete: `skills/crazy-professor/scripts/validate_output.py`
- Delete: `skills/crazy-professor/scripts/lint_voice.py`
- Delete: `skills/crazy-professor/scripts/lint_word_pool.py`
- Delete: `skills/crazy-professor/scripts/lint_cross_pollination.py`
- Delete: `skills/crazy-professor/scripts/eval_suite.py`
- Delete: `skills/crazy-professor/scripts/telemetry.py`
- Delete: `skills/crazy-professor/scripts/patch_suggester.py`
- Delete: `skills/crazy-professor/scripts/run_planner.py`
- Delete: `skills/crazy-professor/scripts/build_playground.py`
- Delete: `skills/crazy-professor/scripts/telegram_dialogue.py` (untracked)
- Delete: `skills/crazy-professor/scripts/run_linters.sh` (Shell-Wrapper)

(Bleibt: `skills/crazy-professor/scripts/picker.py`)

- [ ] **Step 1: Listen aller Scripts**

```bash
ls skills/crazy-professor/scripts/
```

Erwartet: 11 Files (10 .py + 1 .sh) inkl. `picker.py`.

- [ ] **Step 2: Tracked Skripte löschen**

```bash
git rm skills/crazy-professor/scripts/validate_output.py
git rm skills/crazy-professor/scripts/lint_voice.py
git rm skills/crazy-professor/scripts/lint_word_pool.py
git rm skills/crazy-professor/scripts/lint_cross_pollination.py
git rm skills/crazy-professor/scripts/eval_suite.py
git rm skills/crazy-professor/scripts/telemetry.py
git rm skills/crazy-professor/scripts/patch_suggester.py
git rm skills/crazy-professor/scripts/run_planner.py
git rm skills/crazy-professor/scripts/build_playground.py
git rm skills/crazy-professor/scripts/run_linters.sh
```

Erwartet: 10 "rm"-Bestätigungen.

- [ ] **Step 3: Untracked telegram_dialogue.py löschen**

```bash
rm skills/crazy-professor/scripts/telegram_dialogue.py
```

- [ ] **Step 4: Verifizieren — nur picker.py übrig**

```bash
ls skills/crazy-professor/scripts/
```

Erwartet: nur `picker.py`.

- [ ] **Step 5: Commit**

```bash
git add -A skills/crazy-professor/scripts/
git commit -m "$(cat <<'EOF'
crazy-professor | rueckbau 3/10 — 10 Scripts + 1 Shell-Wrapper gelöscht

validate_output, lint_voice, lint_word_pool, lint_cross_pollination,
eval_suite, telemetry, patch_suggester, run_planner, telegram_dialogue,
build_playground, run_linters.sh entfernt. Bleibt: picker.py.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 6: Verify**

```bash
git status --short
git log --oneline -1
```

---

## Task 4: Resources aufräumen

**Files:**
- Delete: `skills/crazy-professor/resources/archetype-keywords.txt`
- Delete: `skills/crazy-professor/resources/stop-words.txt`
- Delete: `skills/crazy-professor/resources/field-notes-init.md`

(Bleibt: `provocation-words.txt`, `retired-words.txt`, `po-operators.md`, `output-template.md`, `chat-output-template.md`, `field-notes-schema.md`)

- [ ] **Step 1: Existenz prüfen**

```bash
ls skills/crazy-professor/resources/archetype-keywords.txt \
   skills/crazy-professor/resources/stop-words.txt \
   skills/crazy-professor/resources/field-notes-init.md
```

Erwartet: alle 3 existieren.

- [ ] **Step 2: Löschen**

```bash
git rm skills/crazy-professor/resources/archetype-keywords.txt
git rm skills/crazy-professor/resources/stop-words.txt
git rm skills/crazy-professor/resources/field-notes-init.md
```

- [ ] **Step 3: Verifizieren**

```bash
ls skills/crazy-professor/resources/
```

Erwartet: nur noch `provocation-words.txt`, `retired-words.txt`, `po-operators.md`, `output-template.md`, `chat-output-template.md`, `field-notes-schema.md`.

- [ ] **Step 4: Commit**

```bash
git commit -m "$(cat <<'EOF'
crazy-professor | rueckbau 4/10 — 3 Resource-Files gelöscht

archetype-keywords.txt (run_planner-Daten), stop-words.txt
(lint_cross_pollination-Daten), field-notes-init.md (Init-Logik wandert
in picker.py-Docstring) entfernt.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: playground/-Ordner löschen

**Files:**
- Delete: `skills/crazy-professor/playground/` (Ordner mit `index.html` und ggf. anderen Files)

- [ ] **Step 1: Inhalt zeigen**

```bash
ls -la skills/crazy-professor/playground/
```

- [ ] **Step 2: Ordner-Inhalt löschen via git rm -r**

```bash
git rm -r skills/crazy-professor/playground/
```

Erwartet: 1+ "rm"-Bestätigungen je nach Inhalt.

- [ ] **Step 3: Verifizieren**

```bash
ls skills/crazy-professor/playground/ 2>&1
```

Erwartet: "No such file or directory".

- [ ] **Step 4: Commit**

```bash
git commit -m "$(cat <<'EOF'
crazy-professor | rueckbau 5/10 — playground/-Ordner gelöscht

Phase-7-Browser-Playground komplett entfernt. Lab-Browser unter
skills/crazy-professor/lab/ bleibt unverändert (separate Komponente).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: References aufräumen

**Files:**
- Delete: `skills/crazy-professor/references/chat-mode-flow.md` (Stub)
- Delete: `skills/crazy-professor/references/radagast-activation.md`
- Delete: `skills/crazy-professor/references/review-rubric.md`
- Delete: `skills/crazy-professor/references/usage-patterns.md`

(Bleibt: `operating-instructions.md`, `hard-rules.md`, `roadmap.md`)

**Hinweis:** Die Inhalte von `radagast-activation.md` und `review-rubric.md` werden später in Task 8 (Archetype-Templates) bzw. Task 9 (`hard-rules.md` neu schreiben) wieder eingespeist als Prosa. Vor Löschung kein extra Backup nötig — git-Historie ist Archiv.

- [ ] **Step 1: Existenz prüfen**

```bash
ls skills/crazy-professor/references/
```

Erwartet: 7 Files: `chat-mode-flow.md`, `hard-rules.md`, `operating-instructions.md`, `radagast-activation.md`, `review-rubric.md`, `roadmap.md`, `usage-patterns.md`.

- [ ] **Step 2: 4 Files löschen**

```bash
git rm skills/crazy-professor/references/chat-mode-flow.md
git rm skills/crazy-professor/references/radagast-activation.md
git rm skills/crazy-professor/references/review-rubric.md
git rm skills/crazy-professor/references/usage-patterns.md
```

- [ ] **Step 3: Verifizieren**

```bash
ls skills/crazy-professor/references/
```

Erwartet: nur noch `hard-rules.md`, `operating-instructions.md`, `roadmap.md`.

- [ ] **Step 4: Commit**

```bash
git commit -m "$(cat <<'EOF'
crazy-professor | rueckbau 6/10 — 4 Reference-Files gelöscht

chat-mode-flow.md (Stub, Inhalt lebt in docs/chat-mode-flow.md),
radagast-activation.md (binding conditions wandern in
radagast-brown.md Prosa, kommt in Task 8), review-rubric.md
(3-Achsen-Rubrik wandert in hard-rules.md, kommt in Task 9),
usage-patterns.md (Doppel von docs/USAGE-PATTERNS.md, beide raus).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: picker.py schlanker machen — Force-Flags + wishful-share raus

**Files:**
- Modify: `skills/crazy-professor/scripts/picker.py`

**Änderungs-Kontext:** Aktuell hat das Picker-Skript:
- `--force-archetype`, `--force-word`, `--force-operator` (waren für Browser-Roundtrip)
- `--force-timestamp` (war für Tests, bleibt — der Smoke-Test braucht's nicht aber das Skript ist legitime Test-Mechanik)
- `--wishful-share` (war Phase-6-Mechanik mit dynamischen Operator-Gewichten)
- `pick_operator_with_share()` Funktion mit komplexer wishful-share-Logik

**Ziel-Verhalten nach Edit:** Picker zieht aus 4 Operatoren gleichverteilt mit `random.choices` (Microseconds-Seed). `--force-*`-Flags entfernt. `--force-timestamp` bleibt. `--init-template` bleibt.

- [ ] **Step 1: Aktuellen Stand zeigen**

```bash
wc -l skills/crazy-professor/scripts/picker.py
grep -n "force_" skills/crazy-professor/scripts/picker.py | head -20
grep -n "wishful" skills/crazy-professor/scripts/picker.py | head -20
```

Erwartet: ~314 Zeilen, mehrere `force_*`-Vorkommnisse, mehrere `wishful*`-Vorkommnisse.

- [ ] **Step 2: Picker-Skript komplett neu schreiben**

Schreibe die Datei `skills/crazy-professor/scripts/picker.py` mit folgendem Inhalt komplett neu (nicht inkrementell editieren — die Edit-Stellen sind über die ganze Datei verteilt und ein vollständiger Re-Write ist sicherer):

```python
#!/usr/bin/env python3
"""
crazy-professor picker — deterministic stochastic element selection.

Reads field-notes.md (last 10 Log table rows), applies anti-streak guards,
emits one JSON object on stdout per invocation.

Usage:
    picker.py --field-notes <path> --words <path> --retired <path> [options]

Modes:
    --mode single         (default) one archetype/word/operator pick
    --mode chat           four parallel picks (one per archetype)

Options:
    --init-template <path>    if field-notes file is missing, copy this template there first
    --force-timestamp <iso>   override UTC timestamp (testing only)

Exit codes:
    0  success — JSON written to stdout
    1  usage error / unreadable input
    2  empty word pool (all words filtered by retired list)

Fallback if Python is unavailable (prose mechanic for SKILL.md):
    archetype = ARCHETYPES[utc_minute % 4]
    operator  = OPERATORS[utc_second % 4]
    word      = random pick from active pool minus retired
    Then apply variation_guard manually:
        if last 3 archetypes == this archetype: pick the least-recently-seen of the others
        if word in last 10 rows' words: pick another word not in that window
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path

ARCHETYPES = (
    "first-principles-jester",
    "labyrinth-librarian",
    "systems-alchemist",
    "radagast-brown",
)
OPERATORS = ("reversal", "exaggeration", "escape", "wishful-thinking")
LOG_TABLE_HEADER_RE = re.compile(r"^\|\s*#\s*\|\s*Timestamp", re.IGNORECASE)
LOG_TABLE_ROW_RE = re.compile(r"^\|\s*\d+\s*\|")


def read_word_pool(words_path: Path, retired_path: Path) -> list[str]:
    """Return active provocation words (pool minus retired)."""
    pool = [
        line.strip()
        for line in words_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    retired: set[str] = set()
    if retired_path.exists():
        retired = {
            line.strip()
            for line in retired_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        }
    return [w for w in pool if w not in retired]


def read_last_log_rows(field_notes: Path, n: int = 10) -> list[dict]:
    """Parse the last n rows of the Log table into dicts. Empty list if no table."""
    if not field_notes.exists():
        return []
    text = field_notes.read_text(encoding="utf-8")
    in_log = False
    rows: list[list[str]] = []
    for line in text.splitlines():
        if not in_log and LOG_TABLE_HEADER_RE.match(line):
            in_log = True
            continue
        if in_log and LOG_TABLE_ROW_RE.match(line):
            cells = [c.strip() for c in line.strip("|").split("|")]
            rows.append(cells)
        elif in_log and line.startswith("##"):
            break
    columns = ("num", "timestamp", "archetype", "word", "operator", "slug",
               "output", "re_rolled", "kept", "retire", "voice_off", "votum")
    parsed = []
    for row in rows[-n:]:
        cells = (row + [""] * len(columns))[: len(columns)]
        parsed.append(dict(zip(columns, cells)))
    return parsed


def normalize_archetype(raw: str) -> str:
    """Strip suffixes like ' (forced)' and 'all-4 (chat-mode)' wrappers."""
    raw = raw.split(" (")[0].strip()
    return raw


def picker_seed(ts: dt.datetime, offset_seconds: int = 0) -> tuple[str, str, str]:
    """Deterministic mod-based picker for archetype/operator (and timestamp ISO).

    Archetype: minute mod 4
    Operator:  second mod 4 (gleichverteilt über 4 Operatoren since v0.13.0)
    """
    seed_ts = ts + dt.timedelta(seconds=offset_seconds)
    archetype = ARCHETYPES[seed_ts.minute % 4]
    operator = OPERATORS[seed_ts.second % 4]
    return archetype, operator, seed_ts.isoformat().replace("+00:00", "Z")


def variation_guard(
    archetype: str,
    word: str,
    last_rows: list[dict],
    available_words: list[str],
    seed_ts: dt.datetime,
) -> tuple[str, str, str]:
    """Apply anti-streak rules. Returns (archetype, word, re_rolled)."""
    re_rolled = "no"
    last_archetypes = [normalize_archetype(r["archetype"]) for r in last_rows]
    if last_archetypes[-3:] == [archetype] * 3 and len(last_archetypes) >= 3:
        candidates = [a for a in ARCHETYPES if a != archetype]
        seen_recency = {a: -1 for a in candidates}
        for i, prev in enumerate(reversed(last_archetypes)):
            if prev in seen_recency and seen_recency[prev] == -1:
                seen_recency[prev] = i
        candidates.sort(key=lambda a: (seen_recency[a] if seen_recency[a] >= 0 else 1e9, a))
        archetype = candidates[0]
        re_rolled = "archetype"

    last_words = {r["word"].split(" (")[0] for r in last_rows}
    if word in last_words:
        remaining = [w for w in available_words if w not in last_words and w != word]
        if remaining:
            idx = (seed_ts.microsecond + len(last_rows)) % len(remaining)
            word = remaining[idx]
            re_rolled = "both" if re_rolled == "archetype" else "word"
        # else: pool exhausted, accept original word; re_rolled stays as-is

    return archetype, word, re_rolled


def pick_word(available_words: list[str], seed_ts: dt.datetime, offset: int = 0) -> str:
    """Deterministic word pick from microseconds + offset."""
    idx = (seed_ts.microsecond + offset) % len(available_words)
    return available_words[idx]


def pick_single(words: list[str], rows: list[dict], ts: dt.datetime) -> dict:
    archetype, operator, ts_iso = picker_seed(ts)
    word = pick_word(words, ts)
    archetype, word, re_rolled = variation_guard(archetype, word, rows, words, ts)
    return {
        "timestamp": ts_iso,
        "mode": "single",
        "archetype": archetype,
        "word": word,
        "operator": operator,
        "re_rolled": re_rolled,
        "field_notes_rows_read": len(rows),
    }


def pick_chat(words: list[str], rows: list[dict], ts: dt.datetime) -> dict:
    """Four picks, one per archetype. Word-guard runs across the chat-run."""
    chat_rolled = []
    chat_words: set[str] = set()
    picks = []
    for i, archetype in enumerate(ARCHETYPES):
        offset = i  # one second per archetype to vary operator pick
        _, operator, _ = picker_seed(ts, offset_seconds=offset)
        word = pick_word(words, ts, offset=i * 7)  # spread word picks
        intra_chat = "no"
        if word in chat_words:
            for candidate in words:
                if candidate not in chat_words:
                    word = candidate
                    intra_chat = "intra-chat"
                    break
        chat_words.add(word)
        archetype_kept, word_kept, re_rolled = variation_guard(
            archetype, word, rows, [w for w in words if w not in chat_words or w == word], ts
        )
        # In chat we never re-roll the archetype itself (one of each)
        archetype_kept = archetype
        if re_rolled == "archetype":
            re_rolled = "no"
        elif re_rolled == "both":
            re_rolled = "word"
        if intra_chat == "intra-chat":
            re_rolled = "intra-chat" if re_rolled == "no" else f"{re_rolled}+intra-chat"
        picks.append({
            "archetype": archetype_kept,
            "word": word_kept,
            "operator": operator,
            "re_rolled": re_rolled,
        })
        chat_rolled.append(re_rolled)
    aggregate = "no" if all(r == "no" for r in chat_rolled) else "/".join(chat_rolled)
    return {
        "timestamp": ts.isoformat().replace("+00:00", "Z"),
        "mode": "chat",
        "picks": picks,
        "re_rolled_aggregate": aggregate,
        "field_notes_rows_read": len(rows),
    }


def main() -> int:
    p = argparse.ArgumentParser(description="crazy-professor picker")
    p.add_argument("--field-notes", required=True, type=Path)
    p.add_argument("--words", required=True, type=Path)
    p.add_argument("--retired", required=True, type=Path)
    p.add_argument("--mode", choices=("single", "chat"), default="single")
    p.add_argument("--init-template", type=Path,
                   help="copy this file to --field-notes if missing")
    p.add_argument("--force-timestamp", help="ISO-8601 UTC override (testing)")
    args = p.parse_args()

    # Initialization
    if not args.field_notes.exists():
        if args.init_template and args.init_template.exists():
            args.field_notes.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(args.init_template, args.field_notes)
        else:
            args.field_notes.parent.mkdir(parents=True, exist_ok=True)
            args.field_notes.write_text(
                "# Crazy Professor -- Field Notes\n\n## Log\n\n"
                "| # | Timestamp | Archetype | Word | Operator | Topic slug | Output file | "
                "Re-rolled | Kept | Retire-word | Voice-off | Review1-Votum |\n"
                "|---|-----------|-----------|------|----------|------------|"
                "-------------|-----------|------|-------------|-----------|---------------|\n",
                encoding="utf-8",
            )

    if args.force_timestamp:
        ts = dt.datetime.fromisoformat(args.force_timestamp.replace("Z", "+00:00"))
    else:
        ts = dt.datetime.now(dt.timezone.utc)

    words = read_word_pool(args.words, args.retired)
    if not words:
        print("error: empty word pool (all words filtered by retired list)", file=sys.stderr)
        return 2
    rows = read_last_log_rows(args.field_notes, n=10)

    if args.mode == "single":
        result = pick_single(words, rows, ts)
    else:
        result = pick_chat(words, rows, ts)

    json.dump(result, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Hinweise zur neuen Version:
- `BASE_OPERATORS`/`WISHFUL_OPERATOR`-Konstanten zusammengefasst zu `OPERATORS = (4 items)`.
- `pick_operator_with_share()` entfernt — Operator-Pick ist jetzt `OPERATORS[second % 4]` direkt in `picker_seed()`.
- `--force-archetype`, `--force-word`, `--force-operator` aus argparse entfernt.
- `--wishful-share` aus argparse entfernt.
- `--init-template`, `--force-timestamp` bleiben.
- `pick_single()` Signatur vereinfacht: nimmt jetzt nur `(words, rows, ts)` statt `(args, words, rows, ts)`.
- `pick_chat()` Signatur vereinfacht: kein `wishful_share`-Parameter mehr.
- Komplette `forced_markers`-Logik in `pick_single()` entfällt.
- Modul-Docstring um Fallback-Prosa-Mechanik (für SKILL.md operating-instructions Bezug) ergänzt.

- [ ] **Step 3: Picker-Smoke-Test (mit echtem field-notes)**

```bash
python skills/crazy-professor/scripts/picker.py \
  --field-notes ~/Desktop/.agent-memory/lab/crazy-professor/field-notes.md \
  --words skills/crazy-professor/resources/provocation-words.txt \
  --retired skills/crazy-professor/resources/retired-words.txt \
  --mode single
```

Erwartet: ein JSON-Objekt auf stdout mit Schlüsseln: `timestamp`, `mode`, `archetype`, `word`, `operator`, `re_rolled`, `field_notes_rows_read`. `archetype` ist einer der 4. `operator` ist einer der 4 inkl. `wishful-thinking`. Exit-Code 0.

- [ ] **Step 4: Chat-Mode-Smoke-Test**

```bash
python skills/crazy-professor/scripts/picker.py \
  --field-notes ~/Desktop/.agent-memory/lab/crazy-professor/field-notes.md \
  --words skills/crazy-professor/resources/provocation-words.txt \
  --retired skills/crazy-professor/resources/retired-words.txt \
  --mode chat
```

Erwartet: JSON mit `mode: "chat"`, `picks`-Array mit 4 Einträgen (je `archetype`/`word`/`operator`/`re_rolled`). Alle 4 archetypes erscheinen genau einmal.

- [ ] **Step 5: Verifizieren — Force-Flags raus**

```bash
python skills/crazy-professor/scripts/picker.py --help 2>&1 | grep -i force
```

Erwartet: nur `--force-timestamp` taucht auf, nicht `--force-archetype`/`--force-word`/`--force-operator`.

```bash
python skills/crazy-professor/scripts/picker.py --help 2>&1 | grep -i wishful
```

Erwartet: keine Ausgabe (kein `--wishful-share` mehr).

- [ ] **Step 6: Commit**

```bash
git add skills/crazy-professor/scripts/picker.py
git commit -m "$(cat <<'EOF'
crazy-professor | rueckbau 7/10 — picker.py schlanker

--force-archetype/--force-word/--force-operator entfernt (waren für
Browser-Playground-Roundtrip). --wishful-share entfernt (Phase-6-Dynamik).
4 PO-Operatoren bleiben gleichverteilt via second-mod-4. Skript schrumpft
von ~314 auf ~205 LOC.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Lexicon-Gate-YAML-Blöcke aus Archetype-Templates entfernen

**Files:**
- Modify: `skills/crazy-professor/prompt-templates/first-principles-jester.md` (entferne YAML-Block am Ende)
- Modify: `skills/crazy-professor/prompt-templates/labyrinth-librarian.md` (entferne YAML-Block am Ende)
- Modify: `skills/crazy-professor/prompt-templates/systems-alchemist.md` (entferne YAML-Block am Ende)
- Modify: `skills/crazy-professor/prompt-templates/radagast-brown.md` (entferne YAML-Block am Ende; **Activation Amendments bleiben als Prosa**)

**Pattern in allen 4 Templates:** Am Dateiende steht ein Section-Header `## Lexicon-Gate (machine-readable, used by lint_voice.py)` gefolgt von einem ` ```yaml ... ``` `-Block. Dieser Block (inklusive Section-Header und einer evtl. davorstehenden Trenn-Linie `---`) ist zu entfernen.

**Wichtig zu radagast-brown.md:** Die Sections "Activation Amendments (2026-04-23, binding)" und ihre Unter-Punkte (1-5) bleiben erhalten — sie sind Prosa-Bullets und gehören gemäß Spec in das Template. Nur der `## Lexicon-Gate`-Block am Ende wird entfernt.

- [ ] **Step 1: Aktuelle Endezeilen aller 4 Templates inspizieren**

```bash
tail -30 skills/crazy-professor/prompt-templates/first-principles-jester.md
echo '---'
tail -30 skills/crazy-professor/prompt-templates/labyrinth-librarian.md
echo '---'
tail -30 skills/crazy-professor/prompt-templates/systems-alchemist.md
echo '---'
tail -30 skills/crazy-professor/prompt-templates/radagast-brown.md
```

Erwartet: alle 4 enden mit ` ```yaml ... ``` `-Block, vorausgegangen von ` ## Lexicon-Gate (machine-readable, used by lint_voice.py) `.

- [ ] **Step 2: first-principles-jester.md edit**

Identifiziere im File die Zeile mit `## Lexicon-Gate (machine-readable, used by lint_voice.py)`. Alles ab dieser Zeile (inklusive) bis Dateiende muss entfernt werden. Falls direkt davor eine Trenn-Linie `---` steht (auf eigener Zeile, nur drei Bindestriche), die entfernt sich auch.

Im first-principles-jester.md ist die zu entfernende Section laut Read-Output: ab Zeile 73 (`---`) bis Zeile 110 (Ende). Verwende den Edit-Tool mit `old_string` = der gesamte Block (Zeilen 73-110), `new_string` = leer.

Konkret zu entfernender Block (verbatim from current file):
```
---

## Lexicon-Gate (machine-readable, used by lint_voice.py)

```yaml
archetype: first-principles-jester
# Required: at least N of these tokens must appear in each provocation
# (case-insensitive substring match, so "verboten" matches "Wiederholungs-
# verbot"). The jester has a 3-part structure (Zerlegung, Illegalisierung,
# Re-Kombination), so we require markers from each part.
required:
  - warum
  - verboten
  - darf nicht
  - waere wenn
  - was waere
  - besteht aus
  - zerleg
  - illegal
required_min_per_provocation: 2
# Forbidden: never appear anywhere in the output (these belong to other
# archetypes). Match is case-insensitive substring.
forbidden:
  - in der mykologie
  - in der biologie
  - in der meteorologie
  - in der chemie
  - pilzmyzel
  - katalysator
  - membran
  - reststoff
  - ueberlauf
  - flussdiagramm
  - unterholz
  - winterruhe
  - mondphase
  - daemmerung
` ` `
```

(Die letzte Zeile ist drei Backticks — `\`\`\``-Trenner. In dieser Plan-Datei zur Vermeidung von Markdown-Verschachtelung escaped als `` ` ` ` ``.)

- [ ] **Step 3: labyrinth-librarian.md edit**

Analoge Operation. Block ab `## Lexicon-Gate`-Zeile bis Dateiende entfernen, plus vorausgehende `---`-Trenn-Linie. Die exakten Zeilen sind im Read-Output zu sehen — Zeile 81 (`---`) bis Zeile 134 (Ende).

- [ ] **Step 4: systems-alchemist.md edit**

Analoge Operation. Block ab `## Lexicon-Gate`-Zeile bis Dateiende entfernen, plus vorausgehende `---`-Trenn-Linie. Im Read-Output: Zeile 88 (`---`) bis Zeile 130 (Ende).

- [ ] **Step 5: radagast-brown.md edit**

**Achtung:** Bei radagast-brown.md gibt es ZWEI `---`-Trenn-Linien gegen Dateiende:
- Eine VOR den "Activation Amendments" — diese Trenn-Linie BLEIBT, weil die Activation Amendments bleiben.
- Eine VOR dem `## Lexicon-Gate`-Block — diese Trenn-Linie wird MIT entfernt.

Im Read-Output: der Lexicon-Gate-Block beginnt mit `---` auf Zeile 185 und geht bis Zeile 266 (Ende). Nur diese beiden Marker (Zeile 185 `---` + Zeile 187 `## Lexicon-Gate ...` + ` ```yaml ... ``` `-Block bis Ende) werden entfernt. Die Section "Activation Amendments (2026-04-23, binding)" mit ihren 5 Unterpunkten BLEIBT vollständig erhalten.

- [ ] **Step 6: Verifizieren — kein Lexicon-Gate mehr**

```bash
grep -l "Lexicon-Gate" skills/crazy-professor/prompt-templates/*.md
```

Erwartet: keine Ausgabe (kein File matched mehr).

```bash
grep -l "Activation Amendments" skills/crazy-professor/prompt-templates/*.md
```

Erwartet: nur `skills/crazy-professor/prompt-templates/radagast-brown.md`.

- [ ] **Step 7: Tail aller 4 Files prüfen**

```bash
tail -10 skills/crazy-professor/prompt-templates/first-principles-jester.md
echo '---'
tail -10 skills/crazy-professor/prompt-templates/labyrinth-librarian.md
echo '---'
tail -10 skills/crazy-professor/prompt-templates/systems-alchemist.md
echo '---'
tail -20 skills/crazy-professor/prompt-templates/radagast-brown.md
```

Erwartet: jester/librarian/alchemist enden mit Beispiel-Ton-Charakteristika (kein YAML mehr), radagast-brown endet mit dem letzten Activation-Amendment-Punkt 5 ("Repetition Watch") und seinen abschließenden Sätzen.

- [ ] **Step 8: Commit**

```bash
git add skills/crazy-professor/prompt-templates/
git commit -m "$(cat <<'EOF'
crazy-professor | rueckbau 8/10 — Lexicon-Gate-YAML-Blöcke entfernt

4 Lexicon-Gate-YAML-Blöcke am Ende der Archetype-Templates entfernt
(waren ausschließlich von lint_voice.py gelesen worden — Skript wurde
in Task 3 entfernt). Verbotenes Vokabular bleibt als Prosa-Bullet im
"Verbotenes Vokabular"-Block der jeweiligen System-Prompt-Kerne.

radagast-brown.md "Activation Amendments"-Section bleibt unverändert
(binding conditions als Prosa-Bullets, ersetzt das gelöschte
references/radagast-activation.md aus Task 6).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: SKILL.md, commands/crazy.md, operating-instructions.md, hard-rules.md neu schreiben

Das ist der Kern-Commit. 4 Files werden komplett neu geschrieben — von 273+30+494+106 = 903 Zeilen auf ungefähr 120+12+80+80 = 292 Zeilen.

**Files:**
- Modify (rewrite): `skills/crazy-professor/SKILL.md`
- Modify (rewrite): `commands/crazy.md`
- Modify (rewrite): `skills/crazy-professor/references/operating-instructions.md`
- Modify (rewrite): `skills/crazy-professor/references/hard-rules.md`
- Modify (touch): `skills/crazy-professor/references/roadmap.md` (kürzen, kein Phase 8 mehr)

- [ ] **Step 1: commands/crazy.md neu schreiben**

Schreibe `commands/crazy.md` mit folgendem Inhalt (~14 Zeilen):

```markdown
---
description: Invoke the crazy-professor divergence generator on a topic. Default: 10 provocations. With --chat: all four voices and 20 distilled ideas. --lab: open the static review browser.
argument-hint: [topic] [--chat] [--lab]
---

# Crazy Professor -- On-Demand

Activate the `crazy-professor` skill and run it against the following arguments:

**Arguments:** $ARGUMENTS

Topic resolution (single source of truth — the SKILL.md operating-instructions reference is the canonical version):

- If `$ARGUMENTS` contains `--lab`, open the static Ideation Lab at `skills/crazy-professor/lab/index.html` via `webbrowser.open()`. Standalone — no topic, no `--chat`.
- If `$ARGUMENTS` contains `--chat` and no topic text outside the flag, **reject explicitly** and stop. Return: `Chat-mode requires an explicit topic. Run /crazy <topic> --chat or use single-run for ambient topics.`
- If `$ARGUMENTS` is empty (no `--chat`, no `--lab`, no topic), run single-run on the most recent concrete task, plan, or problem from the current conversation. If the conversation context is empty, meta, or too vague, ask one clarifying question and stop.
- If `$ARGUMENTS` contains a topic and no `--chat`, dispatch to single-run mode: one active archetype, one provocation word, one PO operator, exactly 10 provocations, and one next experiment.
- If `$ARGUMENTS` contains a topic and `--chat`, dispatch to Chat-Mode: all four active archetypes, 3 rounds, final 20-idea distillation.

Follow the skill's full protocol exactly. All four archetypes are active: first-principles-jester, labyrinth-librarian, systems-alchemist, radagast-brown. No advice, no softening. Strange but anchored.
```

- [ ] **Step 2: skills/crazy-professor/references/hard-rules.md neu schreiben**

Schreibe `skills/crazy-professor/references/hard-rules.md` mit folgendem Inhalt (~80 Zeilen):

```markdown
---
title: crazy-professor — Hard Rules
status: v0.13.0 (Phase 4-8 zurückgebaut, Inhalte konsolidiert)
load_when: any invocation, before generation
path_convention: all paths are relative to plugin repo root <repo-root> = crazy-professor/
---

# Hard Rules

These rules override helpfulness-tuning. Persona prompting without
guardrails can degrade factual accuracy by up to 30 percentage points
on knowledge-heavy tasks (Search Engine Journal, 2024). The skill is a
divergence tool, not an advisor.

1. **Output is never advice.** Every provocation is framed as
   hypothesis, provocation, or "what if" — never as recommendation.
2. **The warning banner is always present.** The output template
   (`<repo-root>/skills/crazy-professor/resources/output-template.md`)
   includes the divergence warning verbatim.
3. **The goal of the topic is respected.** Conventions are attacked,
   goals are not.
4. **Anchor or it doesn't count.** Every provocation names at least
   one existing structure in the user's infrastructure. "Adapt this in
   agentic-os iterations.jsonl" beats "adapt this somehow."
5. **Exactly one concrete next experiment.** The final section names
   ONE of the 10 provocations as testable in the next hour and nothing
   more. This is the anti-adoption safety mechanism.
6. **No cross-archetype contamination.** Each archetype has a
   verbotenes Vokabular block in its prompt template. Honor those bans
   as prose rules — there is no automated linter as of v0.13.0.

## Museum Clause (hard gate)

After the **10th invocation**, check field-notes.md. If fewer than 3
invocations produced an output that the user flagged as "kept" (landed
in `wiki/inbox/`, ISSUES2FIX, or .agent-memory/skills-backlog/ within
14 days), the skill is moved to `.agent-memory/museum/crazy-professor/`
with a short post-mortem noting what was learned. The gap in the
pipeline stays visible rather than being papered over with a bad tool.

**Adoption is the risk, not build.** The skill earns its continued
existence through use, not through existence.

## Chat-Mode Museum Clause

Chat-mode has its own 5-run museum gate, independent of the V1 gate:

- After 5 chat-runs: user review.
- Pass: ≥ 3 of 5 chat-runs produced final-20 lists where ≥ 10 ideas
  are `kept` or `conditional` under the rubric.
- Fail: 3+ chat-runs broke structurally (format errors, codex failure,
  5-per-archetype rule violated) OR produced < 10 viable ideas per
  run on average. Chat-mode moves to
  `.agent-memory/museum/crazy-professor-chat/`, single-run remains
  active.

## Field Test Rule (living artifact)

After a provocation word has produced output in **3 invocations** and
in all 3 cases the user flagged the result as "too close to variations
of previous outputs" (in field-notes.md, in a column marked "retire?"),
the word is moved from
`<repo-root>/skills/crazy-professor/resources/provocation-words.txt`
to `<repo-root>/skills/crazy-professor/resources/retired-words.txt`.
This keeps the word pool alive rather than frozen.

The list of archetypes is NOT subject to the same rule; archetype
changes require a version bump.

## Radagast-Activation Status

`radagast-brown` is **ACTIVE** since 2026-04-23. mod-4 is live; all
four archetypes participate at equal 25% probability.

The four binding conditions for Radagast outputs (first-sentence
vocabulary rule, no foreign-field smuggling, optimization-under-care
flagging, anti-folder-sprawl limit) live as the "Activation
Amendments" prose section at the bottom of
`<repo-root>/skills/crazy-professor/prompt-templates/radagast-brown.md`.

## Review Rubric

All reviews use three criteria:

- **Wert (Value)** — Does the provocation open a genuinely new
  working mode, or is it a near-variation of something already present?
- **Umsetzbarkeit (Feasibility)** — Testable in under 1-2 hours, or
  materializable as a small backlog artefact? The Adoption-Cost-Tag
  (`low` / `medium` / `high` / `system-break`) is the first signal,
  but the rubric overrides the tag.
- **Systemfit** — Fits into Agentic-OS / Claude / Codex / Wiki workflow
  without architectural theater?

**Verdict levels:** `kept` (durable value), `conditional` (kept iff a
named artefact materializes within deadline), `backlog` (strong concept
but too heavy for immediate adoption).

**Special rule for labyrinth-librarian:** Do not evaluate the
historical/scientific analogies as facts. Only the transferred
mechanism is rated. An analogy that turns out to be fictional is not a
mark against the provocation if the mechanism translates cleanly.

The old per-output `kept` checkbox in the output template remains for
museum-clause mechanics (14-day artefact-materialization tracking).
The verdict above is run-level.
```

- [ ] **Step 3: skills/crazy-professor/references/operating-instructions.md neu schreiben**

Schreibe `skills/crazy-professor/references/operating-instructions.md` mit folgendem Inhalt (~85 Zeilen):

```markdown
---
title: crazy-professor — Operating Instructions
status: v0.13.0 (Phase 4-8 zurückgebaut)
load_when: any invocation, after parsing the trigger
path_convention: all paths are relative to plugin repo root <repo-root> = crazy-professor/
---

# Operating Instructions

Claude follows these steps on every invocation. Steps 1-5 cover the
default single-run path; Steps C1-C6 cover Chat-Mode (`--chat`); Step
L1 covers `--lab`. All file paths are relative to the plugin repo root
(`<repo-root>` = `crazy-professor/`).

## Single-Run Path

**Step 1: Parse the topic.** Strip to a single sentence.

- If `$ARGUMENTS` contains `--lab`: jump to Step L1 (no topic parsing,
  no generation).
- **Single-run with topic:** proceed.
- **Single-run without topic:** use the most recent concrete task,
  plan, or problem from the current conversation as topic. If the
  conversation context is empty, meta, or too vague ("tell me a
  story", "how does this skill work"), ask one clarifying question
  and stop — do not fabricate a topic.
- **Chat-mode with topic:** proceed (jump to Step C1).
- **Chat-mode without topic** (`--chat` flag but no topic text):
  reject explicitly. Return:
  `Chat-mode requires an explicit topic. Run /crazy <topic> --chat or use single-run for ambient topics.`

**Step 2: Pick stochastic elements (picker call).**

```bash
python <repo-root>/skills/crazy-professor/scripts/picker.py \
  --field-notes <target-project>/.agent-memory/lab/crazy-professor/field-notes.md \
  --words <repo-root>/skills/crazy-professor/resources/provocation-words.txt \
  --retired <repo-root>/skills/crazy-professor/resources/retired-words.txt \
  --mode single
```

Parses one JSON object from stdout: `archetype`, `word`, `operator`,
`re_rolled`, `timestamp`. The variation-guard (3-archetype-streak
re-roll, 10-row word-window dedup) is applied inside the script.

If Python is unavailable, use the prose fallback documented in the
`picker.py` module docstring: `archetype = ARCHETYPES[utc_minute % 4]`,
`operator = OPERATORS[utc_second % 4]`, random word from the active
pool minus retired, then variation-guard manually.

**Step 3: Load the archetype's prompt template.** Read the matching
`<repo-root>/skills/crazy-professor/prompt-templates/<archetype>.md`
file. Its System-Prompt-Kern is the authoritative voice rules.

**Step 4: Generate 10 provocations.** Follow the archetype rules
strictly. Each provocation carries an Adoption-Cost-Tag (`low` |
`medium` | `high` | `system-break`) and a one-phrase anchor. Format
per line:

`<provocation text> -- [cost: <level>] -- anchor: <link>`

The cost tag is honest per provocation. No forced distribution. Pick
ONE of the 10 as the next experiment — the one most testable in under
one hour with tools the user already has.

Write the output file using the frontmatter and body structure
defined in
`<repo-root>/skills/crazy-professor/resources/output-template.md`,
to path
`<target-project>/.agent-memory/lab/crazy-professor/YYYY-MM-DD-HHMM-<topic-slug>.md`.
Create the directory if it does not exist.

**Step 5: Append a row to field-notes.md.** One Markdown table row in
`<target-project>/.agent-memory/lab/crazy-professor/field-notes.md`
matching the existing table columns (see
`<repo-root>/skills/crazy-professor/resources/field-notes-schema.md`).
At minimum: timestamp, archetype, word, operator, topic slug, output
filename, `re-rolled` value. Default review columns to `pending`.

## Chat-Mode Path (`--chat`)

**Step C1: Parse arguments.** Topic mandatory; reject `--chat` without
topic per Step 1 rule. Optional `--chat --dry-run-round1` runs only
round 1 (internal testing, no round 2/3).

**Step C2: Generate 4 picker calls.**

```bash
python <repo-root>/skills/crazy-professor/scripts/picker.py \
  --field-notes <target-project>/.agent-memory/lab/crazy-professor/field-notes.md \
  --words <repo-root>/skills/crazy-professor/resources/provocation-words.txt \
  --retired <repo-root>/skills/crazy-professor/resources/retired-words.txt \
  --mode chat
```

Returns 4 picks (one per archetype) in a single JSON object. Word-guard
runs intra-chat (no duplicate word within the chat-run; if duplicate,
re-roll with marker `re-rolled: intra-chat`).

**Step C3: Round 1 — 4 parallel LLM calls.** Each archetype with its
standard prompt template + `chat-round-1-wrapper.md` override block.
User message: topic + word + operator. Each archetype returns 5
provocations. Collect all 20.

If ≥2 of 4 archetypes return empty/format-broken output, abort
chat-mode and fall back to a single-run with a note in the output file
that chat-mode failed in round 1.

**Step C4: Round 2 — 4 parallel LLM calls.** Each archetype with its
standard prompt template + `chat-round-2-wrapper.md` override block.
User message: topic + the 15 provocations from the OTHER three
archetypes' round 1. Each archetype returns 2-3 provocations with
`counter:`/`extend:` markers.

Degradation: If ≥2 of 4 archetypes return fewer than 2 provocations,
set `round2_status: degraded` in the frontmatter, skip round-2 outputs
entirely, and pass only round-1 data to round 3. NOT an abort.

**Step C5: Round 3 — Codex distillation.** Invoke `codex:codex-rescue`
subagent with `chat-curator.md` prompt. Direct Markdown return: no
scratch file, no path-only response. Output must have exactly 4
sections × 5 ideas, a Top-3 Cross-Pollination block, and a Next
Experiment block.

If Codex fails (timeout/error/rate-limit) or returns broken structure
after one retry: run the identical distillation prompt through Claude
self-call. Mark `distiller: claude (codex-fallback)` in frontmatter
plus a `distiller_reason`.

**Step C6: Write output + append field-notes row.** Output to
`<target-project>/.agent-memory/lab/crazy-professor/chat/YYYY-MM-DD-HHMM-<topic-slug>.md`
using `chat-output-template.md`. Field-notes row marks `mode: chat`,
`archetype: all-4`, `word: multi`, `operator: multi`. Brief
user-facing summary: topic + 4 picks + round-2 status + distiller +
output-file pointer. Do NOT repeat the 20 final ideas in the chat —
the user reads them in the file.

## Lab Path (`--lab`, standalone)

**Step L1: Open the static lab.** Verify
`<repo-root>/skills/crazy-professor/lab/index.html` exists. Open it
via Python `webbrowser.open(...)`. Fallback if that fails: print
`Open this file manually: file://<absolute-path>`. No LLM call, no
file write, no field-notes row, no telemetry. Done.

The lab is paste-only: the user pastes an existing crazy-professor
output, scores ideas, copies one experiment card. Browser-side
JavaScript only.
```

- [ ] **Step 4: skills/crazy-professor/SKILL.md neu schreiben**

Schreibe `skills/crazy-professor/SKILL.md` mit folgendem Inhalt (~125 Zeilen):

```markdown
---
name: crazy-professor
description: >
  Divergence generator. Produces 10 unhinged provocations for any topic
  using random archetype + random provocation word + random PO operator
  (De Bono's Provocation Operation). Four voices: first-principles-jester,
  labyrinth-librarian, systems-alchemist, radagast-brown (a warm, forest-
  dwelling caretaker archetype that asks what needs shelter rather than
  optimization). Output is never advice, always a deliberately strange
  nudge away from the obvious. Use when feeling stuck, when the first
  idea feels too normal, when a feature needs a weirder starting point,
  when a brainstorm needs a destabilizer, or when a plan feels like it
  converged too fast. Trigger phrases: "crazy professor", "provoke me",
  "break my thinking", "give me weird ideas", "divergence", "shake this
  up", "destabilize", "unstick me", "too normal", "weirder starting
  point", "unhinged thinker", "nudge away from obvious", "radagast",
  "radagast der braune", "cozy provocation", "gentler nudge", "waldhaft".
  Chat-Mode (`--chat` flag, since v0.5.0): four archetypes in 3-round
  distilled dialog producing curated 20-idea output (5 per archetype)
  with Codex-based scoring. Lab (`--lab` flag, since v0.13.0): opens a
  static review browser for triaging existing outputs.
metadata:
  author: domes
  version: '0.13.0'
  part-of: crazy-professor
  layer: divergence
  status: V1 + Chat-Mode + Lab (Phase 4-8 rolled back)
  user_invocable: true
---

# Crazy Professor

Divergence generator for creative ideation. Not an advisor. Not a
coach. A deliberately unhinged thinker whose only job is to produce
strange but anchored provocations the user would not have reached on
their own.

## German Trigger Phrases (body-level, not in frontmatter)

The plugin catalog enforces English trigger phrases in YAML
frontmatter. The user works primarily in German. The following German
phrases should also activate this skill:

"verrueckter professor", "professor", "spinn herum", "bring mich raus
aus der spur", "gib mir wilde ideen", "steck mich fest", "ideen
ausbrechen", "wilde provokationen", "das ist zu normal", "brauche was
verdrehtes", "zu gerade gedacht", "stoss mich an".

## Modes

| Trigger | Mode | Output |
|---|---|---|
| `/crazy <topic>` | Single-Run (default, ~30s, 1 LLM call) | 10 provocations + 1 next experiment |
| `/crazy <topic> --chat` | Chat-Mode (~2-4 min, ~10 LLM calls + Codex) | 4×5 distilled ideas + Top-3 + 1 next experiment |
| `/crazy --lab` | Lab (browser-only, no LLM) | Static review surface for an existing output |

The full step-by-step (Steps 1-5 single, C1-C6 chat, L1 lab, plus the
topic-resolution contract) lives in
`<repo-root>/skills/crazy-professor/references/operating-instructions.md`.
Load that file before generating any output.

## Hard Rules (load on every invocation)

The full Hard Rules block (output-is-never-advice, warning-banner,
goal-respect, anchor-or-it-doesnt-count, exactly-one-experiment,
no-cross-archetype-contamination), plus Museum-Clause, Chat-Mode
Museum-Clause, Field-Test-Rule, Radagast-Activation status, and Review
Rubric, lives in
`<repo-root>/skills/crazy-professor/references/hard-rules.md`. Load
that file before generating any output.

## Archetypes (V1)

| Archetype | Purpose | Voice |
|---|---|---|
| `first-principles-jester` | Illegalizes conventions. Breaks down a habit into atoms, declares one atom illegal, rebuilds. | Naive, playful, never cynical. |
| `labyrinth-librarian` | Imports mechanisms from distant fields. Opens in mykology/meteorology/ornithology/architecture, translates the mechanism back. | Quiet, learned, never pedantic. |
| `systems-alchemist` | Rewires flows. Maps the topic as input/output/overflow/leak/wall and re-routes one element. | Precise, observational, like a process engineer drawing a flow diagram. |
| `radagast-brown` | Protects the useful-uselessness. Asks what needs care, shelter, slowness — defends a part of the system against optimization. | Softly distracted but never dumb. Speaks in living creatures and natural time. |

See the four files in
`<repo-root>/skills/crazy-professor/prompt-templates/` for full voice
rules and verbotenes Vokabular per archetype. The `radagast-brown.md`
template additionally carries the Activation Amendments (binding
conditions for Radagast outputs since 2026-04-23).

## Helper Script

Single Python helper, stdlib-only:

- `picker.py` — deterministic stochastic-element selection with
  built-in variation-guard. Reads `field-notes.md`, the active word
  pool, and the retired list. Writes JSON to stdout. Modes: `--mode
  single` (default), `--mode chat`. The skill's only required external
  call. If Python is unavailable, prose fallback in
  `operating-instructions.md` Step 2.

## Path Convention

All file paths in this SKILL.md, in `references/`, and in
`commands/crazy.md` are written relative to the plugin repo root
(`<repo-root>` = `crazy-professor/`). This makes them resolvable
regardless of which file the reader is currently in.

## File Layout

```
crazy-professor/                              (repo root = plugin root)
|-- .claude-plugin/
|   |-- marketplace.json
|   \-- plugin.json
|-- commands/
|   \-- crazy.md                              (/crazy slash command)
|-- docs/
|   |-- PROJECT.md, CAPABILITIES.md, ARCHITECTURE.md, CHANGELOG.md
|   |-- chat-mode-flow.md                     (canonical flow spec)
|   |-- VERSIONING.md
|   |-- plans/                                (master plans + historical phase plans)
|   \-- specs/                                (active specs only)
\-- skills/
    \-- crazy-professor/
        |-- SKILL.md                          (this file, ~125 lines)
        |-- prompt-templates/
        |   |-- first-principles-jester.md
        |   |-- labyrinth-librarian.md
        |   |-- systems-alchemist.md
        |   |-- radagast-brown.md             (with Activation Amendments)
        |   |-- chat-round-1-wrapper.md
        |   |-- chat-round-2-wrapper.md
        |   \-- chat-curator.md
        |-- references/                       (load-on-demand)
        |   |-- operating-instructions.md     (Steps 1-5, C1-C6, L1)
        |   |-- hard-rules.md
        |   \-- roadmap.md
        |-- resources/
        |   |-- provocation-words.txt
        |   |-- retired-words.txt
        |   |-- po-operators.md
        |   |-- field-notes-schema.md
        |   |-- output-template.md
        |   \-- chat-output-template.md
        |-- lab/
        |   \-- index.html                    (static review surface, browser-only)
        \-- scripts/
            \-- picker.py                     (the only helper script)
```

## Output Target

Single + Chat outputs land in the **target project's** `.agent-memory/`
(not the plugin repo):

```
.agent-memory/lab/crazy-professor/
|-- field-notes.md                            (one line per run, single+chat mixed)
|-- YYYY-MM-DD-HHMM-<topic-slug>.md           (single-run output)
\-- chat/
    \-- YYYY-MM-DD-HHMM-<topic-slug>.md       (chat-mode output)
```

## What Was Removed in v0.13.0

The Phase 4-8 subsystems (telemetry, patch-suggester, run-planner,
voice/word-pool/cross-pollination linters, eval-suite, telegram
dialogue scaffold, browser playground, ideation-lab v2 design) were
rolled back on 2026-05-02. Reason: 18 runs total, 0 telemetry records,
0 patch suggestions, 0 telegram dialogues — Phase 4-8 was built before
Phase 1-3 produced a data stream that could justify it. See
`<repo-root>/docs/CHANGELOG.md` v0.13.0 entry.

If something from those subsystems is later needed: git history is
the archive (`git show <commit>:<path>` to retrieve).
```

- [ ] **Step 5: skills/crazy-professor/references/roadmap.md kürzen**

Aktueller Inhalt der `roadmap.md` enthält Phase 8 Telegram-Material. Vor dem Rewrite den File einmal lesen, um den genauen Stand zu sehen, dann die Phase-8-Telegram-Solution-Dialogue-Sektion und alles was auf gelöschte Skripte/Files verweist entfernen. Das Resultat soll ungefähr sein:

```markdown
# Roadmap & Out-of-Scope Design Intent

This file preserves design intent for deliberately-deferred features.
None of the items below are built. They are documented to prevent
ad-hoc reimplementation and to anchor decisions when a feature is
eventually reconsidered.

## V1.1 Candidates

- **stage-magician** archetype. Purpose: sensory/dramaturgic
  provocations using stage, prop, reveal, audience, timing. Originally
  tagged as the V1.1 sensory slot. **Parked in v0.3.0** because
  `radagast-brown` took the adjacent slot (biosphere/care axis)
  first; dramaturgic/sensory stays open if Radagast proves itself but
  a further distinct voice is still missing.

## V2 Extensions

- **`--deep` mode.** Calls `devil-advocate-swarms:swarm-orchestrator`
  on the V1 quick output to pressure-test the 10 provocations and
  cluster them into 3 fleshed-out outliers.
- ~~`--chat` mode~~ — shipped as v0.5.0, 2026-04-23. Synchronous flow
  (rounds 1-2 parallel calls, round 3 Codex distillation), ~10 LLM
  calls total. Canonical spec: `<repo-root>/docs/chat-mode-flow.md`.

## V3 Bridge

- **Telegram bridge.** Mobile trigger via ductor or Anthropic's
  external_plugins/telegram. Decision deferred. Security gate:
  full security-audit + codex:rescue security-review pass required
  before any Telegram adoption. The Phase-8 Telegram solution-dialogue
  scaffold from 2026-04-30 was rolled back in v0.13.0 on 2026-05-02
  (never used). When this is reconsidered, start fresh from the
  security-audit step.

## Rolled-Back in v0.13.0

The following Phase 4-8 subsystems were removed on 2026-05-02:
telemetry layer, patch-suggester loop, run-planner (`--from-session`,
`--dry-run`), voice/word-pool/cross-pollination linters, eval-suite,
browser playground (`--playground`), telegram-dialogue scaffold,
ideation-lab-v2 design. See `<repo-root>/docs/CHANGELOG.md` v0.13.0
entry. If any of these are needed again, retrieve from git history
rather than rebuilding from the spec files (the specs are also
deleted).
```

- [ ] **Step 6: Verify alle 5 Files**

```bash
wc -l commands/crazy.md skills/crazy-professor/SKILL.md \
       skills/crazy-professor/references/hard-rules.md \
       skills/crazy-professor/references/operating-instructions.md \
       skills/crazy-professor/references/roadmap.md
```

Erwartet: ungefähr 14 / 125 / 80 / 85 / 50 Zeilen.

```bash
grep -l "playground\|--from-session\|--dry-run\|--compact\|--strict-cross-pollination" \
  commands/crazy.md \
  skills/crazy-professor/SKILL.md \
  skills/crazy-professor/references/*.md 2>&1
```

Erwartet: keine Treffer (kein einziger Verweis auf entfernte Flags).

- [ ] **Step 7: Commit**

```bash
git add commands/crazy.md \
       skills/crazy-professor/SKILL.md \
       skills/crazy-professor/references/hard-rules.md \
       skills/crazy-professor/references/operating-instructions.md \
       skills/crazy-professor/references/roadmap.md
git commit -m "$(cat <<'EOF'
crazy-professor | rueckbau 9/10 — SKILL/Command/Refs neu geschrieben

SKILL.md von 273 auf ~125 Zeilen.
operating-instructions.md von 494 auf ~85 Zeilen.
hard-rules.md von 106 auf ~80 Zeilen (review-rubric Inhalt integriert).
commands/crazy.md von 30 auf ~14 Zeilen.
roadmap.md gekürzt — Phase-8-Detail raus, "Rolled-Back in v0.13.0"-Section.

User-Surface: /crazy <topic>, /crazy <topic> --chat, /crazy --lab.
Keine --playground/--from-session/--dry-run/--compact/--strict-cross-
pollination mehr.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: Doku + Versions-Bump

**Files:**
- Modify: `.claude-plugin/plugin.json` (version 0.12.0 → 0.13.0)
- Modify: `docs/PROJECT.md` (Aktueller Stand + Offene Baustellen)
- Modify: `docs/CAPABILITIES.md` (auf ~12-15 Zeilen kürzen)
- Modify: `docs/ARCHITECTURE.md` (Komponentendiagramm aktualisieren, gelöschte Komponenten raus)
- Modify: `docs/CHANGELOG.md` (v0.13.0 Eintrag voranstellen mit Lerngeschichte)
- Modify: `docs/chat-mode-flow.md` (`version: 0.12.0` → `version: 0.13.0` im Frontmatter; sonst unverändert)
- Modify: `README.md` (Trigger-Liste + Status-Section auf v0.13.0-Surface)
- Modify: `skills/crazy-professor/resources/output-template.md` (`version: 0.12.0` → `0.13.0`)
- Modify: `skills/crazy-professor/resources/chat-output-template.md` (`version: 0.12.0` → `0.13.0`)
- Modify: `skills/crazy-professor/prompt-templates/chat-curator.md` (`version: 0.12.0` → `0.13.0`)
- Modify: `skills/crazy-professor/prompt-templates/chat-round-1-wrapper.md` (`version: 0.12.0` → `0.13.0`)
- Modify: `skills/crazy-professor/prompt-templates/chat-round-2-wrapper.md` (`version: 0.12.0` → `0.13.0`)
- Modify: `docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md` (Phase-Tabelle: 8 → "rolled back in v0.13.0")

- [ ] **Step 1: plugin.json bumpen**

Edit `.claude-plugin/plugin.json`:
- `"version": "0.12.0"` → `"version": "0.13.0"`
- Description aktualisieren auf:
  `"Divergence generator for creative ideation. Four active voices (first-principles-jester, labyrinth-librarian, systems-alchemist, radagast-brown) produce strange but anchored provocations, never advice. Default mode returns 10 provocations; --chat mode runs all four voices and distills 20 ideas; --lab opens a static review browser. Local-only. Phase 4-8 was rolled back in v0.13.0 (see CHANGELOG)."`

- [ ] **Step 2: 5 Frontmatter-Files bumpen**

Suche-und-ersetze `version: 0.12.0` → `version: 0.13.0` in:
- `skills/crazy-professor/resources/output-template.md`
- `skills/crazy-professor/resources/chat-output-template.md`
- `skills/crazy-professor/prompt-templates/chat-curator.md`
- `skills/crazy-professor/prompt-templates/chat-round-1-wrapper.md`
- `skills/crazy-professor/prompt-templates/chat-round-2-wrapper.md`
- `docs/chat-mode-flow.md` (zwei Vorkommen: Frontmatter + Status-Line — beide bumpen)

```bash
grep -rn "version: 0.12.0\|version: '0.12.0'" --include='*.md' --include='*.json' . 2>&1 | grep -v node_modules
```

Erwartet (vorher): ~6-8 Treffer. Edit jeden auf `0.13.0`.

```bash
grep -rn "version: 0.12.0\|version: '0.12.0'" --include='*.md' --include='*.json' . 2>&1 | grep -v node_modules
```

Erwartet (nachher): keine Treffer.

- [ ] **Step 3: docs/CHANGELOG.md aktualisieren — v0.13.0 Eintrag voranstellen**

Lies den aktuellen `docs/CHANGELOG.md`. Füge **direkt nach** der einleitenden ersten Zeile (die mit "Neueste Eintraege oben...") einen neuen v0.13.0-Eintrag ein, **vor** dem aktuellen letzten Eintrag (Phase 8 Draft):

```markdown
## [v0.13.0] [2026-05-02] Rückbau auf Single-Run + Chat-Mode + Lab

**Versions-Bump-Begründung (per VERSIONING.md):** MINOR-Bump weil die User-Flag-Surface schrumpft (`--playground`, `--from-session`, `--dry-run`, `--compact`, `--strict-cross-pollination` entfernt) und ~3000 Zeilen Tooling stillgelegt werden. Skill-Kern (4 Archetypen, Picker, Chat-Mode-Distillation) bleibt unverändert.

**Lerngeschichte:** Stand 2026-05-02 hatte der Skill 18 Runs total in field-notes, 0 telemetry records, 0 patch suggestions, 0 telegram dialogues. Die Phasen 4-8 (Telemetrie, Patch-Suggester, Run-Planner, Cross-Pollination-Linter, Voice-Linter, Word-Pool-Linter, Eval-Suite, Telegram-Dialogue, Playground, Lab v2) wurden gebaut, ohne dass die Phasen 1-3 jemals einen Datenstrom produziert haben, gegen den die späteren Phasen sich rechtfertigen konnten. Master-Plan-Drift mit geplanter Phasen-Erfüllung als Selbstzweck. Rückbau ist die Konsequenz: weniger Maschinerie, sodass die Frage "wird der Skill wirklich genutzt" überhaupt sauber beantwortbar wird.

- 10 Python-Skripte + 1 Shell-Wrapper gelöscht (validate_output, lint_voice, lint_word_pool, lint_cross_pollination, eval_suite, telemetry, patch_suggester, run_planner, telegram_dialogue, build_playground, run_linters.sh).
- `playground/`-Ordner gelöscht.
- 4 Reference-Files gelöscht (chat-mode-flow stub, radagast-activation, review-rubric, usage-patterns).
- 3 Resources gelöscht (archetype-keywords, stop-words, field-notes-init).
- 4 Lexicon-Gate-YAML-Blöcke aus den Archetype-Templates entfernt.
- 5 User-Flags entfernt (`--playground`, `--from-session`, `--dry-run`, `--compact`, `--strict-cross-pollination`).
- `picker.py` schlanker (Force-Flags + `--wishful-share` raus, von ~314 auf ~205 LOC).
- `SKILL.md` von 273 auf ~125 Zeilen.
- `operating-instructions.md` von 494 auf ~85 Zeilen.
- `hard-rules.md` von 106 auf ~80 Zeilen (review-rubric integriert).
- `commands/crazy.md` von 30 auf ~14 Zeilen.
- 10 Plan-/Spec-Files gelöscht (Phase 5/6/7 Designs, Phase-8-Spec, Ideation-Lab-v2 Spec+Plan, 2 eval-baselines, USAGE-PATTERNS-Doppel, linters.md).
- radagast-brown.md "Activation Amendments"-Section bleibt unverändert (binding conditions als Prosa-Bullets, ersetzt das gelöschte references/radagast-activation.md).

---
```

(Trenn-Linie `---` davor und danach jeweils — siehe existierendes Format.)

- [ ] **Step 4: docs/PROJECT.md aktualisieren**

Lies das aktuelle `docs/PROJECT.md`. Update:
- "Aktueller Stand"-Section: aktuelle Beschreibung durch den v0.13.0-Stand ersetzen. Etwa:
  > v0.13.0 released 2026-05-02. Single-Run, Chat-Mode und statisches Lab-HTML aktiv. Master-Plan-Phasen 1-3 belassen, Phasen 4-8 zurückgebaut (kein Voice/Word-Pool/Cross-Pollination-Linter, keine Telemetrie, kein Patch-Suggester, kein Run-Planner, kein Telegram-Scaffold, kein Browser-Playground). Skill-Kern: ein Python-Helper (`picker.py`), 4 Archetype-Templates, Single-Run + Chat-Mode-Distillation via Codex-Subagent. Versions-Policy in `docs/VERSIONING.md`.
- "Offene Baustellen"-Liste: alle Phase-2..Phase-7-Bullets bleiben mit Status `[x]`, Phase 8 wird gestrichen. Eine neue Zeile: `- [x] v0.13.0 (2026-05-02): Phasen 4-8 zurückgebaut, Skill auf Kern reduziert`.

- [ ] **Step 5: docs/CAPABILITIES.md komplett neu schreiben**

Lies den aktuellen Stand zur Sicherheit, dann schreibe das File neu (kürzer):

```markdown
# Faehigkeiten — crazy-professor

## Tools & Integrationen

| Tool / Feature | Status | Seit | Beschreibung |
|----------------|--------|------|--------------|
| Single-Run-Mode | aktiv | 2026-04-22 | 1 Archetype, 10 Provokationen + 1 Next-Experiment, ~30s |
| Chat-Mode (`--chat`) | aktiv | 2026-04-23 | 4 Archetypen, 3 Runden, 20 destillierte Ideen, ~10 LLM-Calls |
| Lab (`--lab`) | aktiv | 2026-04-30 | Standalone Browser für Output-Triage, paste-only, kein LLM-Call |
| Variation-Guard | aktiv | 2026-04-22 | Anti-Streak-Logik in `picker.py` (Archetype-Streak ≥3, Wort-Window 10) |
| Field-Notes-Log | aktiv | 2026-04-22 | Markdown-Tabelle in `.agent-memory/lab/crazy-professor/field-notes.md` |
| Museum-Clause | aktiv | 2026-04-22 | Skill zieht sich nach 10 Runs ohne Keeper selbst zurueck |
| Codex-Round-3-Distiller | aktiv | 2026-04-23 | `codex:codex-rescue` als Round-3-Juror in Chat-Mode |
| Claude-Distiller-Fallback | aktiv | 2026-04-23 | Falls Codex nicht erreichbar |
| Picker-Skript | aktiv | 2026-04-27 | `picker.py` (stdlib-only): mod-4 archetype, mod-4 operator, microsecond-seeded word, JSON-Output. Force-Flags + wishful-share v0.13.0 entfernt. |
| Output-Template + Field-Notes-Schema | aktiv | 2026-04-27 | Marker-Pattern + Tabellen-Spec, Format ist Soll-Vertrag im Prompt (kein Linter mehr) |

Status-Werte: `aktiv`, `experimentell`, `geplant`, `out of scope`, `deprecated`, `entfernt`

## Profile / Modi

- **Single-Run** (default): 1 Archetype-Pick via mod-4 + Variation-Guard, 10 Provokationen, 1 Next-Experiment.
- **Chat-Mode** (`--chat`): alle 4 Archetypen parallel in Runde 1 (5 Provokationen je), Cross-Pollination in Runde 2 (counter/extend), Codex-Distillation in Runde 3 (5 Final-Ideen je Archetype = 20 total).
- **Chat-Mode Dry-Run** (`--chat --dry-run-round1`): nur Runde 1, kein Round-2/3, fuer internes Testen.
- **Lab** (`--lab`): standalone Browser, paste-only, kein LLM-Call.

## MCP-Server

Nicht zutreffend — crazy-professor exponiert keinen MCP-Server. Es nutzt das Codex-Plugin als Subagent fuer Round-3-Distillation, kommuniziert sonst nur ueber Datei-Output.

## Einschraenkungen

- **Lokal nur**: kein Cloud-Sync, kein Multi-Maschinen-State (field-notes liegt pro Projekt)
- **Manuelles Triggering**: kein Auto-Schedule, kein Webhook, kein Bot
- **Single-Topic pro Run**: Chat-Mode kann keinen Multi-Topic-Batch
- **Keine Modell-Mix-Optionen**: Claude fuer Runde 1+2, Codex fuer Runde 3 ist fix
- **Format-Vertrag ist Soll**: kein Pre-Write-Validator mehr (v0.13.0 zurückgebaut). Format-Drift wird beim Lesen sichtbar.
- **Picker-Skript ist optional**: Plugin laeuft auch ohne Python (Fallback-Prosa-Mechanik in operating-instructions Step 2 / picker.py docstring)

## Entfernte Funktionen (v0.13.0, 2026-05-02)

Phase-4-8-Funktionalität entfernt — siehe `docs/CHANGELOG.md` v0.13.0 Eintrag. Wenn etwas davon zurückkommen soll: git-Historie als Archiv.
```

- [ ] **Step 6: docs/ARCHITECTURE.md aktualisieren**

Lies das aktuelle `docs/ARCHITECTURE.md`. Update:
- Komponentendiagramm (Single-Run + Chat-Mode-Pfade): bleibt im Wesentlichen, aber alle Verweise auf "Phase 4 Telemetrie", "Phase 5 Run-Planner", "Lexicon-Gate Lint" etc. entfernen.
- "Kernkomponenten" Section:
  - "Linter-Skripte" Abschnitt komplett entfernen
  - "Browser-Playground" Abschnitt komplett entfernen
  - "Telegram Solution Dialogue Scaffold" Abschnitt komplett entfernen
  - Verbleibende Komponenten aktualisieren: SKILL.md (~125 Zeilen), Prompt-Templates (Lexicon-Gate raus), References (4 statt 7), Resources (6 statt 8), Scripts (1 statt 11)
- "Datenfluss"-Section: alle Verweise auf Telemetrie/Patch-Suggester/Run-Planner/Voice-Linter/Cross-Pollination-Linter raus. Zusammen mit den vereinfachten Steps aus operating-instructions.
- "Persistenz"-Tabelle: Telemetrie-Zeile raus, Patches-Zeile raus, sonst unverändert.
- "Sicherheit"-Section: "Persona-Drift-Risiko" + "Adoption-Risiko" + "Telegram-Bridge"-Bullet bleiben, "Telegram Solution Dialogue (Phase-8-Draft)"-Bullet raus.
- Section "Browser-Playground" und "Telegram Solution Dialogue Scaffold" komplett entfernen.

Konkret: das File bekommt am Ende einen neuen kleinen Block:

```markdown
## Was in v0.13.0 entfernt wurde

Phasen 4-8 (Telemetrie, Patch-Suggester, Run-Planner, Voice/Word-Pool/Cross-Pollination-Linter, Eval-Suite, Telegram-Dialogue, Browser-Playground, Ideation-Lab-v2-Design) wurden am 2026-05-02 zurückgebaut. Detail in `docs/CHANGELOG.md` v0.13.0 Eintrag.
```

- [ ] **Step 7: README.md aktualisieren**

In `README.md`:
- Trigger-Block: `--dry-run`, `--from-session` Zeilen entfernen. Behalten: `/crazy <topic>`, `/crazy <topic> --chat`, `/crazy --lab`.
- Topic-Resolution-Block: `--from-session`, `--dry-run`-Bullets entfernen. `--lab`-Bullet bleibt.
- Status-Section: aktualisieren auf "v0.13.0 active. Default single-run + Chat-Mode + static Lab. Phase 4-8 rolled back on 2026-05-02 (telemetry, linters, playground, telegram-dialogue scaffold all removed). See CHANGELOG."
- Phase 8 / Telegram solution-dialogue Erwähnung in Status-Block entfernen.

- [ ] **Step 8: Master-Plan-Tabelle aktualisieren**

In `docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md`:
- In der Phasen-Tabelle: Status der Phasen 4-7 von ✅ auf "✅ → ❌ zurückgebaut in v0.13.0" oder ähnlich. Phase 8 von ⏳ auf "❌ zurückgebaut in v0.13.0".
- Optional: ein neuer Bullet unter der Tabelle: "**Update 2026-05-02:** Phasen 4-8 zurückgebaut. Skill auf Phase-1-3-Stand reduziert. Siehe `docs/CHANGELOG.md` v0.13.0 Eintrag und `docs/specs/2026-05-02-v013-rueckbau-design.md`."

(Bitte nur die Phasen-Tabelle und einen kurzen Update-Bullet ändern. Die Plan-Punkte-Listen darunter unangetastet lassen — das ist historisches Material.)

- [ ] **Step 9: Verify gesamten Stand**

```bash
git status --short
```

Erwartet: 12-13 modified Files, kein untracked.

```bash
grep -rn "version: 0.12.0\|version: '0.12.0'" --include='*.md' --include='*.json' . 2>&1 | grep -v node_modules
```

Erwartet: keine Treffer.

```bash
grep -rn "playground\|--from-session\|--dry-run\|--compact\|--strict-cross-pollination\|telemetry\|patch_suggester\|lint_voice\|lint_word_pool\|lint_cross_pollination\|run_planner\|eval_suite\|build_playground\|telegram_dialogue" \
  commands/ skills/crazy-professor/ 2>&1 | grep -v "Binary file"
```

Erwartet: keine Treffer in den User-Pfaden (kann aber in `docs/` und `docs/CHANGELOG.md` geben — Erwähnungen im "was wurde entfernt"-Kontext sind erlaubt und sogar erwünscht).

- [ ] **Step 10: Commit**

```bash
git add .claude-plugin/plugin.json \
       README.md \
       docs/PROJECT.md docs/CAPABILITIES.md docs/ARCHITECTURE.md \
       docs/CHANGELOG.md docs/chat-mode-flow.md \
       docs/plans/2026-04-26-crazy-professor-erweiterungs-master-plan.md \
       skills/crazy-professor/resources/output-template.md \
       skills/crazy-professor/resources/chat-output-template.md \
       skills/crazy-professor/prompt-templates/chat-curator.md \
       skills/crazy-professor/prompt-templates/chat-round-1-wrapper.md \
       skills/crazy-professor/prompt-templates/chat-round-2-wrapper.md
git commit -m "$(cat <<'EOF'
crazy-professor | rueckbau 10/10 — v0.13.0 Doku + Versions-Bump

plugin.json 0.12.0 → 0.13.0. 5 Frontmatter-Files gebumpt.
PROJECT/CAPABILITIES/ARCHITECTURE/README aktualisiert auf v0.13.0
Surface (Single + Chat + Lab). CHANGELOG bekommt v0.13.0 Eintrag mit
Lerngeschichte. Master-Plan-Phasen-Tabelle markiert Phase 4-8 als
zurückgebaut. chat-mode-flow.md Frontmatter gebumpt.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 11: Smoke-Test (manuell, kein Commit)

**Ziel:** Drei Pfade im Manualtest verifizieren. Kein Code committen — wenn ein Test fehlschlägt, einen Fix-Commit auf master setzen oder zurück zu Task 7-9.

- [ ] **Step 1: `git status` clean — alle 10 Tasks gelandet**

```bash
git status --short
git log --oneline -11
```

Erwartet: clean working tree, 11 Commits seit dem Spec-Commit (Plan + 10 Rueckbau-Schritte).

- [ ] **Step 2: Single-Run-Smoke**

In Claude-Code-Session (interaktiv):

```
/crazy schreibtisch aufräumen
```

Erwartet:
- Skill rennt durch ohne Fehler
- Output-File entsteht in `~/Desktop/.agent-memory/lab/crazy-professor/2026-05-02-HHMM-schreibtisch-aufraeumen.md` (oder ähnlich)
- File hat: Frontmatter mit `mode: single` + `version: 0.13.0`, Divergence-Banner, **exakt 10** Provokationen mit Pattern `<text> -- [cost: X] -- anchor: Y`, "Next Experiment"-Section, "Self-Flag"-Checkbox-Section
- Field-notes bekommt **eine** neue Row angehängt (Run-Nummer +1, mode:single)

Manuell prüfen, ob die 10 Provokationen tatsächlich 10 sind, ob das Format passt, ob die Voice zum gepickten Archetype passt.

- [ ] **Step 3: Chat-Mode-Smoke**

```
/crazy plugin marketplace strategie --chat
```

Erwartet:
- Skill rennt durch ohne Fehler (~2-4 min)
- Output-File entsteht in `~/Desktop/.agent-memory/lab/crazy-professor/chat/2026-05-02-HHMM-plugin-marketplace-strategie.md`
- File hat: Frontmatter mit `mode: chat` + `distiller` + `round1_picks` + `round2_status`, Divergence-Banner, **Round 1** (4×5 Provokationen), **Round 2** (oder `round2_status: degraded`), **Round 3** (4×5 Final-Ideen + Top-3 + Next Experiment)
- Field-notes bekommt **eine** neue Row angehängt (mode:chat, archetype: all-4, word: multi)
- Codex-Subagent wurde aufgerufen (oder Claude-Fallback griff)

- [ ] **Step 4: Lab-Smoke**

```
/crazy --lab
```

Erwartet:
- Browser-Tab öffnet sich (oder fallback: `Open this file manually: file://...` wird ausgegeben)
- HTML-Lab lädt, statisches UI ohne LLM-Call

- [ ] **Step 5: Reject-Smoke**

```
/crazy --chat
```

Erwartet:
- Sofortige Ablehnung mit Text:
  `Chat-mode requires an explicit topic. Run /crazy <topic> --chat or use single-run for ambient topics.`

- [ ] **Step 6: Code-Hygiene-Verify**

```bash
grep -rn "playground\|--from-session\|--dry-run\b\|--compact\|--strict-cross-pollination\|telemetry\.py\|patch_suggester\|lint_voice\|lint_word_pool\|lint_cross_pollination\|run_planner\|eval_suite\|build_playground\|telegram_dialogue" \
  commands/ skills/crazy-professor/ 2>&1 | grep -v "Binary file" | grep -v "^Binary"
```

Erwartet: keine Treffer in `commands/` und `skills/crazy-professor/` (Erwähnungen in `docs/` sind okay als Lerngeschichte).

- [ ] **Step 7: Done — Smoke pass berichten**

Berichte dem User:
- "Alle 10 Code-Commits gelandet, working tree clean."
- Ergebnis Single-Run-Smoke (Output-File-Pfad + erste 3 Provokationen-Stichprobe)
- Ergebnis Chat-Mode-Smoke (Output-File-Pfad + Distiller-Status)
- Lab öffnete sich
- Reject-Pfad funktioniert
- Bereit für nächsten Schritt.

---

## Self-Review (vom Plan-Schreiber, nach Schreibphase)

**1. Spec coverage check.** Jede Bullet-Liste in der Spec hat einen Task:

- ✅ "Was bleibt (Skill-Komponenten)" — wird in Tasks 7+8+9 nicht angefasst (außer Lexicon-Gate aus Templates raus).
- ✅ "10 Python-Skripte + 1 Shell-Wrapper löschen" — Task 3
- ✅ "1 Ordner: playground/" — Task 5
- ✅ "4 References löschen" — Task 6
- ✅ "3 Resources löschen" — Task 4
- ✅ "4 Lexicon-Gate-YAML-Blöcke" — Task 8
- ✅ "10 Plan-/Spec-Files löschen" — Task 2
- ✅ "5 User-Flags weg" — Task 9 (in commands/crazy.md + SKILL.md + operating-instructions.md)
- ✅ "Datenfluss Single-Run 5 Steps" — Task 9 operating-instructions.md
- ✅ "Datenfluss Chat-Mode C1–C6" — Task 9 operating-instructions.md
- ✅ "--lab L1" — Task 9 operating-instructions.md
- ✅ "Was rausfällt aus dem Datenfluss" — Task 9 (negativ: nicht mehr drin)
- ✅ "Hard Rules nach Rückbau" — Task 9 hard-rules.md
- ✅ "PO-Operatoren alle 4, gleichverteilt" — Task 7 picker.py
- ✅ "Picker-Force-Flags raus" — Task 7
- ✅ "Migrationsplan 11 Schritte" — Tasks 1-11
- ✅ "Risiken" — keine Action, nur dokumentiert in Spec; im Plan abgedeckt durch defensive Schritte (Smoke-Test, Verify-Steps)
- ✅ "Versionierung v0.13.0 MINOR" — Task 10
- ✅ "Smoke-Test Akzeptanzkriterien" — Task 11
- ✅ "CHANGELOG-Eintrag (vorbereitet)" — Task 10 Step 3

**2. Placeholder scan.** Kein "TBD"/"TODO"/"implement later" außer im Plan-Titel des follow_up_plan-Eintrags der Spec — der ist im Spec, nicht im Plan, und ist berechtigt (er war eine Vorab-Eintragung). Kein "Add appropriate error handling". Kein "Similar to Task N" ohne Wiederholung des Codes.

**3. Type/Identifier consistency.** `picker.py`-Funktionsnamen `pick_single`/`pick_chat`/`variation_guard`/`picker_seed`/`pick_word`/`read_word_pool`/`read_last_log_rows`/`normalize_archetype` sind in Task 7 alle definiert und kommen sonst nicht außerhalb dieses Tasks vor. `OPERATORS` ist die einzige Operator-Konstante (kein `BASE_OPERATORS`/`WISHFUL_OPERATOR` mehr). `ARCHETYPES` bleibt als 4-Tupel.

**4. Scope.** 11 Tasks, jeder Task ist ein logischer Commit, keiner über 200 Zeilen Plan-Text — granular genug.

Plan ist konsistent.

---

## Plan complete

**Plan complete and saved to `docs/plans/2026-05-02-v013-rueckbau-implementation.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
