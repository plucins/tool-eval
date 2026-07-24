#!/bin/bash
# post-ask-user-decision-check.sh — PostToolUse hook for AskUserQuestion
# Part of the Dialogue Framework plugin
#
# AskUserQuestion answers bypass UserPromptSubmit, so decisions made
# through the question UI are never classified. This hook injects a
# directive to assess whether the answer constitutes a decision.

set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/hook-lib.sh"

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // ""')

if [[ "$TOOL_NAME" != "AskUserQuestion" ]]; then
    exit 0
fi

cat << 'EOF'
{"hookSpecificOutput": {"additionalContext": "<dialogue-instruction>DECISION CHECK: The user just answered a question via AskUserQuestion. Their selection likely constitutes a decision. You MUST either (a) use the dialogue-log-decision skill to record this decision (OPERATIONAL or TACTICAL depending on impact), OR (b) explicitly state why not (e.g. 'Skipping log: routine confirmation'). Silent skips are not acceptable.</dialogue-instruction>"}}
EOF
