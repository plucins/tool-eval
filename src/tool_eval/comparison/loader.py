"""Load and validate active profiles for a comparison (Increment 3, Sec 18).

IO wrapper around the pure comparison logic: it resolves each requested
``tool_id`` to its active ``data/profiles/<tool_id>/`` directory, reads and
validates the profile through the existing JSON Schema + business validators
(D-016), and reads the semantic ``description.md``. A missing profile is a hard
error; an old taxonomy/template revision only produces a warning (Sec 18).
Comparison never runs research or workers (Sec 3.7).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tool_eval.config import load_config_bundle
from tool_eval.errors import ErrorFamily, ToolEvalError
from tool_eval.profiles.validate import validate_profile

_TOOL_ID_OK = "abcdefghijklmnopqrstuvwxyz0123456789_"


@dataclass(frozen=True)
class LoadedComparison:
    profiles: list[dict[str, Any]]
    descriptions: dict[str, str]
    warnings: list[str]


def _profile_dir(root: Path, tool_id: str) -> Path:
    return root / "data" / "profiles" / tool_id


def _validate_tool_ids(tool_ids: list[str]) -> None:
    if len(tool_ids) < 2:
        raise ToolEvalError(
            code=f"{ErrorFamily.INPUT}_TOO_FEW_TOOLS",
            message=f"compare needs at least two tools; got {len(tool_ids)}.",
        )
    seen: set[str] = set()
    for tool_id in tool_ids:
        if not tool_id or tool_id[0] not in _TOOL_ID_OK[:26] or any(c not in _TOOL_ID_OK for c in tool_id):
            raise ToolEvalError(
                code=f"{ErrorFamily.INPUT}_INVALID_TOOL_ID",
                message=f"tool_id {tool_id!r} must match ^[a-z][a-z0-9_]*$.",
            )
        if tool_id in seen:
            raise ToolEvalError(
                code=f"{ErrorFamily.INPUT}_DUPLICATE_TOOL",
                message=f"tool_id {tool_id!r} was requested more than once.",
            )
        seen.add(tool_id)


def _revision_warnings(profile: dict[str, Any], effective: dict[str, int], tool_name: str) -> list[str]:
    research = profile["research"]
    warnings: list[str] = []
    checks = (
        ("taxonomy_revision", "feature-taxonomy.yaml"),
        ("template_revision", "profile-sections.yaml"),
        ("source_policy_revision", "source-policies.yaml"),
    )
    for field, config_name in checks:
        current = effective.get(config_name)
        if current is not None and research.get(field, current) < current:
            warnings.append(
                f"{tool_name}: {field} {research[field]} is older than the current "
                f"revision {current}; cells may be out of date."
            )
    return warnings


def load_comparison(root: Path, tool_ids: list[str]) -> LoadedComparison:
    """Resolve, read, and validate every requested profile. Preserves order."""
    _validate_tool_ids(tool_ids)

    bundle = load_config_bundle(root)
    effective = {
        name: cf.revision
        for name, cf in bundle.files.items()
        if cf.revision is not None
    }

    profiles: list[dict[str, Any]] = []
    descriptions: dict[str, str] = {}
    warnings: list[str] = []

    for tool_id in tool_ids:
        directory = _profile_dir(root, tool_id)
        profile_path = directory / "profile.json"
        if not profile_path.is_file():
            raise ToolEvalError(
                code=f"{ErrorFamily.INPUT}_PROFILE_NOT_FOUND",
                message=f"No active profile for tool {tool_id!r} at {profile_path}.",
                path=str(profile_path),
            )
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        errors = validate_profile(profile, require_content=False)
        if errors:
            raise ToolEvalError(
                code=f"{ErrorFamily.VALIDATION}_PROFILE_INVALID",
                message=(
                    f"profile for {tool_id!r} is invalid and cannot be compared "
                    f"({len(errors)} error(s); first: {errors[0]['message']})."
                ),
                path=str(profile_path),
            )

        description_path = directory / "description.md"
        descriptions[tool_id] = (
            description_path.read_text(encoding="utf-8") if description_path.is_file() else ""
        )
        warnings.extend(_revision_warnings(profile, effective, profile["tool"]["name"]))
        profiles.append(profile)

    return LoadedComparison(profiles=profiles, descriptions=descriptions, warnings=warnings)
