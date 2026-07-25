# tool-eval User Guide

**Audience:** operators who research, profile, and compare AI coding tools with
tool-eval. No prior knowledge of the internals is assumed.

tool-eval is a repository of Claude Code skills, agents, and a deterministic
Python core. Claude does all research and writing; Python validates, merges,
and publishes the results. **No API key or model-provider SDK is required** —
all LLM work runs inside the Claude Code harness.

---

## 1. Prerequisites and installation

You need **Python 3.11 or later** and **Claude Code**. tool-eval runs on
Windows, Linux, and macOS. It does not depend on PowerShell, Bash, Node.js, or
any network service at runtime.

### 1.1 Create a virtual environment and install

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

For the test suite, install the dev extras instead: `pip install -e ".[dev]"`.
`uv` may be used as an optional accelerator (`uv venv` / `uv pip install -e .`)
but is not required.

### 1.2 Verify the installation

```bash
python -m tool_eval config validate
```

A healthy install prints a single JSON envelope with `"code": "CONFIG_VALID"`.
If you see `CONFIG_MISSING_FILE`, `CONFIG_INVALID_YAML`, or
`CONFIG_MISSING_REVISION`, fix the reported file under `config/` before
continuing (see [Troubleshooting](#8-troubleshooting)).

---

## 2. Starting the orchestrator

All operations run inside a Claude Code session led by the orchestrator agent:

```bash
claude --agent tool-eval-orchestrator
```

The orchestrator owns the run end to end: it validates configuration, drives the
Python CLI, delegates isolated research tasks to `tool-eval-worker` subagents,
runs the single curation gate, manages the bounded retry/repair loop, and
triggers publication. You interact with it through the three entry skills below.

---

## 3. Entry skills

You never call the Python CLI by hand. You invoke one of three skills; the
orchestrator selects the deterministic commands for you.

### 3.1 `/tool-eval-research <tool_name>`

Research one tool and publish its profile.

- **Argument:** exactly one tool name, e.g. `cursor`, `devin`. The CLI
  normalizes it to a lowercase-ASCII-and-underscores `tool_id`.
- **Flow:** config validate → run init → source discovery → feature research via
  isolated workers → merge → **single curation gate** → research any accepted
  features → build → validate (≤3 repair rounds) → publish.
- **Output:** a final envelope with the `run_id`, the published profile artifacts
  (`data/profiles/<tool_id>/profile.json` and `description.md`), and any
  warnings.
- **Guarantees:** research pauses at exactly one curation point; an invalid or
  incomplete profile is never published; a failed run leaves any existing
  profile and its date untouched.

### 3.2 `/tool-eval-compare <tool_id> <tool_id> [<tool_id>...]`

Build a single self-contained, offline HTML comparison of two or more tools that
already have published profiles. **Comparison never starts research or workers.**

- **Argument:** two or more `tool_id`s, each with a published active profile.
- **Flow:** resolve tools → copy active profiles into the comparison run →
  validate profiles/revisions/dates → compute deterministic freshness and flags
  → render sanitized Markdown into the template with bundled assets → publish one
  file under `outputs/comparisons/`.
- **Output:** the path to the HTML report, plus any warnings.
- **Guarantees:** a missing profile for a requested tool is an **error**; an old
  revision or a stale date is a **warning**, not a failure. `requires_research`
  profiles are allowed with a warning and their unresearched cells are excluded
  from flags.

### 3.3 `/tool-eval-resume <run_id>`

Safely resume an interrupted run.

- **Argument:** the `run_id` of a previously created run, e.g.
  `research-20260724-053608-3e810720`.
- **Flow:** runs `run resume-check`. If the run's frozen configuration revisions
  still match the current configuration (`RUN_RESUMABLE`), the run continues from
  its recorded state. If they have changed (`CONFIG_REVISION_MISMATCH`), resume
  is refused.
- **Guarantees:** a controlled taxonomy revision bump recorded inside the run
  (from curation) does not block resume; any other configuration change does. A
  failed or unresumable run never alters an existing profile.

---

## 4. Reading command results

Every Python command the orchestrator runs prints exactly one JSON envelope:

```json
{"status": "ok", "code": "PROFILE_PUBLISHED", "run_id": "research-...",
 "next_action": "Active profile replaced at ...", "artifacts": ["..."], "errors": []}
```

- `status` — `ok` or `error`.
- `code` — a stable `<FAMILY>_<REASON>` code (families: `CONFIG`, `INPUT`,
  `HARNESS`, `RESEARCH`, `VALIDATION`, `BUDGET`, `PUBLISH`).
- `next_action` — the recommended next step.
- `artifacts` — paths or JSON payloads produced.
- `errors` — structured error records when `status` is `error`.

Common success codes: `CONFIG_VALID`, `RUN_INITIALIZED`, `SOURCES_ACCEPTED`,
`FEATURE_TASKS_CREATED`, `MERGE_COMPLETE`, `CANDIDATES_CURATED`, `PROFILE_BUILT`,
`PROFILE_PUBLISHED`, `COMPARISON_BUILT`, `RECOVERY_COMPLETE`, `CLEANUP_COMPLETE`.

---

## 5. Sample sessions

### 5.1 Research with curation

```
claude --agent tool-eval-orchestrator
> /tool-eval-research cursor
```

The orchestrator researches the taxonomy and pauses at the curation gate,
presenting every candidate feature it discovered. You respond with a decision per
candidate:

- **accept** — the feature is added to the taxonomy (its revision increments),
  it is researched for the current tool before publishing, and every other
  profile is marked `requires_research`;
- **reject** — the candidate is discarded (recorded in
  `data/feature-candidates/rejected.json`);
- **defer** — the candidate moves to the waiting room
  (`data/feature-candidates/pending.json`) for a later decision.

After curation the orchestrator finishes research, builds the profile, validates
it (repairing up to three times if needed), and publishes it. The final envelope
reports `PROFILE_PUBLISHED` and the two profile files.

### 5.2 A controlled failure preserves the old profile

If a run cannot complete (budget exceeded, unresolved validation after three
repair rounds, or an operator-triggered stop), the orchestrator records the
failure:

- the run is moved to `.work/failed-runs/<run_id>/` with a `report.json`;
- the **active profile and its date are untouched**;
- if publication was interrupted mid-replacement, the next run restores the
  previous profile automatically (see [recovery](#71-recovery-and-cleanup)).

### 5.3 Resume

```
> /tool-eval-resume research-20260724-053608-3e810720
```

- `RUN_RESUMABLE` → the run continues where it stopped; completed tasks are not
  repeated.
- `CONFIG_REVISION_MISMATCH` → resume is refused because the taxonomy, schema, or
  policy revisions changed since the run started. Start a fresh
  `/tool-eval-research` run instead so incompatible data is never mixed.

### 5.4 Comparison

```
> /tool-eval-compare cursor devin copilot claude_code
```

Produces one self-contained HTML file under `outputs/comparisons/`. Open it
directly in a current version of Chrome, Edge, Firefox, or Safari — it works
fully offline with no network access.

---

## 6. Directory reference

| Path | Contents |
|---|---|
| `data/profiles/<tool_id>/` | The active profile: `profile.json` (machine-readable) + `description.md` (semantic description). |
| `data/feature-candidates/` | `pending.json` (deferred candidates / waiting room) and `rejected.json`. |
| `outputs/comparisons/` | Generated self-contained HTML comparison reports. |
| `.work/runs/<run_id>/` | State of an active run: `run.json`, frozen config, task manifests/results, merged data, staged `publish/`. |
| `.work/failed-runs/<run_id>/` | Retained post-mortem of a permanently failed run (report, run data, validation errors, artifacts — never full page copies). |
| `config/` | Manually edited YAML configuration (taxonomy, source policies, freshness, runtime limits, presentation). |

`.work/` is transient and Git-ignored. Profiles, configuration, and accepted
taxonomy changes are persistent.

---

## 7. Interpreting results

### 7.1 Feature statuses

| Presentation label | Meaning |
|---|---|
| `Has` | The tool implements the feature, backed by an official source. |
| `Partial` | Partially implemented or conditional, backed by an official source. |
| `Not found` | No official source confirms the feature **and** the full not-found protocol completed (all relevant source classes checked, no errors, no conflicts). |
| `Uncertain / disputed` | Research was incomplete, a material source was unavailable, or sources conflicted. Never silently downgraded to `Not found`. |

### 7.2 Constraints, freshness, and warnings

- **Constraints** are structured, source-backed limitations shown with their
  evidence in the report.
- **Freshness** is computed from each profile's UTC research date against the
  thresholds in `config/freshness.yaml`; the comparison also shows the **date
  spread** across the compared profiles.
- **Warnings** (attached as `INPUT_COMPARE_WARNING` records) flag stale dates,
  old revisions, or `requires_research` profiles. They do not stop a comparison;
  unresearched cells are simply excluded from flags.

---

## 8. Troubleshooting

| Symptom / code | Cause | What to do |
|---|---|---|
| `CONFIG_MISSING_FILE`, `CONFIG_INVALID_YAML`, `CONFIG_MISSING_REVISION`, `CONFIG_INVALID_SHAPE` | A file under `config/` is missing, malformed, or missing its integer `revision`. | Fix the reported file; re-run `config validate`. |
| `CONFIG_REVISION_MISMATCH` (on resume) | Taxonomy/schema/policy revisions changed since the run started. | Do not resume; start a new research run. |
| `BUDGET_TASKS_EXCEEDED` | The run would delegate more worker tasks than `budgets.max_worker_tasks` in `config/runtime.yaml`. | Fail the run (do not retry). Narrow scope, or raise the budget deliberately and start a new run. |
| `VALIDATION_REPAIR_LIMIT_EXCEEDED` | A profile was still invalid after the maximum repair rounds (default 3). | The run must be failed; inspect `validation-errors.json` under the run directory. |
| `VALIDATION_INCOMPLETE_MERGE` | Features have gaps or duplicate results. | Repair the flagged features and re-merge. |
| `PUBLISH_STAGING_INCOMPLETE` / `PUBLISH_VALIDATION_FAILED` | The staged profile is missing files or failed validation. | The active profile is untouched; rebuild and re-validate before publishing. |
| `PUBLISH_REPLACE_FAILED` | Publication failed mid-replacement and rolled back. | Run `work recover` (below) to confirm the previous profile is intact. |
| An interrupted session left a half-written profile | Publication was interrupted. | The next run auto-recovers; you can also run recovery manually (below). |

### 8.1 Recovery and cleanup

These maintenance operations are deterministic and safe to run any time:

```bash
python -m tool_eval work recover   # restore any interrupted publication
python -m tool_eval work cleanup   # apply failed-run retention
```

- **recover** reads the publication journal; if the active profile is complete it
  clears the stale journal, otherwise it restores the technical backup.
- **cleanup** removes failed runs older than `failed_run_retention.max_age_days`
  (default 30) or beyond `failed_run_retention.max_count` (default 20), keeping
  the newest. Both limits are configurable in `config/runtime.yaml`.

### 8.2 Tuning budgets

`config/runtime.yaml` holds the run budgets:

```yaml
budgets:
  max_worker_tasks: 40      # total delegated research tasks per run
  max_technical_retries: 2  # per-task technical retries (standard cap: 2)
  max_repair_rounds: 3      # profile repair rounds (standard cap: 3)
```

Budgets are frozen into each run at initialization, so changing them affects only
**new** runs, never a resumed one. `max_technical_retries` and
`max_repair_rounds` are also the standard's hard upper bounds and should not be
raised above 2 and 3.

---

## 9. MVP limitations

The current release deliberately excludes the following (tracked for after the
MVP; see `docs/implementation_plan_v1.md` §4.2):

- harnesses other than Claude Code (Codex CLI, GitHub Copilot CLI, adapter
  generator);
- direct LLM API access;
- a crawler, local corpus, page archive, BM25, embeddings, or vector database —
  research uses the harness's web tools, and full source pages are not stored;
- any web application, hosting, backend, or telemetry;
- profile and source history (successful history is not retained);
- Node.js as a mandatory dependency;
- internationalization — the system is English-only;
- PDF export;
- effectiveness benchmarks.

Because tool-eval runs on demand, profiles do not refresh automatically. Re-run
`/tool-eval-research <tool>` when freshness warnings appear.
