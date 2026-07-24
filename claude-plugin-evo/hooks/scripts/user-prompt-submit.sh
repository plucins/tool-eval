#!/bin/bash
# UserPromptSubmit hook: Inject minimal framework context signals.
#
# Detects framework-relevant patterns in user prompts and injects
# short hints to help Claude recognise when to invoke framework components.
#
# Design: Minimal and quiet. No output for non-framework prompts.


# IMPORTANT: THIS IS SUPERSEDED BY user-prompt-submit-guided.sh FOR GUIDED PROMPTS
# ALWAYS USE THE GUIDED VARIANT NO MORE MODIFICATIONS SHOULD BE MADE HERE


set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/hook-lib.sh"

# Read JSON input
INPUT=$(cat)
PROMPT=$(echo "$INPUT" | jq -r '.prompt // ""')

if [[ -z "$PROMPT" ]]; then
    exit 0
fi

PROMPT_LOWER=$(echo "$PROMPT" | tr '[:upper:]' '[:lower:]')
SIGNALS=""

# Decision indicators
if echo "$PROMPT_LOWER" | grep -qE "(i decided|let'?s go with|decision is|i chose|we'?ll use|going with|decided to|make a decision)"; then
    SIGNALS="$SIGNALS decision-capture"
fi

# Observation indicators
if echo "$PROMPT_LOWER" | grep -qE "(i noticed|i observed|here'?s an observation|worth noting|i see that|observation:|noticed that)"; then
    SIGNALS="$SIGNALS observation-capture"
fi

# Task references (SH-NNN, FW-NNN, CD-NNN)
if echo "$PROMPT" | grep -qiE "\b(SH|FW|CD)-[0-9]{3}\b"; then
    SIGNALS="$SIGNALS task-context"
fi

# Reference resolution requests (THY, REF, ADR, DEC, OBS patterns)
if echo "$PROMPT" | grep -qiE "\b(THY|REF|STR|ADR)-[0-9]{3}\b"; then
    SIGNALS="$SIGNALS resolve-reference"
fi
if echo "$PROMPT" | grep -qE "\b(DEC|OBS)-[0-9]{8}-[0-9]{6}\b"; then
    SIGNALS="$SIGNALS resolve-reference"
fi

# Phase-specific work indicators
if echo "$PROMPT_LOWER" | grep -qE "(phase\s*1|initiation|opportunity|stakeholder)"; then
    SIGNALS="$SIGNALS phase-1"
elif echo "$PROMPT_LOWER" | grep -qE "(phase\s*2|planning|estimate|schedule)"; then
    SIGNALS="$SIGNALS phase-2"
elif echo "$PROMPT_LOWER" | grep -qE "(phase\s*3|requirements?|specification)"; then
    SIGNALS="$SIGNALS phase-3"
elif echo "$PROMPT_LOWER" | grep -qE "(phase\s*4|design|architecture)"; then
    SIGNALS="$SIGNALS phase-4"
elif echo "$PROMPT_LOWER" | grep -qE "(phase\s*5|implement|coding|develop)"; then
    SIGNALS="$SIGNALS phase-5"
fi

# Elicitation requests
if echo "$PROMPT_LOWER" | grep -qE "(elicit|extract|gather|capture).*(knowledge|context|understanding)"; then
    SIGNALS="$SIGNALS structured-elicit"
fi

# ADR creation
if echo "$PROMPT_LOWER" | grep -qE "(create|write|draft).*(adr|architecture decision)"; then
    SIGNALS="$SIGNALS create-adr"
fi

# Task candidate detection
# Only if no existing task ID referenced (avoid double-signaling)
if ! echo "$PROMPT" | grep -qiE "\b(SH|FW|CD)-[0-9]{3}\b"; then
    # Substantive project-level work patterns
    # Creation: implement, build, create, develop (+ noun suggesting scope)
    # Research: investigate, research, explore, analyse, understand
    # Design: design, architect, plan, prototype
    if echo "$PROMPT_LOWER" | grep -qE "(implement|build|develop|create).*(feature|capability|system|component|integration|module|service|api|framework|plugin)"; then
        SIGNALS="$SIGNALS task-candidate"
    elif echo "$PROMPT_LOWER" | grep -qE "(investigate|research|explore|analy[sz]e|understand).*(how|why|what|whether|if|issue|problem|approach|option)"; then
        SIGNALS="$SIGNALS task-candidate"
    elif echo "$PROMPT_LOWER" | grep -qE "(design|architect|plan|prototype).*(system|component|approach|solution|integration|interface)"; then
        SIGNALS="$SIGNALS task-candidate"
    # Explicit work tracking language
    elif echo "$PROMPT_LOWER" | grep -qE "(add to|track|capture|record).*(backlog|task|task list|roadmap)"; then
        SIGNALS="$SIGNALS task-candidate"
    # "I need to" / "we need to" + substantive verb
    elif echo "$PROMPT_LOWER" | grep -qE "(i|we) need to.*(implement|build|create|design|investigate|research|develop|integrate)"; then
        SIGNALS="$SIGNALS task-candidate"
    fi
fi

# Trim leading space
SIGNALS=$(echo "$SIGNALS" | xargs)

if [[ -z "$SIGNALS" ]]; then
    # No framework relevance detected - stay quiet
    exit 0
fi

# Output minimal context hint
jq -n --arg signals "$SIGNALS" '{
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": "<dialogue-signals>\($signals)</dialogue-signals>"
    }
}'
