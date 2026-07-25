"""Profile-writing task creation: the run's content-authoring phase (D-016).

Mirrors :func:`tool_eval.research.sources.create_source_task` - a single
deterministic Python operation plans one ``profile-writing`` task manifest,
inlining everything a worker needs (tool identity, the accepted source
registry, the merged feature results, and the description-section /
additional-fact-section configuration) so the worker never has to read
repository config files itself. A ``tool-eval-worker`` fills in ``result.json``
with ``additional_facts``, ``use_cases``, ``release_history``,
``unresolved_issues``, and ``description_sections``; ``profiles/build.py``
consumes that result directly (no separate merge step for this task type).

Python never researches or writes prose (D-005); it only prepares the
contract.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tool_eval.config import load_config_bundle
from tool_eval.errors import ErrorFamily, ToolEvalError
from tool_eval.paths import resolve_within
from tool_eval.research.sources import project_known_sources, read_tool_identity
from tool_eval.runs.manager import read_run, save_run, transition
from tool_eval.validation import schema

PROFILE_WRITING_TASK_ID = "profile-writing-01"

# Used only on a tool's first-ever research pass (no prior published profile);
# a re-research pass instead caps by date (see `_release_history_directive`).
DEFAULT_RELEASE_HISTORY_CAP = 10


def _run_dir(root: Path, run_id: str) -> Path:
    run_dir = root / ".work" / "runs" / run_id
    if not run_dir.is_dir():
        raise ToolEvalError(
            code=f"{ErrorFamily.INPUT}_RUN_NOT_FOUND",
            message=f"No run directory for {run_id!r}",
            path=str(run_dir),
        )
    return run_dir


def _require_json(path: Path, what: str) -> Any:
    if not path.is_file():
        raise ToolEvalError(
            code=f"{ErrorFamily.INPUT}_MERGED_ARTIFACT_MISSING",
            message=f"{what} not found at {path}; run `research merge` first",
            path=str(path),
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _release_history_directive(root: Path, tool_id: str) -> dict[str, Any]:
    """Build the unambiguous release-history capture directive (D3).

    ``since_date`` mode is only safe when the previous profile actually
    captured release entries: it caps capture to releases newer than the
    latest one already on file, so nothing already covered gets re-fetched.
    Basing the cutoff on ``research.researched_at`` instead (the date the
    *research ran*, not the date releases were captured through) is wrong
    whenever that prior pass captured little or nothing - e.g. because a
    tooling limitation (no WebFetch) starved that pass's release-history
    section. In that case ``since_date`` would keep re-applying a
    near-today cutoff forever, permanently limiting the section to at most
    one entry per pass instead of ever backfilling it. So: no prior
    profile, or a prior profile with an empty/missing `release_history`,
    is treated as needing a first-ever, count-capped pass, regardless of
    whether it is technically a re-research run.
    """
    published_path = root / "data" / "profiles" / tool_id / "profile.json"
    if published_path.is_file():
        published = json.loads(published_path.read_text(encoding="utf-8"))
        existing_releases = published.get("release_history") or []
        dates = [r["release_date"] for r in existing_releases if r.get("release_date")]
        if dates:
            return {"mode": "since_date", "since_date": max(dates)}
    return {"mode": "most_recent", "max_items": DEFAULT_RELEASE_HISTORY_CAP}


def create_profile_writing_task(root: Path, run_id: str) -> dict[str, Any]:
    """Write the ``profile-writing`` task manifest for the run's tool.

    Requires source-discovery and feature-research to already be merged
    (``merged/sources.json`` / ``merged/feature-results.json``), matching
    where this phase sits in the workflow (plan Sec 3.6 step 5).
    """
    run_dir = _run_dir(root, run_id)
    record = read_run(root, run_id)

    identity = read_tool_identity(run_dir)
    if not identity or not identity.get("tool_id"):
        raise ToolEvalError(
            code=f"{ErrorFamily.INPUT}_TOOL_IDENTITY_MISSING",
            message="no tool identity recorded for this run; run `create-source-task` first",
        )
    tool_id = identity["tool_id"]
    tool_name = identity.get("name", tool_id)

    _require_json(run_dir / "merged" / "sources.json", "merged sources")
    feature_results = _require_json(
        run_dir / "merged" / "feature-results.json", "merged feature results"
    )

    bundle = load_config_bundle(root)
    sections_config = bundle.files["profile-sections.yaml"].data.get("sections", [])
    fact_sections_config = bundle.files["additional-fact-sections.yaml"].data.get(
        "sections", []
    )

    manifest = {
        "task_id": PROFILE_WRITING_TASK_ID,
        "run_id": run_id,
        "task_type": "profile-writing",
        "skill": "profile-writing",
        "inputs": {
            "tool_id": tool_id,
            "tool_name": tool_name,
            "known_sources": project_known_sources(run_dir),
            "feature_results": feature_results,
            "sections": sections_config,
            "additional_fact_sections": fact_sections_config,
            "release_history": _release_history_directive(root, tool_id),
        },
        "output_path": "result.json",
    }
    errors = schema.validate("task", manifest)
    if errors:
        raise ToolEvalError(
            code=f"{ErrorFamily.VALIDATION}_TASK_MANIFEST_INVALID",
            message=f"profile-writing manifest failed schema: {errors[0].message}",
        )

    task_dir = resolve_within(run_dir / "tasks", PROFILE_WRITING_TASK_ID)
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "task.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (task_dir / "input.json").write_text(
        json.dumps(manifest["inputs"], indent=2), encoding="utf-8"
    )

    transition(record, "profile_writing_in_progress", detail=f"tool={tool_id}")
    save_run(root, record)

    return {
        "run_id": run_id,
        "tool_id": tool_id,
        "task_id": PROFILE_WRITING_TASK_ID,
        "manifest_path": str(task_dir / "task.json"),
    }
