# tool-eval — AI Coding Tool Comparison System

Research, document, and compare AI coding tools on demand, using Claude Code
as the agent harness. See `docs/ai_coding_tool_comparison_system_requirements_v2.md`
for the product requirements and `docs/implementation_plan_v1.md` for the
architecture and work plan.

**Status:** Increments 2–4 implemented. The full research pipeline — profile
model, bundle planning, D-009 protocol enforcement, curation, deterministic
merge, bounded retries/repairs, failed-run handling, and staged profile
publication with rollback/recovery — is in place and unit-tested. Comparison and
self-contained HTML (Increment 3) are implemented: `compare build` produces a
single offline, Capgemini-themed HTML report with deterministic freshness and
flags, embedded assets (no CDN), and no execution of profile data as code.
Operations and documentation (Increment 4) add configurable run budgets
(`config/runtime.yaml: budgets`), cleanup/retention, publication recovery, and a
full operator guide.

**New here? Read the [User Guide](docs/user-guide.md)** — install, starting the
orchestrator, the three entry skills, sample sessions, and troubleshooting.

## Installation

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -e .

# For development (test suite):
pip install -e ".[dev]"
```

Requires Python 3.11+. No API key or model-provider SDK is required — all
LLM reasoning is performed by the Claude Code harness. Python is deterministic
only: it validates, merges, and publishes, but never calls a model or the web.

## CLI

Every command prints a single JSON envelope to stdout
(`status`, `code`, `run_id`, `next_action`, `artifacts`, `errors`); logs go to
stderr. See `docs/implementation_plan_v1.md` Sec 3.5 for the full surface.

```bash
# Configuration and run lifecycle
python -m tool_eval config validate
python -m tool_eval run init research
python -m tool_eval run status <run_id>
python -m tool_eval run resume-check <run_id>
python -m tool_eval run fail <run_id> "<reason>"

# Research pipeline (Increment 2)
python -m tool_eval research create-feature-tasks <run_id> [--isolate <feature_id>]
python -m tool_eval research merge <run_id>
python -m tool_eval research curate-candidates <run_id> <decisions.json>
python -m tool_eval research prepare-repair <run_id> [--feature-id <feature_id>]

# Profiles
python -m tool_eval profile validate <profile.json> [--check-completeness]
python -m tool_eval profile publish <run_id> <tool_id> [--check-completeness]
python -m tool_eval profile list

# Comparison (Increment 3): one self-contained offline HTML report
python -m tool_eval compare build --tools <tool_id> <tool_id> [<tool_id>...] [--out <file.html>]

# Maintenance
python -m tool_eval work recover   # restore an interrupted publication
python -m tool_eval work cleanup   # apply failed-run retention
```

Data contracts live as JSON Schemas under `src/tool_eval/validation/schemas/`
(the source of truth per D-016); status-dependent and cross-record rules are
enforced by the business validator in `src/tool_eval/validation/business.py`.

## Tests

```bash
python -m pytest -q
```

The suite is deterministic and offline; worker/LLM research is exercised with
fixture JSON, never live calls.
