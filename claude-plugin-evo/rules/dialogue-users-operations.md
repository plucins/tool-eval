---
paths:
  - ".dialogue/users/**/*"
---

# User Registration Files

**User files are managed automatically by the SessionStart hook.**

Do NOT use Edit or Write directly on `.dialogue/users/*.yaml` files.

## How It Works

- SessionStart hook detects current user via `$USER`
- Creates `.dialogue/users/{username}.yaml` on first session
- Updates `last_seen` timestamp on subsequent sessions

## Required Behaviour

```
CORRECT: Let SessionStart hook manage user registration
WRONG: Manually create or edit user files
```

## Exceptions

MAY use raw tools only for:
- Emergency recovery when hook is broken
- Explicit user instruction to modify registration

When bypassing, state: "Using direct Edit because [reason]."
