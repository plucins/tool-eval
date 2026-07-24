"""Item 7: technical retries, bundle splitting, three repair rounds (D-011)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tool_eval.errors import ToolEvalError
from tool_eval.research.planner import Bundle
from tool_eval.research.repair import (
    MAX_REPAIR_ROUNDS,
    MAX_TECHNICAL_RETRIES,
    next_repair_round,
    plan_retry_or_split,
    prepare_repair,
    record_technical_retry,
)
from tool_eval.research.tasks import create_feature_tasks
from tool_eval.runs.manager import init_run, read_run


# --- technical retries + split ---------------------------------------------


def test_retry_while_under_cap_then_split():
    b = Bundle(bundle_id="feat-a-01", group="a", feature_ids=("x", "y"))
    assert plan_retry_or_split(b, 0)[0] == "retry"
    assert plan_retry_or_split(b, 1)[0] == "retry"
    action, bundles = plan_retry_or_split(b, 2)
    assert action == "split"
    assert [bb.feature_ids for bb in bundles] == [("x",), ("y",)]


def test_record_technical_retry_bounded(temp_project: Path):
    run = init_run(temp_project, operation="research")
    record = read_run(temp_project, run.run_id)
    assert record_technical_retry(record) is True   # 1
    assert record_technical_retry(record) is True   # 2
    assert record_technical_retry(record) is False  # capped
    assert record.retry_counters["technical_retries"] == MAX_TECHNICAL_RETRIES


# --- repair rounds ---------------------------------------------------------


def test_next_repair_round_increments_then_refuses():
    class R:
        retry_counters = {"repair_rounds": 0}

    r = R()
    for expected in (1, 2, 3):
        assert next_repair_round(r) == expected
        r.retry_counters["repair_rounds"] = expected
    with pytest.raises(ToolEvalError) as exc:
        next_repair_round(r)
    assert exc.value.code == "VALIDATION_REPAIR_LIMIT_EXCEEDED"


def test_prepare_repair_writes_manifest_and_advances(temp_project: Path):
    run = init_run(temp_project, operation="research")
    create_feature_tasks(temp_project, run.run_id)
    summary = prepare_repair(temp_project, run.run_id, ["inline_code_completion"])
    assert summary["round"] == 1
    manifest = json.loads(Path(summary["repair_manifest"]).read_text())
    assert manifest["feature_ids"] == ["inline_code_completion"]
    assert read_run(temp_project, run.run_id).state == "repair_in_progress"


def test_fourth_repair_round_prohibited(temp_project: Path):
    run = init_run(temp_project, operation="research")
    for _ in range(MAX_REPAIR_ROUNDS):
        prepare_repair(temp_project, run.run_id, ["inline_code_completion"])
    with pytest.raises(ToolEvalError) as exc:
        prepare_repair(temp_project, run.run_id, ["inline_code_completion"])
    assert exc.value.code == "VALIDATION_REPAIR_LIMIT_EXCEEDED"


def test_prepare_repair_requires_features(temp_project: Path):
    run = init_run(temp_project, operation="research")
    with pytest.raises(ToolEvalError) as exc:
        prepare_repair(temp_project, run.run_id, [])
    assert exc.value.code == "INPUT_NOTHING_TO_REPAIR"


def test_repair_counter_survives_reload(temp_project: Path):
    run = init_run(temp_project, operation="research")
    prepare_repair(temp_project, run.run_id, ["inline_code_completion"])
    reloaded = read_run(temp_project, run.run_id)
    assert reloaded.retry_counters["repair_rounds"] == 1
