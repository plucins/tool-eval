#!/bin/bash
# session-start.sh — Check if project has initialised Dialogue
# Part of the Dialogue Framework plugin
# SessionStart hook

# IMPORTANT: THIS IS SUPERSEDED BY session-start-guided.sh FOR GUIDED SESSIONS
# ALWAYS USE THE GUIDED VARIANT NO MORE MODIFICATIONS SHOULD BE MADE HERE

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/hook-lib.sh"

# Use Claude's project directory
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:?CLAUDE_PROJECT_DIR must be set}"

DIALOGUE_DIR="${PROJECT_ROOT}/.dialogue"
CONFIG_FILE="${DIALOGUE_DIR}/config.yaml"
TASKS_DIR="${DIALOGUE_DIR}/tasks"
TASKS_FILE="${DIALOGUE_DIR}/tasks.yaml"  # Legacy single-file location

# Session memo (per-user for merge-friendly multi-user workflows)
USERNAME="${USER:-$(whoami 2>/dev/null || echo 'unknown')}"
SESSION_MEMO="${DIALOGUE_DIR}/session-memo-${USERNAME}.yaml"

# Check status and output simple systemMessage (CLAUDE.md handles instructions)
if [[ ! -d "$DIALOGUE_DIR" ]]; then
    echo "[dialogue-hook] NOT INITIALISED" >&2
    echo '{"continue": true, "systemMessage": "Dialogue Framework: NOT INITIALISED. Run `dialogue init` to set up."}'
    exit 0
fi

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "[dialogue-hook] PARTIAL" >&2
    echo '{"continue": true, "systemMessage": "Dialogue Framework: Missing config.yaml file. Run `dialogue init` to re-initialize."}'
    exit 0
fi

# Count tasks from both new (tasks/) and legacy (tasks.yaml) structures
in_progress=0
ready=0
in_progress_tasks=""

if [[ -d "$TASKS_DIR" ]] && [[ -n "$(ls -A "$TASKS_DIR" 2>/dev/null)" ]]; then
    # New structure: individual task files
    for task_file in "$TASKS_DIR"/*.yaml; do
        [[ -f "$task_file" ]] || continue
        status=$(grep -m1 "^status:" "$task_file" 2>/dev/null | awk '{print $2}' || echo "")
        if [[ "$status" == "IN_PROGRESS" ]]; then
            ((++in_progress))
            id=$(grep -m1 "^id:" "$task_file" | awk '{print $2}' | tr -d '"')
            title=$(grep -m1 "^title:" "$task_file" | sed 's/^title: *//' | tr -d '"')
            if [[ $in_progress -le 5 ]]; then
                [[ -n "$in_progress_tasks" ]] && in_progress_tasks+="; "
                in_progress_tasks+="${id}: ${title}"
            fi
        elif [[ "$status" == "READY" ]]; then
            ((++ready))
        fi
    done
elif [[ -f "$TASKS_FILE" ]]; then
    # Legacy structure: single tasks.yaml file
    in_progress=$(grep -c "status: IN_PROGRESS" "$TASKS_FILE" 2>/dev/null || echo "0")
    ready=$(grep -c "status: READY" "$TASKS_FILE" 2>/dev/null || echo "0")

    if [[ "$in_progress" -gt 0 ]]; then
        in_progress_tasks=$(awk '
            /^  - id:/ { id = $3; gsub(/"/, "", id) }
            /^    title:/ { title = substr($0, index($0, ":")+2); gsub(/"/, "", title) }
            /^    status: IN_PROGRESS/ { print id ": " title }
        ' "$TASKS_FILE" | head -5 | tr '\n' ';' | sed 's/;$//')
    fi
fi

# Build task status message
task_msg=""
if [[ $in_progress -gt 0 || $ready -gt 0 ]]; then
    if [[ -n "$in_progress_tasks" ]]; then
        task_msg="${in_progress} in-progress [${in_progress_tasks}], ${ready} ready"
    else
        task_msg="${in_progress} in-progress, ${ready} ready"
    fi
fi

# Read session memo if it exists (per-user file)
session_context=""
if [[ -f "$SESSION_MEMO" ]]; then
    # Extract key fields from session memo
    last_session=$(grep -m1 "^last_session:" "$SESSION_MEMO" 2>/dev/null | sed 's/^last_session: *//' | tr -d '"' || echo "")
    active_focus=$(grep -m1 "^active_focus:" "$SESSION_MEMO" 2>/dev/null | sed 's/^active_focus: *//' | tr -d '"' || echo "")
    open_questions=$(grep -m1 "^open_questions:" "$SESSION_MEMO" 2>/dev/null | sed 's/^open_questions: *//' | tr -d '"' || echo "")

    if [[ -n "$active_focus" ]]; then
        session_context="Previous focus: ${active_focus}"
        if [[ -n "$open_questions" && "$open_questions" != "[]" && "$open_questions" != "~" ]]; then
            session_context+="; Open questions pending"
        fi
    fi
fi

# Build final system message
system_msg="Dialogue Framework"
if [[ -n "$task_msg" ]]; then
    system_msg+=": ${task_msg}"
else
    system_msg+=": (no tasks)"
fi
if [[ -n "$session_context" ]]; then
    system_msg+=". ${session_context}"
fi

echo "[dialogue-hook] INITIALISED: user=${USERNAME}, tasks=${in_progress}/${ready}" >&2
echo "{\"continue\": true, \"systemMessage\": \"${system_msg}\"}"
exit 0
