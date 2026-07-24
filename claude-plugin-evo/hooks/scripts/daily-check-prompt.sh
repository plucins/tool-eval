#!/bin/bash
# daily-check-prompt.sh — Stop hook to remind about daily check assessments
# Part of the Dialogue Framework
#
# This hook runs when a session stops. It checks:
# 1. Whether substantive work was done (decisions or observations logged)
# 2. Whether a daily check has already been done today
#
# If work was done but no daily check exists, outputs a reminder.
# Non-blocking: always exits 0.

set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/hook-lib.sh"

# Use Claude's project directory environment variable
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-}"
if [[ -z "$PROJECT_ROOT" ]]; then
    # Silently exit if not in a project context
    exit 0
fi

LOG_DIR="${PROJECT_ROOT}/.dialogue/logs"
ASSESSMENTS_DIR="${LOG_DIR}/assessments"
DECISIONS_DIR="${LOG_DIR}/decisions"
OBSERVATIONS_DIR="${LOG_DIR}/observations"

# Get today's date in the format used by IDs (YYYYMMDD)
TODAY=$(date -u +"%Y%m%d")

# Check if a daily check assessment exists for today
check_daily_assessment_exists() {
    if [[ ! -d "$ASSESSMENTS_DIR" ]]; then
        return 1
    fi

    # Look for ASSESS-{TODAY}-*.yaml files
    local found
    found=$(find "$ASSESSMENTS_DIR" -name "ASSESS-${TODAY}-*.yaml" -type f 2>/dev/null | head -1)

    if [[ -n "$found" ]]; then
        return 0
    fi
    return 1
}

# Check if substantive work was done today (decisions or observations logged)
check_substantive_work() {
    local work_found=0

    # Check for decisions logged today
    if [[ -d "$DECISIONS_DIR" ]]; then
        local decisions
        decisions=$(find "$DECISIONS_DIR" -name "DEC-${TODAY}-*.yaml" -type f 2>/dev/null | wc -l | tr -d ' ')
        if [[ "$decisions" -gt 0 ]]; then
            work_found=1
        fi
    fi

    # Check for observations logged today
    if [[ -d "$OBSERVATIONS_DIR" ]]; then
        local observations
        observations=$(find "$OBSERVATIONS_DIR" -name "OBS-${TODAY}-*.yaml" -type f 2>/dev/null | wc -l | tr -d ' ')
        if [[ "$observations" -gt 0 ]]; then
            work_found=1
        fi
    fi

    return $((1 - work_found))
}

# Main logic
main() {
    # Skip if no dialogue directory
    if [[ ! -d "$LOG_DIR" ]]; then
        exit 0
    fi

    # Check if daily assessment already done
    if check_daily_assessment_exists; then
        # Already done today, no reminder needed
        exit 0
    fi

    # Check if substantive work was done
    if ! check_substantive_work; then
        # No substantive work logged, skip reminder
        exit 0
    fi

    # Substantive work done but no daily check - output reminder
    # Using a format that will be visible in hook output
    cat << 'EOF'

---
Daily Check Reminder: You've done substantive work today but haven't logged a daily check assessment.

Consider running `/daily-check` to capture your developer experience signals.
This helps track patterns and surface systematic issues early.

Quick questions: progress, learning, support, agency, blockers, context-switching, unclear requirements.
---

EOF
}

main
exit 0
