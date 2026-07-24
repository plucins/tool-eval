#!/bin/bash
# check-git-sync.sh — Check git sync status for team mode
# Part of the Dialogue Framework (FW-040)
#
# Performs quick fetch and compares local vs remote.
# Outputs: synced | ahead | behind | diverged | not-git | no-remote
#
# Options:
#   --quiet    Suppress stderr messages (for session start integration)

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/hook-lib.sh"

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:?CLAUDE_PROJECT_DIR must be set}"
QUIET=false

# Parse options
while [[ $# -gt 0 ]]; do
    case "$1" in
        --quiet)
            QUIET=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# Check if we're in a git repo
if ! git -C "$PROJECT_ROOT" rev-parse --git-dir &>/dev/null; then
    echo "not-git"
    exit 0
fi

cd "$PROJECT_ROOT"

# Get current branch
BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "")
if [[ -z "$BRANCH" ]]; then
    # Detached HEAD state
    echo "synced"
    exit 0
fi

# Get tracking remote
REMOTE=$(git config "branch.${BRANCH}.remote" 2>/dev/null || echo "")
if [[ -z "$REMOTE" ]]; then
    echo "no-remote"
    exit 0
fi

REMOTE_BRANCH=$(git config "branch.${BRANCH}.merge" 2>/dev/null | sed 's|refs/heads/||' || echo "$BRANCH")

# Quick fetch (timeout after 5 seconds, fail silently)
if ! timeout 5 git fetch "$REMOTE" "$REMOTE_BRANCH" --quiet 2>/dev/null; then
    if [[ "$QUIET" != "true" ]]; then
        echo "[dialogue] Warning: Could not fetch from remote" >&2
    fi
    # Proceed with potentially stale data
fi

# Compare local and remote
LOCAL=$(git rev-parse HEAD 2>/dev/null || echo "")
REMOTE_REF="${REMOTE}/${REMOTE_BRANCH}"
REMOTE_HEAD=$(git rev-parse "$REMOTE_REF" 2>/dev/null || echo "")

if [[ -z "$LOCAL" ]] || [[ -z "$REMOTE_HEAD" ]]; then
    echo "synced"
    exit 0
fi

if [[ "$LOCAL" == "$REMOTE_HEAD" ]]; then
    echo "synced"
    exit 0
fi

# Check relationship
BASE=$(git merge-base "$LOCAL" "$REMOTE_HEAD" 2>/dev/null || echo "")

if [[ "$BASE" == "$REMOTE_HEAD" ]]; then
    # Remote is ancestor of local = we're ahead
    echo "ahead"
elif [[ "$BASE" == "$LOCAL" ]]; then
    # Local is ancestor of remote = we're behind
    echo "behind"
else
    # Neither is ancestor = diverged
    echo "diverged"
fi
