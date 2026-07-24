#!/bin/bash
# plan-mode-catchup.sh — PostToolUse(ExitPlanMode) hook
# Part of the Dialogue Framework plugin
#
# Fires when plan mode exits. Injects catch-up directive to review the plan
# for decisions and observations that should be logged. At this point the AI
# has full tool access again, so it can use logging skills.
#
# Context: FW-054 layer 3 — plan mode tool availability workaround.
# During plan mode, hooks detect decisions/observations but the AI cannot
# act on them (Skill/Task/Bash unavailable). This hook provides a catch-up
# window when tools are restored.

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/hook-lib.sh"

# Read JSON input — PostToolUse provides tool_name, tool_input, tool_response, permission_mode
INPUT=$(cat)

# Output catch-up directive
jq -n '{
    "hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": "<dialogue-instruction>PLAN MODE EXIT: You have just exited plan mode and regained full tool access. Before proceeding with implementation, review the plan for any decisions or observations made during planning that should be logged. Use dialogue-log-decision for choices made and dialogue-log-observation for findings. Only log substantive items — skip trivial or procedural decisions.</dialogue-instruction>"
    }
}'
