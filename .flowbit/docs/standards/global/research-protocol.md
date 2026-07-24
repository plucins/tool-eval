## Research Protocol

### Single Curation Gate
Research has exactly one curation point where every candidate feature receives an accept, reject, or defer decision. Publication is blocked while any candidate is undecided; only accepted candidates trigger controlled taxonomy revision changes through the CLI. Source: docs/implementation_plan_v1.md, .claude/skills/tool-eval-orchestration/SKILL.md.

### Complete Not-Found Protocol
`not_found` is allowed only after the full auditable search protocol runs: all relevant source classes checked, no material errors or unresolved conflicts, no full/partial confirmation, `protocol_complete: true`, and Python validation of checklist completeness. An unavailable material source, tool failure, or incomplete research yields `uncertain`, never `not_found`. Source: docs/implementation_plan_v1.md.

### No Source Voting
Resolve conflicts by policy order: scope match → current state vs history → recency → type policy → broader research → `uncertain/disputed`. Never vote by number of occurrences, because pages may copy one another. Source: docs/ai_coding_tool_comparison_system_requirements_v2.md.

### Evidence & Retained-Source Scope
Do not store complete copies of pages, HTML, PDFs, or screenshots. Store source metadata (URL, title, type), availability/redirect info, checked-at date, short excerpts for has/partial, and structured search traces for negative results. Source: docs/implementation_plan_v1.md.

### Research Concurrency Limits
Delegate independent feature bundles with at most four concurrent workers by default (configurable, cannot exceed harness capacity). A typical bundle is two to four related features; complex features get their own task; each feature returns a separate JSON record; wait for all mandatory tasks before merging. Source: docs/implementation_plan_v1.md, .claude/agents/tool-eval-orchestrator.md.
