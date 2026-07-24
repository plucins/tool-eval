## Development Conventions

### Predictable Structure
Organize files and directories in a logical, navigable layout.

### Up-to-Date Documentation
Keep README files current with setup steps, architecture overview, and contribution guidelines.

### Clean Version Control
Write clear commit messages, use feature branches, and add meaningful descriptions to pull requests.

### Environment Variables
Store configuration in environment variables; never commit secrets or API keys.

### Minimal Dependencies
Keep dependencies lean and up-to-date; document why major ones are included.

### Consistent Reviews
Follow a defined code review process with clear expectations for reviewers and authors.

### Testing Standards
Define required test coverage (unit, integration, etc.) before merging.

### Feature Flags
Use flags for incomplete features instead of long-lived branches.

### Changelog Updates
Maintain a changelog or release notes for significant changes.

### Build What's Needed
Avoid speculative code and "just in case" additions (see minimal-implementation.md).

## Project Standards (tool-eval)

### Python & Config Naming
Python modules use snake_case (or dunder) names; classes use PascalCase; functions/methods use snake_case. Configuration and JSON Schema assets use lowercase kebab-case filenames (e.g., `source-policies.yaml`, `feature-result.schema.json`). Evidence: 129/129 sampled functions snake_case, 12/12 classes PascalCase, 6/6 configs and 11/11 schemas kebab-case.

### Format Split by Artifact Type
Use the right format per artifact: YAML for manually edited configuration; JSON for profiles, manifests, tasks, subagent results, candidates, and error reports; JSON Schema for validating generated data; Markdown for skills, agents, docs, and semantic descriptions; HTML only for the self-contained output artifact. Source: docs/implementation_plan_v1.md.

### English Technical Content with Exact Excerpts
All implemented content — field names, enums, identifiers, skills, prompts, validator messages, technical docs, and UI — is written in English. The `excerpt` field preserves the source's exact wording verbatim and is never translated or paraphrased. Source: docs/implementation_plan_v1.md, .claude/agents/tool-eval-worker.md.
