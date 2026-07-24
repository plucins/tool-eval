# Schema: Process Instance

**Document Type**: SPC (Specification)
**Temporal Class**: Standing
**Scope**: Organisational
**Status**: ACTIVE
**Version**: 1.0

---

## Purpose

This schema defines the YAML structure for **ProcessInstances** — runtime execution intent records. ProcessInstances capture what process will be (or has been) executed, linking template definitions to actual execution logs.

**Key distinction**:
- **ProcessDefinition** = reusable template (what *could* happen)
- **ProcessInstance** = execution intent (what *will* happen)
- **ExecutionLog** = execution record (what *did* happen)

**Related documents**:
- [Process Definition Schema](./schema_process-definition.md) — Reusable templates
- [Execution Log Schema](./schema_execution-log.md) — Execution audit trail
- [Framework Manual](./framework-manual.md) — Process specification reference

---

## Design Rationale

ProcessInstances serve as the **execution intent** layer:

1. **Plan before execution** — Instance created before executor starts
2. **Dynamic or well-known** — Can reference a template or define inline
3. **Plain English mandatory** — Users see descriptions, never IDs (per DEC-20260115-173448)
4. **Audit linkage** — Links to ExecutionLog for traceability

---

## Schema Definition

### File Structure

ProcessInstance files use the naming convention `PINST-YYYYMMDD-HHMMSS.yaml` and are stored in `.dialogue/processes/`.

```yaml
---
# ProcessInstance Schema v1.0

instance:
  id: string                    # PINST-YYYYMMDD-HHMMSS format
  created: string               # ISO 8601 timestamp
  created_by: string            # Actor reference (ai:claude, human:pid)

  # MANDATORY: Plain English description for users
  plain_english_description: string

  # What process to execute
  definition_source:
    type: enum                  # WELL_KNOWN | DYNAMIC
    # For WELL_KNOWN:
    definition_id: string       # Optional: PROC-P.S reference
    definition_path: string     # Path to definition file
    # For DYNAMIC:
    inline_definition: object   # Full ProcessDefinition embedded

  # Execution context
  context:
    trigger: string             # What initiated this instance
    inputs: object              # Key-value pairs for input data
    parameters: object          # Runtime parameters
    test_mode: boolean          # Optional: dry-run without side effects (default: false)

  # Execution state
  status: enum                  # PLANNED | IN_PROGRESS | SUSPENDED | COMPLETED | FAILED
  execution_log_id: string      # EXEC-* reference (set when execution starts)

  # Definition approval (for criteria evaluation)
  approval:
    definition_approved: boolean  # Has human approved this definition?
    approved_by: string           # Actor who approved (human:pid)
    approved_at: string           # ISO 8601 timestamp
    trust_level: enum             # REVIEW_EACH | TRUST_APPROVED
    approval_decision_id: string  # DEC-* reference for approval decision

  # Execution history
  run_count: integer              # Number of times this definition has been executed

  # Timestamps
  started: string               # ISO 8601 (set when status → IN_PROGRESS)
  completed: string             # ISO 8601 (set when status → COMPLETED|FAILED)

  # Outcome
  outcome:
    execution_success: boolean  # Did process run without errors?
    process_result: string      # Process-specific result (e.g., "PASS", "FAIL", "APPROVED")
    summary: string             # Plain English outcome summary
    outputs: object             # Key-value pairs for output data
---
```

---

## Enumeration Values

### Definition Source Type

| Value | Description | Required Fields |
|-------|-------------|-----------------|
| `WELL_KNOWN` | References a pre-defined process | `definition_path` (and optionally `definition_id`) |
| `DYNAMIC` | Process defined inline | `inline_definition` containing full definition |

### Instance Status

| Value | Description | Valid Transitions |
|-------|-------------|-------------------|
| `PLANNED` | Instance created, not yet started | → IN_PROGRESS, CANCELLED |
| `IN_PROGRESS` | Currently executing | → SUSPENDED, COMPLETED, FAILED |
| `SUSPENDED` | Paused (DEFER triggered) | → IN_PROGRESS, CANCELLED |
| `COMPLETED` | Successfully finished | (terminal) |
| `FAILED` | Execution failed | (terminal) |
| `CANCELLED` | Aborted before completion | (terminal) |

### Trust Level

| Value | Description | Behaviour |
|-------|-------------|-----------|
| `REVIEW_EACH` | Review criteria on every run | Human approves entry/exit criteria each execution |
| `TRUST_APPROVED` | Trust previous approval | Skip criteria review; AI evaluates with escalation on uncertainty |

### Test Mode

When `context.test_mode: true`:

| Aspect | Behaviour |
|--------|-----------|
| **Validation** | Full validation runs (V1-V8) |
| **Entry Criteria** | Evaluated but not enforced |
| **Step Execution** | Steps run but side effects skipped |
| **Logging** | DEC-*/OBS-* entries marked as test |
| **External Actions** | No external API calls, file writes, etc. |
| **Outcome** | `execution_success: true` if flow completes, `process_result: "TEST"` |

Use test mode to:
- Validate process definitions before deployment
- Verify input/output mappings
- Check escalation trigger conditions
- Dry-run without affecting production state

---

## ID Convention

ProcessInstance IDs use timestamp-based format:

```
PINST-YYYYMMDD-HHMMSS
```

Example: `PINST-20260118-143052`

This ensures:
- Unique identification
- Chronological ordering
- No collision risk

---

## Examples

### Well-Known Process Instance

```yaml
# .dialogue/processes/PINST-20260118-143052.yaml
---
instance:
  id: "PINST-20260118-143052"
  created: "2026-01-18T14:30:52Z"
  created_by: "ai:claude"

  plain_english_description: >
    Review the pull request for the authentication refactor,
    checking for security issues and code quality.

  definition_source:
    type: WELL_KNOWN
    definition_id: "PROC-5.1"
    definition_path: "claude-plugin-evo/processes/process-code-review.yaml"

  context:
    trigger: "User requested PR review"
    inputs:
      pr_url: "https://github.com/org/repo/pull/123"
      branch: "feature/auth-refactor"
    parameters:
      focus_areas:
        - security
        - performance

  status: PLANNED
  execution_log_id: null

  approval:
    definition_approved: false
    approved_by: null
    approved_at: null
    trust_level: null
    approval_decision_id: null

  run_count: 0

  started: null
  completed: null

  outcome: null
---
```

### Dynamic Process Instance

```yaml
# .dialogue/processes/PINST-20260118-150000.yaml
---
instance:
  id: "PINST-20260118-150000"
  created: "2026-01-18T15:00:00Z"
  created_by: "ai:claude"

  plain_english_description: >
    Analyse the error logs from the last 24 hours and
    generate a summary report of recurring issues.

  definition_source:
    type: DYNAMIC
    inline_definition:
      definition:
        id: "PROC-DYNAMIC"
        name: "Ad-hoc Log Analysis"
        description: "Analyse and summarise error logs"
        version: "1.0.0"
        phase: 7
        information_composition:
          formal: 60
          tacit: 30
          emergent: 10

      steps:
        - id: "D.1"
          name: "Gather Logs"
          capability: Elicit
          pattern: AI-Only
          human_role: "Defines log sources and timeframe; audits completeness"
          ai_role: "Retrieve error logs from specified timeframe"
          escalation_triggers:
            - condition: "Log retrieval fails"
              action: BLOCK
              severity: HIGH
              target: null
              context: "Manual log access required"
          completion_criteria: "Logs retrieved"
          validation: "Log data available"

        - id: "D.2"
          name: "Analyse Patterns"
          capability: Analyse
          pattern: AI-Led
          human_role: "Validate pattern significance"
          ai_role: "Identify recurring errors and patterns"
          escalation_triggers:
            - condition: "Critical security pattern detected"
              action: ESCALATE
              severity: HIGH
              target: human
              context: "Security patterns require human review"
          completion_criteria: "Patterns identified"
          validation: "All errors categorised"

        - id: "D.3"
          name: "Generate Report"
          capability: Generate
          pattern: AI-Only
          human_role: "Defines report format and recipients; reviews output"
          ai_role: "Create summary report"
          escalation_triggers: []
          completion_criteria: "Report generated"
          validation: "Report complete"

  context:
    trigger: "Scheduled daily analysis"
    inputs:
      timeframe: "24h"
      log_source: "/var/log/application"
    parameters: {}

  status: PLANNED
  execution_log_id: null

  approval:
    definition_approved: false
    approved_by: null
    approved_at: null
    trust_level: null
    approval_decision_id: null

  run_count: 0

  started: null
  completed: null

  outcome: null
---
```

### Completed Instance

```yaml
# .dialogue/processes/PINST-20260118-143052.yaml (after execution)
---
instance:
  id: "PINST-20260118-143052"
  created: "2026-01-18T14:30:52Z"
  created_by: "ai:claude"

  plain_english_description: >
    Review the pull request for the authentication refactor,
    checking for security issues and code quality.

  definition_source:
    type: WELL_KNOWN
    definition_id: "PROC-5.1"
    definition_path: "claude-plugin-evo/processes/process-code-review.yaml"

  context:
    trigger: "User requested PR review"
    inputs:
      pr_url: "https://github.com/org/repo/pull/123"
      branch: "feature/auth-refactor"
    parameters:
      focus_areas:
        - security
        - performance

  status: COMPLETED
  execution_log_id: "EXEC-20260118-143055"

  approval:
    definition_approved: true
    approved_by: "human:pid"
    approved_at: "2026-01-18T14:31:00Z"
    trust_level: TRUST_APPROVED
    approval_decision_id: "DEC-20260118-143100"

  run_count: 1

  started: "2026-01-18T14:30:55Z"
  completed: "2026-01-18T14:45:12Z"

  outcome:
    execution_success: true
    process_result: "APPROVED"
    summary: >
      Code review completed. Found 2 minor issues (addressed in comments)
      and no security concerns. Approved with suggestions.
    outputs:
      review_status: "approved"
      issues_found: 2
      blocking_issues: 0
---
```

---

## Validation Rules

### Required Field Validation

1. `instance.id` must match pattern `PINST-[0-9]{8}-[0-9]{6}`
2. `instance.plain_english_description` must be non-empty (MANDATORY)
3. `instance.definition_source.type` must be WELL_KNOWN or DYNAMIC
4. If WELL_KNOWN: `definition_path` must be provided
5. If DYNAMIC: `inline_definition` must contain valid ProcessDefinition
6. `instance.status` must be valid enum value

### Consistency Validation

1. `execution_log_id` should be set when status transitions to IN_PROGRESS
2. `started` should be set when status transitions to IN_PROGRESS
3. `completed` should be set when status transitions to COMPLETED or FAILED
4. `outcome` should be set when status is COMPLETED or FAILED

### Outcome Field Semantics

The outcome object distinguishes between **process execution** and **process result**:

| Field | Meaning | Example |
|-------|---------|---------|
| `execution_success` | Did the process run without errors? | `true` (all steps completed) |
| `process_result` | What was the outcome of the work? | `"FAIL"` (validation found issues) |

**Key distinction**: A validation process can execute successfully (`execution_success: true`) while reporting that the artifact failed validation (`process_result: "FAIL"`).

**Common process_result values by process type:**

| Process Type | Possible Results |
|--------------|-----------------|
| Validation | `PASS`, `FAIL`, `PARTIAL` |
| Review | `APPROVED`, `REJECTED`, `CHANGES_REQUESTED` |
| Analysis | `COMPLETE`, `INCOMPLETE`, `BLOCKED` |
| Generation | `GENERATED`, `FAILED` |

---

## Operations

### Creating an Instance

The orchestrator creates instances by:
1. Generating timestamp-based ID
2. Setting `plain_english_description` (MANDATORY)
3. Specifying definition source (WELL_KNOWN or DYNAMIC)
4. Setting status to PLANNED
5. Writing to `.dialogue/processes/`

### Invoking Execution

The orchestrator invokes the process-executor agent via Task tool:
```
Execute process. Instance: .dialogue/processes/PINST-20260118-143052.yaml
```

### Updating During Execution

The process-executor updates the instance:
1. Sets `execution_log_id` to new ExecutionLog ID
2. Sets `started` timestamp
3. Updates `status` to IN_PROGRESS
4. On completion: sets `completed`, `status`, and `outcome`

---

## Traceability Chain

```
User Request
    ↓
PINST-* (intent: what will happen)
    ↓
EXEC-* (actuality: what did happen)
    ↓
DEC-*/OBS-* (audit: decisions and observations)
```

Users interact with plain English descriptions. Internal components use IDs for programmatic reference.

---

*This schema enables execution intent capture while maintaining plain English UX and audit traceability.*
