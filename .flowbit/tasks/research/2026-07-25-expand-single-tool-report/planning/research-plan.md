# Research Plan: Expand Single-Tool Report Content Model

## 1. Research Overview

**Research question**: What content should the single-tool profile/report in
tool-eval contain to give a full overview of an AI coding tool — specifically
its **use cases** and **built-in tools/capabilities** — and what other
sections should be proposed for a complete AI-tool overview?

**Research type**: Mixed (Technical + Literature)

**Scope**: See `research-brief.md`. In short: inventory what the current
schema family, `feature-taxonomy.yaml`, `profile-sections.yaml`, and
reporting layer already capture/render for a single tool; identify the gap
that there is no dedicated single-tool HTML template (only
`comparison.html.j2`); and propose additional report sections informed by
how the AI-coding-tool industry structures comparable evaluation content.
Implementation is explicitly out of scope for this phase.

**Key sub-questions**:
1. What does today's profile already capture that's relevant to "use cases"
   and "built-in tools" (schema fields, taxonomy features, existing profile
   data)?
2. Where does a single-tool view actually render today, and what's missing
   structurally (template, renderer function) versus just missing content?
3. What does "built-in tools" mean precisely in this domain, and does it map
   cleanly onto existing `feature_results` (e.g. `workflow_ecosystem`,
   `agentic_execution` groups) or does it need a new first-class concept?
4. What sections do credible public AI-coding-tool comparison/evaluation
   writeups typically include, beyond use cases and built-in tools?
5. For each candidate new section: is it schema-representable today, does it
   need a schema addition, and is it realistically source-backable (per
   research-protocol: documented vs. inferred, no fabrication)?

## 2. Methodology

**Primary approach**: Parallel multi-source gathering (codebase + example
data + docs) followed by literature/best-practice gathering, then synthesis
that cross-references "what exists" against "what's typically expected."

**Analysis framework**:
- *Technical* angle: component identification (what schema/taxonomy/template
  pieces exist) → gap analysis (rendered vs. captured vs. absent) → mapping
  (how a literature-derived section would attach to schema/taxonomy).
- *Literature* angle: pattern comparison across known AI coding tool
  categories → best-practice section identification → applicability
  assessment filtered through the project's source-backed-only constraint.

**Fallback strategy**: If external sources are unavailable/blocked in the
gathering environment, rely on general, widely-known public conventions for
AI developer-tool comparison content (documented as "general industry
practice," not attributed to a fabricated specific source) and flag this
explicitly as a gap per the research-protocol standard (no source voting,
no fabricated facts).

## 3. Data Sources

### Codebase sources
- `src/tool_eval/validation/schemas/profile.schema.json` — top-level profile
  shape (`use_cases`, `additional_facts`, `feature_results`, `unresolved_issues`).
- `src/tool_eval/validation/schemas/use-case.schema.json` — existing
  documented/inferred use-case model (title, description, kind,
  supporting_features, rationale, evidence).
- `src/tool_eval/validation/schemas/feature-result.schema.json` — per-feature
  status/evidence/constraints/search_trace model.
- `src/tool_eval/validation/schemas/additional-fact.schema.json` — free-form
  topic/description/evidence fact model (candidate home for many literature
  sections, e.g. pricing, security posture, if not made first-class).
- `config/feature-taxonomy.yaml` (revision 4) — 27 features across 5 groups
  (`code_authoring`, `agentic_execution`, `context_quality`,
  `workflow_ecosystem`, `security_governance`); `workflow_ecosystem` already
  includes `mcp_or_plugin_extensibility`, `third_party_integration_catalog`,
  `standalone_cli`, `multi_ide_support`; `security_governance` already
  includes SSO, data retention, on-prem, IP indemnity, audit logging.
- `config/profile-sections.yaml` (revision 1) — `description.md` section
  list: `characteristics`, `access` (required), `internal_tools` (NOT
  required — title "Internal tools and mechanisms"), `workflows` (required —
  title "Workflows and use cases"), `integrations`, `security`, `constraints`
  (required). Directly relevant: an `internal_tools` section already exists
  in config but is optional and its actual current content/usage is unverified.
- `src/tool_eval/profiles/description.py` — deterministic assembler that
  enforces required sections from `profile-sections.yaml` and rejects
  unknown ones; LLM supplies prose per section.
- `src/tool_eval/reporting/html.py` — `render_comparison_html()`; only
  renderer today; renders `additional_facts` and `use_cases` per tool inside
  per-tool tab panes of the comparison view — confirms no single-tool
  template/function exists yet.
- `src/tool_eval/reporting/templates/comparison.html.j2` (lines ~180-227) —
  per-tool tab pane markup: avatar, name/vendor, freshness badge,
  `requires_research` flag, homepage link, rendered `description`,
  "Additional facts" list, "Use cases" list. This is effectively today's
  entire single-tool "report" content, embedded inside a multi-tool doc.
- `src/tool_eval/reporting/markdown.py` — sanitized Markdown rendering
  (nh3 + markdown-it) used for description/fact/use-case text.
- `src/tool_eval/comparison/model.py`, `flags.py` — comparison view-model and
  flag computation; check for any per-tool (non-comparative) model path.
- `data/profiles/*/profile.json` (5 tools: `claude_code`, `cursor`, `demo_tool`,
  `github_copilot`, `windsurf`) — real populated examples; all 5 already
  contain non-empty `use_cases` and `additional_facts` arrays today, useful
  to judge realistic content richness and gaps.
- `docs/user-guide.md` — sections 3 (entry skills), 6 (directory reference),
  7 (interpreting results); confirms only `outputs/comparisons/` HTML exists,
  no single-tool report artifact or CLI verb described.
- `src/tool_eval/cli.py` — confirm `profile` subcommand's actual verbs (no
  `profile show`/render-single-report verb found in initial scan; verify).

### Documentation / standards sources
- `.flowbit/docs/project/architecture.md` — deterministic-core boundary;
  any new report content must be pre-computed data, not live LLM calls at
  render time.
- `.flowbit/docs/project/tech-stack.md` — confirms Jinja2/markdown-it/nh3 as
  the only rendering stack (no new template engine should be proposed).
- `.flowbit/docs/standards/global/validation.md` — JSON Schema as source of
  truth (D-016): any new section needs a schema change, not ad hoc fields.
- `.flowbit/docs/standards/global/security.md` — self-contained sanitized
  HTML output, no secrets in profiles/HTML, official-sources-only feature
  status — constrains what a "pricing" or "security posture" section can
  claim and how it must be evidenced.
- `.flowbit/docs/standards/global/research-protocol.md` — single curation
  gate, complete not-found protocol, no source voting — governs how new
  literature-inspired sections would actually get populated (documented vs.
  inferred, never fabricated).
- `.flowbit/docs/standards/global/minimal-implementation.md` — YAGNI; any
  proposed sections must be justified, not just "nice to have."
- `.flowbit/docs/standards/backend/models.md` — schema/model conventions to
  follow if new fields are proposed.

### External / literature sources
- Public vendor documentation and comparison pages for representative AI
  coding tools already profiled in this repo (Claude Code, Cursor, GitHub
  Copilot, Windsurf) as concrete evidence of what such a report page
  typically covers: use cases, built-in agents/tools, IDE/editor support,
  pricing/plans, deployment models (cloud/on-prem), data handling/privacy,
  extensibility (MCP/plugins), and known limitations.
- Independent AI-coding-tool comparison/review write-ups (analyst blogs,
  engineering-team comparison posts) for the generic "what a thorough
  comparison covers" structure — used only to corroborate section *types*,
  not to source tool-specific facts (tool facts stay source-backed per
  profile, not invented from a generic comparison post).
- No academic literature expected to be relevant; this is an industry/
  vendor-documentation domain, not an academic one.

## 4. Research Phases

**Phase 1 — Broad discovery**
- Glob `src/tool_eval/validation/schemas/*.json`, `config/*.yaml`,
  `src/tool_eval/reporting/**`, `src/tool_eval/profiles/**`,
  `data/profiles/*/profile.json`.
- Confirm via `cli.py` grep whether any single-profile render path exists
  (e.g. `profile show`, `profile render`) beyond `build`/`validate`/`publish`.

**Phase 2 — Targeted reading**
- Read all five schema files in full; read `feature-taxonomy.yaml` and
  `profile-sections.yaml` in full (not just excerpts already seen).
- Read `reporting/html.py`, `reporting/markdown.py`,
  `templates/comparison.html.j2` in full; read `profiles/description.py`,
  `profiles/build.py`, `profiles/publication.py`.
- Read one full example profile (`claude_code`, richest) plus one thin one
  (`demo_tool`) to bound realistic content variance.

**Phase 3 — Deep dive**
- Trace how `use_cases` and `additional_facts` flow from schema →
  curation/merge → rendered HTML, to confirm there's no silent truncation or
  unused schema capability.
- For "built-in tools": map candidate feature_ids (from
  `agentic_execution`, `workflow_ecosystem`, `security_governance` groups)
  against what a user would intuitively call "built-in tools" (e.g.
  sandboxed execution, terminal execution, multi-agent orchestration, MCP/
  plugin extensibility) vs. what's genuinely absent from taxonomy (e.g.
  built-in linters/formatters/language-server integrations, specific named
  sub-agents, model/tool selection controls).
- Externally: pull structure of 2-3 public AI coding tool overview/comparison
  pages (for tools already in this repo) to see how they organize "use
  cases" and "built-in tooling" sections, plus what else they include
  (pricing, security/compliance, deployment, extensibility, limitations,
  target audience, benchmarks).

**Phase 4 — Verification**
- Cross-reference every literature-derived candidate section against: (a)
  whether it's already representable via `additional_facts` /
  `feature_results` / `use_cases` without schema change, (b) whether it
  needs a new schema field, (c) whether it's realistically source-backable
  per research-protocol, flagging any that would require speculation.
- Confirm no proposal implies a live/model call inside the Python core
  (architecture constraint) or an unsanitized/external-CDN-dependent
  rendering change (security constraint).

## 5. Gathering Strategy

### Instances: 4 (max 8)

| # | Category ID | Focus Area | Tools | Output Prefix |
|---|------------|------------|-------|---------------|
| 1 | codebase | Schemas, feature-taxonomy.yaml, profile-sections.yaml, reporting/profiles source code (renderer, template, description assembler), cli.py profile verbs | Glob, Grep, Read | codebase |
| 2 | example-profiles | Full content of `data/profiles/*/profile.json` (all 5), especially `use_cases`, `additional_facts`, `feature_results` richness and patterns | Read, Grep | example-profiles |
| 3 | docs | `docs/user-guide.md`, `.flowbit/docs/project/*.md`, `.flowbit/docs/standards/global/*.md` (validation, security, research-protocol, minimal-implementation, architecture), `.flowbit/docs/standards/backend/models.md` | Read, Grep | docs |
| 4 | external-best-practice | Public vendor/comparison pages for Claude Code, Cursor, GitHub Copilot, Windsurf, and general AI-coding-assistant comparison writeups: what sections a thorough overview includes (use cases, built-in tools/agents, IDE support, pricing/licensing, deployment/security/data handling, extensibility/MCP-plugins, limitations, target audience, benchmarks) | WebSearch, WebFetch | external-best-practice |

### Rationale
Four categories cleanly separate the two research angles required by the
brief without redundant overlap: (1) `codebase` and (2) `example-profiles`
together cover the full technical angle — schema/taxonomy/renderer structure
versus real populated data — kept separate because schema-reading and
data-reading benefit from different search strategies (structural grep vs.
full-file reads across 5 similarly-shaped JSON files). (3) `docs` covers
both user-facing documentation and internal standards that constrain any
proposal (deterministic core, schema-as-source-of-truth, source-backing
rules) — grouping these avoids a gatherer having to switch between doc types
mid-task. (4) `external-best-practice` is the sole literature/web-facing
gatherer, isolated because it uses different tools (WebSearch/WebFetch) and
a different verification standard (corroborating general section types) than
the internal sources. No sub-splitting by tool vendor or config file is
needed — the scope is bounded enough for one gatherer per category to
complete within its instance.

## 6. Success Criteria

- [ ] Current single-tool report/profile content fully documented, including
      the existing `use_cases` schema (documented vs. inferred), the
      `additional_facts` schema, and confirmation that no dedicated
      single-tool HTML template/renderer exists today (only per-tool tab
      panes inside `comparison.html.j2`).
- [ ] "Built-in tools" concretely defined for this domain (e.g. embedded
      linters/formatters, built-in agents/sub-agents, MCP/tool-use support,
      terminal/sandboxed execution) with an explicit mapping to which are
      already captured via `feature_results` (and which groups/feature_ids)
      versus genuinely uncaptured.
- [ ] A concrete, prioritized list of additional report sections proposed,
      each with: rationale, whether it needs a schema change (schema
      impact) or is representable via existing generic containers
      (`additional_facts`), and a note on rendering impact (new template
      needed vs. extension of comparison per-tool pane).
- [ ] Gaps between what research workers can realistically source (official
      docs, changelogs, vendor pages) and what would require speculation are
      explicitly flagged, per the research-protocol standard (no fabricated
      facts, complete not-found protocol).
- [ ] All claims about current codebase behavior backed by a specific file
      path (and line reference where useful); all literature claims backed
      by which sources were consulted or explicitly marked as "general
      industry pattern, not tool-specific" where sourcing is thin.

## 7. Expected Outputs

- A research report (via research-synthesizer) presenting:
  1. Current-state inventory (schema + taxonomy + rendering) for use cases
     and built-in tools.
  2. Gap analysis: no single-tool HTML report exists today; `internal_tools`
     description section exists in config but is optional.
  3. Definition of "built-in tools" for this domain with taxonomy mapping.
  4. Prioritized list of proposed additional sections (e.g. pricing/licensing,
     deployment & security posture, extensibility/MCP-plugin ecosystem,
     target audience/team size fit, limitations/known issues, benchmarks/
     independent evaluations where available) each with rationale and
     schema/rendering impact notes.
  5. Explicit flag list of sourcing gaps / inference-only areas.
- No code or schema changes in this phase — recommendations only, feeding a
  follow-up `/flowbit-development` (or spec/plan) task.
