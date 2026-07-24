#!/bin/bash
# enforce-dialogue-bash.sh — PreToolUse hook for Bash
# Part of the Dialogue Framework plugin
#
# Blocks Bash commands that directly manipulate .dialogue/ paths when
# skills should be used instead. Allows legitimate Bash operations
# like running skill scripts.
#
# Context: FW-047 identified repeated bypass of skills with raw tools.
# Pattern: `ls .dialogue/tasks/` instead of dialogue-manage-tasks skill.

set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/hook-lib.sh"

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // ""')

# Only check Bash tool
if [[ "$TOOL_NAME" != "Bash" ]]; then
    exit 0
fi

COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

# Skip empty commands
if [[ -z "$COMMAND" ]]; then
    exit 0
fi

# Allow skill script execution (these are the approved entry points)
if echo "$COMMAND" | grep -qE "(dialogue-manage-tasks|log-decision|log-observation|create-task|update-task|list-tasks)"; then
    exit 0
fi

# Allow context-graph scripts explicitly
if echo "$COMMAND" | grep -qE "context-graph/scripts/"; then
    exit 0
fi

# Check for direct file listing of protected paths
# Pattern: ls, cat, head, tail, grep on .dialogue/ subdirectories
if echo "$COMMAND" | grep -qE "(ls|cat|head|tail|less|more|grep|rg|awk|sed)\s+.*\.dialogue/tasks"; then
    cat << 'EOF'
{"decision": "block", "reason": "SKILL REQUIRED: Use dialogue-manage-tasks skill to list/view tasks. Do NOT use ls/cat/grep on .dialogue/tasks/ directly. Example: Invoke Skill tool with skill='dialogue-framework:dialogue-manage-tasks'."}
EOF
    exit 0
fi

if echo "$COMMAND" | grep -qE "(ls|cat|head|tail|less|more|grep|rg|awk|sed)\s+.*\.dialogue/logs/decisions"; then
    cat << 'EOF'
{"decision": "block", "reason": "SKILL REQUIRED: Use dialogue-resolve-reference skill to view decisions. Do NOT use cat/grep on .dialogue/logs/decisions/ directly."}
EOF
    exit 0
fi

if echo "$COMMAND" | grep -qE "(ls|cat|head|tail|less|more|grep|rg|awk|sed)\s+.*\.dialogue/logs/observations"; then
    cat << 'EOF'
{"decision": "block", "reason": "SKILL REQUIRED: Use dialogue-resolve-reference skill to view observations. Do NOT use cat/grep on .dialogue/logs/observations/ directly."}
EOF
    exit 0
fi

# Check for direct echo/printf redirection to protected paths
if echo "$COMMAND" | grep -qE "(echo|printf).*>>?\s*.*\.dialogue/(tasks|logs|users)/"; then
    cat << 'EOF'
{"decision": "block", "reason": "SKILL REQUIRED: Use dialogue framework skills instead of echo/printf redirection to .dialogue/ files. Tasks: dialogue-manage-tasks. Decisions: dialogue-log-decision. Observations: dialogue-log-observation."}
EOF
    exit 0
fi

# Check for direct rm/mv on protected paths (destructive operations)
if echo "$COMMAND" | grep -qE "(rm|mv)\s+.*\.dialogue/(tasks|logs|context-graph|users)/"; then
    cat << 'EOF'
{"decision": "block", "reason": "DESTRUCTIVE OPERATION BLOCKED: Do NOT delete/move files in .dialogue/ directly. Use dialogue framework skills for state management."}
EOF
    exit 0
fi

# Check for touch/mkdir in protected paths
if echo "$COMMAND" | grep -qE "(touch|mkdir)\s+.*\.dialogue/(tasks|logs|context-graph|users)/"; then
    cat << 'EOF'
{"decision": "block", "reason": "SKILL REQUIRED: Use dialogue framework skills to create files in .dialogue/. Do NOT use touch/mkdir directly. Skills handle proper schema, timestamps, and context-graph integration."}
EOF
    exit 0
fi

# Not a problematic pattern - allow
exit 0
