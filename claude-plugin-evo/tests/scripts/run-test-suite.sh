#!/bin/bash
# run-test-suite.sh - Run the hook effectiveness test suite
#
# Usage: ./run-test-suite.sh [baseline|guided]
#
# Runs all test prompts through the specified hook configuration
# and records the output for analysis.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PROJECT_ROOT="$(cd "$PLUGIN_ROOT/../.." && pwd)"

export CLAUDE_PROJECT_DIR="$PROJECT_ROOT"
export CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT"

MODE="${1:-baseline}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OUTPUT_DIR="$PLUGIN_ROOT/tests/results"
OUTPUT_FILE="$OUTPUT_DIR/test-run-${MODE}-${TIMESTAMP}.yaml"

mkdir -p "$OUTPUT_DIR"

# Select hook scripts based on mode
if [[ "$MODE" == "guided" ]]; then
    SESSION_HOOK="$PLUGIN_ROOT/hooks/scripts/session-start-guided.sh"
    PROMPT_HOOK="$PLUGIN_ROOT/hooks/scripts/user-prompt-submit-guided.sh"
else
    SESSION_HOOK="$PLUGIN_ROOT/hooks/scripts/session-start.sh"
    PROMPT_HOOK="$PLUGIN_ROOT/hooks/scripts/user-prompt-submit.sh"
fi

echo "=== Hook Effectiveness Test Suite ==="
echo "Mode: $MODE"
echo "Output: $OUTPUT_FILE"
echo ""

# Start output file
cat > "$OUTPUT_FILE" << EOF
# Hook Effectiveness Test Results
# Mode: $MODE
# Timestamp: $TIMESTAMP
# Session Hook: $SESSION_HOOK
# Prompt Hook: $PROMPT_HOOK

session_start_output: |
$(bash "$SESSION_HOOK" 2>/dev/null | sed 's/^/  /')

test_cases:
EOF

# Define test prompts
declare -a TEST_PROMPTS=(
    # Decision capture
    "D1|I decided we should use PostgreSQL for the database|dialogue-log-decision"
    "D2|Let's go with the microservices approach|dialogue-log-decision"
    "D3|The decision is to postpone the release|dialogue-log-decision"
    "D4|We'll use React for the frontend|dialogue-log-decision"

    # Observation capture
    "O1|I noticed the tests are running slowly|dialogue-log-observation"
    "O2|Here's an observation: the API response time increased|dialogue-log-observation"
    "O3|Worth noting that the error rate spiked yesterday|dialogue-log-observation"
    "O4|I observed that users are abandoning checkout at step 3|dialogue-log-observation"

    # Task reference
    "T1|Let's work on FW-038|dialogue-manage-tasks"
    "T2|What's the status of SH-005?|dialogue-manage-tasks"

    # Reference resolution
    "R1|What does THY-001 say about theory building?|dialogue-resolve-reference"
    "R2|Look up REF-001|dialogue-resolve-reference"

    # Phase context
    "P1|We're in the initiation phase, help me define the opportunity|phase-guidance"
    "P2|Let's work on requirements for this feature|phase-guidance"

    # Negative cases
    "N1|What time is it?|none"
    "N2|Fix the typo on line 42|none"
    "N3|How do I format a string in Python?|none"
)

for test_case in "${TEST_PROMPTS[@]}"; do
    IFS='|' read -r test_id prompt expected_skill <<< "$test_case"

    echo "Running $test_id..."

    # Run the prompt through the hook
    hook_output=$(echo "{\"prompt\": \"$prompt\"}" | bash "$PROMPT_HOOK" 2>/dev/null || echo "")

    # Extract the signal/instruction
    if [[ -n "$hook_output" ]]; then
        context=$(echo "$hook_output" | jq -r '.hookSpecificOutput.additionalContext // ""')
    else
        context=""
    fi

    # Append to output file
    cat >> "$OUTPUT_FILE" << EOF

  - id: "$test_id"
    prompt: "$prompt"
    expected_skill: "$expected_skill"
    hook_output: |
      $(echo "$hook_output" | sed 's/^/      /' || echo "      (none)")
    extracted_context: "$context"
    # Manual scoring (fill in after Claude session test):
    # skill_invoked:
    # correct_invocation:
    # notes:
EOF

done

echo ""
echo "Test prompts processed. Results saved to: $OUTPUT_FILE"
echo ""
echo "Next steps:"
echo "1. Switch hooks: ./switch-hooks.sh $MODE"
echo "2. Start Claude Code session"
echo "3. Run each prompt and record whether Claude invokes the expected skill"
echo "4. Fill in 'skill_invoked' and 'correct_invocation' fields in $OUTPUT_FILE"
