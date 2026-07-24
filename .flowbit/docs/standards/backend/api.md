## API Design

### RESTful Principles
Use resource-based URLs with appropriate HTTP methods (GET, POST, PUT, PATCH, DELETE).

### Consistent Naming
Use lowercase, hyphenated or underscored names consistently across endpoints.

### Versioning
Implement versioning (URL path or headers) to manage breaking changes.

### Plural Nouns
Use plural nouns for resources (`/users`, `/products`).

### Limited Nesting
Keep URL nesting to 2-3 levels maximum for readability.

### Query Parameters
Use query parameters for filtering, sorting, and pagination.

### Proper Status Codes
Return appropriate HTTP status codes (200, 201, 400, 404, 500).

### Rate Limit Headers
Include rate limit information in response headers.

## Project Standards (tool-eval)

### Single JSON Envelope CLI Contract
Every CLI command prints exactly one JSON envelope to stdout — `{status, code, run_id, next_action, artifacts, errors}` — and sends all logs to stderr. Large data stays in schema-compliant artifact files; agents parse stdout as JSON and act on `code`/`next_action`. Evidence: 18/18 `cmd_*` handlers return via `_envelope`; single `json.dumps` to stdout; logging to `sys.stderr`. Source: README.md, .claude/agents/tool-eval-orchestrator.md.

### Canonical `python -m tool_eval` Interface
The stable scripting interface is `python -m tool_eval <command>` (console script `tool-eval`). Agents invoke deterministic operations through this CLI rather than ad-hoc script steps. Source: docs/implementation_plan_v1.md.
