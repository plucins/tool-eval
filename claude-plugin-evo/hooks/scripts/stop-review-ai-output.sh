#!/bin/bash
# stop-review-ai-output.sh — Stop hook to detect unlogged decisions/observations in AI output
# Part of the Dialogue Framework plugin
#
# When Claude finishes responding, this hook reads the transcript to check if
# the AI's response contained decision or observation language that wasn't
# followed by logging skill invocations. If found, blocks and directs Claude
# to log them.
#
# Context: FW-054 layer 2 — AI-generated content invisible to UserPromptSubmit
# hooks (which only see user messages). This hook closes the gap by scanning
# AI output via the transcript.
#
# Uses stop_hook_active to prevent infinite recursion.

set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/hook-lib.sh"

INPUT=$(cat)

# Prevent recursion — if already continuing from a stop hook, exit cleanly
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')
if [[ "$STOP_HOOK_ACTIVE" == "true" ]]; then
    exit 0
fi

TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // ""')
if [[ -z "$TRANSCRIPT_PATH" || ! -f "$TRANSCRIPT_PATH" ]]; then
    exit 0
fi

# Extract the last turn's AI text: all assistant text blocks after the last user message.
# We read the transcript backwards, collecting assistant text until we hit a user message.
LAST_TURN_TEXT=$(tac "$TRANSCRIPT_PATH" 2>/dev/null | jq -r '
    select(.type == "assistant") | .message.content[]? |
    select(.type == "text") | .text // ""
' 2>/dev/null | head -50) || true

if [[ -z "$LAST_TURN_TEXT" ]]; then
    exit 0
fi

LAST_TURN_LOWER=$(echo "$LAST_TURN_TEXT" | tr '[:upper:]' '[:lower:]')

# Check if logging skills were already invoked in the last turn
LOGGED_DECISION=false
LOGGED_OBSERVATION=false

# Check for Skill tool_use with dialogue-log-decision or dialogue-log-observation
SKILL_USES=$(jq -r 'select(.type == "assistant") | .message.content[]? |
    select(.type == "tool_use" and .name == "Skill") | .input.skill // ""
' "$TRANSCRIPT_PATH" 2>/dev/null | tail -10)

if echo "$SKILL_USES" | grep -q "log-decision"; then
    LOGGED_DECISION=true
fi
if echo "$SKILL_USES" | grep -q "log-observation"; then
    LOGGED_OBSERVATION=true
fi

# Detect decision language in AI output
# These patterns are tuned for AI's analytical voice, not conversational user language
DECISION_FOUND=false
if [[ "$LOGGED_DECISION" == "false" ]]; then
    if echo "$LAST_TURN_LOWER" | grep -qE "(i recommend|my recommendation is|the best (approach|option|strategy) (is|would be))"; then
        DECISION_FOUND=true
    elif echo "$LAST_TURN_LOWER" | grep -qE "(we should (use|adopt|go with|implement|choose)|i.ve (decided|chosen) to)"; then
        DECISION_FOUND=true
    elif echo "$LAST_TURN_LOWER" | grep -qE "(the (decision|conclusion|verdict) is|after (weighing|considering|evaluating).*(i |we ))"; then
        DECISION_FOUND=true
    elif echo "$LAST_TURN_LOWER" | grep -qE "(trade-off|trade off).*(favour|favor|prefer|choose|select)"; then
        DECISION_FOUND=true
    fi
fi

# Detect observation language in AI output
OBSERVATION_FOUND=false
if [[ "$LOGGED_OBSERVATION" == "false" ]]; then
    if echo "$LAST_TURN_LOWER" | grep -qE "(i notice(d)? (that |a |the )|this reveals|this (indicates|suggests|shows) (that |a ))"; then
        OBSERVATION_FOUND=true
    elif echo "$LAST_TURN_LOWER" | grep -qE "(interesting(ly)?|notable|noteworthy|significant(ly)?) .*(finding|pattern|result|gap|discrepancy)"; then
        OBSERVATION_FOUND=true
    elif echo "$LAST_TURN_LOWER" | grep -qE "(key (finding|insight|observation)|worth (highlighting|flagging|noting))"; then
        OBSERVATION_FOUND=true
    fi
fi

# Build directive if anything found
ITEMS=""
if [[ "$DECISION_FOUND" == "true" ]]; then
    ITEMS+="decisions "
fi
if [[ "$OBSERVATION_FOUND" == "true" ]]; then
    ITEMS+="observations "
fi

ITEMS=$(echo "$ITEMS" | xargs)

if [[ -z "$ITEMS" ]]; then
    exit 0
fi

# Block and direct Claude to log
cat << EOF
{"decision": "block", "reason": "AI OUTPUT REVIEW: Your last response contained ${ITEMS} that should be logged. Use dialogue-log-decision and/or dialogue-log-observation skills to record them before continuing. Only log substantive project-level items."}
EOF
