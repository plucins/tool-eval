---
name: copilot-tool-eval-compare
description: Build one offline HTML comparison of two or more already-published tool profiles with Copilot CLI. Use /copilot-tool-eval-compare <tool_id> <tool_id> [<tool_id>...]; never starts research.
---

# Comparison entry

Require at least two distinct tool IDs whose profiles are already published.
Use IDs, not display names; `profile list` can identify existing IDs.
Report invalid or missing arguments before creating output.

Load `copilot-tool-eval-orchestration` in the current main session with operation
`compare` and the IDs. Do not spawn an orchestrator or workers.
If needed, read `.github/agents/copilot-tool-eval-orchestrator.agent.md` to
adopt its operating contract.

Comparison uses only the deterministic CLI; no web tools or research.
Report the HTML path returned by `COMPARISON_BUILT`, plus warnings.
A missing profile is an error; do not silently drop the tool, fabricate its
profile, or launch research.
