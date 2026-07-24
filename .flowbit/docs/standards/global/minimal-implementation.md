## Minimal Implementation

### Build What You Need
Create only methods, classes, and functions that will actually be called.

### Clear Purpose
Every method should either be called or improve code readability; nothing else.

### Delete Exploration Artifacts
Remove helper methods and utilities created during development that ended up unused.

### No Future Stubs
Avoid empty methods, placeholder functions, or interfaces "for future extensibility".

### No Speculative Abstractions
Skip factories, strategies, or adapters unless there's an immediate need.

### Review Before Commit
Verify all new methods have callers or serve a clear readability purpose before completing a task.

### Unused Code Is Debt
Remove dead code promptly; it confuses readers and adds maintenance burden.

## Project Standards (tool-eval)

### Minimal Dependency Stack
Keep the runtime stack intentionally small: PyYAML via `safe_load` only, jsonschema (Draft 2020-12), Jinja2 with `autoescape` + `StrictUndefined`, markdown-it-py with raw HTML disabled, nh3 for sanitization, and the standard library (argparse/json/pathlib/subprocess with `shell=False`/hashlib/logging). Do not add Pydantic, Click/Typer, Requests, web frameworks, databases, or crawler libraries without explicit need. Source: docs/implementation_plan_v1.md.

### Add Tools Without Generator Changes
Onboarding a new AI coding tool must not require changes to the generator or to existing profile code — a tool is added purely through the research workflow / profile data (e.g., `/tool-eval-research X`). Source: docs/ai_coding_tool_comparison_system_requirements_v2.md.
