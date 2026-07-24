#!/bin/bash
# test-enforce-dialogue-bash.sh — Test cases for enforce-dialogue-bash.sh
# Verifies the hook blocks direct bash operations on .dialogue/ paths

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_SCRIPT="$SCRIPT_DIR/enforce-dialogue-bash.sh"

PASS=0
FAIL=0

run_test() {
    local description="$1"
    local command="$2"
    local expect_block="$3"

    local input
    input=$(jq -n --arg cmd "$command" '{
        tool_name: "Bash",
        tool_input: { command: $cmd }
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

echo "=== Testing enforce-dialogue-bash.sh ==="
echo ""

# Blocked: Direct file listing of protected paths
run_test "ls .dialogue/tasks" "ls .dialogue/tasks/" "true"
run_test "cat .dialogue/tasks/FW-001.yaml" "cat .dialogue/tasks/FW-001.yaml" "true"
run_test "grep pattern .dialogue/tasks" "grep 'status' .dialogue/tasks/*.yaml" "true"
run_test "head .dialogue/tasks/file" "head -5 .dialogue/tasks/FW-001.yaml" "true"

# Blocked: Direct listing of logs
run_test "ls .dialogue/logs/decisions" "ls -la .dialogue/logs/decisions/" "true"
run_test "cat .dialogue/logs/observations" "cat .dialogue/logs/observations/OBS-123.yaml" "true"

# Blocked: Direct echo/redirection to protected paths
run_test "echo >> .dialogue/tasks" "echo 'status: COMPLETED' >> .dialogue/tasks/FW-001.yaml" "true"
run_test "printf to .dialogue/logs" "printf 'content' > .dialogue/logs/decisions/new.yaml" "true"

# Blocked: Destructive operations
run_test "rm .dialogue/tasks" "rm .dialogue/tasks/FW-001.yaml" "true"
run_test "mv .dialogue/logs" "mv .dialogue/logs/decisions/old.yaml /tmp/" "true"

# Blocked: Creating files directly
run_test "touch .dialogue/tasks" "touch .dialogue/tasks/new.yaml" "true"
run_test "mkdir .dialogue/logs" "mkdir -p .dialogue/logs/new/" "true"

# Allowed: Skill script execution (legitimate)
run_test "dialogue-manage-tasks skill" "bash skill/dialogue-manage-tasks/scripts/list-tasks.sh" "false"
run_test "log-decision skill" "bash skill/dialogue-log-decision/scripts/log-decision.sh" "false"
run_test "context-graph script" "bash .dialogue/context-graph/scripts/graph-locate.sh ABC-001" "false"

# Allowed: Non-.dialogue operations
run_test "ls regular directory" "ls src/" "false"
run_test "cat regular file" "cat README.md" "false"
run_test "git status" "git status" "false"
run_test "npm install" "npm install" "false"

# Test non-Bash tool separately (different input format)
echo ""
echo "Testing non-Bash tool handling..."
NON_BASH_INPUT='{"tool_name": "Edit", "tool_input": {"file_path": ".dialogue/tasks/FW-001.yaml"}}'
NON_BASH_OUTPUT=$(echo "$NON_BASH_INPUT" | bash "$HOOK_SCRIPT" 2>&1)
if echo "$NON_BASH_OUTPUT" | grep -q '"decision": "block"'; then
    echo "FAIL: Non-Bash tool (expected allow, got block)"
    ((FAIL++))
else
    echo "PASS: Non-Bash tool (correctly allowed - ignored by this hook)"
    ((PASS++))
fi

echo ""
echo "=== Results ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"

if [[ $FAIL -gt 0 ]]; then
    exit 1
fi
exit 0
