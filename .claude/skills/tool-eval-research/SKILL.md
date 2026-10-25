---
name: tool-eval-research
description: >
  Operator entry skill to research one AI coding tool and publish its profile.
  Invoke as `/tool-eval-research <tool_name>`. Validates arguments, then hands
  control to the tool-eval-orchestration workflow. Use when you want to create or
  refresh the profile for a single tool.
---

# tool-eval-research

Entry skill (D-018). Directly invoked by the operator; it does not do research
itself — it validates arguments and hands the operation to the orchestration
workflow.

## Usage

```
/tool-eval-research <tool_name>
```

- `<tool_name>` (required): the tool to research, e.g. `cursor`, `windsurf`.
  Normalised to a lowercase-ASCII-and-underscores `tool_id` by the CLI.

## What it does

1. Validate that exactly one tool name was provided.
2. Hand over to `tool-eval-orchestration` with operation `research` and the tool
   name. That workflow runs config validate -> run init -> source discovery ->
   feature research via isolated workers -> merge -> single curation gate ->
   research accepted features -> build, validate (<=3 repairs), and publish the
   profile.
3. Report the final envelope: `run_id`, published profile artifacts, and any
   warnings (e.g. `requires_research`, stale sources, ignored prompt-injection
   attempts).

## Guarantees and limits

- Research pauses at exactly one curation point where you accept, reject, or
  defer each candidate feature (D-018).
- An invalid or incomplete profile is never published; a failed run leaves any
  existing profile and its date untouched.
- No API key is required; all LLM work runs inside Claude Code (D-015).

Accept a quoted multiword name as one argument (e.g. `"OpenAI Codex"`). Report
the actual final CLI code, run id, artifact paths, and warnings; never report a
staged profile as published.
