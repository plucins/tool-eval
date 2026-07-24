# Dialogue Framework Quick Reference

Scannable reference for all commands and skills. For detailed documentation, see `framework-manual.md`.

---

## Commands (explicit `/command` invocation)

| Command | Purpose | Example |
|---------|---------|---------|
| `/init-dialogue` | Initialise framework for a project | `/init-dialogue` |
| `/create-theory` | Create THY document (understanding, mental models) | `/create-theory authentication flow` |
| `/create-reference` | Create REF document (catalogues, glossaries) | `/create-reference API endpoints` |
| `/create-strategy` | Create STR document (decisions, rationale) | `/create-strategy migration approach` |
| `/create-note` | Create NOT document (notes, workshop outputs) | `/create-note sprint review` |
| `/help [topic]` | Get help (commands, phases, patterns, skills) | `/help skills` |
| `/set-mode` | Change interaction mode mid-session | `/set-mode ai-led` |

---

## Skills (activate automatically on trigger phrases)

### Document Creation

| Skill | Triggers | Purpose |
|-------|----------|---------|
| `dialogue-create-theory` | "capture theory", "document understanding", "explain why this works" | Create THY documents |
| `dialogue-create-reference` | "create reference", "make glossary", "catalogue these" | Create REF documents |
| `dialogue-create-strategy` | "document strategy", "capture rationale", "business case" | Create STR documents |
| `dialogue-create-note` | "capture notes", "document meeting", "save analysis" | Create NOT documents |
| `dialogue-create-adr` | "create an ADR", "architecture decision", "formal alternatives" | Create Architecture Decision Records |

### Logging & Tracking

| Skill | Triggers | Purpose |
|-------|----------|---------|
| `dialogue-log-decision` | "I decided...", "let's go with...", "log decision" | Record decisions with rationale |
| `dialogue-log-observation` | "I noticed...", "log observation", "capture state" | Record findings, measurements, events |
| `dialogue-manage-tasks` | "create task", "next task", "what's in progress", "status" | Manage work items in `.dialogue/tasks/` |
| `dialogue-save-session` | "save session", "end session", "remember context" | Save session memo for continuity |
| `dialogue-daily-check` | "daily check", "end of day check", "how was today" | Log developer experience assessment |

### Assessment & Process

| Skill | Triggers | Purpose |
|-------|----------|---------|
| `dialogue-assess-phase` | "assess phase", "phase readiness", "ready to proceed" | Check readiness for phase transition |
| `dialogue-assess-framing` | "assess framing", "check problem framing", "well-defined?" | Validate problem definition quality |
| `dialogue-verify-logging-compliance` | "verify logging", "check compliance" | Ensure decisions/observations captured |
| `dialogue-structured-elicit` | "gather requirements", "elicit context", "need to understand" | Framework-aware questioning |

### Discovery & Help

| Skill | Triggers | Purpose |
|-------|----------|---------|
| `dialogue-help` | "what can you do", "how does dialogue work", "framework help" | Get contextual help |
| `dialogue-resolve-reference` | "look up THY-001", "find DEC-...", "what is ADR-001" | Resolve framework IDs to content |

### Utility

| Skill | Triggers | Purpose |
|-------|----------|---------|
| `tmux` | "tmux", "create session", "terminal session" | Manage tmux sessions |

---

## Common Workflows

| "How do I..." | Use |
|---------------|-----|
| **Log a decision** | Say "I decided to..." or "let's go with..." |
| **Record an observation** | Say "I noticed..." or "log observation" |
| **Create documentation** | `/create-theory`, `/create-reference`, `/create-strategy` |
| **See what's in progress** | Say "status" or "what tasks" |
| **Create a new task** | Say "create task for..." |
| **Get help** | `/help` or ask "what can you do" |
| **Check phase readiness** | Say "assess phase" or "ready to proceed" |
| **Save context for later** | Say "save session" |
| **Change help verbosity** | `/set-mode human-led` or `/set-mode ai-led` |

---

## Interaction Modes

Control how verbose and proactive Claude is:

| Mode | Help Style | Session Start | When to Use |
|------|------------|---------------|-------------|
| `human-led` | Concise, on-demand | Status only | Experienced users, focused work |
| `partnership` | Balanced, suggests | Status + hints | Default, general use |
| `ai-led` | Verbose, proactive | Status + recommendations | New users, exploration |

Change with: `/set-mode [mode]` or set `interaction_mode` in `.dialogue/config.yaml`

---

## Document Types

| Type | Code | Persistence | Use For |
|------|------|-------------|---------|
| Theory | THY | Standing | Mental models, integrated understanding |
| Reference | REF | Standing | Catalogues, glossaries, explainers |
| Strategy | STR | Standing | Decisions, rationale, business cases |
| Note | NOT | Ephemeral | Workshop notes, analysis, meeting outputs |
| ADR | ADR | Standing | Architecture decisions with alternatives |

---

## SDLC Phases (for context)

| Phase | Name | Tacit % | Typical Pattern |
|-------|------|---------|-----------------|
| 1 | Initiation | 75% | Human-Led |
| 2 | Planning | 55% | Human-Led |
| 3 | Requirements | 40% | Partnership |
| 4 | Design | 35% | Partnership |
| 5 | Implementation | 25% | AI-Led |
| 6 | Testing | 20% | AI-Led |
| 7 | Operations | 30% | Partnership |

---

*For detailed documentation: `claude-plugin-evo/references/framework-manual.md`*
