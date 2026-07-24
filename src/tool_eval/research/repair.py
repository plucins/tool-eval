"""Bounded retry / bundle-splitting / repair-round logic (D-011).

Two distinct bounded loops, both enforced by Python so an agent cannot skip
them (D-003):

- *Technical* tool errors allow at most two retries of a task; if the problem
  repeats, the bundle is split into individual features and each is retried
  once more (D-010/D-011).
- *Structural / business-rule* errors go through at most three LLM repair
  rounds; the whole profile is validated after each round, and a fourth repair
  is prohibited (D-011; requirements criterion 9).

Counters live in ``run.json`` (``retry_counters``) so they survive resume.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tool_eval.errors import ErrorFamily, ToolEvalError
from tool_eval.research.planner import Bundle, split_bundle
from tool_eval.runs.manager import RunRecord, read_run, save_run, transition

MAX_TECHNICAL_RETRIES = 2
MAX_REPAIR_ROUNDS = 3


def plan_retry_or_split(
    bundle: Bundle,
    technical_retries_so_far: int,
    *,
    max_retries: int = MAX_TECHNICAL_RETRIES,
) -> tuple[str, list[Bundle]]:
    """Decide the response to a technical failure on ``bundle``.

    Returns ("retry", [bundle]) while retries remain, otherwise
    ("split", [singletons]) - the bundle is broken into single-feature tasks.
    """
    if technical_retries_so_far < max_retries:
        return "retry", [bundle]
    return "split", split_bundle(bundle)


def record_technical_retry(
    record: RunRecord, *, max_retries: int = MAX_TECHNICAL_RETRIES
) -> bool:
    """Increment the technical-retry counter; return True if a retry is allowed.

    Returns False once the cap is reached (caller should split the bundle).
    """
    current = record.retry_counters.get("technical_retries", 0)
    if current >= max_retries:
        return False
    record.retry_counters["technical_retries"] = current + 1
    return True


def next_repair_round(
    record: RunRecord, *, max_rounds: int = MAX_REPAIR_ROUNDS
) -> int:
    """Return the next repair-round number, or raise if the cap is exceeded.

    A fourth repair round is prohibited (requirements criterion 9): the run
    must be failed instead of repaired again.
    """
    current = record.retry_counters.get("repair_rounds", 0)
    if current >= max_rounds:
        raise ToolEvalError(
            code=f"{ErrorFamily.VALIDATION}_REPAIR_LIMIT_EXCEEDED",
            message=(
                f"repair round {current + 1} refused: at most {max_rounds} repair "
                "rounds are allowed; fail the run instead (D-011)"
            ),
        )
    return current + 1


def prepare_repair(
    root: Path, run_id: str, invalid_feature_ids: list[str]
) -> dict[str, Any]:
    """Open the next repair round for the given invalid features (D-011).

    Increments the repair-round counter (refusing a fourth), writes a repair
    manifest under ``repairs/<round>/`` listing the features to re-research,
    and advances the run state.
    """
    record = read_run(root, run_id)
    run_dir = root / ".work" / "runs" / run_id
    if not run_dir.is_dir():
        raise ToolEvalError(
            code=f"{ErrorFamily.INPUT}_RUN_NOT_FOUND",
            message=f"No run directory for {run_id!r}",
            path=str(run_dir),
        )
    if not invalid_feature_ids:
        raise ToolEvalError(
            code=f"{ErrorFamily.INPUT}_NOTHING_TO_REPAIR",
            message="prepare-repair requires at least one invalid feature_id",
        )

    round_number = next_repair_round(record)
    record.retry_counters["repair_rounds"] = round_number

    repair_dir = run_dir / "repairs" / str(round_number)
    repair_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": run_id,
        "round": round_number,
        "feature_ids": sorted(set(invalid_feature_ids)),
    }
    (repair_dir / "repair.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    transition(
        record,
        "repair_in_progress",
        detail=f"repair round {round_number} for {len(manifest['feature_ids'])} feature(s)",
    )
    save_run(root, record)

    return {
        "run_id": run_id,
        "round": round_number,
        "max_rounds": MAX_REPAIR_ROUNDS,
        "feature_ids": manifest["feature_ids"],
        "repair_manifest": str(repair_dir / "repair.json"),
    }
