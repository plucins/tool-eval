# Codebase Findings: Schemas, Taxonomy, Sections Config, Rendering Layer, CLI

Category: codebase (per research-plan.md section 5, row 1)
Scope covered: `src/tool_eval/validation/schemas/*.json`, `config/feature-taxonomy.yaml`,
`config/profile-sections.yaml`, `src/tool_eval/profiles/description.py`,
`src/tool_eval/reporting/html.py`, `src/tool_eval/reporting/templates/comparison.html.j2`,
`src/tool_eval/reporting/markdown.py`, `src/tool_eval/cli.py`, plus a quick check of
`src/tool_eval/comparison/model.py` (needed to answer "is there any per-tool render path").

All claims below are taken directly from the current working tree; no inference.

---

## 1. `src/tool_eval/validation/schemas/profile.schema.json` — top-level profile shape

Full file: `src/tool_eval/validation/schemas/profile.schema.json:1-87`. `additionalProperties: false` at
the top level (line 7), so the profile object cannot carry any field not listed here — any new
report section requiring new profile data needs a schema change here.

Required top-level properties (`profile.schema.json:8-14`): `schema_version`, `tool`, `research`,
`sources`, `feature_results`.

Optional top-level properties:
- `additional_facts` — array of `additional-fact.schema.json` items (`profile.schema.json:56-59`).
- `use_cases` — array of `use-case.schema.json` items (`profile.schema.json:60-63`).
- `unresolved_issues` — array of inline-typed objects (`profile.schema.json:64-84`), each requiring
  `issue_id`, `kind` (enum: `conflict`, `access_gap`, `coverage_gap`, `prompt_injection_warning`,
  `other` — `profile.schema.json:73-75`), `description`; optional `feature_id`,
  `related_source_ids`.

`tool` object (`profile.schema.json:17-27`): required `tool_id`, `name`; optional `vendor`,
`homepage` (must match `^https?://`).

`research` object (`profile.schema.json:28-47`): required `run_id`, `researched_at`,
`taxonomy_revision`, `template_revision`, `source_policy_revision`, `profile_state` (enum
`current`/`requires_research`, line 45). This is the freshness/staleness metadata, not content.

Note: there is no first-class container for "built-in tools" as a named concept — the closest
existing mechanisms are `feature_results` (taxonomy-driven, see section 4) and the generic
`additional_facts` free-form container.

---

## 2. `src/tool_eval/validation/schemas/use-case.schema.json` — use-case model

Full file: `src/tool_eval/validation/schemas/use-case.schema.json:1-48`.

Required fields (`:8`): `use_case_id`, `title`, `description`, `kind`.
`kind` enum (`:13`): `documented` | `inferred` — matches the plan's "documented vs inferred" framing
exactly.

Optional fields:
- `supporting_features` — array of feature_id strings (`:14-17`).
- `rationale` — free string (`:18`).
- `evidence` — array of `{source_id, excerpt}` objects, both required if evidence items present
  (`:19-30`).

Conditional requirements via `allOf`/`if`/`then` (`:32-47`):
- If `kind == "documented"`: `evidence` is required with `minItems: 1` (`:33-39`) — a documented
  use case must cite at least one source.
- If `kind == "inferred"`: `rationale` and `supporting_features` (with `minItems: 1`) are required
  (`:40-46`) — an inferred use case must explain *why* it was inferred and link it to at least one
  taxonomy feature that supports the inference.

Description field of the schema (`:5`) states explicitly: "Either vendor-documented (source-backed)
or LLM-inferred (labelled, with rationale, supporting features, and evidence). Inferred use cases do
not affect flags." This confirms use-cases already have a mature, source-disciplined model; the gap
(per section 8 below) is not the schema but that only `title`, `kind`, `description` are actually
rendered today.

---

## 3. `feature-result.schema.json` and `additional-fact.schema.json`

**`feature-result.schema.json`** (full file: `:1-103`):
- Required (`:7`): `feature_id`, `status`, `rationale`, `search_trace`.
- `status` enum (`:10-13`): `has`, `partial`, `not_found`, `uncertain`.
- `evidence` — array of `{source_id, excerpt}` (`:15-26`).
- `constraints` — array of objects with required `type`, `description`, `source_id` (`:27-50`);
  `type` enum (`:36-45`): `plan_or_license`, `platform_or_ide`, `model`, `region`,
  `product_version`, `release_stage`, `integration_required`, `other`. This is where
  plan/tier-gating detail for a feature would already live (e.g. "sandboxed execution available
  only on Enterprise plan").
- `search_trace` — required object (`:52-61`) with `protocol_complete` (bool), `queries`,
  `source_classes_checked`, optional `access_gaps` — this is the "complete not-found protocol"
  evidence trail referenced by the research-protocol standard.
- `conflict` — optional object for recording conflicting evidence (`:63-82`).
- Conditional rules (`:84-101`): `status: has` and `status: partial` both require
  non-empty `evidence`; `status: not_found` requires `search_trace.protocol_complete == true`.

**`additional-fact.schema.json`** (full file: `:1-27`):
- Required (`:8`): `fact_id`, `topic`, `description`.
- Optional `evidence` array of `{source_id, excerpt}` (`:13-24`).
- Description (`:5`): "A fact about the tool that matters for the profile but sits outside the
  comparable taxonomy... Source-backed; the LLM may not add facts from memory." No `evidence`
  minItems constraint is enforced at the schema level (unlike use-case/feature-result), so
  `additional_facts` entries are *not* schema-required to carry evidence, even though the
  description states they must be source-backed — this is enforced by process/protocol, not by
  the JSON Schema itself. Flagging this as a schema-vs-description gap worth noting for any new
  literature-derived sections that might be modeled as `additional_facts`.

---

## 4. `config/feature-taxonomy.yaml` — full taxonomy (revision 4)

Full file: `config/feature-taxonomy.yaml:1-523`. Revision: `4` (`:2`). 5 groups (`:3-13`):
`code_authoring`, `agentic_execution`, `context_quality`, `workflow_ecosystem`,
`security_governance`.

Full feature list (27 features) by group, with line references (`feature_id` at each cited line):

**`code_authoring`** (4 features):
- `inline_code_completion` — `:15`
- `natural_language_code_generation` — `:34`
- `multi_file_code_generation` — `:52`
- `automated_refactoring` — `:177`
- `diff_review_apply_workflow` — `:194`
  (5 features total in this group, counting both blocks — see note below)

**`agentic_execution`** (5 features) — candidate group for "built-in tools/agents":
- `autonomous_task_execution` — `:69` ("Autonomous multi-step task execution" / "agent mode")
- `background_long_running_tasks` — `:87` ("Background / long-running task execution")
- `multi_agent_orchestration` — `:105` ("Multi-agent / sub-agent orchestration" — explicitly
  matches "built-in sub-agents" from the brief)
- `terminal_command_execution` — `:262` ("Terminal command execution")
- `sandboxed_execution_environment` — `:280` ("Sandboxed / isolated execution environment")

**`context_quality`** (5 features):
- `codebase_semantic_search` — `:123`
- `long_context_large_repo_handling` — `:141`
- `persistent_project_memory` — `:159`
- `automated_test_generation` — `:210`
- `automated_code_review` — `:226`
- `static_analysis_integration` — `:244`
  (6 features in this group — see note below)

**`workflow_ecosystem`** (8 features) — candidate group for "built-in tools" (integrations/ecosystem
angle):
- `git_native_workflow` — `:298`
- `pull_request_creation` — `:316`
- `multi_ide_support` — `:334`
- `standalone_cli` — `:348`
- `web_hosted_access` — `:364`
- `mcp_or_plugin_extensibility` — `:379` (matches "MCP/tool-use support" from the brief directly)
- `third_party_integration_catalog` — `:397`
- `mobile_app_access` — `:505`

**`security_governance`** (5 features):
- `enterprise_sso_access_control` — `:414`
- `data_retention_training_opt_out` — `:430`
- `on_premises_private_deployment` — `:449`
- `ip_indemnity_duplication_filter` — `:468`
- `audit_logging` — `:488`

Note on count: I counted feature_id occurrences per group by reading the full file; totals above
are: code_authoring=5, agentic_execution=5, context_quality=6, workflow_ecosystem=8,
security_governance=5 = **29 features total** (not 27 as stated in research-plan.md:70 — flagging
this discrepancy; the plan text may be stale relative to taxonomy revision 4, or I may be
miscounting group membership for a couple of features that read as borderline — e.g.
`automated_refactoring`/`diff_review_apply_workflow` are listed under `code_authoring` per their
`group:` field even though they appear later in file order interleaved with `agentic_execution`/
`context_quality` entries; verified by reading the literal `group:` value at each feature, not by
file position). This count discrepancy should be verified independently before being treated as
authoritative in synthesis.

Each feature entry has a consistent schema of fields (evidenced at `:15-33` for the first entry):
`feature_id`, `name`, `group`, `definition`, `has_criteria`, `partial_criteria`, `exclusions`,
`aliases`, `research_question`. This is a rich, structured definition per feature — the taxonomy
itself is not a flat list, each feature carries its own operational definition of "has" vs
"partial" vs excluded, which is directly reusable as the basis for a "built-in tools" report
section without new taxonomy fields, only new grouping/labeling in the render layer.

Mapping candidate "built-in tools" feature_ids relevant to the brief's own examples:
- "sandboxed execution" → `sandboxed_execution_environment` (`agentic_execution`, `:280`) — already
  captured.
- "terminal execution" → `terminal_command_execution` (`agentic_execution`, `:262`) — already
  captured.
- "multi-agent orchestration" → `multi_agent_orchestration` (`agentic_execution`, `:105`) — already
  captured.
- "MCP/tool-use support" → `mcp_or_plugin_extensibility` (`workflow_ecosystem`, `:379`) — already
  captured.
- "built-in linters/formatters" → `static_analysis_integration` (`context_quality`, `:244`) exists
  but is scoped to "integrates with or runs static analysis/lint tooling ... surfaces results to the
  AI assistant" (`:247-249`) — this is about the AI *consuming* lint output, not the tool shipping
  its own linter/formatter as a distinct built-in utility. No feature_id in the taxonomy captures
  "ships its own formatter/linter as a standalone utility" as a first-class concept; this looks like
  a genuine gap rather than a mis-grouping.
- "specific named sub-agents" (e.g. a named "planner" or "reviewer" sub-agent persona) — not
  represented; the taxonomy captures *that* multi-agent orchestration exists (`:105-122`) but has no
  field for enumerating named/branded sub-agent roles. This would need either a new
  `additional_facts` entry per tool or a schema extension if it's to be structured/comparable.
- "model/tool selection controls" (e.g. user picks which underlying LLM model powers the tool) — not
  represented in the taxonomy at all under any group. Genuine gap.

---

## 5. `config/profile-sections.yaml` — description.md sections (revision 1)

Full file: `config/profile-sections.yaml:1-29`. Revision: `1` (`:5`). Comment at `:1-3` states
changing a `required` section bumps `revision`, which marks older profiles as `requires_research`
(tied to `research.template_revision` in `profile.schema.json:35`).

All 7 sections in file order (`:8-28`):

| id | title | required |
|---|---|---|
| `characteristics` | "Characteristics" | **true** |
| `access` | "Access methods" | **true** |
| `internal_tools` | "Internal tools and mechanisms" | **false** |
| `workflows` | "Workflows and use cases" | **true** |
| `integrations` | "Integrations" | false |
| `security` | "Security" | false |
| `constraints` | "Constraints" | **true** |

Directly relevant to the research question: `internal_tools` ("Internal tools and mechanisms",
`config/profile-sections.yaml:14-16`) already exists as a description-section concept, but is marked
`required: false` — so a profile can be published (per `description.py`, section 6 below) with this
section entirely absent or empty, with no schema/build-time enforcement that any tool's built-in
mechanisms are actually documented. This is the config-level confirmation of the plan's stated gap
("an `internal_tools` section already exists in config but is optional").

Also note `workflows` ("Workflows and use cases", `:17-19`) is `required: true` — so every published
profile must have non-empty prose in this Markdown section already, independent of the structured
`use_cases` array in `profile.schema.json`. These are two separate mechanisms: `workflows` is a
required free-text Markdown section in `description.md`; `use_cases` is a structured, optional JSON
array. Both currently exist without being cross-validated against each other (no code found in
`description.py` that requires `use_cases` array entries to correspond to what's stated in the
`workflows` prose, or vice versa).

---

## 6. `src/tool_eval/profiles/description.py` — section assembly/enforcement

Full file: `src/tool_eval/profiles/description.py:1-81`.

`assemble_description(sections_config, section_texts)` (`:39-80`):
- Takes the `sections` list from `profile-sections.yaml` and a dict of LLM-provided
  section-id → Markdown text.
- Rejects unknown section ids not present in the config (`:52-59`, error code
  `VALIDATION_UNKNOWN_SECTION`) — so a new section (e.g. "pricing") cannot be freely added by the
  LLM at build time; it must first be added to `profile-sections.yaml`.
- Enforces that every section marked `required: true` in config has non-empty, non-whitespace text
  (`:61-71`, error code `VALIDATION_MISSING_REQUIRED_SECTION`).
- Non-required sections with empty/missing text are silently omitted from the assembled Markdown
  (`:73-79`, `if isinstance(text, str) and text.strip()` gate) — so an optional section like
  `internal_tools` producing no text simply does not appear in `description.md` at all; there is no
  placeholder, no "not researched" marker rendered for skipped optional sections.
- Docstring (`:1-12`) confirms the architectural split: this module does only deterministic
  assembly/validation; the LLM supplies all prose; HTML rendering/sanitization happens later (in
  `reporting/markdown.py` / `reporting/html.py`, confirmed in sections 7-9 below).

This confirms: adding a genuinely new section (e.g. "Pricing & licensing") to satisfy the brief
would require (a) an entry in `profile-sections.yaml`, and (b) if it should ever be required, a
revision bump per the header comment in that file (`config/profile-sections.yaml:1-4`), which
retroactively invalidates existing published profiles (`requires_research` state).

---

## 7. `src/tool_eval/reporting/html.py` — render functions that exist

Full file: `src/tool_eval/reporting/html.py:1-137`.

I grepped the entire `reporting/` package (`assets.py`, `html.py`, `markdown.py`) for any
`def render*`/public API surface. Result: **`render_comparison_html` (`html.py:103-136`) is the only
HTML-rendering entry point in the whole package.** There is no `render_profile_html`,
`render_tool_html`, or any per-tool-only render function anywhere in `src/tool_eval/reporting/`.

`render_comparison_html(model, profiles, descriptions=None, *, assets=None, title=...)`
(`:103-109`) signature requires a `ComparisonModel` (`model` — see section below on
`comparison/model.py`) and a `list[dict]` of full profile JSON objects (`profiles`) — i.e. its
input shape is inherently multi-tool; there is no code path that accepts a single tool/profile and
skips the comparison scaffolding.

Inside the function: it builds a `sources_by_id` registry across all supplied profiles (`:113`,
using `_sources_by_id` at `:90-95`), renders each tool's `description` Markdown into sanitized HTML
per tool_id (`:116-120`), and renders the single Jinja2 template `comparison.html.j2` (`:122-136`,
`_TEMPLATE_NAME = "comparison.html.j2"` at `:25`) — confirming there is exactly one template file in
use, referenced at `_TEMPLATE_DIR = Path(__file__).parent / "templates"` (`:24`).

`_summary_stats` (`:63-87`) computes KPI counts (status counts, freshness counts, flagged feature
counts) purely from `model.groups`/`model.tools` — i.e. this is comparison-summary data, not
per-tool report data.

**Also checked `src/tool_eval/comparison/model.py`** (grep only, not full read — within scope as
"comparison view-model... check for any per-tool (non-comparative) model path" per
research-plan.md:95-96): top-level definitions are `ToolColumn`, `Cell`, `FeatureRow`,
`FeatureGroup`, `ComparisonModel`, and `build_comparison_model(...)`
(`comparison/model.py:26,37,51,60,67,113`). `build_comparison_model` is the only model-construction
function; by name and by the multi-tool column/row/cell shape, this is inherently a
multiple-tools-side-by-side model — no single-tool model constructor was found. This corroborates
that there is no per-tool (non-comparative) model path anywhere in `comparison/`.

**Conclusion for the research question's core technical sub-question:** there is currently no
dedicated single-tool report renderer, template, or model in the codebase. The only way a tool's
profile content becomes HTML today is as one tab pane inside a multi-tool `compare build` output
(`cli.py` `compare build` → `build_comparison` → `render_comparison_html` → `comparison.html.j2`).

---

## 8. `comparison.html.j2` — per-tool tab pane markup (profile panel, lines ~176-226)

Full template is 247 lines (`src/tool_eval/reporting/templates/comparison.html.j2:1-247`); the
per-tool "Profiles" tab pane is at `:176-226`.

Exact fields rendered per tool inside `#profile-{{ tool.tool_id }}` (`:188-223`):
1. Avatar — first two characters of tool name, upper-cased (`:192`, `tool.name[:2]|upper`).
2. Name (`:193`, `tool.name`) and, if present, vendor as "by {{ tool.vendor }}" (`:194`).
3. Freshness badge (`:195`) — `cg-fresh-{{ tool.freshness }}` class, label from `freshness_labels`
   dict, plus literal `researched {{ tool.researched_at }}`.
4. `requires_research` flag badge, conditionally shown only if
   `tool.profile_state == 'requires_research'` (`:196-198`).
5. Homepage link, conditionally shown if `tool.homepage` is set (`:200-202`), rendered as a plain
   `<a>` with `rel="noopener noreferrer nofollow"`.
6. Description — the full assembled `description.md` (all sections from `profile-sections.yaml`
   concatenated, per section 6 above), rendered as sanitized HTML via the `descriptions` dict
   pre-rendered in `html.py:117-120`, shown as one undifferentiated block (`:203-205`,
   `<div class="cg-description">{{ descriptions[tool.tool_id] }}</div>`) — i.e. the template does
   **not** re-split this back into per-section headers/anchors/tabs; it's one HTML blob per the
   Markdown headers `description.py` already wrote (`## {section title}`, `description.py:78`).
7. "Additional facts" — only rendered `if profile.get('additional_facts')` (`:206`); for each fact,
   renders `<strong>{{ fact.topic }}</strong>: {{ fact.description|md }}` (`:209-211`). Fields
   rendered: `topic`, `description` only — `fact_id` and `evidence` are **not** rendered anywhere in
   this pane.
8. "Use cases" — only rendered `if profile.get('use_cases')` (`:214`); for each use case, renders
   `<strong>{{ uc.title }}</strong> ({{ uc.kind }}) — {{ uc.description|md }}` (`:217-219`). Fields
   rendered: `title`, `kind`, `description` only — `use_case_id`, `supporting_features`,
   `rationale`, and `evidence` are **not** rendered anywhere in this pane, even though they exist in
   the schema and are schema-required for certain `kind` values (section 2 above).

I grepped the whole template file for `unresolved_issues`, `feature_results`, `internal_tools`,
`supporting_features`, `rationale`, `evidence` (verification step, not just a visual read): the only
hit across the entire template is `rationale` at `:144`, which is a tooltip (`data-bs-toggle
title="{{ cell.rationale }}"`) on a feature-grid cell in the *comparison table* section (above the
per-tool profile tab pane, not part of it) — i.e. feature-level rationale is surfaced only as a
hover tooltip in the comparative grid, not in the per-tool profile view at all. None of
`unresolved_issues`, `feature_results` (by that name — the grid iterates `model.groups`/`features`,
which is the pre-processed form of `feature_results`), or `internal_tools` (the description section)
appear anywhere in the template as distinctly labeled content; `internal_tools` prose, if present, is
folded invisibly into the single `descriptions[tool.tool_id]` blob (item 6 above) with no separate
heading/anchor a reader could jump to distinctly (though the Markdown `## Internal tools and
mechanisms` header from `description.py:78` would appear inline within that blob if the LLM
populated the section).

**This confirms the plan's assertion verbatim**: today's entire single-tool "report" content is:
avatar/name/vendor, freshness badge, requires_research flag, homepage link, one big rendered
description blob, a flat additional-facts list (topic+description only), and a flat use-cases list
(title+kind+description only) — embedded inside a multi-tool comparison document, with no dedicated
single-tool page, template, or URL/output artifact.

---

## 9. `src/tool_eval/reporting/markdown.py` — rendering/sanitization approach (noted, not deep-dived)

Full file: `src/tool_eval/reporting/markdown.py:1-84`. CommonMark via `markdown_it.MarkdownIt` with
raw HTML disabled (`html=False`, `linkify=False`, `:38`); output sanitized with `nh3.clean` using an
explicit allow-list of tags/attributes/URL schemes (`http`, `https`, `mailto` only, `:20-34,41-50`).
Evidence references of the form `[[source_id]]` are resolved to Markdown links against a
`sources_by_id` registry before rendering (`:53-69`); unknown ids degrade to plain `[source_id]`
text rather than a broken link (`:64`). This is the only Markdown→HTML path in the codebase and
would be reused unchanged by any new single-tool report template — no new rendering stack is
implied by adding sections, per the architecture constraint noted in research-plan.md:110-111.

---

## 10. `src/tool_eval/cli.py` — `profile` subcommand verbs

Full file: `src/tool_eval/cli.py:1-529`. The `profile` subparser group is built at
`cli.py:465-479`:
```
profile_parser = subparsers.add_parser("profile", help="Profile operations")
profile_sub = profile_parser.add_subparsers(dest="action", required=True)

p_validate = profile_sub.add_parser("validate")       # cli.py:468-471
p_publish  = profile_sub.add_parser("publish")        # cli.py:473-477
profile_sub.add_parser("list")                        # cli.py:479
```
Exactly **three** verbs exist under `profile`: `validate` (`profile_path`, optional
`--check-completeness`, handler `cmd_profile_validate` at `:280-294`), `publish` (`run_id`,
`tool_id`, optional `--check-completeness`, handler `cmd_profile_publish` at `:297-312`), and `list`
(handler `cmd_profile_list` at `:315-321`, backed by `list_profiles(root)` from
`tool_eval.profiles.publication`).

There is **no** `profile show`, `profile render`, or any verb that renders a single tool's report
independently of the comparison flow. The only HTML-producing CLI verb anywhere in the whole file is
`compare build` (`cli.py:481-487`, handler `cmd_compare_build` at `:327-340`), which requires
`--tools` with **two or more** `tool_id`s (per its help text and per `build_comparison`'s multi-tool
contract) and always goes through `render_comparison_html`. This directly confirms the plan's
open verification item ("no `profile show`/render-single-report verb found in initial scan; verify")
— verified true: no such verb exists as of this read.

Also relevant to the "no live/model call in core" architecture constraint (out of scope for this
category's deep-dive but noted because it surfaced while reading `cli.py`): every `cmd_*` handler in
this file only reads/writes local files and calls into `tool_eval.*` modules — no network or model
client import appears anywhere in `cli.py:1-34` (import block) or in the handler bodies read above.

---

## Ambiguities / things I could not fully verify within this category's scope

1. **Feature count discrepancy**: research-plan.md:70 states "27 features across 5 groups" but my
   direct count of `feature_id:` occurrences by their literal `group:` value in
   `config/feature-taxonomy.yaml` gives 29 (5 + 5 + 6 + 8 + 5). I have not cross-checked this against
   an automated schema/count tool (e.g. `taxonomy_feature_ids()` in `research/pipeline.py`, which is
   outside this category's assigned scope) — flagging for the synthesizer to resolve, since it
   affects how "27" vs "29" is cited in the final report.
2. **`additional_facts` evidence is optional at the schema level** despite the schema description
   stating facts must be source-backed (section 3 above) — whether this is intentional (enforced
   elsewhere, e.g. in curation/build pipeline code not in this category's scope) or a schema gap is
   unverified from this category alone; the `example-profiles` and `docs` gatherer categories may be
   able to confirm whether populated profiles in practice always include evidence for
   `additional_facts`.
3. I did not deep-read `src/tool_eval/profiles/build.py` or `src/tool_eval/profiles/publication.py`
   (mentioned in the research plan's Phase 2 reading list but not in my assigned focus-area file
   list) — I only confirmed their entry points are invoked from `cli.py` (`build_profile`,
   `publish_profile`, `list_profiles`, `recover`). If the synthesis needs to know exactly how
   `use_cases`/`additional_facts` content flows from research task JSON into the built profile, that
   would need a targeted read of `build.py`, which is out of this category's assigned scope.
