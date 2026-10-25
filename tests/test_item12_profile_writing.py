"""profile-writing task creation and its consumption by build-profile.

Deterministic and offline: worker output is fixture JSON, per the project's
testing standard. Covers the gap where a run reaching `merged` state had no
way to create a `profile-writing` task manifest, and `build-profile` had no
production path to source `description_sections` from a worker result.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tool_eval.errors import ToolEvalError
from tool_eval.profiles.build import build_profile
from tool_eval.research.pipeline import merge_run, taxonomy_feature_ids
from tool_eval.research.profile_writing import (
    DEFAULT_RELEASE_HISTORY_CAP,
    PROFILE_WRITING_TASK_ID,
    create_profile_writing_task,
)
from tool_eval.research.sources import accept_sources, create_source_task
from tool_eval.research.tasks import create_feature_tasks
from tool_eval.runs.manager import init_run, read_run

SOURCE_TASK_ID = "src-discovery-01"


def _discovery_result(run_id: str, sources: list[dict]) -> dict:
    return {
        "task_id": SOURCE_TASK_ID,
        "run_id": run_id,
        "task_type": "source-discovery",
        "sources": sources,
        "warnings": [],
    }


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


def _write_task_result(temp_project: Path, run_id: str, task_id: str, payload: dict) -> None:
    task_dir = temp_project / ".work" / "runs" / run_id / "tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "result.json").write_text(json.dumps(payload), encoding="utf-8")


def _drive_to_merged(temp_project: Path, run_id: str, make_source) -> str:
    """Drive a run from init through `research merge`; returns the tool_id."""
    summary = create_source_task(temp_project, run_id, "GitHub Copilot")
    _write_task_result(
        temp_project, run_id, SOURCE_TASK_ID, _discovery_result(run_id, [make_source("src_docs")])
    )
    accept_sources(temp_project, run_id)
    create_feature_tasks(temp_project, run_id)
    tasks_dir = temp_project / ".work" / "runs" / run_id / "tasks"
    for task_dir in sorted(tasks_dir.iterdir()):
        if task_dir.name == SOURCE_TASK_ID:
            continue
        manifest = json.loads((task_dir / "task.json").read_text())
        _write_task_result(
            temp_project,
            run_id,
            manifest["task_id"],
            _feature_worker(run_id, manifest["task_id"], manifest["feature_ids"]),
        )
    merge_summary = merge_run(temp_project, run_id)
    assert merge_summary["complete"] is True, merge_summary["errors"]
    return summary["tool_id"]


def _required_sections(temp_project: Path) -> list[str]:
    import yaml

    cfg = yaml.safe_load((temp_project / "config" / "profile-sections.yaml").read_text())
    return [s["id"] for s in cfg["sections"] if s.get("required")]


def _profile_writing_worker_result(
    run_id: str, required_sections: list[str], a_feature: str
) -> dict:
    return {
        "task_id": PROFILE_WRITING_TASK_ID,
        "run_id": run_id,
        "task_type": "profile-writing",
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
        "release_history": [
            {
                "release_id": "r1",
                "version": "1.2.0",
                "release_date": "2026-07-01",
                "summary": "Adds foo.",
                "evidence": [{"source_id": "src_docs", "excerpt": "1.2.0 adds foo."}],
            }
        ],
        "unresolved_issues": [
            {
                "issue_id": "gap_1",
                "kind": "coverage_gap",
                "description": "Could not confirm pricing tiers beyond the free tier.",
            }
        ],
        "description_sections": {sid: f"Prose for {sid}." for sid in required_sections},
    }


# --- create_profile_writing_task --------------------------------------------


def test_create_profile_writing_task_requires_tool_identity(temp_project: Path):
    run = init_run(temp_project, operation="research")
    with pytest.raises(ToolEvalError) as exc:
        create_profile_writing_task(temp_project, run.run_id)
    assert exc.value.code == "INPUT_TOOL_IDENTITY_MISSING"


def test_create_profile_writing_task_requires_merge_first(temp_project: Path, make_source):
    run = init_run(temp_project, operation="research")
    create_source_task(temp_project, run.run_id, "GitHub Copilot")
    _write_task_result(
        temp_project,
        run.run_id,
        SOURCE_TASK_ID,
        _discovery_result(run.run_id, [make_source("src_docs")]),
    )
    accept_sources(temp_project, run.run_id)

    with pytest.raises(ToolEvalError) as exc:
        create_profile_writing_task(temp_project, run.run_id)
    assert exc.value.code == "INPUT_MERGED_ARTIFACT_MISSING"


def test_create_profile_writing_task_first_pass_uses_most_recent_cap(
    temp_project: Path, make_source
):
    run = init_run(temp_project, operation="research")
    tool_id = _drive_to_merged(temp_project, run.run_id, make_source)
    assert not (temp_project / "data" / "profiles" / tool_id / "profile.json").exists()

    summary = create_profile_writing_task(temp_project, run.run_id)
    assert summary["tool_id"] == tool_id
    assert summary["task_id"] == PROFILE_WRITING_TASK_ID

    manifest = json.loads(Path(summary["manifest_path"]).read_text())
    assert manifest["task_type"] == "profile-writing"
    assert manifest["skill"] == "profile-writing"
    assert manifest["inputs"]["release_history"] == {
        "mode": "most_recent",
        "max_items": DEFAULT_RELEASE_HISTORY_CAP,
    }
    assert manifest["inputs"]["feature_results"]
    assert manifest["inputs"]["known_sources"][0]["source_id"] == "src_docs"
    assert {s["id"] for s in manifest["inputs"]["sections"]} >= set(
        _required_sections(temp_project)
    )
    assert read_run(temp_project, run.run_id).state == "profile_writing_in_progress"


def test_create_profile_writing_task_reresearch_uses_since_date_cap(
    temp_project: Path, make_source
):
    """since_date mode only applies when the prior profile actually captured
    releases - the cutoff is the latest captured release_date, not the
    research timestamp (see `_release_history_directive`'s docstring for why
    researched_at is the wrong basis)."""
    run = init_run(temp_project, operation="research")
    tool_id = _drive_to_merged(temp_project, run.run_id, make_source)

    published_dir = temp_project / "data" / "profiles" / tool_id
    published_dir.mkdir(parents=True, exist_ok=True)
    (published_dir / "profile.json").write_text(
        json.dumps(
            {
                "research": {"researched_at": "2026-07-01T00:00:00Z"},
                "release_history": [
                    {
                        "release_id": "r1",
                        "version": "1.2.0",
                        "release_date": "2026-06-15",
                        "summary": "Adds foo.",
                        "evidence": [{"source_id": "src_docs", "excerpt": "1.2.0 adds foo."}],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    summary = create_profile_writing_task(temp_project, run.run_id)
    manifest = json.loads(Path(summary["manifest_path"]).read_text())
    assert manifest["inputs"]["release_history"] == {
        "mode": "since_date",
        "since_date": "2026-06-15",
    }


def test_create_profile_writing_task_reresearch_with_no_prior_releases_uses_most_recent_cap(
    temp_project: Path, make_source
):
    """Regression test: a re-research pass whose prior profile has an empty
    (or missing) release_history must NOT get since_date-capped off
    researched_at - that would permanently starve the section to at most one
    entry per pass whenever an earlier pass under-captured it (e.g. due to a
    tooling gap like missing WebFetch access)."""
    run = init_run(temp_project, operation="research")
    tool_id = _drive_to_merged(temp_project, run.run_id, make_source)

    published_dir = temp_project / "data" / "profiles" / tool_id
    published_dir.mkdir(parents=True, exist_ok=True)
    (published_dir / "profile.json").write_text(
        json.dumps(
            {"research": {"researched_at": "2026-07-24T09:42:45Z"}, "release_history": []}
        ),
        encoding="utf-8",
    )

    summary = create_profile_writing_task(temp_project, run.run_id)
    manifest = json.loads(Path(summary["manifest_path"]).read_text())
    assert manifest["inputs"]["release_history"] == {
        "mode": "most_recent",
        "max_items": DEFAULT_RELEASE_HISTORY_CAP,
    }


# --- build-profile consuming a profile-writing result end to end -----------


def test_build_profile_sources_sections_from_profile_writing_result(
    temp_project: Path, make_source
):
    run = init_run(temp_project, operation="research")
    tool_id = _drive_to_merged(temp_project, run.run_id, make_source)
    create_profile_writing_task(temp_project, run.run_id)

    a_feature = taxonomy_feature_ids(temp_project)[0]
    required_sections = _required_sections(temp_project)
    _write_task_result(
        temp_project,
        run.run_id,
        PROFILE_WRITING_TASK_ID,
        _profile_writing_worker_result(run.run_id, required_sections, a_feature),
    )

    # No --content / --sections: the production path must source everything
    # from the profile-writing task result alone.
    summary = build_profile(temp_project, run.run_id)
    assert summary["built"] is True, summary.get("errors")
    assert summary["tool_id"] == tool_id

    publish_dir = temp_project / ".work" / "runs" / run.run_id / "publish"
    profile = json.loads((publish_dir / "profile.json").read_text())
    assert profile["additional_facts"][0]["fact_id"] == "pricing_note"
    assert profile["use_cases"][0]["use_case_id"] == "onboarding"
    assert profile["release_history"][0]["release_id"] == "r1"
    assert profile["unresolved_issues"][0]["issue_id"] == "gap_1"

    description = (publish_dir / "description.md").read_text()
    for sid in required_sections:
        assert f"Prose for {sid}." in description


def test_build_profile_missing_sections_without_profile_writing_task(
    temp_project: Path, make_source
):
    run = init_run(temp_project, operation="research")
    _drive_to_merged(temp_project, run.run_id, make_source)

    with pytest.raises(ToolEvalError) as exc:
        build_profile(temp_project, run.run_id)
    assert exc.value.code == "INPUT_DESCRIPTION_SECTIONS_MISSING"


@pytest.mark.parametrize("explicit_content", [False, True])
def test_build_profile_registers_content_sources(
    temp_project: Path, make_source, explicit_content: bool
):
    run = init_run(temp_project, operation="research")
    _drive_to_merged(temp_project, run.run_id, make_source)
    create_profile_writing_task(temp_project, run.run_id)
    payload = _profile_writing_worker_result(
        run.run_id, _required_sections(temp_project), taxonomy_feature_ids(temp_project)[0]
    )
    payload["sources"] = [make_source("src_new"), make_source("src_docs"), make_source("src_new")]
    for key in ("additional_facts", "use_cases", "release_history"):
        for item in payload[key]:
            for evidence in item.get("evidence", []):
                evidence["source_id"] = "src_new"
    payload["unresolved_issues"][0]["related_source_ids"] = ["src_new"]
    run_dir = temp_project / ".work" / "runs" / run.run_id
    merged_sources_before = (run_dir / "merged" / "sources.json").read_bytes()
    content_path = None
    if explicit_content:
        content_path = run_dir / "content.json"
        content_path.write_text(json.dumps(payload), encoding="utf-8")
    else:
        _write_task_result(temp_project, run.run_id, PROFILE_WRITING_TASK_ID, payload)

    summary = build_profile(temp_project, run.run_id, content_path=content_path)

    assert summary["built"] is True, summary["errors"]
    profile = json.loads((run_dir / "publish" / "profile.json").read_text())
    assert profile["sources"] == [make_source("src_docs"), make_source("src_new")]
    assert (run_dir / "merged" / "sources.json").read_bytes() == merged_sources_before
    assert profile["additional_facts"][0]["evidence"][0]["source_id"] == "src_new"
    assert profile["release_history"][0]["evidence"][0]["source_id"] == "src_new"
    assert profile["unresolved_issues"][0]["related_source_ids"] == ["src_new"]


@pytest.mark.parametrize("conflicts_with_merged", [False, True])
def test_build_profile_rejects_conflicting_content_sources(
    temp_project: Path, make_source, conflicts_with_merged: bool
):
    run = init_run(temp_project, operation="research")
    _drive_to_merged(temp_project, run.run_id, make_source)
    create_profile_writing_task(temp_project, run.run_id)
    payload = _profile_writing_worker_result(
        run.run_id, _required_sections(temp_project), taxonomy_feature_ids(temp_project)[0]
    )
    source_id = "src_docs" if conflicts_with_merged else "src_new"
    original = make_source(source_id)
    conflicting = {**original, "title": "Conflicting title"}
    payload["sources"] = [conflicting] if conflicts_with_merged else [original, conflicting]
    _write_task_result(temp_project, run.run_id, PROFILE_WRITING_TASK_ID, payload)

    summary = build_profile(temp_project, run.run_id)

    assert summary["built"] is False
    assert any(error["code"] == "VALIDATION_SOURCE_CONFLICT" for error in summary["errors"])
    assert not (temp_project / ".work" / "runs" / run.run_id / "publish").exists()
