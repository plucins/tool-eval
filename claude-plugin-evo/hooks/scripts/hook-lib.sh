#!/bin/bash
# hook-lib.sh — Shared logging and error handling for dialogue hook scripts
# Part of the Dialogue Framework plugin (FW-073)
#
# Source this at the top of hook scripts AFTER set -euo pipefail:
#   source "$(dirname "${BASH_SOURCE[0]}")/hook-lib.sh"
#
# Features:
#   - ERR trap: logs failing command, line number, and script name to log file
#   - DIALOGUE_HOOK_DEBUG=1: enables verbose tracing (set -x output to log file)
#   - hook_log(): write timestamped entries to log file
#   - hook_debug(): write only when DIALOGUE_HOOK_DEBUG=1
#
# Log location: /tmp/dialogue-hooks.log (append-mode, survives session restarts)
# To watch live: tail -f /tmp/dialogue-hooks.log

DIALOGUE_HOOK_LOG="${DIALOGUE_HOOK_LOG:-/tmp/dialogue-hooks.log}"
DIALOGUE_HOOK_DEBUG="${DIALOGUE_HOOK_DEBUG:-0}"

# Derive script name from the caller (not this library)
_HOOK_SCRIPT_NAME="$(basename "${BASH_SOURCE[1]:-unknown}")"

# Timestamped log entry
hook_log() {
    local level="${1:-INFO}"
    shift
    printf '[%s] [%s] [%s] %s\n' \
        "$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%SZ)" \
        "$level" \
        "$_HOOK_SCRIPT_NAME" \
        "$*" \
        >> "$DIALOGUE_HOOK_LOG" 2>/dev/null || true
}

# Debug-only log (suppressed unless DIALOGUE_HOOK_DEBUG=1)
hook_debug() {
    if [[ "$DIALOGUE_HOOK_DEBUG" == "1" ]]; then
        hook_log "DEBUG" "$@"
    fi
}

# ERR trap — captures the failing command and line number
_hook_err_trap() {
    local exit_code=$?
    local line_no="${1:-?}"
    local command="${BASH_COMMAND:-unknown}"
    hook_log "ERROR" "exit_code=${exit_code} line=${line_no} cmd='${command}'"
    # Also write to stderr so Claude Code can surface it if it captures stderr
    echo "[dialogue-hook] ${_HOOK_SCRIPT_NAME}:${line_no} failed (exit ${exit_code}): ${command}" >&2
}

# Install ERR trap (works with set -e)
trap '_hook_err_trap ${LINENO}' ERR

# Enable bash tracing to log file when debug mode is on
if [[ "$DIALOGUE_HOOK_DEBUG" == "1" ]]; then
    hook_log "DEBUG" "=== Hook invoked (debug mode) ==="
    # Redirect trace output (set -x) to log file via fd 4
    exec 4>>"$DIALOGUE_HOOK_LOG"
    BASH_XTRACEFD=4
    PS4='+[${_HOOK_SCRIPT_NAME}:${LINENO}] '
    set -x
fi

# Log hook start in debug mode
hook_debug "Script started, PID=$$"
