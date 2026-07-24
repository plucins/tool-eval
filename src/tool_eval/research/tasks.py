"""Create validated feature-research task manifests for a run (D-010/D-015).

This is the Python side of the worker-wave contract: it plans bundles from the
frozen taxonomy, writes one ``tasks/<task_id>/task.json`` manifest (plus an
``input.json``) per bundle, validates each manifest against ``task.schema.json``,
records the wave layout, and marks the mandatory task set on the run so merging
can later verify completeness. Workers (subagents) fill in ``result.json``;
Python never researches (D-005).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tool_eval.config import load_config_bundle
from tool_eval.errors import ErrorFamily, ToolEvalError
from tool_eval.paths import resolve_within
from tool_eval.research.planner import Bundle, plan_bundles, plan_waves
from tool_eval.runs.manager import read_run, save_run, transition
from tool_eval.validation import schema


def _taxonomy_features(root: Path) -> list[dict[str, Any]]:
    bundle = load_config_bundle(root)
    data = bundle.files["feature-taxonomy.yaml"].data
    features = data.get("features")
    if not isinstance(features, list) or not features:
        raise ToolEvalError(
            code=f"{ErrorFamily.CONFIG}_EMPTY_TAXONOMY",
            message="feature-taxonomy.yaml declares no features",
        )
    return features


def _bundling_params(root: Path) -> tuple[int, int, int]:
    bundle = load_config_bundle(root)
    runtime = bundle.files["runtime.yaml"].data
    bundling = runtime.get("bundling", {})
    concurrency = runtime.get("concurrency", {})
    min_size = int(bundling.get("min_features_per_bundle", 2))
    max_size = int(bundling.get("max_features_per_bundle", 4))
    max_concurrent = int(concurrency.get("max_concurrent_workers", 4))
    return min_size, max_size, max_concurrent


def create_feature_tasks(
    root: Path, run_id: str, isolate: list[str] | None = None
) -> dict[str, Any]:
    """Plan bundles and write validated task manifests into the run directory.

    Returns a summary dict: bundle count, wave layout, and manifest paths.
    """
    record = read_run(root, run_id)
    run_dir = root / ".work" / "runs" / run_id
    if not run_dir.is_dir():
        raise ToolEvalError(
            code=f"{ErrorFamily.INPUT}_RUN_NOT_FOUND",
            message=f"No run directory for {run_id!r}",
            path=str(run_dir),
        )

    features = _taxonomy_features(root)
    min_size, max_size, max_concurrent = _bundling_params(root)

    bundles = plan_bundles(
        features, min_size=min_size, max_size=max_size, isolate=isolate or []
    )
    waves = plan_waves(bundles, max_concurrent=max_concurrent)

    tasks_root = run_dir / "tasks"
    manifest_paths: list[str] = []
    for bundle in bundles:
        manifest = bundle.to_task_manifest(run_id)
        errors = schema.validate("task", manifest)
        if errors:
            raise ToolEvalError(
                code=f"{ErrorFamily.VALIDATION}_TASK_MANIFEST_INVALID",
                message=f"Planned task {bundle.bundle_id} failed schema: {errors[0].message}",
            )
        # resolve_within guards against any manifest id that would escape the run dir.
        task_dir = resolve_within(tasks_root, bundle.bundle_id)
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "task.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )
        (task_dir / "input.json").write_text(
            json.dumps(_task_input(features, bundle), indent=2), encoding="utf-8"
        )
        manifest_paths.append(str(task_dir / "task.json"))

    record.mandatory_tasks = [b.bundle_id for b in bundles]
    transition(
        record,
        "research_in_progress",
        detail=f"{len(bundles)} feature tasks in {len(waves)} wave(s)",
    )
    save_run(root, record)

    return {
        "run_id": run_id,
        "bundle_count": len(bundles),
        "wave_count": len(waves),
        "max_concurrent": max_concurrent,
        "waves": [[b.bundle_id for b in wave] for wave in waves],
        "manifest_paths": manifest_paths,
    }


def _task_input(features: list[dict[str, Any]], bundle: Bundle) -> dict[str, Any]:
    """The read-only research brief handed to a worker for its bundle.

    Contains only the taxonomy entries for the bundle's features (definitions,
    criteria, aliases, research questions) - no secrets, no host paths (D-017).
    """
    index = {f["feature_id"]: f for f in features}
    return {
        "bundle_id": bundle.bundle_id,
        "group": bundle.group,
        "features": [index[fid] for fid in bundle.feature_ids if fid in index],
    }
