# Schema: Execution Log

**Document Type**: SPC (Specification)
**Temporal Class**: Standing
**Scope**: Organisational
**Status**: ACTIVE
**Version**: 1.0

---

## Purpose

This schema defines the YAML structure for **ExecutionLogs** — runtime execution records that capture what actually happened during process execution. ExecutionLogs link execution actuality to the DEC-*/OBS-* audit trail.

**Key distinction**:
- **ProcessDefinition** = reusable template (what *could* happen)
- **ProcessInstance** = execution intent (what *will* happen)
- **ExecutionLog** = execution record (what *did* happen)

**Related documents**:
- [Process Definition Schema](./schema_process-definition.md) — Reusable templates
- [Process Instance Schema](./schema_process-instance.md) — Execution intent
- [Framework Manual](./framework-manual.md) — Decision and observation logging

---

## Design Rationale

ExecutionLogs capture the complete execution trace:

1. **Audit trail** — Links step executions to DEC-*/OBS-* entries
2. **Traceability** — Each step records what decisions and observations occurred
3. **Debugging** — Captures errors, escalations, and control flow changes
4. **Metrics** — Enables execution analysis and process improvement

---

## Schema Definition

### File Structure

ExecutionLog files use the naming convention `EXEC-YYYYMMDD-HHMMSS.yaml` and are stored in `.dialogue/logs/executions/`.

```yaml
---
# ExecutionLog Schema v1.0

execution:
  id: string                    # EXEC-YYYYMMDD-HHMMSS format
  instance_id: string           # PINST-* reference
  started: string               # ISO 8601 timestamp
  completed: string             # ISO 8601 timestamp (when finished)
  status: enum                  # IN_PROGRESS | COMPLETED | FAILED | BLOCKED

  # Executor information
  executor:
    agent: string               # Agent that executed (e.g., "process-executor")
    session_id: string          # Optional: session identifier

step_executions:                # Ordered list of step execution records
  - <StepExecution>

# Aggregate audit linkage
audit_summary:
  total_decisions: integer      # Count of DEC-* entries
  total_observations: integer   # Count of OBS-* entries
  decision_ids: [string]        # All DEC-* IDs from this execution
  observation_ids: [string]     # All OBS-* IDs from this execution

# Control flow tracking
control_flow_events:            # Optional: flow changes during execution
  - <ControlFlowEvent>

# Error tracking
errors: [string]                # Error messages if any
---
```

### StepExecution Schema

Record of each step's execution:

```yaml
step_execution:
  step_id: string               # Step ID from definition
  step_name: string             # Step name for readability
  capability: string            # Capability used
  pattern: string               # Pattern applied

  # Timing
  started: string               # ISO 8601 timestamp
  completed: string             # ISO 8601 timestamp
  duration_ms: integer          # Milliseconds

  # Outcome
  status: enum                  # COMPLETED | FAILED | ESCALATED | SKIPPED
  outcome_summary: string       # Brief description of what happened

  # Audit linkage (critical for traceability)
  decisions: [string]           # DEC-* IDs logged during this step
  observations: [string]        # OBS-* IDs logged during this step

  # Escalation details (if status = ESCALATED)
  escalation:
    trigger: string             # What condition triggered escalation
    action: string              # ESCALATE | RETURN | BLOCK | DEFER
    target: string              # Where escalated to
    context: string             # Context passed

  # Iteration tracking (for retry loops)
  iteration: integer            # Which iteration (1 = first attempt)

  # Error details (if status = FAILED)
  error:
    message: string
    recoverable: boolean
```

### ControlFlowEvent Schema

Records when control flow deviates from linear:

```yaml
control_flow_event:
  timestamp: string             # ISO 8601
  type: enum                    # RETURN | BLOCK | DEFER | RESUME
  from_step: string             # Step where event occurred
  to_step: string               # Step to proceed to (if applicable)
  reason: string                # Why flow changed
  iteration: integer            # Which iteration triggered this
```

---

## Enumeration Values

### Execution Status

| Value | Description |
|-------|-------------|
| `IN_PROGRESS` | Currently executing |
| `COMPLETED` | All steps finished successfully |
| `FAILED` | Execution failed (unrecoverable) |
| `BLOCKED` | Halted; requires manual intervention |

### Step Execution Status

| Value | Description |
|-------|-------------|
| `COMPLETED` | Step finished successfully |
| `FAILED` | Step failed |
| `ESCALATED` | Step escalated to human/governance |
| `SKIPPED` | Step skipped (e.g., fix step not triggered) |

### Control Flow Event Type

| Value | Description |
|-------|-------------|
| `RETURN` | Looped back to earlier step |
| `BLOCK` | Process halted |
| `DEFER` | Process suspended for async |
| `RESUME` | Process resumed from suspension |

---

## ID Convention

ExecutionLog IDs use timestamp-based format:

```
EXEC-YYYYMMDD-HHMMSS
```

Example: `EXEC-20260118-143055`

---

## Complete Example

```yaml
# .dialogue/logs/executions/EXEC-20260118-143055.yaml
---
execution:
  id: "EXEC-20260118-143055"
  instance_id: "PINST-20260118-143052"
  started: "2026-01-18T14:30:55Z"
  completed: "2026-01-18T14:45:12Z"
  status: COMPLETED

  executor:
    agent: "process-executor"
    session_id: "sess-abc123"

step_executions:
  - step_id: "5.1.1"
    step_name: "Gather Context"
    capability: "Elicit"
    pattern: "AI-Only"
    started: "2026-01-18T14:30:55Z"
    completed: "2026-01-18T14:31:20Z"
    duration_ms: 25000
    status: COMPLETED
    outcome_summary: "Retrieved PR #123 metadata and diff (342 lines)"
    decisions: []
    observations:
      - "OBS-20260118-143100"
    iteration: 1

  - step_id: "5.1.2"
    step_name: "Analyse Changes"
    capability: "Analyse"
    pattern: "AI-Led"
    started: "2026-01-18T14:31:20Z"
    completed: "2026-01-18T14:38:45Z"
    duration_ms: 445000
    status: COMPLETED
    outcome_summary: "Identified 2 code quality issues, no security concerns"
    decisions:
      - "DEC-20260118-143500"
    observations:
      - "OBS-20260118-143200"
      - "OBS-20260118-143400"
    iteration: 1

  - step_id: "5.1.3"
    step_name: "Generate Review"
    capability: "Generate"
    pattern: "AI-Led"
    started: "2026-01-18T14:38:45Z"
    completed: "2026-01-18T14:43:30Z"
    duration_ms: 285000
    status: COMPLETED
    outcome_summary: "Generated 2 review comments with suggestions"
    decisions: []
    observations:
      - "OBS-20260118-143900"
    iteration: 1

  - step_id: "5.1.4"
    step_name: "Record Review"
    capability: "Preserve"
    pattern: "AI-Only"
    started: "2026-01-18T14:43:30Z"
    completed: "2026-01-18T14:45:12Z"
    duration_ms: 102000
    status: COMPLETED
    outcome_summary: "Review submitted to GitHub PR"
    decisions: []
    observations:
      - "OBS-20260118-144500"
    iteration: 1

audit_summary:
  total_decisions: 1
  total_observations: 5
  decision_ids:
    - "DEC-20260118-143500"
  observation_ids:
    - "OBS-20260118-143100"
    - "OBS-20260118-143200"
    - "OBS-20260118-143400"
    - "OBS-20260118-143900"
    - "OBS-20260118-144500"

control_flow_events: []

errors: []
---
```

### Example with Retry Loop

```yaml
# .dialogue/logs/executions/EXEC-20260118-160000.yaml
---
execution:
  id: "EXEC-20260118-160000"
  instance_id: "PINST-20260118-155955"
  started: "2026-01-18T16:00:00Z"
  completed: "2026-01-18T16:20:30Z"
  status: COMPLETED

  executor:
    agent: "process-executor"

step_executions:
  - step_id: "3.1.1"
    step_name: "Gather Requirements"
    capability: "Elicit"
    pattern: "Human-Led"
    started: "2026-01-18T16:00:00Z"
    completed: "2026-01-18T16:05:00Z"
    duration_ms: 300000
    status: COMPLETED
    outcome_summary: "Initial requirements gathered from stakeholder"
    decisions: []
    observations:
      - "OBS-20260118-160200"
    iteration: 1

  - step_id: "3.1.2"
    step_name: "Analyse Requirements"
    capability: "Analyse"
    pattern: "Partnership"
    started: "2026-01-18T16:05:00Z"
    completed: "2026-01-18T16:10:00Z"
    duration_ms: 300000
    status: COMPLETED
    outcome_summary: "Requirements analysed; gaps identified"
    decisions:
      - "DEC-20260118-160700"
    observations:
      - "OBS-20260118-160600"
    iteration: 1

  - step_id: "3.1.3"
    step_name: "Validate Completeness"
    capability: "Validate"
    pattern: "AI-Led"
    started: "2026-01-18T16:10:00Z"
    completed: "2026-01-18T16:11:00Z"
    duration_ms: 60000
    status: ESCALATED
    outcome_summary: "Validation failed - missing acceptance criteria"
    decisions:
      - "DEC-20260118-161000"
    observations:
      - "OBS-20260118-161000"
    escalation:
      trigger: "Missing required fields"
      action: "RETURN"
      target: "3.1.1"
      context: "Need acceptance criteria for features F1, F2"
    iteration: 1

  # Second iteration after RETURN
  - step_id: "3.1.1"
    step_name: "Gather Requirements"
    capability: "Elicit"
    pattern: "Human-Led"
    started: "2026-01-18T16:11:30Z"
    completed: "2026-01-18T16:15:00Z"
    duration_ms: 210000
    status: COMPLETED
    outcome_summary: "Additional requirements gathered - acceptance criteria added"
    decisions: []
    observations:
      - "OBS-20260118-161300"
    iteration: 2

  - step_id: "3.1.2"
    step_name: "Analyse Requirements"
    capability: "Analyse"
    pattern: "Partnership"
    started: "2026-01-18T16:15:00Z"
    completed: "2026-01-18T16:18:00Z"
    duration_ms: 180000
    status: COMPLETED
    outcome_summary: "Requirements complete"
    decisions: []
    observations:
      - "OBS-20260118-161600"
    iteration: 2

  - step_id: "3.1.3"
    step_name: "Validate Completeness"
    capability: "Validate"
    pattern: "AI-Led"
    started: "2026-01-18T16:18:00Z"
    completed: "2026-01-18T16:20:30Z"
    duration_ms: 150000
    status: COMPLETED
    outcome_summary: "All requirements validated"
    decisions: []
    observations:
      - "OBS-20260118-162000"
    iteration: 2

audit_summary:
  total_decisions: 2
  total_observations: 7
  decision_ids:
    - "DEC-20260118-160700"
    - "DEC-20260118-161000"
  observation_ids:
    - "OBS-20260118-160200"
    - "OBS-20260118-160600"
    - "OBS-20260118-161000"
    - "OBS-20260118-161300"
    - "OBS-20260118-161600"
    - "OBS-20260118-162000"

control_flow_events:
  - timestamp: "2026-01-18T16:11:00Z"
    type: RETURN
    from_step: "3.1.3"
    to_step: "3.1.1"
    reason: "Missing acceptance criteria"
    iteration: 1

errors: []
---
```

---

## Validation Rules

### Required Field Validation

1. `execution.id` must match pattern `EXEC-[0-9]{8}-[0-9]{6}`
2. `execution.instance_id` must match pattern `PINST-[0-9]{8}-[0-9]{6}`
3. `execution.started` must be valid ISO 8601
4. Each step_execution must have `step_id`, `status`, `started`

### Consistency Validation

1. `completed` should be set when status is COMPLETED, FAILED, or BLOCKED
2. All DEC-* and OBS-* IDs in step_executions should exist in audit_summary lists
3. Audit summary counts should match actual counts
4. Control flow events should correspond to step execution escalations

---

## Operations

### Creating an ExecutionLog

The process-executor creates logs by:
1. Generating timestamp-based ID
2. Setting `instance_id` from ProcessInstance
3. Setting `started` timestamp
4. Initialising empty `step_executions` array
5. Writing to `.dialogue/logs/executions/`

### Recording Step Execution

After each step:
1. Create StepExecution record with timing
2. Record any DEC-*/OBS-* IDs created during step
3. Update audit_summary counts
4. Append to step_executions array

### Finalising Execution

When execution completes:
1. Set `completed` timestamp
2. Set final `status`
3. Verify audit_summary matches step_execution totals

---

## Traceability

The ExecutionLog enables full traceability:

```
EXEC-20260118-143055
    ├── step 5.1.1 → OBS-20260118-143100
    ├── step 5.1.2 → DEC-20260118-143500
    │               → OBS-20260118-143200
    │               → OBS-20260118-143400
    ├── step 5.1.3 → OBS-20260118-143900
    └── step 5.1.4 → OBS-20260118-144500
```

Given any DEC-* or OBS-*, you can trace back to:
- Which step produced it
- Which process instance
- Which process definition
- What the user's plain English request was

---

*This schema enables complete execution audit trails with linkage to decisions and observations.*
