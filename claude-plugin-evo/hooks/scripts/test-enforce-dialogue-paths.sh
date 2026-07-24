#!/bin/bash
# test-enforce-dialogue-paths.sh — Test cases for enforce-dialogue-paths.sh
# Verifies the hook blocks protected paths and allows non-protected paths

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_SCRIPT="$SCRIPT_DIR/enforce-dialogue-paths.sh"

PASS=0
FAIL=0

run_test() {
    local description="$1"
    local tool_name="$2"
    local file_path="$3"
    local expect_block="$4"

    local input
    input=$(jq -n --arg tool "$tool_name" --arg path "$file_path" '{
        tool_name: $tool,
        tool_input: { file_path: $path }
    }')

    local output
    output=$(echo "$input" | bash "$HOOK_SCRIPT" 2>&1)
    local exit_code=$?

    local blocked=false
    if echo "$output" | grep -q '"decision": "block"'; then
        blocked=true
    fi

    if [[ "$expect_block" == "true" && "$blocked" == "true" ]]; then
        echo "PASS: $description (correctly blocked)"
        ((PASS++))
    elif [[ "$expect_block" == "false" && "$blocked" == "false" ]]; then
        echo "PASS: $description (correctly allowed)"
        ((PASS++))
    elif [[ "$expect_block" == "true" && "$blocked" == "false" ]]; then
        echo "FAIL: $description (expected block, got allow)"
        ((FAIL++))
    else
        echo "FAIL: $description (expected allow, got block)"
        echo "  Output: $output"
        ((FAIL++))
    fi
}

echo "=== Testing enforce-dialogue-paths.sh ==="
echo ""

# Task paths - should block Edit and Write
run_test "Edit .dialogue/tasks/FW-001.yaml" "Edit" ".dialogue/tasks/FW-001.yaml" "true"
run_test "Write .dialogue/tasks/FW-002.yaml" "Write" ".dialogue/tasks/FW-002.yaml" "true"

# Decision log paths - should block
run_test "Write .dialogue/logs/decisions/DEC-123.yaml" "Write" ".dialogue/logs/decisions/DEC-20260101-120000.yaml" "true"
run_test "Edit .dialogue/logs/decisions/test.yaml" "Edit" ".dialogue/logs/decisions/test.yaml" "true"

# Observation log paths - should block
run_test "Write .dialogue/logs/observations/OBS-123.yaml" "Write" ".dialogue/logs/observations/OBS-20260101-120000.yaml" "true"
run_test "Edit .dialogue/logs/observations/test.yaml" "Edit" ".dialogue/logs/observations/test.yaml" "true"

# Context graph paths - should block
run_test "Edit .dialogue/context-graph/nodes/test.yaml" "Edit" ".dialogue/context-graph/nodes/test.yaml" "true"
run_test "Write .dialogue/context-graph/edges/test.yaml" "Write" ".dialogue/context-graph/edges/test.yaml" "true"

# User paths - should block
run_test "Edit .dialogue/users/pidster.yaml" "Edit" ".dialogue/users/pidster.yaml" "true"
run_test "Write .dialogue/users/newuser.yaml" "Write" ".dialogue/users/newuser.yaml" "true"

# Non-protected paths - should allow
run_test "Edit README.md" "Edit" "README.md" "false"
run_test "Write src/main.ts" "Write" "src/main.ts" "false"
run_test "Edit .dialogue/README.md" "Edit" ".dialogue/README.md" "false"
run_test "Write .dialogue/config.yaml" "Write" ".dialogue/config.yaml" "false"

# Other tools - should allow (not Edit or Write)
run_test "Read .dialogue/tasks/FW-001.yaml" "Read" ".dialogue/tasks/FW-001.yaml" "false"
run_test "Bash command" "Bash" "/some/path" "false"

echo ""
echo "=== Results ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"

if [[ $FAIL -gt 0 ]]; then
    exit 1
fi
exit 0
