---
name: copilot-tool-eval-research
description: Research or refresh one AI coding tool and publish its profile using the Copilot CLI adapter. Use /copilot-tool-eval-research <tool_name> in the main orchestrator session.
---

# Research entry

Accept exactly one non-empty tool name; a quoted multiword name counts as one
argument, for example `/copilot-tool-eval-research "GitHub Copilot"`.
If missing or ambiguous, ask for the tool name before creating a run.
Let the Python CLI normalize the name into a tool ID.

Load `copilot-tool-eval-orchestration` in this main session with operation
`research` and the tool name. Do not launch an orchestrator subagent. If not
already selected, read
`.github/agents/copilot-tool-eval-orchestrator.agent.md` and adopt its operating
contract in the current main session.

Run the entire research, single curation checkpoint, validation, and publication
flow. Report the actual final CLI code, run ID, artifact paths, and warnings;
do not report a planned or staged profile as published.
