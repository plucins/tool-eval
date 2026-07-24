---
name: dialogue-graph-value
description: Query the context graph to demonstrate captured value. Use when the user asks about gaps, coverage, decisions, assumptions, or wants to understand what's been captured. Triggers on "what's missing", "show me gaps", "why did we", "what do we know about", "who knows", "unvalidated assumptions", "coverage", "trace to".
allowed-tools: Bash, Read
---

# Dialogue: Graph Value

Query the context graph to surface insights from captured information. This skill demonstrates the value of systematic capture by answering questions that would otherwise require searching through documents, code, and memories.

## Framework Grounding

This skill operationalises:
- **TMS (Transactive Memory System)**: Directory lookup, allocation queries
- **Traceability**: Requirements → Design → Implementation chains
- **Risk visibility**: Unvalidated assumptions, contradicted theories
- **Context preservation**: "Why did we..." queries that restore decision context

## Relationship to context-graph Skill

This skill is a **user-facing layer** that wraps the existing `dialogue-evo:context-graph` skill.

| Skill | Purpose | Audience |
|-------|---------|----------|
| `context-graph` | Graph operations: init, configure, status, raw queries | Operators, setup |
| `graph-value` | Value demonstration: coverage, risk, context, TMS queries | Users, daily work |

**How they interact:**

```
User asks: "What's missing?"
    │
    ▼
┌─────────────────────────────────────┐
│  dialogue-graph-value               │
│  - Classifies intent (coverage)     │
│  - Selects appropriate query        │
│  - Formats output for human         │
│  - Suggests follow-up actions       │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  context-graph (raw query)          │
│  - Executes SurrealDB query         │
│  - Returns structured data          │
└─────────────────────────────────────┘
```

**What graph-value adds:**
- Natural language classification
- Human-readable output formatting
- Suggested actions based on results
- Progressive disclosure (adapts vocabulary to user)
- The "aha moment" framing — value, not mechanics

**When to use which:**
- User asks about gaps, risk, rationale → `graph-value`
- Need to initialise or configure the graph → `context-graph`
- Building tooling that needs raw JSON → `context-graph` with `--format json`
- Debugging graph structure → `context-graph status`

## When to Use

Use this skill when the user:
- Asks about gaps or coverage ("What's missing?", "What requirements have no implementation?")
- Asks about rationale ("Why did we choose X?", "What led to this decision?")
- Asks about risk ("What assumptions haven't been validated?", "What's at risk?")
- Asks about knowledge location ("Who knows about X?", "Where is this documented?")
- Wants to see what's been captured ("What do we know?", "Show me the graph")
- Returns after time away ("What changed?", "Where was I?")

## Query Categories

### 1. Coverage Queries

Surface gaps between what's specified and what's built.

| Query Intent | Natural Language | Graph Query |
|--------------|------------------|-------------|
| Requirements without design | "What requirements have no design?" | `undesigned-requirements` |
| Requirements without implementation | "What's not implemented yet?" | `unimplemented-requirements` |
| Implementations without requirements | "What's undocumented?" | `orphan-implementations` |
| Untested implementations | "What's not tested?" | `untested-implementations` |

### 2. Risk Queries

Surface areas where we're proceeding at risk.

| Query Intent | Natural Language | Graph Query |
|--------------|------------------|-------------|
| Unvalidated assumptions | "What assumptions haven't been checked?" | `unvalidated-assumptions` |
| Decisions depending on unvalidated assumptions | "What's at risk if assumptions are wrong?" | `at-risk-decisions` |
| Contradicted theories | "What understanding has been challenged?" | `contradicted-theories` |
| Stale artifacts | "What's out of date?" | `stale-artifacts` |

### 3. Context Queries

Restore understanding about why things are the way they are.

| Query Intent | Natural Language | Graph Query |
|--------------|------------------|-------------|
| Decision rationale | "Why did we choose X?" | `decision-context` |
| Requirement provenance | "Where did this requirement come from?" | `requirement-provenance` |
| Implementation justification | "Why is it built this way?" | `implementation-chain` |
| Change history | "What changed since [date]?" | `session-delta` |

### 4. TMS Queries

Support transactive memory — knowing who knows what.

| Query Intent | Natural Language | Graph Query |
|--------------|------------------|-------------|
| Knowledge location | "Who knows about X?" | `who-knows` |
| Actor contributions | "What has [actor] worked on?" | `actor-contributions` |
| Expertise domains | "Who's the expert on X?" | `domain-experts` |

## How to Query

### Interactive Mode (Recommended)

When a user asks a natural language question, classify and execute the appropriate query:

```
User: "What requirements haven't been implemented yet?"
AI: [Executes unimplemented-requirements query]
    [Formats results for human consumption]
    [Offers follow-up actions]
```

### Direct Query Mode

For specific queries, execute via script:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-graph-value/scripts/query-graph.sh <query-name> [parameters]
```

## Query Implementations

### Coverage Queries

#### `unimplemented-requirements`

Find requirements with no satisfying implementation.

```bash
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-graph-value/scripts/query-graph.sh unimplemented-requirements
```

**SurrealDB Query:**
```surql
SELECT id, title, status, created
FROM artifact
WHERE artifact_type = 'REQUIREMENT'
  AND status = 'ACTIVE'
  AND count(<-satisfies<-artifact WHERE artifact_type = 'IMPLEMENTATION') = 0
ORDER BY created DESC;
```

**Output format:**
```
Unimplemented Requirements (3 found):

  REQ-001: User authentication required
    Created: 2026-03-10
    Status: ACTIVE

  REQ-003: Session timeout after inactivity
    Created: 2026-03-12
    Status: ACTIVE

  REQ-007: Audit logging for admin actions
    Created: 2026-03-14
    Status: ACTIVE

Suggested actions:
  - Review priorities: Are these deferred intentionally?
  - Start implementation: "Let's implement REQ-001"
  - Log deferral: "Defer REQ-007 to next iteration"
```

#### `orphan-implementations`

Find implementations that don't trace to requirements.

```bash
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-graph-value/scripts/query-graph.sh orphan-implementations
```

**SurrealDB Query:**
```surql
SELECT id, title, source_path, created
FROM artifact
WHERE artifact_type = 'IMPLEMENTATION'
  AND status = 'ACTIVE'
  AND count(->satisfies->artifact) = 0
ORDER BY created DESC;
```

**Output format:**
```
Orphan Implementations (2 found):

  IMP-005: ErrorBoundary component
    Path: src/components/ErrorBoundary.tsx
    Created: 2026-03-13
    No requirement trace

  IMP-008: Rate limiter middleware
    Path: src/middleware/rateLimiter.ts
    Created: 2026-03-15
    No requirement trace

These may be:
  - Emergent requirements (discovered during build)
  - Scope creep (features added without approval)
  - Infrastructure (may not need explicit requirements)

Suggested actions:
  - Link to requirement: "Link IMP-005 to REQ-002"
  - Create requirement: "Create requirement for rate limiting"
  - Mark as infrastructure: "IMP-005 is infrastructure, no requirement needed"
```

#### `undesigned-requirements`

Find requirements with no design decisions.

```bash
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-graph-value/scripts/query-graph.sh undesigned-requirements
```

**SurrealDB Query:**
```surql
SELECT id, title, status
FROM artifact
WHERE artifact_type = 'REQUIREMENT'
  AND status = 'ACTIVE'
  AND count(<-satisfies<-artifact WHERE artifact_type IN ['ADR', 'DOCUMENT'] AND content_domain = 'DES') = 0
ORDER BY created DESC;
```

### Risk Queries

#### `unvalidated-assumptions`

Find assumptions that haven't been validated.

```bash
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-graph-value/scripts/query-graph.sh unvalidated-assumptions
```

**SurrealDB Query:**
```surql
SELECT id, title, created,
       count(<-assumes<-artifact) AS dependent_decisions
FROM artifact
WHERE artifact_type = 'ASSUMPTION'
  AND status IN ['ACTIVE', 'UNVALIDATED']
  AND count(<-validates<-artifact) = 0
ORDER BY dependent_decisions DESC;
```

**Output format:**
```
Unvalidated Assumptions (4 found):

  HIGH RISK (multiple decisions depend on these):

    ASM-002: "Database can handle 10k concurrent connections"
      Depends on: 3 decisions (ADR-001, DEC-012, DEC-015)
      Created: 2026-03-08
      Action: Validate with load testing

    ASM-005: "Third-party API has 99.9% uptime"
      Depends on: 2 decisions (DEC-018, DEC-019)
      Created: 2026-03-11
      Action: Check SLA, add fallback

  LOWER RISK (fewer dependencies):

    ASM-007: "Users prefer dark mode"
      Depends on: 1 decision
      Created: 2026-03-14

    ASM-009: "Mobile traffic is <20%"
      Depends on: 0 decisions
      Created: 2026-03-15

Suggested actions:
  - Validate assumption: "Let's test ASM-002"
  - Accept risk: "We'll proceed at risk on ASM-005"
  - Invalidate: "ASM-009 is wrong, mobile is actually 40%"
```

#### `at-risk-decisions`

Find decisions that depend on unvalidated assumptions.

```bash
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-graph-value/scripts/query-graph.sh at-risk-decisions
```

**SurrealDB Query:**
```surql
SELECT
  decision.id,
  decision.title,
  assumption.id AS risky_assumption,
  assumption.title AS assumption_title
FROM artifact AS decision
WHERE decision.artifact_type IN ['ADR', 'DECISION']
  AND decision.status = 'ACTIVE'
  AND decision->assumes->artifact.status IN ['ACTIVE', 'UNVALIDATED']
  AND count(decision->assumes->artifact<-validates<-artifact) = 0;
```

#### `contradicted-theories`

Find theories that have contradicting evidence.

```bash
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-graph-value/scripts/query-graph.sh contradicted-theories
```

**SurrealDB Query:**
```surql
SELECT
  id, title,
  <-validates<-artifact AS supporting_evidence,
  <-contradicts<-artifact AS contradicting_evidence
FROM artifact
WHERE artifact_type = 'THEORY'
  AND count(<-contradicts<-artifact WHERE resolution_status = 'UNRESOLVED') > 0;
```

### Context Queries

#### `decision-context`

Restore full context for a decision.

```bash
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-graph-value/scripts/query-graph.sh decision-context <decision-id>
```

**SurrealDB Query:**
```surql
SELECT
  *,
  ->assumes->artifact AS assumptions,
  ->satisfies->artifact AS requirements_addressed,
  <-derives_from<-artifact AS derived_artifacts,
  <-created<-actor_human AS decision_maker
FROM artifact:<decision-id>;
```

**Output format:**
```
Decision Context: ADR-001

  Title: Use filesystem for initial Context Graph storage
  Date: 2026-03-06
  Made by: human:pidster
  Status: Accepted

  Why this decision was made:
    Context: Need to store Context Graph data for TMS operations.
             Must support location-agnostic access and future migration.

    Rationale: Start simple, evolve when needed. Filesystem provides
               immediate value without premature optimisation.

  Assumptions made:
    - ASM-001: File system performance adequate for current scale [UNVALIDATED]
    - ASM-003: YAML human-readability valuable for debugging [VALIDATED]

  Requirements addressed:
    - REQ-002: Context persistence across sessions
    - REQ-004: Human-reviewable storage

  What depends on this:
    - IMP-001: Context graph YAML storage
    - IMP-003: Graph resolver abstraction
    - DEC-015: Query implementation approach
```

#### `session-delta`

Show what changed since a given time.

```bash
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-graph-value/scripts/query-graph.sh session-delta [since-date]
```

**SurrealDB Query:**
```surql
LET $since = <datetime>$date;

SELECT
  artifact_type,
  array::group(id) AS ids,
  count() AS count
FROM artifact
WHERE created > $since OR updated > $since
GROUP BY artifact_type
ORDER BY count DESC;
```

**Output format:**
```
Changes since 2026-03-15 (yesterday):

  Decisions: 3 new
    - DEC-20260316-091500: API versioning approach
    - DEC-20260316-103000: Error handling strategy
    - DEC-20260316-142000: Cache invalidation

  Observations: 5 new
    - OBS-20260316-094500: Test coverage at 78%
    - OBS-20260316-110000: Performance regression in auth
    [+3 more]

  Requirements: 1 updated
    - REQ-005: Status changed to IMPLEMENTED

  Implementations: 2 new
    - IMP-012: Auth service refactor
    - IMP-013: Cache layer

Summary: 11 artifacts created/updated
```

### TMS Queries

#### `who-knows`

Find actors with knowledge about a topic.

```bash
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-graph-value/scripts/query-graph.sh who-knows <topic>
```

**SurrealDB Query:**
```surql
SELECT
  in AS actor,
  out.title AS topic,
  confidence,
  last_interaction,
  evidence
FROM knows
WHERE out.title @@ $topic OR out.summary @@ $topic
ORDER BY confidence DESC, last_interaction DESC;
```

**Output format:**
```
Who knows about "authentication"?

  human:pidster
    Confidence: HIGH
    Last interaction: 2026-03-15
    Evidence: Created ADR-001, implemented auth service
    Artifacts: 12 related

  ai:claude
    Confidence: MEDIUM
    Last interaction: 2026-03-16
    Evidence: Assisted with auth refactor
    Artifacts: 8 related

  human:reviewer
    Confidence: LOW
    Last interaction: 2026-03-10
    Evidence: Reviewed auth PR
    Artifacts: 2 related
```

## Progressive Disclosure

The skill adapts to user sophistication:

### New User (first queries)
- Simple natural language: "What's missing?"
- Plain language results
- Suggested actions as prompts
- No graph terminology

### Growing Familiarity
- Introduce artifact types: "3 requirements without implementations"
- Show relationships: "This decision depends on 2 assumptions"
- Offer deeper queries: "Want to see what depends on this?"

### Deep Engagement
- Full graph vocabulary appropriate
- Direct query syntax available
- Complex multi-hop queries supported

## Error Handling

### No Results
```
No unimplemented requirements found.

This means either:
- All requirements have implementations (great!)
- No requirements have been captured yet

If you expected results, try:
- "Show me all requirements" to see what's captured
- Log a requirement: "The system must authenticate users"
```

### Database Not Running
```
Context graph database not available.

The graph queries require SurrealDB to be running.
Start it with: surreal start --log info file://${DIALOGUE_RUNTIME}/context-graph.db

Or use file-based queries (limited): query-graph.sh --file-mode <query>
```

### Empty Graph
```
The context graph is empty — no artifacts captured yet.

This is normal at the start of a project. The graph populates as you:
- Log decisions: "Decided to use React for the frontend"
- Log observations: "Tests are passing"
- Run processes: Problem framing, requirements elicitation

Start with: "Let's capture the vision for this project"
```

## Integration with Other Skills

| Skill | Integration |
|-------|-------------|
| `context-graph` | Underlying query execution (this skill wraps it) |
| `dialogue-log-decision` | Query results may prompt logging |
| `dialogue-log-observation` | Gaps become observations |
| `dialogue-assess-phase` | Coverage queries inform phase readiness |
| `dialogue-structured-elicit` | Missing items drive elicitation |
| `dialogue-infer-from-code` | Populates graph that this skill queries |

## Output Formats

### Human (default)
Readable prose with suggested actions.

### Structured (for tooling)
```bash
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-graph-value/scripts/query-graph.sh --format json <query>
```

Returns JSON for integration with other tools.

### Summary (for status checks)
```bash
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-graph-value/scripts/query-graph.sh --format summary <query>
```

Returns counts only: "3 unimplemented requirements, 4 unvalidated assumptions"

---

## Script Implementation Notes

The `query-graph.sh` script should:

1. **Check database availability** — Fall back to file-based queries if SurrealDB unavailable
2. **Accept natural language** — Map common phrases to query names
3. **Format for context** — Adapt output based on result count and user history
4. **Suggest actions** — Every query result includes actionable next steps
5. **Support piping** — JSON output for toolchain integration

### File-Based Fallback

When SurrealDB is not running, provide limited queries against YAML files:

```bash
# File-based query (limited)
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-graph-value/scripts/query-graph.sh --file-mode unvalidated-assumptions
```

This searches `.dialogue/evo/v1/context-graph/` YAML files directly. Slower and less powerful, but works without database.

---

*Part of the Dialogue Framework — demonstrating value from systematic capture*
