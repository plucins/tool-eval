## Architecture Principles

### Deterministic Python Core
The Python codebase performs only deterministic work — validation, merging, calculation, rendering, state management, and publication. It never calls a model API, performs LLM reasoning, or conducts web research; all such work belongs to the agent harness. Source: README.md, docs/implementation_plan_v1.md.

### Harness-Portability Boundaries
Domain logic, data contracts, configuration, and schemas must not depend on any single agent-harness API. Harness-specific files are thin adapters; shared workflow instructions are harness-neutral Markdown, and data/config/schemas are identical regardless of harness. Invoke shared logic through `python -m tool_eval`. Source: docs/implementation_plan_v1.md.

### Pure Logic Behind IO Wrappers
Separate deterministic pure functions from filesystem/run orchestration. Pure logic (e.g., `research/merge.py`, `research/planner.py`, `validation/business.py`) is testable without a filesystem; companion IO wrappers (`research/pipeline.py`, `research/tasks.py`, `validation/schema.py`) handle reads/writes.

### Cross-Platform Python & Pathlib
Support Python 3.11+ on Windows, Linux, and macOS. Do not depend on PowerShell or Bash; use `pathlib` and safe process invocation (`shell=False`). `venv` + `pip` is the guaranteed install path; packaging metadata lives in `pyproject.toml`. Source: README.md, docs/implementation_plan_v1.md, pyproject.toml.

### Packaging Conventions
Build with the hatchling backend (PEP 517). Use a src-layout package rooted at `src/tool_eval`. Validation schemas under `src/tool_eval/validation/schemas` are package data and must be force-included in built wheels so they ship with the distribution. Source: pyproject.toml.
