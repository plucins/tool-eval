# Human-Only Handoff Mechanism

**Document Type**: REF (Reference)
**Status**: ACTIVE
**Version**: 1.1
**References**: DEC-20260120-174641

---

## Purpose

This document defines the operational mechanism for **Human-Only** collaboration pattern steps. Human-Only encompasses two modes:

- **Exit mode**: AI absent entirely; creates blocking handoff, process pauses
- **Observer mode**: AI present but passive; provides ambient support (prepares materials, records outcomes)

In both modes, the human has sole execution responsibility — AI does not actively participate in the capability.

### Distinguishing Human-Only Modes from Human-Led

| Pattern | AI Presence | AI Activity | Process State |
|---------|-------------|-------------|---------------|
| **Human-Led** | Present, active | Drives analysis, suggests, supports | Continues |
| **Human-Only (Observer)** | Present, passive | Prepares, records, synthesises | May continue in background |
| **Human-Only (Exit)** | Absent | None | Pauses |

---

## When to Use Each Mode

### Exit Mode

Use exit mode when AI presence would inhibit the activity:

1. **Psychological safety required**: Team retrospectives, conflict resolution
2. **Sensitive conversations**: Performance discussions, confidential matters
3. **AI presence inappropriate**: Formal approvals requiring human-only accountability
4. **No value from recording**: Activities where AI observation adds no benefit

### Observer Mode

Use observer mode when AI can provide ambient support without active participation:

1. **Workshops and meetings**: AI prepares materials beforehand, records outcomes afterward
2. **Executive briefings**: AI provides background materials, synthesises notes
3. **Planning sessions**: AI tracks decisions without driving the discussion
4. **External activities**: Where AI preparation and post-processing adds value

### Human-Led (Not Human-Only)

Use Human-Led when AI should actively participate:
- AI could usefully drive analysis or provide suggestions during the activity
- AI could provide real-time information to support human decisions
- The activity benefits from AI's active support throughout

---

## Blocking Task Structure

When AI encounters a Human-Only step, it creates a blocking task with the following structure:

```yaml
# Blocking task for Human-Only handoff
id: "<generated-id>"
title: "<step name> - Human-Only"
status: BLOCKED_PENDING_HUMAN
created: "<timestamp>"
type: HANDOFF

# Who is responsible
responsible_party:
  role: "<role or specific person>"
  contact: "<optional contact info>"

# What is needed
required_output:
  description: "<what the human must produce>"
  format: "<expected format of output>"
  acceptance_criteria:
    - "<criterion 1>"
    - "<criterion 2>"

# How - expected activities
expected_activities:
  - activity: "<activity description>"
    participants: ["<who should be involved>"]
    duration_estimate: "<optional duration>"

# What this blocks
downstream_dependencies:
  process_id: "<PROC-X.Y>"
  blocked_steps:
    - "<step id that cannot proceed>"
  impact: "<what happens if delayed>"

# Where to resume
re_entry:
  step_id: "<step to resume at>"
  context_needed:
    - "<what context AI needs to continue>"

# When
timeline:
  requested_by: "<optional deadline>"
  sla_hours: <optional SLA>
  escalation_path: "<who to escalate to if overdue>"

# Process context
process_context:
  instance_id: "<process instance if applicable>"
  completed_steps: ["<list of completed steps>"]
  state_snapshot: "<relevant state at handoff>"
```

---

## AI Behaviour at Human-Only Steps

When AI reaches a Human-Only step:

### 1. Announce the Handoff

```
This step requires Human-Only execution: [step name]

I need to hand off to you for [activity description].

What's needed:
- [required output description]

Expected activities:
- [activity 1]
- [activity 2]

This blocks: [downstream steps/processes]

I'll create a task to track this and pause here until you return with [output].
```

### 2. Create the Blocking Task

Create a task file in `.dialogue/tasks/` with the blocking task structure.

### 3. Exit the Process

The process pauses. AI should:
- Confirm the task was created
- Provide any context the human needs to complete the activity
- Indicate how to signal completion
- Not proceed with subsequent steps

### 4. Do Not Simulate Completion

AI must **never**:
- Generate output that should come from the human activity
- Assume what the human decided or discovered
- Skip the step because it "seems straightforward"

---

## Re-Entry Mechanism

### Human Signals Completion

The human signals completion by:

1. **Updating the task status**: Change `status: BLOCKED_PENDING_HUMAN` to `status: COMPLETED`
2. **Providing the output**: Add the required output to the task or reference where it's stored
3. **Resuming dialogue**: Return to the AI dialogue and indicate readiness to continue

### Resumption Prompt

Human returns with:
```
[Task X] is complete. Here's the output: [output or reference]

Ready to continue with [process name].
```

### AI Validates and Continues

AI should:
1. Read the completed task
2. Validate the output meets acceptance criteria
3. Resume at the specified re-entry step
4. Incorporate the human-provided output into the process

If output is incomplete:
```
The output from [step] doesn't fully meet the acceptance criteria:
- [criterion]: [status]

Should we:
1. Proceed with partial information
2. Return to complete [missing aspect]
```

---

## Example Human-Only Steps

### Example 1: Stakeholder Workshop

**Process**: PROC-1.2 Stakeholder Alignment
**Step**: Conduct stakeholder workshop

```yaml
id: "HO-20260120-001"
title: "Conduct Stakeholder Alignment Workshop - Human-Only"
status: BLOCKED_PENDING_HUMAN
type: HANDOFF

responsible_party:
  role: "Project Lead"

required_output:
  description: "Workshop outcomes documenting stakeholder priorities and concerns"
  format: "Meeting notes or structured summary"
  acceptance_criteria:
    - "All key stakeholders represented"
    - "Priority rankings captured"
    - "Major concerns documented"
    - "Action items identified"

expected_activities:
  - activity: "Facilitate stakeholder workshop"
    participants: ["Project Lead", "Key Stakeholders", "Business Sponsor"]
    duration_estimate: "2-3 hours"

downstream_dependencies:
  process_id: "PROC-1.2"
  blocked_steps: ["1.2.4", "1.2.5"]
  impact: "Cannot finalise stakeholder alignment without workshop input"

re_entry:
  step_id: "1.2.4"
  context_needed:
    - "Workshop outcomes"
    - "Stakeholder priority rankings"
    - "Identified concerns and constraints"

timeline:
  requested_by: "2026-01-25"
  escalation_path: "Business Sponsor"
```

### Example 2: Executive Sign-Off

**Process**: PROC-1.4 Business Case
**Step**: Obtain executive approval

```yaml
id: "HO-20260120-002"
title: "Obtain Executive Sign-Off - Human-Only"
status: BLOCKED_PENDING_HUMAN
type: HANDOFF

responsible_party:
  role: "Business Sponsor"

required_output:
  description: "Formal approval decision with any conditions"
  format: "Signed approval or documented decision"
  acceptance_criteria:
    - "Decision is explicit (approved/rejected/conditional)"
    - "Any conditions are documented"
    - "Decision-maker is authorised"

expected_activities:
  - activity: "Present business case to executive"
    participants: ["Business Sponsor", "Executive Approver"]
  - activity: "Address questions and concerns"
    participants: ["Business Sponsor", "Project Lead"]
  - activity: "Obtain formal decision"
    participants: ["Executive Approver"]

downstream_dependencies:
  process_id: "PROC-1.4"
  blocked_steps: ["1.4.6"]
  impact: "Project cannot proceed to planning without executive approval"

re_entry:
  step_id: "1.4.6"
  context_needed:
    - "Approval decision"
    - "Any conditions or modifications required"
    - "Timeline expectations from executive"

timeline:
  sla_hours: 72
  escalation_path: "Programme Director"
```

### Example 3: Team Retrospective

**Process**: PROC-7.3 Incident Response
**Step**: Conduct blameless retrospective

```yaml
id: "HO-20260120-003"
title: "Conduct Blameless Retrospective - Human-Only"
status: BLOCKED_PENDING_HUMAN
type: HANDOFF

responsible_party:
  role: "Team Lead"

required_output:
  description: "Retrospective findings and improvement actions"
  format: "Retrospective summary document"
  acceptance_criteria:
    - "Root causes identified (not individuals blamed)"
    - "Contributing factors documented"
    - "Improvement actions proposed"
    - "Action owners assigned"

expected_activities:
  - activity: "Facilitate blameless retrospective"
    participants: ["Team Lead", "Incident Responders", "Affected Team Members"]
    duration_estimate: "1-2 hours"

downstream_dependencies:
  process_id: "PROC-7.3"
  blocked_steps: ["7.3.6"]
  impact: "Prevention planning requires retrospective input"

re_entry:
  step_id: "7.3.6"
  context_needed:
    - "Root cause analysis"
    - "Proposed improvement actions"
    - "Assigned action owners"

timeline:
  requested_by: "Within 5 business days of incident resolution"
  escalation_path: "Engineering Manager"
```

---

## Schema Constraint Clarification

Schema constraint **C1** applies to Human-Only steps:

> **C1**: Human-Only → ai_role is "None" or describes passive/ambient support (not active participation)

This means:
- If `pattern: Human-Only` with **exit mode**, then `ai_role: "None"`
- If `pattern: Human-Only` with **observer mode**, then `ai_role` describes ambient support (e.g., "Prepares background materials; records outcomes")
- In both cases, AI does not actively participate in the capability execution

The distinction from Human-Led: in Human-Led, AI actively supports throughout (analysis, suggestions, real-time information). In Human-Only observer mode, AI only provides preparation and post-processing — passive presence during the activity itself.

---

## Choosing Between Modes

| Consideration | Human-Only (Exit) | Human-Only (Observer) | Human-Led |
|---------------|-------------------|----------------------|-----------|
| Activity location | External | External or internal | Within dialogue |
| AI presence | Inappropriate | Acceptable but passive | Active participation |
| AI adds value during activity | No | No (only before/after) | Yes |
| Multiple participants | Often | Often | Rarely |
| Duration | Hours to days | Hours to days | Minutes |
| Process state | Pauses | May continue | Continues |

**Decision flow**:
1. Would AI presence inhibit the activity? → **Exit mode**
2. Can AI usefully prepare materials or record outcomes? → **Observer mode**
3. Should AI actively support throughout? → **Human-Led**

---

## Integration with Process Executor

When the process executor encounters a Human-Only step:

1. **Pre-step**: Executor identifies `pattern: Human-Only`
2. **Handoff**: Executor creates blocking task with step context
3. **Pause**: Executor marks process instance as `AWAITING_HUMAN_INPUT`
4. **Resume trigger**: Human updates task to `COMPLETED`
5. **Validation**: Executor validates output against acceptance criteria
6. **Continue**: Executor proceeds to next step with human-provided output

The executor should never attempt to execute a Human-Only step itself.

---

*This mechanism ensures Human-Only truly means human-only, enabling proper separation between AI-assisted activities and external human activities.*
