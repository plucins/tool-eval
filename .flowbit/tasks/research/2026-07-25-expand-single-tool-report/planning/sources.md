# Research Sources

## Codebase Sources

### Schemas (source of truth per D-016)
- `src/tool_eval/validation/schemas/profile.schema.json` — top-level profile:
  `schema_version`, `tool`, `research`, `sources`, `feature_results`,
  `additional_facts`, `use_cases`, `unresolved_issues`. `additionalProperties: false`
  at every level — any new top-level report content must be added here first.
- `src/tool_eval/validation/schemas/use-case.schema.json` — `use_case_id`,
  `title`, `description`, `kind` (`documented`|`inferred`),
  `supporting_features`, `rationale`, `evidence[]`. Conditional requirements:
  `documented` needs `evidence` (>=1); `inferred` needs `rationale` +
  `supporting_features` (>=1).
- `src/tool_eval/validation/schemas/feature-result.schema.json` —
  `feature_id`, `status` (`has`|`partial`|`not_found`|`uncertain`),
  `rationale`, `evidence[]`, `constraints[]` (typed:
  `plan_or_license`|`platform_or_ide`|`model`|`region`|`product_version`|
  `release_stage`|`integration_required`|`other`), `search_trace`
  (`protocol_complete`, `queries`, `source_classes_checked`, `access_gaps`),
  `conflict`.
- `src/tool_eval/validation/schemas/additional-fact.schema.json` —
  `fact_id`, `topic`, `description`, `evidence[]`. Generic free-form
  container; candidate home for literature-derived sections that don't
  warrant a first-class schema field.
- `src/tool_eval/validation/schemas/source.schema.json`,
  `unresolved-issues.schema.json` — supporting schemas for evidence/source
  registry and issue tracking (conflict, access_gap, coverage_gap,
  prompt_injection_warning, other).

### Configuration (revisioned per D-016)
- `config/feature-taxonomy.yaml` (revision 4) — 27 features / 5 groups:
  `code_authoring`, `agentic_execution`, `context_quality`,
  `workflow_ecosystem`, `security_governance`. Each feature has
  `feature_id`, `name`, `group`, `definition`, `has_criteria`,
  `partial_criteria`, `exclusions`, `aliases`, `research_question`.
  Directly relevant feature_ids for "built-in tools": `autonomous_task_execution`,
  `background_long_running_tasks`, `multi_agent_orchestration`,
  `terminal_command_execution`, `sandboxed_execution_environment`,
  `mcp_or_plugin_extensibility`, `third_party_integration_catalog`,
  `standalone_cli`, `static_analysis_integration`, `automated_test_generation`,
  `automated_code_review`.
- `config/profile-sections.yaml` (revision 1) — `description.md` section
  list: `characteristics` (required), `access` (required), `internal_tools`
  (optional, "Internal tools and mechanisms"), `workflows` (required,
  "Workflows and use cases"), `integrations` (optional), `security`
  (optional), `constraints` (required).

### Key Files (reporting/profile pipeline)
- `src/tool_eval/profiles/description.py` — deterministic `description.md`
  assembler; enforces required sections from `profile-sections.yaml`,
  rejects unknown section ids; LLM supplies the prose.
- `src/tool_eval/profiles/build.py`, `validate.py`, `publication.py` —
  profile construction/validation/publish pipeline (read as needed for how
  use_cases/additional_facts get merged in).
- `src/tool_eval/reporting/html.py` — `render_comparison_html()`; only HTML
  renderer today; confirms no single-tool template/function exists.
- `src/tool_eval/reporting/templates/comparison.html.j2` (per-tool tab pane,
  ~lines 176-227) — today's entire single-tool "report" content: avatar,
  name/vendor, freshness badge, `requires_research` flag, homepage,
  description, "Additional facts" list, "Use cases" list — embedded inside a
  multi-tool comparison document, not a standalone artifact.
- `src/tool_eval/reporting/markdown.py` — sanitized Markdown rendering
  (nh3 + markdown-it) shared by any new prose section.
- `src/tool_eval/reporting/assets.py` — inlined CSS/JS/fonts (self-contained
  HTML constraint).
- `src/tool_eval/comparison/model.py`, `flags.py`, `builder.py`,
  `freshness.py`, `loader.py` — comparison view-model; check for any
  per-tool (non-comparative) construction path.
- `src/tool_eval/cli.py` — verify actual `profile` subcommand verbs (initial
  scan found no `profile show`/single-report render verb; confirm during
  gathering).

### Directories
- `src/tool_eval/validation/schemas/` — schema family.
- `src/tool_eval/reporting/` (+ `templates/`, `static/`) — rendering layer.
- `src/tool_eval/profiles/` — profile assembly/description/publication.
- `config/` — revisioned taxonomy and section config.
- `data/profiles/<tool_id>/profile.json` — one example per tool
  (`claude_code`, `cursor`, `demo_tool`, `github_copilot`, `windsurf`); all
  five already contain non-empty `use_cases` and `additional_facts`.

## Documentation Sources

### Project Documentation
- `.flowbit/docs/project/architecture.md` — deterministic Python core (no
  model/LLM/web calls at render time); constrains how any new section's
  content is produced (research-time LLM output, not render-time).
- `.flowbit/docs/project/tech-stack.md` — Jinja2 + markdown-it-py + nh3 is
  the entire rendering stack; no new templating engine should be proposed.

### Technical Standards
- `.flowbit/docs/standards/global/validation.md` — JSON Schema is the
  source of truth (D-016); any new report field requires a schema change.
- `.flowbit/docs/standards/global/security.md` — self-contained sanitized
  HTML, no secrets in profiles/HTML, official-sources-only feature status,
  safe URL rules — constrains pricing/security-posture style sections.
- `.flowbit/docs/standards/global/research-protocol.md` — single curation
  gate, complete not-found protocol, no source voting — governs how any new
  literature-inspired section gets populated (documented vs. inferred,
  never fabricated).
- `.flowbit/docs/standards/global/minimal-implementation.md` — YAGNI;
  proposed sections must be justified against a real evaluation need.
- `.flowbit/docs/standards/global/architecture.md` — pure-logic-behind-IO,
  deterministic core boundary.
- `.flowbit/docs/standards/backend/models.md` — schema/model conventions
  for any new profile fields.

### Code Documentation
- `docs/user-guide.md` — sections 3 (entry skills), 6 (directory
  reference: confirms `outputs/comparisons/` is the only generated HTML
  artifact today), 7 (interpreting results: feature statuses,
  constraints/freshness/warnings).
- Inline comments in `src/tool_eval/reporting/html.py` (module docstring
  explains autoescape/sanitization contract) and
  `src/tool_eval/profiles/description.py` (module docstring explains the
  Python-vs-LLM content split).

## Configuration Sources
- `config/feature-taxonomy.yaml` — revision 4, dependencies noted above.
- `config/profile-sections.yaml` — revision 1, description section list.
- No `package.json`/`docker-compose.yml`/build-tool config is relevant here
  (pure-Python, no containers per architecture standard).

## External Sources (literature / best-practice)
- Public official documentation for tools already profiled in this repo
  (used only to corroborate general report-structure conventions, not as a
  substitute for the profile's own sourced facts):
  - Claude Code docs (code.claude.com/docs, docs.anthropic.com) — already
    cited extensively in `data/profiles/claude_code/profile.json`.
  - Cursor, GitHub Copilot, Windsurf official docs/comparison pages —
    to be identified during external gathering.
- General AI-coding-assistant comparison/review structures (independent
  blogs, vendor comparison pages) — used only to identify *section types*
  commonly present (use cases, built-in tools/agents, IDE/language support,
  pricing/licensing, deployment/security/data handling, extensibility
  (MCP/plugins), limitations/known issues, target audience, benchmarks) —
  not to source tool-specific facts.
