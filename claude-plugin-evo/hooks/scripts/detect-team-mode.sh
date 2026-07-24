#!/bin/bash
# detect-team-mode.sh — Detect team mode (solo or team) for feature gating
# Part of the Dialogue Framework (FW-040)
#
# Reads team_mode from config.yaml:
#   - auto: Detect from active user count (2+ users within 30 days = team)
#   - solo: Force simplified mode
#   - team: Force full features
#
# Outputs: "solo" or "team"

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/hook-lib.sh"

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:?CLAUDE_PROJECT_DIR must be set}"
CONFIG_FILE="${PROJECT_ROOT}/.dialogue/config.yaml"
USERS_DIR="${PROJECT_ROOT}/.dialogue/users"

# Default if no config exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "solo"
    exit 0
fi

# Read team_mode from config (default: auto)
TEAM_MODE="auto"
mode_line=$(grep -m1 "^team_mode:" "$CONFIG_FILE" 2>/dev/null || echo "")
if [[ -n "$mode_line" ]]; then
    TEAM_MODE=$(echo "$mode_line" | awk '{print $2}' | tr -d '"' | tr -d "'" || echo "auto")
fi

# Handle explicit modes
case "$TEAM_MODE" in
    solo)
        echo "solo"
        exit 0
        ;;
    team)
        echo "team"
        exit 0
        ;;
    auto|*)
        # Fall through to auto-detection
        ;;
esac

# Auto-detection: count users active within last 30 days
if [[ ! -d "$USERS_DIR" ]]; then
    echo "solo"
    exit 0
fi

# Get cutoff timestamp (30 days ago)
if [[ "$(uname)" == "Darwin" ]]; then
    CUTOFF=$(date -v-30d -u +"%Y-%m-%dT%H:%M:%SZ")
else
    CUTOFF=$(date -u -d "30 days ago" +"%Y-%m-%dT%H:%M:%SZ")
fi

ACTIVE_USERS=0

for user_file in "$USERS_DIR"/*.yaml; do
    [[ -f "$user_file" ]] || continue

    # Extract last_seen timestamp
    last_seen=$(grep -m1 "^last_seen:" "$user_file" 2>/dev/null | awk '{print $2}' | tr -d '"' || echo "")

    if [[ -n "$last_seen" ]]; then
        # Compare timestamps lexicographically (ISO 8601 format allows this)
        if [[ "$last_seen" > "$CUTOFF" ]] || [[ "$last_seen" == "$CUTOFF" ]]; then
            ((ACTIVE_USERS++))
        fi
    fi
done

# 2+ active users = team mode
if [[ $ACTIVE_USERS -ge 2 ]]; then
    # Promote auto to team permanently (FW-050, DEC-20260203-190913)
    # Once multiple team members have worked, that history is permanent
    if [[ -f "$CONFIG_FILE" ]] && grep -q "^team_mode: auto" "$CONFIG_FILE" 2>/dev/null; then
        sed -i.bak "s/^team_mode: auto/team_mode: team/" "$CONFIG_FILE" 2>/dev/null || true
        rm -f "${CONFIG_FILE}.bak" 2>/dev/null || true
        echo "[dialogue] Auto mode promoted to team mode (2+ active users)" >&2
    fi
    echo "team"
else
    echo "solo"
fi
