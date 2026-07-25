# Synthesis: Expand Single-Tool Report Content Model

## Research Question

What content should the single-tool profile/report in tool-eval contain to give a full
overview of an AI coding tool — specifically its use cases and built-in tools/capabilities
— and what other sections should be proposed for a complete AI-tool overview?

## Source Note — Gap in the Gathering Pass Itself

The task brief for this synthesis specified four findings files. Only three exist on disk:

- `analysis/findings/codebase-schemas-and-rendering.md`
- `analysis/findings/docs-and-standards.md`
- `analysis/findings/external-best-practice.md`

`analysis/findings/example-profiles-data.md` (category 2 in `planning/research-plan.md`
section 5, "Full content of `data/profiles/*/profile.json`") was never produced — the
gatherer for that category did not complete or was not launched. This is itself a finding:
the research pass has a hole in its own execution record.

Because "what the current profile already captures in practice" is core, load-bearing
content for the deliverable (Phase 6 of this agent's own mandate), a bounded, direct check
of the five real profile files was performed here as a substitute, restricted to counts and
structural facts (not new tool-fact claims). This is disclosed explicitly rather than
silently patched over. All such directly-observed facts below are marked **[synthesizer
direct-check]** to distinguish them from the three gatherers' own findings.

---

## Cross-Source Analysis

### Confirmed patterns (multiple sources agree)

| Claim | codebase-schemas-and-rendering.md | docs-and-standards.md | external-best-practice.md | synthesizer direct-check |
|---|---|---|---|---|
| No dedicated single-tool HTML render path exists; only a per-tool tab pane inside `comparison.html.j2` | §7 (`html.py:103-136`, `render_comparison_html` is the only render fn), §8 (tab pane at `:176-226`), §10 (`cli.py` has no `profile show/render` verb) | §1 (`user-guide.md` documents zero single-tool artifact; only `outputs/comparisons/`) | n/a | Confirmed |
| `use_cases` schema already models documented-vs-inferred with evidence/rationale, but only 3 of ~6 fields are actually rendered | §2 (schema `:1-48`), §8 (template renders only `title`/`kind`/`description`) | n/a | Use cases/workflows confirmed as a standard section industry-wide (§1 of that file) | High confidence — schema capability outstrips render capability |
| `additional_facts` is the de facto catch-all already carrying pricing/platform/data-handling content | §3 (schema `:1-27`, generic topic/description model) | §6 (open question on protocol rigor) | §4, §6 (pricing, security/data-handling are standard sections) | **[synthesizer direct-check]**: confirmed by content — see "Resolved ambiguity 3" below |
| Any new first-class field requires a schema change (D-016); `additionalProperties: false` blocks ad hoc fields | §1 (`profile.schema.json:7`) | §4 (`validation.md:32-36`) | n/a | Confirmed, doubly-sourced |
| Deterministic core / no live model or network calls at render time | §7, §9 (rendering is pure Jinja2 + markdown-it + nh3, no model imports in `cli.py`) | §2 (`architecture.md:4,122`) | n/a (external gatherer's own scope note echoes this: findings are for corroboration only, not for direct profile ingestion) | Confirmed, doubly-sourced |
| Official-sources-only fact sourcing; no fabrication | n/a (not this gatherer's scope) | §5, §6 (`security.md:9-10`, `research-protocol.md`) | Explicit self-caveat throughout (pricing figures, SWE-bench scores marked third-party/unverified) | Confirmed; the external gatherer's own discipline in flagging its evidence as "corroboration of section type, not sourceable fact" is itself a demonstration of the standard being followed correctly |

### Contradictions identified and resolved

**Contradiction 1 — "stubbed" vs. working comparison pipeline.**
`.flowbit/docs/project/architecture.md:78-80` calls Comparison & Reporting "stubbed" and says
`compare build` returns `INPUT_NOT_IMPLEMENTED`. This directly contradicts
`docs/user-guide.md:90-105,192-200` (fully described working `/tool-eval-compare` flow) and the
codebase gatherer's own direct reads of `html.py`, `comparison.html.j2`, and `cli.py`, all of
which show a complete, working render pipeline (§7-§10 of codebase findings).

*Resolution*: `architecture.md`'s footer is dated 2026-07-24, one day before this research task,
and the working tree (per `git status` at session start) shows `reporting/html.py`,
`comparison.html.j2`, and `feature-taxonomy.yaml` as locally modified and uncommitted. The
straightforward read is that Increment 3 (comparison rendering) landed after that doc snapshot
and `architecture.md` simply wasn't refreshed. **Confidence: high** that "stubbed" is stale
documentation, not an accurate description of current runtime behavior — three independent
lines of evidence (user-guide prose, direct code reads, git status/dates) converge on the same
conclusion. This is a documentation-maintenance issue worth flagging to the user separately from
the research question itself (candidate for `/flowbit-standards-update` or a docs-refresh task,
not part of this research's scope).

**Contradiction 2 (apparent, resolved as non-contradiction) — 27 vs. 29 features.**
`research-plan.md:70` states "27 features across 5 groups." The codebase gatherer counted 29 by
reading each feature's literal `group:` field in `config/feature-taxonomy.yaml` (revision 4):
code_authoring=5, agentic_execution=5, context_quality=6, workflow_ecosystem=8,
security_governance=5 = 29. The gatherer flagged this discrepancy as unresolved and asked the
synthesizer to check independently.

*Resolution* **[synthesizer direct-check]**: cross-referencing against the five real profile
files settles this. `cursor`, `github_copilot`, and `windsurf` are all at
`research.taxonomy_revision: 4` and each carries exactly **29** `feature_results` entries.
`claude_code` and `demo_tool` are at `research.taxonomy_revision: 1` with `profile_state:
requires_research` and carry only **26** `feature_results` entries — consistent with being
stale profiles from before the taxonomy grew to 29 features, not evidence against the count.
**Conclusion: 29 is the correct current count for taxonomy revision 4; the plan's "27" was
simply stale/incorrect text written before the taxonomy's last expansion.** Confidence: high
(three independent revision-4 profiles agree exactly with the codebase gatherer's direct file
read).

### Ambiguity resolved via direct check — additional_facts protocol rigor

The docs gatherer flagged an open question (§6, and repeated in its "Ambiguities" section):
does `additional_facts` get the same not-found/curation-gate rigor as `feature_results`, or a
lighter weight? It could not resolve this from docs alone and asked for codebase/example-profile
verification.

**[synthesizer direct-check]**, reading `src/tool_eval/research/curation.py` and
`src/tool_eval/profiles/build.py` directly:

- `curation.py`'s docstring and functions (`curate_candidates`, `accept_feature_into_taxonomy`,
  `_append_waiting_room`, `_append_rejected`) are exclusively about **feature candidates** for
  taxonomy revision — the single curation gate (accept/reject/defer) never mentions
  `additional_facts` anywhere in the file. `additional_facts` are structurally outside the
  curation gate.
- `build.py:_collect_content` (`:65-101`) absorbs `additional_facts` and `use_cases` from
  worker `profile-writing` task results purely by `fact_id`/`use_case_id` dedup — no evidence
  check, no not-found protocol, no cross-validation against `feature_results` happens at merge
  time. This matches the schema finding (`additional-fact.schema.json` does not enforce
  `evidence` with `minItems`, unlike `use-case.schema.json`'s conditional requirement for
  `kind: documented`).
- However, reading all five real profile files directly: **every single `additional_facts`
  entry across all 5 tools (16 facts total) carries a non-empty `evidence` array** (1-2 items
  each). In practice, the profile-writing workers populate evidence even though nothing in the
  schema or the merge code forces them to.

**Conclusion**: this is a genuine structural gap — `additional_facts` has neither the curation
gate nor schema-enforced evidence that `feature_results`/`use-case (documented)` have — but it
has not yet manifested as a real quality problem in the five existing profiles, because worker
behavior (not enforcement) happens to comply with the stated intent in the schema description.
**Confidence: high on the structural gap (directly read code); high but data-limited on "no
problem in practice" (n=5 profiles, all produced by the same harness/skill version — this is
not proof the pattern holds for future or differently-authored profiles).** This is a legitimate
candidate for a future `/flowbit-standards-update` (tighten `additional-fact.schema.json` to
require evidence, matching `use-case.schema.json`'s pattern) but is out of scope for this
research phase's recommendation, which is about report *content*, not schema hardening for its
own sake — noted here for completeness per the task brief, not carried forward as a "new
section" recommendation.

---

## Patterns and Themes

### Pattern: "documented vs. inferred" is the project's dominant epistemic model
Prevalence: appears in `use-case.schema.json` (`kind` enum), `feature-result.schema.json`
(`status` enum with `uncertain`), and the research-protocol standard's not-found/no-voting
rules. Quality: mature, consistently applied to the two schemas that carry it
(feature-result, use-case). Gap: `additional_facts` doesn't carry an explicit `kind`/label
field at all — it's implicitly "documented" only by convention/description text, not by a
structured discriminator. Any new section modeled as `additional_facts` inherits this
weaker labeling unless the schema is extended.

### Pattern: schema capability regularly exceeds render capability
Recurs three times: (1) `use_case.rationale`, `.supporting_features`, `.evidence` all exist
in schema but are dropped in the template (only `title`/`kind`/`description` render); (2)
`feature_result.rationale` is only shown as a hover tooltip in the comparison grid, not
surfaced per-tool; (3) `internal_tools` description section exists in `profile-sections.yaml`
but is optional, so it can be silently absent with no placeholder. This is the single most
important structural theme for this research question: **a meaningful fraction of what the
brief is asking for ("full overview... use cases and built-in tools") may already be captured
in the data and simply needs a richer render path, not new research/schema work.**

### Pattern: a single generic container (`additional_facts`) is absorbing most literature-style content that would otherwise need bespoke schema fields
Confirmed by direct read of real data: existing fact topics already span exactly the kind of
content the external-best-practice gatherer identified as standard "sections" — pricing
(`plans_and_tiers`, `pricing_tiers`, `plan_availability`, `pricing_note`), platform/access
(`access_surfaces`), data handling (`data_no_training_default`), extensibility
(`mcp_extensibility`), and vendor identity (`vendor_identity`). This strongly supports treating
`additional_facts` as the default landing zone for new literature-derived sections rather than
proposing schema changes for each one individually, consistent with the minimal-implementation
standard's YAGNI framing.

### Pattern: rigor is proportional to comparability, not to importance
`feature_results` and `use_cases` (when `kind: documented`) carry the heaviest protocol
(search trace, not-found rigor, curation gate for new features) because they feed the
comparison table's flags/scoring. `additional_facts` — despite frequently carrying
business-critical content like pricing and data-training policy — carries the lightest
protocol, because it was designed as a non-comparable, prose-adjacent catch-all. This is a
reasonable design trade-off (per minimal-implementation's YAGNI principle: don't build
comparison machinery for non-comparable content) but is worth stating explicitly since a
naive reader might assume "more prominent section in a report" implies "more rigorously
sourced," and here it's often the reverse.

---

## Key Insights

1. **The gap is almost entirely a rendering/template gap, not a data-modeling gap, for the two
   things the brief names explicitly (use cases, built-in tools).** Use cases already have a
   rich schema; "built-in tools" maps cleanly onto six existing `feature_id`s across
   `agentic_execution` and `workflow_ecosystem` groups. Evidence: codebase findings §2, §4, §8.
   Confidence: high.

2. **For everything beyond use-cases/built-in-tools (pricing, security posture, deployment,
   extensibility, limitations, target audience), the industry-standard content already has a
   home in this project's data model (`additional_facts`) and, empirically, is already being
   populated there for real tools.** Evidence: external-best-practice §1-9 cross-referenced
   against synthesizer direct-check of all 5 profiles' `additional_facts` topics. Confidence:
   high for "a home exists"; medium for "current population is comprehensive" (existing facts
   are ad hoc per-tool, not driven by a canonical list of expected topics — nothing enforces
   that e.g. every tool profile has a "security & data handling" fact).

3. **Independent benchmarks are the one proposed section type with a credibility problem
   serious enough that inclusion itself is contestable**, per the external gatherer's sourced
   finding that OpenAI's own evaluators publicly disputed SWE-bench Verified's integrity
   (59.4% of a sampled hard subset had flawed/contaminated test cases). Confidence: medium-high
   on the underlying claim (single external gatherer, WebSearch-snippet sourcing only, not
   independently corroborated inside this project) — but the *implication* (if benchmarks are
   included, scope to the underlying model and flag low confidence, or omit) is a reasonable,
   evidence-grounded recommendation regardless.

4. **The project's own protocol rigor is uneven across the two data channels that would carry
   new content** (see "Ambiguity resolved" above) — a genuine, code-confirmed gap, not
   speculation.

---

## Relationships and Dependencies

- `profile-sections.yaml` (Markdown prose sections) and `use_cases`/`feature_results`/
  `additional_facts` (structured JSON) are **parallel, non-cross-validated** content channels
  feeding the same rendered output. `internal_tools` and `workflows` are prose sections;
  `use_cases` and `feature_results` are structured arrays. No code cross-checks that prose in
  `workflows` agrees with the structured `use_cases` array, or that `internal_tools` prose
  agrees with the `agentic_execution`/`workflow_ecosystem` `feature_results`. Any new section
  proposal should decide explicitly which channel it uses and accept that today's architecture
  does not reconcile the two automatically.
- `render_comparison_html` → `comparison.html.j2` is a single dependency chain with no branch
  point for "single tool only" — extending it for richer per-tool content (more `use_case`
  fields, `internal_tools` as its own anchored block, new `additional_facts` sub-grouping) is
  editing the *existing* tab pane markup (`:176-226`), not building new infrastructure. A true
  standalone single-tool report (its own HTML file, its own CLI verb) would be new
  infrastructure: a new render function, a new template, and a new `cli.py` verb (there is
  currently no `profile render`/`profile show`).
- Any new first-class schema field flows through `profile.schema.json` → build.py merge →
  business validation → template. Because `additionalProperties: false` is set at multiple
  levels, a new field is invisible to the pipeline until declared in schema — there is no
  "soft" way to smuggle a new structured field through only the template layer.

---

## Gaps and Uncertainties

1. **Missing gatherer output**: `example-profiles-data.md` was never produced (see Source Note
   above). The counts and structural facts used here to fill that hole were obtained via a
   narrow, direct read restricted to counts/topics/evidence-presence — not a full re-run of that
   gatherer's intended scope (e.g., it might also have assessed prose richness of `description.md`
   files, which was not checked here).
2. **External findings are WebSearch-snippet-only**, no WebFetch available in that gatherer's
   environment — every external citation is corroboration of section *type* presence, not a
   verified read of page structure or exact current facts (explicitly self-flagged by that
   gatherer, §"Gaps/limitations").
3. **`additional_facts` real-world evidence discipline is based on n=5 profiles**, all produced
   by this project's own harness — not a large or externally-diverse sample; do not treat
   "100% carry evidence today" as a durable guarantee.
4. **Whether `tool.vendor`/`tool.homepage` should become mandatory/first-class** is unresolved:
   the schema allows them (`profile.schema.json:17-27`) but nothing in the three findings files
   establishes how consistently real profiles populate them. Not independently checked here
   either (out of the narrow direct-check scope) — flagged as an open question rather than
   answered.
5. **Doc staleness** (`architecture.md` "stubbed" language) is resolved *for the purposes of this
   research* (treat as stale) but is not itself corrected — a separate documentation-hygiene
   action, not part of this deliverable.

---

## Synthesis by Framework (Mixed: Technical + Literature)

**Technical (component/gap analysis)**: see codebase findings §1-10, cross-referenced and
resolved above. Net result: schema is ahead of render for use_cases; taxonomy already covers
most of "built-in tools"; no single-tool render path exists at all (confirmed by three
independent evidence types: code read, doc read, CLI verb enumeration).

**Literature (best-practice comparison)**: see external findings §1-11 and the cross-tool
corroboration table. Net result: 10 recurring section types plus one synthesis pattern
("best for X" positioning). All except benchmarks have solid multi-source corroboration; all
require official-sources-only sourcing per this project's own standards, which the literature
gatherer itself flagged repeatedly.

**Applicability filter (this project's constraints)**: every literature-derived candidate was
run through: (a) representable in `additional_facts` today? (b) needs schema change? (c)
needs new render path/template? — this filtering is carried into the research report's
prioritized table.

---

## Conclusions

**Primary**: The single-tool report gap is real but narrower than it might first appear. Two
of the three things the brief asks about (use cases, built-in tools) are largely **schema-and-
taxonomy solved already** — the work is in rendering more of what's already captured, plus
closing two genuine taxonomy gaps (vendor-bundled linters/formatters as a distinct concept;
named sub-agent enumeration). The third thing (a fuller AI-tool overview) is best served by
formalizing `additional_facts` usage around a recommended-topic checklist rather than by
schema expansion for every new topic, with 1-2 exceptions (see research report).

**Secondary**: The project's own gathering process for this research task has a hole
(missing `example-profiles-data.md`), and the project's documentation has a known staleness
issue (`architecture.md` "stubbed" language) — both worth surfacing to the user as
process/hygiene items distinct from the content question itself.

**Recommendation**: Treat this synthesis and the accompanying research report as the complete
research-phase deliverable. Any schema/template/CLI changes are implementation and belong in a
follow-up `/flowbit-development` (or spec/plan) task, not this research task.
