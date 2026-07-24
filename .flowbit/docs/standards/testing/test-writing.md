## Test Writing

### Test Behavior
Focus on what code does, not how it does it, to allow safe refactoring.

### Clear Names
Use descriptive names explaining what's tested and expected (`shouldReturnErrorWhenUserNotFound`).

### Mock External Dependencies
Isolate tests by mocking databases, APIs, and external services.

### Fast Execution
Keep unit tests fast (milliseconds) so developers run them frequently.

### Risk-Based Testing
Prioritize testing based on business criticality and likelihood of bugs.

### Balance Coverage and Velocity
Adjust test coverage based on project needs and team workflow.

### Critical Path Focus
Ensure core user workflows and critical business logic are well-tested.

### Appropriate Depth
Match edge case testing to the risk profile of the code.

## Project Standards (tool-eval)

### Deterministic Offline Tests & Pytest Conventions
Tests are deterministic and offline: worker/LLM research is exercised with fixture JSON, never live model or network calls. Use pytest with shared fixtures in `tests/conftest.py` (e.g., `temp_project` copies real config into an isolated tmp tree). Name test files `test_item{N}_{feature}.py` and test functions in snake_case. Evidence: 11/11 test files follow the naming + offline pattern; README documents `python -m pytest -q`. Source: README.md, tests/conftest.py.
