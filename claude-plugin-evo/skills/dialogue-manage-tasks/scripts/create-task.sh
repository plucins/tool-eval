#!/bin/bash
# create-task.sh — Create a new task file
# Part of the Dialogue Framework (FW-052)
# Usage: create-task.sh <PREFIX> <TITLE> [options]
#
# Required:
#   PREFIX              Task ID prefix (SH, CD, FW, DOC, VAL)
#   TITLE               Task title (brief description)
#
# Options:
#   --status <STATUS>   Initial status [default: BACKLOG]
#   --type <TYPE>       Task type (CAPABILITY, SCHEMA, DOCUMENT, RESEARCH, DEBT, DECISION)
#   --priority <PRIO>   Priority (CRITICAL, HIGH, MEDIUM, LOW) [default: MEDIUM]
#   --phase <N>         SDLC phase (1-7)
#   --description <D>   Full description
#   --objective <O>     Success criteria
#   --rationale <R>     Why this is needed
#   --blocked-by <IDS>  Comma-separated IDs of blocking tasks
#   --blocks <IDS>      Comma-separated IDs this blocks
#   --notes <N>         Initial notes
#   --id <ID>           Use specific ID instead of auto-generating
#   --no-commit         Skip auto-commit and push
#   --no-push           Commit but skip push

set -euo pipefail

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:?CLAUDE_PROJECT_DIR must be set}"
TASKS_DIR="${PROJECT_ROOT}/.dialogue/tasks"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Validate minimum arguments
if [[ $# -lt 2 ]]; then
    echo "Usage: create-task.sh <PREFIX> <TITLE> [options]" >&2
    echo "" >&2
    echo "Required:" >&2
    echo "  PREFIX              Task ID prefix (SH, CD, FW, DOC, VAL)" >&2
    echo "  TITLE               Task title" >&2
    echo "" >&2
    echo "Options:" >&2
    echo "  --status <STATUS>   Initial status [default: BACKLOG]" >&2
    echo "  --type <TYPE>       Task type (CAPABILITY, SCHEMA, etc.)" >&2
    echo "  --priority <PRIO>   Priority [default: MEDIUM]" >&2
    echo "  --phase <N>         SDLC phase (1-7)" >&2
    echo "  --description <D>   Full description" >&2
    echo "  --objective <O>     Success criteria" >&2
    echo "  --rationale <R>     Why needed" >&2
    echo "  --blocked-by <IDS>  Comma-separated blocking task IDs" >&2
    echo "  --blocks <IDS>      Comma-separated IDs this blocks" >&2
    echo "  --notes <N>         Initial notes" >&2
    echo "  --id <ID>           Use specific ID (skip auto-generation)" >&2
    echo "  --no-commit         Skip auto-commit and push" >&2
    echo "  --no-push           Commit but skip push" >&2
    exit 1
fi

PREFIX="$1"
TITLE="$2"
shift 2

# Defaults
STATUS="BACKLOG"
TYPE=""
PRIORITY="MEDIUM"
PHASE=""
DESCRIPTION=""
OBJECTIVE=""
RATIONALE=""
BLOCKED_BY=""
BLOCKS=""
NOTES=""
EXPLICIT_ID=""
NO_COMMIT=false
NO_PUSH=false

# Parse options
while [[ $# -gt 0 ]]; do
    case "$1" in
        --status)
            STATUS="$2"
            shift 2
            ;;
        --type)
            TYPE="$2"
            shift 2
            ;;
        --priority)
            PRIORITY="$2"
            shift 2
            ;;
        --phase)
            PHASE="$2"
            shift 2
            ;;
        --description)
            DESCRIPTION="$2"
            shift 2
            ;;
        --objective)
            OBJECTIVE="$2"
            shift 2
            ;;
        --rationale)
            RATIONALE="$2"
            shift 2
            ;;
        --blocked-by)
            BLOCKED_BY="$2"
            shift 2
            ;;
        --blocks)
            BLOCKS="$2"
            shift 2
            ;;
        --notes)
            NOTES="$2"
            shift 2
            ;;
        --id)
            EXPLICIT_ID="$2"
            shift 2
            ;;
        --no-commit)
            NO_COMMIT=true
            shift
            ;;
        --no-push)
            NO_PUSH=true
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Validate status
case "$STATUS" in
    BACKLOG|READY|IN_PROGRESS|BLOCKED|COMPLETED|CANCELLED) ;;
    *)
        echo "Error: Invalid status '$STATUS'" >&2
        echo "Valid: BACKLOG, READY, IN_PROGRESS, BLOCKED, COMPLETED, CANCELLED" >&2
        exit 1
        ;;
esac

# Validate type if provided
if [[ -n "$TYPE" ]]; then
    case "$TYPE" in
        CAPABILITY|SCHEMA|DOCUMENT|RESEARCH|DEBT|DECISION) ;;
        *)
            echo "Error: Invalid type '$TYPE'" >&2
            echo "Valid: CAPABILITY, SCHEMA, DOCUMENT, RESEARCH, DEBT, DECISION" >&2
            exit 1
            ;;
    esac
fi

# Validate priority
case "$PRIORITY" in
    CRITICAL|HIGH|MEDIUM|LOW) ;;
    *)
        echo "Error: Invalid priority '$PRIORITY'" >&2
        echo "Valid: CRITICAL, HIGH, MEDIUM, LOW" >&2
        exit 1
        ;;
esac

# Validate phase if provided
if [[ -n "$PHASE" ]]; then
    if [[ ! "$PHASE" =~ ^[1-7]$ ]]; then
        echo "Error: Phase must be 1-7" >&2
        exit 1
    fi
fi

# Ensure tasks directory exists
mkdir -p "$TASKS_DIR"

# --- Phase 1: Pre-fetch and git state detection ---
GIT_AVAILABLE=false
CAN_PUSH=false
CURRENT_BRANCH=""
REMOTE=""
FETCHED=false

if git -C "$PROJECT_ROOT" rev-parse --git-dir &>/dev/null; then
    GIT_AVAILABLE=true

    CURRENT_BRANCH=$(git -C "$PROJECT_ROOT" symbolic-ref --short HEAD 2>/dev/null || echo "")
    if [[ -n "$CURRENT_BRANCH" ]]; then
        REMOTE=$(git -C "$PROJECT_ROOT" config "branch.${CURRENT_BRANCH}.remote" 2>/dev/null || echo "")
        if [[ -n "$REMOTE" ]]; then
            CAN_PUSH=true
            # Fetch once for both ID scanning and later push
            if git -C "$PROJECT_ROOT" fetch --quiet "$REMOTE" 2>/dev/null; then
                FETCHED=true
            else
                echo "[dialogue] Warning: Could not fetch from remote (offline?)" >&2
            fi
        fi
    fi
fi

# --- Phase 2: Generate or validate ID ---
if [[ -n "$EXPLICIT_ID" ]]; then
    TASK_ID="$EXPLICIT_ID"
    # Validate explicit ID format
    if [[ ! "$TASK_ID" =~ ^[A-Z]{2,4}-[0-9]{3}$ ]]; then
        echo "Error: ID must match pattern PREFIX-NNN (e.g., FW-001)" >&2
        exit 1
    fi
    # Check for conflicts across all sources
    if [[ "$GIT_AVAILABLE" == "true" ]]; then
        EXPLICIT_PREFIX="${TASK_ID%%-*}"
        if [[ "$FETCHED" == "true" ]]; then
            NEXT_AVAILABLE=$("$SCRIPT_DIR/next-id.sh" "$EXPLICIT_PREFIX" --skip-fetch)
        else
            NEXT_AVAILABLE=$("$SCRIPT_DIR/next-id.sh" "$EXPLICIT_PREFIX" --local-only)
        fi
        # Compare: if explicit ID < next available, it likely exists somewhere
        EXPLICIT_NUM=$(echo "$TASK_ID" | sed 's/^[A-Z]*-0*//')
        NEXT_NUM=$(echo "$NEXT_AVAILABLE" | sed 's/^[A-Z]*-0*//')
        if [[ -n "$EXPLICIT_NUM" && -n "$NEXT_NUM" && "$EXPLICIT_NUM" -lt "$NEXT_NUM" ]]; then
            echo "[dialogue] Warning: $TASK_ID may already exist in another branch. Next available: $NEXT_AVAILABLE" >&2
        fi
    fi
else
    if [[ "$GIT_AVAILABLE" == "true" ]]; then
        TASK_ID=$("$SCRIPT_DIR/next-id.sh" "$PREFIX" --skip-fetch)
    else
        TASK_ID=$("$SCRIPT_DIR/next-id.sh" "$PREFIX" --local-only)
    fi
fi

# --- Phase 3: Local existence check ---
TASK_FILE="$TASKS_DIR/${TASK_ID}.yaml"
if [[ -f "$TASK_FILE" ]]; then
    echo "Error: Task $TASK_ID already exists" >&2
    exit 1
fi

# --- Phase 4: Generate timestamp ---
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Helper: Convert comma-separated IDs to YAML array
to_yaml_array() {
    local input="$1"
    if [[ -z "$input" ]]; then
        echo "[]"
        return
    fi
    # Split by comma and format as YAML array
    local result="["
    local first=true
    IFS=',' read -ra items <<< "$input"
    for item in "${items[@]}"; do
        item=$(echo "$item" | xargs)  # trim whitespace
        if [[ "$first" == "true" ]]; then
            first=false
        else
            result+=", "
        fi
        result+="\"$item\""
    done
    result+="]"
    echo "$result"
}

# --- Phase 5: Build YAML content ---
{
    echo "id: \"$TASK_ID\""
    echo "title: \"$TITLE\""
    echo "status: $STATUS"
    echo "created: \"$TIMESTAMP\""
    echo "updated: \"$TIMESTAMP\""

    if [[ -n "$TYPE" ]]; then
        echo "type: $TYPE"
    fi

    if [[ -n "$PHASE" ]]; then
        echo "phase: $PHASE"
    fi

    echo "priority: $PRIORITY"

    if [[ -n "$DESCRIPTION" ]]; then
        echo "description: |"
        # Indent each line of description
        echo "$DESCRIPTION" | sed 's/^/  /'
    fi

    if [[ -n "$OBJECTIVE" ]]; then
        echo "objective: \"$OBJECTIVE\""
    fi

    if [[ -n "$RATIONALE" ]]; then
        echo "rationale: |"
        echo "$RATIONALE" | sed 's/^/  /'
    fi

    echo "blocked_by: $(to_yaml_array "$BLOCKED_BY")"
    echo "blocks: $(to_yaml_array "$BLOCKS")"

    if [[ -n "$NOTES" ]]; then
        echo "notes: |"
        echo "$NOTES" | sed 's/^/  /'
    else
        # Add default creation note
        created_date=$(date -u +"%d %B %Y")
        echo "notes: |"
        echo "  Created $created_date."
    fi
} > "$TASK_FILE"

# Output the created task ID
echo "$TASK_ID"

# --- Phase 6: Auto-commit and push ---
if [[ "$NO_COMMIT" == "true" ]]; then
    # Preserve old-style team mode reminder for manual workflow
    if [[ -n "${CLAUDE_PLUGIN_ROOT:-}" ]]; then
        DETECT_SCRIPT="${CLAUDE_PLUGIN_ROOT}/hooks/scripts/detect-team-mode.sh"
        if [[ -x "$DETECT_SCRIPT" ]]; then
            TEAM_MODE=$("$DETECT_SCRIPT" 2>/dev/null || echo "solo")
            if [[ "$TEAM_MODE" == "team" ]]; then
                echo "[team] Remember to commit and push for team visibility." >&2
            fi
        fi
    fi
    exit 0
fi

if [[ "$GIT_AVAILABLE" == "true" && -n "$CURRENT_BRANCH" ]]; then
    # Auto-commit (include all pending .dialogue/ changes for clean working tree)
    if git -C "$PROJECT_ROOT" add "$TASK_FILE" && \
       { git -C "$PROJECT_ROOT" add "${PROJECT_ROOT}/.dialogue/" 2>/dev/null || true; } && \
       git -C "$PROJECT_ROOT" commit -m "${TASK_ID}: ${TITLE}" --quiet 2>/dev/null; then
        echo "[dialogue] Committed ${TASK_ID}" >&2

        # Auto-push (unless --no-push or solo mode)
        if [[ "$NO_PUSH" != "true" && "$CAN_PUSH" == "true" ]]; then
            SHOULD_PUSH=true

            # Check team mode — solo mode skips push
            if [[ -n "${CLAUDE_PLUGIN_ROOT:-}" ]]; then
                DETECT_SCRIPT="${CLAUDE_PLUGIN_ROOT}/hooks/scripts/detect-team-mode.sh"
                if [[ -x "$DETECT_SCRIPT" ]]; then
                    TEAM_MODE=$("$DETECT_SCRIPT" 2>/dev/null || echo "solo")
                    if [[ "$TEAM_MODE" == "solo" ]]; then
                        SHOULD_PUSH=false
                    fi
                fi
            fi

            if [[ "$SHOULD_PUSH" == "true" ]]; then
                # Pull --rebase to integrate any remote changes before pushing
                # --autostash handles unstaged changes in the working tree
                if ! git -C "$PROJECT_ROOT" pull --rebase --autostash --quiet 2>/dev/null; then
                    echo "[dialogue] Warning: Pull --rebase failed. Task committed locally." >&2
                    echo "[dialogue] Resolve conflicts then push manually: git push" >&2
                elif git -C "$PROJECT_ROOT" push --quiet 2>/dev/null; then
                    echo "[dialogue] Pushed ${TASK_ID} to ${REMOTE}" >&2
                else
                    echo "[dialogue] Warning: Push failed. Task committed locally." >&2
                    echo "[dialogue] If this is due to a conflict, run: resolve-collisions.sh" >&2
                    echo "[dialogue] Otherwise, push manually when online: git push" >&2
                fi
            fi
        fi
    else
        echo "[dialogue] Warning: Auto-commit failed. Task file created at ${TASK_FILE}" >&2
    fi
elif [[ "$GIT_AVAILABLE" != "true" ]]; then
    echo "[dialogue] Not in a git repo — task created locally only" >&2
elif [[ -z "$CURRENT_BRANCH" ]]; then
    echo "[dialogue] Detached HEAD — task created locally, auto-commit skipped" >&2
fi
