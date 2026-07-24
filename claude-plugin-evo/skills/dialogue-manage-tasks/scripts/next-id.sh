#!/bin/bash
# next-id.sh — Get the next available task ID for a prefix
# Part of the Dialogue Framework (FW-052)
# Usage: next-id.sh <PREFIX> [--skip-fetch] [--local-only]
#   PREFIX:       Task ID prefix (SH, CD, FW, DOC, VAL, or custom 2-4 letter prefix)
#   --skip-fetch: Skip git fetch (caller has already fetched)
#   --local-only: Only scan local filesystem (offline/non-git fallback)
#
# Scans all sources for existing IDs:
#   1. Local filesystem (.dialogue/tasks/)
#   2. All local git branches
#   3. All remote git branches (after fetching)
# Returns the next available ID from the union of all found IDs.

set -euo pipefail

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:?CLAUDE_PROJECT_DIR must be set}"
TASKS_DIR="${PROJECT_ROOT}/.dialogue/tasks"

# --- Argument parsing ---
if [[ $# -lt 1 ]]; then
    echo "Usage: next-id.sh <PREFIX> [--skip-fetch] [--local-only]" >&2
    echo "  PREFIX:       2-4 uppercase letters (e.g., SH, FW, DOC)" >&2
    echo "  --skip-fetch: Skip git fetch (caller has already fetched)" >&2
    echo "  --local-only: Only scan local filesystem" >&2
    exit 1
fi

PREFIX="$1"
shift

SKIP_FETCH=false
LOCAL_ONLY=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --skip-fetch) SKIP_FETCH=true; shift ;;
        --local-only) LOCAL_ONLY=true; shift ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Validate prefix format (2-4 uppercase letters)
if [[ ! "$PREFIX" =~ ^[A-Z]{2,4}$ ]]; then
    echo "Error: PREFIX must be 2-4 uppercase letters (e.g., SH, FW, DOC)" >&2
    exit 1
fi

# Ensure tasks directory exists
mkdir -p "$TASKS_DIR"

# --- Source 1: Local filesystem scan (always) ---
collect_local_ids() {
    local prefix="$1"
    for file in "$TASKS_DIR"/${prefix}-*.yaml; do
        [[ -f "$file" ]] || continue
        local filename
        filename=$(basename "$file" .yaml)
        if [[ "$filename" =~ ^${prefix}-([0-9]+)$ ]]; then
            echo "${BASH_REMATCH[1]}"
        fi
    done
}

# --- Source 2: Git tree scan across all branches ---
collect_git_ids() {
    local prefix="$1"

    # Check if we're in a git repo
    if ! git -C "$PROJECT_ROOT" rev-parse --git-dir &>/dev/null; then
        return
    fi

    cd "$PROJECT_ROOT"

    # Fetch if not skipped
    if [[ "$SKIP_FETCH" != "true" ]]; then
        git fetch --quiet origin 2>/dev/null || true
    fi

    # Collect all refs: local branches + remote branches
    local refs=()
    while IFS= read -r ref; do
        [[ -n "$ref" ]] && refs+=("$ref")
    done < <(git for-each-ref --format='%(refname)' refs/heads/ refs/remotes/ 2>/dev/null)

    # Also include HEAD (covers detached HEAD and current working state)
    refs+=("HEAD")

    # Deduplicate by tree hash for .dialogue/tasks/ to avoid scanning identical trees
    local seen_trees=""
    for ref in "${refs[@]}"; do
        local tree_hash
        tree_hash=$(git rev-parse "${ref}:.dialogue/tasks" 2>/dev/null) || continue

        # Skip if we've already scanned this tree
        if echo "$seen_trees" | grep -qF "$tree_hash" 2>/dev/null; then
            continue
        fi
        seen_trees="${seen_trees}${tree_hash}\n"

        # List task files matching PREFIX in this tree
        git ls-tree "$ref" -- ".dialogue/tasks/" 2>/dev/null | while read -r _mode _type _hash path; do
            local filename
            filename=$(basename "$path" .yaml)
            if [[ "$filename" =~ ^${prefix}-([0-9]+)$ ]]; then
                echo "${BASH_REMATCH[1]}"
            fi
        done
    done
}

# --- Union all IDs and find max ---
max_num=0

while IFS= read -r num; do
    [[ -z "$num" ]] && continue
    num=$((10#$num))  # Remove leading zeros
    if [[ $num -gt $max_num ]]; then
        max_num=$num
    fi
done < <(
    collect_local_ids "$PREFIX"
    if [[ "$LOCAL_ONLY" != "true" ]]; then
        collect_git_ids "$PREFIX"
    fi
)

# Next ID is max + 1, zero-padded to 3 digits
next_num=$((max_num + 1))
next_id=$(printf "%s-%03d" "$PREFIX" "$next_num")

echo "$next_id"
