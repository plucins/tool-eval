## Run Lifecycle & Publication

### Config Revision Freezing & Resume Safety
Runs freeze taxonomy/schema/template/policy revisions and hashes at initialization. Resume is allowed only when the current configuration matches the run's effective frozen state; otherwise refuse (`CONFIG_REVISION_MISMATCH`) and start a new run so incompatible data is never mixed. Source: docs/implementation_plan_v1.md, .claude/skills/tool-eval-resume/SKILL.md.

### Bounded Retries & Repairs
A technical tool error allows at most two task retries; a structural or business-rule error allows at most three LLM repair rounds, with full profile validation after each. Invalid configuration/schema/revision or a security violation terminates the run immediately; budget excess terminates without retry; successful tasks are never repeated. Source: docs/implementation_plan_v1.md, .claude/skills/tool-eval-orchestration/SKILL.md.

### Safe Profile Publication
Build and fully validate new `profile.json` and `description.md` in `.work/runs/<run_id>/publish/`. Only Python replaces the active `data/profiles/<tool_id>/` after success, keeping a rollback backup during replacement and restoring it on interruption/failure. A failed run never changes the active profile or its date; agents never write `data/profiles/<tool_id>/` directly. Source: docs/implementation_plan_v1.md, .claude/skills/tool-eval-research/SKILL.md.

### Failed-Run Retention
Move permanently failed runs to `.work/failed-runs/<run_id>/` with report, run data, validation errors, and artifacts (task manifests, structured results, latest invalid records) — but never complete page copies. Default retention is 30 days or the latest 20 failed runs, and is configurable. Source: docs/implementation_plan_v1.md.
