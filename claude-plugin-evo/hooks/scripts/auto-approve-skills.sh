#!/bin/bash
# PreToolUse hook: Auto-approve Dialogue Framework skills
#
# Checks if a Skill tool invocation is for a dialogue-framework skill
# and auto-approves it to avoid permission prompts.
#
# Also checks for upstream changes to .dialogue/tasks/ when using
# task management skills, to warn about potential ID conflicts.
#
# Design: Only approve skills from the dialogue-framework plugin.

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/hook-lib.sh"

# Read JSON input
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // ""')
SKILL_NAME=$(echo "$INPUT" | jq -r '.tool_input.skill // ""')

# Only process Skill tools
if [[ "$TOOL_NAME" != "Skill" ]]; then
    exit 0
fi

# Check for upstream task changes when using task management skill
check_upstream_tasks() {
    local project_dir="${CLAUDE_PROJECT_DIR:-}"
    [[ -z "$project_dir" ]] && return 1

    cd "$project_dir" || return 1

    # Quick fetch (suppress errors for offline/no-remote scenarios)
    if ! git fetch --quiet origin 2>/dev/null; then
        return 1
    fi

    # Get the default branch (main or master)
    local default_branch
    default_branch=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@') || default_branch="main"

    # Compare local vs remote for .dialogue/tasks/
    local local_tree remote_tree
    local_tree=$(git rev-parse "HEAD:.dialogue/tasks" 2>/dev/null) || return 1
    remote_tree=$(git rev-parse "origin/${default_branch}:.dialogue/tasks" 2>/dev/null) || return 1

    if [[ "$local_tree" != "$remote_tree" ]]; then
        return 0  # Upstream has changes
    fi

    return 1  # No upstream changes
}

# Auto-approve dialogue-framework skills
if [[ "$SKILL_NAME" == dialogue-framework:* ]] || [[ "$SKILL_NAME" == "dialogue-"* ]]; then

    # For task management skills, check for upstream changes
    if [[ "$SKILL_NAME" == *"manage-tasks"* ]]; then
        if check_upstream_tasks; then
            jq -n --arg skill "$SKILL_NAME" '{
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                    "permissionDecisionReason": ("Auto-approved with upstream warning: " + $skill),
                    "additionalContext": "WARNING: Remote has changes to .dialogue/tasks/ that you do not have locally. Consider running git pull before creating new tasks to avoid ID conflicts. If you already have unpushed task commits, run resolve-collisions.sh to check for ID conflicts."
                }
            }'
            exit 0
        fi
    fi

    # Standard approval (no upstream issues)
    jq -n --arg skill "$SKILL_NAME" '{
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": ("Auto-approved dialogue-framework skill: " + $skill)
        }
    }'
    exit 0
fi

# Not a dialogue-framework skill - allow normal permission flow
exit 0
