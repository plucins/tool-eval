"""Per-task worker-result validation (plan Sec 3.6 step 6).

Before the lead agent merges, each worker ``result.json`` is validated on its
own: JSON Schema for structure (``subagent-result``) plus the status-dependent
D-009 business rules for a feature-research result. A technical failure can be
retried or the bundle split; a *structural/business* failure feeds the repair
loop (D-011). The report is written to ``tasks/<task_id>/validation.json`` per
the run-artifact layout (plan Sec 3.4).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tool_eval.errors import ErrorFamily, ToolEvalError
from tool_eval.validation import business, schema


def _run_dir(root: Path, run_id: str) -> Path:
    run_dir = root / ".work" / "runs" / run_id
    if not run_dir.is_dir():
        raise ToolEvalError(
            code=f"{ErrorFamily.INPUT}_RUN_NOT_FOUND",
            message=f"No run directory for {run_id!r}",
            path=str(run_dir),
        )
    return run_dir


def _sources_by_id(run_dir: Path, result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Sources visible to a feature result: the accepted registry ∪ the result's own."""
    by_id: dict[str, dict[str, Any]] = {}
    registry_path = run_dir / "merged" / "sources.json"
    if registry_path.is_file():
        for src in json.loads(registry_path.read_text(encoding="utf-8")):
            by_id[src["source_id"]] = src
    for src in result.get("sources", []) or []:
        by_id.setdefault(src["source_id"], src)
    return by_id


def validate_task(root: Path, run_id: str, task_id: str) -> dict[str, Any]:
    """Validate one worker result; write validation.json; return the report."""
    run_dir = _run_dir(root, run_id)
    task_dir = run_dir / "tasks" / task_id
    result_path = task_dir / "result.json"
    if not result_path.is_file():
        raise ToolEvalError(
            code=f"{ErrorFamily.RESEARCH}_TASK_RESULT_MISSING",
            message=f"task {task_id!r} has no result.json to validate",
            path=str(result_path),
        )

    result = json.loads(result_path.read_text(encoding="utf-8"))
    errors: list[dict[str, Any]] = [e.to_dict() for e in schema.validate("subagent-result", result)]

    # Business rules only make sense once the shape is well-formed.
    if not errors and result.get("task_type") == "feature-research":
        sources_by_id = _sources_by_id(run_dir, result)
        for fr in result.get("feature_results", []) or []:
            errors.extend(e.to_dict() for e in business.validate_feature_result(fr, sources_by_id))

    report = {"task_id": task_id, "valid": not errors, "errors": errors}
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
