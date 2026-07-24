# Dialogue Framework (Evolution Model)

An AI-augmented software development lifecycle framework that leverages dialogue, decisions, and observations to enhance project outcomes.

## Overview

This Claude Code plugin provides skills and agents for maintaining structured logs of decisions and observations during software development work. These logs create an audit trail that supports:

- **Traceability**: Understanding why decisions were made
- **Knowledge preservation**: Capturing tacit knowledge as it emerges
- **Compliance verification**: Ensuring required documentation occurs

## Installation

### Development (self-hosted)

Run Claude Code with the plugin directory:

```bash
claude --plugin-dir ./claude-plugin-evo
```

### Production

Copy the `claude-plugin-evo/` directory to your Claude Code plugins location or install from marketplace (when published).

## Quick Start

Ask Claude to explain Dialogue.

```
What is Dialogue?
```

Or

```
How do I get started?
```


## Commands

User-invoked commands for explicit actions.

| Command | Purpose |
|---------|---------|
| `/init-dialogue` | Initialise framework for a project (creates `.dialogue/` directory) |
| `/create-theory` | Create THY document (integrated understanding, the "why") |
| `/create-reference` | Create REF document (catalogues, glossaries, explainers, pattern library, principle list) |
| `/create-strategy` | Create STR document (decisions, rationale, business cases) |
| `/create-note` | Create NOT document (ephemeral notes, workshop outputs) |
| `/help` | Get help with the framework, list commands, explain concepts |

## Skills

### Core Logging Skills

#### dialogue-log-decision

Log decisions to a chronological decision log. Supports four decision types:

| Type | Use Case |
|------|----------|
| OPERATIONAL | Routine choices during task execution |
| TACTICAL | Approach changes affecting method |
| DESIGN | Component/schema decisions with rationale |
| ADR | Cross-reference to Architecture Decision Record |

**Triggers**: "log decision", "record decision", "document choice"

#### dialogue-log-observation

Log observations (measurements, states, events) to an observation log.

| Type | Use Case |
|------|----------|
| MEASUREMENT | Quantitative data |
| STATE | System/process state |
| EVENT | Occurrences |

**Triggers**: "log observation", "record observation", "note finding", "capture state"

#### dialogue-create-adr

Create Architecture Decision Records for significant architectural decisions requiring formal alternatives analysis.

**Triggers**: "create ADR", "make ADR", "record architecture decision", "formal alternatives analysis"

### Supporting Skills

#### dialogue-resolve-reference

Resolve framework reference IDs (THY-001, DEC-..., ADR-001, etc.) to their content.

**Triggers**: "resolve reference", "look up THY-001", "find DEC-...", "what is ADR-001"

#### dialogue-structured-elicit

Gather structured information through framework-aware questioning.

**Triggers**: "gather requirements", "elicit context", "structured questions", "need to understand"

#### dialogue-verify-logging-compliance

Verify that required logging occurred during process execution.

**Triggers**: "verify logging", "check compliance", "validate logs"

#### dialogue-manage-tasks

Manage persistent tasks in `.dialogue/tasks.yaml`. Guidance-only skill for direct YAML editing.

**Triggers**: "create task", "update task", "manage tasks", "track tasks"

### Document Creation Skills

These skills activate autonomously and reference their corresponding commands for implementation.

#### dialogue-create-theory

Create Theory (THY) documents capturing integrated understanding.

**Triggers**: "capture theory", "document understanding", "write theory", "explain why this works"

#### dialogue-create-reference

Create Reference (REF) documents for catalogues, glossaries, and explainers.

**Triggers**: "create reference", "document concepts", "make glossary", "catalogue these"

#### dialogue-create-strategy

Create Strategy (STR) documents for decisions and rationale.

**Triggers**: "document strategy", "record strategic decision", "capture rationale"

#### dialogue-create-note

Create Note (NOT) documents for ephemeral process artefacts.

**Triggers**: "capture notes", "document meeting", "record workshop", "save analysis"

### Help Skill

#### dialogue-help

Provide contextual help and orientation for the Dialogue Framework.

**Triggers**: "how does dialogue work", "what commands", "explain phases", "framework help"

## Agents

### Process Architect

Designs capability flow specifications for SDLC processes following the AI-Augmented SDLC Framework.

**Use when**: Analysing or creating process definitions with human-AI collaboration patterns.

**Collaboration pattern**: Partnership — human provides context and approves; AI applies framework knowledge and drafts specifications.

**Tools**: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion

## Hooks

### PreToolUse: auto-approve-framework

Auto-approves Bash commands that run known-safe framework scripts, eliminating permission prompts for routine operations.

**Approved scripts:**
- `dialogue-log-decision/scripts/log-decision.sh`
- `dialogue-log-observation/scripts/log-observation.sh`
- `dialogue-resolve-reference/scripts/resolve-reference.sh`
- `dialogue-create-adr/scripts/create-adr.sh`

**Behaviour:** Returns `permissionDecision: "allow"` for approved scripts. Silent for other commands (normal permission flow).

### SessionStart: check-dialogue-init

Checks if the Dialogue Framework is initialised when a session starts. Reports status to help Claude guide the user.

### UserPromptSubmit: framework-context

Detects framework-relevant patterns in user prompts and injects directive instructions. These instructions tell Claude explicitly which skill to use, removing ambiguity.

**Instructions emitted:**

| Pattern Detected | Instruction | Action |
|------------------|-------------|--------|
| "I decided", "let's go with", etc. | `DECISION DETECTED` | Use `dialogue-log-decision` skill |
| "I noticed", "I observed", etc. | `OBSERVATION DETECTED` | Use `dialogue-log-observation` skill |
| `SH-NNN`, `FW-NNN`, `CD-NNN` | `TASK REFERENCE` | Use `dialogue-manage-tasks` skill |
| `THY-NNN`, `REF-NNN`, `DEC-*`, etc. | `REFERENCE` | Use `dialogue-resolve-reference` skill |
| Phase keywords (initiation, planning, etc.) | `PHASE N CONTEXT` | Apply phase guidance from framework-manual.md |
| "create ADR", "architecture decision" | `ADR REQUEST` | Use `dialogue-create-adr` skill |
| "implement feature", "investigate issue", etc. | `TASK CANDIDATE` | Triage: session todo vs project task |

**Output format:** `<dialogue-instruction>INSTRUCTION: Action to take.</dialogue-instruction>`

**Behaviour:** Silent when no framework relevance detected.

**Example instructions:**

```
<dialogue-instruction>DECISION DETECTED: After responding, use the dialogue-log-decision skill to record this decision with rationale.</dialogue-instruction>
```

```
<dialogue-instruction>TASK REFERENCE: Resolve FW-047 using dialogue-manage-tasks skill to understand context.</dialogue-instruction>
```

Instructions are explicit directives, not hints. When you see a `<dialogue-instruction>`, follow it.

**Task candidate triage:**

When you see `TASK CANDIDATE`, determine if the request is:

| Type | Characteristics | Action |
|------|-----------------|--------|
| **Session todo** | Quick task, single session, tactical | Use `TodoWrite` tool |
| **Project task** | Persistent, multi-session, strategic | Use `dialogue-manage-tasks` skill |

Triage questions:
1. Is this already tracked in `.dialogue/tasks/`? → Use existing item
2. Will this span multiple sessions or require ongoing tracking? → Project task
3. Is this part of the project roadmap or backlog? → Project task
4. Is this a quick fix or one-off task? → Session todo

When uncertain, default to session todo. Project tasks should be deliberate.

## Requirements

- Claude Code with plugin support
- Project must have `.dialogue/logs/` directory (created automatically)

## Environment Variables

The plugin uses Claude Code's built-in environment variables:

| Variable | Purpose |
|----------|---------|
| `CLAUDE_PROJECT_DIR` | Project root for log file storage |
| `CLAUDE_PLUGIN_ROOT` | Plugin installation directory |

## Log File Locations

Logs are written to the project directory (per-file structure):

- Decisions: `${CLAUDE_PROJECT_DIR}/.dialogue/logs/decisions/*.yaml`
- Observations: `${CLAUDE_PROJECT_DIR}/.dialogue/logs/observations/*.yaml`
- Tasks: `${CLAUDE_PROJECT_DIR}/.dialogue/tasks/*.yaml`
- ADRs: `${CLAUDE_PROJECT_DIR}/decisions/ADR-NNN-*.md`

## Part of the Dialogue Framework

This plugin implements the **Evolution** meta-process—incremental AI adoption that preserves existing practices while adding AI capabilities.

### Conceptual Basis

The plugin operationalises the guidance in [dialogue-framework-evolution.md](../dialogue-framework-evolution.md), which defines:

- Phase-specific document types and collaboration patterns
- When and how to apply AI assistance at each SDLC phase
- Transition readiness criteria between phases
- Backward event detection and handling

### Relationship

| Evolution Document | This Plugin |
|--------------------|-------------|
| Conceptual guidance | Operational tools |
| *What* to do | *How* to do it |
| Phase-by-phase practices | Skills and agents |

For the full conceptual framework, see [dialogue-framework-evolution.md](../dialogue-framework-evolution.md).
