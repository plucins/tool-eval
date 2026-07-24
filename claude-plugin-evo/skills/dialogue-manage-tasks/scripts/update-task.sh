#!/bin/bash
# update-task.sh — Update an existing task file
# Part of the Dialogue Framework (FW-062)
# Usage: update-task.sh <TASK_ID> [options]
#
# Required:
#   TASK_ID             Task ID to update (e.g., FW-062) — never accepts file paths
#
# Status shortcuts:
#   --start             Set status=IN_PROGRESS
#   --complete          Set status=COMPLETED + completed timestamp
#   --block             Set status=BLOCKED
#   --ready             Set status=READY
#
# Metadata:
#   --status <STATUS>   BACKLOG|READY|IN_PROGRESS|BLOCKED|COMPLETED|CANCELLED
#   --priority <PRIO>   CRITICAL|HIGH|MEDIUM|LOW
#   --type <TYPE>       CAPABILITY|SCHEMA|DOCUMENT|RESEARCH|DEBT|DECISION
#   --phase <N>         1-7
#   --title <TITLE>     Update title
#
# Dependencies:
#   --add-blocked-by <IDs>     Add to blocked_by (comma-separated)
#   --remove-blocked-by <IDs>  Remove from blocked_by (comma-separated)
#   --add-blocks <IDs>         Add to blocks (comma-separated)
#   --remove-blocks <IDs>      Remove from blocks (comma-separated)
#
# Notes:
#   --append-note <TEXT>       Append timestamped note
#
# Content replacement (interactive confirmation by default):
#   --set-description <TEXT>   Replace description (shows existing, prompts confirm)
#   --set-objective <TEXT>     Replace objective (shows existing, prompts confirm)
#   --set-rationale <TEXT>     Replace rationale (shows existing, prompts confirm)
#
# Git:
#   --no-commit         Skip auto-commit
#   --no-push           Commit but skip push
#
# Safety:
#   --force             Skip confirmation prompts
#   --dry-run           Preview changes without writing

set -euo pipefail

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:?CLAUDE_PROJECT_DIR must be set}"
TASKS_DIR="${PROJECT_ROOT}/.dialogue/tasks"

# --- Phase 1: Argument parsing and validation ---

if [[ $# -lt 1 ]]; then
    echo "Usage: update-task.sh <TASK_ID> [options]" >&2
    echo "" >&2
    echo "Status shortcuts:" >&2
    echo "  --start            Set status=IN_PROGRESS" >&2
    echo "  --complete         Set status=COMPLETED + completed timestamp" >&2
    echo "  --block            Set status=BLOCKED" >&2
    echo "  --ready            Set status=READY" >&2
    echo "" >&2
    echo "Metadata:" >&2
    echo "  --status <STATUS>  BACKLOG|READY|IN_PROGRESS|BLOCKED|COMPLETED|CANCELLED" >&2
    echo "  --priority <PRIO>  CRITICAL|HIGH|MEDIUM|LOW" >&2
    echo "  --type <TYPE>      CAPABILITY|SCHEMA|DOCUMENT|RESEARCH|DEBT|DECISION" >&2
    echo "  --phase <N>        1-7" >&2
    echo "  --title <TITLE>    Update title" >&2
    echo "" >&2
    echo "Dependencies:" >&2
    echo "  --add-blocked-by <IDs>     Add to blocked_by (comma-separated)" >&2
    echo "  --remove-blocked-by <IDs>  Remove from blocked_by" >&2
    echo "  --add-blocks <IDs>         Add to blocks (comma-separated)" >&2
    echo "  --remove-blocks <IDs>      Remove from blocks" >&2
    echo "" >&2
    echo "Notes:" >&2
    echo "  --append-note <TEXT>  Append timestamped note" >&2
    echo "" >&2
    echo "Content replacement (prompts for confirmation):" >&2
    echo "  --set-description <TEXT>   Replace description" >&2
    echo "  --set-objective <TEXT>     Replace objective" >&2
    echo "  --set-rationale <TEXT>     Replace rationale" >&2
    echo "" >&2
    echo "Git:" >&2
    echo "  --no-commit   Skip auto-commit" >&2
    echo "  --no-push     Commit but skip push" >&2
    echo "" >&2
    echo "Safety:" >&2
    echo "  --force       Skip confirmation prompts" >&2
    echo "  --dry-run     Preview changes without writing" >&2
    exit 1
fi

TASK_ID="$1"
shift

# Security: Validate task ID format (never accept paths)
if [[ ! "$TASK_ID" =~ ^[A-Z]{2,4}-[0-9]{3}$ ]]; then
    echo "Error: Invalid task ID '$TASK_ID'" >&2
    echo "Task ID must match pattern PREFIX-NNN (e.g., FW-001)" >&2
    exit 1
fi

# Parse options
NEW_STATUS=""
NEW_PRIORITY=""
NEW_TYPE=""
NEW_PHASE=""
NEW_TITLE=""
ADD_BLOCKED_BY=""
REMOVE_BLOCKED_BY=""
ADD_BLOCKS=""
REMOVE_BLOCKS=""
APPEND_NOTE=""
SET_DESCRIPTION=""
SET_OBJECTIVE=""
SET_RATIONALE=""
NO_COMMIT=false
NO_PUSH=false
FORCE=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --start)
            NEW_STATUS="IN_PROGRESS"
            shift
            ;;
        --complete)
            NEW_STATUS="COMPLETED"
            shift
            ;;
        --block)
            NEW_STATUS="BLOCKED"
            shift
            ;;
        --ready)
            NEW_STATUS="READY"
            shift
            ;;
        --status)
            NEW_STATUS="$2"
            shift 2
            ;;
        --priority)
            NEW_PRIORITY="$2"
            shift 2
            ;;
        --type)
            NEW_TYPE="$2"
            shift 2
            ;;
        --phase)
            NEW_PHASE="$2"
            shift 2
            ;;
        --title)
            NEW_TITLE="$2"
            shift 2
            ;;
        --add-blocked-by)
            ADD_BLOCKED_BY="$2"
            shift 2
            ;;
        --remove-blocked-by)
            REMOVE_BLOCKED_BY="$2"
            shift 2
            ;;
        --add-blocks)
            ADD_BLOCKS="$2"
            shift 2
            ;;
        --remove-blocks)
            REMOVE_BLOCKS="$2"
            shift 2
            ;;
        --append-note)
            APPEND_NOTE="$2"
            shift 2
            ;;
        --set-description)
            SET_DESCRIPTION="$2"
            shift 2
            ;;
        --set-objective)
            SET_OBJECTIVE="$2"
            shift 2
            ;;
        --set-rationale)
            SET_RATIONALE="$2"
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
        --force)
            FORCE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Validate status if provided
if [[ -n "$NEW_STATUS" ]]; then
    case "$NEW_STATUS" in
        BACKLOG|READY|IN_PROGRESS|BLOCKED|COMPLETED|CANCELLED) ;;
        *)
            echo "Error: Invalid status '$NEW_STATUS'" >&2
            echo "Valid: BACKLOG, READY, IN_PROGRESS, BLOCKED, COMPLETED, CANCELLED" >&2
            exit 1
            ;;
    esac
fi

# Validate type if provided
if [[ -n "$NEW_TYPE" ]]; then
    case "$NEW_TYPE" in
        CAPABILITY|SCHEMA|DOCUMENT|RESEARCH|DEBT|DECISION) ;;
        *)
            echo "Error: Invalid type '$NEW_TYPE'" >&2
            echo "Valid: CAPABILITY, SCHEMA, DOCUMENT, RESEARCH, DEBT, DECISION" >&2
            exit 1
            ;;
    esac
fi

# Validate priority if provided
if [[ -n "$NEW_PRIORITY" ]]; then
    case "$NEW_PRIORITY" in
        CRITICAL|HIGH|MEDIUM|LOW) ;;
        *)
            echo "Error: Invalid priority '$NEW_PRIORITY'" >&2
            echo "Valid: CRITICAL, HIGH, MEDIUM, LOW" >&2
            exit 1
            ;;
    esac
fi

# Validate phase if provided
if [[ -n "$NEW_PHASE" ]]; then
    if [[ ! "$NEW_PHASE" =~ ^[1-7]$ ]]; then
        echo "Error: Phase must be 1-7" >&2
        exit 1
    fi
fi

# --- Phase 2: Task file existence check ---

TASK_FILE="$TASKS_DIR/${TASK_ID}.yaml"
if [[ ! -f "$TASK_FILE" ]]; then
    echo "Error: Task $TASK_ID not found at $TASK_FILE" >&2
    exit 1
fi

# --- Phase 3: Read existing task YAML ---

# Helper: Extract simple field from YAML
extract_field() {
    local file="$1"
    local field="$2"
    grep "^${field}:" "$file" 2>/dev/null | sed "s/^${field}:[[:space:]]*//" | tr -d '"' || echo ""
}

# Helper: Extract YAML array field as comma-separated string
extract_array_field() {
    local file="$1"
    local field="$2"
    local line
    line=$(grep "^${field}:" "$file" 2>/dev/null || echo "")
    if [[ -z "$line" ]]; then
        echo ""
        return
    fi
    # Handle inline array format: [item1, item2]
    echo "$line" | sed "s/^${field}:[[:space:]]*//" | tr -d '[]"' | sed 's/, */,/g' | sed 's/^,//;s/,$//'
}

# Helper: Extract multi-line field (literal block scalar)
extract_multiline_field() {
    local file="$1"
    local field="$2"
    local in_field=false
    local content=""
    while IFS= read -r line || [[ -n "$line" ]]; do
        if [[ "$in_field" == "true" ]]; then
            # Check if line starts with indent (part of block)
            if [[ "$line" =~ ^[[:space:]] ]]; then
                # Remove leading two spaces (YAML block indent)
                content+="${line#  }"$'\n'
            else
                # New field started, stop
                break
            fi
        elif [[ "$line" =~ ^${field}:[[:space:]]*\| ]]; then
            in_field=true
        elif [[ "$line" =~ ^${field}:[[:space:]]*\"(.*)\"$ ]]; then
            # Single-line quoted value
            echo "${BASH_REMATCH[1]}"
            return
        elif [[ "$line" =~ ^${field}:[[:space:]]*(.+)$ ]]; then
            # Single-line unquoted value
            echo "${BASH_REMATCH[1]}"
            return
        fi
    done < "$file"
    # Remove trailing newline
    echo -n "$content" | sed 's/[[:space:]]*$//'
}

# Read current values
CURRENT_TITLE=$(extract_field "$TASK_FILE" "title")
CURRENT_STATUS=$(extract_field "$TASK_FILE" "status")
CURRENT_TYPE=$(extract_field "$TASK_FILE" "type")
CURRENT_PRIORITY=$(extract_field "$TASK_FILE" "priority")
CURRENT_PHASE=$(extract_field "$TASK_FILE" "phase")
CURRENT_CREATED=$(extract_field "$TASK_FILE" "created")
CURRENT_UPDATED=$(extract_field "$TASK_FILE" "updated")
CURRENT_COMPLETED=$(extract_field "$TASK_FILE" "completed")
CURRENT_BLOCKED_BY=$(extract_array_field "$TASK_FILE" "blocked_by")
CURRENT_BLOCKS=$(extract_array_field "$TASK_FILE" "blocks")
CURRENT_DESCRIPTION=$(extract_multiline_field "$TASK_FILE" "description")
CURRENT_OBJECTIVE=$(extract_multiline_field "$TASK_FILE" "objective")
CURRENT_RATIONALE=$(extract_multiline_field "$TASK_FILE" "rationale")
CURRENT_NOTES=$(extract_multiline_field "$TASK_FILE" "notes")

# --- Phase 4: Apply updates (merge changes) ---

# Helper: Convert comma-separated IDs to YAML array
to_yaml_array() {
    local input="$1"
    if [[ -z "$input" ]]; then
        echo "[]"
        return
    fi
    local result="["
    local first=true
    IFS=',' read -ra items <<< "$input"
    for item in "${items[@]}"; do
        item=$(echo "$item" | xargs)  # trim whitespace
        [[ -z "$item" ]] && continue
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

# Helper: Merge arrays (add items not already present)
merge_arrays() {
    local existing="$1"
    local to_add="$2"
    local result=""

    # Start with existing items
    result="$existing"

    # Add new items if not present
    IFS=',' read -ra add_items <<< "$to_add"
    for item in "${add_items[@]}"; do
        item=$(echo "$item" | xargs)
        [[ -z "$item" ]] && continue
        # Check if already present
        if [[ ! ",$result," =~ ,"$item", ]]; then
            if [[ -n "$result" ]]; then
                result+=",$item"
            else
                result="$item"
            fi
        fi
    done
    echo "$result"
}

# Helper: Remove items from array
remove_from_array() {
    local existing="$1"
    local to_remove="$2"
    local result=""

    IFS=',' read -ra existing_items <<< "$existing"
    IFS=',' read -ra remove_items <<< "$to_remove"

    for item in "${existing_items[@]}"; do
        item=$(echo "$item" | xargs)
        [[ -z "$item" ]] && continue
        local should_remove=false
        for rem in "${remove_items[@]}"; do
            rem=$(echo "$rem" | xargs)
            if [[ "$item" == "$rem" ]]; then
                should_remove=true
                break
            fi
        done
        if [[ "$should_remove" == "false" ]]; then
            if [[ -n "$result" ]]; then
                result+=",$item"
            else
                result="$item"
            fi
        fi
    done
    echo "$result"
}

# Apply changes
FINAL_TITLE="${NEW_TITLE:-$CURRENT_TITLE}"
FINAL_STATUS="${NEW_STATUS:-$CURRENT_STATUS}"
FINAL_TYPE="${NEW_TYPE:-$CURRENT_TYPE}"
FINAL_PRIORITY="${NEW_PRIORITY:-$CURRENT_PRIORITY}"
FINAL_PHASE="${NEW_PHASE:-$CURRENT_PHASE}"
FINAL_DESCRIPTION="$CURRENT_DESCRIPTION"
FINAL_OBJECTIVE="$CURRENT_OBJECTIVE"
FINAL_RATIONALE="$CURRENT_RATIONALE"
FINAL_NOTES="$CURRENT_NOTES"
FINAL_COMPLETED="$CURRENT_COMPLETED"

# Process blocked_by changes
FINAL_BLOCKED_BY="$CURRENT_BLOCKED_BY"
if [[ -n "$ADD_BLOCKED_BY" ]]; then
    FINAL_BLOCKED_BY=$(merge_arrays "$FINAL_BLOCKED_BY" "$ADD_BLOCKED_BY")
fi
if [[ -n "$REMOVE_BLOCKED_BY" ]]; then
    FINAL_BLOCKED_BY=$(remove_from_array "$FINAL_BLOCKED_BY" "$REMOVE_BLOCKED_BY")
fi

# Process blocks changes
FINAL_BLOCKS="$CURRENT_BLOCKS"
if [[ -n "$ADD_BLOCKS" ]]; then
    FINAL_BLOCKS=$(merge_arrays "$FINAL_BLOCKS" "$ADD_BLOCKS")
fi
if [[ -n "$REMOVE_BLOCKS" ]]; then
    FINAL_BLOCKS=$(remove_from_array "$FINAL_BLOCKS" "$REMOVE_BLOCKS")
fi

# Handle content replacement with confirmation
confirm_replace() {
    local field_name="$1"
    local current_content="$2"
    local new_content="$3"

    if [[ "$FORCE" == "true" ]]; then
        return 0  # Approved
    fi

    echo "" >&2
    echo "Current ${field_name}:" >&2
    echo "---" >&2
    echo "$current_content" >&2
    echo "---" >&2
    echo "" >&2
    echo "Replace with new content? [y/N]: " >&2
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        return 0  # Approved
    else
        return 5  # Rejected
    fi
}

if [[ -n "$SET_DESCRIPTION" ]]; then
    if [[ -n "$CURRENT_DESCRIPTION" ]] && [[ "$FORCE" != "true" ]] && [[ "$DRY_RUN" != "true" ]]; then
        if ! confirm_replace "description" "$CURRENT_DESCRIPTION" "$SET_DESCRIPTION"; then
            echo "Description replacement cancelled" >&2
            exit 5
        fi
    fi
    FINAL_DESCRIPTION="$SET_DESCRIPTION"
fi

if [[ -n "$SET_OBJECTIVE" ]]; then
    if [[ -n "$CURRENT_OBJECTIVE" ]] && [[ "$FORCE" != "true" ]] && [[ "$DRY_RUN" != "true" ]]; then
        if ! confirm_replace "objective" "$CURRENT_OBJECTIVE" "$SET_OBJECTIVE"; then
            echo "Objective replacement cancelled" >&2
            exit 5
        fi
    fi
    FINAL_OBJECTIVE="$SET_OBJECTIVE"
fi

if [[ -n "$SET_RATIONALE" ]]; then
    if [[ -n "$CURRENT_RATIONALE" ]] && [[ "$FORCE" != "true" ]] && [[ "$DRY_RUN" != "true" ]]; then
        if ! confirm_replace "rationale" "$CURRENT_RATIONALE" "$SET_RATIONALE"; then
            echo "Rationale replacement cancelled" >&2
            exit 5
        fi
    fi
    FINAL_RATIONALE="$SET_RATIONALE"
fi

# Handle note appending
if [[ -n "$APPEND_NOTE" ]]; then
    NOTE_DATE=$(date -u +"%d %B %Y")
    if [[ -n "$FINAL_NOTES" ]]; then
        FINAL_NOTES="${FINAL_NOTES}

${NOTE_DATE}: ${APPEND_NOTE}"
    else
        FINAL_NOTES="${NOTE_DATE}: ${APPEND_NOTE}"
    fi
fi

# Handle completed timestamp for COMPLETED status
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
if [[ "$FINAL_STATUS" == "COMPLETED" && -z "$FINAL_COMPLETED" ]]; then
    FINAL_COMPLETED="$TIMESTAMP"
fi

# Add automatic audit note for content replacements
if [[ -n "$SET_DESCRIPTION" || -n "$SET_OBJECTIVE" || -n "$SET_RATIONALE" ]]; then
    AUDIT_DATE=$(date -u +"%d %B %Y")
    AUDIT_PARTS=()
    [[ -n "$SET_DESCRIPTION" ]] && AUDIT_PARTS+=("description")
    [[ -n "$SET_OBJECTIVE" ]] && AUDIT_PARTS+=("objective")
    [[ -n "$SET_RATIONALE" ]] && AUDIT_PARTS+=("rationale")
    AUDIT_FIELDS=$(IFS=', '; echo "${AUDIT_PARTS[*]}")
    AUDIT_NOTE="${AUDIT_DATE}: ${AUDIT_FIELDS} replaced via update-task.sh"
    if [[ -n "$FINAL_NOTES" ]]; then
        FINAL_NOTES="${FINAL_NOTES}

${AUDIT_NOTE}"
    else
        FINAL_NOTES="$AUDIT_NOTE"
    fi
fi

# --- Dry run output ---
if [[ "$DRY_RUN" == "true" ]]; then
    echo "=== DRY RUN: Changes to $TASK_ID ===" >&2
    [[ "$FINAL_TITLE" != "$CURRENT_TITLE" ]] && echo "title: $CURRENT_TITLE -> $FINAL_TITLE" >&2
    [[ "$FINAL_STATUS" != "$CURRENT_STATUS" ]] && echo "status: $CURRENT_STATUS -> $FINAL_STATUS" >&2
    [[ "$FINAL_TYPE" != "$CURRENT_TYPE" ]] && echo "type: $CURRENT_TYPE -> $FINAL_TYPE" >&2
    [[ "$FINAL_PRIORITY" != "$CURRENT_PRIORITY" ]] && echo "priority: $CURRENT_PRIORITY -> $FINAL_PRIORITY" >&2
    [[ "$FINAL_PHASE" != "$CURRENT_PHASE" ]] && echo "phase: $CURRENT_PHASE -> $FINAL_PHASE" >&2
    [[ "$FINAL_BLOCKED_BY" != "$CURRENT_BLOCKED_BY" ]] && echo "blocked_by: [$CURRENT_BLOCKED_BY] -> [$FINAL_BLOCKED_BY]" >&2
    [[ "$FINAL_BLOCKS" != "$CURRENT_BLOCKS" ]] && echo "blocks: [$CURRENT_BLOCKS] -> [$FINAL_BLOCKS]" >&2
    [[ -n "$SET_DESCRIPTION" ]] && echo "description: <replaced>" >&2
    [[ -n "$SET_OBJECTIVE" ]] && echo "objective: <replaced>" >&2
    [[ -n "$SET_RATIONALE" ]] && echo "rationale: <replaced>" >&2
    [[ -n "$APPEND_NOTE" ]] && echo "notes: <appended>" >&2
    echo "updated: $CURRENT_UPDATED -> $TIMESTAMP" >&2
    [[ "$FINAL_STATUS" == "COMPLETED" && -z "$CURRENT_COMPLETED" ]] && echo "completed: <set to $TIMESTAMP>" >&2
    echo "=== END DRY RUN ===" >&2
    exit 0
fi

# --- Phase 5: Write updated file ---

{
    echo "id: \"$TASK_ID\""
    echo "title: \"$FINAL_TITLE\""
    echo "status: $FINAL_STATUS"
    echo "created: \"$CURRENT_CREATED\""
    echo "updated: \"$TIMESTAMP\""

    if [[ -n "$FINAL_COMPLETED" ]]; then
        echo "completed: \"$FINAL_COMPLETED\""
    fi

    if [[ -n "$FINAL_TYPE" ]]; then
        echo "type: $FINAL_TYPE"
    fi

    if [[ -n "$FINAL_PHASE" ]]; then
        echo "phase: $FINAL_PHASE"
    fi

    if [[ -n "$FINAL_PRIORITY" ]]; then
        echo "priority: $FINAL_PRIORITY"
    fi

    if [[ -n "$FINAL_DESCRIPTION" ]]; then
        echo "description: |"
        echo "$FINAL_DESCRIPTION" | sed 's/^/  /'
    fi

    if [[ -n "$FINAL_OBJECTIVE" ]]; then
        echo "objective: \"$FINAL_OBJECTIVE\""
    fi

    if [[ -n "$FINAL_RATIONALE" ]]; then
        echo "rationale: |"
        echo "$FINAL_RATIONALE" | sed 's/^/  /'
    fi

    echo "blocked_by: $(to_yaml_array "$FINAL_BLOCKED_BY")"
    echo "blocks: $(to_yaml_array "$FINAL_BLOCKS")"

    if [[ -n "$FINAL_NOTES" ]]; then
        echo "notes: |"
        echo "$FINAL_NOTES" | sed 's/^/  /'
    fi
} > "$TASK_FILE"

echo "$TASK_ID"

# --- Phase 6: Auto-commit and push ---

if [[ "$NO_COMMIT" == "true" ]]; then
    exit 0
fi

GIT_AVAILABLE=false
CAN_PUSH=false
CURRENT_BRANCH=""
REMOTE=""

if git -C "$PROJECT_ROOT" rev-parse --git-dir &>/dev/null; then
    GIT_AVAILABLE=true
    CURRENT_BRANCH=$(git -C "$PROJECT_ROOT" symbolic-ref --short HEAD 2>/dev/null || echo "")
    if [[ -n "$CURRENT_BRANCH" ]]; then
        REMOTE=$(git -C "$PROJECT_ROOT" config "branch.${CURRENT_BRANCH}.remote" 2>/dev/null || echo "")
        if [[ -n "$REMOTE" ]]; then
            CAN_PUSH=true
        fi
    fi
fi

if [[ "$GIT_AVAILABLE" == "true" && -n "$CURRENT_BRANCH" ]]; then
    # Build commit message
    COMMIT_MSG="${TASK_ID}: Update"
    [[ -n "$NEW_STATUS" ]] && COMMIT_MSG="${TASK_ID}: ${NEW_STATUS}"
    [[ -n "$NEW_TITLE" ]] && COMMIT_MSG="${TASK_ID}: ${NEW_TITLE}"

    if git -C "$PROJECT_ROOT" add "$TASK_FILE" && \
       git -C "$PROJECT_ROOT" commit -m "$COMMIT_MSG" --quiet 2>/dev/null; then
        echo "[dialogue] Committed ${TASK_ID}" >&2

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
                fi
            fi
        fi
    else
        echo "[dialogue] Warning: Auto-commit failed or no changes to commit." >&2
    fi
fi
