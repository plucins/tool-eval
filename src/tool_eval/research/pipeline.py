"""Run-scoped orchestration wrappers around the pure research functions.

These read/write the run directory and are what the CLI calls. The heavy logic
lives in :mod:`planner` and :mod:`merge` as pure functions so it can be tested
without a filesystem.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tool_eval.config import load_config_bundle
from tool_eval.errors import ErrorFamily, ToolEvalError
from tool_eval.research.merge import merge_results, verify_completeness
from tool_eval.runs.manager import read_run, save_run, transition
from tool_eval.validation import schema


def _run_dir(root: Path, run_id: str) -> Path:
    run_dir = root / ".work" / "runs" / run_id
    if not run_dir.is_dir():
        raise ToolEvalError(
            code=f"{ErrorFamily.INPUT}_RUN_NOT_FOUND",
            message=f"No run directory for {run_id!r}",
            path=str(run_dir),
        )
    return run_dir


def taxonomy_feature_ids(root: Path) -> list[str]:
    bundle = load_config_bundle(root)
    features = bundle.files["feature-taxonomy.yaml"].data.get("features", [])
    return [f["feature_id"] for f in features]


def load_worker_results(root: Path, run_id: str) -> tuple[list[dict[str, Any]], list[dict]]:
    """Load and schema-validate every task's result.json.

    Returns (results, schema_error_records). A missing mandatory result blocks
    merge (D-010: the lead agent waits for every mandatory task).
    """
    run_dir = _run_dir(root, run_id)
    record = read_run(root, run_id)
    tasks_dir = run_dir / "tasks"

    results: list[dict[str, Any]] = []
    errors: list[dict] = []
    for task_id in record.mandatory_tasks:
        result_path = tasks_dir / task_id / "result.json"
        if not result_path.is_file():
            errors.append(
                {
                    "code": "RESEARCH_TASK_RESULT_MISSING",
                    "message": f"mandatory task {task_id!r} has no result.json yet",
                }
            )
            continue
        data = json.loads(result_path.read_text(encoding="utf-8"))
        schema_errors = schema.validate("subagent-result", data)
        if schema_errors:
            for se in schema_errors:
                errors.append(se.to_dict())
            continue
        results.append(data)
    return results, errors


def merge_run(root: Path, run_id: str) -> dict[str, Any]:
    """Merge all worker results, verify completeness, and persist merged/*."""
    run_dir = _run_dir(root, run_id)
    results, load_errors = load_worker_results(root, run_id)

    if load_errors:
        raise ToolEvalError(
            code=f"{ErrorFamily.RESEARCH}_MERGE_BLOCKED",
            message=(
                f"cannot merge: {len(load_errors)} task result(s) missing or invalid "
                f"(first: {load_errors[0]['message']})"
            ),
        )

    # The source registry accepted at the discovery gate is authoritative
    # (D-016: sources are registered once). Feature workers cite sources by
    # source_id; if a worker re-declares a registry source with slightly
    # different metadata that is not a real conflict - the registry wins. So we
    # drop worker re-declarations of registry ids (keeping any genuinely new
    # source a worker contributes) and union the accepted registry back in
    # rather than letting merge clobber or false-conflict it.
    accepted_sources_path = run_dir / "merged" / "sources.json"
    if accepted_sources_path.is_file():
        accepted = json.loads(accepted_sources_path.read_text(encoding="utf-8"))
        accepted_ids = {s["source_id"] for s in accepted}
        deduped: list[dict[str, Any]] = []
        for r in results:
            r = dict(r)
            if r.get("sources"):
                r["sources"] = [s for s in r["sources"] if s["source_id"] not in accepted_ids]
            deduped.append(r)
        results = [{"sources": accepted}, *deduped]

    merged, merge_errors = merge_results(results)
    completeness = verify_completeness(merged["feature_results"], taxonomy_feature_ids(root))
    all_errors = [e.to_dict() for e in merge_errors] + [e.to_dict() for e in completeness]

    merged_dir = run_dir / "merged"
    merged_dir.mkdir(parents=True, exist_ok=True)
    (merged_dir / "sources.json").write_text(
        json.dumps(merged["sources"], indent=2), encoding="utf-8"
    )
    (merged_dir / "feature-results.json").write_text(
        json.dumps(merged["feature_results"], indent=2), encoding="utf-8"
    )
    (merged_dir / "candidates.json").write_text(
        json.dumps({"candidates": merged["candidates"]}, indent=2), encoding="utf-8"
    )

    if not all_errors:
        record = read_run(root, run_id)
        transition(record, "merged", detail=f"{len(merged['feature_results'])} features merged")
        save_run(root, record)

    return {
        "run_id": run_id,
        "merged_feature_count": len(merged["feature_results"]),
        "source_count": len(merged["sources"]),
        "candidate_count": len(merged["candidates"]),
        "complete": not all_errors,
        "errors": all_errors,
    }
