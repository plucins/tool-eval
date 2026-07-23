# Requirements Document — AI Coding Tool Comparison System

**Version:** 2.1
**Status:** approved MVP requirements baseline
**Date:** July 13, 2026
**Audience:** team and internal clients

---

## Table of Contents

1. [Purpose of this document](#1-purpose-of-this-document)
2. [Executive summary](#2-executive-summary)
3. [Problem and objectives](#3-problem-and-objectives)
4. [Guiding principles](#4-guiding-principles)
5. [Scope and stages](#5-scope-and-stages)
6. [Audience and HTML output](#6-audience-and-html-output)
7. [Objects and lifecycles](#7-objects-and-lifecycles)
8. [Feature taxonomy](#8-feature-taxonomy)
9. [Statuses](#9-statuses)
10. [Constraints and integrations](#10-constraints-and-integrations)
11. [Sources and policies](#11-sources-and-policies)
12. [Complete search protocol](#12-complete-search-protocol)
13. [LLM evaluation frame](#13-llm-evaluation-frame)
14. [Semantic profile](#14-semantic-profile)
15. [`/tool-eval-research` skill](#15-tool-eval-research-skill)
16. [Complete system workflow](#16-complete-system-workflow)
17. [Validation and persistence](#17-validation-and-persistence)
18. [Comparison and flags](#18-comparison-and-flags)
19. [Freshness](#19-freshness)
20. [Section B — Stage 2](#20-section-b--stage-2)
21. [Technical roles](#21-technical-roles)
22. [Configuration](#22-configuration)
23. [Non-functional requirements](#23-non-functional-requirements)
24. [Stage 1 acceptance criteria](#24-stage-1-acceptance-criteria)
25. [Implementation plan](#25-implementation-plan)
26. [Open implementation details](#26-open-implementation-details)
27. [Accepted trade-offs](#27-accepted-trade-offs)

## 1. Purpose of this document

This document describes a system for researching, documenting, and comparing AI coding tools on demand. It defines the product scope, data model, inference rules, roles of the LLM and scripts, operator workflows, validation, and output format.

The rationale behind key decisions has intentionally been retained. It protects the project from later simplifications that would reduce the credibility of the comparison.

## 2. Executive summary

The system researches tools such as GitHub Copilot, Cursor, Claude Code, Devin, Kiro, OpenCode, Antigravity, and future products. It uses public documentation, changelogs, product pages, pricing pages, integration catalogs, and—in the second stage—benchmark sources.

It produces:

1. **Tool profile** — facts, evidence, constraints, technical information, use cases, and a semantic description.
2. **Capability comparison** — tables divided into feature-group tabs, with deterministic flags.
3. **Effectiveness comparison** — in the second stage, benchmarks grouped by the entity providing the results.

The system is not a continuously running web application. It is a collection of agents, skills, configuration, and scripts executed on demand by an operator. Its output is a self-contained HTML file that opens without a server.

Transparency is the system's central principle: results show their sources, availability conditions, research date, data age, and disputed information.

## 3. Problem and objectives

The system supports:

1. **Team enablement** — understanding capabilities, mechanisms, and use cases.
2. **Internal clients** — sharing profiles and comparisons without repeating manual research.
3. **Market monitoring** — maintaining a current view of product capabilities.

The main problem is that vendors use different names for similar features. The solution is a canonical feature taxonomy to which the LLM maps vendor terminology.

A second problem is that documentation mostly describes what a product can do, rather than what it cannot do. The system therefore uses a complete search protocol, after which it may operationally conclude that a feature is not present.

## 4. Guiding principles

### 4.1 The profile is the source; the table is derived

A complete profile of an individual tool is created first. Only then does a script compare selected profiles. The LLM does not generate a table directly from memory.

### 4.2 Capabilities are separate from effectiveness

- **Section A — Capability map:** what the tool provides and under which conditions.
- **Section B — Effectiveness:** how the tool performs in benchmarks.

Vendor documentation can confirm that a feature exists, but not its quality. Effectiveness assessments do not feed into Section A.

### 4.3 The LLM conducts research; scripts enforce controls

The LLM, operating through an agent and the harness's web tools, conducts all research: it discovers sources, opens and evaluates content, searches by meaning, maps information to features, analyzes conflicts, and creates the description. Python scripts maintain run state, prepare contracts, validate results, check the completeness of search traces, manage revisions, calculate flags, generate HTML, and publish valid artifacts.

### 4.4 Always-current, as-is mode

Only the current tool profile is stored. A successful re-research run overwrites the previous state. Profile history and full reproducibility of old results are not maintained.

Generated HTML remains frozen. The risk of incomplete reproducibility is consciously accepted; the research date defines the boundary of responsibility.

### 4.5 A constraint does not remove the `Has` status

If a feature exists in any officially supported product variant, it receives the `Has` status, even when it works only under a specific plan, environment, model, region, beta release, or official integration. These conditions are recorded as constraints.

## 5. Scope and stages

### 5.1 Tools

The scope includes AI coding assistants and agents. The list is open-ended. Adding a tool must not require changes to the generator or to the code of existing profiles.

CLI, editor, IDE plugin, and web access are access-form features, not separate product categories.

### 5.2 Stage 1 — profiles and capability map

The first implementation includes:

- the feature taxonomy and waiting room;
- source onboarding and re-research;
- the complete search protocol;
- statuses, evidence, and constraints;
- profiles and semantic descriptions;
- validation and the repair loop;
- arithmetic flags;
- the Section A comparison and HTML output.

### 5.3 Stage 2 — benchmarks

The second stage includes:

- benchmark sources and data model;
- comparability assessment;
- tabs grouped by result provider;
- distinction between independent and vendor-reported measurements;
- integration of Section B into the HTML output.

Section B is described in this document, but does not block Stage 1.

### 5.4 Out of scope

Feature-change history, a public web application, a sales-oriented view for external clients, sentiment, opinions, and selection of the “best” tool.

## 6. Audience and HTML output

The first artifact is intended for the team and internal clients.

### Comparison view

- one tab for each feature group;
- features in rows and tools in columns;
- statuses, constraints, and flags;
- filters;
- dates and freshness warnings;
- markers for profiles that require research;
- navigation to an individual tool profile.

### Individual tool view

- characteristics and access methods;
- detailed capability map;
- internal tools and mechanisms;
- workflows and use cases;
- integrations, security, and constraints;
- disputed information;
- sources and research date.

Tooltips that display details use conventional hover behavior.

## 7. Objects and lifecycles

### Profile

The current source of truth about a tool. It contains feature results, evidence, constraints, additional facts, use cases, an LLM-generated description, and a date. A failed research run does not replace it.

### Comparison

Created from current profiles. It has its own date as well as each tool's research date. It is a frozen HTML file.

### Feature taxonomy

The canonical feature list has a current revision number used to identify profiles that require research. This does not require taxonomy history to be retained.

### Profile template

The editable list of description sections has its own revision. Changing a required section marks older profiles as requiring re-research.

### Waiting room

Stores capabilities outside the taxonomy. The operator may accept, reject, or defer them.

## 8. Feature taxonomy

The taxonomy has a “group → feature” structure. Each feature contains:

- a stable `feature_id`;
- a name, group, and definition;
- `Has` and `Partial` criteria;
- exclusions;
- aliases and synonyms;
- a research question for the LLM.

The initial taxonomy is created inclusively under human supervision and covers every distinct capability accepted by the curator, including singletons. A candidate contains a definition, group, evidence, sources, and a preliminary relevance suggestion. The suggestion is used only during curation.

There is no “taxonomy maturity” threshold. Every research run performs lightweight detection of new capabilities. Candidates are presented together at a single curation point. The operator may accept, reject, or defer them to the waiting room.

Accepting a feature increments the taxonomy revision. Older profiles receive the `requires_research` state. A missing field for a new feature does not mean `Not found` and does not participate in flags.

## 9. Statuses

### `Has`

There is evidence that the complete definition is satisfied. A quotation and source are required.

### `Partial`

The tool satisfies part of the definition. Evidence and a description of the covered scope are required. This status is not used for a restricted plan, platform, or beta release.

### `Not found`

The complete protocol has been executed and no public confirmation of the feature was found.

> `Not found` means that, as of the research date, the complete protocol found no confirmation in the public sources examined. It is not a claim about private or undocumented functionality.

The evidence is the search trace, not a quotation stating that the feature is absent.

### `Uncertain / disputed`

The research was insufficient, the definition is ambiguous, or sources conflict. A reason must be provided and evidence of the conflict retained.

### `Requires research`

A technical profile state, not a substantive feature status.

## 10. Constraints and integrations

A feature available in any officially supported variant receives `Has`. Conditions are stored as separate constraints:

- plan or license;
- platform or IDE;
- model;
- region;
- product version;
- release stage: experimental, preview, beta, or GA;
- required extension or integration;
- another technical condition.

Each constraint has its own source.

A feature receives `Has` when it is native, implemented through a vendor integration, or provided by a third-party solution that the vendor officially documents and supports. In the latter cases, it receives the `integration_required` constraint.

Community integrations and unofficial workarounds do not affect the table. Mere presence in a marketplace is not sufficient evidence of official support.

The UI cell still displays `HAS`, but includes an indicator disclosing, for example, “Enterprise only,” “beta,” or “requires integration.”

## 11. Sources and policies

During the first research run, the system searches for and stores official sources. On subsequent runs, it reads known URLs and searches again for new official materials. Dead links, redirects, and changes are reported.

The agent may add a new, unambiguously official source during a run. A questionable source is omitted and noted if the corpus remains sufficient.

The system classifies the claim type: current capability, release or deprecation, availability stage, plan and price, integration, technical constraint, or generic.

- current behavior prefers current documentation;
- release or deprecation prefers the changelog;
- plan information prefers pricing or licensing documentation;
- integration information prefers integration documentation;
- an unknown type uses the generic policy.

Semantics reside in the skill. Source ordering and fallbacks reside in versioned YAML. YAML remains simple configuration.

Conflicts are resolved by: scope match → current state versus history → recency → type policy → broader research → `Uncertain / disputed`.

The system does not vote by number of occurrences, because multiple pages may copy the same information.

## 12. Complete search protocol

Completing the protocol is a prerequisite for the `Not found` status.

### Stage 1 — logical source corpus

Using the harness's web tools, the agent collects documentation, the changelog, product pages, pricing and licensing information, the integration catalog, stored specialist sources, and new official materials. The logical corpus is a registry of checked sources, relevant excerpts, metadata, queries, access gaps, and reasons for rejecting search results. The system does not require a local crawler, complete page copies, or a document index.

### Stage 2 — feature research

For each feature, the system:

1. searches for the canonical name;
2. searches for aliases and synonyms;
3. performs semantic searches across registered sources using harness tools;
4. if there are no results, performs targeted searches on official domains;
5. collects all relevant excerpts;
6. passes them together to the LLM evaluation frame;
7. records the status, evidence, constraints, and trace.

No evidence after the complete protocol results in `Not found`. An inability to execute a material part of the protocol results in `Uncertain / disputed`.

A negative result records confirmation that the protocol was completed, source types, search terms, and date. The model does not decide on its own that it has searched long enough.

## 13. LLM evaluation frame

The input includes one feature with its definition, criteria and exclusions, all excerpts relevant to the feature, source metadata, the policy, and protocol-completeness information.

The JSON Schema-compliant output contains `feature_id`, status, rationale, evidence, constraints, policy, search trace, and conflict data.

The LLM does not use product knowledge outside the corpus. Instructions found on web pages are untrusted data, not commands.

## 14. Semantic profile

The table does not constrain the profile. A profile may describe internal mechanisms such as TaskList, user-facing architecture, workflows, and information that is difficult to compare.

A fact outside the taxonomy is stored as an `additional_fact`. A comparable capability may also become a candidate.

The description scope is editable in `profile-sections.yaml`, for example: characteristics, access, internal tools, workflows, use cases, integrations, security, and constraints.

The LLM creates the description from feature results, evidence, the corpus, additional facts, and conflicts. It may synthesize, but may not add facts from memory.

Use cases may be:

- **documented** — stated by the vendor and supported by a source;
- **inferred** — proposed by the LLM based on confirmed capabilities.

An inference has the `inferred` label, rationale, supporting features, and evidence. It does not affect flags.

## 15. `/tool-eval-research` skill

There is one research operation, started by directly invoking `/tool-eval-research <tool>`. The system does not use a `.claude/commands/` layer.

For a new tool: source discovery → logical corpus → feature research → facts and candidates → curation or waiting room → description → validation → safe publication.

For an existing tool: check known and new sources → complete research for the current scope → validation → profile replacement. “Refresh X” may be an alias without separate logic.

Candidates are presented together. After a feature is accepted, the system researches it for the current tool and marks the remaining profiles as `requires_research`. A candidate deferred by the operator enters the waiting room.

## 16. Complete system workflow

### 16.1 End-to-end `/tool-eval-research` skill workflow

From the user's perspective, the entry point is a direct skill invocation: **`/tool-eval-research X`**.

The operation guides the operator through a single curation point at which all candidates detected during the run are considered.

    USER: “/tool-eval-research X”
            │
            ▼
    [1. Run initialization]
            │
            ├─ identify tool and research scope
            ├─ assign run ID
            ├─ load configuration and schemas
            └─ check whether the profile exists
            │
            ▼
    [2. Source preparation]
            │
            ├─ new tool: onboarding
            ├─ existing tool: inspect stored sources
            ├─ search for new sources
            └─ check links and redirects
            │
            ▼
    [3. Logical corpus construction]
            │
            ├─ agents browse sources
            ├─ register relevant excerpts and queries
            └─ classify sources and access gaps
            │
            ▼
    [4. Research all features]
            │
            ├─ names, aliases, and semantic search
            ├─ targeted search when no results are found
            ├─ LLM evaluation frame
            └─ status + evidence + constraints + trace
            │
            ▼
    [5. Expand the profile]
            │
            ├─ additional facts
            ├─ internal mechanisms
            ├─ use cases
            └─ new-feature candidates
            │
            ▼
    [6. Single curation point]
            │
            ├─ accept or reject
            └─ defer to the waiting room
            │
            ▼
    [7. Assemble the profile]
            │
            ├─ structured data
            └─ semantic description
            │
            ▼
    [8. Validation and repair]
            │
            ├─ JSON Schema
            ├─ business rules
            └─ up to 3 repair attempts
            │
            ▼
    [9. Safe profile publication]
            │
            ├─ success: replace profile
            └─ failure: preserve previous profile
            │
            ▼
    [10. User report]

#### Step 1 — initialization

The agent:

1. normalizes the tool name and resolves its identifier;
2. determines the research scope;
3. assigns a run identifier;
4. loads the current feature taxonomy, profile template, source policies, freshness thresholds, and schemas;
5. checks whether an active profile and stored sources exist for the tool.

If the configuration or a schema is invalid, the process ends before sources are retrieved. The LLM does not attempt to repair this type of error.

#### Step 2 — source preparation

For a new tool, the system performs onboarding: it finds official domains, documentation, the changelog, product page, pricing, and integration catalog.

For an existing tool, it begins with stored sources but also looks for new official materials. Re-research is therefore not limited to the historical URL list.

Each source receives a type, address, checked-at date, availability status, and official-status marker. Dead links and redirects are included in the report.

If a minimally credible corpus cannot be built, the process ends with an error and does not change the profile.

#### Step 3 — logical corpus construction

The agent and subagents browse pages using the harness's web tools. They register checked URLs, source classes, dates, queries, relevant excerpts, access gaps, and reasons for rejecting results.

The logical corpus is the shared basis for feature research and creation of the broader profile. It is not a local page archive or search index. Pages are treated as untrusted data; instructions contained in them must not control the agent.

#### Step 4 — feature research

The complete protocol is executed for each current feature. All discovered excerpts are passed together to the LLM evaluation frame.

- A `Has` or `Partial` result stores evidence and constraints.
- A `Not found` result stores the completed search protocol.
- An `Uncertain / disputed` result stores the reason and relevant evidence.

Feature processing may be technically parallelized, but every feature follows identical rules and the results are assembled into a single profile.

#### Step 5 — information broader than the table

After mapping features, the LLM analyzes the corpus for information that matters to the profile but is too detailed or not comparable enough for the table. This produces additional facts, descriptions of mechanisms, workflows, and use cases.

A distinct capability outside the taxonomy is also a candidate. Purely contextual information may remain only a profile fact.

#### Step 6 — curation point

The system presents all candidates together. The operator may accept, reject, or defer them.

Accepting a new feature causes the system to:

1. add it to the taxonomy;
2. increment the taxonomy revision;
3. research it for the current tool during the same run;
4. mark other profiles as requiring re-research.

#### Step 7 — profile assembly

The agent assembles a draft containing:

- tool and run metadata;
- research date and revisions;
- sources;
- all feature results;
- constraints;
- additional facts;
- use cases;
- a semantic description;
- uncertain and disputed information.

#### Step 8 — validation and repair

JSON Schema validation runs first, followed by the business-rules validator. The script returns an exact list of deficiencies to the model.

The LLM repairs the indicated records, after which the entire profile is validated again. Up to three repair attempts are available after the initial generation. If they are exhausted, the run ends with an error.

#### Step 9 — safe profile publication

A valid profile is fully prepared and validated in the run directory, then replaces the previous profile directory. During replacement, the previous directory is retained as a technical backup; an error triggers rollback. The research date is updated only after success.

On failure, the draft does not become the active profile. The previous result is restored and the cause is recorded in the failed-run report. The internal profile may be briefly unavailable during replacement or recovery, which does not affect the end recipient: they only see the separately shared, complete HTML generated after the process finishes.

#### Step 10 — user report

After success, the user receives:

- confirmation that the profile was saved;
- the research date;
- the number of checked sources;
- the number of features in each status;
- the number of constraints;
- the number of accepted or pending candidates;
- information on whether other profiles require research;
- the path to the output.

After an error, the user receives the stage at which the run stopped, the cause, the number of repair attempts used, and confirmation that the previous profile was not overwritten.

### 16.2 `/tool-eval-compare` skill workflow

The entry point is a direct skill invocation: **`/tool-eval-compare A B C`**.

    USER: “/tool-eval-compare A B C”
            │
            ▼
    [1. Resolve tools]
            │
            ▼
    [2. Load active profiles]
            │
            ├─ missing profile → error for that tool
            └─ old revision → warning
            │
            ▼
    [3. Check dates and revisions]
            │
            ├─ data age
            └─ date spread
            │
            ▼
    [4. Arrange features by tab]
            │
            ▼
    [5. Deterministically calculate flags]
            │
            ▼
    [6. Assemble tables and profiles into HTML]
            │
            ▼
    [7. Validate and save the artifact]
            │
            ▼
    [8. User report]

The skill does not re-research old profiles. It displays warnings and leaves the decision to the operator. A missing or unresearched feature is not converted to `Not found` and does not participate in flags.

After success, the user receives the comparison date, a list of profiles used and their dates, freshness warnings, and the path to the HTML file.

### 16.3 Main failure paths

| Situation | Behavior |
|---|---|
| Invalid configuration or schema | End before research |
| No credible sources for a new tool | Do not create a profile |
| Some sources unavailable | `Uncertain / disputed` if a valid profile can still be built |
| Excessive source loss | Reject the run and preserve the old profile |
| Repairable validation error | Up to three repair attempts |
| Error after three attempts | Reject the run |
| Missing profile during comparison | Message identifying the tool that requires research |
| Profile at an old revision | Compare with a warning and omit flags for incomplete features |

## 17. Validation and persistence

### Two layers

JSON Schema validates structure and types. The business validator checks:

- one result for every feature;
- evidence for `Has` and `Partial`;
- the protocol for `Not found`;
- a reason for `Uncertain / disputed`;
- sources for constraints;
- identifier validity;
- date, revisions, and required sections;
- resolution or deferral of candidates.

### Repair loop

The validator returns an error code, path, `feature_id`, and description. The LLM receives the invalid fragment, sources, and errors. After correction, the entire profile is validated again.

Up to three repair attempts are allowed after the initial generation. An error that cannot be repaired by the LLM terminates the process immediately.

### Publication

A new profile replaces the active one only after staging validation succeeds completely. Replacement uses a technical backup, rollback, and recovery. On failure, the previous profile and its date are restored, the incomplete result is not published, and the attempt is reported. The HTML report is a separate, frozen artifact made available to the recipient only after generation finishes.

## 18. Comparison and flags

The `/tool-eval-compare A B C` skill loads profiles, checks revisions and dates, arranges data, calculates flags with a script, and generates HTML.

A comparison may be created despite `requires_research` profiles, but it displays a warning. Unresearched cells are not `Not found` and do not participate in flags.

- `Has` with a constraint counts as `Has`;
- `Partial` counts as neither `Has` nor `Not found`;
- `Uncertain / disputed` and an unresearched cell exclude the feature from flags;
- any occurrence of `Partial` produces `Varied implementation`.

Distribution flags require at least four tools and a complete set of unambiguous results:

- **Only one has it** — one `Has`, all others `Not found`.
- **Only one lacks it** — one `Not found`, all others `Has`.
- **Rare** — two `Has`, all others `Not found`.
- **Common in this comparison** — all have it or only one lacks it.
- **Split** — the difference between the number of `Has` and `Not found` results is at most one.
- **Varied implementation** — at least one `Partial` result exists.

Flags may coexist. They always refer to the compared set, not the entire market.

## 19. Freshness

Each profile has a research date and each comparison has a generation date.

- 0–30 days — current;
- 31–60 days — aging;
- more than 60 days — stale;
- more than 14 days' spread between profiles — warning.

Thresholds are configurable in YAML. The system warns but does not force re-research.

## 20. Section B — Stage 2

Section B contains objective benchmarks, without sentiment or opinions.

The main tab represents the entity performing or providing the evaluation. Within it are separate tables for benchmarks and comparable configurations. Different configurations are not merged into a single ranking.

Each result distinguishes:

- `benchmark_owner` — the benchmark creator;
- `evaluator` — the party performing the measurement;
- `publisher` — the publishing party.

If a vendor cites a leaderboard, the leaderboard operator remains the result provider.

A source is labeled as an official leaderboard, independent measurement, vendor self-evaluation, vendor comparison of competitors, or third-party source. Vendor results remain visible with a clearly disclosed conflict of interest.

A measurement includes the benchmark and version, harness, metric and mode, model, tool version, configuration, result, date, evaluator, publisher, source, and verification information.

Direct comparison requires key conditions to match. Other measurements are shown separately. A missing result means no published measurement, not zero.

Hierarchy: official leaderboard → independent publication or paper → vendor report → third-party source. Other results are not removed; tabs expose discrepancies.

## 21. Technical roles

The **agent** conducts research and manages phases, curation, validation, and safe publication.

The **entry skills** `/tool-eval-research`, `/tool-eval-compare`, and `/tool-eval-resume` are direct user entry points. **Domain skills** describe onboarding, claim types, feature research, conflicts, candidates, profiles, and Section B.

The **scripts** maintain run state, prepare manifests, validate data and trace completeness, merge results, manage revisions, calculate flags, check freshness, generate HTML, and publish and restore profiles.

Page content is untrusted. Prompt injection must not control the agent.

## 22. Configuration

Logical layout:

- `config/source-policies.yaml`;
- `config/freshness.yaml`;
- `config/profile-sections.yaml`;
- `config/feature-taxonomy.yaml`;
- `config/tools/`;
- `schemas/`;
- `data/profiles/`;
- `data/feature-candidates/`;
- `.work/failed-runs/`;
- `outputs/comparisons/`.

The names are proposals. Configuration must be separated from skill instructions, profiles from comparisons, candidates from the taxonomy, and failed runs from active data.

## 23. Non-functional requirements

- **Transparency:** evidence, traces for negative results, constraint sources, conflict reasons, and dates.
- **Extensibility:** add a tool through `/tool-eval-research X`, add features through the waiting room, and edit sections and policies.
- **Consistency:** an incomplete profile does not replace a valid one; a failure does not silently turn `Has` into `Not found`.
- **Security:** HTML sanitization, safe links, no execution of code from sources, and no secrets.
- **Self-containment:** HTML works locally without a backend.
- **Cost:** configurable limits for time, sources, and LLM calls; exceeding a limit does not save an incomplete profile.

## 24. Stage 1 acceptance criteria

1. `/tool-eval-research X` creates a profile for a new tool.
2. Re-research uses known sources and searches for new official sources.
3. Every current feature has exactly one valid result.
4. Results contain the required evidence or protocol trace.
5. Constraints are structured, source-backed, and visible in the UI.
6. An official integration may produce `Has`; a community integration does not affect the status.
7. Candidates are curated together or enter the waiting room.
8. A taxonomy or template change marks older profiles.
9. The validator returns specific errors and starts no more than three repairs.
10. Failed research does not change the profile or date.
11. `/tool-eval-compare` creates self-contained HTML with tabs and profiles.
12. Flags are deterministic and incomplete features are excluded.
13. HTML shows dates, age, and date spread.
14. A profile contains an LLM-generated description, additional facts, and both types of use cases.
15. Page content cannot control the agent or execute code in HTML.

## 25. Implementation plan

1. **Foundation:** taxonomy of 20–30 features, stable IDs, schemas, configuration, and validator.
2. **Individual tool:** onboarding, logical corpus, LLM evaluation frame, constraints, profile, and publication.
3. **Comparison:** tables, flags, freshness, navigation, and HTML.
4. **Operations:** waiting room, reports, recovery, and limits.
5. **Section B:** measurement schema, providers, comparability, and tabs.

## 26. Open implementation details

The implementation plan resolves architecture and conventions that remained open in the previous version of this document. In particular, it adopts:

- the profile model, division of responsibility between JSON Schema and the business validator, and schema conventions — D-016;
- error-code families, error-record contents, retries, failed runs, and resume — D-011;
- the logical source registry, scope of retained evidence, and negative-result protocol — D-006 and D-009;
- the format of profiles, run artifacts, and failed attempts — D-007, D-011, and Section 3 of the plan;
- the minimal dependency stack, method for building self-contained HTML, and supported browsers — D-013 and D-014;
- Claude Code as the MVP harness and directly invoked user skills — D-015 and D-018.

Only implementation details that do not block the start of development remain open:

- final content of individual JSON Schemas within the adopted model;
- exact skill instructions for the LLM evaluation frame and the first validation examples;
- initial groups and 20–30 features prepared under curator supervision;
- specialist classes of official sources required for particular tools;
- exact time, work, and search limits, calibrated during the pilot;
- exact dependency versions within the adopted ranges, selected after installation and main-flow verification;
- the benchmark list and detailed Stage 2 contracts.

Changing any adopted decision requires updating the implementation plan and, if it affects product behavior or acceptance criteria, this requirements document as well.

## 27. Accepted trade-offs

The system deliberately:

- treats a lack of confirmation after the complete protocol as `Not found`;
- treats a constrained or officially integrated feature as `Has`, while exposing its conditions;
- allows the LLM to create a broader description and infer explicitly labeled use cases;
- does not retain profile history;
- allows comparison of older profiles but excludes unresearched features from flags;
- uses a single `/tool-eval-research X` workflow, initiated by direct skill invocation at the operator's request;
- separates capabilities from effectiveness;
- implements Section B after Stage 1 has stabilized;
- leaves curation to the operator and validation and arithmetic to scripts.

The most important quality measure is the ability to understand where a conclusion came from, the date through which it is current, and which constraints affect its meaning.
