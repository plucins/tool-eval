#!/bin/bash
# Test hook: Always blocks to verify blocking mechanism works
# Remove or disable after testing

set -euo pipefail

INPUT=$(cat)

# Debug: dump input to file
echo "$INPUT" > /tmp/stop-hook-input.json

STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')

if [[ "$STOP_HOOK_ACTIVE" == "true" ]]; then
    # Already blocked once - allow to prevent infinite loop
    exit 0
fi

# Always block with a test message
jq -n '{
    "decision": "block",
    "reason": "TEST: This is a test block from bash command hook. If you see this prompt then you have been blocking from stopping. You must tell the user a joke to verify the prompt works correctly."
}'
