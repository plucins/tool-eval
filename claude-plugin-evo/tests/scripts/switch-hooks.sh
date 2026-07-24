#!/bin/bash
# switch-hooks.sh - Switch between baseline and guided hook configurations
#
# Usage: ./switch-hooks.sh [baseline|guided|status]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOKS_JSON="$PLUGIN_ROOT/hooks/hooks.json"

show_status() {
    echo "Current hook configuration:"
    echo ""
    if grep -q "session-start-guided.sh" "$HOOKS_JSON"; then
        echo "  SessionStart:      GUIDED"
    else
        echo "  SessionStart:      BASELINE"
    fi
    if grep -q "user-prompt-submit-guided.sh" "$HOOKS_JSON"; then
        echo "  UserPromptSubmit:  GUIDED"
    else
        echo "  UserPromptSubmit:  BASELINE"
    fi
    echo ""
}

switch_to_guided() {
    echo "Switching to GUIDED hooks..."

    # Create backup
    cp "$HOOKS_JSON" "$HOOKS_JSON.bak"

    # Switch SessionStart
    sed -i '' 's|hooks/scripts/session-start\.sh|hooks/scripts/session-start-guided.sh|g' "$HOOKS_JSON"

    # Switch UserPromptSubmit
    sed -i '' 's|hooks/scripts/user-prompt-submit\.sh|hooks/scripts/user-prompt-submit-guided.sh|g' "$HOOKS_JSON"

    echo "Done. Restart Claude Code session to apply."
    show_status
}

switch_to_baseline() {
    echo "Switching to BASELINE hooks..."

    # Create backup
    cp "$HOOKS_JSON" "$HOOKS_JSON.bak"

    # Switch SessionStart
    sed -i '' 's|hooks/scripts/session-start-guided\.sh|hooks/scripts/session-start.sh|g' "$HOOKS_JSON"

    # Switch UserPromptSubmit
    sed -i '' 's|hooks/scripts/user-prompt-submit-guided\.sh|hooks/scripts/user-prompt-submit.sh|g' "$HOOKS_JSON"

    echo "Done. Restart Claude Code session to apply."
    show_status
}

MODE="${1:-status}"

case "$MODE" in
    guided)
        switch_to_guided
        ;;
    baseline)
        switch_to_baseline
        ;;
    status)
        show_status
        ;;
    *)
        echo "Usage: $0 [baseline|guided|status]"
        echo ""
        echo "  baseline  - Use signal-based hooks (current production)"
        echo "  guided    - Use directive-based hooks (experimental)"
        echo "  status    - Show current configuration"
        exit 1
        ;;
esac
