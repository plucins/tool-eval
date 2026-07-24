#!/bin/bash
# resolve-collisions.sh — Detect and resolve task ID collisions
# Part of the Dialogue Framework (FW-052)
#
# Compares local task commits against remote state and renumbers
# any colliding IDs. Designed for offline recovery scenarios.
#
# Usage: resolve-collisions.sh [--dry-run] [--prefix PREFIX]

set -euo pipefail

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:?CLAUDE_PROJECT_DIR must be set}"
TASKS_DIR="${PROJECT_ROOT}/.dialogue/tasks"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DRY_RUN=false
FILTER_PREFIX=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --prefix)
            FILTER_PREFIX="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: resolve-collisions.sh [--dry-run] [--prefix PREFIX]" >&2
            echo "" >&2
            echo "Detects task ID collisions between local and remote branches" >&2
            echo "and renumbers conflicting local tasks." >&2
            echo "" >&2
            echo "Options:" >&2
            echo "  --dry-run     Show what would change without modifying" >&2
            echo "  --prefix      Only check specific prefix (e.g., FW)" >&2
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Must be in a git repo
if ! git -C "$PROJECT_ROOT" rev-parse --git-dir &>/dev/null; then
    echo "Error: Not a git repository" >&2
    exit 1
fi

cd "$PROJECT_ROOT"

# Determine current branch and its remote tracking ref
CURRENT_BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "")
if [[ -z "$CURRENT_BRANCH" ]]; then
    echo "Error: Detached HEAD — cannot determine branch for collision resolution" >&2
    exit 1
fi

REMOTE=$(git config "branch.${CURRENT_BRANCH}.remote" 2>/dev/null || echo "origin")
REMOTE_BRANCH=$(git config "branch.${CURRENT_BRANCH}.merge" 2>/dev/null | \
    sed 's|refs/heads/||' || echo "$CURRENT_BRANCH")
REMOTE_REF="${REMOTE}/${REMOTE_BRANCH}"

# Fetch latest remote state
echo "Fetching remote state from ${REMOTE}..." >&2
if ! git fetch --quiet "$REMOTE" 2>/dev/null; then
    echo "Error: Cannot fetch from ${REMOTE}. Are you online?" >&2
    exit 1
fi

# Verify remote ref exists
if ! git rev-parse "$REMOTE_REF" &>/dev/null; then
    echo "Error: Remote ref $REMOTE_REF does not exist" >&2
    exit 1
fi

# Get merge base
MERGE_BASE=$(git merge-base HEAD "$REMOTE_REF" 2>/dev/null || echo "")
if [[ -z "$MERGE_BASE" ]]; then
    echo "Error: Cannot determine merge base with $REMOTE_REF" >&2
    exit 1
fi

# Find local task files added since merge base
LOCAL_TASK_FILES=()
while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    [[ "$file" == .dialogue/tasks/*.yaml ]] || continue
    LOCAL_TASK_FILES+=("$file")
done < <(git diff --name-only --diff-filter=A "$MERGE_BASE"..HEAD -- .dialogue/tasks/ 2>/dev/null)

if [[ ${#LOCAL_TASK_FILES[@]} -eq 0 ]]; then
    echo "No local task additions found since divergence from $REMOTE_REF" >&2
    exit 0
fi

# Collect remote task IDs from the remote ref (newline-separated list)
REMOTE_IDS=""
while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    path=$(echo "$line" | awk '{print $4}')
    filename=$(basename "$path" .yaml)
    REMOTE_IDS="${REMOTE_IDS}${filename}\n"
done < <(git ls-tree -r "$REMOTE_REF" -- .dialogue/tasks/ 2>/dev/null || true)

# Detect collisions
COLLISIONS=()
for file in "${LOCAL_TASK_FILES[@]}"; do
    task_id=$(basename "$file" .yaml)

    # Filter by prefix if specified
    if [[ -n "$FILTER_PREFIX" ]]; then
        prefix="${task_id%%-*}"
        [[ "$prefix" != "$FILTER_PREFIX" ]] && continue
    fi

    if echo -e "$REMOTE_IDS" | grep -qF "$task_id"; then
        COLLISIONS+=("$task_id")
    fi
done

if [[ ${#COLLISIONS[@]} -eq 0 ]]; then
    echo "No collisions detected." >&2
    exit 0
fi

echo "Collisions detected: ${COLLISIONS[*]}" >&2
echo "" >&2

# Track IDs allocated during this run to avoid dry-run duplicates
ALLOCATED_IDS=""

# Resolve each collision
for old_id in "${COLLISIONS[@]}"; do
    prefix="${old_id%%-*}"

    # Get next available ID (exhaustive scan, fresh fetch already done)
    new_id=$("$SCRIPT_DIR/next-id.sh" "$prefix" --skip-fetch)

    # If this ID was already allocated during this run, increment
    while echo "$ALLOCATED_IDS" | grep -qF "$new_id" 2>/dev/null; do
        new_num=$(echo "$new_id" | sed 's/^[A-Z]*-0*//')
        new_num=$((new_num + 1))
        new_id=$(printf "%s-%03d" "$prefix" "$new_num")
    done
    ALLOCATED_IDS="${ALLOCATED_IDS}${new_id}\n"

    echo "  $old_id -> $new_id" >&2

    if [[ "$DRY_RUN" == "true" ]]; then
        continue
    fi

    OLD_FILE="$TASKS_DIR/${old_id}.yaml"
    NEW_FILE="$TASKS_DIR/${new_id}.yaml"

    # Rename file
    mv "$OLD_FILE" "$NEW_FILE"

    # Update id field inside YAML
    sed -i '' "s/^id:.*$/id: \"${new_id}\"/" "$NEW_FILE"

    # Update blocked_by/blocks cross-references in ALL task files
    for task_file in "$TASKS_DIR"/*.yaml; do
        [[ -f "$task_file" ]] || continue
        [[ "$task_file" == "$NEW_FILE" ]] && continue
        if grep -q "$old_id" "$task_file" 2>/dev/null; then
            sed -i '' "s/${old_id}/${new_id}/g" "$task_file"
            echo "    Updated cross-reference in $(basename "$task_file")" >&2
        fi
    done

    # Stage all task file changes
    git add "$TASKS_DIR/"
done

if [[ "$DRY_RUN" == "true" ]]; then
    echo "" >&2
    echo "Dry run complete. No changes made." >&2
    exit 0
fi

# Create a new commit with the renumbering
COLLISION_LIST=$(printf ", %s" "${COLLISIONS[@]}")
COLLISION_LIST="${COLLISION_LIST:2}"  # Remove leading ", "
git commit -m "Resolve task ID collisions: ${COLLISION_LIST}" --quiet

echo "" >&2
echo "Collisions resolved. You can now push:" >&2
echo "  git push" >&2
