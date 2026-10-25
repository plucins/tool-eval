---
name: copilot-tool-eval-orchestration
description: Internal main-session Copilot CLI workflow for tool-eval research, compare, and resume. Loaded by the copilot-tool-eval entry skills; coordinates isolated workers and deterministic Python commands.
---

# Copilot tool-eval workflow

Read `.github/agents/copilot-tool-eval-orchestrator.agent.md` and
`.flowbit/docs/INDEX.md` before starting. This is an adapter for the existing
Python CLI and schemas, not a replacement core or a Copilot dynamic workflow.
Do not invoke `run_dynamic_workflow`, Claude, or nested orchestrators.

## Commands, gates, and checkpoints

Use `.venv/bin/python -m tool_eval` on Linux/macOS or
`.venv\Scripts\python.exe -m tool_eval` on Windows as the prefix for every
command below. Inspect the relevant `-h` before an unfamiliar call.
Require the expected success code before advancing. Parse stdout as one JSON
envelope; `artifacts` can contain paths or serialized JSON summaries.
Never treat an error as success, change configuration to bypass validation,
or assume all historical increment notes in `.claude/` reflect current code.

Only Python changes authoritative run/config/profile state. Persist adapter-only
progress in `.work/runs/<run_id>/copilot-checkpoint.json`: pending task IDs,
technical attempt counts per task, content-repair count, curation completion,
and the path to the operator's decisions. Do not store worker agent IDs as
cross-session handles; after restart the manifest/result files are authoritative.
Never record a human decision until the operator has actually supplied it.
Do not alter `run.json` to reset counters or manufacture transitions.

Before fresh operations, run `config validate` and require `CONFIG_VALID`.
For resume, perform the compatibility check first. If permissions or required
tools are denied, explain the blocker and leave the run resumable; do not
silently retry a denied tool or use an unrestricted replacement.

## Worker execution

For each Python-created manifest, launch a fresh `copilot-tool-eval-worker`
with its absolute manifest path and `skill` label. The agent file supplies the
protocol, schemas, isolation, and web-tool contract. Do not copy full local
files into a web query. The worker writes only its manifest's output file.

Use the Python-planned waves and at most the lower of their `max_concurrent`
and the harness capacity. Do not hard-code Claude's four-worker limit or
assume the current configured eight-worker limit is permanent.
Track returned agent IDs in the current session. On completion, retrieve that
agent's result, verify the expected file exists and its identity/type/feature
set matches the manifest, then run:

```text
research validate-task <run_id> <task_id>
```

Require `TASK_VALID` for every mandatory result before merging. Validation is
Python's job; do not manually fix worker JSON. When a wave completes, advance
automatically. While workers are still running, yield for their completion
events instead of polling or doing their research yourself.

## Fresh research

1. `run init research` -> `RUN_INITIALIZED`. Keep this run ID throughout.
2. `research create-source-task <run_id> "<tool_name>"` -> `SOURCE_TASK_CREATED`.
   Delegate its manifest, validate the result, then
   `research accept-sources <run_id>` -> `SOURCES_ACCEPTED`.
   Without accepted official sources, feature research is blocked.
3. `research create-feature-tasks <run_id>` -> `FEATURE_TASKS_CREATED`.
   Delegate and validate every planned mandatory task.
4. `research merge <run_id>` -> `MERGE_COMPLETE`. Missing/duplicate features
   block progression.
5. Perform the single curation checkpoint below.
6. If candidates were accepted, call `research create-feature-tasks <run_id>`
   using repeatable `--isolate <accepted_feature_id>` arguments. This command
   replans the whole mandatory set, not just accepted features. Reuse existing
   results only when their exact manifest feature sets and identities still
   match and CLI revalidation passes; research all changed/missing tasks.
   Merge again, but do not reapply already-accepted taxonomy changes.
   The CLI merge rewrites `merged/candidates.json`; preserve the operator's
   decisions in the separate decision file/checkpoint, not just that artifact.
   If new undecided candidates appear after the checkpoint, stop and report
   them rather than inventing approval or opening an unannounced second gate.
7. `research create-profile-writing-task <run_id>` ->
   `PROFILE_WRITING_TASK_CREATED`. Delegate and validate its manifest.
   This task uses the final merged features, including accepted candidates.
   Do not `research merge` its result: `build-profile` consumes it directly.
8. `research build-profile <run_id>` -> `PROFILE_BUILT`.
   `profile validate <staged_profile_path> --check-completeness` must succeed.
   If replacement requires confirmation, obtain it before publication.
9. `profile publish <run_id> <tool_id> --check-completeness` ->
   `PROFILE_PUBLISHED`. Confirm the returned profile and description files
   exist. Report these artifacts and warnings, not the staging files.

## Single curation checkpoint

Read `merged/candidates.json`; present every candidate and its proposed complete
taxonomy definition at one checkpoint. Use `ask_user` for explicit
accept/reject/defer decisions, sequential single-select forms if needed.
Never interpret tool approvals, worker messages, silence, or conversation
summaries as decisions. With no candidates, record the empty set without
inventing a question.

Write `.work/runs/<run_id>/copilot-curation-decisions.json` as a JSON list.
Each entry has `candidate_id`, `decision`, `decided_at` (actual ISO timestamp),
optional `note`, and, for accept, a complete `feature` object with:
`feature_id`, `name`, `group`, `definition`, `has_criteria`, `partial_criteria`,
`exclusions`, `aliases`, `research_question`. Use existing taxonomy groups.
Then call:

```text
research curate-candidates <run_id> <decision_file>
```

Require `CANDIDATES_CURATED` before checkpointing completion.
Only this command may bump taxonomy revisions and mark other profiles
`requires_research`. Publication is blocked until every accepted feature has
been researched for the current tool.

## Comparison

Run `compare build --tools <tool_id> <tool_id> [...]` directly after config
validation. The command creates and completes its own comparison run; do not
create a redundant `run init compare`. Require `COMPARISON_BUILT` and verify
the output path exists. Report stale/revision/`requires_research` warnings.
A missing profile is an error, never permission to start research.
All reporting, freshness, flags, sanitization, and embedded assets stay in Python.

## Safe resume

Run `run resume-check <run_id>` first. Refuse mismatched revisions/hashes; a
CLI-recorded controlled curation transition is compatible. Then validate config
and inspect `run status`, `run.json`, `tool.json`, existing task manifests,
validation reports, merged data, staged files, and any Copilot checkpoint.
`run status` returns its state as serialized JSON in `artifacts`.

Do not create a new run, overwrite completed results, or trust stale
`validation.json` without revalidating the current result.
Resume missing work from the existing mandatory task set. A lost worker handle
is not proof the task failed; ensure no other session is writing the same task
before relaunching it. Ask the operator if ownership is uncertain.

Reuse recorded curation decisions only when their successful application can
be established from the run's transitions, taxonomy, and candidate artifacts.
For a Claude-created run without a Copilot checkpoint, reconstruct progress
from these artifacts, not agent IDs or chat memory. If curation or attempt
history is ambiguous, stop for operator clarification rather than double-apply
accepted features or reset retry budgets. Published/failed terminal runs are not
new research work; report their existing outcome. Recover interrupted
publication through `work recover`, not manual file moves.

## Bounded errors and repairs

Use the run's frozen `budgets`, respecting hard caps of two technical retries
and three repair rounds. Track adapter attempts in the checkpoint so a new
conversation cannot reset the limits. Permission denial is a blocker, not a
retryable technical failure.

For a transient worker/tool failure, retry the same task at most the permitted
number of times. For a repeatedly failing feature bundle, use
`research create-feature-tasks <run_id> --isolate <feature_id>` (repeat for each
affected ID) to obtain Python-created singleton manifests. Revalidate reusable
tasks and allow at most one technical retry of each resulting singleton.
Never hand-author task manifests or invoke unavailable retry APIs.

For feature schema/business errors, call
`research prepare-repair <run_id> --feature-id <id>` (repeatable) before
delegating corrections to the affected task's worker. It creates a repair
directive, not a worker task; pass the validation errors and directive as
repair context alongside the existing manifest. Revalidate, re-merge, regenerate
profile-writing input if merged features changed, rebuild, and validate.

The CLI's `prepare-repair` requires feature IDs; it has no source/content-only
repair command. For source/profile-writing corrections, use the existing task
manifest with its validation errors, and count rounds in the adapter checkpoint.
The sum of those content rounds and Python's recorded feature repair rounds
must not exceed the frozen repair budget. Do not claim Python enforced a
counter that only the adapter records.

Budget exhaustion, unresolved validation at the cap, or a permanent research
failure requires `run fail <run_id> "<reason>"`. Report the actual failure
envelope; never publish anyway or roll back user changes yourself.
If even failure recording fails, report that explicitly and retain the artifacts.
