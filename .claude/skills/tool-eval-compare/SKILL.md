---
name: tool-eval-compare
description: >
  Operator entry skill to build a self-contained offline HTML comparison of two
  or more already-researched tools. Invoke as
  `/tool-eval-compare <tool_id> <tool_id> [<tool_id>...]`. Validates arguments,
  then hands control to the tool-eval-orchestration workflow. Does not start
  research.
---

# tool-eval-compare

Entry skill (D-018). Directly invoked by the operator; it validates arguments and
hands the operation to the orchestration workflow. Comparison never starts
research or workers (Sec 3.7).

## Usage

```
/tool-eval-compare <tool_id> <tool_id> [<tool_id>...]
```

- Two or more `tool_id`s (required): the tools to compare. Each must already
  have a published active profile.

## What it does

1. Validate that at least two tool ids were provided.
2. Hand over to `tool-eval-orchestration` with operation `compare` and the tool
   ids. That workflow resolves the tools, copies active profiles into the
   comparison run, validates profiles/revisions/dates, computes deterministic
   freshness and flags, renders sanitised Markdown into a Jinja2 template with
   bundled Bootstrap, and publishes one HTML file under `outputs/comparisons/`.
3. Report the output HTML path and any warnings.

## Guarantees and limits

- A missing profile for a requested tool is an error. An old revision or stale
  date produces a warning, not a failure.
- `requires_research` profiles are allowed with a warning; their unresearched
  cells are excluded from flags.
- The output is a single self-contained file that works offline with no CDN and
  no execution of profile data as code (D-017 / R-09).

## Increment 3 status

Implemented. `compare build --tools <id> <id> [...]` loads and validates the
active profiles, computes deterministic freshness and flags, renders sanitized
Markdown into a Jinja2 template with bundled Bootstrap and a Capgemini-inspired
theme, and writes one self-contained offline HTML file under
`outputs/comparisons/`. The report embeds all CSS/JS/fonts locally (no CDN) and
never executes profile or source data as code (D-017 / R-09).
