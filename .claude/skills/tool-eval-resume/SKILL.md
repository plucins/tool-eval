---
name: tool-eval-resume
description: >
  Operator entry skill to safely resume an interrupted run by id. Invoke as
  `/tool-eval-resume <run_id>`. Validates the argument and checks resume safety,
  then hands control to the tool-eval-orchestration workflow. Refuses to resume
  when the frozen configuration revisions no longer match.
---

# tool-eval-resume

Entry skill (D-018). Directly invoked by the operator; it validates the argument,
checks that resuming is safe, and hands the operation to the orchestration
workflow.

## Usage

```
/tool-eval-resume <run_id>
```

- `<run_id>` (required): the id of a previously created run, e.g.
  `research-20260724-053608-3e810720`.

## What it does

1. Validate that exactly one run id was provided.
2. Run `python -m tool_eval run resume-check <run_id>`.
   - `RUN_RESUMABLE`: hand over to `tool-eval-orchestration` to continue the run
     from its recorded state.
   - `CONFIG_REVISION_MISMATCH`: refuse to resume, explain that the taxonomy /
     schema / policy revisions have changed since the run started, and advise
     starting a new run so incompatible data is not mixed (R-07).
3. Report the outcome envelope.

## Guarantees and limits

- Resume is allowed only when the run's frozen `effective_revisions` still match
  the current configuration; a controlled revision change forces a fresh run.
- A failed or unresumable run never alters an existing active profile.

Never `run init resume` or replace the original run id. Continue from validated
on-disk results and recorded decisions; never infer curation approval from a
previous session's summary.
