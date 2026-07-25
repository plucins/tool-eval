# Solution Exploration: Expand Single-Tool Report Content Model

## Problem Reframing

### Research Question

What content should tool-eval's single-tool profile/report contain (use cases, built-in
tools, and other sections) for a full AI-tool overview?

### How Might We Questions

- **HMW1**: How might we let a user see a fuller, richer report for *one* tool, given no
  dedicated single-tool render path exists today (only a tab pane inside the multi-tool
  comparison document)?
- **HMW2**: How might we group the sprawling, flat `feature_results`/`additional_facts`
  arrays into named, scannable sections (e.g. "Built-in tools," "Pricing & licensing")
  without inventing new comparison machinery for non-comparable content?
- **HMW3**: How might we represent "known limitations" — a section every external source
  treats as standard, but which this project has no clean data home for and which is
  structurally hard to source to the official-sources-only standard?
- **HMW4**: How might we close the two genuine "built-in tools" taxonomy gaps (vendor-bundled
  linters/formatters distinct from AI-consumed lint integration; named sub-agent
  enumeration) without violating YAGNI or triggering unjustified curation-gate overhead?
- **HMW5**: How might we let a report show a point-in-time "last ~10 releases" changelog for a
  tool that keeps shipping after the profile is researched, given the project's deterministic
  core forbids fetching new release data at render time and there is today no schema field,
  taxonomy feature, or `profile-sections.yaml` section for release/version history at all?

---

## Explored Alternatives

## Decision Area 1 — How to Render a Single-Tool Report At All

### Alternative 1A: Enrich the existing tab pane in place (no new template, no new CLI verb)

Extend `comparison.html.j2`'s per-tool tab pane (`:176-226`) and `render_comparison_html`
(`html.py:103-136`) to render the fields the schema already carries but the template drops:
`use_case.rationale`/`.supporting_features`/`.evidence`, `additional_fact.evidence`, and
`feature_results` grouped by taxonomy group under headings (e.g. "Built-in tools"). No new
render function, no new CLI verb, no new output artifact — the single-tool report remains
"a tab inside the comparison document," just a much richer one.

- **Strengths**: Zero new infrastructure. Directly targets the research report's own
  highest-priority, lowest-risk item (§6 #10: "richer rendering of existing fields ... the
  data already exists"). No schema change, no CLI surface change, no new render/model code
  path to test and maintain. Fully consistent with YAGNI — the report explicitly frames this
  as answering most of the brief already.
- **Weaknesses**: Still requires `compare build --tools <a> <b>` (2+ tools) to produce any
  HTML at all (`cli.py:481-487` — `compare build` has no single-tool path) — a user wanting
  *just* one tool's report still has to run a comparison and click into a tab. Doesn't
  produce a standalone, shareable single-tool artifact (e.g. to email a stakeholder one
  tool's report). The comparison grid framing ("vs. other tools") stays baked into the
  document chrome even when the user only cares about one tool.
- **Best when**: The primary use case is "look at one tool's detail while already in a
  comparison session," not "produce a standalone single-tool deliverable." Evidence: research
  report §4.2, §6 row 10, §9 conclusion 1.
- **Evidence links**: Research report §4.2 (current tab-pane content), §4.3-4.4 (schema vs.
  template gap), §6 row 10 (priority-1 recommendation), synthesis "Pattern: schema capability
  regularly exceeds render capability."

### Alternative 1B: New standalone single-tool template + new `profile show`/`render` CLI verb

Add a new Jinja2 template (e.g. `profile.html.j2`), a new render function (e.g.
`render_profile_html`) parallel to `render_comparison_html`, and a new `profile show <tool_id>`
or `profile render <tool_id>` CLI verb that emits a standalone, self-contained HTML file (no
comparison grid, no other tools) to a new output location (e.g. `outputs/profiles/`).

- **Strengths**: Produces a genuinely shareable, single-tool deliverable — closer to what an
  external stakeholder or a "send me the Cursor report" request actually wants. Cleanly
  separates single-tool concerns (rich narrative, all fields) from comparison-grid concerns
  (flags, scoring, cross-tool table), which the research explicitly notes are architecturally
  different renders (comparison model is "inherently multi-tool by shape," §4.1).
- **Weaknesses**: New infrastructure on every axis the constraints call out: a new render
  function, a new template (still Jinja2+markdown-it+nh3, so no *new* tech, but new code
  surface), a new CLI verb, a new output directory convention, and duplicated
  sanitization/asset-embedding logic unless carefully factored to share code with
  `render_comparison_html`. Meaningfully more effort and testing surface than 1A for a
  research question the report itself concludes is "overwhelmingly a rendering expansion,"
  not a call for new product surface. Two render paths must now both be updated whenever a
  profile field changes, unless a shared partial/macro is factored out immediately — a real
  maintenance-burden risk the report doesn't flag but is a direct consequence of this
  alternative.
- **Best when**: There's a stated, current need for standalone single-tool exports (e.g. for
  external distribution, README embedding, or archival) rather than just "reading it in the
  app." Nothing in the research findings or brief establishes that need today.
- **Evidence links**: Research report §4.1 (no render path exists, no `profile show/render`
  verb), §7 constraint 4 (existing stack only — satisfied, but adds surface), §7 constraint 6
  (YAGNI — this is the alternative most exposed to a YAGNI objection).

### Alternative 1C: Hybrid — reuse `render_comparison_html`'s Jinja environment/partials, but add a thin single-tool template and CLI verb that renders one tool through a shared macro set

Extract the per-tool tab-pane markup from `comparison.html.j2` into a Jinja include/macro
(e.g. `_tool_detail.html.j2`) used both by the existing multi-tool tab loop and by a new,
minimal single-tool template that wraps one instance of that macro plus a page shell (title,
nh3-sanitized style, no grid). Add a `profile show <tool_id>` CLI verb that calls this new
thin render path.

- **Strengths**: Gets the standalone-artifact benefit of 1B without the duplication risk —
  the actual per-tool content markup lives in exactly one place, so 1A's richer-rendering work
  (which must happen regardless, per the report's own priority ordering) directly benefits
  both the tab pane and the standalone report. Bounds the new-code surface to: one macro
  extraction, one thin wrapper template, one CLI verb, one render function that composes the
  macro — no duplicated field-rendering logic.
- **Weaknesses**: Still adds a new CLI verb and a new render function (real, if smaller, new
  surface) — same YAGNI question as 1B applies, just with less downside if pursued. Requires
  disciplined refactor discipline (the macro extraction must happen before or alongside the
  content-rendering work, not after, or the team ends up doing 1A's work twice). Slightly more
  upfront design cost than 1A for a benefit (standalone artifact) that isn't yet a stated
  requirement.
- **Best when**: There's reasonable confidence that a standalone single-tool artifact will be
  wanted eventually, and the team wants to avoid paying the duplication cost of building 1A
  now and 1B later on separately-maintained markup.
- **Evidence links**: Research report §4.1 (single dependency chain, no branch point today),
  synthesis "Relationships and Dependencies" (`render_comparison_html` → `comparison.html.j2`
  is a single chain; extending it is editing existing markup, building standalone is new
  infrastructure).

### Recommended Alternative: 1A (enrich the existing tab pane in place)

**Rationale**: The research report is explicit and high-confidence that this is "overwhelmingly
a rendering expansion" against data that already exists, and ranks richer-field-rendering as
the single highest-value, lowest-risk starting point (§6 row 10, §9). Nothing in the brief or
findings establishes a current need for a standalone, shareable single-tool artifact — that
need is plausible but unconfirmed, which is exactly the YAGNI test the constraints require
("every new section needs an explicit rationale beyond industry parity," §7 constraint 6). 1C
is a reasonable fallback if the standalone-artifact need is later confirmed; it should reuse
whatever markup 1A produces rather than starting over. 1B is not recommended as a first move —
it pays new-infrastructure cost today for a benefit that isn't yet demonstrated to be needed.

---

## Decision Area 2 — How to Group Existing feature_results/additional_facts into Named Sections

### Alternative 2A: Free-text `topic` matching (no schema change)

Group `additional_facts` under report headings by pattern-matching known `topic` strings
(e.g. any fact whose topic contains "pricing," "plan," or "tier" language lands under
"Pricing & licensing") using a hardcoded set of match rules in the template/render layer.
`feature_results` grouping is already schema-clean — group by the existing `group:` field
directly, no matching needed there.

- **Strengths**: Zero schema change, zero new config artifact, fastest to implement — pure
  render-layer logic. No impact on `additionalProperties: false` at any schema level (D-016).
- **Weaknesses**: Fragile by construction — a worker writing a fact with topic "Cost
  overview" instead of "Pricing tiers" silently falls outside every match rule and the fact
  either lands in an "Other" bucket or is dropped from grouped display entirely, with no
  validation-time signal that anything went wrong. Matching logic drifts from actual
  profile-writing behavior over time and is invisible until a human notices a
  miscategorized/missing fact in rendered output. No mechanism enforces or documents the
  expected vocabulary for future profile-writing workers.
- **Best when**: The set of tools/profiles is small and stable enough that a human can spot-
  check miscategorization quickly (true today — 5 profiles), and schema-change overhead isn't
  justified for a grouping need that's cosmetic, not comparability-driven.
- **Evidence links**: Research report §6 row 1 ("group facts whose topic matches a recognized
  set"); §4.4 (16 real facts across 5 profiles, ad hoc topics, no canonical list).

### Alternative 2B: Add an optional categorization/discriminator field to `additional-fact.schema.json`

Add an optional enum field (e.g. `category: "pricing" | "security" | "deployment" |
"extensibility" | "target_audience" | "other"`) to `additional-fact.schema.json`, populated by
the profile-writing worker at fact-creation time. The render layer groups deterministically on
this field instead of matching prose.

- **Strengths**: Deterministic, robust grouping — no drift risk, no silent miscategorization.
  Makes the "recommended topics" checklist concept (research report §4.4's "canonical topic
  checklist" idea) machine-checkable rather than aspirational. Small, additive schema change
  (optional field, not a new required constraint) — satisfies D-016 (schema is the source of
  truth for new first-class concepts) without breaking existing profiles (no `minItems`/
  `required` addition needed, so old profiles remain valid without a `template_revision` bump).
- **Weaknesses**: Real schema change — goes through the schema-change discipline the standards
  call for, however lightweight. Every profile-writing worker/skill must be updated to
  populate the new field going forward, or facts silently fall into "other" with no
  enforcement (same failure mode as 2A, just for a smaller "other" bucket instead of failing
  every match). Doesn't retroactively categorize the 16 existing facts across 5 real profiles
  — those stay uncategorized until re-researched, which is unlikely to happen purely for this.
- **Best when**: Deterministic, durable grouping is valued over implementation speed, and the
  team is comfortable evolving the profile-writing worker prompt/skill alongside the schema
  change (schema changes here are cheap in isolation, but only pay off if paired with a worker-
  side update).
- **Evidence links**: Research report §6 row 1 ("cleaner: add an optional discriminator/
  category"); §7 constraint 2 (D-016, schema as source of truth); synthesis "Pattern: a single
  generic container is absorbing most literature-style content."

### Alternative 2C: Config-driven mapping table (e.g. new `additional-fact-sections.yaml` or extending `profile-sections.yaml`)

Introduce a versioned config file mapping known `fact_id`/`topic` strings and `feature_id`s to
report section headings (e.g. `pricing_tiers: "Pricing & licensing"`,
`mcp_or_plugin_extensibility: "Extensibility & MCP ecosystem"`), maintained as a revisioned
YAML artifact the same way `feature-taxonomy.yaml` and `profile-sections.yaml` already are in
this project.

- **Strengths**: No schema change to `additional-fact.schema.json` — existing profiles remain
  valid as-is, no worker-prompt change required for existing facts. Fits the project's existing
  pattern of revisioned YAML config for exactly this kind of mapping (`feature-taxonomy.yaml`
  already maps `feature_id` → `group`; this is a direct structural analog). Easy to extend
  incrementally (add a new mapping line) without touching schema or render code, once the
  render layer is built to consult the config.
- **Weaknesses**: A new config artifact to create, document, and keep in sync as new fact
  topics appear — mapping table maintenance burden shifts from "schema enforcement" to "someone
  remembers to update the YAML," which is a softer guarantee than 2B's structural field. Still
  has to match on `fact_id`/`topic` strings for facts not yet in the table (same drift risk as
  2A, just centralized in one file instead of scattered template logic) — new/unmapped facts
  fall into an "Other" bucket rather than failing outright, which is better than 2A but not as
  robust as 2B.
- **Best when**: The team wants centralized, auditable, versioned control over section mapping
  (consistent with how `feature-taxonomy.yaml`'s revision already governs `profile_state`)
  without paying a schema-change cost, and is comfortable with "Other" as an acceptable overflow
  bucket for anything not yet mapped.
- **Evidence links**: Research report §7 constraint 6 (YAGNI, prefer generic/data-driven
  mechanisms); project convention already established by `feature-taxonomy.yaml`'s `group:`
  field and `profile-sections.yaml`'s existing revisioned-config pattern (`config/profile-
  sections.yaml:1-5`).

### Alternative 2D: Combination — `feature_results` grouped by existing `group:` field (needs no new mechanism at all) + `additional_facts` grouped via config mapping (2C), with 2B deferred

Recognize that `feature_results` grouping needs *no new mechanism whatsoever* — the taxonomy's
`group:` field (`code_authoring`, `agentic_execution`, `context_quality`, `workflow_ecosystem`,
`security_governance`) already exists, is already 100% populated for every feature, and needs
only a render-layer heading per group. Apply 2C only to `additional_facts`, and treat 2B (schema
discriminator) as a future upgrade path if 2C's config-mapping approach proves too manual over
time.

- **Strengths**: Recognizes that the two grouping problems (`feature_results` vs.
  `additional_facts`) are not actually the same problem — `feature_results` is already
  schema-clean and needs zero new mechanism, so bundling it into the same
  schema-change/config-table discussion as `additional_facts` overstates the work needed.
  Minimizes total new mechanism to exactly one (the config mapping), applied only where it's
  actually needed.
- **Weaknesses**: Splits the "grouping" story into two different code paths (direct
  `group:`-field grouping for features, config-table lookup for facts) rather than one uniform
  mechanism — a minor consistency cost, though arguably the honest reflection of the two data
  channels' genuinely different maturity (per synthesis: "rigor is proportional to
  comparability, not to importance").
- **Best when**: The team wants to avoid solving an already-solved problem (`feature_results`
  grouping) while still addressing the real gap (`additional_facts` grouping) with the
  lowest-maintenance-burden mechanism available.
- **Evidence links**: Research report §5.1 ("group the six existing feature_ids... reusing the
  taxonomy's own rich per-feature definitions"), §6 rows 1-4 (all four sections map cleanly to
  existing `feature_id`s plus informal facts); synthesis "Pattern: rigor is proportional to
  comparability, not to importance."

### Recommended Alternative: 2D (feature_results grouped natively by existing `group:` field; additional_facts grouped via a new config-mapping table per 2C), with 2B flagged as a future upgrade

**Rationale**: This decomposes the problem correctly instead of treating "grouping" as one
monolithic decision. `feature_results` grouping is already free — the taxonomy's `group:` field
is schema-complete and 100%-populated today (research report §5.1), so no new mechanism is
needed there at all. For `additional_facts`, 2C (config mapping) is preferred over 2A (raw
string matching) because it centralizes and versions the mapping the same way this project
already versions `feature-taxonomy.yaml` and `profile-sections.yaml` — consistent with
established convention, no schema change, and an explicit "Other" overflow bucket makes drift
visible rather than silent. 2B (schema discriminator) is the more robust long-term answer and
should be revisited if the config-table approach proves to need frequent, error-prone updates
in practice — but per YAGNI (§7 constraint 6), a schema change is not justified until the
lighter-weight config approach demonstrably fails.

---

## Decision Area 3 — How to Model "Known Limitations"

### Alternative 3A: Repurpose `unresolved_issues` (add a new `kind` enum value, e.g. `known_limitation`)

Add `known_limitation` to the existing `kind` enum in `profile.schema.json`'s inline
`unresolved_issues` array (`:72-75`, currently `conflict | access_gap | coverage_gap |
prompt_injection_warning | other`), and render these entries as a "Known limitations" section
in the report.

- **Strengths**: Smallest possible schema change (one enum value, not a new object). Reuses an
  existing, already-wired array (`issue_id`, `kind`, `feature_id`, `description`,
  `related_source_ids`) rather than inventing new structure.
- **Weaknesses**: Semantically awkward — `unresolved_issues` is currently framed as
  process/research-quality issues (research conflicts, access gaps, coverage gaps, prompt-
  injection warnings) surfaced *by this project's own research process*, not user-facing
  product limitations reported by the tool's community. Overloading the same array conflates
  "our research had a gap" with "the tool itself has a known weakness," which are different
  audiences and different sourcing standards. Existing consumers of `unresolved_issues` (if
  any exist in curation/repair flows) would need to be checked for assumptions about what
  `kind` values mean, since `kind` currently reads as exclusively about the research process
  itself, not the tool's product limitations.
- **Best when**: The team is comfortable treating "known limitations" as conceptually adjacent
  to research-process gaps, and the small enum addition is judged worth the semantic overload
  risk.
- **Evidence links**: Research report §6 row 5 ("could reuse `unresolved_issues`... if
  reframed"); `profile.schema.json:64-84` (existing `kind` enum and required fields).

### Alternative 3B: New lightweight schema construct dedicated to limitations (e.g. `known_limitations` array, structurally parallel to `additional_facts` but explicitly framed as critical/comparative)

Add a new top-level array, structurally similar to `additional-fact.schema.json` (id, short
label, description, evidence) but with its own schema file and its own semantic framing as
"a documented limitation or common complaint about the tool," distinct from both
`unresolved_issues` (research-process gaps) and `additional_facts` (neutral facts).

- **Strengths**: Cleanest semantics — a dedicated home means the section's sourcing standard
  (community/blog-sourced content, inherently harder to hold to official-sources-only rigor)
  can be made explicit in the schema's own description field, exactly the way
  `additional-fact.schema.json` already documents its own sourcing expectation in its
  `description` field. Doesn't overload an existing construct's meaning.
- **Weaknesses**: The most schema/process work of any alternative here — a new schema file, a
  new top-level `profile.schema.json` property (another `additionalProperties: false`
  boundary to cross), new render logic, and critically, a real answer to the sourcing problem
  the report flags: limitations are "self-reported community/blog material" that would need
  independent, official-source verification per research-protocol before being asserted
  (§6 row 5) — a new construct doesn't solve that sourcing tension, it just gives the
  unsolved tension a nicer home. Highest effort for a section the report itself flags as the
  one non-mechanical decision requiring real thought before any rendering work.
- **Best when**: There's a stated intent to invest in limitations as a first-class, durable
  report feature and the team has a credible plan for satisfying official-sources-only rigor
  for community-sourced claims (e.g. only including limitations independently confirmed via
  vendor changelogs/issue trackers, not raw blog sentiment).
- **Evidence links**: Research report §6 row 5, §7 constraint 3 (official-sources-only,
  no fabrication), §9 conclusion 3 (limitations "would need its own decision... before it
  could be populated at the same rigor as the rest of the profile").

### Alternative 3C: Model purely as an `additional_facts` entry with a conventional topic name (e.g. `topic: "Known limitations"`), no schema change

Treat limitations exactly like any other `additional_facts` entry — same schema, same
evidence-optional structure, distinguished only by a conventional topic string, grouped under
its own heading via the Decision-Area-2 mechanism (2D's config-mapping table).

- **Strengths**: Zero schema change — reuses 2D's grouping mechanism directly (map
  `topic: "Known limitations"` or similar to a "Known limitations" heading in the config
  table). Fastest to ship if the team decides this section is worth adding at all. Consistent
  with the report's broader theme that `additional_facts` is already the default landing zone
  for literature-derived content not covered by the taxonomy (synthesis "Pattern: a single
  generic container... is absorbing most literature-style content").
- **Weaknesses**: Inherits `additional_facts`' existing structural gap at full strength — no
  curation gate, no schema-enforced evidence requirement (§7 constraint 5; synthesis
  "Ambiguity resolved... additional_facts protocol rigor"), and this is precisely the section
  type where that gap matters most, since limitations are explicitly the hardest content to
  source to the official-sources-only standard in the first place. Doesn't semantically
  distinguish "this is a neutral fact" from "this is a critical/comparative claim about a
  weakness" — a reader has no signal that this fact category carries a different (weaker, per
  current schema) evidentiary bar than, say, a pricing fact.
- **Best when**: The team wants the lowest-cost way to add the section but accepts that doing
  so surfaces (does not create, but foregrounds) the existing `additional_facts` rigor gap the
  research already flagged as a known asymmetry.
- **Evidence links**: Research report §6 row 5 ("a new `additional_facts`-style entry");
  synthesis "Ambiguity resolved via direct check — additional_facts protocol rigor" (full
  section); §7 constraint 5.

### Alternative 3D: Do not add a "known limitations" section now

Explicitly decline to add this section in the current iteration. Revisit only if a specific,
concrete sourcing approach for community/blog-derived limitations claims is worked out
separately (e.g. as its own small research/standards task), given that this section is the one
place the research findings themselves flag a genuine tension with the project's own
official-sources-only, no-voting research protocol.

- **Strengths**: Directly honors the research report's own caveat rather than working around
  it — the report explicitly says this section "would need its own decision... before it could
  be populated at the same rigor as the rest of the profile" and ranks it last-but-one in
  priority (§6, ordering note), specifically flagging the sourcing-rigor mismatch as the
  reason. Avoids shipping a report section whose evidentiary bar is quietly lower than every
  other section in the same document, which risks misleading a reader who doesn't notice
  the difference. Zero schema/process/effort cost.
- **Weaknesses**: Leaves a section every external comparison source treats as standard
  (research report §6 row 5's external corroboration) absent from tool-eval's output, which
  is a real, acknowledged gap versus industry norms — this alternative is explicitly punting on
  the brief's "complete AI-tool overview" framing for one section, not fully answering it.
- **Best when**: The team is not prepared, in this iteration, to resolve how community/blog-
  sourced limitation claims can meet the official-sources-only bar (§7 constraint 3), and
  would rather ship nothing than ship something under-sourced relative to the rest of the
  report.
- **Evidence links**: Research report §6 row 5 (the sourcing-rigor caveat, in the gatherer's
  own words); §9 conclusion 3 ("would need its own decision... before it could be populated at
  the same rigor"); §7 constraint 3 (official-sources-only, no fabrication).

### Recommended Alternative: 3D (do not add the section now), with 3C as the fallback if the user wants it anyway

**Rationale**: This is the one decision area where the research itself supplies a strong,
explicit reason to prefer inaction: the report's own sourcing-rigor caveat (limitations are
typically community/blog-sourced, which is structurally harder to reconcile with this
project's official-sources-only, no-source-voting research protocol than any other candidate
section) is not a minor implementation detail — it is a genuine tension between the section's
industry-standard content and this project's core evidentiary standard. Shipping 3A or 3B
before that tension is resolved risks either overloading an existing construct's meaning (3A)
or investing real schema effort in a construct that still can't answer the sourcing question
(3B). If the user nonetheless wants this section now, 3C is the pragmatic fallback — it's
honest about reusing the existing lower-rigor `additional_facts` channel rather than pretending
a new schema construct solves the sourcing problem it doesn't actually solve.

---

## Decision Area 4 — Whether/How to Close the Two "Built-In Tools" Taxonomy Gaps

(Vendor-bundled linters/formatters as distinct from AI-consumed static-analysis integration;
named/branded sub-agent enumeration.)

### Alternative 4A: Promote each gap to a full taxonomy `feature_id` (goes through the single curation gate)

Add two new feature_ids to `feature-taxonomy.yaml` (e.g. `bundled_formatter_linter` and
`named_subagent_roles`), each with full `has_criteria`/`partial_criteria`/`exclusions`/
`aliases`/`research_question` definitions, processed through `curation.py`'s single curation
gate (`curate_candidates`/`accept_feature_into_taxonomy`) like any other taxonomy candidate.

- **Strengths**: Gives both concepts full has/partial/not_found comparability across every
  tool, the same protocol rigor (search trace, not-found completeness, evidence requirements)
  as the other 29 features (research report §4.5, §5.1). Consistent, structurally, with how
  every other comparable capability in this taxonomy is modeled — no special-casing.
- **Weaknesses**: Highest cost of the three alternatives — requires re-researching all 5
  existing profiles against the new feature_id(s) (a `taxonomy_revision` bump means existing
  profiles at the new revision need `has`/`partial`/`not_found` status recorded, or they're
  marked `requires_research`, per the project's own revision-staleness mechanism observed in
  §4.5's revision-1-vs-4 profile split). Goes through the full curation gate for two concepts
  that, per the report, currently have no stated comparability need — this is exactly the
  "industry parity alone is not sufficient rationale" case the YAGNI standard warns against
  (§7 constraint 6).
- **Best when**: Cross-tool comparability on these two specific points becomes a stated user
  need (e.g. "does tool X ship a formatter that tool Y doesn't" becomes a real
  decision-relevant question), justifying the re-research and curation-gate cost.
- **Evidence links**: Research report §5.2 (both gaps described, with explicit curation-gate
  path noted as option (a)); §7 constraint 5 (same rigor for any new taxonomy feature).

### Alternative 4B: Model via `additional_facts` only (no taxonomy change)

Represent both concepts as ordinary `additional_facts` entries (e.g. `fact_id:
bundled_formatter`, `topic: "Bundled tooling"`; `fact_id: named_subagents`, `topic: "Named
sub-agent roles"`), grouped under the "Built-in tools" heading via the Decision-Area-2
mechanism (2D), with no schema/taxonomy change at all.

- **Strengths**: Lowest cost — no taxonomy revision, no re-research of existing profiles, no
  curation-gate involvement, immediately available to any profile-writing worker today. The
  research report explicitly names this as "the lower-cost starting point" per YAGNI
  (§5.2, closing paragraph). Both concepts can appear in the report right away without
  blocking on any process change.
- **Weaknesses**: No has/partial/not_found comparability — a reader can't scan the comparison
  grid to see which tools have/lack bundled formatters or named sub-agents the way they can for
  every other "built-in tool" concept; these two would sit visually adjacent to, but
  structurally different from, their five taxonomy-backed siblings in the same "Built-in
  tools" section, which the report itself groups together (§5.1). Inherits `additional_facts`'
  lighter-weight evidence discipline (no schema-enforced `minItems`, no curation gate) for
  content that is otherwise conceptually a "capability," which is exactly the kind of content
  the taxonomy exists to hold at higher rigor (synthesis "Pattern: rigor is proportional to
  comparability, not to importance").
- **Best when**: No stated cross-tool comparability need exists yet for these two concepts
  specifically (true today, per the report), and the priority is getting *some* representation
  of them into the report quickly.
- **Evidence links**: Research report §5.2 (explicitly recommends this as lower-cost option
  (b)); synthesis "Pattern: a single generic container... is absorbing most literature-style
  content."

### Alternative 4C: Do nothing now; revisit only if a specific tool-profile need arises (YAGNI-driven deferral)

Neither add a taxonomy feature nor an `additional_facts` entry for either gap in this round of
work; leave both concepts entirely unrepresented until a concrete profile-writing need
surfaces them organically (e.g. a worker researching a specific tool finds a bundled-formatter
claim worth recording and adds an ad hoc `additional_facts` entry for that one tool at that
time, without a prior decision to formalize the concept project-wide).

- **Strengths**: Truest form of YAGNI — no upfront modeling decision at all, deferred entirely
  until real research work naturally produces the need. Zero cost today.
- **Weaknesses**: Leaves the "Built-in tools" section (Decision Area 1/2's grouped heading)
  incomplete relative to what the external research corroborates as a real, named market
  differentiator (Claude Code's plugin system bundling "slash commands, agents, MCP servers,
  and hooks" as distinct nameable extension points, per external-best-practice findings cited
  in §5.2) — the gap the report identifies would simply persist unaddressed, with no
  convention even for an ad hoc future entry, risking inconsistent, uncoordinated modeling
  later (one worker calls it `bundled_formatter`, another calls it `builtin_linter` for a
  different tool, with no shared `fact_id`/topic convention to align them).
- **Best when**: The team judges even the low-cost 4B path isn't justified without a concrete
  trigger, and is comfortable with these two named gaps (which the research did identify as
  genuine, not speculative) remaining fully unaddressed for now.
- **Evidence links**: Research report §5.2 (gaps identified as genuine, not hypothetical);
  §7 constraint 6 (YAGNI: "every new section needs an explicit rationale beyond industry
  parity").

### Recommended Alternative: 4B (model via `additional_facts` only, no taxonomy change)

**Rationale**: This is the research report's own explicit recommendation (§5.2: "the
additional_facts route is the lower-cost starting point; promoting to a full taxonomy feature
is justified only if comparability across tools becomes a stated need"). Both gaps are
genuine and externally corroborated (not speculative), so 4C's "do nothing" is a weaker fit
here than it is a legitimate answer might be elsewhere — these are named, real market
differentiators the report found evidence for, not a hypothetical extension. But nothing in
the research establishes a current comparability need strong enough to justify 4A's
re-research-all-profiles-plus-curation-gate cost. 4B threads this: it gets both concepts into
the report now, at low cost, leaving 4A available as a later upgrade if a user or downstream
task states a specific comparability requirement (e.g. "I need to know which tools ship their
own formatter" as a scored/flagged comparison axis, not just descriptive text).

---

## Decision Area 5 — How to Model and Source a "Changelog / Last N Releases" Section

(New scope, added mid-workflow, not covered by the original four gatherers — see note below.)

**Note on evidence base**: unlike Decision Areas 1-4, no findings file or synthesis pass exists
for this concept — the original research task scoped four gatherers (codebase, example-profiles,
docs, external-best-practice) around use cases and built-in tools, not release/version history.
The alternatives below are grounded directly in the project's own constraints as restated in this
follow-on scope brief (`architecture.md`'s deterministic-core rule, D-016's schema-as-source-of-
truth, `security.md`/`research-protocol.md`'s official-sources-only rule, and the `research.
researched_at`/`profile_state` point-in-time convention already present in `profile.schema.json`)
plus the existing `additional-fact.schema.json`/`use-case.schema.json` structural pattern
observed directly in the codebase. No claim below is attributed to the four original gatherers.

### Alternative 5A: New structured `release_history` schema array (mandatory evidence per entry)

Add a new top-level array to `profile.schema.json` (crossing its `additionalProperties: false`
boundary per D-016), e.g. `release_history`, with items validated by a new
`release-history-entry.schema.json` structurally parallel to `additional-fact.schema.json` and
`use-case.schema.json`: `{release_id, version, release_date, summary, evidence: [{source_id,
excerpt}]}`. Unlike `additional_facts` (where `evidence` is optional) and `use_cases` (where
`evidence` is only conditionally required for `kind: documented`), every `release_history` entry
would require `evidence` unconditionally (`minItems: 1`) — a version number and release date are
inherently point-in-time factual claims with no legitimate "inferred" variant the way an
`inferred` use case has. Populated by a research worker under `.claude/` reading the vendor's
official GitHub Releases page or changelog at research time; the Python core only ever reads the
resulting stored array — no network/model call happens at render time.

- **Deterministic-core fit**: Full compliance — identical shape to how `feature_results` and
  `use_cases` are already populated (worker gathers at research time, core renders stored JSON).
  No new render-time behavior is introduced.
- **Official-sources-only fit**: Strongest of the four alternatives — mandatory, unconditional
  evidence per entry means every version/date claim must cite a real `source_id` (GitHub Releases
  page, vendor changelog, official release-notes blog), with no schema path to assert a version
  number without a citation, closing exactly the gap `additional-fact.schema.json` currently
  leaves open (evidence there is optional despite the schema's own stated intent).
- **Staleness handling**: Structurally acknowledges but does not solve staleness — the array is
  exactly as point-in-time as the rest of the profile (bound to `research.researched_at`), and a
  vendor shipping release #11 the week after publication makes the section incomplete, not wrong;
  this alternative's only defense against a misleadingly "current-looking" list is a rendered
  freshness caveat (see Alternative 5D and the Recommended Approach below), not anything in the
  schema itself.
- **Strengths**: Per-version structure a reader can actually scan/sort (version, date, summary
  as distinct fields, not buried in prose); strongest evidence discipline of any alternative
  here, arguably tighter than `additional_facts`' own current practice; consistent with the
  project's established "documented" epistemic pattern (mirrors `use-case.schema.json`'s
  conditional evidence requirement, made unconditional here since there's no legitimate
  "inferred" release).
- **Weaknesses**: Real schema-change cost — new schema file, new top-level property, a new
  `additionalProperties: false` boundary crossing, and a worker/skill update to actually populate
  it; existing published profiles have no `release_history` and would render an empty/absent
  section until re-researched. Highest process cost of the four alternatives, though smaller than
  a full taxonomy `feature_id` (no curation-gate involvement, since this isn't a comparable
  has/partial/not_found capability).
- **Best when**: The team wants the report to make an explicit, structured, per-version claim
  (which is what the user's brief literally asks for — "clearly showing which version... a
  what's new summary per release") and is willing to pay a one-time schema/worker cost for it.
- **Evidence links**: Project constraints as restated in this task's brief (deterministic-core/
  `architecture.md`, D-016/`validation.md`, official-sources-only/`security.md` +
  `research-protocol.md`); direct schema reads of `additional-fact.schema.json` and
  `use-case.schema.json` (the evidence-requirement pattern this alternative extends).

### Alternative 5B: Single `additional_facts` entry with a prose "what's new" summary

Model the whole section as one ordinary `additional_facts` entry (e.g. `fact_id:
recent_release_history`, `topic: "Release history"`), whose `description` is an LLM-authored
prose paragraph summarizing the last ~10 releases, with a single shared `evidence` array (per
`additional-fact.schema.json`'s existing, optional-evidence shape) citing the changelog/releases
page it was drawn from. No schema change.

- **Deterministic-core fit**: Full compliance, same as 5A — worker gathers at research time, core
  only renders stored text.
- **Official-sources-only fit**: Weaker than 5A — `additional_facts`' `evidence` field is
  optional at the schema level (confirmed by direct schema read; synthesis notes this is a
  known, code-confirmed rigor gap versus `feature_results`/`use_cases`), and even where evidence
  is attached, one shared evidence array covers an entire multi-release prose summary rather than
  citing each version claim individually — a reader (or a future auditor) cannot tell which
  specific version/date claim inside the prose maps to which cited excerpt.
- **Staleness handling**: Same underlying point-in-time limitation as 5A, but harder to caveat
  cleanly — a single prose block doesn't have a natural per-entry place to hang a "current as of"
  marker the way a table row does; the whole paragraph either reads as current or the caveat has
  to apply blanket-style to undifferentiated prose.
- **Strengths**: Lowest cost of any alternative that still asserts real version content
  (no new schema file, no new top-level property, immediately usable by any profile-writing
  worker today) — genuinely the cheapest way to satisfy the user's literal request without any
  schema-change discipline.
- **Weaknesses**: No per-version structure a reader can scan, sort, or filter by (a limitation
  explicitly named in the task brief itself); inherits `additional_facts`' lighter evidence
  discipline for exactly the kind of specific, individually-checkable factual claims (version
  numbers, dates) that most benefit from per-item citation.
- **Best when**: The team wants the section shipped quickly and judges that a readable prose
  summary satisfies the brief well enough, without investing in per-version structure or
  strengthened evidence discipline.
- **Evidence links**: Direct schema read of `additional-fact.schema.json` (optional evidence,
  single shared array); synthesis "Pattern: a single generic container... is absorbing most
  literature-style content" (this alternative is a direct instance of that same pattern, applied
  to a genuinely new content type).

### Alternative 5C: Pointer-only — link out to the vendor's official changelog/releases URL, no versioned content asserted

Do not store or assert any version-specific data at all. Represent the section as a single
`additional_facts` entry (or, if the tool's `homepage`-style metadata is judged the better home,
a small addition there) whose content is limited to "see the official changelog at {url}" —
citing the changelog/releases *page's existence*, not any of its version-specific content.

- **Deterministic-core fit**: Full compliance — the stored URL is itself gathered at research
  time by a worker, and the Python core never fetches it at render time; the report merely
  displays a static link.
- **Official-sources-only fit**: Avoids the sourcing question by construction — since no
  version/date/summary claim is made, there is nothing that could be fabricated or go stale; the
  only fact asserted ("this URL is the tool's official changelog page") is trivially verifiable
  and durable.
- **Staleness handling**: Solves staleness completely, by not making the kind of claim that goes
  stale — a link to the vendor's own changelog is exactly as current the day a reader clicks it
  as it was the day it was researched, unlike any of the other three alternatives' embedded
  version data.
- **Strengths**: Zero schema change, zero ongoing staleness liability, cheapest to source (a
  worker only needs to confirm the changelog page exists and cite its URL, not read and
  summarize ~10 releases' worth of content).
- **Weaknesses**: Does not satisfy what the user actually asked for — a "review of the last ~10
  releases... with a what's new summary per release" rendered *in the report itself*. Pushes all
  the value (the actual release content) off-platform, which is a real functional regression
  relative to the brief, not just a lower-fidelity version of it.
- **Best when**: The team decides the staleness risk of asserting any version-specific content is
  not acceptable for this project's publication cadence, and is willing to trade away the user's
  literal ask (an in-report changelog) for a zero-liability pointer instead.
- **Evidence links**: `research.researched_at`/`profile_state: current|requires_research`
  convention in `profile.schema.json` (the point-in-time framing this alternative takes to its
  logical conclusion); project constraint restatement in this task's brief (staleness of a "last
  10 releases" claim flagged as the central design tension for this decision area).

### Alternative 5D: Same structured array as 5A, scoped by a "since last research" delta-and-cap policy plus a mandatory rendered freshness caveat

Use the same schema shape as 5A, but change the *population policy* the research worker follows:
instead of always fetching "the last 10 releases regardless of date," the worker captures
releases newer than the tool's previous profile's `research.researched_at` (or, for a first-ever
research pass, the most recent N up to a cap — e.g. 10), and the render layer always displays an
explicit "Release history reflects data available as of {researched_at}; check the vendor's
official channel for newer releases" caveat immediately above the section, regardless of how
recently the tool last shipped.

- **Deterministic-core fit**: Same as 5A — worker-gathered, core-rendered, no live calls.
- **Official-sources-only fit**: Same as 5A (mandatory per-entry evidence).
- **Staleness handling**: The one alternative that treats staleness as a first-class *policy*
  question, not just an accepted side effect. Anchoring capture to "since the previous research
  pass" keeps the list's implicit claim ("these are the releases you don't already know about")
  honest across re-research cycles, rather than a fixed "last 10" window that either re-lists
  releases the reader already saw in a prior report (if the tool ships slowly) or silently drops
  older-but-still-recent releases outside the fixed window (if the tool ships fast). The mandatory
  rendered caveat is the most direct mitigation of the "report claims 'last 10 releases,' goes
  stale within weeks" risk named in the task brief, and — unlike a caveat considered in isolation
  — this alternative treats it as a required rendering rule rather than an optional nicety.
- **Strengths**: Directly answers the brief's own framing of the central tension (staleness) with
  a concrete policy, not just an acknowledgment; reuses 5A's schema and evidence discipline
  unchanged, so it costs nothing beyond 5A's own schema-change price; degrades gracefully for a
  first-time research pass (cap at 10) and stays useful on every subsequent re-research (delta
  since last pass, capped at some sane maximum to avoid an unbounded list for a long-neglected
  profile).
- **Weaknesses**: Slightly more worker-logic complexity than 5A's simpler "always fetch last 10"
  rule (the worker needs the previous profile's `researched_at` as an input, which is available
  but adds a lookup step); the "since last research" framing is less immediately intuitive to a
  reader than a flat "last 10," and needs the rendered caveat to carry real explanatory weight
  (if the caveat is dropped or under-emphasized in rendering, this alternative's core advantage
  over 5A disappears).
- **Best when**: The team accepts 5A's schema/evidence approach but wants the population and
  rendering policy to actively manage the staleness risk rather than merely accept it as an
  inherent, unaddressed limitation of a point-in-time profile.
- **Evidence links**: `research.researched_at`/`taxonomy_revision`/`profile_state` fields already
  present in `profile.schema.json` (the mechanism this alternative's "since last research" policy
  reuses, rather than inventing a new timestamp concept); task brief's explicit framing of
  staleness as "the most important design tension for this specific decision area."

### Recommended Alternative: 5A/5D combined — structured `release_history` array with mandatory per-entry evidence, populated under 5D's since-last-research capping policy, with a mandatory rendered freshness caveat

**Rationale**: Unlike Decision Area 3's "known limitations" (where the research itself surfaced a
genuine, unresolved sourcing-rigor tension that justified deferring the section entirely), this
decision area has an unambiguous, official, first-party source available for every claim it would
make — a vendor's own GitHub Releases page or changelog is exactly the kind of official source
the research-protocol standard already treats as authoritative, with no community/blog-sourcing
ambiguity comparable to Decision Area 3's. That removes the strongest reason 3D had for declining
to build a section at all. Given that, and given the user explicitly asked for this section (this
is stated new scope, not a speculative industry-parity addition the way some of Decision Area 4's
gaps were), 5C's "pointer only" retreat gives up too much of what was actually requested, and 5B's
prose-only approach under-delivers on the explicit "clearly showing which version" structural ask
and inherits `additional_facts`' weaker evidence discipline for content that is unusually
well-suited to strict per-entry sourcing. 5A's schema shape — mandatory evidence, no schema-
sanctioned "inferred" variant — is the correct fit for content that is inherently either
documented-and-cited or not includable at all. 5D's population/rendering policy is adopted on top
of 5A because the staleness tension is real and worth actively managing (not just accepting) —
anchoring capture to the previous `researched_at` and mandating a rendered freshness caveat
directly answers the task brief's own framing of this as the central design tension, at no
additional schema cost over 5A alone.

**Key trade-off accepted**: a genuine schema change (new schema file, new top-level property,
worker/skill update) is required before this section can be populated at all — smaller than a
full taxonomy `feature_id` (Decision Area 4's Alternative 4A) since no curation gate or
cross-tool comparability is implied, but larger than any of the render-only work recommended in
Decision Areas 1/2/4.

**Deferred/out-of-scope idea**: any mechanism to auto-refresh the `release_history` section after
publication (e.g. a background job that re-checks the vendor's releases page and silently updates
a published profile) is explicitly out of scope — it would require a network/model call outside
the research-time worker path, directly violating the deterministic-core constraint
(`architecture.md`) that the Python core never calls a model or the network. The correct
mechanism for keeping this section current is the project's existing re-research/`profile_state:
requires_research` cycle, not a new live-refresh mechanism.

---

## Trade-Off Analysis

Ratings are relative, within each decision area, not an absolute cross-area scale.

### Decision Area 1 — Single-tool report rendering

| Alternative | Technical Feasibility | User Impact | Simplicity | Risk | Scalability |
|---|---|---|---|---|---|
| 1A: Enrich existing tab pane | High — pure template/render edit, no new code path | Medium — richer detail, but still requires a 2+-tool comparison run to view | High — no new mechanism | Low — no schema, no new CLI surface, easily reversible | Medium — scales with comparison feature; doesn't add a distinct single-tool artifact type |
| 1B: New standalone template + CLI verb | Medium — new render fn/template/CLI verb, real new surface | High — genuinely shareable single-tool artifact | Low — duplicate render logic unless carefully factored | Medium — new code path to maintain/test; duplication risk if not factored well | High — a clean, separate single-tool artifact scales well to future needs (export, archival) |
| 1C: Hybrid (shared macro, thin new template) | Medium — requires upfront macro-extraction discipline | High — same standalone benefit as 1B | Medium — one source of truth for content markup, but two entry points | Medium — new CLI verb/render fn, but lower duplication risk than 1B | High — best long-term scalability if standalone need materializes |

### Decision Area 2 — Grouping into named sections

| Alternative | Technical Feasibility | User Impact | Simplicity | Risk | Scalability |
|---|---|---|---|---|---|
| 2A: Free-text topic matching | High — fastest to build | Medium — works until a topic string drifts | Medium — matching rules grow ad hoc over time | Medium — silent miscategorization risk, no validation signal | Low — every new topic variant needs a new match rule |
| 2B: Schema discriminator field | Medium — schema change + worker prompt update needed | High — deterministic, durable grouping | Medium — one more schema field to maintain | Low — once populated, no drift risk; but requires coordinated rollout | High — most robust as fact volume/topic diversity grows |
| 2C: Config-driven mapping table | High — no schema change, follows existing YAML-config convention | Medium-High — centralized, auditable | High — consistent with `feature-taxonomy.yaml` pattern already in use | Low-Medium — mapping table must be kept current, but overflow ("Other") makes gaps visible | Medium-High — scales well if the table is actively maintained |
| 2D: feature_results native + facts via 2C (recommended) | High — reuses an already-solved sub-problem plus 2C | Medium-High — same as 2C for facts, "free" for features | High — least total new mechanism | Low — same profile as 2C, reduced scope | Medium-High |

### Decision Area 3 — Known limitations

| Alternative | Technical Feasibility | User Impact | Simplicity | Risk | Scalability |
|---|---|---|---|---|---|
| 3A: Repurpose unresolved_issues | High — one enum value | Low-Medium — semantically confusing to readers/maintainers | Medium — reuses existing structure but overloads meaning | Medium — conflates research-process gaps with product limitations | Low — the enum wasn't designed for this; awkward to extend further |
| 3B: New dedicated schema construct | Low — most schema/process work of the four | High if executed well — clean, explicit semantics | Low — genuinely new construct to design, test, maintain | Medium-High — doesn't solve the underlying sourcing-rigor problem, just relocates it | Medium — clean structure scales, but sourcing problem doesn't go away |
| 3C: additional_facts with conventional topic | High — zero schema change | Medium — content appears, but rigor is inconsistent with rest of report | High — reuses existing mechanism | Medium-High — surfaces the existing additional_facts rigor gap most acutely | Medium |
| 3D: Do not add now (recommended) | High — no work required | Low in the short term (section absent) but avoids a misleading section | High | Low — avoids shipping under-sourced content | N/A — deferred, not scaled |

### Decision Area 4 — Built-in tools taxonomy gaps

| Alternative | Technical Feasibility | User Impact | Simplicity | Risk | Scalability |
|---|---|---|---|---|---|
| 4A: Full taxonomy feature_id | Low-Medium — curation gate + re-research of 5 profiles | High — full comparability | Low — most process overhead | Medium — schema/taxonomy revision bump affects all profiles' staleness state | High — best long-term comparability |
| 4B: additional_facts only (recommended) | High — no process change, immediately usable | Medium — descriptive but not comparable | High — reuses existing mechanism | Low-Medium — inherits additional_facts' lighter rigor, acceptable for non-comparable content | Medium |
| 4C: Do nothing now | High — zero effort | Low — real, corroborated gaps remain fully unaddressed | High | Low effort/risk today, but risk of uncoordinated ad hoc modeling later | Low |

### Decision Area 5 — Changelog / release history section

| Alternative | Technical Feasibility | User Impact | Simplicity | Risk | Scalability |
|---|---|---|---|---|---|
| 5A: Structured `release_history` array, mandatory evidence | Medium — new schema file + top-level property + worker/skill update | High — per-version structure matches the literal ask | Medium — one more schema construct, but follows an established pattern (use-case/additional-fact shape) | Medium — staleness is real but bounded to the profile's own point-in-time convention; no live-refresh risk | Medium — scales fine per-tool; doesn't yet solve the "list overlaps across re-research passes" problem |
| 5B: additional_facts prose entry | High — zero schema change | Medium — content appears, but not scannable/sortable per-version | High — reuses existing mechanism | Medium — inherits additional_facts' lighter, single-shared-evidence discipline for specific, individually-checkable claims | Low-Medium — a growing prose block gets harder to keep useful over successive re-research passes |
| 5C: Pointer-only, no versioned content | High — trivial to source and render | Low — pushes the actual content off-report, under-delivers the ask | High — simplest possible implementation | Low — no version-specific claim can ever go stale or be wrong | High — trivially maintainable regardless of how often the tool ships |
| 5D: 5A + since-last-research capping policy + mandatory freshness caveat (recommended) | Medium — same schema cost as 5A, plus a small worker-logic addition (previous `researched_at` lookup) | High — same structural benefit as 5A, with the staleness risk actively managed rather than merely accepted | Medium — same as 5A, plus one policy rule and one mandatory render-layer caveat | Low-Medium — best of the four on staleness specifically, though still bound by the profile's inherent point-in-time nature | Medium-High — the delta-since-last-research framing scales better across repeated re-research cycles than a flat "last 10" |

---

## User Preferences

No user dialogue preferences were supplied to this phase — per this agent's mandate, these
alternatives were generated purely from the research synthesis and report evidence, without
interactive convergence. The recommendations above are the starting proposals for the
orchestrator's Phase 4 user convergence step, not final decisions.

---

## Recommended Approach (Combined, Cross-Area)

Taking all five areas together, the coherent, lowest-risk starting package is:

1. **Decision Area 1 → 1A**: Enrich the existing per-tool tab pane in `comparison.html.j2` to
   render `use_case.rationale`/`.supporting_features`/`.evidence`, `additional_fact.evidence`,
   and grouped `feature_results`. No new render path, no new CLI verb.
2. **Decision Area 2 → 2D**: Group `feature_results` natively by their existing `group:` field
   (no new mechanism); group `additional_facts` via a new, versioned config-mapping table
   (2C), following the same revisioned-YAML convention as `feature-taxonomy.yaml` and
   `profile-sections.yaml`.
3. **Decision Area 3 → 3D**: Do not add a "known limitations" section in this round; the
   sourcing-rigor tension the research itself flags is a real blocker, not a formality, and
   should be resolved (likely via a separate, small standards/research task) before any of
   3A/3B/3C are pursued.
4. **Decision Area 4 → 4B**: Represent both "built-in tools" taxonomy gaps
   (vendor-bundled linters/formatters; named sub-agent enumeration) as `additional_facts`
   entries grouped under the "Built-in tools" heading, without a taxonomy/curation-gate change.
5. **Decision Area 5 → 5A/5D (combined)**: Add a new, schema-validated `release_history` array
   (mandatory per-entry evidence citing the vendor's official changelog/GitHub Releases page),
   populated by the research worker under a since-last-research capping policy, with a
   mandatory rendered "as of `researched_at`" freshness caveat. This is new scope (added
   mid-workflow, not part of the original brief the other four areas answer) — see Decision
   Area 5 above for its distinct evidence base (project constraints restated in the follow-on
   brief, not the four original gatherers' findings).

**Primary rationale**: every recommended alternative is the lowest-schema-risk,
lowest-new-infrastructure option that still fully answers the parts of the brief the research
found solid evidence for, and explicitly declines to force a section (limitations) or a
process (curation gate) where the evidence itself argues against doing so yet. This keeps the
work squarely in "rendering expansion," consistent with the research's own primary conclusion,
while leaving clearly marked upgrade paths (2B, 4A, 3C) for later if user needs prove those
alternatives' extra cost is warranted. Decision Area 5 is the one deliberate exception to the
"rendering expansion, not data modeling" framing that governs Areas 1/2/4 — it requires a real
schema addition — but it is recommended anyway because it is explicitly requested new scope
with an unambiguous official-source answer available (vendor changelogs), unlike Decision
Area 3's unresolved sourcing-rigor tension.

**Key trade-offs accepted**:
- No standalone, shareable single-tool HTML artifact yet (1B/1C deferred) — the single-tool
  report remains "a tab inside a comparison document," just far richer.
- `additional_facts` grouping (2C) relies on a manually maintained config table rather than a
  schema-enforced discriminator (2B) — acceptable now, but requires someone to keep the
  mapping current as new fact topics appear.
- "Known limitations" is absent from the report in this round, a real, acknowledged gap
  relative to industry norms, accepted deliberately because of the sourcing-rigor concern.
- The two built-in-tools gaps get descriptive-only treatment (4B), not full cross-tool
  comparability, until a stated need for that comparability emerges.
- Decision Area 5's `release_history` section requires a genuine schema change (new schema
  file, new top-level property, worker/skill update) before it can be populated at all — the
  smallest schema-change cost of any "new construct" alternative considered across all five
  areas (no curation gate, no cross-tool comparability), but real cost nonetheless; existing
  published profiles will show an absent section until re-researched under the new schema
  revision, and the section can never fully eliminate staleness — only actively manage it via
  5D's capping policy and mandatory caveat.

**Key assumptions** (if wrong, would change the recommendation):
- No current, concrete requirement exists for a standalone/exportable single-tool HTML file
  independent of the comparison flow. If such a requirement is confirmed, 1C (not 1B, to avoid
  duplicated markup) should be adopted instead of 1A alone.
- The config-mapping table (2C) will actually be kept up to date as new fact topics are
  introduced by profile-writing workers. If mapping-table staleness becomes a recurring
  problem in practice, 2B (schema discriminator) should be revisited.
- No stated need exists yet for cross-tool comparability on bundled-formatter or
  named-sub-agent presence specifically. If a user articulates that need, 4A becomes
  justified for that specific concept.
- The sourcing-rigor tension flagged for "known limitations" is not resolved by any of this
  research's own findings — this recommendation assumes that tension remains unresolved. If a
  workable sourcing approach is defined separately, 3C becomes a reasonable low-cost way to add
  the section.
- Decision Area 5 assumes every profiled tool has a discoverable official GitHub Releases page
  or vendor changelog a research worker can cite. If a given tool has no such official source
  (e.g. a closed-beta tool with no public release notes), `release_history` should be omitted
  for that tool (an empty/absent array) rather than backfilled from unofficial sources —
  consistent with official-sources-only, but worth confirming this doesn't leave the section
  perpetually empty for any profiled tool.

**Confidence**: High for Decision Areas 1, 2, and 4 (directly supported by high-confidence
research findings and explicit report recommendations). Medium for Decision Area 3 — the
recommendation to defer is well-supported by the research's own caveat, but "do nothing" is
inherently a lower-certainty recommendation than "do X," since it depends on the user's
tolerance for an acknowledged content gap versus the sourcing-rigor risk. Medium for Decision
Area 5 — the recommendation to build a structured, evidence-required section is well-grounded
in project constraints and the ready availability of official vendor changelogs as a source,
but (unlike Areas 1/2/4) it rests on no dedicated gatherer/synthesis pass of its own; it is
grounded directly in restated project constraints from the follow-on scope brief, not in
findings the original four gatherers produced.

---

## Why Not Others

**Decision Area 1**:
- *1B (standalone template/CLI verb)*: Rejected as a first move because it adds real new
  infrastructure (render function, template, CLI verb, output directory) for a standalone-
  artifact need that isn't established in the research or brief — a YAGNI violation risk per
  §7 constraint 6, and premature relative to 1A's lower-cost, higher-confidence path.
- *1C (hybrid)*: Rejected as the *first* move (though noted as the right upgrade path later)
  because it still adds CLI/render surface before any stated need for a standalone artifact
  exists; doing 1A first and refactoring into 1C later if needed avoids paying that cost
  speculatively.

**Decision Area 2**:
- *2A (free-text matching)*: Rejected as the long-term mechanism because of its drift/
  silent-failure risk — acceptable only as a stopgap, not as the recommended approach, given a
  better-fitting, similarly-low-cost alternative (2C) exists.
- *2B (schema discriminator)*: Rejected as the *immediate* choice (though flagged as a
  legitimate future upgrade) because it requires a schema change and coordinated worker-prompt
  rollout for a grouping need that 2C can satisfy without either, honoring YAGNI's "prefer the
  lighter-weight mechanism first" framing.

**Decision Area 3**:
- *3A (repurpose unresolved_issues)*: Rejected — conflates research-process-quality issues
  with product limitations, a semantic overload risk not worth the small schema saving.
- *3B (new dedicated schema construct)*: Rejected — highest effort of the four, and critically,
  does not itself resolve the sourcing-rigor problem the research flagged; it only gives that
  unsolved problem better-looking packaging.
- *3C (additional_facts entry)*: Not rejected outright — it's the recommended fallback if the
  user wants this section despite the sourcing caveat — but not the primary recommendation
  because it ships content under a visibly lighter evidentiary bar than the rest of the report,
  without flagging that difference to the reader.

**Decision Area 4**:
- *4A (full taxonomy feature_id)*: Rejected as the immediate choice — the re-research and
  curation-gate cost is substantial and, per the research's own framing, only justified once a
  stated comparability need exists, which is not yet the case.
- *4C (do nothing)*: Rejected — unlike Decision Area 3's limitations section, these two gaps
  are not blocked by a sourcing-rigor problem; they're straightforwardly representable via the
  existing `additional_facts` mechanism at near-zero cost, so declining to represent them at
  all leaves real, evidenced market differentiators unaddressed for no corresponding benefit.

**Decision Area 5**:
- *5B (additional_facts prose entry)*: Not rejected outright — it's a legitimate lower-cost
  fallback if the team decides the schema-change cost of 5A/5D isn't justified — but not the
  primary recommendation because it under-delivers the user's explicit ask for per-version,
  scannable structure and inherits `additional_facts`' weaker, single-shared-evidence sourcing
  discipline for content (version numbers, dates) that is unusually well-suited to strict
  per-entry citation.
- *5C (pointer-only, no versioned content)*: Rejected as the primary recommendation — while it
  fully eliminates the staleness risk, it does so by declining to assert the very content the
  user asked for ("a review of the last ~10 releases... with a what's new summary per
  release"), which is a functional regression relative to the stated new scope, not a
  lower-fidelity version of it. Unlike Decision Area 3's "do nothing" recommendation, there is
  no comparable sourcing-rigor blocker here to justify this level of retreat — official vendor
  changelogs are exactly the kind of first-party source the project's own protocol already
  treats as authoritative.
- *5A alone (without 5D's capping policy)*: Not rejected as unsound, but superseded by 5D — 5D
  reuses 5A's schema and evidence discipline at no extra schema cost while directly addressing
  the staleness tension the task brief itself names as the central design question for this
  area; there is no reason to accept 5A's plain "always fetch last 10" policy once the
  since-last-research alternative is on the table at the same cost.

---

## Deferred Ideas

The following are explicitly out of scope for this solution exploration — they were surfaced
by the research but are not part of the four decision areas above, and must not be folded into
any of the alternatives:

1. **Hardening `additional-fact.schema.json` to require evidence** (matching
   `use-case.schema.json`'s conditional `minItems` requirement for `kind: documented`). The
   research found this is a real, code-confirmed structural gap (`build.py:_collect_content`
   does simple `fact_id` dedup with no evidence enforcement; `curation.py`'s single curation
   gate never touches `additional_facts`) — but the synthesis explicitly frames this as "a
   legitimate candidate for a future `/flowbit-standards-update`... but out of scope for this
   research phase's recommendation, which is about report content, not schema hardening for
   its own sake." Worth a separate, small hardening task if the team wants to close this gap.
2. **Fixing `architecture.md`'s stale "stubbed" language** describing Comparison & Reporting.
   The research resolved this as stale documentation (three independent lines of evidence:
   working code, user-guide description, git-status dates) but did not correct the doc itself,
   since that's a documentation-hygiene action unrelated to report content.
3. **Whether `tool.vendor`/`tool.homepage` should become mandatory/first-class fields.** Flagged
   as an open, unresolved question in the research (§8 point 3) — not investigated deeply
   enough to feed a decision area here, and orthogonal to the four content-model decisions
   above.
4. **Re-running or completing the missing `example-profiles-data.md` gatherer output.** The
   research process itself has a hole (that gatherer never produced output; a narrow,
   disclosed direct-check substituted for it). Completing a fuller pass (e.g., assessing
   `description.md` prose richness/quality across the five tools) is a research-process
   follow-up, not a solution alternative.
5. **A canonical "recommended additional_facts topics" checklist** (e.g., a documented
   convention that every profile should have a pricing fact, a security/data-handling fact,
   etc.) — the research flags today's topic coverage as "ad hoc per-tool, not driven by a
   canonical list" (§4.4, medium confidence), but formalizing such a checklist is a distinct,
   adjacent idea from the four grouping/rendering/gap decisions above and was not generated as
   a fifth decision area per the task's explicit scope.
6. **"Best for X" positioning summary and independent-benchmarks sections** (research report
   §6 rows 8-9) — both were explicitly ranked lowest priority in the research report itself and
   were not named as one of the four decision areas for this exploration; they remain
   candidate future report sections but are out of scope here.
7. **Auto-refreshing the `release_history` section after publication** (e.g., a background job
   that periodically re-checks the vendor's releases page and updates a published profile
   without a full re-research pass) — surfaced during Decision Area 5's exploration but
   excluded from every alternative considered there, since it would require a network/model
   call outside the research-time worker path, directly violating the deterministic-core
   constraint (`architecture.md`: the Python core never calls a model or the network). The
   existing re-research/`profile_state: requires_research` cycle is the correct mechanism for
   keeping this section current, not a new live-refresh mechanism.
