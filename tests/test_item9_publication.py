"""Item 9: staging, rollback, safe replacement + recovery (D-012)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tool_eval.errors import ToolEvalError
from tool_eval.profiles import publication
from tool_eval.profiles.publication import (
    is_complete_profile_dir,
    list_profiles,
    publish_profile,
    recover,
)
from tool_eval.runs.manager import init_run


def _stage(temp_project: Path, run_id: str, profile: dict, desc: str = "# Desc\n\n## Characteristics\n\nx\n"):
    staging = temp_project / ".work" / "runs" / run_id / "publish"
    staging.mkdir(parents=True, exist_ok=True)
    (staging / "profile.json").write_text(json.dumps(profile), encoding="utf-8")
    (staging / "description.md").write_text(desc, encoding="utf-8")


def test_publish_creates_active_profile(temp_project: Path, valid_profile):
    run = init_run(temp_project, operation="research")
    _stage(temp_project, run.run_id, valid_profile)
    result = publish_profile(temp_project, run.run_id, "example_tool")
    assert result.published is True
    target = temp_project / "data" / "profiles" / "example_tool"
    assert is_complete_profile_dir(target)
    # no journal or backup left behind
    assert not (temp_project / "data" / "profiles" / ".publish-journal" / "example_tool.json").exists()


def test_publish_replaces_and_keeps_no_backup(temp_project: Path, valid_profile):
    run = init_run(temp_project, operation="research")
    # first publish
    _stage(temp_project, run.run_id, valid_profile)
    publish_profile(temp_project, run.run_id, "example_tool")
    # second publish with a changed field
    v2 = json.loads(json.dumps(valid_profile))
    v2["tool"]["name"] = "Example Tool v2"
    run2 = init_run(temp_project, operation="research")
    _stage(temp_project, run2.run_id, v2)
    publish_profile(temp_project, run2.run_id, "example_tool")

    active = json.loads(
        (temp_project / "data" / "profiles" / "example_tool" / "profile.json").read_text()
    )
    assert active["tool"]["name"] == "Example Tool v2"
    assert not (temp_project / ".work" / "runs" / run2.run_id / "publish-backup" / "example_tool").exists()


def test_invalid_profile_does_not_touch_active(temp_project: Path, valid_profile):
    # publish a good one first
    run = init_run(temp_project, operation="research")
    _stage(temp_project, run.run_id, valid_profile)
    publish_profile(temp_project, run.run_id, "example_tool")
    good_name = json.loads(
        (temp_project / "data" / "profiles" / "example_tool" / "profile.json").read_text()
    )["tool"]["name"]

    # now stage a broken profile (unknown source ref) and try to publish
    broken = json.loads(json.dumps(valid_profile))
    broken["feature_results"][0]["evidence"][0]["source_id"] = "src_missing"
    run2 = init_run(temp_project, operation="research")
    _stage(temp_project, run2.run_id, broken)
    result = publish_profile(temp_project, run2.run_id, "example_tool")

    assert result.published is False
    assert result.validation_errors
    # active profile is unchanged
    still = json.loads(
        (temp_project / "data" / "profiles" / "example_tool" / "profile.json").read_text()
    )["tool"]["name"]
    assert still == good_name


def test_rollback_restores_previous_on_write_failure(temp_project: Path, valid_profile, monkeypatch):
    run = init_run(temp_project, operation="research")
    _stage(temp_project, run.run_id, valid_profile)
    publish_profile(temp_project, run.run_id, "example_tool")
    original = (temp_project / "data" / "profiles" / "example_tool" / "profile.json").read_text()

    # make the copy step fail mid-replacement
    import tool_eval.profiles.publication as pub

    calls = {"n": 0}
    real_copy = pub.shutil.copy2

    def boom(src, dst):
        calls["n"] += 1
        raise OSError("disk full")

    monkeypatch.setattr(pub.shutil, "copy2", boom)

    run2 = init_run(temp_project, operation="research")
    _stage(temp_project, run2.run_id, valid_profile)
    with pytest.raises(ToolEvalError) as exc:
        publish_profile(temp_project, run2.run_id, "example_tool")
    assert exc.value.code == "PUBLISH_REPLACE_FAILED"

    # previous active profile restored
    restored = (temp_project / "data" / "profiles" / "example_tool" / "profile.json").read_text()
    assert restored == original


def test_recover_restores_incomplete_replacement(temp_project: Path, valid_profile):
    run = init_run(temp_project, operation="research")
    _stage(temp_project, run.run_id, valid_profile)
    publish_profile(temp_project, run.run_id, "example_tool")

    target = temp_project / "data" / "profiles" / "example_tool"
    # simulate a crash: backup exists, active dir emptied, journal says written
    backup = temp_project / ".work" / "runs" / run.run_id / "publish-backup" / "example_tool"
    import shutil

    shutil.copytree(target, backup)
    shutil.rmtree(target)
    jdir = temp_project / "data" / "profiles" / ".publish-journal"
    jdir.mkdir(parents=True, exist_ok=True)
    (jdir / "example_tool.json").write_text(
        json.dumps(
            {
                "tool_id": "example_tool",
                "run_id": run.run_id,
                "target": str(target),
                "backup": str(backup),
                "phase": "backed_up",
            }
        ),
        encoding="utf-8",
    )

    actions = recover(temp_project)
    assert any(a["action"] == "restored_backup" for a in actions)
    assert is_complete_profile_dir(target)


def test_recover_clears_stale_journal_when_target_complete(temp_project: Path, valid_profile):
    run = init_run(temp_project, operation="research")
    _stage(temp_project, run.run_id, valid_profile)
    publish_profile(temp_project, run.run_id, "example_tool")

    target = temp_project / "data" / "profiles" / "example_tool"
    jdir = temp_project / "data" / "profiles" / ".publish-journal"
    jdir.mkdir(parents=True, exist_ok=True)
    (jdir / "example_tool.json").write_text(
        json.dumps({"tool_id": "example_tool", "run_id": run.run_id, "target": str(target), "backup": "nonexistent", "phase": "written"}),
        encoding="utf-8",
    )
    actions = recover(temp_project)
    assert any(a["action"] == "cleared_stale_journal" for a in actions)


def test_list_profiles(temp_project: Path, valid_profile):
    run = init_run(temp_project, operation="research")
    _stage(temp_project, run.run_id, valid_profile)
    publish_profile(temp_project, run.run_id, "example_tool")
    listed = list_profiles(temp_project)
    assert any(p["tool_id"] == "example_tool" and p["complete"] for p in listed)
