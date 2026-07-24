---
name: set-mode
description: Change interaction mode mid-session. Controls help verbosity and AI proactivity.
argument-hint: <human-led|partnership|ai-led>
---

# /set-mode Command

Change the interaction mode for this session and future sessions.

## Usage

```
/set-mode human-led    # Concise, on-demand help
/set-mode partnership  # Balanced help with suggestions (default)
/set-mode ai-led       # Verbose, proactive help
```

## Steps

### 1. Validate the Mode Argument

Check `$ARGUMENTS` for a valid mode:
- `human-led` - Concise, minimal output
- `partnership` - Balanced (default)
- `ai-led` - Verbose, proactive

If no argument or invalid argument:
- Show current mode (read from session memo or config)
- List valid options with brief descriptions
- Ask which mode they want

### 2. Update Session Memo

Determine the username and update the session memo:

```bash
USERNAME="${USER:-$(whoami)}"
SESSION_MEMO=".dialogue/session-memo-${USERNAME}.yaml"
```

If session memo exists:
- Update or add `interaction_mode_preference: <mode>`

If session memo doesn't exist:
- Create minimal session memo with the preference:
```yaml
username: "{username}"
last_session: "{timestamp}"
interaction_mode_preference: {mode}
```

### 3. Confirm the Change

Adapt confirmation message to the new mode:

**For human-led**:
> Mode set to human-led.

**For partnership**:
> Mode set to partnership. I'll provide balanced help with suggestions.

**For ai-led**:
> Mode set to ai-led. I'll provide comprehensive help and proactively suggest actions. Here's what I can help with:
> - Decision and observation logging (say "I decided..." or "I noticed...")
> - Task management (say "create task", "status", "next task")
> - Document creation (/create-theory, /create-reference, etc.)
> - Phase assessments (say "assess phase" or "ready to proceed")
>
> What would you like to work on?

## Mode Descriptions

| Mode | What Changes |
|------|--------------|
| **human-led** | Minimal session start message. Help is direct without elaboration. No unsolicited suggestions. |
| **partnership** | Status + hints at session start. Help includes context and follow-up options. Occasional suggestions. |
| **ai-led** | Full instructions + recommendations at session start. Verbose help with examples. Explains framework actions. Proactively surfaces capabilities. |

## Notes

- Mode preference is stored per-user in session memo
- Persists across sessions until changed
- User preference overrides project config
- Project config is in `.dialogue/config.yaml` as `interaction_mode`
