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
Delegate independent feature bundles with at most `runtime.yaml` `concurrency.max_concurrent_workers` concurrent workers by default (currently 8; configurable, cannot exceed harness capacity). A typical bundle is `runtime.yaml` `bundling.min/max_features_per_bundle` related features (currently 2-8, raised from 2-4 to let one bundle cover a whole taxonomy group and cut redundant per-bundle source re-discovery — see "Source Reuse & Search Budget" below); complex features get their own task; each feature returns a separate JSON record; wait for all mandatory tasks before merging. Raising concurrency and bundle size together increases the worst-case blast radius of a repeated technical failure (D-011 splits a failing bundle into single-feature tasks after 2 retries, so an 8-feature bundle can fragment into 8 isolated tasks) - recalibrate downward if that path is observed in practice. Source: docs/implementation_plan_v1.md, .claude/agents/tool-eval-orchestrator.md.

### Source Reuse & Search Budget
Feature-research workers must check the accepted source registry (`known_sources`, projected from `merged/sources.json` into the task input) and `WebFetch` known official URLs before issuing any new `WebSearch` call; a new search is justified only when no known source plausibly covers the assigned feature. Source discovery should cover all required source classes with the fewest broad `WebSearch` queries — typically one query to find the official homepage/docs root, then `WebFetch` crawling its own on-site navigation for pricing/changelog/integration pages — rather than one search per source class or per feature. This exists because the organization requires manual approval of every `WebSearch` call, and redundant re-discovery of already-known official sources was the main driver of that approval overhead; the rule reduces search volume without relaxing the official-sources-only rule or the not-found protocol above. Source: src/tool_eval/research/tasks.py (`_known_sources`, `_task_input`), .claude/agents/tool-eval-worker.md.
