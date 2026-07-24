"""Business rules for comparison distribution flags (requirements Sec 18)."""

from __future__ import annotations

from tool_eval.comparison.flags import (
    FLAG_COMMON,
    FLAG_ONLY_ONE_HAS_IT,
    FLAG_ONLY_ONE_LACKS_IT,
    FLAG_RARE,
    FLAG_SPLIT,
    FLAG_VARIED,
    feature_flags,
    is_excluded,
)


def test_has_with_constraint_still_counts_as_has():
    # The model normalizes a constrained "has" to status "has"; constraints are
    # carried separately, so a constrained has behaves exactly like a plain has.
    cells = ["has", "has", "has", "has"]
    assert FLAG_COMMON in feature_flags(cells)


def test_partial_counts_as_neither_has_nor_not_found():
    # One partial among has/not_found blocks the unambiguous distribution flags
    # but still yields Varied implementation.
    flags = feature_flags(["has", "not_found", "not_found", "partial"])
    assert flags == [FLAG_VARIED]


def test_uncertain_cell_excludes_feature_from_flags():
    assert is_excluded(["has", "has", "has", "uncertain"]) is True
    assert feature_flags(["has", "has", "has", "uncertain"]) == []


def test_unresearched_cell_excludes_feature_from_flags():
    assert is_excluded(["has", "has", "has", None]) is True
    assert feature_flags(["has", "has", "has", None]) == []


def test_any_partial_produces_varied_implementation():
    assert FLAG_VARIED in feature_flags(["partial", "has", "not_found", "has"])
    assert FLAG_VARIED in feature_flags(["partial", "partial"])


def test_only_one_has_it_flag():
    flags = feature_flags(["has", "not_found", "not_found", "not_found"])
    assert FLAG_ONLY_ONE_HAS_IT in flags
    assert FLAG_ONLY_ONE_LACKS_IT not in flags


def test_only_one_lacks_it_flag():
    flags = feature_flags(["has", "has", "has", "not_found"])
    assert FLAG_ONLY_ONE_LACKS_IT in flags
    assert FLAG_COMMON in flags  # "only one lacks it" is also common in this set


def test_rare_flag():
    flags = feature_flags(["has", "has", "not_found", "not_found", "not_found"])
    assert FLAG_RARE in flags


def test_common_in_this_comparison_flag_when_all_have_it():
    assert FLAG_COMMON in feature_flags(["has", "has", "has", "has"])


def test_split_flag_when_has_and_not_found_are_balanced():
    assert FLAG_SPLIT in feature_flags(["has", "has", "not_found", "not_found"])


def test_distribution_flags_require_at_least_four_tools():
    # Three tools: no distribution flags even for a clean one-has pattern.
    assert feature_flags(["has", "not_found", "not_found"]) == []


def test_flags_can_coexist():
    # 4 tools, one not_found => "only one lacks it" AND "common in this comparison".
    flags = feature_flags(["has", "has", "has", "not_found"])
    assert FLAG_ONLY_ONE_LACKS_IT in flags
    assert FLAG_COMMON in flags
    assert len(flags) >= 2
