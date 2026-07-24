---
paths:
  - ".dialogue/logs/observations/**/*"
---

# Observation Log Operations

**MUST use `dialogue-framework:dialogue-log-observation` skill for all observation logging.**

Do NOT use Edit, Write, or Bash directly on `.dialogue/logs/observations/` files.

## Required Behaviour

```
User: "note this observation" or "I noticed that..."
CORRECT: Invoke Skill tool with skill="dialogue-framework:dialogue-log-observation"
WRONG: Write directly to .dialogue/logs/observations/
```

## Why Skills

- Skills generate correct timestamps and IDs
- Skills categorise observations appropriately
- Skills maintain audit trail

## Exceptions

MAY use raw tools only for emergency recovery or explicit user instruction.
When bypassing, state: "Using direct Write because [reason]."
