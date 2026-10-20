"""Business rules for the end-to-end `compare build` command (Sec 18-19)."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from tool_eval.cli import main
from tool_eval.comparison.builder import build_comparison
from tool_eval.errors import ToolEvalError

GENERATED = "2026-07-24T00:00:00Z"


def _publish(root: Path, tool_id: str, profile: dict[str, Any]) -> None:
    directory = root / "data" / "profiles" / tool_id
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "profile.json").write_text(json.dumps(profile), encoding="utf-8")
    (directory / "description.md").write_text(f"# {tool_id}\nGreat **tool**.", encoding="utf-8")


def _profile_for(tool_id: str, valid_profile: dict[str, Any], status: str = "has") -> dict[str, Any]:
    p = copy.deepcopy(valid_profile)
    p["tool"]["tool_id"] = tool_id
    p["tool"]["name"] = tool_id.replace("_", " ").title()
    p["research"]["taxonomy_revision"] = 4
    p["feature_results"][0]["status"] = status
    if status not in ("has", "partial"):
        p["feature_results"][0].pop("evidence", None)
    return p


def _publish_four(root: Path, valid_profile: dict[str, Any]) -> list[str]:
    ids = ["tool_a", "tool_b", "tool_c", "tool_d"]
    statuses = ["has", "has", "has", "not_found"]
    for tid, st in zip(ids, statuses):
        _publish(root, tid, _profile_for(tid, valid_profile, st))
    return ids


def test_four_profiles_produce_single_offline_html(temp_project, valid_profile):
    ids = _publish_four(temp_project, valid_profile)
    build = build_comparison(temp_project, ids, generated_at=GENERATED)
    assert build.output_path.is_file()
    html = build.output_path.read_text(encoding="utf-8")
    assert html.startswith("<!DOCTYPE html>")
    assert "AI Coding Tool Comparison" in html


def test_output_has_no_cdn_or_network_references(temp_project, valid_profile):
    ids = _publish_four(temp_project, valid_profile)
    build = build_comparison(temp_project, ids, generated_at=GENERATED)
    html = build.output_path.read_text(encoding="utf-8").lower()
    assert "cdn.jsdelivr" not in html
    assert "https://cdn" not in html
    assert 'src="http' not in html
    assert "fonts/ubuntu" not in html  # fonts inlined as data: URIs
    assert "data:image/svg+xml;base64," in html


def test_flags_are_identical_across_two_builds(temp_project, valid_profile):
    ids = _publish_four(temp_project, valid_profile)
    first = build_comparison(temp_project, ids, output_name="a.html", generated_at=GENERATED)
    second = build_comparison(temp_project, ids, output_name="b.html", generated_at=GENERATED)
    assert first.output_path.read_text(encoding="utf-8") == second.output_path.read_text(encoding="utf-8")


def test_output_is_written_inside_outputs_comparisons(temp_project, valid_profile):
    ids = _publish_four(temp_project, valid_profile)
    build = build_comparison(temp_project, ids, output_name="report.html", generated_at=GENERATED)
    assert build.output_path == temp_project / "outputs" / "comparisons" / "report.html"


def test_output_name_cannot_escape_directory(temp_project, valid_profile):
    ids = _publish_four(temp_project, valid_profile)
    with pytest.raises(ToolEvalError) as exc:
        build_comparison(temp_project, ids, output_name="../escape.html", generated_at=GENERATED)
    assert exc.value.code == "INPUT_INVALID_OUTPUT_NAME"


def test_only_one_lacks_it_flag_appears_for_three_has_one_not_found(temp_project, valid_profile):
    ids = _publish_four(temp_project, valid_profile)
    build = build_comparison(temp_project, ids, generated_at=GENERATED)
    html = build.output_path.read_text(encoding="utf-8")
    assert "Only one lacks it" in html


def test_cli_compare_build_emits_single_json_envelope(temp_project, valid_profile, capsys, monkeypatch):
    ids = _publish_four(temp_project, valid_profile)
    monkeypatch.chdir(temp_project)
    code = main(["compare", "build", "--tools", *ids, "--out", "cli.html"])
    captured = capsys.readouterr()
    envelope = json.loads(captured.out)
    assert code == 0
    assert envelope["status"] == "ok"
    assert envelope["code"] == "COMPARISON_BUILT"
    assert envelope["artifacts"] and envelope["artifacts"][0].endswith("cli.html")


def test_cli_compare_build_rejects_single_tool(temp_project, valid_profile, capsys, monkeypatch):
    _publish(temp_project, "tool_a", _profile_for("tool_a", valid_profile))
    monkeypatch.chdir(temp_project)
    code = main(["compare", "build", "--tools", "tool_a"])
    envelope = json.loads(capsys.readouterr().out)
    assert code == 1
    assert envelope["code"] == "INPUT_TOO_FEW_TOOLS"
