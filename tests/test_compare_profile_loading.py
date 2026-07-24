"""Business rules for loading and validating profiles for a comparison."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from tool_eval.comparison.loader import load_comparison
from tool_eval.errors import ToolEvalError


def _publish(root: Path, tool_id: str, profile: dict[str, Any], description: str = "# Desc\nText.") -> None:
    directory = root / "data" / "profiles" / tool_id
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "profile.json").write_text(json.dumps(profile), encoding="utf-8")
    (directory / "description.md").write_text(description, encoding="utf-8")


def _profile_for(tool_id: str, valid_profile: dict[str, Any], **research: Any) -> dict[str, Any]:
    p = copy.deepcopy(valid_profile)
    p["tool"]["tool_id"] = tool_id
    p["tool"]["name"] = tool_id.replace("_", " ").title()
    p["research"].update(research)
    return p


def test_two_profiles_are_loaded_in_requested_order(temp_project, valid_profile):
    _publish(temp_project, "tool_a", _profile_for("tool_a", valid_profile))
    _publish(temp_project, "tool_b", _profile_for("tool_b", valid_profile))
    loaded = load_comparison(temp_project, ["tool_b", "tool_a"])
    assert [p["tool"]["tool_id"] for p in loaded.profiles] == ["tool_b", "tool_a"]
    assert loaded.descriptions["tool_a"].startswith("# Desc")


def test_missing_profile_is_an_error(temp_project, valid_profile):
    _publish(temp_project, "tool_a", _profile_for("tool_a", valid_profile))
    with pytest.raises(ToolEvalError) as exc:
        load_comparison(temp_project, ["tool_a", "ghost_tool"])
    assert exc.value.code == "INPUT_PROFILE_NOT_FOUND"


def test_fewer_than_two_tools_is_rejected(temp_project, valid_profile):
    _publish(temp_project, "tool_a", _profile_for("tool_a", valid_profile))
    with pytest.raises(ToolEvalError) as exc:
        load_comparison(temp_project, ["tool_a"])
    assert exc.value.code == "INPUT_TOO_FEW_TOOLS"


def test_duplicate_tool_is_rejected(temp_project, valid_profile):
    _publish(temp_project, "tool_a", _profile_for("tool_a", valid_profile))
    with pytest.raises(ToolEvalError) as exc:
        load_comparison(temp_project, ["tool_a", "tool_a"])
    assert exc.value.code == "INPUT_DUPLICATE_TOOL"


def test_invalid_tool_id_is_rejected(temp_project):
    with pytest.raises(ToolEvalError) as exc:
        load_comparison(temp_project, ["Tool-A", "tool_b"])
    assert exc.value.code == "INPUT_INVALID_TOOL_ID"


def test_schema_invalid_profile_is_rejected(temp_project, valid_profile):
    good = _profile_for("tool_a", valid_profile)
    broken = _profile_for("tool_b", valid_profile)
    broken.pop("feature_results")  # violates required schema
    _publish(temp_project, "tool_a", good)
    _publish(temp_project, "tool_b", broken)
    with pytest.raises(ToolEvalError) as exc:
        load_comparison(temp_project, ["tool_a", "tool_b"])
    assert exc.value.code == "VALIDATION_PROFILE_INVALID"


def test_old_taxonomy_revision_produces_warning_not_failure(temp_project, valid_profile):
    current = _profile_for("tool_a", valid_profile, taxonomy_revision=4)
    old = _profile_for("tool_b", valid_profile, taxonomy_revision=1)
    _publish(temp_project, "tool_a", current)
    _publish(temp_project, "tool_b", old)
    loaded = load_comparison(temp_project, ["tool_a", "tool_b"])
    assert any("taxonomy_revision" in w for w in loaded.warnings)
