# Chat-Mode Output Template

Every `--chat` invocation produces a Markdown file in this exact shape.
The skill fills in the angle-bracketed fields.

Pfad: `.agent-memory/lab/crazy-professor/chat/YYYY-MM-DD-HHMM-<topic-slug>.md`

---

```markdown
---
skill: crazy-professor
mode: chat
version: 0.9.0
timestamp: <ISO-8601 UTC>
topic: "<user input, one line, unmodified>"
archetypes: [first-principles-jester, labyrinth-librarian, systems-alchemist, radagast-brown]
rounds: 3
distiller: <codex | claude-fallback>
distiller_reason: <only if claude-fallback: why codex was unavailable>
round1_picks:
  jester: { word: <w>, operator: <op> }
  librarian: { word: <w>, operator: <op> }
  alchemist: { word: <w>, operator: <op> }
  radagast: { word: <w>, operator: <op> }
round2_status: <full | degraded | failed>
round2_reason: <only if degraded/failed: why>
llm_calls: <number, expected 10>
---

# Chat: <topic>

**Mode:** chat | **Distiller:** <codex|claude-fallback>

> DIVERGENCE WARNING: This output is provocation material, not advice.
> The ideas below are deliberately exaggerated, one-sided, or absurd.
> They exist to destabilize fixed thinking, not to be implemented as-is.
> The final 20 ideas in Round 3 are Codex-curated but still provocations,
> not recommendations. Pick what moves you, discard the rest, and use
> the "Next Experiment" section to turn one nudge into something
> testable.

## Round 1 — Parallel Voices (5 Provocations per Archetype)

### Jester (word: <w>, operator: <op>)

1. <provocation> — anchor: <link>
2. <provocation> — anchor: <link>
3. <provocation> — anchor: <link>
4. <provocation> — anchor: <link>
5. <provocation> — anchor: <link>

### Librarian (word: <w>, operator: <op>)

1. <provocation> — anchor: <link>
2. <provocation> — anchor: <link>
3. <provocation> — anchor: <link>
4. <provocation> — anchor: <link>
5. <provocation> — anchor: <link>

### Alchemist (word: <w>, operator: <op>)

1. <provocation> — anchor: <link>
2. <provocation> — anchor: <link>
3. <provocation> — anchor: <link>
4. <provocation> — anchor: <link>
5. <provocation> — anchor: <link>

### Radagast (word: <w>, operator: <op>)

1. <provocation> — anchor: <link>
2. <provocation> — anchor: <link>
3. <provocation> — anchor: <link>
4. <provocation> — anchor: <link>
5. <provocation> — anchor: <link>

## Round 2 — Cross-Pollination (2-3 per Archetype, counter/extend)

Wenn round2_status: degraded: dieser Block traegt einen Disclaimer am
Anfang: "Runde 2 degradiert: <n> von 4 Archetypen unter 2 Provokationen.
Nur Runde-1-Daten sind in die Codex-Destillation eingeflossen."

### Jester — Runde 2

- counter: <archetype> #<n> — <provokation> — anchor: <link>
- extend: <archetype> #<n> — <provokation> — anchor: <link>
- <counter|extend>: ...

### Librarian — Runde 2

- ...

### Alchemist — Runde 2

- ...

### Radagast — Runde 2

- ...

## Round 3 — Codex Distillation (Final 20)

*Exactly 5 ideas per archetype. Scoring: W = Wert, U = Umsetzbarkeit,
S = Systemfit (each 1-5). Cost-Tag: low | medium | high | system-break.
Counter/Extend markers preserved where applicable.*

### Jester-5

1. <idee> — [cost: X] — anchor: Y — [score: W=n U=n S=n]
2. ...
5.

### Librarian-5

1. ...
5.

### Alchemist-5

1. ...
5.

### Radagast-5

1. ...
5.

## Top-3 Cross-Pollination Hits

The three most substantial counter/extend-provocations from Round 2,
with short justification of why the crossing produced genuine insight.

1. <ref, e.g. "jester counter: alchemist #4"> — <1-sentence justification>
2. ...
3. ...

*If round2_status was `degraded` or `failed`: "Keine Cross-Pollination-
Hits verfuegbar, Runde 2 degradiert."*

## Next Experiment (one, only)

Provocation number **<Archetype-Name #n, e.g. "Librarian-5 #2">** is
testable in the next hour with tools you already have.

<one-paragraph description of the test: what you do, when, what you
observe, what counts as "this was worth trying">

## Self-Flag (for field-notes.md)

- [ ] kept (at least 1 of 20 final ideas landed in wiki/inbox, ISSUES2FIX, or skills-backlog within 14 days)
- [ ] round2-was-degraded (track if degradation was triggered)
- [ ] distiller-fallback-used (Codex was unavailable, Claude destilled)
- [ ] voice-cross-drift (one or more archetypes sounded like another in Round 2)
```

---

## Notes on the template

- **Divergence warning** is mandatory and slightly different from
  Single-Run (mentions Codex curation). Keep verbatim.
- **Frontmatter round1_picks** records all 4 words+operators for
  reproducibility and field-test analysis.
- **Round 2 degradation** is dokumentiert im Frontmatter
  (`round2_status`) UND im Body-Disclaimer. Doppelte Markierung ist
  gewollt — Frontmatter fuer Tooling, Body-Text fuer User.
- **Counter/Extend-Marker** bleiben sowohl in Round 2 als auch in
  Round 3 (wo sie in die Final-20 uebernommen wurden) erhalten. Das
  ist Transparenz ueber die Herkunft einer Idee.
- **Scoring** erscheint nur in Round 3, nicht in Round 1/2.
- **Self-Flag** ist erweitert um Chat-Mode-spezifische Flags
  (round2-degraded, distiller-fallback, voice-cross-drift).
- **Next Experiment** verweist mit Archetype-Nummer-Notation, damit
  der User sofort weiss, aus welcher Sektion die gewaehlte Idee kommt.

## Worst-Case Minimal Template (nur Runde 1, wenn 2+3 gescheitert)

Falls Runde 2 UND Runde 3 scheitern (z.B. Codex nicht verfuegbar UND
Claude-Fallback wirft), schreibt das Skill einen Minimal-Output:

```
round2_status: failed
round3_status: failed
distiller: none
```

Body enthaelt nur Runde-1-Outputs plus einen Abschluss-Block:

> **Chat-Mode konnte nicht vollstaendig ausgefuehrt werden.** Runde 2
> und/oder Runde 3 sind gescheitert. Die 20 Provokationen aus Runde 1
> sind unten gelistet. Fuer die volle Chat-Mode-Erfahrung
> (Cross-Pollination + Destillation): erneut aufrufen, wenn die
> Ursache (<reason>) behoben ist.

Dann folgen die 20 Runde-1-Provokationen als Liste — kein Scoring,
kein Ranking, kein Next-Experiment.

Das ist KEIN Produkt-Output, sondern ein Rohmaterial-Dump fuer den
User, damit die Arbeit nicht verloren ist. Das Flag
`distiller-fallback-used` wird NICHT gesetzt (weil auch kein Fallback
lief) — stattdessen das neue Flag `chat-mode-incomplete` eingefuehrt.
