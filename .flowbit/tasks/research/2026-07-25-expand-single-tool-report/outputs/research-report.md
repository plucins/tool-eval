# Research Report: Expand Single-Tool Report Content Model

**Research type**: Mixed (technical codebase analysis + industry literature/best-practice)
**Date**: 2026-07-25
**Task path**: `.flowbit/tasks/research/2026-07-25-expand-single-tool-report`

## Table of Contents

1. Executive Summary
2. Research Objectives
3. Methodology
4. Current State: What a "Single-Tool Report" Is Today
5. "Built-In Tools" Defined for This Domain
6. Prioritized Additional Report Sections
7. Constraints Any Proposal Must Satisfy
8. Confidence Levels and Open Gaps
9. Conclusions — Direct Answer to the Research Question
10. Out of Scope / Next Steps
11. Appendices

---

## 1. Executive Summary

**What was researched**: what content a single AI coding tool's profile/report in tool-eval
should contain to give a full overview — specifically its use cases and built-in
tools/capabilities — and what other sections a complete overview should propose.

**How it was researched**: three parallel gatherers covered the codebase (schemas, taxonomy,
rendering layer), project documentation and standards, and external industry best practice for
AI-coding-tool comparison content. A fourth planned gatherer (direct read of the five real
`data/profiles/*/profile.json` files) did not produce output; this report's synthesis phase
performed a narrow, disclosed direct check of those five files to fill that hole for the
counts and structural facts needed here (see §8 and the appendix).

**Key findings**:
- There is **no dedicated single-tool HTML report** anywhere in the codebase today. The only
  renderer is `render_comparison_html` (`src/tool_eval/reporting/html.py:103-136`), which
  always requires two or more tool profiles and renders a single `comparison.html.j2`
  template; a tool's content appears only as one tab pane inside that multi-tool document
  (`comparison.html.j2:176-226`). No CLI verb renders a single profile (`cli.py` has only
  `profile validate|publish|list`, no `profile show`/`render`).
- **Use cases** already have a mature schema (`use-case.schema.json`) distinguishing
  `documented` (source-backed, evidence required) from `inferred` (rationale +
  supporting-features required) — but the current template renders only `title`/`kind`/
  `description`, dropping `rationale`, `supporting_features`, and `evidence` entirely.
- **"Built-in tools"** maps cleanly onto six existing taxonomy `feature_id`s
  (`mcp_or_plugin_extensibility`, `multi_agent_orchestration`, `terminal_command_execution`,
  `sandboxed_execution_environment`, `static_analysis_integration`, `standalone_cli`), with two
  genuine taxonomy gaps: vendor-bundled linters/formatters as a distinct concept, and
  enumeration of named sub-agent roles.
- **Everything else** industry comparisons typically cover (pricing, deployment, security/data
  handling, extensibility, limitations, target audience) already has a working, if informal,
  home in the existing `additional_facts` generic container — real profile data already
  populates topics like "Plans and tiers," "Data usage," "Vendor identity," and "Free tier
  limits" this way today.

**Main conclusion**: most of what the brief asks for is a **rendering gap**, not a
data-modeling gap. A small number of genuinely new concepts (named sub-agents, vendor-bundled
tooling, a canonical "recommended additional-facts topics" list) would benefit from either a
light schema extension or a documented convention, but the large majority of the proposed
content can be surfaced by writing a richer single-tool render path against data that mostly
already exists.

---

## 2. Research Objectives

**Primary research question**: What content should the single-tool profile/report in
tool-eval contain to give a full overview of an AI coding tool — specifically its use cases
and built-in tools/capabilities — and what other sections should be proposed for a complete
AI-tool overview?

**Sub-questions** (from `planning/research-plan.md:20-33`):
1. What does today's profile already capture relevant to "use cases" and "built-in tools"?
2. Where does a single-tool view actually render today, and what's missing structurally
   (template/renderer) versus just missing content?
3. What does "built-in tools" mean precisely in this domain, and does it map onto existing
   `feature_results` or need a new concept?
4. What sections do credible public AI-coding-tool comparisons typically include beyond use
   cases and built-in tools?
5. For each candidate new section: schema-representable today, needs a schema addition, and
   realistically source-backable per research-protocol?

**Scope** (`orchestrator-state.yml:39-55`):
- Included: profile/use-case/feature-result schemas, `feature-taxonomy.yaml`,
  `reporting/` (html.py, markdown.py, templates), `description.py`, example profile data,
  `docs/user-guide.md`, external industry practice.
- Excluded: implementing schema/report changes (research + recommendation only); live
  scoring/benchmarking execution or network calls in the core.

---

## 3. Methodology

Mixed-methods: parallel information gathering across four planned categories (codebase,
example-profile-data, docs/standards, external best-practice — see `planning/research-plan.md`
§5), followed by cross-source synthesis. One category (example-profile-data) produced no
findings file; the synthesis phase performed a bounded, disclosed direct verification of the
five real profile files to cover the specific facts this report needed (counts, evidence
presence, taxonomy revisions) — see §8.4 and Appendix C.

**Analysis framework**: mixed — technical component/gap analysis for the codebase angle,
best-practice pattern comparison plus an applicability filter (schema-representable today? /
needs schema change? / needs new render path?) for the literature angle.

**Data sources**: 3 findings files (~61KB combined), `planning/research-plan.md`,
`orchestrator-state.yml`, direct reads of `src/tool_eval/research/curation.py`,
`src/tool_eval/profiles/build.py`, `config/profile-sections.yaml`, and all five
`data/profiles/*/profile.json` files.

---

## 4. Current State: What a "Single-Tool Report" Is Today

### 4.1 No dedicated single-tool render path exists

Confirmed by three independent lines of evidence:

- **Code**: `render_comparison_html` is the only render function in `src/tool_eval/reporting/`
  (grep across `assets.py`, `html.py`, `markdown.py`); its signature requires a
  `ComparisonModel` and a `list[dict]` of profiles — inherently multi-tool
  (`html.py:103-109`). `comparison/model.py`'s only constructor, `build_comparison_model`, is
  likewise multi-tool by shape (`ToolColumn`/`Cell`/`FeatureRow`/`FeatureGroup`). `cli.py`'s
  only HTML-producing verb is `compare build`, which requires `--tools` with two or more
  `tool_id`s (`cli.py:327-340,481-487`); the `profile` subcommand group has exactly three
  verbs — `validate`, `publish`, `list` (`cli.py:465-479`) — no `show`/`render`.
- **User documentation**: `docs/user-guide.md` lists exactly three entry skills — research,
  compare, resume — with the compare skill explicitly described as needing "two or more"
  tools (`user-guide.md:92-100`); the directory reference names `data/profiles/<tool_id>/`
  (profile.json + description.md, no HTML) and `outputs/comparisons/` (the only HTML output
  path, plural/comparison-only by name) at lines 208 and 210.
- **Architecture documentation caveat**: `.flowbit/docs/project/architecture.md:78-80` calls
  Comparison & Reporting "stubbed," which — cross-referenced against the working code just
  cited, `user-guide.md`'s description of a functioning `/tool-eval-compare` flow, and the
  fact that `reporting/html.py`, `comparison.html.j2`, and `feature-taxonomy.yaml` show as
  locally modified in git status at a date one day after that doc's stated snapshot — is
  assessed as **stale documentation, not an accurate description of current behavior**. This
  synthesis treats the working code and user-guide as authoritative for "what renders today."

### 4.2 The closest existing artifact: profile.json + description.md, surfaced as a tab pane

A tool's entire "report" content today, all embedded as one tab pane inside the multi-tool
comparison HTML (`comparison.html.j2:176-226`):

1. Avatar (first two chars of name), name, vendor ("by {vendor}") — `:192-194`.
2. Freshness badge + `researched_at` date, `requires_research` flag if stale — `:195-198`.
3. Homepage link, if set — `:200-202`.
4. The full assembled `description.md` for the tool, rendered as one undifferentiated
   sanitized-HTML blob — `:203-205`. `description.md` itself is built from up to 7 Markdown
   prose sections defined in `config/profile-sections.yaml` (revision 1): `characteristics`,
   `access` (required), `internal_tools` (optional, title "Internal tools and mechanisms"),
   `workflows` (required, title "Workflows and use cases"), `integrations` (optional),
   `security` (optional), `constraints` (required). Because `internal_tools` is optional, a
   published profile can entirely omit "built-in mechanisms" prose with no placeholder shown
   (`description.py:73-79`).
5. "Additional facts" list — only `topic` and `description` rendered per fact
   (`comparison.html.j2:209-211`); `fact_id` and `evidence` exist in the data but are not shown.
6. "Use cases" list — only `title`, `kind`, `description` rendered per use case
   (`:217-219`); `use_case_id`, `supporting_features`, `rationale`, `evidence` exist in the
   schema/data but are not shown.

### 4.3 What the schema already captures for "use cases"

`use-case.schema.json` (full file, `:1-48`) requires `use_case_id`, `title`, `description`,
`kind` (`documented` | `inferred`). Conditional rules: if `kind: documented`, `evidence`
(min 1 item) is required; if `kind: inferred`, `rationale` and `supporting_features` (min 1
item) are required. This is a mature, source-disciplined model — matching the project's
"documented vs. LLM-inferred, labelled" epistemic pattern exactly. The gap is not the schema;
it's that the template drops most of these fields at render time (§4.2 item 6).

**[synthesizer direct-check]** Real data confirms use_cases are consistently populated:
`claude_code` 5, `cursor` 4, `github_copilot` 5, `windsurf` 4, `demo_tool` 2 use cases — none
empty.

### 4.4 What `additional_facts` already carries in practice

`additional-fact.schema.json` (full file, `:1-27`) requires only `fact_id`, `topic`,
`description`; `evidence` is optional at the schema level (no `minItems` conditional, unlike
`use-case.schema.json`), even though the schema's own description states facts must be
"source-backed; the LLM may not add facts from memory."

**[synthesizer direct-check]**, reading all five real profiles' `additional_facts` arrays:
already-populated topics are: *Platform and access surfaces* (claude_code, cursor, windsurf),
*Data usage* (claude_code), *Models and context handling* (claude_code), *Plans and
availability / Plans and tiers / Pricing tiers / Pricing note* (all five, in some form),
*Release stage* (claude_code), *Model choice* (cursor), *Free tier limits* (github_copilot),
*Extensibility via MCP* (github_copilot), *Vendor identity* (github_copilot), *Cascade agent*
(windsurf, product-name-specific), *Plans and deployment* (windsurf). Despite the schema not
requiring it, **every one of the 16 facts across all five profiles carries a non-empty
`evidence` array** — worker behavior already complies with the schema's stated intent, even
though nothing enforces it structurally (see §8.4 for the process-level gap this reveals).

**Conclusion**: `additional_facts` is already, informally, the home for exactly the kind of
content (pricing, platform/access, data handling, extensibility, vendor identity) that
industry comparisons treat as standard sections (§6 below) — it just isn't driven by any
canonical topic checklist, so coverage is inconsistent tool-to-tool (e.g. only github_copilot
has an explicit MCP-extensibility fact; only claude_code has an explicit data-training fact).

### 4.5 `feature_results`: the taxonomy-driven comparison backbone

`config/feature-taxonomy.yaml` (revision 4) defines **29 features** across 5 groups —
`code_authoring` (5), `agentic_execution` (5), `context_quality` (6), `workflow_ecosystem` (8),
`security_governance` (5) — counted by the codebase gatherer directly from each feature's
literal `group:` field, not by file position. (`planning/research-plan.md:70` states "27,"
which this synthesis resolves as stale text: three real profiles at `taxonomy_revision: 4`
each carry exactly 29 `feature_results` entries; two older profiles at `taxonomy_revision: 1`
carry 26, consistent with predating the taxonomy's growth, not contradicting the count — see
Appendix C.) Each feature carries a rich per-feature definition (`has_criteria`,
`partial_criteria`, `exclusions`, `aliases`, `research_question`) plus, per profile, `status`
(`has`/`partial`/`not_found`/`uncertain`), `evidence`, `constraints` (plan/tier/platform
gating detail), and a `search_trace` (protocol-completeness record). This is the most
rigorously sourced content in the profile — feature status may only rest on official public
sources, `not_found` requires the complete search protocol to have run, and conflicts are
resolved by policy order, never by counting how many pages repeat a claim
(`.flowbit/docs/standards/global/research-protocol.md:6-13`).

---

## 5. "Built-In Tools" Defined for This Domain

For this project's purposes, "built-in tools/capabilities" maps to the mechanisms an
AI coding tool ships natively — agentic execution behaviors, extensibility surfaces, and
native automation — as distinct from features that are just "the AI writes code well."

### 5.1 Existing taxonomy coverage (already captured, no schema change needed)

| Built-in tool concept | `feature_id` | Group | Taxonomy line |
|---|---|---|---|
| Sandboxed/isolated execution | `sandboxed_execution_environment` | `agentic_execution` | `feature-taxonomy.yaml:280` |
| Terminal command execution | `terminal_command_execution` | `agentic_execution` | `:262` |
| Multi-agent / sub-agent orchestration | `multi_agent_orchestration` | `agentic_execution` | `:105` |
| MCP / plugin extensibility | `mcp_or_plugin_extensibility` | `workflow_ecosystem` | `:379` |
| Static-analysis/lint integration (AI *consuming* lint output) | `static_analysis_integration` | `context_quality` | `:244` |
| Standalone CLI | `standalone_cli` | `workflow_ecosystem` | `:348` |

These six feature_ids already carry the full protocol rigor described in §4.5 — no new
schema/taxonomy work is needed to report on them; what's missing is a render-layer grouping
that labels them together under a "Built-in tools" heading rather than leaving them scattered
across the flat comparison grid, invisible in the current per-tool tab pane (§4.2 confirms
none of `feature_results`, `internal_tools`, or `unresolved_issues` appear as distinctly
labeled content in `comparison.html.j2` today, apart from a hover tooltip on `rationale` in
the comparison grid at `:144`).

### 5.2 Genuine taxonomy gaps

- **Vendor-bundled linters/formatters as a distinct, shipped utility.**
  `static_analysis_integration`'s definition is explicitly scoped to "integrates with or runs
  static analysis/lint tooling ... surfaces results to the AI assistant"
  (`feature-taxonomy.yaml:247-249`) — i.e., the AI *consuming* lint output, not the product
  shipping its own formatter/linter as a standalone utility. No feature_id captures the latter.
- **Named/branded sub-agent enumeration.** The taxonomy captures *that* multi-agent
  orchestration exists (`:105-122`) but has no field for enumerating specific named sub-agent
  roles (e.g. a product's built-in "planner" or "reviewer" persona). External best-practice
  findings corroborate this is a real, named differentiator in the market — Claude Code's
  plugin system is described as bundling "slash commands, agents, MCP servers, and hooks" as
  distinct, nameable extension points (external-best-practice.md §2, §7, citing
  anthropic.com/news/claude-code-plugins).
- **Model/tool selection controls** (user picks which underlying LLM powers the tool) — not
  represented in the taxonomy under any group; flagged by the codebase gatherer as a genuine
  gap, and corroborated by the external gatherer's cross-tool table noting Cursor's "model
  choice" and windsurf's model-dependent behavior as a recurring comparison axis.

For these three gaps, representability requires either (a) a schema/taxonomy extension (new
feature_id(s), which would then need to pass through the single curation gate like any other
taxonomy candidate — `curation.py`'s `curate_candidates`/`accept_feature_into_taxonomy`), or
(b) a lighter-weight `additional_facts` entry per tool (e.g. `fact_id: bundled_formatter`,
`topic: "Bundled tooling"`) if full comparability (has/partial/not_found across all tools) is
not required. Given the YAGNI standard (`minimal-implementation.md:3-22`), the additional_facts
route is the lower-cost starting point; promoting to a full taxonomy feature is justified only
if comparability across tools becomes a stated need.

---

## 6. Prioritized Additional Report Sections

Each candidate below cites external corroboration (from `external-best-practice.md`) and is
run through the project's own applicability filter: current representability, schema impact,
rendering impact.

| # | Section | Rationale (external corroboration) | Current representability | Schema impact | Rendering impact |
|---|---|---|---|---|---|
| 1 | **Pricing & licensing** | Confirmed as one of the most consistently present sections across every source found; often the top-level differentiator in article titles (external §4) | Already used informally — `plans_and_tiers`/`pricing_tiers`/`plan_availability`/`pricing_note` facts exist in 4 of 5 real profiles today | None — fits `additional_facts` as-is | Add a distinct "Pricing & licensing" heading in the per-tool pane that groups facts whose `topic` matches a recognized set, or (cleaner) add an optional discriminator/category to `additional-fact.schema.json` so the template can group deterministically instead of matching on free-text `topic` strings |
| 2 | **Deployment model** (cloud/on-prem/self-hosted) | Confirmed common, especially in enterprise comparisons (external §5) | Overlaps existing taxonomy feature `on_premises_private_deployment` (`security_governance`, already has full protocol rigor) plus informal facts like windsurf's "Plans and deployment" | None for the taxonomy-covered part; `additional_facts` for anything beyond the existing feature | Surface `on_premises_private_deployment`'s feature_result alongside deployment-related facts under one heading |
| 3 | **Security & data-handling posture** | Confirmed common, high-attention, often its own dedicated article (external §6) | Overlaps existing taxonomy features (`data_retention_training_opt_out`, `enterprise_sso_access_control`, `audit_logging`, `ip_indemnity_duplication_filter`) plus informal facts (claude_code's "Data usage") | None — taxonomy already covers the comparable core; `additional_facts` for nuance | Group the four `security_governance` feature_results with any security-labeled `additional_facts` under one section, replacing today's scattered/hidden presentation |
| 4 | **Extensibility / MCP ecosystem** | Confirmed common and increasingly its own axis as MCP adoption spreads (external §7) | Maps to existing `mcp_or_plugin_extensibility` and `third_party_integration_catalog` feature_ids, plus github_copilot's existing "Extensibility via MCP" fact | None | Same pattern — group feature_result + any matching facts |
| 5 | **Known limitations / common complaints** | Confirmed common; independent posts consistently separate this from the feature list (external §8) | **No existing home.** Not a feature_result (limitations aren't "has/partial/not_found" against a defined capability), not a natural `additional_facts` topic either since it's inherently comparative/critical framing rather than a fact about the tool | Could reuse `unresolved_issues` (`profile.schema.json:64-84`, kind enum includes `coverage_gap`, `other`) if reframed, or a new lightweight `additional_facts`-style entry — **needs a decision, not purely mechanical**; per the external gatherer's own confidence note, individual claims here are self-reported community/blog material and would need independent, official-source verification per this project's research-protocol before being asserted, which may make this section hard to populate rigorously in practice | New grouping in the template if `unresolved_issues` is reused; otherwise none beyond `additional_facts` |
| 6 | **Target audience / team-size fit** | Confirmed common; multiple sources structure entire articles around this axis (external §9) | No existing home; this is inherently a synthesized judgment, not a discrete fact | Best modeled as a single `additional_facts` entry (e.g. `topic: "Target audience"`) rather than a schema field, since it's prose-like synthesis, not a comparable status | New "Target audience" grouping/heading |
| 7 | **Supported IDEs/languages** | Confirmed common, treated as a distinct axis, not folded into "features" (external §3) | Already exists as taxonomy feature `multi_ide_support` (`workflow_ecosystem`) — external gatherer flagged this as only "medium confidence" for standing alone vs. being folded into general features, matching this project's existing choice to keep it inside the taxonomy | None | Surface `multi_ide_support`'s feature_result (with its `constraints` array, which already models platform/IDE detail per `feature-result.schema.json:27-50`) prominently rather than only in the flat grid |
| 8 | **Independent benchmarks / evaluations** | Confirmed present but with a **material credibility caveat**: OpenAI's own Frontier Evals team publicly reported that 59.4% of a sampled hard SWE-bench Verified subset had flawed/unsolvable test cases with confirmed training-data contamination (external §10) | No existing home; would need to be scoped carefully | If added at all, should be scoped to the *underlying model*, not the tool product (benchmarks measure model coding ability, not IDE/agent UX), and explicitly labeled low-confidence per the evaluators' own stated conclusion that "testing on your own repository" is the more reliable signal | **Recommend low priority / conditional inclusion only**, and only as an `additional_facts` entry with an explicit caveat in its `description`, never as a comparable `feature_result` |
| 9 | **"Best for X" positioning summary** | Every external comparison source found ends with an explicit verdict mapping tool → best-fit scenario (external §11) | This is a synthesis of #1 (pricing) + #6 (target audience) + #3 (security), not new source-backed content — it would be a curator/LLM-authored summary, not a fact | If included, this is prose (fits the existing `characteristics` or a new optional `profile-sections.yaml` Markdown section), not a structured/comparable field | New optional Markdown section in `profile-sections.yaml`, following the existing `internal_tools`/`workflows` pattern |
| 10 | **Richer rendering of existing use_cases/additional_facts/feature_results fields** | Not an external-practice item — an internal gap identified by cross-referencing schema vs. template (§4.2-4.4) | Fully representable today — the data already exists | None | This is the **highest-value, lowest-risk** change: extend `comparison.html.j2`'s per-tool pane to render `rationale`/`supporting_features`/`evidence` for use cases, `evidence` for additional_facts, and group `feature_results` by taxonomy group instead of leaving them implicit in the comparison grid only |

**Priority ordering recommendation** (rationale-driven, not a formal scoring model): #10
(render existing fields more fully) first, since it is zero schema risk and directly answers
the brief's own framing ("use cases and built-in tools" already have data); then #1-4 and #7
(group existing `feature_results`/`additional_facts` into named headings — still zero schema
risk, pure template work); then #6 and #9 (new optional prose sections, low schema risk — one
new `profile-sections.yaml` entry each); then #5 (limitations — needs an explicit decision on
data model before any rendering work); #8 (benchmarks) last and conditionally, given the
credibility caveat.

---

## 7. Constraints Any Proposal Must Satisfy

Repeated here verbatim in substance from the docs/standards findings, because every section
above was filtered through these before being included:

1. **Deterministic core, no live LLM/network calls at render time**
   (`.flowbit/docs/project/architecture.md:4,122`). Any new content must be pre-gathered data
   stored in the profile; the Python renderer only ever reads stored data.
2. **JSON Schema is the source of truth (D-016)** for any new first-class field
   (`.flowbit/docs/standards/global/validation.md:32-36`); `additionalProperties: false` at
   the profile top level (`profile.schema.json:7`) means no field can be added ad hoc in code
   or templates alone.
3. **Official-sources-only facts; no fabrication; no secrets in profiles/HTML**
   (`.flowbit/docs/standards/global/security.md:6-13`) — this bears directly on candidate
   sections like pricing and benchmarks, where the external gatherer's own sourced figures are
   explicitly third-party-reported and not fit for direct profile use without independent
   verification.
4. **Existing Jinja2 + markdown-it-py + nh3 stack only**
   (`.flowbit/docs/project/tech-stack.md:16-18,80-82`; reinforced by
   `minimal-implementation.md:26-27`'s "Minimal Dependency Stack") — no new templating
   technology, no client-side JS rendering.
5. **Same research-protocol rigor for any new taxonomy feature**: single curation gate,
   complete not-found protocol, no source voting
   (`.flowbit/docs/standards/global/research-protocol.md:3-16`); confirmed by direct code read
   that `curation.py` governs feature candidates only — `additional_facts` sit structurally
   outside this gate (see §8.4).
6. **YAGNI**: every new section needs an explicit rationale beyond "industry parity"
   (`.flowbit/docs/standards/global/minimal-implementation.md:3-22`); prefer data-driven,
   generic mechanisms over per-tool bespoke code, consistent with "add tools without generator
   changes" (`:29-30`).

---

## 8. Confidence Levels and Open Gaps

**High confidence** (multiple independent sources, or direct code/data verification):
- No single-tool render path exists today (§4.1) — code + docs + CLI enumeration agree.
- Use-case schema outstrips template rendering (§4.3) — direct schema and template reads.
- 29 is the correct current taxonomy feature count, not 27 (§4.5, resolved via cross-checking
  three real revision-4 profiles' `feature_results` counts against the codebase gatherer's
  direct taxonomy read).
- Six existing feature_ids already cover the core "built-in tools" concept (§5.1).
- Use cases, built-in tools/agents, pricing, security/data handling, extensibility, and known
  limitations are all confirmed as standard external section types by 3+ independent sources
  each (external-best-practice.md's confidence summary).

**Medium confidence**:
- Supported IDEs/languages "as a standalone section" — external gatherer rated this only
  medium confidence (often folded into general "features" rather than broken out), and this
  project's taxonomy already makes the same choice, which is a point in favor of not changing
  the current approach.
- `additional_facts` real-world evidence discipline (100% of 16 facts across 5 profiles carry
  evidence) is based on a small sample (n=5), all produced by this project's own harness — not
  strong enough to call a durable guarantee for future or externally-authored profiles.

**Low confidence / explicitly caveated**:
- Independent benchmarks as a trustworthy, stable section — the external gatherer's own
  sourced material documents a serious, publicly reported integrity problem with the leading
  benchmark (SWE-bench Verified); this gatherer had no WebFetch tool, so even this caveat
  itself rests on WebSearch snippets, not a first-hand page read — flagged at two removes of
  uncertainty.

**Explicitly unresolved / open gaps**:
1. **Missing gatherer output**: the planned `example-profiles-data.md` findings file was never
   produced. This report's §4.3-4.5 direct-check figures partially substitute for it but were
   deliberately narrow (counts, evidence presence, taxonomy revisions) — a fuller pass (e.g.,
   assessing `description.md` prose richness/quality across the five tools) was not performed
   and remains an open gap.
2. **`additional_facts` structural gap, confirmed by direct code read**: `curation.py` (single
   curation gate) governs only taxonomy feature candidates; `build.py:_collect_content`
   (`:65-101`) merges `additional_facts` by simple `fact_id` dedup with no evidence check.
   `additional-fact.schema.json` does not enforce `evidence` the way `use-case.schema.json`
   enforces it for `kind: documented`. This is a real, code-confirmed asymmetry in protocol
   rigor between the two content channels — noted as a finding of this research, not resolved
   here (a schema-hardening fix would be a separate, small, follow-up change if the user wants
   to pursue it, distinct from the report-content question this task was scoped to answer).
3. **Whether `tool.vendor`/`tool.homepage` should become mandatory/first-class fields** given
   they are optional today (`profile.schema.json:17-27`) — not resolved by any of the three
   findings files nor by the narrow direct-check performed here; would need a dedicated look at
   how consistently real profiles populate them.
4. **External findings are WebSearch-snippet-only** — no WebFetch tool was available to that
   gatherer, so exact page structure/headings for cited vendor/comparison pages were not
   directly verified, only the presence/topic of each section type.

---

## 9. Conclusions — Direct Answer to the Research Question

**What the single-tool report should contain, concretely:**

1. **Use cases** — already schema-complete; the fix needed is rendering `rationale`,
   `supporting_features`, and `evidence` (not just `title`/`kind`/`description`) so a reader
   can see *why* an inferred use case was inferred and what source backs a documented one.
2. **Built-in tools/capabilities** — group the six existing feature_ids
   (`mcp_or_plugin_extensibility`, `multi_agent_orchestration`, `terminal_command_execution`,
   `sandboxed_execution_environment`, `static_analysis_integration`, `standalone_cli`) under an
   explicit "Built-in tools" heading in the per-tool view, reusing the taxonomy's own rich
   per-feature definitions and status/evidence/constraints already collected. Close the two
   genuine gaps (vendor-bundled linters/formatters as a distinct concept; named sub-agent
   enumeration) via `additional_facts` first, promoting to full taxonomy features only if
   cross-tool comparability on those specific points becomes a stated need.
3. **A complete overview should additionally cover** (in priority order, per §6): pricing &
   licensing, deployment model, security & data-handling posture, extensibility/MCP ecosystem,
   supported IDEs/languages — all of which already have a representational home
   (`additional_facts` and/or existing taxonomy features) and need only render-layer grouping —
   followed by target-audience fit and an optional "best for X" positioning summary (new
   optional prose section), and finally, conditionally and with an explicit low-confidence
   caveat, independent benchmarks scoped to the underlying model rather than the tool product.
   Known limitations is corroborated as a standard section but has no clean existing data home
   and would need its own decision (reuse `unresolved_issues` vs. a new mechanism) before it
   could be populated at the same rigor as the rest of the profile.

**Primary conclusion**: the work implied by this research is overwhelmingly a **rendering
expansion**, not a data-modeling overhaul. Two of the three things the brief names (use cases,
built-in tools) are schema-complete already; most of "everything else" already lands
informally in `additional_facts`. The genuinely new schema/process work is narrow: closing two
taxonomy gaps (optional, low-priority), deciding how to model "known limitations," and
optionally tightening `additional-fact.schema.json` to require evidence (a hygiene fix
independent of this report's content question).

---

## 10. Out of Scope / Next Steps

Per `orchestrator-state.yml:49-51` and `planning/research-plan.md:18,256-257`, **implementing
any of the above (schema changes, new template sections, a new CLI verb, taxonomy additions)
is explicitly out of scope for this research phase.** This report is a recommendation
document only. Any decision to proceed should be scoped as a follow-up `/flowbit-development`
(or spec/plan) task, informed by:
- The priority ordering in §6 (start with #10 — render existing fields more fully — as the
  lowest-risk, highest-value first step).
- The open gap on `additional_facts` evidence enforcement (§8, point 2) as a candidate,
  separate, small hardening change.
- The doc-staleness item (`architecture.md`'s "stubbed" language) as a candidate documentation
  refresh, unrelated to report content.

---

## 11. Appendices

### Appendix A — Complete Source List

**Findings files** (gatherer category → file):
- codebase → `analysis/findings/codebase-schemas-and-rendering.md`
- docs/standards → `analysis/findings/docs-and-standards.md`
- external best-practice → `analysis/findings/external-best-practice.md`
- example-profiles-data → **not produced** (see §8, point 1)

**Codebase files read/cited** (via the codebase and docs gatherers, and this synthesis's
direct checks): `src/tool_eval/validation/schemas/profile.schema.json`,
`use-case.schema.json`, `feature-result.schema.json`, `additional-fact.schema.json`,
`config/feature-taxonomy.yaml`, `config/profile-sections.yaml`,
`src/tool_eval/profiles/description.py`, `src/tool_eval/profiles/build.py`,
`src/tool_eval/research/curation.py`, `src/tool_eval/reporting/html.py`,
`src/tool_eval/reporting/templates/comparison.html.j2`, `src/tool_eval/reporting/markdown.py`,
`src/tool_eval/cli.py`, `src/tool_eval/comparison/model.py` (grep only),
`data/profiles/{claude_code,cursor,demo_tool,github_copilot,windsurf}/profile.json`.

**Documentation/standards read**: `docs/user-guide.md`,
`.flowbit/docs/project/architecture.md`, `.flowbit/docs/project/tech-stack.md`,
`.flowbit/docs/standards/global/validation.md`, `security.md`, `research-protocol.md`,
`minimal-implementation.md`, `.flowbit/docs/standards/backend/models.md` (flagged by the docs
gatherer as generic/non-authoritative for this file-based, no-database project).

**External sources** (all via WebSearch, no WebFetch — see external-best-practice.md for the
full list of ~15 cited URLs covering Claude Code, Cursor, GitHub Copilot, Windsurf, and
general AI-coding-assistant comparison writeups).

### Appendix B — Gaps and Uncertainties (consolidated)

See §8 above for the full breakdown by confidence tier.

### Appendix C — Direct-Check Raw Data (synthesizer, supplementing the missing example-profiles gatherer)

| Tool | `use_cases` | `additional_facts` | `feature_results` | `taxonomy_revision` | `profile_state` | All facts have evidence? |
|---|---|---|---|---|---|---|
| claude_code | 5 | 5 | 26 | 1 | requires_research | Yes (5/5) |
| cursor | 4 | 3 | 29 | 4 | current | Yes (3/3) |
| github_copilot | 5 | 4 | 29 | 4 | current | Yes (4/4) |
| windsurf | 4 | 3 | 29 | 4 | current | Yes (3/3) |
| demo_tool | 2 | 1 | 26 | 1 | requires_research | Yes (1/1) |

Method: `python3 -c "..."` reading each `data/profiles/<tool>/profile.json` directly and
counting array lengths / checking `evidence` key presence, run during this synthesis phase.
No tool-specific facts from this data are asserted as new profile content in this report —
only structural counts used to resolve the 27-vs-29 discrepancy and the additional_facts
evidence question.
