#!/bin/bash
# process-delegation-routing.sh — Process delegation trigger detection
# Part of the Dialogue Framework plugin
# UserPromptSubmit hook — detects process-related user prompts and injects
# delegation instructions for the Dialogue Agent to invoke the Process Orchestrator.
#
# Separate from user-prompt-submit-guided.sh for clean separation of concerns.

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/hook-lib.sh"

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-}"
DIALOGUE_DIR="${PROJECT_ROOT}/.dialogue"
CONFIG_FILE="${DIALOGUE_DIR}/config.yaml"

# Check agent_architecture config (default: two-agent)
AGENT_ARCH="two-agent"
if [[ -f "$CONFIG_FILE" ]]; then
    arch=$(grep -m1 "^agent_architecture:" "$CONFIG_FILE" 2>/dev/null | awk '{print $2}' | tr -d '"' || echo "")
    if [[ -n "$arch" ]]; then
        AGENT_ARCH="$arch"
    fi
fi

# Skip if single-agent architecture
if [[ "$AGENT_ARCH" == "single" ]]; then
    exit 0
fi

# Read user prompt
INPUT=$(cat)
PROMPT=$(echo "$INPUT" | jq -r '.prompt // ""')

if [[ -z "$PROMPT" ]]; then
    exit 0
fi

PROMPT_LOWER=$(echo "$PROMPT" | tr '[:upper:]' '[:lower:]')

DELEGATE=false

# Process delegation indicators
if echo "$PROMPT_LOWER" | grep -qE "(ready to move|phase gate|phase transition|assess readiness|process status|coordination check|what phase)"; then
    DELEGATE=true
fi

# Capability flow triggers
if echo "$PROMPT_LOWER" | grep -qE "(design.*(process|flow|capability)|execute.*(process|flow)|run.*(process|flow))"; then
    DELEGATE=true
fi

if [[ "$DELEGATE" != "true" ]]; then
    exit 0
fi

jq -n '{
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": "<dialogue-instruction>PROCESS DELEGATION: Delegate this to the Process Orchestrator agent via Task tool. Provide current conversation context.</dialogue-instruction>"
    }
}'
