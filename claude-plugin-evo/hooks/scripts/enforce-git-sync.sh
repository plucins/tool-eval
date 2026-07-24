#!/bin/bash
# enforce-git-sync.sh — Enforce git sync on session startup (FW-057)
# Part of the Dialogue Framework plugin
#
# Wraps check-git-sync.sh: checks status, then pulls when behind or diverged.
# Designed to run at SessionStart for all modes (solo and team).
#
# Outputs JSON: { "status": "...", "message": "...", "commits": N, "completed_tasks": [...] }
#   status:  synced | ahead | pulled | conflict | not-git | no-remote | offline
#   message: Human-readable summary (empty for synced/ahead)
#   commits: Number of commits pulled (0 if not pulled)
#   completed_tasks: Tasks that were IN_PROGRESS locally but COMPLETED after pull
#
# Options:
#   --quiet    Suppress stderr messages

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/hook-lib.sh"

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:?CLAUDE_PROJECT_DIR must be set}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QUIET=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --quiet) QUIET=true; shift ;;
        *) shift ;;
    esac
done

log_stderr() {
    if [[ "$QUIET" != "true" ]]; then
        echo "[dialogue-sync] $1" >&2
    fi
}

output_json() {
    local status="$1"
    local message="$2"
    local commits="${3:-0}"
    local completed_tasks="${4:-}"
    if [[ -n "$completed_tasks" ]]; then
        jq -n --arg s "$status" --arg m "$message" --argjson c "$commits" --argjson ct "$completed_tasks" \
            '{ "status": $s, "message": $m, "commits": $c, "completed_tasks": $ct }'
    else
        jq -n --arg s "$status" --arg m "$message" --argjson c "$commits" \
            '{ "status": $s, "message": $m, "commits": $c, "completed_tasks": [] }'
    fi
}

# Check for active rebase/merge state from a previous failed sync
GIT_DIR=$(git -C "$PROJECT_ROOT" rev-parse --git-dir 2>/dev/null || echo "")
if [[ -n "$GIT_DIR" ]]; then
    if [[ -d "${GIT_DIR}/rebase-merge" ]] || [[ -d "${GIT_DIR}/rebase-apply" ]]; then
        CONFLICTED_FILES=$(git -C "$PROJECT_ROOT" diff --name-only --diff-filter=U 2>/dev/null | head -10)
        CONFLICT_COUNT=$(git -C "$PROJECT_ROOT" diff --name-only --diff-filter=U 2>/dev/null | wc -l | tr -d ' ')
        output_json "conflict" "Rebase in progress with ${CONFLICT_COUNT} conflicted file(s): ${CONFLICTED_FILES}" 0
        exit 0
    elif [[ -f "${GIT_DIR}/MERGE_HEAD" ]]; then
        CONFLICTED_FILES=$(git -C "$PROJECT_ROOT" diff --name-only --diff-filter=U 2>/dev/null | head -10)
        CONFLICT_COUNT=$(git -C "$PROJECT_ROOT" diff --name-only --diff-filter=U 2>/dev/null | wc -l | tr -d ' ')
        output_json "conflict" "Merge in progress with ${CONFLICT_COUNT} conflicted file(s): ${CONFLICTED_FILES}" 0
        exit 0
    fi
fi

# Delegate status check to check-git-sync.sh
if [[ ! -x "${SCRIPT_DIR}/check-git-sync.sh" ]]; then
    log_stderr "check-git-sync.sh not found"
    output_json "synced" "" 0
    exit 0
fi

SYNC_STATUS=$("${SCRIPT_DIR}/check-git-sync.sh" --quiet 2>/dev/null || echo "synced")

case "$SYNC_STATUS" in
    synced)
        output_json "synced" "" 0
        exit 0
        ;;
    ahead)
        output_json "ahead" "" 0
        exit 0
        ;;
    not-git)
        output_json "not-git" "" 0
        exit 0
        ;;
    no-remote)
        output_json "no-remote" "" 0
        exit 0
        ;;
esac

# At this point status is "behind" or "diverged" — attempt pull
cd "$PROJECT_ROOT"

# Snapshot IN_PROGRESS tasks before pulling — to detect tasks completed by others
TASKS_DIR="${PROJECT_ROOT}/.dialogue/tasks"
PRE_PULL_IN_PROGRESS=""
if [[ -d "$TASKS_DIR" ]]; then
    for task_file in "$TASKS_DIR"/*.yaml; do
        [[ -f "$task_file" ]] || continue
        status=$(grep -m1 "^status:" "$task_file" 2>/dev/null | awk '{print $2}' || echo "")
        if [[ "$status" == "IN_PROGRESS" ]]; then
            task_id=$(grep -m1 "^id:" "$task_file" 2>/dev/null | awk '{print $2}' | tr -d '"' || echo "")
            [[ -n "$task_id" ]] && PRE_PULL_IN_PROGRESS+="${task_id} "
        fi
    done
fi

# Count commits we're behind before pulling
REMOTE=$(git config "branch.$(git symbolic-ref --short HEAD).remote" 2>/dev/null || echo "origin")
REMOTE_BRANCH=$(git config "branch.$(git symbolic-ref --short HEAD).merge" 2>/dev/null | sed 's|refs/heads/||' || echo "$(git symbolic-ref --short HEAD)")
BEHIND_COUNT=$(git rev-list --count HEAD.."${REMOTE}/${REMOTE_BRANCH}" 2>/dev/null || echo "0")

log_stderr "Local is ${SYNC_STATUS} origin by ${BEHIND_COUNT} commit(s). Pulling..."

# Attempt git pull (--rebase: replay local commits on top of origin for linear history)
PULL_OUTPUT=$(git pull --rebase --autostash 2>&1) || {
    PULL_EXIT=$?
    # Check if it's a rebase conflict (unmerged files or rebase-merge dir present)
    if git diff --name-only --diff-filter=U 2>/dev/null | grep -q . || [[ -d "$(git rev-parse --git-dir)/rebase-merge" ]]; then
        CONFLICTED_FILES=$(git diff --name-only --diff-filter=U 2>/dev/null | head -10)
        CONFLICT_COUNT=$(git diff --name-only --diff-filter=U 2>/dev/null | wc -l | tr -d ' ')
        log_stderr "Rebase produced ${CONFLICT_COUNT} conflicted file(s)"
        output_json "conflict" "Rebase from origin produced conflicts in ${CONFLICT_COUNT} file(s): ${CONFLICTED_FILES}" 0
        exit 0
    fi
    # Some other pull failure
    log_stderr "Pull failed: ${PULL_OUTPUT}"
    output_json "offline" "" 0
    exit 0
}

# Pull succeeded — check for tasks completed by others
COMPLETED_TASKS_JSON="[]"
if [[ -n "$PRE_PULL_IN_PROGRESS" ]]; then
    COMPLETED_LIST=""
    for task_id in $PRE_PULL_IN_PROGRESS; do
        task_file="${TASKS_DIR}/${task_id}.yaml"
        [[ -f "$task_file" ]] || continue
        new_status=$(grep -m1 "^status:" "$task_file" 2>/dev/null | awk '{print $2}' || echo "")
        if [[ "$new_status" == "COMPLETED" ]]; then
            task_title=$(grep -m1 "^title:" "$task_file" 2>/dev/null | sed 's/^title: *//' | tr -d '"' || echo "")
            COMPLETED_LIST+="${task_id}:${task_title},"
            log_stderr "Task ${task_id} was completed on origin"
        fi
    done
    if [[ -n "$COMPLETED_LIST" ]]; then
        # Build JSON array: [{"id":"FW-054","title":"..."},...]
        COMPLETED_TASKS_JSON=$(echo "$COMPLETED_LIST" | sed 's/,$//' | tr ',' '\n' | while IFS=: read -r id title; do
            jq -n --arg id "$id" --arg title "$title" '{"id":$id,"title":$title}'
        done | jq -s '.')
    fi
fi

log_stderr "Pulled ${BEHIND_COUNT} commit(s) from origin"
output_json "pulled" "Synced with origin — pulled ${BEHIND_COUNT} commit(s)" "$BEHIND_COUNT" "$COMPLETED_TASKS_JSON"
