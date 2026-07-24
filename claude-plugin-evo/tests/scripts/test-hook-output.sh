#!/bin/bash
# test-hook-output.sh - Test hook output for given prompts
#
# Usage: ./test-hook-output.sh "prompt text"
#
# Tests both SessionStart and UserPromptSubmit hooks and shows their output.
# Useful for verifying hook behaviour before running full A/B tests.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Set required environment variables
export CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$PLUGIN_ROOT/../.." && pwd)}"
export CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT"

PROMPT="${1:-}"

echo "=== Hook Output Test ==="
echo "CLAUDE_PROJECT_DIR: $CLAUDE_PROJECT_DIR"
echo "CLAUDE_PLUGIN_ROOT: $CLAUDE_PLUGIN_ROOT"
echo ""

# Test SessionStart hooks
echo "--- SessionStart (baseline) ---"
bash "$PLUGIN_ROOT/hooks/scripts/session-start.sh" 2>/dev/null || echo "(no output)"
echo ""

echo "--- SessionStart (guided) ---"
bash "$PLUGIN_ROOT/hooks/scripts/session-start-guided.sh" 2>/dev/null || echo "(no output)"
echo ""

if [[ -n "$PROMPT" ]]; then
    echo "--- UserPromptSubmit (baseline) ---"
    echo "Prompt: $PROMPT"
    echo "{\"prompt\": \"$PROMPT\"}" | bash "$PLUGIN_ROOT/hooks/scripts/user-prompt-submit.sh" 2>/dev/null || echo "(no output)"
    echo ""

    echo "--- UserPromptSubmit (guided) ---"
    echo "Prompt: $PROMPT"
    echo "{\"prompt\": \"$PROMPT\"}" | bash "$PLUGIN_ROOT/hooks/scripts/user-prompt-submit-guided.sh" 2>/dev/null || echo "(no output)"
    echo ""
else
    echo "(No prompt provided - skipping UserPromptSubmit test)"
    echo "Usage: $0 \"I decided to use PostgreSQL\""
fi
