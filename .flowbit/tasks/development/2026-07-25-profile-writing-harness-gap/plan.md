# Plan: implement the `profile-writing` task type end to end

## Trigger

Run `research-20260725-092106-96b31f5c` (GitHub Copilot) reached state `merged`
(29 merged feature results, 39 sources) and then stalled: per
`tool-eval-orchestration/SKILL.md` step 5, the next step is delegating a
`profile-writing` task to a worker, but no part of the harness actually
supports that task type end to end. This plan closes the gap so the run (and
future runs) can proceed past `merged` to a published profile.

## Applicable Standards

Read from `.flowbit/docs/INDEX.md` and the files it indexes:

- **`standards/global/architecture.md`** — deterministic Python core (no
  model/LLM/web calls in Python), pure logic behind IO wrappers (e.g.
  `research/sources.py` vs `research/pipeline.py`), hatchling/src-layout
  packaging (schemas force-included as a directory, so editing existing
  schema files needs no `pyproject.toml` change).
- **`standards/global/validation.md`** — JSON Schema is the source of truth
  for structure/types; status-dependent/cross-record rules belong in
  `validation/business.py`, not schemas. Profile schema conventions (D-016):
  lowercase-ASCII identifiers, `additionalProperties: false`, omit rather than
  null optional fields.
- **`standards/global/research-protocol.md`** — single curation gate (not
  touched by this change: profile-writing content is not a curation-gate
  citizen); no source voting; evidence/retained-source scope (short excerpts,
  not full page copies); source reuse before new `WebSearch` calls.
- **`standards/global/security.md`** — worker isolation: a worker writes only
  inside its own task directory and writes exactly **one** result file; no
  secrets/credentials in output; official-sources-only for factual claims.
  This directly shapes the core design decision below (section prose must be
  embedded in the worker's single `result.json`, not a second file).
- **`standards/backend/api.md`** — single JSON envelope CLI contract; new
  command follows the existing `research <verb>` pattern exactly.
- **`standards/global/conventions.md`** — snake_case functions, kebab-case
  JSON/YAML config and schema filenames, JSON for manifests/results, English
  content with verbatim `excerpt` fields.
- **`standards/global/minimal-implementation.md`** — no speculative
  abstractions; reuse the existing `create_source_task` pattern rather than
  inventing a new task-creation framework.
- **`standards/testing/test-writing.md`** — new tests follow
  `test_item{N}_{feature}.py`; next free number is `12`.

## Root causes (confirmed by direct code/schema reads)

1. **No CLI command creates a `profile-writing` task manifest.** Only
   `create-feature-tasks` and `create-source-task` exist
   (`src/tool_eval/cli.py`); `task.schema.json` and `subagent-result.schema.json`
   already enumerate `profile-writing` as a valid `task_type`, but nothing
   ever writes one.
2. **The worker contract never describes writing `description.md` section
   prose.** `.claude/agents/tool-eval-worker.md` §"Profile-writing tasks"
   covers `additional_facts`/`use_cases`/`release_history` only.
   `profiles/build.py:_load_section_texts` hard-requires `--sections` or a
   `description-sections.json` file in the run directory, and
   `profiles/description.py:assemble_description` rejects a profile that's
   missing prose for any `required: true` section
   (`characteristics`, `access`, `workflows`, `constraints` today, config-driven).
3. **No code path ever produces `description-sections.json`.** The only
   references to that filename are test fixtures
   (`tests/test_item10_source_build.py:267-276,393-395`) that write it by hand.
4. **Newly found, adjacent schema bug:** `subagent-result.schema.json` has
   `additionalProperties: false` and does **not** declare `unresolved_issues`
   as a property, yet `profiles/build.py:_collect_content`/`_absorb` already
   reads `payload.get("unresolved_issues", [])` from worker results and folds
   it into `profile.json`. Today, any worker that actually returns
   `unresolved_issues` (a legitimate, documented content channel per the
   worker doc) would fail schema validation in `validate_task`. This has to be
   fixed together with `description_sections`, since both are new/expanded
   properties on the same schema.
5. **Doc-accuracy nit in `SKILL.md` step 5:** it says the profile-writing task
   also extracts "candidate features," but `research/merge.py` already merges
   `candidates` from **feature-research** task results at the `merge` step
   (`_merge_named(worker_results, "candidates", "candidate_id")`) —
   confirmed by the stuck run's own `merged/candidates.json`, produced before
   profile-writing ever ran. This is a wording fix, not a functional gap.

## Design decisions

**D1 — Section prose is embedded in the worker's single `result.json`, not a
second file.** The worker-isolation standard requires a worker to write
exactly one result file inside its own task directory. So `description_sections`
becomes a new object property on `subagent-result.schema.json` (section id →
Markdown string), populated by the profile-writing worker in the same
`result.json` as `additional_facts`/`use_cases`/etc. `build.py` then sources
section text from that result by default. `--sections` / a manual
`description-sections.json` remain as an explicit operator override (keeps
existing tests and any manual-recovery workflow working unchanged).

**D2 — The manifest inlines everything the worker needs; the worker does not
read repository config files itself.** Matches the existing feature-research
pattern (`_task_input` inlines taxonomy entries rather than pointing the
worker at `feature-taxonomy.yaml`). The profile-writing `input.json` will
carry: tool identity, the accepted source registry projection, the merged
`feature_results` (so descriptive prose is grounded in already-verified
statuses, not re-invented), the `additional-fact-sections.yaml` topic/`fact_id`
hints (already referenced by the worker doc but never delivered), the ordered
`profile-sections.yaml` section list (`id`/`title`/`required`), and an
explicit, unambiguous release-history capture directive (see D3).

**D3 — Replace the vague "manifest's stated number" wording with a concrete,
mutually exclusive directive:**
```json
"release_history": {
  "mode": "since_date",       // or "most_recent" on a tool's first-ever pass
  "since_date": "2026-07-24T09:42:45Z",
  "max_items": 10               // present only when mode is "most_recent"
}
```
`mode` is `"since_date"` whenever `data/profiles/<tool_id>/profile.json`
already exists (re-research pass; `since_date` = its `research.researched_at`);
otherwise `"most_recent"` with a fixed default cap (`DEFAULT_RELEASE_HISTORY_CAP
= 10`, a new module constant — no new `runtime.yaml` key, consistent with how
`DEFAULT_SOURCE_CLASSES` is already a plain module constant in `sources.py`,
not a config knob).

**D4 — `unresolved_issues` on `subagent-result.schema.json` copies the inline
item shape already used inline in `profile.schema.json`**, rather than
factoring out a new shared `unresolved-issue.schema.json` file. The item
shape is used in exactly two places after this change (same reuse count as
today's single inline copy in `profile.schema.json`); introducing a new
schema file + registry entry + cross-file `$ref` for two call sites is more
machinery than the change needs (minimal-implementation standard). Leave the
pre-existing, apparently-unused wrapper `unresolved-issues.schema.json`
(`{"issues": [...]}`) alone — nothing in the pipeline produces that wrapped
shape; it's exercised only by one standalone unit test
(`test_item1_profile_model.py:162`). Not in scope to remove or fix here.

**D5 — No new run state-machine enforcement needed.** `runs/manager.py`'s
`transition()` is a free-form state string append; it does not validate
from/to pairs. Adding `"profile_writing_in_progress"` as a new transition
value needs no changes to `manager.py`.

**D6 — No separate `research merge` step for profile-writing content.**
`build_profile`'s `_collect_content` already scans `tasks/*/task.json` for
`task_type == "profile-writing"` directly; unlike feature-research results,
these content channels are consumed straight from the task directory. Make
this explicit in `SKILL.md` so the orchestrator doesn't wait for a merge that
will never run for this task type.

## Implementation steps

### 1. Schema changes (`src/tool_eval/validation/schemas/subagent-result.schema.json`)
- Add `description_sections`: object, `propertyNames: {"pattern":
  "^[a-z][a-z0-9_]*$"}`, `additionalProperties: {"type": "string",
  "minLength": 1}`.
- Add `unresolved_issues`: array of objects, same required
  (`issue_id`/`kind`/`description`) and `kind` enum as
  `profile.schema.json`'s existing inline `unresolved_issues` property —
  copy verbatim for consistency.
- No changes to `task.schema.json` (already has `profile-writing` in the
  `task_type` enum; `inputs` is untyped `object`, so the new manifest shape
  needs no schema change there).

### 2. New module `src/tool_eval/research/profile_writing.py`
Mirrors `sources.py:create_source_task`'s shape and error handling:
- `DEFAULT_RELEASE_HISTORY_CAP = 10` module constant.
- `PROFILE_WRITING_TASK_ID = "profile-writing-01"`.
- `create_profile_writing_task(root: Path, run_id: str) -> dict[str, Any]`:
  - Requires the run to already have `merged/sources.json` and
    `merged/feature-results.json` (raise
    `INPUT_MERGED_ARTIFACT_MISSING`-style error otherwise, matching
    `build.py:_require_json`'s pattern — i.e. this command is only callable
    after `research merge`, matching where the stuck run already is).
  - Requires `tool.json` (tool identity) to exist (raise
    `INPUT_TOOL_IDENTITY_MISSING` otherwise, matching `build.py:_resolve_tool`).
  - Reads `data/profiles/<tool_id>/profile.json` if present to get
    `research.researched_at` for the `since_date` cap; otherwise builds the
    `most_recent` directive.
  - Reads `profile-sections.yaml` (`sections` list) and
    `additional-fact-sections.yaml` (`sections` list) from the config bundle
    and inlines both into `inputs`.
  - Projects the accepted source registry the same way `tasks.py:_known_sources`
    does. Promote that helper (rename, drop the leading underscore) into
    `sources.py` as `project_known_sources(run_dir)` so both `tasks.py` and
    `profile_writing.py` import one shared implementation instead of
    duplicating it — `tasks.py`'s current private copy becomes a thin call
    to the shared function; no behavior change for feature-research tasks.
  - Inlines the merged `feature_results` array so the worker can ground
    descriptive prose in verified statuses.
  - Writes `task.json` + `input.json` under
    `tasks/profile-writing-01/`, schema-validated the same way
    `create_source_task` validates its manifest.
  - `transition(record, "profile_writing_in_progress", detail=f"tool={tool_id}")`.
  - Returns `{run_id, tool_id, task_id, manifest_path}`.

### 3. CLI wiring (`src/tool_eval/cli.py`)
- Import `create_profile_writing_task`.
- `cmd_research_create_profile_writing_task(args)` → calls it, returns the
  standard envelope, `code="PROFILE_WRITING_TASK_CREATED"`, `next_action`
  telling the orchestrator to delegate the task to a worker and then run
  `validate-task` before `build-profile`.
- New subparser: `research create-profile-writing-task <run_id>` (positional
  `run_id`, same shape as `create-source-task`).

### 4. `src/tool_eval/profiles/build.py`
- Extend `_collect_content`'s `_absorb`/return value with a fifth key,
  `description_sections: dict[str, str]` (first-task-wins on a duplicate
  section id across profile-writing task results, consistent with the
  existing `setdefault`-based dedup for facts/use_cases — in practice exactly
  one profile-writing task is ever created per run, so this only matters for
  determinism, not real conflict resolution).
- Change `_load_section_texts`'s priority order to:
  1. explicit `--sections` file (unchanged — operator/test override),
  2. `run_dir/description-sections.json` if present (unchanged — manual
     back-compat path),
  3. **new:** the `description_sections` collected from the run's
     profile-writing task result(s),
  4. else raise `INPUT_DESCRIPTION_SECTIONS_MISSING` (unchanged).
- Thread `content["description_sections"]` from `_collect_content` into
  `_load_section_texts` (single scan of `tasks/`, no second directory walk).

### 5. Worker contract (`.claude/agents/tool-eval-worker.md`)
Expand "Profile-writing tasks" (~line 95) with:
- A **"Description sections"** subsection: for each entry in the manifest's
  `sections` list, write Markdown prose into `description_sections[id]` in
  the same `result.json`; every section marked `required` in the manifest
  must get non-empty prose; optional sections only when there's real
  grounded material — omit rather than pad; never emit a section id absent
  from the manifest's list (rejected by `build.py`/schema). Every substantive
  claim should trace back to the `feature_results`/sources/facts already
  inlined in the manifest — this is a synthesis pass over already-researched
  material, not new invention, though `WebFetch`/`WebSearch` may still be used
  for gaps under the same official-sources-only and source-reuse-before-search
  rules as any other task.
- Concrete `unresolved_issues` guidance now that the schema accepts it: when
  to raise one (`kind`: `conflict`/`access_gap`/`coverage_gap`/
  `prompt_injection_warning`/`other`), and that it's optional, not required
  per task.
- Replace the vague "manifest's stated number of most-recent releases" line
  with the concrete `release_history.mode`/`since_date`/`max_items` directive
  from D3.

### 6. `SKILL.md` (`.claude/skills/tool-eval-orchestration/SKILL.md`)
- Step 5: add the explicit CLI call
  `python -m tool_eval research create-profile-writing-task <run_id>` before
  "Delegate a profile-writing task...".
- Remove/correct the "candidate features" phrase (root cause 5) — candidates
  already come from feature-research merge.
- State explicitly that profile-writing results feed `build-profile` directly
  (no `research merge` step for this task type — D6).

### 7. Tests — new `tests/test_item12_profile_writing.py`
- `create_profile_writing_task` happy path: manifest written, schema-valid,
  `since_date` mode populated correctly when a prior published profile
  exists for the tool_id (build a fixture profile under `data/profiles/...`
  first), `most_recent` mode with the default cap otherwise.
- Error path: calling it before `merge` (no `merged/feature-results.json`)
  raises the expected `ToolEvalError` code.
- `subagent-result` schema now accepts a payload carrying both
  `description_sections` and `unresolved_issues` together with
  `task_type: "profile-writing"`; rejects an unknown section id under
  `description_sections` only at the `assemble_description` layer (schema
  itself doesn't know section ids — confirm existing
  `VALIDATION_UNKNOWN_SECTION` test in `test_item4_description.py` still
  covers that; no new schema-level test needed there beyond structural
  acceptance).
- End-to-end: extend the existing `_drive_to_merged` flow
  (`test_item10_source_build.py`'s helper, or a local equivalent) one step
  further — after merge, call `create_profile_writing_task`, write a worker
  result containing `description_sections` for the required sections plus
  `additional_facts`/`use_cases`/`release_history`/`unresolved_issues`, then
  call `build_profile` **without** `--sections`/`--content` and assert it
  builds successfully purely from the profile-writing task result (this is
  the regression test that proves the production path — as opposed to the
  existing tests, which only exercise the manual-file override path).

## Standards Compliance Checklist

- [ ] New CLI command follows the single-JSON-envelope contract and the
      `research <verb>` naming/argument pattern (`standards/backend/api.md`).
- [ ] `create_profile_writing_task` stays a deterministic IO wrapper around
      pure data assembly; it performs no model/LLM/web calls
      (`standards/global/architecture.md`).
- [ ] All new/changed JSON Schema files keep `additionalProperties: false`
      and lowercase-ASCII, pattern-constrained identifiers
      (`standards/global/validation.md`, D-016).
- [ ] Worker doc changes preserve official-sources-only, source-reuse-before-search,
      and untrusted-content rules; no relaxation of the not-found protocol
      (`standards/global/research-protocol.md`, `standards/global/security.md`).
- [ ] Worker isolation preserved: the worker still writes exactly one file
      inside its own task directory (`standards/global/security.md`).
- [ ] New test file named `test_item12_profile_writing.py`
      (`standards/testing/test-writing.md`).
- [ ] No speculative config knobs added (`DEFAULT_RELEASE_HISTORY_CAP` is a
      constant, not a new `runtime.yaml` key) (`standards/global/minimal-implementation.md`).
- [ ] `sources.py:project_known_sources` extraction removes duplication
      without adding a new abstraction layer beyond what two call sites need.

## Unblocking the stuck run

Once the above lands, resume `research-20260725-092106-96b31f5c` from its
current `merged` state (no feature research needs to be repeated):
1. `python -m tool_eval research create-profile-writing-task research-20260725-092106-96b31f5c`
2. Delegate the resulting task to a `tool-eval-worker`.
3. `python -m tool_eval research validate-task research-20260725-092106-96b31f5c profile-writing-01`
4. `python -m tool_eval research build-profile research-20260725-092106-96b31f5c`
5. Continue with curation / publish as normal.

## Explicitly out of scope (belongs to the parallel research task)

`.flowbit/tasks/research/2026-07-25-expand-single-tool-report/analysis/synthesis.md`
identifies two related-but-separate structural questions this plan does not
touch: (a) `additional_facts`/`use_cases` have no curation gate and
`additional-fact.schema.json` doesn't enforce `evidence` the way
`use-case.schema.json` does for `kind: documented`; (b) `use_cases` schema
fields (`rationale`, `supporting_features`, full `evidence`) exceed what the
comparison template renders. Both are candidates for a future
`/flowbit-standards-update` / schema-hardening pass, independent of making
`profile-writing` functional at all.
