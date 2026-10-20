---
name: copilot-tool-eval-resume
description: Safely resume an interrupted tool-eval run by ID in Copilot CLI. Use /copilot-tool-eval-resume <run_id>; refuses incompatible configuration and reuses validated results.
---

# Resume entry

Require exactly one run ID. Load `copilot-tool-eval-orchestration` in the
current main session with operation `resume` and that ID. If needed, read
`.github/agents/copilot-tool-eval-orchestrator.agent.md` to adopt its contract.

Run `run resume-check <run_id>` before mutating the run. On
`CONFIG_REVISION_MISMATCH`, refuse to continue and recommend a fresh research
run. On any other error, report the actual code and blocker.
Only `RUN_RESUMABLE` permits continuation.

Never create `run init resume` or replace the original run ID. Resume is not
Copilot's `/resume` command, which resumes a conversation rather than Python
run artifacts. Continue from validated on-disk results and recorded decisions;
never infer curation approval from a previous session's summary.
