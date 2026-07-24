---
paths:
  - ".dialogue/tasks/**/*"
---

# Task File Operations

**MUST use `dialogue-framework:dialogue-manage-tasks` skill for all task operations.**

Do NOT use Edit, Write, or Bash directly on `.dialogue/tasks/*.yaml` files.

## Required Behaviour

```
User: "list tasks"
CORRECT: Invoke Skill tool with skill="dialogue-framework:dialogue-manage-tasks"
WRONG: Run list-tasks.sh via Bash directly

User: "update FW-047 to completed"
CORRECT: Invoke Skill tool with skill="dialogue-framework:dialogue-manage-tasks"
WRONG: Use Edit tool on .dialogue/tasks/FW-047.yaml directly

User: "start on FW-043"
CORRECT: Invoke Skill tool to update status
WRONG: Use sed or Edit to change status field
```

## Exceptions

MAY use raw tools only for:
- Initial framework setup via `/init-dialogue`
- Emergency recovery when skills are broken
- Explicit user instruction to bypass

When bypassing, state: "Using direct Edit because [reason]."
