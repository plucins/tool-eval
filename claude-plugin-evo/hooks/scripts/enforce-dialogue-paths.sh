#!/bin/bash
# enforce-dialogue-paths.sh — PreToolUse hook for Edit and Write
# Part of the Dialogue Framework plugin
#
# Blocks direct Edit/Write operations on protected .dialogue/ paths,
# directing Claude to use the appropriate skill instead.
#
# Context: FW-047 identified repeated bypass of skills with raw tools.
# This hook enforces the path-to-skill mapping documented in rule files.

set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/hook-lib.sh"

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // ""')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""')

# Only check Edit and Write tools
if [[ "$TOOL_NAME" != "Edit" && "$TOOL_NAME" != "Write" ]]; then
    exit 0
fi

# Bypass check (FW-065): correction mode via signal file.
# To enable: echo "reason for correction" > /tmp/dialogue-correction-mode
# The file MUST contain a non-empty reason string — empty files (touch) are ignored.
# This is an escape hatch for fixing errors in existing log entries
# (wrong attribution, typos, etc). Remove the signal file after corrections.
# A PreToolUse:Bash hook (guard-correction-mode.sh) gates creation of this file.
if [[ -f /tmp/dialogue-correction-mode ]]; then
    CORRECTION_REASON=$(head -1 /tmp/dialogue-correction-mode 2>/dev/null | xargs)
    if [[ -n "$CORRECTION_REASON" ]]; then
        exit 0
    fi
fi

# Extract just the relative path for matching
REL_PATH="$FILE_PATH"
if [[ "$FILE_PATH" == /* ]]; then
    # Get project directory from environment or infer from common patterns
    PROJECT_DIR="${CLAUDE_PROJECT_DIR:-}"
    if [[ -n "$PROJECT_DIR" && "$FILE_PATH" == "$PROJECT_DIR"* ]]; then
        REL_PATH="${FILE_PATH#$PROJECT_DIR/}"
    fi
fi

# Check if this is a protected .dialogue/ path
case "$REL_PATH" in
    .dialogue/tasks/*.yaml|.dialogue/tasks/*)
        cat << 'EOF'
{"decision": "block", "reason": "SKILL REQUIRED: Use dialogue-manage-tasks skill for task operations. Do NOT edit .dialogue/tasks/ files directly. The skill ensures correct status transitions, timestamps, and auto-commits. If you must bypass, say 'bypass dialogue skill' explicitly."}
EOF
        exit 0
        ;;

    .dialogue/logs/decisions/*.yaml|.dialogue/logs/decisions/*)
        cat << 'EOF'
{"decision": "block", "reason": "SKILL REQUIRED: Use dialogue-log-decision skill to log decisions. Do NOT write to .dialogue/logs/decisions/ directly. The skill generates correct IDs, timestamps, and context-graph entries. If you must bypass, say 'bypass dialogue skill' explicitly."}
EOF
        exit 0
        ;;

    .dialogue/logs/observations/*.yaml|.dialogue/logs/observations/*)
        cat << 'EOF'
{"decision": "block", "reason": "SKILL REQUIRED: Use dialogue-log-observation skill to log observations. Do NOT write to .dialogue/logs/observations/ directly. The skill generates correct IDs, timestamps, and categorisation. If you must bypass, say 'bypass dialogue skill' explicitly."}
EOF
        exit 0
        ;;

    .dialogue/context-graph/nodes/*.yaml|.dialogue/context-graph/edges/*.yaml|.dialogue/context-graph/*)
        # Context graph has scripts, not skills
        cat << 'EOF'
{"decision": "block", "reason": "SCRIPTS REQUIRED: Use context-graph scripts in .dialogue/context-graph/scripts/ for graph operations. Do NOT edit node/edge YAML directly. Scripts maintain referential integrity. Available: graph-locate.sh, bootstrap-node.sh, graph-trace.sh. If you must bypass, say 'bypass dialogue skill' explicitly."}
EOF
        exit 0
        ;;

    .dialogue/users/*.yaml|.dialogue/users/*)
        cat << 'EOF'
{"decision": "block", "reason": "AUTOMATIC MANAGEMENT: User files are managed by SessionStart hook. Do NOT edit .dialogue/users/ directly. The hook handles registration and last_seen timestamps. If you must bypass, say 'bypass dialogue skill' explicitly."}
EOF
        exit 0
        ;;
esac

# Not a protected path - allow
exit 0
