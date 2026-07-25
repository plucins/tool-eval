# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

**tool-eval** — the AI Coding Tool Comparison System. A CLI that researches, profiles, and compares AI coding tools on demand.

Core design principle: a strict split of responsibilities.
- The **Python core is deterministic and offline** — it validates, merges, and publishes data but never calls a model or the network.
- All **LLM reasoning is delegated to the external agent harness** under `.claude/`.

## Coding Standards & Conventions

Read `.flowbit/docs/INDEX.md` before starting any task. It indexes the project's coding standards and conventions:
- Coding standards organized by domain (global, backend, testing).
- Project vision, tech stack, and architecture decisions (`.flowbit/docs/project/`).

Follow the standards in `.flowbit/docs/standards/` when writing code — they represent team decisions. If a standard conflicts with the task, ask the user.

Key standards to be aware of:
- **Global**: error handling (structured `ToolEvalError` codes, `<FAMILY>_<REASON>`), validation (JSON Schema is the source of truth), conventions, coding style (fully typed public surface), commenting, minimal implementation (YAGNI), architecture (deterministic core, no model/LLM/web calls), security (untrusted-source/prompt-injection handling, sanitized self-contained HTML, worker isolation), research protocol (single curation gate, no source voting).
- **Backend**: API design (single-JSON-envelope CLI contract via `python -m tool_eval`), run lifecycle & publication, models, queries, migrations.
- **Testing**: deterministic offline pytest (`test_item{N}_{feature}.py`, `tests/conftest.py`).

### Standards Evolution

When you notice recurring patterns, fixes, or conventions during implementation that are not yet captured in standards, suggest adding them. Examples:
- A bug fix reveals a pattern that should be standardized (e.g. "always validate X before Y").
- PR review feedback identifies a convention the team wants enforced.
- The same type of fix is needed across multiple files.
- A new library/pattern is adopted that should be documented.

When this happens, briefly suggest the standard to the user. If approved, invoke `/flowbit-standards-update` with the identified pattern.

## Flowbit Workflows

This project uses the flowbit plugin for structured development workflows. When any `/flowbit-*` command is invoked, execute it via the Skill tool immediately — do not skip workflows for "straightforward" tasks. The user chose the workflow intentionally; complexity assessment is the workflow's job.

## Tech Stack

- **Language**: Python >= 3.11 (`from __future__ import annotations`, PEP 604 unions, frozen dataclasses, `pathlib`).
- **CLI**: standard-library `argparse` with grouped subcommands (`config`, `run`, `research`, `profile`, `compare`, `work`), each emitting a single JSON envelope to stdout.
- **Dependencies**: `PyYAML`, `jsonschema`, `Jinja2`, `markdown-it-py`, `nh3` (HTML sanitization).
- **Build**: `hatchling`, src-layout (`packages = ["src/tool_eval"]`). JSON schemas, templates, and static assets are force-included as package data.
- **Testing**: `pytest` (offline, fixture-based; isolated temp project trees via `conftest.py`).
- **No database, no web framework, no containers.** State is persisted as files: JSON Schemas under `validation/schemas/`, revisioned YAML under `config/`, artifacts under `data/`, runtime state under `.work/runs`.

## Layout

```
src/tool_eval/
  cli.py, __main__.py, errors.py, paths.py
  config/       config loading
  research/     planner, tasks, sources, pipeline, curation, merge, repair
  profiles/     build, validate, description, publication
  comparison/   builder, flags, freshness, loader, model
  reporting/    html, markdown, assets (+ templates/, static/)
  runs/         manager, retention
  validation/   schema, business (+ schemas/)
tests/          pytest suite + conftest.py
config/         revisioned YAML configuration
data/           generated JSON/Markdown artifacts
```

## Commands

This repository ships its own virtual environment at `.venv/` — there is no
`activate` script in it, so `source .venv/bin/activate` will fail. Always
invoke the interpreter directly from the repository root:

```bash
.venv/bin/python -m tool_eval ...   # canonical CLI entry (or `.venv/bin/tool-eval ...`)
.venv/bin/pytest                    # run the offline test suite
```

Do not use a bare `python`/`python3` (may be missing or the wrong version) and
do not try to activate the venv. Before guessing flags, check
`.venv/bin/python -m tool_eval <subcommand> -h` — the CLI contract is a single
JSON envelope per call; it does not accept ad-hoc flags.

If `.venv/` is ever missing or broken, recreate it:

```bash
pip install -e ".[dev]"
```

