"""Safe staged publication with rollback and recovery (D-012).

The active profile lives at ``data/profiles/<tool_id>/`` and must never be left
half-written. The staged ``profile.json`` + ``description.md`` are built and
fully validated in the run's ``publish/`` directory; only after validation
passes does Python replace the active directory:

1. validate the staged files (a failure never touches the active profile);
2. write a journal recording the in-flight replacement;
3. move any existing active directory aside as a technical backup;
4. write the new active directory from the staged files;
5. delete the backup and journal.

Any error during 3-4 triggers rollback (restore the backup). If the process is
interrupted, :func:`recover` reads the journal on the next run and restores the
backup when the active directory is missing or incomplete. A failed run never
changes the active profile (D-011/D-012).
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tool_eval.errors import ErrorFamily, ToolEvalError
from tool_eval.profiles.validate import validate_profile

_PROFILE_FILES = ("profile.json", "description.md")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _profiles_dir(root: Path) -> Path:
    return root / "data" / "profiles"


def _journal_dir(root: Path) -> Path:
    return _profiles_dir(root) / ".publish-journal"


def _journal_path(root: Path, tool_id: str) -> Path:
    return _journal_dir(root) / f"{tool_id}.json"


def is_complete_profile_dir(path: Path) -> bool:
    return path.is_dir() and all((path / f).is_file() for f in _PROFILE_FILES)


@dataclass
class PublishResult:
    tool_id: str
    published: bool
    target: str
    validation_errors: list[dict[str, Any]]
    rolled_back: bool = False


def publish_profile(
    root: Path,
    run_id: str,
    tool_id: str,
    *,
    taxonomy_feature_ids: list[str] | None = None,
) -> PublishResult:
    run_dir = root / ".work" / "runs" / run_id
    staging = run_dir / "publish"
    staged_profile = staging / "profile.json"
    staged_desc = staging / "description.md"

    if not staged_profile.is_file() or not staged_desc.is_file():
        raise ToolEvalError(
            code=f"{ErrorFamily.PUBLISH}_STAGING_INCOMPLETE",
            message="publish/ must contain both profile.json and description.md",
            path=str(staging),
        )

    profile = json.loads(staged_profile.read_text(encoding="utf-8"))
    errors = validate_profile(profile, taxonomy_feature_ids=taxonomy_feature_ids)
    if errors:
        # Persist the report; never touch the active profile on invalid input.
        (run_dir / "validation-errors.json").write_text(
            json.dumps(errors, indent=2), encoding="utf-8"
        )
        return PublishResult(
            tool_id=tool_id,
            published=False,
            target=str(_profiles_dir(root) / tool_id),
            validation_errors=errors,
        )

    target = _profiles_dir(root) / tool_id
    backup = run_dir / "publish-backup" / tool_id
    _journal_dir(root).mkdir(parents=True, exist_ok=True)
    journal = _journal_path(root, tool_id)

    journal.write_text(
        json.dumps(
            {
                "tool_id": tool_id,
                "run_id": run_id,
                "target": str(target),
                "backup": str(backup),
                "phase": "start",
                "started_at": _now(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    try:
        if target.exists():
            backup.parent.mkdir(parents=True, exist_ok=True)
            if backup.exists():
                shutil.rmtree(backup)
            shutil.move(str(target), str(backup))
            _update_phase(journal, "backed_up")

        target.mkdir(parents=True, exist_ok=True)
        for name in _PROFILE_FILES:
            shutil.copy2(staging / name, target / name)
        _update_phase(journal, "written")
    except Exception as exc:  # rollback
        rolled_back = False
        if backup.exists():
            if target.exists():
                shutil.rmtree(target)
            shutil.move(str(backup), str(target))
            rolled_back = True
        journal.unlink(missing_ok=True)
        raise ToolEvalError(
            code=f"{ErrorFamily.PUBLISH}_REPLACE_FAILED",
            message=f"publication failed and was rolled back ({rolled_back}): {exc}",
            path=str(target),
        ) from exc

    # Success: drop backup + journal.
    if backup.exists():
        shutil.rmtree(backup)
    journal.unlink(missing_ok=True)

    return PublishResult(
        tool_id=tool_id, published=True, target=str(target), validation_errors=[]
    )


def _update_phase(journal: Path, phase: str) -> None:
    data = json.loads(journal.read_text(encoding="utf-8"))
    data["phase"] = phase
    data["updated_at"] = _now()
    journal.write_text(json.dumps(data, indent=2), encoding="utf-8")


def recover(root: Path) -> list[dict[str, Any]]:
    """Detect and repair interrupted publications (D-012 recovery)."""
    jdir = _journal_dir(root)
    if not jdir.is_dir():
        return []

    actions: list[dict[str, Any]] = []
    for journal in sorted(jdir.glob("*.json")):
        data = json.loads(journal.read_text(encoding="utf-8"))
        tool_id = data["tool_id"]
        target = Path(data["target"])
        backup = Path(data["backup"])

        if is_complete_profile_dir(target):
            # Replacement actually finished; the journal is stale.
            if backup.exists():
                shutil.rmtree(backup)
            journal.unlink(missing_ok=True)
            actions.append({"tool_id": tool_id, "action": "cleared_stale_journal"})
            continue

        # Active dir missing/incomplete: restore the backup if we have one.
        if backup.exists():
            if target.exists():
                shutil.rmtree(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(backup), str(target))
            journal.unlink(missing_ok=True)
            actions.append({"tool_id": tool_id, "action": "restored_backup"})
        else:
            journal.unlink(missing_ok=True)
            actions.append({"tool_id": tool_id, "action": "no_backup_nothing_to_restore"})

    return actions


def list_profiles(root: Path) -> list[dict[str, Any]]:
    pdir = _profiles_dir(root)
    if not pdir.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for child in sorted(pdir.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        entry: dict[str, Any] = {"tool_id": child.name, "complete": is_complete_profile_dir(child)}
        profile_json = child / "profile.json"
        if profile_json.is_file():
            try:
                data = json.loads(profile_json.read_text(encoding="utf-8"))
                entry["profile_state"] = data.get("research", {}).get("profile_state")
                entry["researched_at"] = data.get("research", {}).get("researched_at")
            except json.JSONDecodeError:
                entry["profile_state"] = "unreadable"
        out.append(entry)
    return out
