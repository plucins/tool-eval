"""Failed-run retention (D-011).

A permanently failed run is kept under ``.work/failed-runs/<run_id>/`` for
post-mortem, but not forever. Default retention is 30 days or the latest 20
failed runs, whichever is tighter, and is configurable via
``runtime.yaml: failed_run_retention``. Cleanup is deterministic: it orders
failed runs by their recorded ``failed_at`` (falling back to directory mtime),
keeps the newest ``max_count``, and drops anything older than ``max_age_days``.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from tool_eval.config import load_config_bundle


def _retention_params(root: Path) -> tuple[int, int]:
    bundle = load_config_bundle(root)
    runtime = bundle.files["runtime.yaml"].data
    ret = runtime.get("failed_run_retention", {})
    return int(ret.get("max_age_days", 30)), int(ret.get("max_count", 20))


def _failed_at(run_dir: Path) -> datetime:
    report = run_dir / "report.json"
    if report.is_file():
        try:
            data = json.loads(report.read_text(encoding="utf-8"))
            stamp = data.get("failed_at")
            if stamp:
                return datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(
                    tzinfo=timezone.utc
                )
        except (json.JSONDecodeError, ValueError):
            pass
    return datetime.fromtimestamp(run_dir.stat().st_mtime, tz=timezone.utc)


def cleanup_failed_runs(root: Path, *, now: datetime | None = None) -> dict[str, Any]:
    """Apply retention to .work/failed-runs; return what was kept/removed."""
    now = now or datetime.now(timezone.utc)
    max_age_days, max_count = _retention_params(root)
    failed_root = root / ".work" / "failed-runs"
    if not failed_root.is_dir():
        return {"removed": [], "kept": [], "max_age_days": max_age_days, "max_count": max_count}

    dirs = [d for d in failed_root.iterdir() if d.is_dir()]
    # Newest first by failure time.
    dirs.sort(key=_failed_at, reverse=True)

    cutoff = now - timedelta(days=max_age_days)
    removed: list[str] = []
    kept: list[str] = []
    for index, run_dir in enumerate(dirs):
        too_old = _failed_at(run_dir) < cutoff
        over_count = index >= max_count
        if too_old or over_count:
            shutil.rmtree(run_dir)
            removed.append(run_dir.name)
        else:
            kept.append(run_dir.name)

    return {
        "removed": removed,
        "kept": kept,
        "max_age_days": max_age_days,
        "max_count": max_count,
    }
