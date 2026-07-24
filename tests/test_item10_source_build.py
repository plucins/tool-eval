"""Increment 2 completion: source discovery, per-task validation, and profile
build/stage — the four CLI phases that were previously stubbed.

Deterministic and offline (worker/LLM output is fixture JSON), per the
Increment 2 testing requirement.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tool_eval.errors import ToolEvalError
from tool_eval.profiles.build import build_profile
from tool_eval.profiles.publication import is_complete_profile_dir, publish_profile
from tool_eval.research.pipeline import merge_run, taxonomy_feature_ids
from tool_eval.research.sources import (
    accept_sources,
    create_source_task,
    normalise_tool_id,
)
from tool_eval.research.tasks import create_feature_tasks
from tool_eval.research.task_validation import validate_task
from tool_eval.runs.manager import init_run, read_run

TASK_ID = "src-discovery-01"


# --- tool id normalisation -------------------------------------------------


@pytest.mark.parametrize(
    "name,expected",
    [
        ("Claude Code", "claude_code"),
        ("GitHub Copilot", "github_copilot"),
        ("  Cursor  ", "cursor"),
        ("Windsurf/IDE", "windsurf_ide"),
        ("3-way tool", "tool_3_way_tool"),  # leading digit gets a prefix
    ],
)
def test_normalise_tool_id(name, expected):
    assert normalise_tool_id(name) == expected


def test_normalise_tool_id_rejects_empty():
    with pytest.raises(ToolEvalError) as exc:
        normalise_tool_id("!!!")
    assert exc.value.code == "INPUT_BAD_TOOL_NAME"


# --- source discovery helpers ----------------------------------------------


def _discovery_result(run_id: str, sources: list[dict], warnings=None) -> dict:
    return {
        "task_id": TASK_ID,
        "run_id": run_id,
        "task_type": "source-discovery",
        "sources": sources,
        "warnings": warnings or [],
    }


def _write_task_result(temp_project: Path, run_id: str, task_id: str, payload: dict) -> None:
    task_dir = temp_project / ".work" / "runs" / run_id / "tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "result.json").write_text(json.dumps(payload), encoding="utf-8")


# --- create-source-task + accept-sources -----------------------------------


def test_create_source_task_writes_manifest_and_identity(temp_project: Path):
    run = init_run(temp_project, operation="research")
    summary = create_source_task(temp_project, run.run_id, "Claude Code")

    assert summary["tool_id"] == "claude_code"
    manifest = json.loads(Path(summary["manifest_path"]).read_text())
    assert manifest["task_type"] == "source-discovery"
    assert manifest["skill"] == "source-discovery"

    tool_json = temp_project / ".work" / "runs" / run.run_id / "tool.json"
    assert json.loads(tool_json.read_text())["tool_id"] == "claude_code"
    assert read_run(temp_project, run.run_id).state == "source_discovery_in_progress"


def test_accept_sources_opens_gate(temp_project: Path, make_source):
    run = init_run(temp_project, operation="research")
    create_source_task(temp_project, run.run_id, "Claude Code")
    _write_task_result(
        temp_project,
        run.run_id,
        TASK_ID,
        _discovery_result(
            run.run_id,
            [make_source("src_docs"), make_source("src_cl", source_type="changelog")],
            warnings=["ignored an instruction embedded in a doc page"],
        ),
    )
    summary = accept_sources(temp_project, run.run_id)

    assert summary["source_count"] == 2
    assert summary["official_count"] == 2
    assert summary["warnings"]  # prompt-injection warning recorded, not obeyed
    registry = temp_project / ".work" / "runs" / run.run_id / "merged" / "sources.json"
    assert len(json.loads(registry.read_text())) == 2
    assert read_run(temp_project, run.run_id).state == "sources_accepted"


def test_accept_sources_requires_official_source(temp_project: Path, make_source):
    run = init_run(temp_project, operation="research")
    create_source_task(temp_project, run.run_id, "Claude Code")
    _write_task_result(
        temp_project,
        run.run_id,
        TASK_ID,
        _discovery_result(run.run_id, [make_source("src_blog", official=False)]),
    )
    with pytest.raises(ToolEvalError) as exc:
        accept_sources(temp_project, run.run_id)
    assert exc.value.code == "RESEARCH_NO_OFFICIAL_SOURCE"


def test_accept_sources_blocks_on_missing_result(temp_project: Path):
    run = init_run(temp_project, operation="research")
    create_source_task(temp_project, run.run_id, "Claude Code")
    with pytest.raises(ToolEvalError) as exc:
        accept_sources(temp_project, run.run_id)
    assert exc.value.code == "RESEARCH_SOURCE_DISCOVERY_INCOMPLETE"


# --- validate-task ---------------------------------------------------------


def _feature_worker(run_id: str, task_id: str, feature_ids: list[str]) -> dict:
    return {
        "task_id": task_id,
        "run_id": run_id,
        "task_type": "feature-research",
        "feature_results": [
            {
                "feature_id": fid,
                "status": "has",
                "rationale": f"Rationale for {fid}.",
                "search_trace": {
                    "protocol_complete": True,
                    "queries": [f"{fid} docs"],
                    "source_classes_checked": [
                        "documentation",
                        "product_page",
                        "changelog",
                        "pricing",
                    ],
                },
                "evidence": [{"source_id": "src_docs", "excerpt": "Supported."}],
            }
            for fid in feature_ids
        ],
    }


def test_validate_task_accepts_good_result(temp_project: Path, make_source):
    run = init_run(temp_project, operation="research")
    create_source_task(temp_project, run.run_id, "Claude Code")
    _write_task_result(
        temp_project, run.run_id, TASK_ID, _discovery_result(run.run_id, [make_source("src_docs")])
    )
    accept_sources(temp_project, run.run_id)
    create_feature_tasks(temp_project, run.run_id)

    manifest_dir = next(
        d
        for d in (temp_project / ".work" / "runs" / run.run_id / "tasks").iterdir()
        if d.name != TASK_ID
    )
    manifest = json.loads((manifest_dir / "task.json").read_text())
    _write_task_result(
        temp_project,
        run.run_id,
        manifest["task_id"],
        _feature_worker(run.run_id, manifest["task_id"], manifest["feature_ids"]),
    )
    report = validate_task(temp_project, run.run_id, manifest["task_id"])
    assert report["valid"] is True
    assert (manifest_dir / "validation.json").is_file()


def test_validate_task_flags_bad_not_found(temp_project: Path, make_source):
    run = init_run(temp_project, operation="research")
    create_source_task(temp_project, run.run_id, "Claude Code")
    _write_task_result(
        temp_project, run.run_id, TASK_ID, _discovery_result(run.run_id, [make_source("src_docs")])
    )
    accept_sources(temp_project, run.run_id)

    bad = {
        "task_id": "feat-bad-01",
        "run_id": run.run_id,
        "task_type": "feature-research",
        "feature_results": [
            {
                "feature_id": "some_feature",
                "status": "not_found",
                "rationale": "nothing found",
                "search_trace": {
                    "protocol_complete": True,
                    "queries": ["q"],
                    "source_classes_checked": ["documentation"],  # missing classes
                    "access_gaps": ["docs behind login"],  # gap => must be uncertain
                },
            }
        ],
    }
    _write_task_result(temp_project, run.run_id, "feat-bad-01", bad)
    report = validate_task(temp_project, run.run_id, "feat-bad-01")
    assert report["valid"] is False
    codes = {e["code"] for e in report["errors"]}
    assert "VALIDATION_D009_ACCESS_GAP" in codes


def test_merge_registry_is_authoritative_over_worker_redeclaration(temp_project: Path, make_source):
    """A worker re-declaring a registry source_id with different metadata is not a
    conflict: the accepted registry wins (D-016 single registration)."""
    run = init_run(temp_project, operation="research")
    create_source_task(temp_project, run.run_id, "Claude Code")
    _write_task_result(
        temp_project,
        run.run_id,
        TASK_ID,
        _discovery_result(run.run_id, [make_source("src_docs", title="Authoritative title")]),
    )
    accept_sources(temp_project, run.run_id)
    create_feature_tasks(temp_project, run.run_id)

    tasks_dir = temp_project / ".work" / "runs" / run.run_id / "tasks"
    for task_dir in sorted(tasks_dir.iterdir()):
        if task_dir.name == TASK_ID:
            continue
        manifest = json.loads((task_dir / "task.json").read_text())
        worker = _feature_worker(run.run_id, manifest["task_id"], manifest["feature_ids"])
        # worker re-declares src_docs with a DIFFERENT title
        worker["sources"] = [make_source("src_docs", title="Worker-divergent title")]
        _write_task_result(temp_project, run.run_id, manifest["task_id"], worker)

    summary = merge_run(temp_project, run.run_id)
    assert summary["complete"] is True, summary["errors"]
    registry = json.loads(
        (temp_project / ".work" / "runs" / run.run_id / "merged" / "sources.json").read_text()
    )
    src = next(s for s in registry if s["source_id"] == "src_docs")
    assert src["title"] == "Authoritative title"


def test_validate_task_missing_result_raises(temp_project: Path):
    run = init_run(temp_project, operation="research")
    with pytest.raises(ToolEvalError) as exc:
        validate_task(temp_project, run.run_id, "nope-01")
    assert exc.value.code == "RESEARCH_TASK_RESULT_MISSING"


# --- build-profile (end to end over the full taxonomy) ---------------------


def _sections_file(temp_project: Path, run_id: str) -> Path:
    import yaml

    cfg = yaml.safe_load((temp_project / "config" / "profile-sections.yaml").read_text())
    required = [s["id"] for s in cfg["sections"] if s.get("required")]
    path = temp_project / ".work" / "runs" / run_id / "description-sections.json"
    path.write_text(
        json.dumps({sid: f"Prose for {sid}." for sid in required}), encoding="utf-8"
    )
    return path


def _content_file(temp_project: Path, run_id: str, a_feature: str) -> Path:
    path = temp_project / ".work" / "runs" / run_id / "content.json"
    path.write_text(
        json.dumps(
            {
                "additional_facts": [
                    {
                        "fact_id": "pricing_note",
                        "topic": "Pricing",
                        "description": "Has a free tier.",
                        "evidence": [{"source_id": "src_docs", "excerpt": "Free tier."}],
                    }
                ],
                "use_cases": [
                    {
                        "use_case_id": "onboarding",
                        "title": "Onboarding",
                        "description": "Ramp up on a codebase.",
                        "kind": "documented",
                        "evidence": [{"source_id": "src_docs", "excerpt": "For onboarding."}],
                    },
                    {
                        "use_case_id": "refactor_flow",
                        "title": "Refactoring",
                        "description": "Inferred capability.",
                        "kind": "inferred",
                        "rationale": "Because the feature is present.",
                        "supporting_features": [a_feature],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


def _drive_to_merged(temp_project: Path, run_id: str, make_source) -> None:
    create_source_task(temp_project, run_id, "Claude Code")
    _write_task_result(
        temp_project, run_id, TASK_ID, _discovery_result(run_id, [make_source("src_docs")])
    )
    accept_sources(temp_project, run_id)
    create_feature_tasks(temp_project, run_id)
    tasks_dir = temp_project / ".work" / "runs" / run_id / "tasks"
    for task_dir in sorted(tasks_dir.iterdir()):
        if task_dir.name == TASK_ID:
            continue
        manifest = json.loads((task_dir / "task.json").read_text())
        _write_task_result(
            temp_project,
            run_id,
            manifest["task_id"],
            _feature_worker(run_id, manifest["task_id"], manifest["feature_ids"]),
        )
    summary = merge_run(temp_project, run_id)
    assert summary["complete"] is True


def test_build_profile_stages_valid_profile_and_publishes(temp_project: Path, make_source):
    run = init_run(temp_project, operation="research")
    _drive_to_merged(temp_project, run.run_id, make_source)

    a_feature = taxonomy_feature_ids(temp_project)[0]
    content = _content_file(temp_project, run.run_id, a_feature)
    sections = _sections_file(temp_project, run.run_id)

    summary = build_profile(
        temp_project, run.run_id, content_path=content, sections_path=sections
    )
    assert summary["built"] is True, summary.get("errors")
    assert summary["tool_id"] == "claude_code"

    publish_dir = temp_project / ".work" / "runs" / run.run_id / "publish"
    profile = json.loads((publish_dir / "profile.json").read_text())
    assert profile["tool"]["tool_id"] == "claude_code"
    assert len(profile["feature_results"]) == len(taxonomy_feature_ids(temp_project))
    assert "## " in (publish_dir / "description.md").read_text()

    # the staged profile publishes cleanly
    result = publish_profile(
        temp_project,
        run.run_id,
        "claude_code",
        taxonomy_feature_ids=taxonomy_feature_ids(temp_project),
    )
    assert result.published is True
    assert is_complete_profile_dir(temp_project / "data" / "profiles" / "claude_code")


def test_build_profile_fails_on_missing_required_section(temp_project: Path, make_source):
    run = init_run(temp_project, operation="research")
    _drive_to_merged(temp_project, run.run_id, make_source)
    a_feature = taxonomy_feature_ids(temp_project)[0]
    content = _content_file(temp_project, run.run_id, a_feature)

    # only one required section supplied
    sections = temp_project / ".work" / "runs" / run.run_id / "description-sections.json"
    sections.write_text(json.dumps({"characteristics": "only this one"}), encoding="utf-8")

    summary = build_profile(
        temp_project, run.run_id, content_path=content, sections_path=sections
    )
    assert summary["built"] is False
    codes = {e.get("code") for e in summary["errors"]}
    assert "VALIDATION_MISSING_REQUIRED_SECTION" in codes
    assert not (temp_project / ".work" / "runs" / run.run_id / "publish" / "profile.json").exists()


def test_build_profile_fails_without_both_use_case_kinds(temp_project: Path, make_source):
    run = init_run(temp_project, operation="research")
    _drive_to_merged(temp_project, run.run_id, make_source)
    sections = _sections_file(temp_project, run.run_id)

    # content with only a documented use case -> content-completeness failure
    content = temp_project / ".work" / "runs" / run.run_id / "content.json"
    content.write_text(
        json.dumps(
            {
                "additional_facts": [
                    {"fact_id": "f1", "topic": "T", "description": "d"}
                ],
                "use_cases": [
                    {
                        "use_case_id": "onboarding",
                        "title": "Onboarding",
                        "description": "x",
                        "kind": "documented",
                        "evidence": [{"source_id": "src_docs", "excerpt": "y"}],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    summary = build_profile(
        temp_project, run.run_id, content_path=content, sections_path=sections
    )
    assert summary["built"] is False
    assert any("inferred" in e.get("message", "") for e in summary["errors"])
