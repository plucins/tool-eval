# Implementation Plan — AI Coding Tool Comparison System

**Version:** 1.1
**Status:** ready to begin MVP implementation
**Date:** July 13, 2026
**Source document:** `ai_coding_tool_comparison_system_requirements_v2.md`

## Table of Contents

1. [Purpose of the plan](#1-purpose-of-the-plan)
2. [Adopted decisions](#2-adopted-decisions)
3. [Target MVP architecture](#3-target-mvp-architecture)
   - [3.1 Responsibility flow](#31-responsibility-flow)
   - [3.2 Components](#32-components)
   - [3.3 Repository structure](#33-repository-structure)
   - [3.4 Run artifacts](#34-run-artifacts)
   - [3.5 User skills and internal CLI](#35-user-skills-and-internal-cli)
   - [3.6 `/tool-eval-research` skill workflow](#36-tool-eval-research-skill-workflow)
   - [3.7 `/tool-eval-compare` skill workflow](#37-tool-eval-compare-skill-workflow)
4. [MVP scope and deferrals](#4-mvp-scope-and-deferrals)
5. [Work plan](#5-work-plan)
   - [Increment 1 — project foundation](#increment-1--project-foundation)
   - [Increment 2 — complete tool research](#increment-2--complete-tool-research)
   - [Increment 3 — comparison and self-contained HTML](#increment-3--comparison-and-self-contained-html)
   - [Increment 4 — operations and documentation](#increment-4--operations-and-documentation)
   - [Increment 5 — manual MVP acceptance](#increment-5--manual-mvp-acceptance)
   - [Dependencies between increments](#dependencies-between-increments)
6. [Risks and mitigations](#6-risks-and-mitigations)
7. [Stage 1 acceptance-criteria coverage matrix](#7-stage-1-acceptance-criteria-coverage-matrix)
8. [Implementation start and completion conditions](#8-implementation-start-and-completion-conditions)

## 1. Purpose of the plan

This plan describes the architecture, data contracts, components, work sequence, MVP constraints, risks, and Stage 1 completion criteria. The decision log retains the rationale and deliberate deferrals agreed during the design session.

## 2. Adopted decisions

### D-001 — Portability across agent harnesses

**Status:** adopted
**Decision:** the solution will be a repository-based collection of skills, agent definitions, and Python scripts executable by different agent harnesses, especially Claude Code, Codex CLI, and GitHub Copilot CLI.

**Consequences:**

- domain and deterministic logic must not depend on a single harness API;
- shared workflow instructions will be maintained as harness-neutral Markdown files;
- harness-specific elements will be thin adapters;
- Python scripts will expose a stable CLI and machine-readable results;
- data, configuration, and schemas will remain identical regardless of harness;
- core contracts will remain LLM-independent, allowing adapters for other harnesses to be added after the MVP without redesigning the data model.

**MVP scope:** the first version integrates only with Claude Code. Codex CLI and GitHub Copilot CLI remain target portability directions after the MVP stabilizes.

### D-002 — Harness-provided LLM

**Status:** adopted
**Decision:** the system does not call model APIs directly. All LLM reasoning is performed by the model exposed by the harness. Installation requires neither an API key nor a model-provider SDK.

### D-003 — The agent invokes Python scripts as needed

**Status:** adopted
**Decision:** the user directly invokes a high-level operation skill, such as `/tool-eval-research X` or `/tool-eval-compare A B`. The agent selects domain skills and invokes Python scripts whenever deterministic operations are required. Scripts are internal agent tools, not steps performed manually by the operator.

The canonical scripting interface will be `python -m tool_eval <command>`. Larger data sets will be exchanged through JSON files in an isolated run directory. Python maintains state and enforces mandatory gates, so the agent cannot skip validation, the repair limit, or safe publication through staging, rollback, and recovery.

### D-004 — Lead agent and subagents

**Status:** adopted
**Decision:** an entry skill runs in the lead agent's session. The lead agent uses domain skills, invokes scripts, and delegates independent work to subagents. A harness with subagent support is assumed.

The minimum set of agent definitions is:

- `tool-eval-orchestrator` — lead agent, owner of the run and curation point;
- `tool-eval-worker` — generic subagent specialized by a task manifest and a specified skill.

Subagents may concurrently discover source classes, research disjoint feature bundles, extract facts, and repair independent records. They do not modify the taxonomy, main manifest, or active profile. Merging, full validation, curation, flags, comparison, and publication remain single-writer operations. Python is the only layer that writes persistent data.

### D-005 — LLM-based research

**Status:** adopted
**Decision:** in Stage 1, all research—source discovery, content browsing, semantic search, and interpretation—is performed by the agent and subagents using the harness's web tools.

In Stage 1, Python does not implement a crawler, local corpus, BM25, embeddings, or a vector database. It is responsible for run state, contract preparation, validation, search-trace completeness, merging, revisions, flags, freshness, HTML, and safe publication. Local retrieval and indexing remain possible extensions if the pilot reveals issues with scale, cost, or completeness.

### D-006 — Scope of retained source data

**Status:** adopted
**Decision:** the system does not store complete copies of pages, HTML, PDFs, or screenshots. It stores the URL, title, source type, checked-at date, availability and redirect information, and a short evidence excerpt required for `has` and `partial` statuses. Negative results contain a structured search trace.

### D-007 — Hybrid tool profile

**Status:** adopted
**Decision:** the active tool profile is a safely published set:

```text
data/profiles/<tool_id>/
├── profile.json
└── description.md
```

`profile.json` is the machine-readable source for metadata, revisions, features, constraints, evidence, search traces, additional facts, and use cases. `description.md` contains an LLM-generated semantic description. HTML renders Markdown safely, while tables and flags are generated from JSON. Markdown may reference evidence through stable identifiers.

### D-008 — Platforms and Python environment

**Status:** adopted
**Decision:** the system supports Python 3.11 or later on Windows, Linux, and macOS. The package uses `pyproject.toml`; `venv` and `pip` are the guaranteed installation method, while `uv` may be an optional accelerator.

The code does not depend on PowerShell or Bash. It uses `pathlib` and safe process invocation. Architecture and file operations must be portable across Windows, Linux, and macOS.

### D-009 — Complete protocol for `not_found`

**Status:** adopted
**Decision:** because Stage 1 does not maintain a local corpus, the corpus is a logical registry of official sources checked by agents. The `not_found` status is permitted only after a complete, auditable protocol has been executed.

The source agent identifies official domains and available source classes: documentation, product pages, changelog or release notes, pricing and licensing, integration documentation, and specialist sources appropriate to the tool.

A subagent researching a feature performs:

1. a search for the canonical name, aliases, and synonyms from the taxonomy;
2. a search for alternative formulations generated from the feature definition;
3. targeted queries restricted to official domains;
4. opening and evaluating potential matches;
5. recording queries, checked source classes, visited URLs, date, access gaps, and reasons for rejecting matches.

The `not_found` status requires all of the following:

- all relevant source classes were checked;
- no errors prevented a material part of the research;
- no unresolved conflicts remain;
- no source confirms full or partial implementation;
- `protocol_complete: true`;
- successful Python validation of checklist completeness.

An unavailable material source, tool failure, or incomplete research results in `uncertain`, never `not_found`. The protocol does not impose an artificial minimum query count; it requires strategy and source coverage.

### D-010 — Feature bundles and concurrency

**Status:** adopted
**Decision:** the lead agent delegates independent tasks in a single subagent layer. The default limit is four concurrent subagents, is configurable, and cannot exceed harness capacity.

Planning rules:

- a typical bundle contains two to four related features from the same group;
- a complex, disputed, or especially expensive feature receives its own task;
- each feature returns a separate JSON record, even when part of a bundle;
- subagents do not delegate to further subagents;
- source discovery may run concurrently across disjoint source classes;
- after an error, the bundle is retried and, if the problem repeats, split into individual features;
- the lead agent waits for every mandatory task before merging;
- exceeding a hard time or work budget stops the run and does not publish an incomplete profile;
- `/tool-eval-compare` does not use subagents because its work is deterministic.

Specific limits for time, search count, and work size will be calibrated after a pilot involving two or three tools.

### D-011 — Errors, retries, and resume

**Status:** adopted
**Decision:** errors have structured codes from the `CONFIG_*`, `INPUT_*`, `HARNESS_*`, `RESEARCH_*`, `VALIDATION_*`, `BUDGET_*`, and `PUBLISH_*` families. An error record contains the stage, message, `retryable` field, optional `feature_id`, and data path.

Retry rules:

- a technical tool error allows at most two retries of the task;
- a structural or business-rule error allows at most three LLM repair rounds;
- the entire profile is validated after each repair round;
- invalid configuration, schema, revision, or a security violation terminates the run immediately;
- exceeding a budget terminates the run without retry;
- successfully completed tasks are not repeated.

An active run resides in `.work/runs/<run_id>/`. It may be resumed only when the current taxonomy, template, schema, and policies match the run's effective frozen state. Controlled acceptance of a new feature at the curation point updates the effective taxonomy revision and hash stored in the run; this is not treated as an external change invalidating resume. Any other configuration change requires a new run.

A permanently failed run is moved to:

```text
.work/failed-runs/<run_id>/
├── report.json
├── run.json
├── validation-errors.json
└── artifacts/
```

Artifacts contain task manifests, structured results, and the latest invalid records, but not complete page copies. Default retention is 30 days or the latest 20 failed runs and is configurable. A successful run removes its working directory only after publication is confirmed. A failed run never changes the active profile or its date.

### D-012 — Simplified profile publication

**Status:** adopted
**Decision:** the system runs locally and does not require continuous profile availability while a new version is generated. It does not use a `current.json` pointer, versioned publications, or locks for concurrent readers.

New `profile.json` and `description.md` files are created and fully validated in `.work/runs/<run_id>/publish/`. Only after success does Python replace `data/profiles/<tool_id>/`. During replacement, the previous directory is retained as a technical backup in the run directory; an error triggers rollback. The backup is removed after the successful write is confirmed.

An interrupted process may make the profile briefly unavailable. The next run detects an incomplete replacement and restores the previous directory. Successful profile history is not retained.

### D-013 — External libraries and self-contained HTML

**Status:** adopted
**Decision:** external Python, CSS, and JavaScript libraries are allowed when they simplify content generation or presentation. The resulting HTML must nevertheless remain self-contained: all required resources are stored locally and embedded in one file, with no CDN or Internet dependency during presentation.

Assumptions:

- HTML templates are generated with a template library;
- `description.md` is rendered with a Markdown library;
- output is sanitized and raw HTML in Markdown is disabled by default;
- Bootstrap is the baseline candidate for layout, cards, tabs, tooltips, and table styling;
- an additional table or filtering library is used only if a prototype demonstrates the need;
- library CSS, fonts, and JavaScript are bundled into the artifact;
- dependency versions are pinned and the project records their sources, licenses, and checksums;
- profile data is escaped, URLs are restricted to safe protocols, and the generator undergoes manual injection-case review before MVP release;
- primary content and tables are accessible without JavaScript, while tabs, filters, and interactions use JavaScript;
- current stable versions of Chrome, Edge, Firefox, and Safari are supported; legacy browsers and Internet Explorer are out of scope.

### D-014 — Minimal dependency stack

**Status:** adopted
**Decision:** the core Python runtime stack includes:

- `PyYAML` for YAML configuration, used only through `safe_load`;
- `jsonschema` for JSON Schema Draft 2020-12 validation;
- `Jinja2` for HTML templates with `autoescape` and `StrictUndefined`;
- `markdown-it-py` for CommonMark with raw HTML disabled;
- `nh3` for final sanitization of rendered content.

The standard library handles the CLI (`argparse`), JSON, paths and files, processes with `shell=False`, hashes, dates, identifiers, and logging. Initially, Pydantic, Click/Typer, Requests, a web framework, a database, and a crawler library are not added.

The presentation layer uses an exactly pinned Bootstrap 5.3.x version. Built CSS and `bootstrap.bundle.min.js` files are stored as project assets with their version, license, and SHA-256 hashes. Node.js, npm, and a CDN are not required. An additional table or filtering library may be added only after the prototype demonstrates a need.

The package build backend is `hatchling`. Library version ranges are constrained to the next major version; exact versions will be pinned after installation and main workflows are manually verified. The project maintains `THIRD_PARTY_NOTICES.md` and copies of licenses for bundled assets.

### D-015 — Claude Code integration and skill packaging

**Status:** adopted
**Decision:** Claude Code is the only MVP harness and handles research and all LLM tasks. The system defines a separate `tool-eval-orchestrator` agent, launched as the main Claude session agent with `claude --agent tool-eval-orchestrator`. It is not a subagent, so it can delegate concurrent tasks to `tool-eval-worker`.

Claude Code artifacts:

```text
.claude/
├── agents/
│   ├── tool-eval-orchestrator.md
│   └── tool-eval-worker.md
└── skills/
    ├── tool-eval-research/
    ├── tool-eval-compare/
    ├── tool-eval-resume/
    ├── tool-eval-orchestration/
    ├── source-discovery/
    ├── feature-research/
    ├── profile-writing/
    ├── profile-validation/
    └── comparison/
```

Instruction split:

- the orchestrator definition specifies its role, tools, permitted workers, and overarching responsibilities;
- `tool-eval-research`, `tool-eval-compare`, and `tool-eval-resume` are directly invoked entry skills that define operation arguments and hand control to the orchestration workflow;
- `tool-eval-orchestration/SKILL.md` describes phases, gates, delegation, curation, retries, and publication;
- the worker definition specifies isolation, how to read the task manifest, and the permitted write area;
- Python mechanically enforces state and the allowed transition order.

Each skill is a package and may contain:

```text
<skill>/
├── SKILL.md
├── references/
├── schemas/
├── examples/
└── scripts/
```

A schema or script used by only one skill belongs in that skill's directory. Shared logic remains in `src/tool_eval/` and is invoked through the stable `python -m tool_eval` CLI. Validators are not duplicated between skills. JSON Schema is the source of truth, and a validation command checks every item in `examples/` against the appropriate schema; in the MVP this check is run manually.

The MVP does not implement an adapter generator, symlinks, or Codex/Copilot integration. Instructions retain harness-neutral semantics where possible so that extracting adapters later does not require changes to the data contracts or Python code.

### D-016 — Profile model and system language

**Status:** adopted
**Decision:** `profile.json` has a partially normalized structure with the main sections `schema_version`, `tool`, `research`, `sources`, `feature_results`, `additional_facts`, `use_cases`, and `unresolved_issues`.

Sources are registered once at profile level and receive a stable `source_id`. Each feature result is a self-contained record with `feature_id`, `status`, `rationale`, `evidence`, `constraints`, `search_trace`, and optional conflict data. Evidence remains with the record it supports but references a source by `source_id`, avoiding duplicated URLs and metadata. The subagent-result schema uses the same feature-record format, so merging requires no semantic transformation.

Conventions:

- internal statuses are `has`, `partial`, `not_found`, and `uncertain`;
- stable identifiers use lowercase ASCII and underscores;
- timestamps use ISO 8601 and UTC;
- `schema_version` uses semantic versioning, while taxonomy and template revisions remain integers;
- schemas set `additionalProperties: false`;
- optional fields are omitted rather than stored as `null`, unless `null` has defined domain meaning;
- JSON Schema validates structure, types, and simple dependencies; the business validator handles status-dependent rules and referential integrity.

The implemented system uses English exclusively: field names, enums, identifiers, skills, prompts, validator messages, technical documentation, Markdown descriptions, and the HTML interface. Localization and translation files are not implemented. Presentation labels for statuses are `Has`, `Partial`, `Not found`, and `Uncertain / disputed`.

The `excerpt` field preserves the source's exact wording. If a source is not in English, the quotation is neither modified nor presented as a translation; all other descriptive fields remain in English. The MVP prefers official English-language sources.

### D-017 — Agent and research security

**Status:** adopted
**Decision:** all page content is untrusted research material. Instructions found in a source never modify the agent's task. Feature statuses may be based only on public official sources; other pages may only help locate an official source.

A research worker receives only the tools needed to read its manifest and skill, search and open pages, and write a result in its own task directory. It cannot execute arbitrary shell commands, modify configuration, schemas, or active profiles, publish results, or delegate further agents.

The orchestrator may invoke only the permitted worker, read state, run specified `python -m tool_eval` commands, conduct curation, and manage the repair loop. Only Python writes the active profile after successful validation.

Technical controls:

- paths from manifests are normalized and must remain within the run directory;
- profiles allow only `http` and `https` URLs without credentials;
- the agent neither downloads nor executes code found in sources;
- worker output passes JSON Schema and business-rule validation;
- unexpected fields, paths, identifiers, and revisions are rejected;
- potential prompt injection is ignored and recorded as a warning;
- secrets, environment variables, and local user data never enter the profile or HTML;
- manual MVP security review covers malicious Markdown, URLs, source excerpts, and instructions attempting to alter the agent's task.

### D-018 — MVP invocation and user documentation

**Status:** adopted
**Decision:** the MVP runs on demand in Claude Code. The operator performs high-level operations by directly invoking entry skills, without a `.claude/commands/` layer or manual control of Python scripts.

The MVP exposes these user-invoked skills:

```text
/tool-eval-research <tool>
/tool-eval-compare <tool...>
/tool-eval-resume <run_id>
```

Research pauses at a single curation point and presents every candidate to the operator. The operator may accept, reject, or defer a candidate to the waiting room.

User documentation is a required release artifact and covers:

- prerequisites and installation on Windows, Linux, and macOS;
- creating a Python environment and installing the project;
- running `claude --agent tool-eval-orchestrator`;
- syntax, arguments, workflows, and results of every entry skill;
- sample research, curation, resume, and comparison sessions;
- profile, comparison, active-run, and failed-run directories;
- interpretation of statuses, constraints, freshness, and warnings;
- troubleshooting common errors and safely resuming a run.

### D-019 — Vertical implementation increments

**Status:** adopted
**Decision:** the MVP is built in five increments that deliver, in order: the project foundation, complete tool research, comparison and self-contained HTML, operational support and documentation, and manual MVP acceptance. Each increment ends with a working result that can be manually verified. The detailed backlog and gates are in Section 5.

### Agreed format split

- YAML — manually edited configuration;
- JSON — profiles, manifests, tasks, subagent results, candidates, and error reports;
- JSON Schema — validation of generated data;
- Markdown — skills, agents, documentation, and semantic profile descriptions;
- HTML — self-contained output artifact.

## 3. Target MVP architecture

### 3.1 Responsibility flow

```text
Direct Claude skill invocation
        │
        ▼
tool-eval-orchestrator (main Claude session agent)
        │
        ├── loads workflow and domain skills
        ├── calls deterministic Python CLI
        └── delegates isolated research tasks
                    │
                    ▼
            tool-eval-worker subagents
                    │
                    └── web research + validated JSON results
        │
        ▼
Python: validate → merge → calculate → render → publish
        │
        ├── data/profiles/<tool_id>/
        └── outputs/comparisons/<comparison_id>.html
```

Claude is responsible for research, source interpretation, semantic classification, conflict detection, and English-language content. Python neither communicates with the model nor conducts research. It enforces state, contracts, business rules, arithmetic, sanitization, and data persistence.

### 3.2 Components

#### `tool-eval-orchestrator`

The main agent of a session launched with `claude --agent tool-eval-orchestrator`. It handles the directly invoked entry skill, loads the orchestration skill, invokes the Python CLI, starts up to four workers, conducts the curation point, and manages the repair loop. It does not write active profiles directly or calculate comparison flags.

#### `tool-eval-worker`

A generic subagent executing one task from `task.json`. Its specialization is determined by `task_type` and the specified skill. The worker reads only explicit inputs, conducts research with Claude tools, and writes the result in its own directory. It does not publish, merge, change configuration, or delegate further.

#### Claude skills

- `tool-eval-orchestration` — phases, gates, retry, resume, curation, and publication;
- `source-discovery` — official domains, source classes, and source registry;
- `feature-research` — statuses, evidence, constraints, conflicts, and protocol D-009;
- `profile-writing` — additional facts, use cases, and `description.md`;
- `profile-validation` — interpretation of validator reports and data repair;
- `comparison` — how to start deterministic comparison and interpret its result.

#### Python package `tool_eval`

- loads and freezes configuration and revisions;
- creates runs, manifests, and tasks;
- validates JSON Schema and business rules;
- merges worker results and checks completeness;
- manages candidates and revisions;
- publishes and restores profiles;
- calculates freshness and comparison flags;
- renders Markdown, sanitizes content, and generates HTML;
- handles retry, resume, failed runs, retention, and recovery.

### 3.3 Repository structure

```text
tool-eval/
├── .claude/
│   ├── agents/
│   │   ├── tool-eval-orchestrator.md
│   │   └── tool-eval-worker.md
│   └── skills/
│       ├── tool-eval-research/
│       ├── tool-eval-compare/
│       ├── tool-eval-resume/
│       ├── tool-eval-orchestration/
│       ├── source-discovery/
│       ├── feature-research/
│       ├── profile-writing/
│       ├── profile-validation/
│       └── comparison/
├── config/
│   ├── feature-taxonomy.yaml
│   ├── source-policies.yaml
│   ├── profile-sections.yaml
│   ├── freshness.yaml
│   ├── runtime.yaml
│   └── presentation.yaml
├── src/tool_eval/
│   ├── __main__.py
│   ├── cli.py
│   ├── errors.py
│   ├── config/
│   ├── runs/
│   ├── validation/
│   ├── research/
│   ├── profiles/
│   ├── comparison/
│   └── reporting/
│       ├── templates/
│       └── assets/
├── data/
│   ├── profiles/<tool_id>/
│   │   ├── profile.json
│   │   └── description.md
│   └── feature-candidates/
│       ├── pending.json
│       └── rejected.json
├── outputs/comparisons/
├── .work/
│   ├── runs/
│   └── failed-runs/
├── docs/
│   ├── ai_coding_tool_comparison_system_requirements_v2.md
│   ├── implementation_plan_v1.md
│   └── user-guide.md
├── pyproject.toml
├── THIRD_PARTY_NOTICES.md
├── README.md
└── .gitignore
```

Each skill directory may contain `SKILL.md`, `references/`, `schemas/`, `examples/`, and `scripts/`. Shared Python code is not copied into skills. `.work/` is ignored by Git. Profiles, configuration, skills, and accepted taxonomy changes are persistent repository elements.

### 3.4 Run artifacts

```text
.work/runs/<run_id>/
├── run.json
├── frozen-config/
├── tasks/<task_id>/
│   ├── task.json
│   ├── input.json
│   ├── result.json
│   └── validation.json
├── merged/
│   ├── sources.json
│   ├── feature-results.json
│   ├── candidates.json
│   └── unresolved-issues.json
├── repairs/<round_number>/
├── publish/
│   ├── profile.json
│   └── description.md
└── validation-errors.json
```

`run.json` contains identifiers, operation, state, timestamps, initial and effective revisions and configuration hashes, retry counters, the list of mandatory tasks, budgets, and transition history. A controlled taxonomy change after candidate acceptance is recorded as an explicit revision transition. Python is the only component that changes the main manifest state.

### 3.5 User skills and internal CLI

User session:

```text
claude --agent tool-eval-orchestrator
/tool-eval-research <tool_name>
/tool-eval-compare <tool_id> <tool_id> [<tool_id>...]
/tool-eval-resume <run_id>
```

Minimum internal Python interface:

```text
python -m tool_eval config validate
python -m tool_eval run init|status|resume-check|fail
python -m tool_eval research create-source-task
python -m tool_eval research accept-sources
python -m tool_eval research create-feature-tasks
python -m tool_eval research validate-task
python -m tool_eval research merge
python -m tool_eval research curate-candidates
python -m tool_eval research prepare-repair
python -m tool_eval research build-profile
python -m tool_eval profile validate|publish|list
python -m tool_eval compare build
python -m tool_eval work cleanup|recover
```

Each internal CLI command writes logs to `stderr` and returns a small JSON envelope on `stdout` with `status`, `code`, `run_id`, `next_action`, `artifacts`, and optional `errors`. Large data always remains in schema-compliant files.

### 3.6 `/tool-eval-research` skill workflow

1. Validate configuration and create the run.
2. Freeze taxonomy, template, schema, and policy revisions.
3. Discover known and new official sources.
4. Validate the logical source registry.
5. Create bundles of 2–4 features and start workers up to the limit of four.
6. Validate each result; perform a technical retry or split an invalid bundle.
7. Merge deterministically and verify exactly one result for every feature.
8. Extract facts, use cases, and candidates.
9. Use one interactive curation point: accept, reject, or defer.
10. For accepted candidates: validate the definition, update the taxonomy through Python, increment the revision, record a controlled transition in the run, and mark remaining profiles as `requires_research`.
11. Create and execute research tasks for the accepted features of the current tool and merge again.
12. Verify exactly one result for every feature in the effective taxonomy revision.
13. Assemble `profile.json` and `description.md`.
14. Run JSON Schema, business rules, and up to three repair rounds.
15. Validate staging, replace the profile directory, and produce the final report.

Key gates: without an accepted source registry, feature research is blocked; a missing worker result blocks merging; `not_found` requires D-009; candidates must receive a decision; an accepted feature must be researched for the current tool before publication; an invalid or incomplete profile cannot be published.

### 3.7 `/tool-eval-compare` skill workflow

1. Resolve tools and copy active profiles to the comparison run directory.
2. Validate profiles, revisions, and dates.
3. Allow `requires_research` profiles with a warning; unresearched cells are excluded from flags.
4. Deterministically calculate freshness, date spread, and flags.
5. Assemble the view model.
6. Render and sanitize `description.md`.
7. Render the Jinja2 template with embedded Bootstrap, CSS, and JavaScript.
8. Publish a single file in `outputs/comparisons/`.

Comparison does not start research or subagents. A missing profile is an error for the specified tool, while an old revision or date generates a warning.

## 4. MVP scope and deferrals

### 4.1 Mandatory scope

- Claude Code as the only harness;
- research, compare, and resume started through directly invoked Claude skills;
- 20–30 initial features;
- complete research, candidates, and curation;
- JSON + Markdown profiles;
- deterministic comparison and self-contained HTML;
- failed runs, retry, resume, rollback, and recovery;
- English data contracts, instructions, and presentation;
- installation, entry-skill, and troubleshooting documentation;
- manual acceptance against all 15 Stage 1 criteria.

### 4.2 Outside the MVP

- Codex CLI, GitHub Copilot CLI, and adapter generator;
- direct LLM API access;
- crawler, local corpus, page archive, BM25, embeddings, and vector database;
- web application, hosting, backend, and telemetry;
- profile and source history;
- Node.js as a mandatory dependency;
- i18n and languages other than English;
- PDF export;
- Section B and effectiveness benchmarks.

### 4.3 Items calibrated during the pilot

These are not decisions blocking implementation: exact time and work limits, final bundle size for difficult features, need for an additional table library, and exact dependency versions within the adopted ranges.

## 5. Work plan

### Increment 1 — project foundation

**Objective:** an installable skeleton, contracts, and Claude integration without complete research.

1. Create `pyproject.toml`, `src/tool_eval`, `python -m tool_eval`, and the common CLI response envelope.
2. Create runtime directories and project-root discovery rules.
3. Add YAML configuration, revisions, and validation through `safe_load`.
4. Prepare the initial taxonomy of 20–30 features under curator supervision.
5. Define baseline run, task, source, and feature-result schemas.
6. Implement the error model and safe paths.
7. Create the orchestrator agent, worker, and baseline orchestration skill.
8. Create skeletons for the three directly invoked Claude skills.

**In parallel:** configuration, error model, and directory structure after package creation; taxonomy and schemas after the YAML format is agreed.

**Gate:** the package installs on Python 3.11+, configuration is valid, Claude recognizes the agents and entry skills, and no component requires an API key.

### Increment 2 — complete tool research

**Objective:** a complete, concurrent, resumable operation for the entire taxonomy.

1. Complete the profile model and references between records.
2. Implement the bundle planner and waves of up to four workers.
3. Implement complete protocol D-009, evidence, constraints, and conflicts.
4. Add additional facts, documented/inferred use cases, and full `description.md`.
5. Add candidates, a single curation gate, waiting room, and controlled revisions; add an accepted feature to the taxonomy, research it for the current tool, and mark remaining profiles as `requires_research`.
6. Merge deterministically and verify completeness across all features.
7. Add two technical retries, bundle splitting, and three repair rounds.
8. Add `.work/failed-runs`, retention, and the `/tool-eval-resume` skill.
9. Add staging, rollback, and safe replacement of the active profile.

**In parallel:** negative protocol, constraints, and candidates after the planner is ready; failed runs and resume after the state machine is defined.

**Gate:** the entire taxonomy has exactly one result per feature, `not_found` does not pass without the protocol, candidates are resolved, and a failed run does not change the profile.

### Increment 3 — comparison and self-contained HTML

**Objective:** a deterministic, offline report for multiple profiles.

1. Load and validate profiles, dates, and revisions.
2. Calculate freshness, date spread, and flags according to the requirements.
3. Exclude incomplete cells from flags and display warnings.
4. Render CommonMark, resolve evidence references, and sanitize through `nh3`.
5. Prepare Jinja2 with `StrictUndefined` and autoescape.
6. Embed pinned Bootstrap, its license, CSS, and a small vanilla JavaScript script.
7. Add tabs, filters, profiles, and conventional hover tooltips.
8. Add manual security cases and the `/tool-eval-compare` skill.

**In parallel:** flag calculations, Markdown pipeline, and template prototype after the view model is agreed.

**Gate:** four profiles produce one English HTML file that works offline, with deterministic flags, dates, warnings, profiles, and no execution of data as code.

### Increment 4 — operations and documentation

**Objective:** an MVP that someone outside the implementation team can use independently.

1. Refine success, error, and next-step messages.
2. Add configurable budgets, cleanup, and failed-run retention.
3. Add recovery for incomplete publication.
4. Write English installation instructions for all three operating systems.
5. Document research, compare, and resume syntax, flow, outputs, and errors.
6. Add sample curation, failed-run, resume, and comparison sessions.
7. Add troubleshooting and an explicit list of MVP limitations.

**In parallel:** operational mechanisms and documentation after the entry skills stabilize.

**Gate:** a new user relying only on the documentation can install the project, start the orchestrator, research a tool, resume a run, and generate a comparison.

### Increment 5 — manual MVP acceptance

**Objective:** confirm the complete solution in real Claude Code sessions.

1. Prepare a pass/fail checklist for all 15 criteria.
2. Research four real tools using the complete taxonomy.
3. Re-research one tool using known and new sources.
4. Trigger a controlled failure and verify preservation of the old profile.
5. Accept, reject, and defer candidates; verify revisions.
6. Resume a compatible run and reject resume after a revision change.
7. Generate a four-profile comparison and open it offline.
8. Test malicious Markdown, URLs, and prompt injection.
9. Validate the instructions with someone not involved in implementation.
10. Produce an acceptance report and post-MVP work list.

**Gate:** all 15 criteria have a `pass` result, no unvalidated profile is published, HTML works offline, and the documentation covers the complete workflow. A criterion may cease blocking release only after an approved change to the requirements document; `accepted limitation` is not a passing result.

### Dependencies between increments

```text
P1 Foundation
    ↓
P2 Full research
    ├──────────────┐
    ↓              ↓
P3 Compare/HTML    P4 Operations/docs
    └───────┬──────┘
            ↓
P5 Manual acceptance
```

## 6. Risks and mitigations

| ID | Risk | Probability / impact | Mitigation | Residual risk |
|---|---|---|---|---|
| R-01 | Nondeterministic Claude responses produce different statuses. | high / high | Strict skills, schemas, business rules, complete validation, and Python as the only merger/publisher. | Evidence interpretation remains model-dependent; disputed results use `uncertain`. |
| R-02 | Research without a local corpus incorrectly produces `not_found`. | medium / high | Complete protocol D-009, logical source registry, query trace, and `uncertain` when gaps exist. | Coverage of the entire Internet cannot be proven. |
| R-03 | Official pages are unavailable or block Claude tools. | medium / medium | Technical retries, alternative official sources, availability registry, and `uncertain`. | Some features may remain unresolved. |
| R-04 | Not storing page copies makes decisions harder to reproduce. | high / medium | URL, title, type, date, and a short faithful excerpt. | A changed page prevents full reproduction; this is a conscious trade-off. |
| R-05 | Prompt injection influences a worker. | medium / high | Untrusted-content treatment, restricted tools, no shell or code execution, and Python gates. | Instruction-level protection is not absolute. |
| R-06 | Workers return conflicts or write outside their task. | medium / high | Isolated directories, stable IDs, one delegation layer, path validation, and one writer. | Semantic conflicts may require operator input. |
| R-07 | A taxonomy or schema change mixes incompatible data. | medium / high | Frozen revisions, `requires_research`, resume checks, and exclusion of unresearched cells from flags. | A taxonomy change forces expensive re-research. |
| R-08 | Publication failure damages the active profile. | low / high | Staging, validation, technical backup, rollback, and recovery. | The profile may be briefly unavailable. |
| R-09 | Profile data executes code in HTML. | medium / high | Jinja2 autoescape, Markdown without raw HTML, `nh3`, safe URLs, and manual adversarial cases. | Library updates require renewed review. |
| R-10 | UI libraries introduce a vulnerability or licensing issue. | medium / medium | Pinned versions, local assets, SHA-256, licenses, and no CDN. | Updates are manual. |
| R-11 | Context, time, or worker limits interrupt research. | high / medium | Bundles of 2–4, at most four workers, bundle splitting, resume, and budgets. | A complex tool may require several sessions. |
| R-12 | The three operating systems behave differently. | medium / medium | `pathlib`, `shell=False`, no shell scripts, and manual verification on every OS. | Filesystem differences may still surface for users. |
| R-13 | Claude-only implementation impedes later portability. | high / medium | Neutral contracts and Python; Claude-specific details only in `.claude/`. | Other harnesses require new delegation instructions. |
| R-14 | On-demand execution does not provide automatic data freshness. | high / medium | Visible dates, freshness thresholds, warnings, and periodic-research instructions. | A profile remains stale until the operator acts. |

## 7. Stage 1 acceptance-criteria coverage matrix

| # | Criterion | Mechanism | Increment | MVP verification |
|---:|---|---|---|---|
| 1 | Research creates a profile for a new tool. | Claude skill, orchestrator, worker, profile builder, and publisher. | P2 | Manually create both profile files. |
| 2 | Re-research uses known sources and searches for new ones. | Read `sources`, source discovery, and a new query trace. | P2 | Re-research one tool. |
| 3 | Every feature has one valid result. | Frozen taxonomy, unique `feature_id`, and completeness validator. | P1–P2 | Missing, duplicate, and foreign IDs are rejected. |
| 4 | A result has evidence or a protocol. | `evidence`, `source_id`, `search_trace`, and D-009. | P2 | Scenarios for all four statuses. |
| 5 | Constraints are structured, source-backed, and visible. | `constraints`, evidence references, and HTML component. | P2–P3 | A constraint is visible with its source. |
| 6 | An official integration may produce `has`; a community one may not. | Source policy, `official`, and integration rules. | P1–P2 | Two manual integration scenarios. |
| 7 | Candidates are curated together or deferred. | One gate, accept/reject/defer, waiting room, and mandatory research of the accepted feature for the current tool. | P2 | Several candidates at one point; an accepted feature has a result before profile publication. |
| 8 | A taxonomy or template change marks old profiles. | Controlled revision transition, `requires_research`, and resume/compare checks. | P1–P3 | Accepting a feature increments the revision, updates the current run, and marks other profiles. |
| 9 | The validator reports errors and permits no more than three repairs. | Structured errors and round counter. | P1–P2 | A fourth repair is prohibited. |
| 10 | Failed research does not change the profile or date. | Staging, rollback, recovery, and failed run. | P2, P4 | Controlled failure after staging is built. |
| 11 | Compare creates self-contained HTML with tabs and profiles. | Comparison builder, Jinja2, Markdown, and bundled Bootstrap. | P3 | A four-profile file works offline. |
| 12 | Flags are deterministic and incomplete features are excluded. | Pure Python functions and completeness checks. | P3 | Repeated generation produces the same flags. |
| 13 | HTML shows dates, age, and date spread. | UTC metadata, freshness configuration, and warnings. | P3 | Profiles with controlled dates. |
| 14 | A profile has a description, facts, and both use-case types. | `description.md`, `additional_facts`, and documented/inferred use cases. | P2–P3 | Review a pilot profile and HTML. |
| 15 | A page does not control the agent or execute code. | Restricted worker, untrusted-content policy, sanitization, and safe URLs. | P1–P3 | Prompt injection, raw HTML, script, and `javascript:` tests. |

## 8. Implementation start and completion conditions

No open decisions block the start of Increment 1. Items calibrated in the pilot have default values and should not lead to speculative extension design before a real need appears.

The MVP is complete after passing the Increment 5 gate, receiving `pass` for all 15 criteria, resolving all blocking defects, and producing an `MVP accepted` report. Any deviation is allowed only after a prior approved and recorded change to the requirements document. Unimplemented out-of-MVP items go to a separate backlog and are not added to the current increment without an explicit scope change.
