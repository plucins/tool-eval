"""Assemble the staged ``profile.json`` + ``description.md`` (plan Sec 3.6 step 13).

Deterministic single-writer assembly (D-004): Python combines the merged,
already-validated research artifacts into the hybrid profile (D-007/D-016) and
stages it under ``<run>/publish/``. It invents nothing (D-005) - sources,
feature results, facts, use cases, and the per-section description prose all
come from the merged worker output / profile-writing input. The staged profile
is validated with the full profile gate before it is written; an invalid or
incomplete profile is never staged, so it can never be published (D-012).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tool_eval.config import load_config_bundle
from tool_eval.errors import ErrorFamily, ToolEvalError
from tool_eval.profiles.description import assemble_description
from tool_eval.profiles.validate import validate_profile
from tool_eval.research.pipeline import taxonomy_feature_ids
from tool_eval.research.sources import read_tool_identity, normalise_tool_id
from tool_eval.runs.manager import read_run, save_run, transition

SCHEMA_VERSION = "1.0.0"


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
            message=f"{what} not found at {path}; run the earlier phases first",
            path=str(path),
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_tool(
    run_dir: Path, tool_id: str | None, tool_name: str | None
) -> tuple[str, str]:
    identity = read_tool_identity(run_dir) or {}
    name = tool_name or identity.get("name")
    if not name:
        raise ToolEvalError(
            code=f"{ErrorFamily.INPUT}_TOOL_IDENTITY_MISSING",
            message="no tool name available; pass --tool-name or run create-source-task first",
        )
    tid = tool_id or identity.get("tool_id") or normalise_tool_id(name)
    return tid, name


def _collect_content(run_dir: Path, content_path: Path | None) -> dict[str, list]:
    """Gather additional_facts + use_cases from profile-writing results and/or a file.

    Deterministic dedup: profile-writing worker results first (sorted by task
    dir), then any explicit content file, keyed by their id fields.
    """
    facts: dict[str, dict[str, Any]] = {}
    use_cases: dict[str, dict[str, Any]] = {}
    issues: dict[str, dict[str, Any]] = {}

    def _absorb(payload: dict[str, Any]) -> None:
        for f in payload.get("additional_facts", []) or []:
            facts.setdefault(f["fact_id"], f)
        for uc in payload.get("use_cases", []) or []:
            use_cases.setdefault(uc["use_case_id"], uc)
        for issue in payload.get("unresolved_issues", []) or []:
            issues.setdefault(issue["issue_id"], issue)

    tasks_dir = run_dir / "tasks"
    if tasks_dir.is_dir():
        for task_dir in sorted(tasks_dir.iterdir()):
            manifest_path = task_dir / "task.json"
            result_path = task_dir / "result.json"
            if not manifest_path.is_file() or not result_path.is_file():
                continue
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("task_type") == "profile-writing":
                _absorb(json.loads(result_path.read_text(encoding="utf-8")))

    if content_path is not None:
        _absorb(_require_json(content_path, "content file"))

    return {
        "additional_facts": [facts[k] for k in sorted(facts)],
        "use_cases": [use_cases[k] for k in sorted(use_cases)],
        "unresolved_issues": [issues[k] for k in sorted(issues)],
    }


def _load_section_texts(run_dir: Path, sections_path: Path | None) -> dict[str, str]:
    if sections_path is not None:
        return _require_json(sections_path, "description-sections file")
    default = run_dir / "description-sections.json"
    if default.is_file():
        return json.loads(default.read_text(encoding="utf-8"))
    raise ToolEvalError(
        code=f"{ErrorFamily.INPUT}_DESCRIPTION_SECTIONS_MISSING",
        message=(
            "no description section text supplied; pass --sections or place "
            "description-sections.json in the run directory (profile-writing output)"
        ),
        path=str(default),
    )


def build_profile(
    root: Path,
    run_id: str,
    *,
    tool_id: str | None = None,
    tool_name: str | None = None,
    content_path: Path | None = None,
    sections_path: Path | None = None,
) -> dict[str, Any]:
    """Assemble and validate the staged profile. Returns a summary dict."""
    run_dir = _run_dir(root, run_id)
    record = read_run(root, run_id)
    bundle = load_config_bundle(root)

    tid, name = _resolve_tool(run_dir, tool_id, tool_name)
    sources = _require_json(run_dir / "merged" / "sources.json", "merged sources")
    feature_results = _require_json(
        run_dir / "merged" / "feature-results.json", "merged feature results"
    )
    content = _collect_content(run_dir, content_path)
    section_texts = _load_section_texts(run_dir, sections_path)

    sections_config = bundle.files["profile-sections.yaml"].data.get("sections", [])
    description_md, desc_errors = assemble_description(sections_config, section_texts)

    taxonomy_rev = record.effective_revisions.get(
        "feature-taxonomy.yaml", bundle.files["feature-taxonomy.yaml"].revision
    )
    profile: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "tool": {"tool_id": tid, "name": name},
        "research": {
            "run_id": run_id,
            "researched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "taxonomy_revision": taxonomy_rev,
            "template_revision": bundle.files["profile-sections.yaml"].revision,
            "source_policy_revision": bundle.files["source-policies.yaml"].revision,
            "profile_state": "current",
        },
        "sources": sources,
        "feature_results": feature_results,
        "additional_facts": content["additional_facts"],
        "use_cases": content["use_cases"],
        "unresolved_issues": content["unresolved_issues"],
    }

    profile_errors = validate_profile(profile, taxonomy_feature_ids=taxonomy_feature_ids(root))
    all_errors = [e.to_dict() for e in desc_errors] + profile_errors

    if all_errors:
        (run_dir / "validation-errors.json").write_text(
            json.dumps(all_errors, indent=2), encoding="utf-8"
        )
        return {
            "run_id": run_id,
            "tool_id": tid,
            "built": False,
            "errors": all_errors,
        }

    staging = run_dir / "publish"
    staging.mkdir(parents=True, exist_ok=True)
    (staging / "profile.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")
    (staging / "description.md").write_text(description_md, encoding="utf-8")

    transition(record, "profile_built", detail=f"tool={tid}")
    save_run(root, record)

    return {
        "run_id": run_id,
        "tool_id": tid,
        "built": True,
        "artifacts": [str(staging / "profile.json"), str(staging / "description.md")],
        "errors": [],
    }
