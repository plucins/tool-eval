#!/bin/bash
# PreToolUse hook: Auto-approve Process Orchestrator Task invocations
#
# Auto-approves Task tool invocations targeting the process-orchestrator agent.
# The Orchestrator is internal infrastructure — it shouldn't require user
# approval for each invocation.
#
# Design: Only approve Task invocations with process-orchestrator subagent_type.

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/hook-lib.sh"

# Read JSON input
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // ""')

# Only process Task tools
if [[ "$TOOL_NAME" != "Task" ]]; then
    exit 0
fi

# Check if the Task invocation targets the Process Orchestrator
SUBAGENT_TYPE=$(echo "$INPUT" | jq -r '.tool_input.subagent_type // ""')

if [[ "$SUBAGENT_TYPE" == *"Process Orchestrator"* ]]; then
    jq -n --arg reason "Auto-approved Process Orchestrator invocation" '{
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": $reason
        }
    }'
    exit 0
fi

# Not an orchestrator invocation - allow normal permission flow
exit 0
