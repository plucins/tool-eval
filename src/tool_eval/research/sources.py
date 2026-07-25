"""Source discovery: the run's first phase (D-009 logical source registry).

Two deterministic, single-writer Python operations frame the LLM research
(D-004/D-005):

- :func:`create_source_task` plans one ``source-discovery`` task manifest and
  captures the tool identity for the run. A ``tool-eval-worker`` fills in
  ``result.json`` with the official sources it found;
- :func:`accept_sources` validates those worker-reported sources, deduplicates
  them into the run's logical source registry (``merged/sources.json``), and
  enforces the acceptance gate: a registry with at least one *official* source
  (D-017 - feature statuses may rest only on official sources). Without an
  accepted registry, feature research is blocked (plan Sec 3.6).

Python never researches (D-005); it only prepares the contract and validates
what the worker returns.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from tool_eval.errors import ErrorFamily, ToolEvalError
from tool_eval.paths import resolve_within
from tool_eval.research.merge import _merge_sources, MergeError
from tool_eval.runs.manager import read_run, save_run, transition
from tool_eval.validation import schema

SOURCE_DISCOVERY_TASK_ID = "src-discovery-01"

# Source classes a discovery pass should try to locate for the tool (D-009).
# Aligned with source.schema.json `source_type` enum.
DEFAULT_SOURCE_CLASSES: tuple[str, ...] = (
    "documentation",
    "product_page",
    "changelog",
    "pricing",
    "integration_catalog",
    "specialist",
)

# Fields a worker needs to decide what to WebFetch; staleness bookkeeping
# (checked_at/available/redirect_from) stays in the registry, not the brief.
_KNOWN_SOURCE_FIELDS = ("source_id", "url", "title", "source_type", "official")


def project_known_sources(run_dir: Path) -> list[dict[str, Any]]:
    """Project the accepted source registry for reuse by later-phase workers.

    Returns ``[]`` if source-discovery hasn't been accepted yet for this run
    (real orchestration order guarantees it has by the time feature-research
    or profile-writing tasks are planned; a soft default just keeps
    direct/unit-test callers working).
    """
    registry_path = run_dir / "merged" / "sources.json"
    if not registry_path.is_file():
        return []
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    return [{k: source[k] for k in _KNOWN_SOURCE_FIELDS} for source in registry]


def normalise_tool_id(tool_name: str) -> str:
    """Normalise a free-text tool name to a ``^[a-z][a-z0-9_]*$`` tool_id (D-016)."""
    lowered = tool_name.strip().lower()
    # Any run of non lowercase-alnum characters collapses to a single underscore.
    slug = re.sub(r"[^a-z0-9]+", "_", lowered).strip("_")
    if not slug:
        raise ToolEvalError(
            code=f"{ErrorFamily.INPUT}_BAD_TOOL_NAME",
            message=f"tool name {tool_name!r} has no usable ASCII letters/digits",
        )
    if not slug[0].isalpha():
        slug = f"tool_{slug}"
    if not re.fullmatch(r"[a-z][a-z0-9_]*", slug):
        raise ToolEvalError(
            code=f"{ErrorFamily.INPUT}_BAD_TOOL_NAME",
            message=f"could not derive a valid tool_id from {tool_name!r} (got {slug!r})",
        )
    return slug


def _run_dir(root: Path, run_id: str) -> Path:
    run_dir = root / ".work" / "runs" / run_id
    if not run_dir.is_dir():
        raise ToolEvalError(
            code=f"{ErrorFamily.INPUT}_RUN_NOT_FOUND",
            message=f"No run directory for {run_id!r}",
            path=str(run_dir),
        )
    return run_dir


def _tool_json_path(run_dir: Path) -> Path:
    return run_dir / "tool.json"


def read_tool_identity(run_dir: Path) -> dict[str, str] | None:
    path = _tool_json_path(run_dir)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def create_source_task(root: Path, run_id: str, tool_name: str) -> dict[str, Any]:
    """Write the ``source-discovery`` task manifest and record the tool identity."""
    run_dir = _run_dir(root, run_id)
    record = read_run(root, run_id)
    tool_id = normalise_tool_id(tool_name)

    manifest = {
        "task_id": SOURCE_DISCOVERY_TASK_ID,
        "run_id": run_id,
        "task_type": "source-discovery",
        "skill": "source-discovery",
        "inputs": {
            "tool_name": tool_name,
            "tool_id": tool_id,
            "source_classes": list(DEFAULT_SOURCE_CLASSES),
        },
        "output_path": "result.json",
    }
    errors = schema.validate("task", manifest)
    if errors:
        raise ToolEvalError(
            code=f"{ErrorFamily.VALIDATION}_TASK_MANIFEST_INVALID",
            message=f"source-discovery manifest failed schema: {errors[0].message}",
        )

    task_dir = resolve_within(run_dir / "tasks", SOURCE_DISCOVERY_TASK_ID)
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "task.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (task_dir / "input.json").write_text(
        json.dumps(manifest["inputs"], indent=2), encoding="utf-8"
    )

    # Persist the tool identity so later phases (build-profile) need no re-entry.
    _tool_json_path(run_dir).write_text(
        json.dumps({"tool_id": tool_id, "name": tool_name}, indent=2), encoding="utf-8"
    )

    transition(record, "source_discovery_in_progress", detail=f"tool={tool_id}")
    save_run(root, record)

    return {
        "run_id": run_id,
        "tool_id": tool_id,
        "tool_name": tool_name,
        "task_id": SOURCE_DISCOVERY_TASK_ID,
        "manifest_path": str(task_dir / "task.json"),
    }


def _load_discovery_results(run_dir: Path) -> tuple[list[dict[str, Any]], list[dict]]:
    """Load + schema-validate every source-discovery result in the run."""
    tasks_dir = run_dir / "tasks"
    results: list[dict[str, Any]] = []
    errors: list[dict] = []
    if not tasks_dir.is_dir():
        return results, errors
    for task_dir in sorted(tasks_dir.iterdir()):
        manifest_path = task_dir / "task.json"
        if not manifest_path.is_file():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("task_type") != "source-discovery":
            continue
        result_path = task_dir / "result.json"
        if not result_path.is_file():
            errors.append(
                {
                    "code": "RESEARCH_SOURCE_RESULT_MISSING",
                    "message": f"source-discovery task {task_dir.name!r} has no result.json",
                }
            )
            continue
        data = json.loads(result_path.read_text(encoding="utf-8"))
        schema_errors = schema.validate("subagent-result", data)
        if schema_errors:
            errors.extend(se.to_dict() for se in schema_errors)
            continue
        results.append(data)
    return results, errors


def accept_sources(root: Path, run_id: str) -> dict[str, Any]:
    """Validate discovered sources into the run's registry and open the gate."""
    run_dir = _run_dir(root, run_id)
    results, load_errors = _load_discovery_results(run_dir)
    if load_errors:
        raise ToolEvalError(
            code=f"{ErrorFamily.RESEARCH}_SOURCE_DISCOVERY_INCOMPLETE",
            message=(
                f"cannot accept sources: {len(load_errors)} discovery result(s) missing "
                f"or invalid (first: {load_errors[0]['message']})"
            ),
        )

    merge_errors: list[MergeError] = []
    sources = _merge_sources(results, merge_errors)
    if merge_errors:
        raise ToolEvalError(
            code=f"{ErrorFamily.VALIDATION}_SOURCE_CONFLICT",
            message=merge_errors[0].message,
        )

    if not sources:
        raise ToolEvalError(
            code=f"{ErrorFamily.RESEARCH}_NO_SOURCES",
            message="source discovery returned no sources; cannot open the research gate",
        )

    official = [s for s in sources if s.get("official") is True]
    if not official:
        raise ToolEvalError(
            code=f"{ErrorFamily.RESEARCH}_NO_OFFICIAL_SOURCE",
            message=(
                "the source registry has no official source; feature statuses may rest "
                "only on official sources (D-017), so the gate stays closed"
            ),
        )

    merged_dir = run_dir / "merged"
    merged_dir.mkdir(parents=True, exist_ok=True)
    (merged_dir / "sources.json").write_text(
        json.dumps(sources, indent=2), encoding="utf-8"
    )

    # D-017: record any ignored prompt-injection / access warnings, never obey them.
    warnings: list[str] = []
    for r in results:
        warnings.extend(r.get("warnings", []) or [])
    if warnings:
        (merged_dir / "warnings.json").write_text(
            json.dumps({"warnings": warnings}, indent=2), encoding="utf-8"
        )

    record = read_run(root, run_id)
    transition(
        record,
        "sources_accepted",
        detail=f"{len(sources)} sources ({len(official)} official)",
    )
    save_run(root, record)

    return {
        "run_id": run_id,
        "source_count": len(sources),
        "official_count": len(official),
        "warnings": warnings,
    }
