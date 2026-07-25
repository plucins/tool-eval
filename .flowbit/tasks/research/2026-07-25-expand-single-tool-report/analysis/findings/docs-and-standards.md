# Docs & Standards Findings — Expand Single-Tool Report

Category: `docs`. Sources: `docs/user-guide.md`, `.flowbit/docs/project/architecture.md`,
`.flowbit/docs/project/tech-stack.md`, `.flowbit/docs/standards/global/validation.md`,
`.flowbit/docs/standards/global/security.md`,
`.flowbit/docs/standards/global/research-protocol.md`,
`.flowbit/docs/standards/global/minimal-implementation.md`,
`.flowbit/docs/standards/backend/models.md`.

---

## 1. `docs/user-guide.md` — no single-tool report artifact described

**Finding: only a multi-tool comparison HTML artifact is documented; no single-tool report/render verb exists.**

- Entry skills (section 3, lines 69–120) list exactly three skills:
  `/tool-eval-research <tool_name>` (research + publish profile, lines 74–89),
  `/tool-eval-compare <tool_id> <tool_id> [...]` (build comparison HTML, lines
  90–105), and `/tool-eval-resume <run_id>` (lines 106–119). There is no
  fourth skill for rendering/showing a single tool's report.
- `docs/user-guide.md:92-100` (section 3.2): "Build a single self-contained,
  offline HTML comparison of two or more tools that already have published
  profiles... Flow: resolve tools → copy active profiles into the comparison
  run → validate profiles/revisions/dates → compute deterministic freshness
  and flags → render sanitized Markdown into the template with bundled assets
  → publish one file under `outputs/comparisons/`." — HTML rendering is
  explicitly scoped to "two or more tools."
- Directory reference table, `docs/user-guide.md:204-216`:
  - Line 208: `data/profiles/<tool_id>/` → "The active profile: `profile.json`
    (machine-readable) + `description.md` (semantic description)." This is
    the entirety of today's per-tool artifact set — no HTML.
  - Line 210: `outputs/comparisons/` → "Generated self-contained HTML
    comparison reports." The only HTML output path documented, and it is
    plural/comparison-only by name and description.
- Section 7 "Interpreting results" (`docs/user-guide.md:220-241`) is framed
  around comparison semantics: 7.2 (lines 231-240) explicitly says "the
  comparison also shows the **date spread** across the compared profiles" and
  describes `INPUT_COMPARE_WARNING` records — i.e., this section documents
  how to read the comparison HTML, not a standalone single-tool report.
- Section 9 "MVP limitations" (`docs/user-guide.md:290-306`) does not
  explicitly list "no single-tool HTML report" as an excluded feature, but
  lists adjacent exclusions: no PDF export (line 304), no effectiveness
  benchmarks (line 305), no profile/source history (line 301) — these bound
  what any new report section could plausibly draw on (no historical
  trend data available to render).

**Conclusion**: `docs/user-guide.md` confirms, end to end, that user-facing
documentation describes zero single-tool report artifact or CLI/skill verb.
The only documented human-readable output is the multi-tool comparison HTML
under `outputs/comparisons/`. This matches the research brief's premise but
is now directly evidenced with line citations.

---

## 2. `.flowbit/docs/project/architecture.md` — deterministic-core boundary

- `.flowbit/docs/project/architecture.md:4`: "the Python core performs only
  deterministic work — validation, merging, publication, and run lifecycle
  management — while all reasoning (research, curation judgement, web
  access) is delegated to an external agent harness defined under `.claude/`."
- `.flowbit/docs/project/architecture.md:122`: "External Integrations: None
  at the Python layer by design — no databases, model SDKs, or network
  calls... Web/model access lives entirely in the harness, never in the
  Python core."
- **Implication for the research question**: any new report content (a
  pricing section, security-posture section, etc.) must be **pre-computed
  data** — gathered by the harness (worker agents) ahead of time and stored
  in the profile/schema — and the Python renderer must only read that stored
  data at render time. No proposal may involve a live LLM call, web fetch, or
  model SDK call inside `src/tool_eval/reporting/` or any other Python-core
  path. This directly matches the brief's stated architecture constraint.

**Flag — possible doc staleness**: `.flowbit/docs/project/architecture.md:78-80`
describes "Comparison & Reporting (Increment 3 — stubbed)... Currently
stubs; `compare build` returns `INPUT_NOT_IMPLEMENTED`." This directly
contradicts `docs/user-guide.md:90-105` and `:192-200`, which document a
fully working `/tool-eval-compare` flow producing real HTML output. The
architecture doc's footer (`.flowbit/docs/project/architecture.md:134`) says
"Based on codebase analysis performed 2026-07-24" — one day before this
research task. Current `git status` (not part of this citation set, but
observable in the working tree) shows `src/tool_eval/reporting/html.py`,
`src/tool_eval/reporting/templates/comparison.html.j2`, and
`config/feature-taxonomy.yaml` as locally modified/uncommitted, suggesting
Increment 3 (comparison rendering) may have progressed past "stubbed" without
`architecture.md` being refreshed yet. **This is an ambiguity to flag
explicitly, not resolve**: treat `docs/user-guide.md`'s description of a
working comparison pipeline as the more current/authoritative source for
"what renders today," and treat `architecture.md:78-80`'s "stubbed" language
as potentially stale documentation, not as evidence that reporting is
unimplemented.

---

## 3. `.flowbit/docs/project/tech-stack.md` — rendering stack confirmed

- `.flowbit/docs/project/tech-stack.md:16-18` (Visual Stack Flow): `cli -->
  render["markdown-it-py + Jinja2<br/>description / HTML render"] --> nh3["nh3
  ...HTML sanitization"]`.
- `.flowbit/docs/project/tech-stack.md:36`: "Presentation output (Increment 3)
  is generated as self-contained, sanitized HTML rather than a running
  frontend."
- Key Dependencies table, `.flowbit/docs/project/tech-stack.md:80-82`:
  `Jinja2` — "Templating for reporting / HTML generation (Increment 3)";
  `markdown-it-py` — "Markdown parsing/rendering of profile descriptions";
  `nh3` — "HTML sanitization for safe self-contained HTML output."
- No other templating/rendering technology is listed anywhere in this file.

**Implication**: any proposal to expand single-tool report content must
render through the existing Jinja2 + markdown-it-py + nh3 pipeline (extending
`comparison.html.j2` or adding a new `.html.j2` template rendered by the same
stack). Introducing a new templating engine, frontend framework, or
client-side JS rendering approach would contradict this documented stack and
also the "Minimal Dependency Stack" standard (see §7 below).

---

## 4. `.flowbit/docs/standards/global/validation.md` — D-016, schema as source of truth

- `.flowbit/docs/standards/global/validation.md:32-33`: "JSON Schemas (under
  `src/tool_eval/validation/schemas/`, D-016) are the source of truth for
  generated-data structure, types, simple dependencies, and examples.
  Status-dependent and cross-record rules (referential integrity,
  completeness) live in the business validator (`validation/business.py`),
  not in schemas."
- `.flowbit/docs/standards/global/validation.md:35-36`: "Profile Schema
  Conventions (D-016): Profile schemas/data use: stable lowercase-ASCII
  underscore identifiers; ISO 8601 UTC timestamps; semantic `schema_version`;
  integer taxonomy/template revisions; `additionalProperties: false`; and
  omission of optional fields rather than storing `null` (unless `null` has a
  defined domain meaning)."

**Implication**: any new profile section (pricing, security posture, target
audience, etc.) that isn't representable via the existing generic
`additional_facts` container requires an actual JSON Schema change under
`src/tool_eval/validation/schemas/` — not an ad hoc field added only in code
or only in a template. Because of `additionalProperties: false`, any new
top-level or nested field must be explicitly declared in the schema or the
profile will fail validation. This is a hard constraint on any proposal that
suggests a new first-class field rather than reusing `additional_facts`.

---

## 5. `.flowbit/docs/standards/global/security.md` — sourcing and sanitization constraints

- `.flowbit/docs/standards/global/security.md:6-7` ("No Secrets; Safe Profile
  URLs"): "Secrets, environment variables, credentials, and local user data
  must never enter profiles or HTML. Profile URLs must use `http`/`https`
  only and contain no credentials."
- `.flowbit/docs/standards/global/security.md:9-10` ("Official Sources for
  Feature Status"): "A feature status may rest only on public official
  sources. Non-official pages can help locate an official source but cannot
  justify a status by themselves; community integrations and unofficial
  workarounds do not affect the table."
- `.flowbit/docs/standards/global/security.md:12-13` ("Self-Contained
  Sanitized HTML"): "Comparison output is a single self-contained offline
  HTML file with all resources embedded locally (no CDN/Internet
  dependency). Rendered Markdown is sanitized, raw HTML is disabled by
  default, profile data is escaped, only safe URL protocols are allowed, and
  no profile/source data is executed as code."
- `.flowbit/docs/standards/global/security.md:18-19` ("Worker Isolation"):
  research workers cannot modify schemas/taxonomy/profiles, cannot publish,
  cannot delegate further.

**Implication for candidate new sections (pricing, security posture, etc.)**:
- Any "pricing/licensing" or "security posture" section's facts must be
  sourced the same way existing feature statuses are — **official public
  sources only**; a blog post, third-party comparison article, or forum
  cannot by itself justify a stated fact (e.g. a specific price, a specific
  compliance certification).
- No section may embed secrets/credentials, and any URLs shown (e.g. a
  pricing page link) must be `http`/`https` with no embedded credentials.
- Whatever new section is added must still render through the sanitized,
  self-contained, escaped-HTML pipeline — no unsanitized raw HTML, no
  external CDN assets, no executable content derived from profile data.

---

## 6. `.flowbit/docs/standards/global/research-protocol.md` — how new sections get populated

- `.flowbit/docs/standards/global/research-protocol.md:3-4` ("Single
  Curation Gate"): "Research has exactly one curation point where every
  candidate feature receives an accept, reject, or defer decision.
  Publication is blocked while any candidate is undecided; only accepted
  candidates trigger controlled taxonomy revision changes through the CLI."
- `.flowbit/docs/standards/global/research-protocol.md:6-7` ("Complete
  Not-Found Protocol"): "`not_found` is allowed only after the full
  auditable search protocol runs... An unavailable material source, tool
  failure, or incomplete research yields `uncertain`, never `not_found`."
- `.flowbit/docs/standards/global/research-protocol.md:9-10` ("No Source
  Voting"): "Resolve conflicts by policy order... Never vote by number of
  occurrences, because pages may copy one another."
- `.flowbit/docs/standards/global/research-protocol.md:12-13` ("Evidence &
  Retained-Source Scope"): "Do not store complete copies of pages... Store
  source metadata (URL, title, type), availability/redirect info,
  checked-at date, short excerpts for has/partial, and structured search
  traces for negative results."
- `.flowbit/docs/standards/global/research-protocol.md:15-16` ("Research
  Concurrency Limits"): default max 4 concurrent workers, bundles of 2-4
  related features.

**Implication**: any literature-inspired new section (e.g. "target audience
fit," "known limitations," "benchmarks") that becomes a first-class taxonomy
feature would flow through the **same** single curation gate as existing
features — it cannot bypass curation or be auto-accepted. Its facts must be
labeled per the same has/partial/not_found/uncertain vocabulary (with the
same not-found protocol rigor), sourced from official documentation, never
inferred-and-presented-as-fact, and never resolved by counting how many blogs
repeat a claim. If a new section is instead added as free-form
`additional_facts` (not a taxonomy feature), the "documented vs inferred,
never fabricated" principle still applies per the research brief's own
constraints section, even though `additional_facts` doesn't go through the
curation gate the way taxonomy features do (that distinction is not spelled
out in this standards file and should be verified against
`additional-fact.schema.json` and `curation.py`, outside this gatherer's
scope — see gap below).

**Gap/ambiguity to flag**: This file governs the curation gate for taxonomy
**features**. It does not explicitly state whether free-form
`additional_facts` entries are subject to the same not-found/no-voting
protocol or only to a lighter evidence requirement. That distinction matters
for deciding whether new literature-derived sections should become taxonomy
features (heavy protocol) or `additional_facts` entries (unclear protocol
weight) — worth resolving via the codebase/example-profiles categories, not
resolvable from docs alone.

---

## 7. `.flowbit/docs/standards/global/minimal-implementation.md` — YAGNI justification requirement

- General principles (`.flowbit/docs/standards/global/minimal-implementation.md:3-22`):
  build only what will be called; no future stubs; no speculative
  abstractions; review before commit; unused code is debt.
- Project-specific, `.flowbit/docs/standards/global/minimal-implementation.md:26-27`
  ("Minimal Dependency Stack"): "Keep the runtime stack intentionally small:
  PyYAML via `safe_load` only, jsonschema (Draft 2020-12), Jinja2 with
  `autoescape` + `StrictUndefined`, markdown-it-py with raw HTML disabled,
  nh3 for sanitization, and the standard library... Do not add Pydantic,
  Click/Typer, Requests, web frameworks, databases, or crawler libraries
  without explicit need."
- `.flowbit/docs/standards/global/minimal-implementation.md:29-30` ("Add
  Tools Without Generator Changes"): "Onboarding a new AI coding tool must
  not require changes to the generator or to existing profile code — a tool
  is added purely through the research workflow / profile data."

**Implication**: every proposed new report section needs an explicit
rationale beyond "nice to have industry parity" — per YAGNI, and per the
project's own stated preference to keep the dependency stack and generator
code minimal. This also reinforces §3's constraint: no new templating
library. And it implies that whichever mechanism is chosen for new sections
should, where possible, be data-driven (schema/config additions) rather than
per-tool bespoke code, consistent with "add tools without generator changes."

---

## 8. `.flowbit/docs/standards/backend/models.md` — likely generic/non-tailored for this project

- Full content (`.flowbit/docs/standards/backend/models.md:1-26`) is a
  generic database-modeling standard: clear singular/plural naming,
  created/updated timestamps, database constraints (NOT NULL, UNIQUE,
  foreign keys), appropriate types, indexing foreign keys, multi-layer
  validation, relationships/cascades, normalization.

**Flag — likely inapplicable in its current form**: `tech-stack.md:44-48`
and `architecture.md:124-125` both explicitly state tool-eval **has no
database** ("Not applicable. tool-eval has no database. State is persisted
as files on disk..."). This `models.md` standards file reads as generic
boilerplate (ORM/RDBMS conventions) that does not map onto tool-eval's actual
architecture, which uses JSON Schema files and revisioned YAML instead of
tables/foreign keys/indexes. None of its bullet points (NOT NULL constraints,
foreign-key indexing, cascade behaviors) have a direct analog in this
codebase. For the purposes of this research task, **the actually-binding
convention for adding new profile fields is D-016 in
`.flowbit/docs/standards/global/validation.md:35-36`** (stable lowercase-ASCII
identifiers, ISO 8601 timestamps, semantic `schema_version`, integer
revisions, `additionalProperties: false`, omit-rather-than-null) — not this
file. Recommend the synthesizer treat `models.md` as non-authoritative for
this project's schema conventions and rely on `validation.md` D-016 instead.
This is a standards-documentation gap (a stale/generic standard file) worth
surfacing to the user as a possible `/flowbit-standards-update` candidate,
independent of the report-content research question itself.

---

## Summary of constraints any proposed new section must satisfy

1. **No live model/network calls at render time** (architecture.md:4,122) —
   content must be pre-gathered data stored in the profile.
2. **Reuse existing Jinja2 + markdown-it-py + nh3 stack** (tech-stack.md:16-18,80-82;
   minimal-implementation.md:26-27) — no new templating technology.
3. **Schema-first**: new first-class fields require a JSON Schema change
   under `validation/schemas/` per D-016 (validation.md:32-36);
   `additionalProperties: false` blocks ad hoc fields. Reuse of
   `additional_facts` avoids a schema change but may carry different
   evidentiary weight (see gap in §6).
4. **Official-sources-only facts**, no secrets, sanitized/self-contained HTML
   output, safe URL protocols only (security.md:6-19).
5. **Same research-protocol rigor** for any new taxonomy-feature-based
   section: single curation gate, complete not-found protocol, no source
   voting, minimal retained evidence (research-protocol.md:3-16) — open
   question whether `additional_facts` entries carry the identical rigor.
6. **YAGNI justification required** per section proposed; prefer
   generic/data-driven mechanisms over per-tool bespoke code
   (minimal-implementation.md:3-30).

## Ambiguities flagged for the synthesizer

- `architecture.md:78-80` calls comparison/reporting "stubbed" /
  `INPUT_NOT_IMPLEMENTED`, contradicting `user-guide.md`'s fully-described
  working comparison flow — likely stale doc, dated one day before this task;
  treat user-guide.md as more current for "what renders today."
- Whether `additional_facts` entries must satisfy the full not-found/curation
  protocol (research-protocol.md) at the same rigor as taxonomy features is
  not stated in the docs read here — needs codebase verification
  (`additional-fact.schema.json`, `curation.py`) outside this category's scope.
- `.flowbit/docs/standards/backend/models.md` is generic DB-modeling content
  that does not fit a no-database, file-based project; flagged as
  non-authoritative/possibly-stale rather than a real constraint on this
  research question.
