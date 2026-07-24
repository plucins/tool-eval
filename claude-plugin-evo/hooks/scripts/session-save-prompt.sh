#!/bin/bash
# session-save-prompt.sh — Stop hook to prompt session memo saving
# Part of the Dialogue Framework
#
# This hook runs when a session stops. It checks:
# 1. Whether stop_hook_active is true (prevent infinite loops)
# 2. Whether substantive work was done (decisions or observations logged)
# 3. Whether session memo was already updated today
#
# If work was done but memo not updated, blocks and reminds Claude to save.
# Non-blocking if no work done or memo already current.

set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/hook-lib.sh"

# Read JSON input from stdin
INPUT=$(cat)

# Check if we're already in a stop hook continuation
STOP_HOOK_ACTIVE=$(echo "$INPUT" | grep -o '"stop_hook_active"[[:space:]]*:[[:space:]]*true' || true)
if [[ -n "$STOP_HOOK_ACTIVE" ]]; then
    # Already continuing from a stop hook, don't block again
    exit 0
fi

# Use Claude's project directory environment variable
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-}"
if [[ -z "$PROJECT_ROOT" ]]; then
    exit 0
fi

LOG_DIR="${PROJECT_ROOT}/.dialogue/logs"
DECISIONS_DIR="${LOG_DIR}/decisions"
OBSERVATIONS_DIR="${LOG_DIR}/observations"
DIALOGUE_DIR="${PROJECT_ROOT}/.dialogue"

# Get current username
USERNAME="${USER:-$(whoami)}"
SESSION_MEMO="${DIALOGUE_DIR}/session-memo-${USERNAME}.yaml"

# Get today's date
TODAY=$(date -u +"%Y%m%d")
TODAY_ISO=$(date -u +"%Y-%m-%d")

# Check if substantive work was done today
check_substantive_work() {
    local work_found=0

    if [[ -d "$DECISIONS_DIR" ]]; then
        local decisions
        decisions=$(find "$DECISIONS_DIR" -name "DEC-${TODAY}-*.yaml" -type f 2>/dev/null | wc -l | tr -d ' ')
        if [[ "$decisions" -gt 0 ]]; then
            work_found=1
        fi
    fi

    if [[ -d "$OBSERVATIONS_DIR" ]]; then
        local observations
        observations=$(find "$OBSERVATIONS_DIR" -name "OBS-${TODAY}-*.yaml" -type f 2>/dev/null | wc -l | tr -d ' ')
        if [[ "$observations" -gt 0 ]]; then
            work_found=1
        fi
    fi

    return $((1 - work_found))
}

# Check if session memo was updated today
check_memo_current() {
    if [[ ! -f "$SESSION_MEMO" ]]; then
        return 1
    fi

    # Check if last_session contains today's date
    if grep -q "last_session:.*${TODAY_ISO}" "$SESSION_MEMO" 2>/dev/null; then
        return 0
    fi

    return 1
}

# Main logic
main() {
    # Skip if no dialogue directory
    if [[ ! -d "$DIALOGUE_DIR" ]]; then
        exit 0
    fi

    # Check if memo already current
    if check_memo_current; then
        exit 0
    fi

    # Check if substantive work was done
    if ! check_substantive_work; then
        exit 0
    fi

    # Work done but memo not current - block and remind
    cat << 'EOF'
{"decision": "block", "reason": "Substantive work was done this session. Use the /save-session skill to save session context before stopping."}
EOF
}

main
exit 0
