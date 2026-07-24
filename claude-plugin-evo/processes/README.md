# Process Definitions

This directory contains **well-known process definitions** — reusable templates for capability flows that can be executed by the process-executor agent.

## Overview

Process definitions describe *what could happen* in a structured, repeatable way. They define:
- Capability flow steps
- Human-AI collaboration patterns for each step
- Escalation triggers and control flow
- Entry and exit criteria

## Schema

Process definitions follow the schema defined in:
- [Schema: Process Definition](../references/schema_process-definition.md)

## File Naming Convention

```
process-<descriptive-name>.yaml
```

Examples:
- `process-code-review.yaml`
- `process-requirements-elicitation.yaml`
- `process-architecture-decision.yaml`

## Usage

Process definitions are referenced by **ProcessInstances** which capture execution intent:

```yaml
# .dialogue/processes/PINST-*.yaml
definition_source:
  type: WELL_KNOWN
  definition_id: "PROC-5.1"
  definition_path: "claude-plugin-evo/processes/process-code-review.yaml"
```

The **process-executor** agent loads and executes these definitions.

## Plain English UX

Users interact with processes via plain English descriptions, never process IDs. The `plain_english_description` field in ProcessInstances translates technical processes into user-understandable language.

## Related Directories

| Directory | Purpose |
|-----------|---------|
| `.dialogue/processes/` | ProcessInstances (runtime execution intent) |
| `.dialogue/logs/executions/` | ExecutionLogs (runtime execution records) |

## Creating New Process Definitions

1. Design the capability flow using the Process Architect agent
2. Validate against schema constraints (C1-C4)
3. Save to this directory with appropriate naming
4. Test by creating a ProcessInstance and executing

## Constraints

All process definitions must satisfy:

| ID | Rule |
|----|------|
| **C1** | Human-Only → ai_role is "None" or describes passive/ambient support (not active participation) |
| **C2** | AI-Only → human_role describes governance (defines rules, audits, oversees) — never "None" |
| **C3** | Active ai_role (analysis, generation, execution) → pattern ≠ Human-Only |
| **C4** | human_role = "None" → pattern ≠ AI-Only |

---

*Part of the Dialogue Framework*
