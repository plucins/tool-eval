# Decision Log: Expand Single-Tool Report Content Model

Each ADR below corresponds to one of the five decision areas explored in
`outputs/solution-exploration.md`; alternatives are summarized here for traceability, not
re-derived — see that document for the full trade-off analysis, evidence links, and "why not
others" reasoning.

---

## ADR-001: Enrich the existing tab pane in place

### Status
Accepted

### Context
No dedicated single-tool HTML render path exists today — `render_comparison_html` always
requires two or more profiles and `cli.py`'s `profile` subcommand group has only
`validate`/`publish`/`list`, no `show`/`render`. A tool's entire report content today is one tab
pane inside `comparison.html.j2` (`:176-226`), and that pane already drops fields the schema
carries (`use_case.rationale`/`.supporting_features`/`.evidence`, `additional_fact.evidence`) and
never groups `feature_results` at all.

### Decision Drivers
- Zero schema change, zero new CLI surface, easily reversible.
- The research report ranks richer rendering of existing fields as the single highest-value,
  lowest-risk starting point.
- No stated, current need for a standalone, shareable single-tool artifact exists in the brief
  or findings.
- YAGNI: avoid speculative new infrastructure (render function, template, CLI verb, output
  directory) for an unconfirmed need.

### Considered Options
1. **Alternative 1A** — enrich the existing tab pane in place (chosen).
2. **Alternative 1B** — new standalone template + new `profile show`/`render` CLI verb.
3. **Alternative 1C** — hybrid: extract a shared Jinja macro, add a thin new template/CLI verb
   on top of it.

### Decision Outcome
Chosen option: **1A**, because it directly answers the brief's own framing ("richer
rendering of existing fields") at the lowest possible cost, with no new code path to test or
maintain, and no unconfirmed-need infrastructure investment.

### Consequences

#### Good
- No new render function, template, or CLI verb to build, test, or maintain.
- All of Decisions 2, 4, and 5's rendering work lands in one place (the existing tab pane),
  simplifying the follow-up specification/implementation task.

#### Bad
- A user wanting *just* one tool's report must still run a 2+-tool comparison and click into a
  tab — there is no standalone, shareable single-tool deliverable.
- If a standalone-artifact need is confirmed later, 1C (not 1B) should be adopted to avoid
  duplicating the markup this decision produces.

---

## ADR-002: Config-mapping file for `additional_facts` section grouping

### Status
Accepted

### Context
`feature_results` and `additional_facts` need to be grouped into named report sections, but they
are not the same problem: `feature_results` already carry a 100%-populated `group:` field from
`feature-taxonomy.yaml` (revision 4, 29 features across 5 groups) and need no new mechanism at
all. `additional_facts` have no such field — only a free-text `topic` string — and 16 real facts
across 5 profiles today use ad hoc topic strings with no canonical vocabulary.

### Decision Drivers
- Avoid solving an already-solved problem (`feature_results` grouping is free).
- Prefer the project's own established convention (revisioned YAML config, as used by
  `feature-taxonomy.yaml` and `profile-sections.yaml`) over a schema change.
- YAGNI: a schema discriminator field is a heavier, more durable mechanism than the grouping
  need currently justifies.
- Drift/silent-miscategorization risk of raw free-text matching should be minimized without
  requiring a worker-prompt rollout.

### Considered Options
1. **Alternative 2A** — free-text `topic` pattern matching in the render layer, no config file.
2. **Alternative 2B** — optional `category` discriminator field added to
   `additional-fact.schema.json`.
3. **Alternative 2C** — new revisioned config-mapping file (`fact_id`/`topic` → heading), with an
   explicit "Other" overflow.
4. **Alternative 2D** (chosen) — `feature_results` grouped natively by `group:` (no mechanism);
   `additional_facts` grouped via 2C; 2B deferred as a future upgrade.

### Decision Outcome
Chosen option: **2D**, because it decomposes the problem correctly — zero new mechanism for
`feature_results`, and the lightest mechanism that is still centralized/versioned/auditable
(2C) for `additional_facts`, consistent with the project's existing config conventions.

### Consequences

#### Good
- `feature_results` grouping ships with literally no new code artifact beyond a render-layer
  heading per group.
- The new mapping file is auditable, versioned, and revision-tracked the same way
  `feature-taxonomy.yaml` already is — no bespoke config-loading logic needed.
- An explicit "Other" bucket makes mapping-table gaps visible in the rendered output rather than
  silently dropping facts.

#### Bad
- The mapping table is a manually-maintained artifact — someone must keep it current as new fact
  topics appear, a softer guarantee than 2B's schema-enforced discriminator.
- If mapping-table staleness becomes a recurring problem, 2B should be revisited.

---

## ADR-003: Defer "known limitations" section

### Status
Accepted

### Context
Every external AI-coding-tool comparison source reviewed treats "known limitations / common
complaints" as a standard section, but this project has no clean data home for it. Limitations
are inherently comparative/critical claims, typically sourced from community or blog material —
structurally harder to reconcile with this project's official-sources-only, no-source-voting
research protocol than any other candidate section.

### Decision Drivers
- The research itself supplies an explicit, high-confidence reason to prefer inaction: the
  sourcing-rigor tension is a genuine blocker, not an implementation detail.
- Official-sources-only, no-fabrication standard (security.md, research-protocol.md) must hold
  for every section, not just the comparable ones.
- Shipping a section under a visibly lower evidentiary bar than the rest of the report risks
  misleading a reader who doesn't notice the difference.

### Considered Options
1. **Alternative 3A** — repurpose `unresolved_issues` with a new `kind: known_limitation` enum
   value.
2. **Alternative 3B** — new dedicated schema construct (`known_limitations` array).
3. **Alternative 3C** — model as an ordinary `additional_facts` entry with a conventional topic.
4. **Alternative 3D** (chosen) — do not add the section now.

### Decision Outcome
Chosen option: **3D**, because none of 3A/3B/3C resolve the underlying sourcing-rigor tension —
3A conflates research-process gaps with product limitations, 3B invests real schema effort
without answering the sourcing question, and 3C ships content at a visibly weaker evidentiary
bar than the rest of the profile. Declining to add the section is the only option that avoids
shipping something under-sourced.

### Consequences

#### Good
- Avoids overloading `unresolved_issues`' meaning or building schema infrastructure that doesn't
  solve the actual (sourcing) problem.
- Every section that does ship in this round meets the same official-sources-only bar.

#### Bad
- A section every external comparison source treats as standard remains absent from tool-eval's
  output — a real, acknowledged gap versus industry norms.
- If a workable sourcing approach for community/blog-derived limitations claims is defined
  separately, 3C becomes a reasonable low-cost fallback to revisit.

---

## ADR-004: Model "built-in tools" taxonomy gaps as `additional_facts`

### Status
Accepted

### Context
Two genuine, externally-corroborated gaps exist in the "built-in tools" taxonomy coverage:
vendor-bundled linters/formatters as a concept distinct from AI-*consuming* lint output
(`static_analysis_integration`), and enumeration of named/branded sub-agent roles (the taxonomy
only captures *that* multi-agent orchestration exists, not named roles within it).

### Decision Drivers
- No stated cross-tool comparability need exists yet for either concept specifically.
- Promoting to a full taxonomy `feature_id` requires re-researching all existing profiles and
  passing the single curation gate (`curation.py`) — real cost with no established payoff.
- Both gaps are genuine, real market differentiators (not speculative) — "do nothing" leaves an
  identified, evidenced gap unaddressed for no corresponding benefit.
- YAGNI: prefer the lowest-cost mechanism that still represents the content.

### Considered Options
1. **Alternative 4A** — promote each gap to a full taxonomy `feature_id`, through the curation
   gate.
2. **Alternative 4B** (chosen) — model both as ordinary `additional_facts` entries, grouped
   under "Built-in tools" via ADR-002's config-mapping mechanism.
3. **Alternative 4C** — do nothing now; revisit only if a concrete profile-writing need arises.

### Decision Outcome
Chosen option: **4B**, because it gets both concepts into the report immediately, at near-zero
cost, without pre-committing to full cross-tool comparability that no stated need currently
justifies. 4A remains available as a later upgrade if comparability becomes a stated requirement.

### Consequences

#### Good
- Both gaps can be represented by any profile-writing worker today, with no taxonomy revision
  bump and no re-research of the 5 existing profiles.
- Lands cleanly under the same "Built-in tools" heading ADR-002 already establishes for
  `additional_facts` grouping.

#### Bad
- No has/partial/not_found comparability for these two concepts — a reader cannot scan the
  comparison grid to see which tools have/lack them the way every other "built-in tool" concept
  supports.
- Inherits `additional_facts`' lighter evidence discipline (no schema-enforced `minItems`, no
  curation gate) for content that is conceptually a "capability."

---

## ADR-005: Structured `release_history` array with mandatory evidence and freshness caveat

### Status
Accepted

### Context
This is new scope, added mid-workflow: the user wants a "last ~10 releases" changelog view per
tool, clearly showing version, date, and a what's-new summary. No schema field, taxonomy
feature, or `profile-sections.yaml` section exists for this today. Unlike "known limitations,"
an unambiguous official first-party source exists for every claim this section would make — a
vendor's own GitHub Releases page or changelog.

### Decision Drivers
- Deterministic core: any new content must be worker-gathered at research time; the renderer
  only ever reads stored data, never fetches live.
- D-016 (JSON Schema is the source of truth): any new first-class field needs an actual schema
  change, not an ad hoc field, given `additionalProperties: false` at the profile top level.
- Official-sources-only, no fabrication: a version/date claim has no legitimate uncited form,
  unlike an `additional_facts` entry or an `inferred` use case.
- Staleness is real and central to this decision area: a "last N releases" list goes stale the
  moment the vendor ships again after research time.

### Considered Options
1. **Alternative 5A** — new `release_history` schema array, mandatory unconditional evidence per
   entry (structurally parallel to `additional-fact.schema.json`/`use-case.schema.json`).
2. **Alternative 5B** — single `additional_facts` entry with a prose "what's new" summary, no
   schema change.
3. **Alternative 5C** — pointer-only: link to the vendor's official changelog URL, no
   version-specific content asserted.
4. **Alternative 5D** — same schema as 5A, plus a since-last-research delta-and-cap population
   policy and a mandatory rendered freshness caveat.
5. **5A/5D combined** (chosen) — 5A's schema shape, populated under 5D's policy.

### Decision Outcome
Chosen option: **5A/5D combined**, because 5A's mandatory-evidence schema shape is the correct
fit for content that is either documented-and-cited or not includable at all, and 5D's
since-last-research capping policy plus mandatory freshness caveat directly manages the
staleness tension at no additional schema cost over 5A alone. 5B under-delivers the explicit
per-version structural ask and inherits weaker evidence discipline; 5C eliminates staleness by
declining to assert the very content requested, which is a functional regression, not a
lower-fidelity answer.

### Consequences

#### Good
- A version/date claim can never be published without at least one cited, registered official
  source — the strongest evidence discipline of any content channel in the profile.
- The since-last-research delta-and-cap policy keeps the list honest across re-research cycles,
  rather than a fixed "last 10" window that either repeats or silently drops releases.
- The mandatory rendered caveat directly addresses the "looks current, goes stale within weeks"
  risk as a rendering rule, not an optional nicety.

#### Bad
- Real schema-change cost: a new schema file, a new top-level property (another
  `additionalProperties: false` boundary crossing), and a required worker/skill-prompt update
  before this section can be populated at all.
- Existing published profiles will show an absent `release_history` until re-researched under
  the new schema.
- The section can never fully eliminate staleness — only actively manage it; a tool with no
  discoverable official release source will show this section perpetually empty rather than
  backfilled from unofficial sources.
- Auto-refreshing this section after publication (a background job re-checking the vendor's
  releases page) is explicitly excluded — it would require a network/model call outside the
  research-time worker path, violating the deterministic-core constraint.
