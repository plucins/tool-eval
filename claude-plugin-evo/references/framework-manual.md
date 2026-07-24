# AI-Augmented SDLC Framework: Usage Manual

**Version**: 1.3
**Purpose**: Operational guidance for practitioners using the framework day-to-day.
**Audience**: Developers, teams, and AI agents working within the framework.

---

## Quick Reference

### Seven Phases

| Phase | Focus | Information Composition |
|-------|-------|------------------------|
| **1. Initiation** | Why: business case, stakeholder alignment | 5% formal, 75% tacit, 20% emergent |
| **2. Planning** | How: resource allocation, governance | 35% formal, 55% tacit, 10% emergent |
| **3. Requirements** | What: stakeholder needs to specs | 40% formal, 50% tacit, 10% emergent |
| **4. Design** | Structure: architecture decisions | 50% formal, 40% tacit, 10% emergent |
| **5. Implementation** | Build: code and components | 55% formal, 35% tacit, 10% emergent |
| **6. Testing** | Correctness: verification | 60% formal, 30% tacit, 10% emergent |
| **7. Operations** | Value: deploy, operate, maintain | 60% formal, 30% tacit, 10% emergent |

**Phase Dynamics**: Phases overlap and cycle—not strictly sequential:
- **Common loops**: Requirements↔Design (mutual refinement), Implementation↔Testing (TDD), Testing→Requirements (acceptance mismatch)
- **Loop cost**: Shorter loops (adjacent phases) = low cost, expected; longer loops (e.g., Testing→Initiation) = high cost, indicates information debt
- **Backward events are valid**: Discoveries that invalidate earlier understanding trigger legitimate returns to earlier work

### Eight Capabilities

| Capability | Description |
|------------|-------------|
| **Elicit** | Extract information from sources |
| **Analyse** | Decompose, classify, identify patterns |
| **Synthesise** | Combine into coherent understanding |
| **Transform** | Convert between representations |
| **Validate** | Confirm correctness and fitness |
| **Decide** | Select among alternatives |
| **Generate** | Produce artifacts |
| **Preserve** | Capture for future retrieval |

### Five Collaboration Patterns

| Pattern | Human Role | AI Role | When to Use |
|---------|------------|---------|-------------|
| **Human-Only** | All activities | Absent or passive observer | Human executes alone; AI may provide ambient support |
| **Human-Led** | Drives, decides | Supports, prepares | Human could complete alone; AI accelerates |
| **Partnership** | Unique judgement | Unique capability | Neither could complete alone |
| **AI-Led** | Reviews, validates | Drives execution | AI could complete; human ensures correctness |
| **AI-Only** | Governs, audits | Autonomous within bounds | Human defines rules and oversees; AI executes |

### Agent Team Architecture

The framework separates human interaction from operational process management through an agent team (THY-008):

```mermaid
flowchart TD
    Human(["Human"])

    subgraph Team["Agent Team (Persistent)"]
        DA["@dialogue-agent<br/>Manages: Scope · Situation · System"]
        PO["@process-orchestrator<br/>Manages: Phase · Process"]
        DM["@dialogue-monitor<br/>Reads: All dimensions"]
    end

    subgraph Ephemeral["Task Workers (Ephemeral)"]
        PE["@process-executor"]
        PA["@process-architect"]
    end

    CG[("Context Graph<br/>Shared State")]

    Human <-- "natural conversation" --> DA
    DA <-- "SendMessage" --> PO
    DA <-- "SendMessage" --> DM
    DM -- "alerts" --> DA
    DM -- "alerts" --> PO
    PO -- "spawns" --> PE
    PO -- "spawns" --> PA
    DA <-. "read/write" .-> CG
    PO <-. "read/write" .-> CG
    DM <-. "read" .-> CG
```

| Agent | Lifecycle | Role | 3S2P Contract |
|-------|-----------|------|---------------|
| **@dialogue-agent** | Persistent | Conversational partner; follows your thread; captures tacit knowledge | Manages Scope, Situation, System; Reads Phase, Process |
| **@process-orchestrator** | Persistent | Phase management; coordination; spawns task workers | Manages Phase, Process; Reads Scope, Situation, System |
| **@dialogue-monitor** | Persistent | Background monitoring of git upstream and context graph | Reads all five dimensions |
| **@process-executor** | Ephemeral | Executes specific tasks; terminates on completion | Receives all at spawn |

**Why a team, not a single agent?** A single agent cannot simultaneously tolerate non-linear human thinking and enforce systematic process management. The team separates concerns while the context graph provides shared state.

**What this means in practice:**

- You converse with @dialogue-agent naturally — it never redirects you to a "proper" sequence
- Phase tracking, readiness assessment, and coordination happen via @process-orchestrator internally
- @dialogue-monitor watches git upstream and alerts the team when relevant changes occur
- When a process concern needs your input, @dialogue-agent translates it into natural conversation
- The context graph stores 3S2P dimensional state; all agents coordinate through it

---

## Logging Decisions and Observations

### When to Record

| Capability Output | Record Type |
|-------------------|-------------|
| Elicit, Analyse, Synthesise, Transform, Validate, Generate | **Observation** |
| **Decide** | **Decision** |
| Preserve | Operates on both |

---

## Skills Reference

### Skills

| Skill | Purpose | Triggers |
|-------|---------|----------|
| `dialogue-log-decision` | Record decisions with rationale | "log decision", "record decision" |
| `dialogue-log-observation` | Record observations | "log observation", "note finding" |
| `dialogue-create-adr` | Create Architecture Decision Records | "create ADR", "record architecture decision" |
| `dialogue-resolve-reference` | Resolve reference IDs to content | "resolve reference", "look up THY-001" |
| `dialogue-structured-elicit` | Gather context through questions | "gather requirements", "elicit context" |
| `dialogue-verify-logging-compliance` | Validate logging occurred | "verify logging", "check compliance" |
| `build-only-validate-capability-flow` | Validate spec against constraints | "validate capability flow" |

### Skill Usage

**Log a decision**:
```bash
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-log-decision/scripts/log-decision.sh \
  <OPERATIONAL|TACTICAL> \
  "<ai:claude|human:id>" \
  "<subject>" \
  "<outcome>" \
  "<rationale>" \
  "[context]" \
  "[tags]"
```

**Log an observation**:
```bash
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-log-observation/scripts/log-observation.sh \
  <MEASUREMENT|STATE|EVENT> \
  "<ai:claude|human:id>" \
  "<subject>" \
  "<value>" \
  "[context]" \
  "[tags]"
```

**Verify logging compliance**:
```bash
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-verify-logging-compliance/scripts/verify-logging.sh \
  "<process-identifier>" \
  <min-decisions> \
  <min-observations>
```

**Create an ADR**:
```bash
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-create-adr/scripts/create-adr.sh \
  "<human:id|ai:id>" \
  "<title>" \
  "<context>" \
  "<decision>" \
  "<alternatives>" \
  "<consequences>" \
  "<rationale>"
```

**Resolve a reference**:
```bash
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-resolve-reference/scripts/resolve-reference.sh \
  <id> \
  [full|metadata|path]
```

Supported reference types: `THY-NNN`, `REF-NNN`, `STR-NNN`, `ADR-NNN`, `DEC-*`, `OBS-*`, `SH-NNN`, `FW-NNN`, `human:<id>`, `ai:<id>`

### Decision Granularity Rule

**One decision per distinct choice**. Do not batch multiple decisions into a single entry.

Correct:
```bash
# Separate entries
log-decision.sh OPERATIONAL "ai:claude" "PA-1 pattern" "Partnership" "Both essential"
log-decision.sh OPERATIONAL "ai:claude" "PA-2 pattern" "AI-Only" "Document review is mechanical"
```

Incorrect:
```bash
# Batched (DON'T DO THIS)
log-decision.sh OPERATIONAL "ai:claude" "PA-1 through PA-5" "Various patterns" "Various rationales"
```

---

## Log Locations

```
.dialogue/
├── logs/
│   ├── decisions/       # Decision records (per-file)
│   └── observations/    # Observation records (per-file)
├── tasks/               # Task records (per-file)
└── README.md
```

---

## Team Modes

The framework adapts behaviour based on team context (FW-040). This right-sizes overhead for solo developers while providing full collaboration features for teams.

### Configuration

In `.dialogue/config.yaml`:

```yaml
# Options: auto | solo | team
team_mode: auto
```

| Mode | Detection | Use Case |
|------|-----------|----------|
| **auto** | 2+ users active within 30 days → team | Default; self-adjusting |
| **solo** | Forced | Solo developer; minimal overhead |
| **team** | Forced | Team project; full collaboration |

### Feature Differences

| Feature | Solo Mode | Team Mode |
|---------|-----------|-----------|
| Git sync reminders | Disabled | After task/decision changes |
| Pull check on session start | Skip | Warn if behind remote |
| User registration files | Skip | Create `.dialogue/users/{user}.yaml` |
| Session memo naming | `.dialogue/session-memo.yaml` | `.dialogue/session-memo-{user}.yaml` |
| Session start verbosity | Minimal collaboration hints | Full collaboration guidance |

### Unaffected Features

These work identically in both modes:
- Decision and observation logging
- Task management
- Per-file artifact structure
- Context graph operations

### Detection Logic

Auto-detection counts users in `.dialogue/users/` with `last_seen` timestamps within 30 days. If 2+ users are active, team mode activates.

**Detection script**: `claude-plugin-evo/hooks/scripts/detect-team-mode.sh`

### Git Sync Status

In team mode, session start checks git sync status:

| Status | Meaning | Action |
|--------|---------|--------|
| synced | Local matches remote | No warning |
| ahead | Local has unpushed commits | No warning (push when ready) |
| behind | Remote has new commits | Warning: pull recommended |
| diverged | Both have new commits | Warning: merge/rebase needed |

**Sync check script**: `claude-plugin-evo/hooks/scripts/check-git-sync.sh`

### Migration

Existing projects without `team_mode` in config default to `auto`. No action required.

---

## Dialogue Protocol

Apply this loop to substantive work:

```
1. ELICIT    — Before generating, ensure you understand the request
               Ask clarifying questions if intent is ambiguous
               Probe for unstated assumptions and constraints

2. ANALYSE   — Examine relevant existing content
               Identify connections to other framework concepts
               Surface potential inconsistencies or gaps

3. SYNTHESISE — Integrate understanding into coherent output
                Connect new content to theoretical foundations
                Maintain consistency with existing framework elements

4. VALIDATE  — Present drafts explicitly as drafts
               Invite human review and correction
               Do not proceed to dependent work until validated

5. PRESERVE  — Capture rationale, not just decisions
               Document why, not just what
               Flag tacit knowledge that should be made explicit
```

---

## Tacit Knowledge Elicitation

Much knowledge exists in human minds but not in documents. Actively elicit:

**Questions to ask:**
- "What is the rationale behind this structure?"
- "How does this connect to [related concept]?"
- "Are there constraints or considerations I should know about?"
- "What alternatives were considered and why were they rejected?"
- "Is there historical context that informs this decision?"

**Capture requirements:**
- When humans provide rationale verbally, offer to capture it in appropriate documents
- Flag when decisions are made without documented rationale
- Suggest where tacit knowledge should be formalised

---

## Skill Preservation

AI assistance must support, not replace, human theory-building:

**Do:**
- Explain reasoning so humans can evaluate and learn
- Present options with trade-offs rather than single recommendations
- Ask questions that deepen human understanding
- Support humans in developing their own synthesis

**Don't:**
- Generate large volumes of content without human engagement
- Make decisions silently embedded in generated text
- Proceed through multiple steps without checkpoints
- Create dependency on AI for routine tasks

---

## Backward Event Detection

Monitor for signals that earlier work needs revisiting:

| Signal | Indicates | Response |
|--------|-----------|----------|
| New content contradicts existing concept | Conceptual inconsistency | Surface conflict; do not paper over |
| Definition has shifted from original | Concept drift | Flag for explicit decision |
| Evidence cited doesn't support claim | Evidential gap | Note the gap; suggest correction |
| Cross-reference target has changed | Broken dependencies | Identify all affected documents |
| New insight invalidates prior decision | Theory evolution | Surface for re-evaluation |

**Response protocol**: When detecting a backward event, stop forward progress and surface the issue. Do not resolve inconsistencies silently.

---

## Phase Transition Gates

Soft gates capture "proceed at risk" decisions, making information debt conscious and tracked.

### Gated Transitions (Balanced Approach)

| Transition | Gate Type | Assessment | Rationale |
|------------|-----------|------------|-----------|
| **1→2** (Initiation→Planning) | **Soft gate required** | `dialogue-assess-framing` + `dialogue-assess-phase` | 75% tacit; highest information debt risk |
| **2→3** (Planning→Requirements) | **Soft gate recommended** | `dialogue-assess-phase` | 55% tacit; scope decisions need validation |
| **3→4** (Requirements→Design) | **Soft gate recommended** | `dialogue-assess-phase` | 50% tacit; requirements clarity critical |
| **4→5** (Design→Implementation) | Optional | `dialogue-assess-phase` | Formal knowledge dominates |
| **5→6** (Implementation→Testing) | Not required | — | Tight feedback loop corrects issues |
| **6→7** (Testing→Operations) | Not required | — | Tight feedback loop corrects issues |

### Soft Gate Outcomes

| Outcome | Meaning | Action |
|---------|---------|--------|
| **PROCEED** | All dimensions ≥4.0, no blockers | Continue to next phase |
| **PROCEED_WITH_CAUTION** | Dimensions ≥3.0, manageable gaps | Continue with conditions recorded |
| **DEFER** | Significant gaps | Remediation before proceeding |

### PROCEED_WITH_CAUTION Pattern

When proceeding with conditions:
1. Record the decision with `dialogue-log-decision` (type: TACTICAL)
2. Document conditions in `approval_conditions` field
3. Create follow-up tasks for condition resolution
4. Conditions become input to next phase assessment

### Why Not Hard Gates?

Hard gates (blocking) are avoided because:
- Context determines appropriate rigour (solo vs enterprise)
- Human judgement required for trade-off decisions
- Information debt is sometimes acceptable (time-to-market)
- Soft gates make debt *visible* without blocking progress

---

## Common Pitfalls

1. **Overgeneralising actor suitability** — Determine at capability *instance* level, not broad categories
2. **Treating phase percentages as measured** — They are derived estimates for guidance
3. **Making absolute AI capability claims** — Always temporally qualify (as of 2024-2025)
4. **Optimising early phases for speed** — Understanding-heavy phases shouldn't prioritise velocity
5. **Conflating correlation with causation** — Most evidence is correlational (T3)
6. **Ignoring joint optimisation** — Human-AI systems require socio-technical design
7. **One capability per step** — If a step seems to require multiple capabilities, decompose it

---

## Phase-Specific Guidance: Phase 1 (Initiation)

### Information Composition

| Type | Percentage | Implication |
|------|------------|-------------|
| **Tacit** | 75% | Most knowledge exists in stakeholder minds; AI cannot lead |
| **Emergent** | 20% | Problem framing evolves through exploration |
| **Formal** | 5% | Very little is formally specifiable |

### Collaboration Pattern Constraints

- **AI cannot lead Phase 1 work** — The tacit knowledge required (strategic context, stakeholder dynamics, organisational politics) is not accessible to AI
- **Human-Only**: Strategic decisions, stakeholder politics, opportunity framing
- **Human-Led**: Market research synthesis, financial modelling, document drafting

### Functional Roles

Phase 1 high-value roles (per I-3 Naur-Wegner Integration):

| Role | Value in Phase 1 | Actor Suitability |
|------|------------------|-------------------|
| **Facilitator** | High | AI excels — structures dialogue without needing tacit knowledge |
| **Scribe** | High | AI excels — captures outputs as they occur (critical for capture windows) |
| **Synthesiser** | Medium | Human-led — integration requires tacit context |
| **Validator** | Medium | Human-led — validating tacit understanding requires tacit context |
| **Researcher** | Low | Limited value — most Phase 1 knowledge is internal, not external |

### Scaling: Minimal vs Full Phase 1

Phase 1 scales dramatically based on project context:

**Full Phase 1** (enterprise projects, significant investment, multiple stakeholders):
- All document types produced
- Formal governance gates
- Explicit stakeholder analysis and alignment

**Minimal Phase 1** (small projects, single stakeholder, low risk):
- Opportunity Statement may be implicit or verbal
- Stakeholder Analysis may be "obvious" (single requester)
- Business Case may be a paragraph, not a document

**Key insight**: A one-paragraph business case is still a business case. Process references trace lineage, not mandate ceremony.

### The Straw Man Pattern

In early-stage or exploratory work, Phase 1 documents often begin as placeholders:

| Document | Straw Man Version | Evolution |
|----------|-------------------|-----------|
| Stakeholder Analysis | "Stakeholders TBD—starting with requester" | Expanded as scope clarifies |
| Opportunity Statement | Initial problem framing (likely incomplete) | Reframed as understanding deepens |
| Business Case | Rough cost/benefit estimate | Refined with actual data |
| Feasibility | "Assumed feasible—will validate" | Updated with technical assessment |

**Straw man documents are valid** — they make assumptions explicit and trackable.

### Document Types

| Document | Required? | When to Create | Minimal Form |
|----------|-----------|----------------|--------------|
| **Opportunity Statement** | Always | Something triggered this work; capture it | Single sentence stating the problem |
| **Stakeholder Analysis** | Always | At minimum: who requested, who approves | List of names with roles |
| **Business Case** | Context-dependent | Formal in enterprises; may be verbal in startups | One paragraph with why and rough cost/benefit |
| **Project Charter** | Context-dependent | When authority must be explicit | Scope + authority statement |
| **Feasibility Assessment** | Context-dependent | When technical risk is non-trivial | Go/no-go with key risks |

### Capture Window Criticality

75% tacit composition means delayed documentation loses most value:

| Capture Requirement | Rationale |
|---------------------|-----------|
| **Real-time note-taking** during interviews/sessions | Tacit context lost immediately |
| **Same-day synthesis** of exploration activities | Reasoning chains decay rapidly |
| **Immediate documentation** of "aha moments" | Problem framing insights are highly perishable |

**Critical**: If an insight occurs and isn't captured immediately, it may be lost. Use Scribe role actively.

### Rationale-First Validation

Phase 1 validation emphasises *why* over *what*:

- ✗ Positions without rationale are **incomplete**
- ✗ Decisions without alternatives considered are **incomplete**
- ✗ Conclusions without reasoning chains are **incomplete**

**Validation checklist for Phase 1 outputs:**
```
□ Problem framing distinguishes problem from solution
□ Alternatives considered are documented
□ Rejection rationale is captured (negative knowledge)
□ Stakeholder positions include their reasoning
□ Assumptions are explicit, not embedded
```

### AI Configuration for Phase 1

When operating in Phase 1:

1. **Activate Facilitator role**: Structure dialogue to help humans articulate tacit knowledge
2. **Activate Scribe role**: Capture decisions and observations in real-time using skills:
   - `dialogue-log-decision` for choices made
   - `dialogue-log-observation` for findings
3. **Use `dialogue-structured-elicit`**: For systematic context gathering
4. **Do not lead**: Present options with trade-offs; let humans decide
5. **Probe for rationale**: When humans state conclusions, ask "why?" and "what alternatives did you consider?"

---

*AI-Augmented SDLC Framework v1.3 — Usage Manual*
