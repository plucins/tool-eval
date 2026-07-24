---
paths:
  - ".dialogue/logs/decisions/**/*"
---

# Decision Log Operations

**MUST use `dialogue-framework:dialogue-log-decision` skill for all decision logging.**

Do NOT use Edit, Write, or Bash directly on `.dialogue/logs/decisions/` files.

## Required Behaviour

```
User makes a decision or says "let's go with X"
CORRECT: Invoke Skill tool with skill="dialogue-framework:dialogue-log-decision"
WRONG: Write directly to .dialogue/logs/decisions/

User: "log this decision"
CORRECT: Invoke the dialogue-log-decision skill
WRONG: Create the log file manually with Write tool
```

## Why Skills

- Skills generate correct timestamps and IDs
- Skills validate required fields (rationale, context)
- Skills maintain audit trail

## Exceptions

MAY use raw tools only for emergency recovery or explicit user instruction.
When bypassing, state: "Using direct Write because [reason]."
