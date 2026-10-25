# Documentation Index

**IMPORTANT**: Read this file at the beginning of any development task to understand available documentation and standards.

## Quick Reference

### Project Documentation
Project-level documentation covering vision, goals, architecture, and technology choices.

### Technical Standards
Coding standards, conventions, and best practices organized by domain.

---

## Project Documentation

Located in `.flowbit/docs/project/`

#### Technology Stack (`project/tech-stack.md`)
Technology choices and rationale for the tool-eval AI Coding Tool Comparison System. Covers the deterministic, offline Python stack (hatchling build, argparse CLI, PyYAML, jsonschema, markdown-it-py/Jinja2 rendering, nh3 sanitization, pytest), and the split of responsibilities between the Python core and the external Claude Code (`.claude/`) or Copilot CLI (`.github/`) agent harness.

#### System Architecture (`project/architecture.md`)
Architecture of the deterministic, offline Python CLI that researches, profiles, and compares AI coding tools. Describes the separation between the Python core (validation, merging, publication, run lifecycle) and the LLM agent harness, the alternative Copilot CLI adapter, the single-JSON-envelope command contract, and the container-level component view.

---

## Technical Standards

### Global Standards

Located in `.flowbit/docs/standards/global/`

These standards apply across the entire codebase, regardless of frontend/backend context.

#### Error Handling (`standards/global/error-handling.md`)
Structured error types, error propagation patterns, user-facing vs internal error messages, try-catch placement guidelines, error logging conventions. Project section adds structured `ToolEvalError` codes (`<FAMILY>_<REASON>`).

#### Validation (`standards/global/validation.md`)
Input validation at system boundaries, sanitization patterns, validation error message formatting, schema validation approach. Project section adds JSON Schema as source of truth and profile schema conventions (D-016).

#### Conventions (`standards/global/conventions.md`)
Naming conventions (files, variables, functions, classes), file organization patterns, import ordering, code structure guidelines. Project section adds Python/config naming, format-per-artifact rules, and English content with exact excerpts.

#### Coding Style (`standards/global/coding-style.md`)
Indentation and formatting rules, spacing conventions, line length limits, bracket style, consistent code readability patterns. Project section adds the fully typed public surface rule.

#### Commenting (`standards/global/commenting.md`)
When to comment (non-obvious logic only), documentation comment format, inline explanation guidelines, TODO/FIXME conventions.

#### Minimal Implementation (`standards/global/minimal-implementation.md`)
No speculative code, no unused methods, no "just in case" abstractions, YAGNI principle enforcement, lean code guidelines. Project section adds the minimal dependency stack and the "add tools without generator changes" rule.

#### Architecture Principles (`standards/global/architecture.md`)
Deterministic Python core (no model/LLM/web calls), harness-portability boundaries, pure logic behind IO wrappers, cross-platform Python 3.11+ with pathlib and safe subprocess use, and hatchling/src-layout packaging conventions.

#### Security & Data Handling (`standards/global/security.md`)
Untrusted source content and prompt-injection handling, no secrets in profiles/HTML with safe URL rules, official-sources-only feature status, self-contained sanitized HTML output, run path safety, and worker isolation with one-layer delegation.

#### Research Protocol (`standards/global/research-protocol.md`)
Single curation gate, complete not-found protocol, no source voting (policy-ordered conflict resolution), evidence/retained-source scope, research concurrency limits, and source reuse/search-budget (known-source reuse before new `WebSearch` calls, minimal broad queries plus on-site `WebFetch` crawling).

---

### Frontend Standards

*Not initialized for this project. If you need frontend standards, you can:*
- *Add them manually using the docs-manager skill*
- *Run `/flowbit-standards-discover --scope=frontend` to auto-discover*

---

### Backend Standards

Located in `.flowbit/docs/standards/backend/`

These standards apply to backend code (APIs, services, data layer).

#### API Design (`standards/backend/api.md`)
REST endpoint naming, request/response format conventions, versioning strategy, error response structure, pagination patterns. Project section adds the single-JSON-envelope CLI contract and the canonical `python -m tool_eval` interface.

#### Run Lifecycle & Publication (`standards/backend/runs.md`)
Config revision freezing and resume safety, bounded retries/repairs, safe profile publication via a staged publish directory, and failed-run retention policy.

#### Models (`standards/backend/models.md`)
Data model structure, schema conventions, business logic placement, relationship patterns, model validation rules.

#### Queries (`standards/backend/queries.md`)
Query optimization patterns, N+1 prevention, index usage guidelines, query builder conventions, raw query policies.

#### Migrations (`standards/backend/migrations.md`)
Migration naming conventions, schema change patterns, data migration approach, rollback requirements, migration testing.

---

### Testing Standards

Located in `.flowbit/docs/standards/testing/`

These standards apply to all testing code (unit, integration, E2E).

#### Test Writing (`standards/testing/test-writing.md`)
Test naming conventions, test file organization, arrange-act-assert structure, mocking guidelines, coverage expectations, test data management. Project section adds deterministic offline tests and pytest conventions (`test_item{N}_{feature}.py`, `tests/conftest.py`).

---

## How to Use This Documentation

1. **Start Here**: Always read this INDEX.md first to understand what documentation exists
2. **Project Context**: Read relevant project documentation before starting work
3. **Standards**: Reference appropriate standards when writing code
   - Global standards apply to all code
   - Domain-specific standards (backend/testing) apply to relevant code
4. **Keep Updated**: Update documentation when making significant changes
5. **Customize**: Adapt all documentation to your project's specific needs

## Updating Documentation

- Project documentation should be updated when goals, tech stack, or architecture changes
- Technical standards should be updated when team conventions evolve
- Always update INDEX.md when adding, removing, or significantly changing documentation

---

**Last Generated**: 2026-07-25 (research-protocol standard extended with source reuse & search budget subsection)
**Maintained by**: Documentation Manager skill
