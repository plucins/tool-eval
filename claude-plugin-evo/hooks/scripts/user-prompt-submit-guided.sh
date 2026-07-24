#!/bin/bash
# user-prompt-submit-guided.sh — Guided variant: directive instructions not just signals
# Part of the Dialogue Framework plugin
# UserPromptSubmit hook - GUIDED APPROACH
#
# Difference from baseline: Outputs explicit action instructions,
# not just signal tags that Claude must interpret.

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/hook-lib.sh"

INPUT=$(cat)
PROMPT=$(echo "$INPUT" | jq -r '.prompt // ""')

if [[ -z "$PROMPT" ]]; then
    exit 0
fi

PROMPT_LOWER=$(echo "$PROMPT" | tr '[:upper:]' '[:lower:]')
# Normalise Unicode apostrophe variants to ASCII apostrophe (OBS-20260216-114748)
# Covers: ´ (U+00B4 acute accent), ' (U+2019 right single quote), ʼ (U+02BC modifier apostrophe)
PROMPT_LOWER=$(echo "$PROMPT_LOWER" | sed "s/[´'ʼ]/'/g")
PERMISSION_MODE=$(echo "$INPUT" | jq -r '.permission_mode // ""')
INSTRUCTIONS=""

# Plan mode detection — when in plan mode, Skill/Task/Bash tools are unavailable.
# Adapt instructions to note items for logging after plan mode exits (FW-054 layer 2).
IN_PLAN_MODE=false
if [[ "$PERMISSION_MODE" == "plan" ]]; then
    IN_PLAN_MODE=true
fi

# Decision indicators → directive instruction
# Layer 1: Explicit decision language (original)
# Layer 2: Agreement/confirmation of a prior option
# Layer 3: Preference/selection language
# Layer 4: Terse confirmation patterns
# Designed to catch natural conversational decision-making (FW-054 findings)
DECISION_DETECTED=false
if echo "$PROMPT_LOWER" | grep -qE "(i decided|let'?s go with|decision is|i chose|we'?ll use|going with|decided to|make a decision)"; then
    DECISION_DETECTED=true
elif echo "$PROMPT_LOWER" | grep -qE "let'?s (go for|do that|do it|proceed|pick|commit to|use|go ahead)"; then
    DECISION_DETECTED=true
elif echo "$PROMPT_LOWER" | grep -qE "(sounds good|agreed|go ahead|yes.*(that|this) (approach|option|one)|ok let'?s)"; then
    DECISION_DETECTED=true
elif echo "$PROMPT_LOWER" | grep -qE "(i prefer|i'?d rather|i think we should|i'?ll take|makes more sense|we should (go|use|do|pick))"; then
    DECISION_DETECTED=true
elif echo "$PROMPT_LOWER" | grep -qE "(fine,? use|yep,? decided|that'?s the one)"; then
    DECISION_DETECTED=true
fi

if [[ "$DECISION_DETECTED" == "true" ]]; then
    if [[ "$IN_PLAN_MODE" == "true" ]]; then
        INSTRUCTIONS+="DECISION DETECTED (plan mode): Note this decision in your plan. It will be logged via dialogue-log-decision after plan mode exits. Include the decision subject, outcome chosen, and rationale. "
    else
        INSTRUCTIONS+="DECISION DETECTED: You MUST either (a) use the dialogue-log-decision skill to record this decision, OR (b) explicitly state why not (e.g. 'Skipping log: routine confirmation'). Routine confirmations of already-discussed actions (yes, ok, push, commit) do not need logging. Substantive choices (selecting approaches, setting direction) MUST be logged. Silent skips are not acceptable. "
    fi
fi

# Observation indicators → directive instruction
# Layer 1: Explicit observation language (original)
# Layer 2: Discovery/investigation outcome
# Layer 3: Anomaly/surprise indicators
# Layer 4: Measurement change language
# Designed to catch natural observational language (FW-054 findings)
OBSERVATION_DETECTED=false
if echo "$PROMPT_LOWER" | grep -qE "(i noticed|i observed|here'?s an observation|worth noting|i see that|observation:|noticed that)"; then
    OBSERVATION_DETECTED=true
elif echo "$PROMPT_LOWER" | grep -qE "(turns out|found (that |the .*(cause|problem|issue|bug|reason))|root cause|it'?s (actually |really ))"; then
    OBSERVATION_DETECTED=true
elif echo "$PROMPT_LOWER" | grep -qE "(that'?s weird|something'?s off|looks like .*(is |was |has )|huh.*(that|the|weird|strange))"; then
    OBSERVATION_DETECTED=true
elif echo "$PROMPT_LOWER" | grep -qE "(doubled|tripled|halved|increased|decreased|climbing|spiked|dropped|went from .* to)"; then
    OBSERVATION_DETECTED=true
elif echo "$PROMPT_LOWER" | grep -qE "(was being|were being|is actually|was actually) "; then
    OBSERVATION_DETECTED=true
fi

if [[ "$OBSERVATION_DETECTED" == "true" ]]; then
    if [[ "$IN_PLAN_MODE" == "true" ]]; then
        INSTRUCTIONS+="OBSERVATION DETECTED (plan mode): Note this observation in your plan. It will be logged via dialogue-log-observation after plan mode exits. Include what was observed and its significance. "
    else
        INSTRUCTIONS+="OBSERVATION DETECTED: You MUST either (a) use the dialogue-log-observation skill to record this finding, OR (b) explicitly state why not. Silent skips are not acceptable. "
    fi
fi

# LLM deterministic classification — when grep patterns find no decision/observation (FW-066)
# Grep is the fast path (deterministic, zero-cost). When grep misses, call claude -p
# with haiku for semantic classification. Environment vars scoped-unset to bypass
# nesting guard (OBS-20260225-185516). Stdin from /dev/null to prevent pipe hang.
# If claude -p fails, classification is silently skipped (no fallback).
# In plan mode, claude -p may not be available — fall back to self-classification directive.
if [[ "$DECISION_DETECTED" == "false" && "$OBSERVATION_DETECTED" == "false" ]]; then
    if [[ "$IN_PLAN_MODE" == "true" ]]; then
        INSTRUCTIONS+="LLM CLASSIFY (plan mode): Grep patterns found no decision or observation. Before responding, assess whether this prompt contains decision or observation language that patterns missed. If so, note it in your plan for logging after plan mode exits. "
    else
        # Build classification prompt — explicit criteria with examples for reliable identification
        CLASSIFY_MSG=$(printf 'You are a message classifier. Classify the user message below into exactly one category.

DECISION — The user is making a choice, confirming an approach, giving approval, expressing a preference, or settling a question. Examples: "yes do that", "option B", "let us keep this", "I prefer the first approach", "approved", "skip that part".

OBSERVATION — The user is reporting a factual finding, noting something they discovered or noticed, describing a state change, or sharing a measurement. Examples: "the test passed", "I see the output changed", "latency dropped to 50ms", "the build is broken", "that file is missing".

NEITHER — The user is asking a question, giving an instruction, making a request, or having general conversation. Examples: "how does this work?", "please fix the bug", "what is the status?", "can you refactor this?", "hello".

Respond with exactly one word: DECISION, OBSERVATION, or NEITHER.

User message: %s' "$PROMPT")

        # Call claude -p with scoped env unset (only for this call, not the whole script).
        # No in-script timeout — hooks.json timeout (15s) handles runaway calls.
        # Stdin from /dev/null prevents pipe hang. Stderr suppressed.
        CLASSIFICATION=$(env \
            -u CLAUDECODE \
            -u CLAUDE_CODE_ENTRYPOINT \
            -u CLAUDE_CODE_ENABLE_TELEMETRY \
            -u CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS \
            claude -p "$CLASSIFY_MSG" --model haiku --output-format text \
            < /dev/null 2>/dev/null) || CLASSIFICATION=""

        # Normalise to uppercase and trim whitespace
        CLASSIFICATION=$(echo "$CLASSIFICATION" | tr -d '[:space:]' | tr '[:lower:]' '[:upper:]')

        if [[ "$CLASSIFICATION" == "DECISION" ]]; then
            # TEMPORARY (FW-066 testing): "State [claude -p: ...]" line ensures user visibility while validating classification. Remove once FW-066 is fully validated.
            INSTRUCTIONS+="DECISION DETECTED (via claude -p): State '[claude -p: DECISION]' at the start of your response. You MUST either (a) use the dialogue-log-decision skill to record this decision, OR (b) explicitly state why not (e.g. 'Skipping log: routine confirmation'). Routine confirmations of already-discussed actions (yes, ok, push, commit) do not need logging. Substantive choices (selecting approaches, setting direction) MUST be logged. Silent skips are not acceptable. "
        elif [[ "$CLASSIFICATION" == "OBSERVATION" ]]; then
            # TEMPORARY (FW-066 testing): see DECISION comment above.
            INSTRUCTIONS+="OBSERVATION DETECTED (via claude -p): State '[claude -p: OBSERVATION]' at the start of your response. You MUST either (a) use the dialogue-log-observation skill to record this finding, OR (b) explicitly state why not. Silent skips are not acceptable. "
        elif [[ "$CLASSIFICATION" == "NEITHER" ]]; then
            # TEMPORARY (FW-066 testing): see DECISION comment above.
            INSTRUCTIONS+="Classified NEITHER (via claude -p). State '[claude -p: NEITHER]' at the start of your response. No logging needed. "
        fi
        # Empty CLASSIFICATION (claude -p failed) — silently skip, no fallback
    fi
fi

# Task operations without ID → directive instruction for skill use
if echo "$PROMPT_LOWER" | grep -qE "(list|show|display)\s*(open\s*)?(tasks?|work\s*items?)"; then
    INSTRUCTIONS+="TASK OPERATION: MUST use dialogue-manage-tasks skill to list tasks. Do NOT run scripts directly via Bash. "
elif echo "$PROMPT_LOWER" | grep -qE "(create|add|new)\s*(a\s*)?(task|work\s*item)"; then
    INSTRUCTIONS+="TASK OPERATION: MUST use dialogue-manage-tasks skill to create task. Do NOT write task files directly. "
fi

# Task references with ID → directive instruction
if echo "$PROMPT" | grep -qiE "\b(SH|FW|CD|DOC|VAL)-[0-9]{3}\b"; then
    TASK_ID=$(echo "$PROMPT" | grep -oiE "\b(SH|FW|CD|DOC|VAL)-[0-9]{3}\b" | head -1)
    # Check for update/status change verbs
    if echo "$PROMPT_LOWER" | grep -qE "(start|begin|work)\s*(on|with)?|update|complete|finish|done|mark\s*(as)?"; then
        INSTRUCTIONS+="TASK UPDATE: MUST use dialogue-manage-tasks skill to update ${TASK_ID} status. Do NOT edit task files directly. "
    else
        INSTRUCTIONS+="TASK REFERENCE: Use dialogue-manage-tasks skill to resolve ${TASK_ID} context. "
    fi
fi

# Reference resolution → directive instruction
if echo "$PROMPT" | grep -qiE "\b(THY|REF|STR|ADR)-[0-9]{3}\b"; then
    REF_ID=$(echo "$PROMPT" | grep -oiE "\b(THY|REF|STR|ADR)-[0-9]{3}\b" | head -1)
    INSTRUCTIONS+="REFERENCE: Resolve ${REF_ID} using dialogue-resolve-reference skill. "
fi
if echo "$PROMPT" | grep -qE "\b(DEC|OBS)-[0-9]{8}-[0-9]{6}\b"; then
    REF_ID=$(echo "$PROMPT" | grep -oE "\b(DEC|OBS)-[0-9]{8}-[0-9]{6}\b" | head -1)
    INSTRUCTIONS+="REFERENCE: Resolve ${REF_ID} using dialogue-resolve-reference skill. "
fi

# Phase indicators → directive instruction
if echo "$PROMPT_LOWER" | grep -qE "(phase\s*1|initiation|opportunity|stakeholder)"; then
    INSTRUCTIONS+="PHASE 1 CONTEXT: Apply Phase 1 guidance from framework-manual.md (tacit-heavy, human-led). "
elif echo "$PROMPT_LOWER" | grep -qE "(phase\s*2|planning|estimate|schedule)"; then
    INSTRUCTIONS+="PHASE 2 CONTEXT: Apply Phase 2 guidance from framework-manual.md. "
elif echo "$PROMPT_LOWER" | grep -qE "(phase\s*3|requirements?|specification)"; then
    INSTRUCTIONS+="PHASE 3 CONTEXT: Apply Phase 3 guidance from framework-manual.md. "
elif echo "$PROMPT_LOWER" | grep -qE "(phase\s*4|design|architecture)"; then
    INSTRUCTIONS+="PHASE 4 CONTEXT: Apply Phase 4 guidance from framework-manual.md. "
elif echo "$PROMPT_LOWER" | grep -qE "(phase\s*5|implement|coding|develop)"; then
    INSTRUCTIONS+="PHASE 5 CONTEXT: Apply Phase 5 guidance from framework-manual.md. "
fi

# ADR creation → directive instruction
if echo "$PROMPT_LOWER" | grep -qE "(create|write|draft).*(adr|architecture decision)"; then
    INSTRUCTIONS+="ADR REQUEST: Use dialogue-create-adr skill for formal architecture decision record. "
fi

# Task candidate → directive instruction with triage guidance
if ! echo "$PROMPT" | grep -qiE "\b(SH|FW|CD)-[0-9]{3}\b"; then
    if echo "$PROMPT_LOWER" | grep -qE "(implement|build|develop|create).*(feature|capability|system|component|integration|module|service|api|framework|plugin)"; then
        INSTRUCTIONS+="TASK CANDIDATE: Consider whether this needs persistent tracking via dialogue-manage-tasks (multi-session work) or TodoWrite (session-only). "
    elif echo "$PROMPT_LOWER" | grep -qE "(investigate|research|explore|analy[sz]e|understand).*(how|why|what|whether|if|issue|problem|approach|option)"; then
        INSTRUCTIONS+="TASK CANDIDATE: Consider whether this needs persistent tracking via dialogue-manage-tasks (multi-session work) or TodoWrite (session-only). "
    elif echo "$PROMPT_LOWER" | grep -qE "(design|architect|plan|prototype).*(system|component|approach|solution|integration|interface)"; then
        INSTRUCTIONS+="TASK CANDIDATE: Consider whether this needs persistent tracking via dialogue-manage-tasks (multi-session work) or TodoWrite (session-only). "
    fi
fi

# Trim
INSTRUCTIONS=$(echo "$INSTRUCTIONS" | xargs)

if [[ -z "$INSTRUCTIONS" ]]; then
    exit 0
fi

# Output directive instructions (not just tags)
jq -n --arg instructions "$INSTRUCTIONS" '{
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": "<dialogue-instruction>\($instructions)</dialogue-instruction>"
    }
}'
