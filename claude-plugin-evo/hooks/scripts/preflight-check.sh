#!/usr/bin/env bash
# preflight-check.sh — Verify critical tool dependencies before session starts.
# Runs as the first SessionStart hook. Cannot use jq (it might be the missing tool).
# All JSON output via cat/heredoc only.

CRITICAL_TOOLS="jq git sed grep"
OPTIONAL_TOOLS="claude tmux"

missing_critical=()
missing_optional=()

for tool in $CRITICAL_TOOLS; do
  command -v "$tool" >/dev/null 2>&1 || missing_critical+=("$tool")
done

for tool in $OPTIONAL_TOOLS; do
  command -v "$tool" >/dev/null 2>&1 || missing_optional+=("$tool")
done

# Happy path — all tools present, no output, zero overhead
if [ ${#missing_critical[@]} -eq 0 ] && [ ${#missing_optional[@]} -eq 0 ]; then
  exit 0
fi

# Critical tools missing — block session + soft-block via systemMessage directive
# NOTE: "continue": false does not work for SessionStart hooks as of Claude Code 2.1.x
# (logged but ignored). We keep it for forward-compatibility and add a systemMessage
# with a red warning + AI directive as the fallback that works today.
if [ ${#missing_critical[@]} -gt 0 ]; then
  missing_list=$(printf ', %s' "${missing_critical[@]}")
  missing_list=${missing_list:2}  # strip leading ', '

  install_cmds=""
  for tool in "${missing_critical[@]}"; do
    install_cmds="${install_cmds}  - ${tool}: apt install ${tool} (Debian/Ubuntu) | brew install ${tool} (macOS)\\n"
  done

  cat <<ENDJSON
{
  "continue": false,
  "stopReason": "Dialogue Framework cannot start — missing critical tools: ${missing_list}.",
  "systemMessage": "\u001b[1;31mDialogue Framework BLOCKED — missing critical tools: ${missing_list}\u001b[0m\n\nThe following tools are required but not installed:\n${install_cmds}\nHook scripts depend on these tools and will silently degrade without them.\nInstall the missing tools and restart Claude Code.",
  "additionalContext": "<dialogue-instruction>CRITICAL: Do NOT proceed with any work. Missing tools (${missing_list}) mean all hook scripts will silently fail. Tell the user they must install the missing tools and restart Claude Code. Do not attempt workarounds.</dialogue-instruction>"
}
ENDJSON
  exit 0
fi

# Optional tools missing — warn but allow session
if [ ${#missing_optional[@]} -gt 0 ]; then
  missing_list=$(printf ', %s' "${missing_optional[@]}")
  missing_list=${missing_list:2}

  warnings=""
  for tool in "${missing_optional[@]}"; do
    case "$tool" in
      claude) warnings="${warnings}- claude CLI not found: UserPromptSubmit classification (claude -p) will be unavailable\n" ;;
      tmux)   warnings="${warnings}- tmux not found: team mode session management will be unavailable\n" ;;
    esac
  done

  cat <<ENDJSON
{
  "continue": true,
  "systemMessage": "Dialogue Framework preflight warning — optional tools missing: ${missing_list}.\n${warnings}The framework will function but some features may be limited."
}
ENDJSON
  exit 0
fi
