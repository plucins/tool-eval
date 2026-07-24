"""Run lifecycle: init, status, resume-check, fail (D-011).

A run is the only unit of work Python tracks end to end. `run.json` freezes
the configuration revisions/hashes in effect when the run started, so that
resuming later can detect whether the active taxonomy/template/schema/policy
state still matches (D-011).
"""

from __future__ import annotations

import json
import shutil
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tool_eval.config import load_config_bundle
from tool_eval.errors import ErrorFamily, ToolEvalError

RUN_STATE_INITIALIZED = "initialized"
RUN_STATE_FAILED = "failed"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_run_id(operation: str) -> str:
    # Lowercase ASCII + digits + hyphens only, per D-016 identifier conventions.
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{operation}-{stamp}-{uuid.uuid4().hex[:8]}"


@dataclass
class TransitionRecord:
    state: str
    at: str
    detail: str = ""


@dataclass
class RunRecord:
    run_id: str
    operation: str
    state: str
    created_at: str
    updated_at: str
    initial_revisions: dict[str, int]
    effective_revisions: dict[str, int]
    config_hashes: dict[str, str]
    mandatory_tasks: list[str] = field(default_factory=list)
    retry_counters: dict[str, int] = field(
        default_factory=lambda: {"technical_retries": 0, "repair_rounds": 0}
    )
    budgets: dict[str, Any] = field(default_factory=dict)
    transitions: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _run_dir(root: Path, run_id: str) -> Path:
    return root / ".work" / "runs" / run_id


def _run_json_path(root: Path, run_id: str) -> Path:
    return _run_dir(root, run_id) / "run.json"


def init_run(root: Path, operation: str, budgets: dict[str, Any] | None = None) -> RunRecord:
    """Create a new run directory, freezing the current config revisions/hashes."""
    bundle = load_config_bundle(root)
    revisions = bundle.revisions()
    now = _utc_now_iso()
    run_id = _new_run_id(operation)

    record = RunRecord(
        run_id=run_id,
        operation=operation,
        state=RUN_STATE_INITIALIZED,
        created_at=now,
        updated_at=now,
        initial_revisions=revisions,
        effective_revisions=dict(revisions),
        config_hashes=bundle.hashes(),
        budgets=budgets or {},
        transitions=[
            TransitionRecord(
                state=RUN_STATE_INITIALIZED, at=now, detail="run created"
            ).__dict__
        ],
    )

    run_dir = _run_dir(root, run_id)
    (run_dir / "frozen-config").mkdir(parents=True, exist_ok=True)
    (run_dir / "tasks").mkdir(parents=True, exist_ok=True)
    (run_dir / "merged").mkdir(parents=True, exist_ok=True)

    run_json_path = _run_json_path(root, run_id)
    run_json_path.write_text(json.dumps(record.to_dict(), indent=2), encoding="utf-8")

    return record


def save_run(root: Path, record: RunRecord) -> Path:
    """Persist a run record back to its run.json (single writer: Python)."""
    record.updated_at = _utc_now_iso()
    path = _run_json_path(root, record.run_id)
    path.write_text(json.dumps(record.to_dict(), indent=2), encoding="utf-8")
    return path


def transition(record: RunRecord, state: str, detail: str = "") -> None:
    """Record a state transition on the run (in memory; caller saves)."""
    now = _utc_now_iso()
    record.state = state
    record.updated_at = now
    record.transitions.append(
        TransitionRecord(state=state, at=now, detail=detail).__dict__
    )


def read_run(root: Path, run_id: str) -> RunRecord:
    path = _run_json_path(root, run_id)
    if not path.is_file():
        raise ToolEvalError(
            code=f"{ErrorFamily.INPUT}_RUN_NOT_FOUND",
            message=f"No run.json found for run_id {run_id!r}",
            path=str(path),
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    return RunRecord(**data)


def run_status(root: Path, run_id: str) -> dict[str, Any]:
    record = read_run(root, run_id)
    return record.to_dict()


def resume_check(root: Path, run_id: str) -> dict[str, Any]:
    """Check whether the run's frozen config state still matches the current one.

    A controlled taxonomy revision bump recorded as an explicit transition in
    the run (curation acceptance) is not, by itself, a mismatch; this check
    only compares the run's `effective_revisions` (not `initial_revisions`)
    against the current config on disk.
    """
    record = read_run(root, run_id)
    current = load_config_bundle(root)
    current_revisions = current.revisions()

    mismatches = {
        name: {"run": record.effective_revisions.get(name), "current": current_rev}
        for name, current_rev in current_revisions.items()
        if record.effective_revisions.get(name) != current_rev
    }

    return {
        "run_id": run_id,
        "resumable": not mismatches,
        "mismatches": mismatches,
    }


def fail_run(root: Path, run_id: str, reason: str) -> dict[str, Any]:
    """Move a run to .work/failed-runs/<run_id>/ and record the failure reason."""
    run_dir = _run_dir(root, run_id)
    if not run_dir.is_dir():
        raise ToolEvalError(
            code=f"{ErrorFamily.INPUT}_RUN_NOT_FOUND",
            message=f"No run directory found for run_id {run_id!r}",
            path=str(run_dir),
        )

    record = read_run(root, run_id)
    record.state = RUN_STATE_FAILED
    record.updated_at = _utc_now_iso()
    record.transitions.append(
        TransitionRecord(state=RUN_STATE_FAILED, at=record.updated_at, detail=reason).__dict__
    )
    (run_dir / "run.json").write_text(
        json.dumps(record.to_dict(), indent=2), encoding="utf-8"
    )

    failed_root = root / ".work" / "failed-runs"
    failed_root.mkdir(parents=True, exist_ok=True)
    destination = failed_root / run_id
    if destination.exists():
        shutil.rmtree(destination)
    shutil.move(str(run_dir), str(destination))

    report = {
        "run_id": run_id,
        "reason": reason,
        "failed_at": record.updated_at,
    }
    (destination / "report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    return report
