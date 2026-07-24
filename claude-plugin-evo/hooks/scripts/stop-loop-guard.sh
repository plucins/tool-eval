#!/bin/bash
# Stop hook: Prompt to check for missed logging, with loop guard.
#
# On first stop attempt: Block and prompt to review for missed decisions/observations.
# On second stop attempt (stop_hook_active=true): Approve to prevent infinite loop.

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/hook-lib.sh"

INPUT=$(cat)
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')

if [[ "$STOP_HOOK_ACTIVE" == "true" ]]; then
    # Already blocked once - allow stop to prevent infinite loop
    jq -n '{
        "decision": "approve",
        "systemMessage": "Logging review completed - proceeding to stop."
    }'
    exit 0
fi

# First stop attempt - block and prompt for logging review
jq -n '{
    "decision": "block",
    "reason": "Log any decisions and observations that you may have missed in your and the user'\''s last turns, using the appropriate skill.",
    "suppressOutput": true,
    "systemMessage": "Performing a sanity check for missed logging."
}'
