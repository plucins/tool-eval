"""Item 2 (integration): create-feature-tasks writes validated manifests and
records the mandatory task set + wave layout on the run (D-010)."""

from __future__ import annotations

import json
from pathlib import Path

from tool_eval.research.sources import accept_sources, create_source_task
from tool_eval.research.tasks import create_feature_tasks
from tool_eval.runs.manager import init_run, read_run
from tool_eval.validation import schema


def test_create_feature_tasks_writes_valid_manifests(temp_project: Path):
    run = init_run(temp_project, operation="research")
    summary = create_feature_tasks(temp_project, run.run_id)

    assert summary["bundle_count"] >= 1
    assert summary["wave_count"] >= 1
    # every wave respects the concurrency limit
    assert all(len(w) <= summary["max_concurrent"] for w in summary["waves"])

    # every manifest exists and is schema-valid
    for path in summary["manifest_paths"]:
        manifest = json.loads(Path(path).read_text(encoding="utf-8"))
        assert schema.validate("task", manifest) == []


def test_mandatory_tasks_recorded_and_state_advanced(temp_project: Path):
    run = init_run(temp_project, operation="research")
    summary = create_feature_tasks(temp_project, run.run_id)

    reloaded = read_run(temp_project, run.run_id)
    assert reloaded.state == "research_in_progress"
    assert sorted(reloaded.mandatory_tasks) == sorted(
        b for wave in summary["waves"] for b in wave
    )


def test_every_taxonomy_feature_is_covered_exactly_once(temp_project: Path):
    run = init_run(temp_project, operation="research")
    summary = create_feature_tasks(temp_project, run.run_id)

    covered = []
    for path in summary["manifest_paths"]:
        manifest = json.loads(Path(path).read_text(encoding="utf-8"))
        covered.extend(manifest["feature_ids"])

    import yaml

    taxonomy = yaml.safe_load((temp_project / "config" / "feature-taxonomy.yaml").read_text())
    expected = [f["feature_id"] for f in taxonomy["features"]]

    assert sorted(covered) == sorted(expected)
    assert len(covered) == len(set(covered))


def test_input_brief_contains_no_host_paths(temp_project: Path):
    run = init_run(temp_project, operation="research")
    summary = create_feature_tasks(temp_project, run.run_id)
    task_dir = Path(summary["manifest_paths"][0]).parent
    brief = json.loads((task_dir / "input.json").read_text(encoding="utf-8"))
    assert "features" in brief and brief["features"]
    # the brief is taxonomy-only; no absolute paths leak into worker inputs
    assert str(temp_project) not in json.dumps(brief)


def test_input_brief_omits_known_sources_when_registry_missing(temp_project: Path):
    # No prior source-discovery/accept-sources for this run.
    run = init_run(temp_project, operation="research")
    summary = create_feature_tasks(temp_project, run.run_id)
    task_dir = Path(summary["manifest_paths"][0]).parent
    brief = json.loads((task_dir / "input.json").read_text(encoding="utf-8"))
    assert brief["known_sources"] == []
    assert brief["tool_id"] is None
    assert brief["tool_name"] is None


def test_input_brief_includes_known_sources_and_tool_identity(
    temp_project: Path, make_source
):
    run = init_run(temp_project, operation="research")
    discovery = create_source_task(temp_project, run.run_id, "Claude Code")

    task_dir = temp_project / ".work" / "runs" / run.run_id / "tasks" / discovery["task_id"]
    (task_dir / "result.json").write_text(
        json.dumps(
            {
                "task_id": discovery["task_id"],
                "run_id": run.run_id,
                "task_type": "source-discovery",
                "sources": [make_source("src_docs")],
                "warnings": [],
            }
        ),
        encoding="utf-8",
    )
    accept_sources(temp_project, run.run_id)

    summary = create_feature_tasks(temp_project, run.run_id)
    brief_dir = Path(summary["manifest_paths"][0]).parent
    brief = json.loads((brief_dir / "input.json").read_text(encoding="utf-8"))

    assert brief["tool_id"] == "claude_code"
    assert brief["tool_name"] == "Claude Code"
    assert brief["known_sources"] == [
        {
            "source_id": "src_docs",
            "url": "https://docs.example.com/src_docs",
            "title": "Doc src_docs",
            "source_type": "documentation",
            "official": True,
        }
    ]
