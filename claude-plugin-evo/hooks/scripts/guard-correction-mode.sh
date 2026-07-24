#!/bin/bash
# guard-correction-mode.sh — PreToolUse hook for Bash
# Part of the Dialogue Framework plugin (FW-065)
#
# Injects a human-approval gate when any Bash command references the
# dialogue correction mode signal file. Ensures Claude does not enter
# correction mode without explicit user request.

set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/hook-lib.sh"

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // ""')

if [[ "$TOOL_NAME" != "Bash" ]]; then
    exit 0
fi

COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

# Check if command references the correction mode signal file
if echo "$COMMAND" | grep -q "dialogue-correction-mode"; then
    cat << 'EOF'
{"hookSpecificOutput": {"additionalContext": "<dialogue-instruction>CORRECTION MODE GATE: This command involves the dialogue correction mode signal file. REQUIREMENTS: (1) The user MUST have explicitly requested entering correction mode in this conversation. (2) Write a reason string into the file — do NOT use touch (empty files are rejected by the bypass check). Use: echo 'reason for correction' > /tmp/dialogue-correction-mode. (3) Remove the signal file immediately after corrections are complete. If the user did not explicitly request correction mode, ABORT this command.</dialogue-instruction>"}}
EOF
    exit 0
fi

exit 0
