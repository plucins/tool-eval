#!/bin/bash
# precompact-review.sh — PreCompact hook to catch unlogged items before context loss
# Part of the Dialogue Framework plugin
#
# Before context compaction, scans the transcript for AI-generated decisions
# and observations that were never logged. This is the last-chance safety net
# before context is permanently compressed.
#
# Context: FW-054 layer 2 complement — catches items that the Stop hook
# might have missed or that accumulated across multiple turns.

set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/hook-lib.sh"

INPUT=$(cat)

TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // ""')
if [[ -z "$TRANSCRIPT_PATH" || ! -f "$TRANSCRIPT_PATH" ]]; then
    exit 0
fi

# Check if any logging skills were used in this session at all
DECISION_LOGS=$(jq -r 'select(.type == "assistant") | .message.content[]? |
    select(.type == "tool_use" and .name == "Skill") | .input.skill // ""
' "$TRANSCRIPT_PATH" 2>/dev/null | grep -c "log-decision" || true)

OBSERVATION_LOGS=$(jq -r 'select(.type == "assistant") | .message.content[]? |
    select(.type == "tool_use" and .name == "Skill") | .input.skill // ""
' "$TRANSCRIPT_PATH" 2>/dev/null | grep -c "log-observation" || true)

# Count how many AI responses contained decision/observation language
ALL_AI_TEXT=$(jq -r 'select(.type == "assistant") | .message.content[]? |
    select(.type == "text") | .text // ""
' "$TRANSCRIPT_PATH" 2>/dev/null)

if [[ -z "$ALL_AI_TEXT" ]]; then
    exit 0
fi

ALL_AI_LOWER=$(echo "$ALL_AI_TEXT" | tr '[:upper:]' '[:lower:]')

DECISION_MENTIONS=0
if echo "$ALL_AI_LOWER" | grep -qE "(i recommend|we should (use|adopt|go with)|the best (approach|option) is|i.ve (decided|chosen)|trade-off.*(favour|favor|prefer))"; then
    DECISION_MENTIONS=1
fi

OBSERVATION_MENTIONS=0
if echo "$ALL_AI_LOWER" | grep -qE "(this reveals|this (indicates|suggests|shows) that|key (finding|insight|observation)|interesting(ly)?.*(finding|pattern|gap))"; then
    OBSERVATION_MENTIONS=1
fi

# If there are mentions but no logs, inject a reminder
ITEMS=""
if [[ "$DECISION_MENTIONS" -gt 0 && "$DECISION_LOGS" -eq 0 ]]; then
    ITEMS+="decisions "
fi
if [[ "$OBSERVATION_MENTIONS" -gt 0 && "$OBSERVATION_LOGS" -eq 0 ]]; then
    ITEMS+="observations "
fi

ITEMS=$(echo "$ITEMS" | xargs)

if [[ -z "$ITEMS" ]]; then
    exit 0
fi

# Output reminder (non-blocking — PreCompact should not prevent compaction)
jq -n --arg items "$ITEMS" '{
    "hookSpecificOutput": {
        "hookEventName": "PreCompact",
        "additionalContext": "<dialogue-instruction>PRE-COMPACT REVIEW: Context is about to be compacted. This session contained AI-generated \($items) that were not logged. After compaction, use dialogue-log-decision and/or dialogue-log-observation to record any substantive items before they are lost from context.</dialogue-instruction>"
    }
}'
