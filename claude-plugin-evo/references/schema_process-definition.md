# Schema: Process Definition

**Document Type**: SPC (Specification)
**Temporal Class**: Standing
**Scope**: Organisational
**Status**: ACTIVE
**Version**: 1.0

---

## Purpose

This schema defines the YAML structure for **ProcessDefinitions** — reusable templates that describe capability flows. ProcessDefinitions are well-known process specifications stored in `claude-plugin-evo/processes/` and referenced by ProcessInstances during execution.

**Related documents**:
- [Process Instance Schema](./schema_process-instance.md) — Runtime execution intent
- [Execution Log Schema](./schema_execution-log.md) — Execution audit trail
- [Framework Manual](./framework-manual.md) — Eight capabilities, five collaboration patterns
- [Framework Manual](./framework-manual.md) — Process specification reference

---

## Design Rationale

ProcessDefinitions capture reusable process templates at capability-instance granularity:

1. **Reusability** — Well-known processes can be executed multiple times
2. **Versioning** — Definitions can evolve while preserving execution history
3. **Separation** — Template vs. instance enables both static analysis and runtime flexibility
4. **Plain English UX** — Users interact via descriptions, never process IDs (per DEC-20260115-173448)

---

## Schema Definition

### File Structure

ProcessDefinition files use the naming convention `process-<name>.yaml` and are stored in `claude-plugin-evo/processes/`.

```yaml
---
# ProcessDefinition Schema v1.0

definition:
  id: string                    # PROC-P.S format (e.g., PROC-3.1)
  name: string                  # Human-readable name
  description: string           # Plain English description for users
  version: string               # Semantic version (e.g., "1.0.0")
  phase: integer                # SDLC phase (1-7)
  information_composition:      # Approximate percentages
    formal: integer             # 0-100
    tacit: integer              # 0-100
    emergent: integer           # 0-100

interfaces:
  inputs:                       # Input document types
    - type: string              # Document type ID
      required: boolean         # Whether mandatory
      description: string       # What this input provides
  outputs:                      # Output document types
    - type: string              # Document type ID
      description: string       # What this output captures

steps:                          # Ordered capability instances
  - <CapabilityInstance>

control_flow:
  retry_policy:
    on_validation_failure:
      return_to: string         # Step ID to return to
      max_iterations: integer   # Maximum retry count (default: 3)
  fix_steps:                    # Optional fix step definitions
    - <FixStep>

quality:
  entry_criteria:               # Conditions to start process
    - string
  exit_criteria:                # Conditions to complete process
    - string
  sla:                          # Optional: Service level expectations
    expected_duration_minutes: integer   # Typical completion time
    timeout_minutes: integer             # Maximum allowed duration
    warning_threshold_percent: integer   # Warn when % of timeout reached (default: 80)

flow: |                           # Required: Mermaid diagram of process flow
  ```mermaid
  flowchart TD
    ...
  ```
---
```

### Flow Diagram

Every ProcessDefinition **must** include a `flow` field containing a Mermaid flowchart diagram. This diagram:
- Provides visual comprehension of the process structure
- Shows step sequence, decision points, and control flow
- Enables comparison between intended and actual execution
- Helps AI agents understand the process at a glance

**Requirements**:
- Must be valid Mermaid flowchart syntax
- Must include all step IDs as nodes
- Must show RETURN loops and fix steps if present
- Should indicate escalation decision points

### CapabilityInstance Schema

Each step in the capability flow:

```yaml
step:
  id: string                    # P.S.N format (e.g., 3.1.1)
  name: string                  # Step name
  capability: enum              # One of eight capabilities
  pattern: enum                 # One of five collaboration patterns
  human_role: string            # Specific activities or "None"
  ai_role: string               # Specific activities or "None"
  escalation_triggers:          # Conditions for escalation
    - condition: string         # What triggers escalation
      action: enum              # ESCALATE | RETURN | BLOCK | DEFER
      severity: enum            # LOW | MEDIUM | HIGH (required)
      target: string            # Role, step ID, or queue
      context: string           # Information to pass
  completion_criteria: string   # How to know step is complete
  validation: string            # What to verify before proceeding
```

### FixStep Schema

Optional corrective steps triggered by RETURN:

```yaml
fix_step:
  id: string                    # Parent step ID + "a" suffix (e.g., 3.1.8a)
  name: string                  # "Fix <Issue>"
  trigger_from: string          # Step ID that triggers this fix
  invocation: enum              # ALWAYS | ON_RETRY | ASK (default: ON_RETRY)
  capability: enum              # Typically Transform
  pattern: enum                 # Typically AI-Led or Partnership
  human_role: string            # Review proposed corrections
  ai_role: string               # Analyse failure; propose corrections
```

---

## Enumeration Values

### Capability

| Value | Description |
|-------|-------------|
| `Elicit` | Extract information from sources |
| `Analyse` | Decompose, classify, identify patterns |
| `Synthesise` | Combine into coherent understanding |
| `Transform` | Convert between representations |
| `Validate` | Confirm correctness and fitness |
| `Decide` | Select among alternatives |
| `Generate` | Produce artifacts |
| `Preserve` | Capture for future retrieval |

### Pattern

| Value | Human Role | AI Role |
|-------|------------|---------|
| `Human-Only` | All activities | Absent or passive observer |
| `Human-Led` | Drives, decides | Supports, prepares |
| `Partnership` | Unique judgement | Unique capability |
| `AI-Led` | Reviews, validates | Drives execution |
| `AI-Only` | Governs, audits | Autonomous within bounds |

### Escalation Action

| Value | Target | Use When |
|-------|--------|----------|
| `ESCALATE` | Role (human, governance) | Decision exceeds AI competence |
| `RETURN` | Step ID | Validation failed; correction needed |
| `BLOCK` | None | Critical failure; halt process |
| `DEFER` | Work queue | Requires extended offline review |

### Severity

| Value | 1st Occurrence | 2nd+ Occurrence | Use When |
|-------|----------------|-----------------|----------|
| `LOW` | Direct action | Fix step (if exists) | Minor issues; retry likely to succeed |
| `MEDIUM` | Direct action | Fix step + human confirmation | Moderate issues; may need intervention |
| `HIGH` | **Escalate first**, then action | BLOCK if still failing | Serious issues; human must review |

**Note**: Severity is **required** on all escalation triggers. Assignment must be logged as a DEC-* entry with rationale.

### Fix Step Invocation

| Value | Behaviour | Use When |
|-------|-----------|----------|
| `ON_RETRY` | Fix step runs on 2nd+ iteration only | Default; retry first, fix if retry fails |
| `ALWAYS` | Fix step intercepts every RETURN | Structured correction always needed |
| `ASK` | Escalate to human to choose path | Uncertain whether fix is needed |

**Note**: When combined with severity:
- HIGH severity + any invocation = Escalate first, then apply invocation logic
- MEDIUM severity + ON_RETRY = Fix step gets human confirmation on 2nd+ iteration
- LOW severity + ON_RETRY = Fix step runs automatically on 2nd+ iteration

---

## ID Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Process | `PROC-[Phase].[Sequence]` | PROC-3.1 |
| Step | `[Phase].[ProcessSeq].[StepSeq]` | 3.1.4 |
| Fix Step | `[Step]a` | 3.1.8a |

---

## Constraints

### Pattern-Role Consistency (C1-C4)

These constraints are **mandatory**. Definitions violating them are invalid.

| ID | Rule |
|----|------|
| **C1** | Human-Only → ai_role is "None" or describes passive/ambient support (not active participation) |
| **C2** | AI-Only → human_role describes governance (defines rules, audits, oversees) — never "None" |
| **C3** | Active ai_role (analysis, generation, execution) → pattern ≠ Human-Only |
| **C4** | human_role = "None" → pattern ≠ AI-Only |

### Additional Constraints

1. Each step uses exactly **one** capability
2. Steps with AI participation **must** have escalation triggers defined
3. Completion criteria must be **testable**
4. `information_composition` percentages must sum to 100

---

## Complete Example

```yaml
# claude-plugin-evo/processes/process-code-review.yaml
---
definition:
  id: PROC-5.1
  name: "Code Review Process"
  description: "Review code changes for quality, correctness, and standards compliance"
  version: "1.0.0"
  phase: 5
  information_composition:
    formal: 55
    tacit: 35
    emergent: 10

interfaces:
  inputs:
    - type: "pull_request"
      required: true
      description: "Code changes to review"
    - type: "coding_standards"
      required: false
      description: "Project coding standards document"
  outputs:
    - type: "review_feedback"
      description: "Review comments and approval status"

steps:
  - id: "5.1.1"
    name: "Gather Context"
    capability: Elicit
    pattern: AI-Only
    human_role: "Defines retrieval scope; audits completeness"
    ai_role: "Retrieve PR metadata, diff, and related issues"
    escalation_triggers:
      - condition: "PR too large (>500 lines)"
        action: ESCALATE
        severity: MEDIUM
        target: human
        context: "Large PR may need manual chunking"
    completion_criteria: "All PR context retrieved"
    validation: "Diff and metadata available"

  - id: "5.1.2"
    name: "Analyse Changes"
    capability: Analyse
    pattern: AI-Led
    human_role: "Review AI analysis for accuracy"
    ai_role: "Identify patterns, potential issues, standards violations"
    escalation_triggers:
      - condition: "Security-sensitive changes detected"
        action: ESCALATE
        severity: HIGH
        target: human
        context: "Security changes require human review"
      - condition: "Architectural changes detected"
        action: ESCALATE
        severity: HIGH
        target: human
        context: "Architecture decisions require human judgement"
    completion_criteria: "Analysis complete with categorised findings"
    validation: "All changes categorised; no uncategorised hunks"

  - id: "5.1.3"
    name: "Generate Review"
    capability: Generate
    pattern: AI-Led
    human_role: "Edit and approve review comments"
    ai_role: "Draft review comments with rationale"
    escalation_triggers:
      - condition: "Blocking issue requires human judgement"
        action: ESCALATE
        severity: MEDIUM
        target: human
        context: "Human must decide on blocking issues"
    completion_criteria: "Review comments drafted"
    validation: "All findings have corresponding comments"

  - id: "5.1.4"
    name: "Record Review"
    capability: Preserve
    pattern: AI-Only
    human_role: "Defines retention policies; audits submission"
    ai_role: "Submit review to PR system"
    escalation_triggers:
      - condition: "Submission fails"
        action: BLOCK
        severity: HIGH
        target: null
        context: "Manual submission required"
    completion_criteria: "Review submitted to system"
    validation: "Review visible on PR"

control_flow:
  retry_policy:
    on_validation_failure:
      return_to: "5.1.2"
      max_iterations: 2

quality:
  entry_criteria:
    - "PR exists and is open"
    - "Diff is retrievable"
  exit_criteria:
    - "Review submitted"
    - "All findings addressed in comments"

flow: |
  ```mermaid
  flowchart TD
    subgraph Steps
      S1["5.1.1 Gather Context<br/>(Elicit, AI-Only)"]
      S2["5.1.2 Analyse Changes<br/>(Analyse, AI-Led)"]
      S3["5.1.3 Generate Review<br/>(Generate, AI-Led)"]
      S4["5.1.4 Record Review<br/>(Preserve, AI-Only)"]
    end

    S1 --> S2
    S2 --> S3
    S3 --> S4

    S1 -->|"PR too large"| ESC1[Escalate to human]
    S2 -->|"Security/Architecture"| ESC2[Escalate to human]
    S3 -->|"Blocking issue"| ESC3[Escalate to human]
    S4 -->|"Submission fails"| BLOCK[BLOCK]

    S2 -->|"Validation fails"| S2

    note1["Retry: return to 5.1.2<br/>max 2 iterations"]
  ```
---
```

---

## Validation Rules

### Required Field Validation

1. `definition.id` must match pattern `PROC-[1-7]\.[0-9]+`
2. `definition.phase` must be 1-7
3. `definition.name` and `definition.description` must be non-empty
4. `information_composition` values must sum to 100
5. Each step must have all required fields
6. Each escalation trigger must have `severity` specified (no default)
7. `flow` field must contain a valid Mermaid flowchart diagram

### Consistency Validation

1. Step IDs must be sequential within the process
2. Pattern-role constraints (C1-C4) must be satisfied
3. Escalation `return_to` targets must reference valid step IDs
4. Fix step IDs must follow `[parent]a` pattern

---

## Operations

### Loading a Definition

The process-executor agent loads definitions by:
1. Reading the YAML file from `claude-plugin-evo/processes/`
2. Validating against this schema
3. Returning error if validation fails

### Referencing from ProcessInstance

ProcessInstances reference definitions via:
```yaml
definition_source:
  type: WELL_KNOWN
  definition_id: "PROC-3.1"
  definition_path: "claude-plugin-evo/processes/process-requirements-elicitation.yaml"
```

---

*This schema enables reusable process templates while maintaining separation from runtime execution state.*
