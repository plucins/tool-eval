"""Project-root discovery, runtime directories, and safe path handling.

Portable across Windows, Linux, and macOS (D-008): pathlib only, no shell
assumptions. `resolve_within` enforces D-017 - paths taken from manifests or
task data must never escape the directory they are scoped to.
"""

from __future__ import annotations

from pathlib import Path

from tool_eval.errors import ErrorFamily, ToolEvalError

_MARKER_FILE = "pyproject.toml"

# Runtime directories created under the project root on first use.
RUNTIME_DIRS: tuple[str, ...] = (
    "data/profiles",
    "data/feature-candidates",
    "outputs/comparisons",
    ".work/runs",
    ".work/failed-runs",
)


def discover_project_root(start: Path | None = None) -> Path:
    """Walk upward from `start` (default: cwd) until `pyproject.toml` is found."""
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / _MARKER_FILE).is_file():
            return candidate
    raise ToolEvalError(
        code=f"{ErrorFamily.CONFIG}_PROJECT_ROOT_NOT_FOUND",
        message=(
            f"Could not locate {_MARKER_FILE} above {current}; "
            "run tool_eval commands from inside a tool-eval checkout."
        ),
    )


def ensure_runtime_dirs(root: Path) -> list[Path]:
    """Create the runtime directories (idempotent). Returns the created paths."""
    created: list[Path] = []
    for rel in RUNTIME_DIRS:
        directory = root / rel
        directory.mkdir(parents=True, exist_ok=True)
        created.append(directory)
    return created


def resolve_within(base: Path, relative: str) -> Path:
    """Resolve `relative` under `base`, rejecting any escape from `base`.

    Used to validate paths coming from task manifests / worker results before
    touching the filesystem (D-017: normalized paths must remain within the
    run directory).
    """
    base_resolved = base.resolve()
    candidate = (base_resolved / relative).resolve()
    try:
        candidate.relative_to(base_resolved)
    except ValueError as exc:
        raise ToolEvalError(
            code=f"{ErrorFamily.INPUT}_UNSAFE_PATH",
            message=f"Path {relative!r} escapes base directory {base_resolved}",
            path=relative,
        ) from exc
    return candidate
