## Validation

### Server-Side Always
Validate on the server; client-side validation alone is insufficient for security and data integrity.

### Client-Side for Feedback
Use client-side validation for immediate user feedback, but duplicate checks server-side.

### Validate Early
Check inputs as early as possible and reject invalid data before processing.

### Specific Errors
Provide clear, field-specific messages that help users correct their input.

### Allowlists Over Blocklists
Define what's allowed rather than trying to block everything else.

### Type and Format Checks
Validate data types, formats, ranges, and required fields systematically.

### Input Sanitization
Sanitize user input to prevent injection attacks (SQL, XSS, command injection).

### Business Rules
Validate business logic (sufficient balance, valid dates) at the appropriate layer.

### Consistent Enforcement
Apply validation uniformly across all entry points (forms, APIs, background jobs).

## Project Standards (tool-eval)

### JSON Schema as Source of Truth
JSON Schemas (under `src/tool_eval/validation/schemas/`, D-016) are the source of truth for generated-data structure, types, simple dependencies, and examples. Status-dependent and cross-record rules (referential integrity, completeness) live in the business validator (`validation/business.py`), not in schemas. Source: README.md, docs/implementation_plan_v1.md.

### Profile Schema Conventions (D-016)
Profile schemas/data use: stable lowercase-ASCII underscore identifiers; ISO 8601 UTC timestamps; semantic `schema_version`; integer taxonomy/template revisions; `additionalProperties: false`; and omission of optional fields rather than storing `null` (unless `null` has a defined domain meaning). Source: docs/implementation_plan_v1.md.
