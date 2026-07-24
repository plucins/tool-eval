"""Business rules for assembling the deterministic comparison view-model."""

from __future__ import annotations

import copy
from typing import Any

from tool_eval.comparison.freshness import FreshnessThresholds
from tool_eval.comparison.model import build_comparison_model

GENERATED = "2026-07-24T00:00:00Z"
THRESHOLDS = FreshnessThresholds()

TAXONOMY: dict[str, Any] = {
    "groups": [
        {"id": "code_generation", "name": "Code Generation"},
        {"id": "testing_quality", "name": "Testing & Quality"},
    ],
    "features": [
        {"feature_id": "inline_code_completion", "name": "Inline completion", "group": "code_generation", "definition": "d"},
        {"feature_id": "chat_generation", "name": "Chat generation", "group": "code_generation", "definition": "d"},
        {"feature_id": "test_generation", "name": "Test generation", "group": "testing_quality", "definition": "d"},
    ],
}


def _profile(tool_id: str, statuses: dict[str, str], *, state: str = "current", researched_at: str = "2026-07-20T00:00:00Z") -> dict[str, Any]:
    feature_results = []
    for fid, status in statuses.items():
        fr: dict[str, Any] = {
            "feature_id": fid,
            "status": status,
            "rationale": f"{fid} rationale",
            "search_trace": {"protocol_complete": True, "queries": [], "source_classes_checked": []},
        }
        if status in ("has", "partial"):
            fr["evidence"] = [{"source_id": "src_docs", "excerpt": "yes"}]
        feature_results.append(fr)
    return {
        "schema_version": "1.0.0",
        "tool": {"tool_id": tool_id, "name": tool_id.replace("_", " ").title()},
        "research": {
            "run_id": f"research-20260720-000000-{tool_id[:8]:0<8}",
            "researched_at": researched_at,
            "taxonomy_revision": 4,
            "template_revision": 1,
            "source_policy_revision": 1,
            "profile_state": state,
        },
        "sources": [],
        "feature_results": feature_results,
    }


def test_groups_and_features_follow_taxonomy_order():
    profiles = [_profile("tool_a", {"inline_code_completion": "has", "chat_generation": "has", "test_generation": "not_found"})]
    model = build_comparison_model(profiles, TAXONOMY, THRESHOLDS, GENERATED)
    assert [g.group_id for g in model.groups] == ["code_generation", "testing_quality"]
    first_group = model.groups[0]
    assert [f.feature_id for f in first_group.features] == ["inline_code_completion", "chat_generation"]


def test_tool_columns_follow_requested_order():
    profiles = [
        _profile("tool_b", {"inline_code_completion": "has"}),
        _profile("tool_a", {"inline_code_completion": "has"}),
    ]
    model = build_comparison_model(profiles, TAXONOMY, THRESHOLDS, GENERATED)
    assert [t.tool_id for t in model.tools] == ["tool_b", "tool_a"]


def test_missing_feature_result_becomes_unresearched_cell():
    # tool_a has no result for test_generation -> unresearched cell (status None).
    profiles = [_profile("tool_a", {"inline_code_completion": "has"})]
    model = build_comparison_model(profiles, TAXONOMY, THRESHOLDS, GENERATED)
    testing_group = model.groups[1]
    cell = testing_group.features[0].cells[0]
    assert cell.status is None
    assert cell.researched is False


def test_requires_research_profile_raises_warning():
    profiles = [_profile("tool_a", {"inline_code_completion": "has"}, state="requires_research")]
    model = build_comparison_model(profiles, TAXONOMY, THRESHOLDS, GENERATED)
    assert any("requires_research" in w for w in model.warnings)


def test_has_with_constraint_keeps_has_status_and_marks_constraint():
    profile = _profile("tool_a", {"inline_code_completion": "has"})
    profile["feature_results"][0]["constraints"] = [{"type": "plan_or_license", "description": "Pro plan"}]
    model = build_comparison_model([profile], TAXONOMY, THRESHOLDS, GENERATED)
    cell = model.groups[0].features[0].cells[0]
    assert cell.status == "has"
    assert cell.has_constraints is True


def test_repeated_build_produces_identical_model():
    profiles = [
        _profile("tool_a", {"inline_code_completion": "has", "chat_generation": "partial", "test_generation": "not_found"}),
        _profile("tool_b", {"inline_code_completion": "not_found", "chat_generation": "has", "test_generation": "has"}),
    ]
    first = build_comparison_model(copy.deepcopy(profiles), TAXONOMY, THRESHOLDS, GENERATED)
    second = build_comparison_model(copy.deepcopy(profiles), TAXONOMY, THRESHOLDS, GENERATED)
    assert first == second


def test_flags_are_computed_per_feature_across_tools():
    profiles = [
        _profile("t1", {"inline_code_completion": "has"}),
        _profile("t2", {"inline_code_completion": "has"}),
        _profile("t3", {"inline_code_completion": "has"}),
        _profile("t4", {"inline_code_completion": "not_found"}),
    ]
    model = build_comparison_model(profiles, TAXONOMY, THRESHOLDS, GENERATED)
    row = model.groups[0].features[0]
    assert "Only one lacks it" in row.flags
