"""Item 8: failed-run retention + resume-check (D-011)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tool_eval.runs.manager import fail_run, init_run, resume_check
from tool_eval.runs.retention import cleanup_failed_runs


def _make_failed_run(temp_project: Path, name: str, failed_at: datetime):
    run_dir = temp_project / ".work" / "failed-runs" / name
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "report.json").write_text(
        json.dumps({"run_id": name, "reason": "test", "failed_at": failed_at.strftime("%Y-%m-%dT%H:%M:%SZ")}),
        encoding="utf-8",
    )


def test_cleanup_removes_runs_older_than_max_age(temp_project: Path):
    now = datetime(2026, 7, 24, tzinfo=timezone.utc)
    _make_failed_run(temp_project, "old-run", now - timedelta(days=40))
    _make_failed_run(temp_project, "fresh-run", now - timedelta(days=2))

    summary = cleanup_failed_runs(temp_project, now=now)
    assert "old-run" in summary["removed"]
    assert "fresh-run" in summary["kept"]
    assert not (temp_project / ".work" / "failed-runs" / "old-run").exists()


def test_cleanup_enforces_max_count(temp_project: Path):
    now = datetime(2026, 7, 24, tzinfo=timezone.utc)
    # 22 recent runs; max_count default is 20
    for i in range(22):
        _make_failed_run(temp_project, f"run-{i:02d}", now - timedelta(hours=i))
    summary = cleanup_failed_runs(temp_project, now=now)
    assert len(summary["kept"]) == 20
    assert len(summary["removed"]) == 2
    # the two oldest (largest hour offset) are removed
    assert "run-21" in summary["removed"] and "run-20" in summary["removed"]


def test_cleanup_no_failed_runs_dir(temp_project: Path):
    import shutil

    shutil.rmtree(temp_project / ".work" / "failed-runs")
    summary = cleanup_failed_runs(temp_project)
    assert summary["removed"] == [] and summary["kept"] == []


def test_fail_run_moves_and_preserves_active_profile(temp_project: Path):
    run = init_run(temp_project, operation="research")
    report = fail_run(temp_project, run.run_id, reason="boom")
    assert report["reason"] == "boom"
    assert (temp_project / ".work" / "failed-runs" / run.run_id / "report.json").exists()
    assert not (temp_project / ".work" / "runs" / run.run_id).exists()


def test_resume_check_matches_frozen_revisions(temp_project: Path):
    run = init_run(temp_project, operation="research")
    result = resume_check(temp_project, run.run_id)
    assert result["resumable"] is True
    assert result["mismatches"] == {}


def test_resume_check_detects_revision_change(temp_project: Path):
    run = init_run(temp_project, operation="research")
    # bump the taxonomy revision on disk -> resume must be refused.
    # Read the current revision rather than assuming a fixed value: the shipped
    # taxonomy revision advances as features are curated in, so hard-coding it
    # here would silently no-op once it moves past the assumed number.
    tax = temp_project / "config" / "feature-taxonomy.yaml"
    text = tax.read_text(encoding="utf-8")
    match = re.search(r"^revision:\s*(\d+)", text, flags=re.MULTILINE)
    assert match, "taxonomy config must declare a top-level revision"
    current_rev = int(match.group(1))
    text = text.replace(match.group(0), f"revision: {current_rev + 1}", 1)
    tax.write_text(text, encoding="utf-8")
    result = resume_check(temp_project, run.run_id)
    assert result["resumable"] is False
    assert "feature-taxonomy.yaml" in result["mismatches"]
