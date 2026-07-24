"""Item 11: configurable bounded-work budgets (D-010/D-011).

Budgets are frozen into run state at init and enforced at the Python gates the
orchestrator calls; the deterministic core never runs the research loop itself.
These tests are offline and use the ``temp_project`` fixture (real config/).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tool_eval.errors import ToolEvalError
from tool_eval.research.repair import prepare_repair
from tool_eval.research.tasks import create_feature_tasks
from tool_eval.runs.manager import (
    DEFAULT_BUDGETS,
    init_run,
    load_budgets,
    read_run,
    run_status,
)


# --- config loading --------------------------------------------------------


def test_budgets_loaded_from_runtime_yaml(temp_project: Path):
    budgets = load_budgets(temp_project)
    # The shipped runtime.yaml sets the standard's hard caps as defaults.
    assert budgets == {
        "max_worker_tasks": 40,
        "max_technical_retries": 2,
        "max_repair_rounds": 3,
    }


def test_default_budgets_cover_every_key():
    # load_budgets always returns a value for each known key, even if config omits it.
    assert set(DEFAULT_BUDGETS) == {
        "max_worker_tasks",
        "max_technical_retries",
        "max_repair_rounds",
    }


# --- freezing at init + resume consistency ---------------------------------


def test_init_run_freezes_budgets_from_config(temp_project: Path):
    run = init_run(temp_project, operation="research")
    assert run.budgets == load_budgets(temp_project)

    # Frozen budgets survive a reload (resume stays consistent, D-011).
    reloaded = read_run(temp_project, run.run_id)
    assert reloaded.budgets == run.budgets

    on_disk = json.loads(
        (temp_project / ".work" / "runs" / run.run_id / "run.json").read_text()
    )
    assert on_disk["budgets"]["max_worker_tasks"] == 40


def test_explicit_budgets_override_config(temp_project: Path):
    run = init_run(
        temp_project,
        operation="research",
        budgets={"max_worker_tasks": 3, "max_technical_retries": 2, "max_repair_rounds": 1},
    )
    assert read_run(temp_project, run.run_id).budgets["max_repair_rounds"] == 1


# --- worker-task budget gate -----------------------------------------------


def test_worker_task_budget_exceeded_raises_and_writes_nothing(temp_project: Path):
    run = init_run(
        temp_project,
        operation="research",
        budgets={"max_worker_tasks": 1, "max_technical_retries": 2, "max_repair_rounds": 3},
    )
    with pytest.raises(ToolEvalError) as exc:
        create_feature_tasks(temp_project, run.run_id)
    assert exc.value.code == "BUDGET_TASKS_EXCEEDED"
    assert exc.value.retryable is False  # budget excess terminates without retry

    # The gate raises before any manifest is written.
    tasks_dir = temp_project / ".work" / "runs" / run.run_id / "tasks"
    assert not any(tasks_dir.iterdir())


def test_worker_task_budget_within_limit_creates_tasks(temp_project: Path):
    run = init_run(temp_project, operation="research")  # generous default (40)
    summary = create_feature_tasks(temp_project, run.run_id)
    assert summary["bundle_count"] >= 1
    tasks_dir = temp_project / ".work" / "runs" / run.run_id / "tasks"
    assert sum(1 for p in tasks_dir.iterdir() if p.is_dir()) == summary["bundle_count"]


# --- repair-round budget comes from the frozen run budget ------------------


def test_repair_rounds_use_frozen_budget(temp_project: Path):
    run = init_run(
        temp_project,
        operation="research",
        budgets={"max_worker_tasks": 40, "max_technical_retries": 2, "max_repair_rounds": 1},
    )
    summary = prepare_repair(temp_project, run.run_id, ["inline_code_completion"])
    assert summary["round"] == 1
    assert summary["max_rounds"] == 1  # reflects the frozen budget, not the constant

    with pytest.raises(ToolEvalError) as exc:
        prepare_repair(temp_project, run.run_id, ["inline_code_completion"])
    assert exc.value.code == "VALIDATION_REPAIR_LIMIT_EXCEEDED"


# --- run status surfaces used-vs-limit -------------------------------------


def test_run_status_surfaces_budget_status(temp_project: Path):
    run = init_run(temp_project, operation="research")
    create_feature_tasks(temp_project, run.run_id)

    status = run_status(temp_project, run.run_id)
    budget_status = status["budget_status"]

    assert budget_status["worker_tasks"]["limit"] == 40
    assert budget_status["worker_tasks"]["used"] >= 1
    assert budget_status["repair_rounds"] == {"used": 0, "limit": 3}
    assert budget_status["technical_retries"] == {"used": 0, "limit": 2}
