## Error Handling

### Clear User Messages
Show helpful, actionable messages without exposing internal details or security-sensitive information.

### Fail Fast
Validate inputs and check preconditions early; reject invalid data before it causes deeper issues.

### Typed Exceptions
Use specific exception types instead of generic ones to enable precise error handling.

### Centralized Handling
Catch and process errors at appropriate boundaries (controllers, API layers) rather than scattering try-catch throughout.

### Graceful Degradation
When non-critical services fail, continue operating with reduced functionality rather than crashing entirely.

### Retry with Backoff
Use exponential backoff for transient failures when calling external services.

### Resource Cleanup
Always release resources (file handles, connections) in finally blocks or equivalent cleanup mechanisms.

## Project Standards (tool-eval)

### Structured ToolEvalError Codes
Raise operational failures as `ToolEvalError` with a structured `code` of the form `<FAMILY>_<REASON>`, built from `ErrorFamily` constants plus an UPPERCASE reason suffix. Evidence: 42/42 raise sites pass a structured code.
```python
raise ToolEvalError(code=f"{ErrorFamily.CONFIG}_MISSING_FILE", message=..., path=str(path))
```
