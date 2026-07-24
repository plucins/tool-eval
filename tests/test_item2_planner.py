"""Item 2: bundle planner and worker-wave orchestration contract (D-010)."""

from __future__ import annotations

import json

import pytest

from tool_eval.research import planner
from tool_eval.research.planner import Bundle, plan_bundles, plan_waves, split_bundle


def _features(spec: dict[str, int]) -> list[dict[str, str]]:
    """Build taxonomy-like features: {group: count}."""
    out = []
    for group, count in spec.items():
        for i in range(count):
            out.append({"feature_id": f"{group}_f{i:02d}", "group": group})
    return out


# --- determinism -----------------------------------------------------------


def test_planning_is_deterministic():
    feats = _features({"a": 5, "b": 3, "c": 1})
    p1 = plan_bundles(feats, min_size=2, max_size=4)
    p2 = plan_bundles(list(reversed(feats)), min_size=2, max_size=4)
    assert p1 == p2  # order of input must not change the plan


# --- bundle sizes (2-4 same group) -----------------------------------------


def test_bundles_respect_min_max_within_group():
    feats = _features({"a": 5})  # 5 -> 4+1 would violate min; must rebalance to 3+2
    bundles = plan_bundles(feats, min_size=2, max_size=4)
    sizes = sorted(len(b.feature_ids) for b in bundles)
    assert sizes == [2, 3]
    assert all(b.group == "a" for b in bundles)


def test_group_smaller_than_min_is_single_bundle():
    feats = _features({"solo": 1})
    bundles = plan_bundles(feats, min_size=2, max_size=4)
    assert len(bundles) == 1
    assert bundles[0].feature_ids == ("solo_f00",)


def test_features_never_split_across_groups():
    feats = _features({"a": 3, "b": 3})
    bundles = plan_bundles(feats, min_size=2, max_size=4)
    for b in bundles:
        groups = {fid.rsplit("_f", 1)[0] for fid in b.feature_ids}
        assert groups == {b.group}


def test_every_feature_appears_exactly_once():
    feats = _features({"a": 7, "b": 4, "c": 2, "d": 1})
    bundles = plan_bundles(feats, min_size=2, max_size=4)
    seen = [fid for b in bundles for fid in b.feature_ids]
    assert sorted(seen) == sorted(f["feature_id"] for f in feats)
    assert len(seen) == len(set(seen))


# --- isolation of complex/disputed features (D-010) ------------------------


def test_isolated_feature_gets_its_own_bundle():
    feats = _features({"a": 4})
    target = feats[0]["feature_id"]
    bundles = plan_bundles(feats, min_size=2, max_size=4, isolate=[target])
    solo = [b for b in bundles if b.isolated]
    assert len(solo) == 1
    assert solo[0].feature_ids == (target,)
    # the isolated feature must not also appear in a normal bundle
    others = [fid for b in bundles if not b.isolated for fid in b.feature_ids]
    assert target not in others


# --- waves (<= max_concurrent) ---------------------------------------------


def test_waves_never_exceed_max_concurrent():
    feats = _features({"a": 4, "b": 4, "c": 4})  # several bundles
    bundles = plan_bundles(feats, min_size=2, max_size=4)
    waves = plan_waves(bundles, max_concurrent=4)
    assert all(len(w) <= 4 for w in waves)
    assert sum(len(w) for w in waves) == len(bundles)


def test_split_bundle_produces_singletons():
    b = Bundle(bundle_id="feat-a-01", group="a", feature_ids=("x", "y", "z"))
    parts = split_bundle(b)
    assert [p.feature_ids for p in parts] == [("x",), ("y",), ("z",)]
    assert all(p.isolated for p in parts)


# --- manifest matches task schema ------------------------------------------


def test_bundle_manifest_is_schema_valid():
    from tool_eval.validation import schema

    b = Bundle(bundle_id="feat-a-01", group="code_generation", feature_ids=("f1", "f2"))
    manifest = b.to_task_manifest("research-20260720-000000-abcd1234")
    assert schema.validate("task", manifest) == []


def test_invalid_sizes_raise():
    with pytest.raises(ValueError):
        plan_bundles([], min_size=0, max_size=4)
    with pytest.raises(ValueError):
        plan_waves([], max_concurrent=0)
