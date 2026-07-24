"""Item 3: D-009 protocol enforcement + evidence/constraints/conflicts.

Covers the four statuses and the rule that anything short of a complete
protocol degrades not_found -> uncertain (D-009; requirements Sec 9-12).
"""

from __future__ import annotations

import copy

import pytest

from tool_eval.validation import schema
from tool_eval.validation.business import (
    validate_feature_result,
    validate_feature_results,
)

ALL_CLASSES = ["documentation", "product_page", "changelog", "pricing"]

OFFICIAL_SOURCES = {
    "src_docs": {"source_id": "src_docs", "official": True},
    "src_blog": {"source_id": "src_blog", "official": False},
}


def _fr(status, **kw):
    base = {
        "feature_id": "inline_code_completion",
        "status": status,
        "rationale": "r",
        "search_trace": {
            "protocol_complete": True,
            "queries": ["q"],
            "source_classes_checked": list(ALL_CLASSES),
        },
    }
    base.update(kw)
    return base


# --- has / partial ---------------------------------------------------------


def test_has_with_official_evidence_ok():
    fr = _fr("has", evidence=[{"source_id": "src_docs", "excerpt": "Supported."}])
    assert validate_feature_result(fr, OFFICIAL_SOURCES) == []


def test_has_with_empty_excerpt_flagged():
    fr = _fr("has", evidence=[{"source_id": "src_docs", "excerpt": "   "}])
    codes = {e.code for e in validate_feature_result(fr, OFFICIAL_SOURCES)}
    assert "VALIDATION_EVIDENCE_REQUIRED" in codes


def test_has_backed_only_by_community_source_rejected():
    fr = _fr("has", evidence=[{"source_id": "src_blog", "excerpt": "It works."}])
    codes = {e.code for e in validate_feature_result(fr, OFFICIAL_SOURCES)}
    assert "VALIDATION_NO_OFFICIAL_SOURCE" in codes


def test_partial_requires_evidence():
    fr = _fr("partial")
    codes = {e.code for e in validate_feature_result(fr, OFFICIAL_SOURCES)}
    assert "VALIDATION_EVIDENCE_REQUIRED" in codes


# --- not_found (the D-009 gate) --------------------------------------------


def test_not_found_complete_protocol_ok():
    fr = _fr("not_found")
    assert validate_feature_result(fr, OFFICIAL_SOURCES) == []


def test_not_found_missing_source_class_rejected():
    fr = _fr("not_found")
    fr["search_trace"]["source_classes_checked"] = ["documentation"]
    codes = {e.code for e in validate_feature_result(fr)}
    assert "VALIDATION_D009_SOURCE_CLASS_MISSING" in codes


def test_not_found_with_access_gap_must_be_uncertain():
    fr = _fr("not_found")
    fr["search_trace"]["access_gaps"] = ["pricing page blocked"]
    codes = {e.code for e in validate_feature_result(fr)}
    assert "VALIDATION_D009_ACCESS_GAP" in codes


def test_not_found_with_conflict_must_be_uncertain():
    fr = _fr("not_found")
    fr["conflict"] = {
        "reason": "disagreement",
        "conflicting_evidence": [{"source_id": "src_docs", "excerpt": "yes"}],
    }
    codes = {e.code for e in validate_feature_result(fr)}
    assert "VALIDATION_D009_UNRESOLVED_CONFLICT" in codes


def test_not_found_with_positive_evidence_rejected():
    fr = _fr("not_found", evidence=[{"source_id": "src_docs", "excerpt": "actually yes"}])
    codes = {e.code for e in validate_feature_result(fr)}
    assert "VALIDATION_NOT_FOUND_HAS_EVIDENCE" in codes


def test_not_found_incomplete_protocol_rejected():
    fr = _fr("not_found")
    fr["search_trace"]["protocol_complete"] = False
    codes = {e.code for e in validate_feature_result(fr)}
    assert "VALIDATION_PROTOCOL_INCOMPLETE" in codes


# --- uncertain -------------------------------------------------------------


def test_uncertain_with_conflict_ok():
    fr = _fr(
        "uncertain",
        conflict={
            "reason": "disagreement",
            "conflicting_evidence": [
                {"source_id": "src_docs", "excerpt": "yes"},
                {"source_id": "src_blog", "excerpt": "no"},
            ],
        },
    )
    assert validate_feature_result(fr) == []


def test_uncertain_from_access_gap_ok():
    fr = _fr("uncertain")
    fr["search_trace"]["access_gaps"] = ["docs unreachable"]
    assert validate_feature_result(fr) == []


def test_uncertain_unjustified_rejected():
    fr = _fr("uncertain")  # no conflict, no gap, protocol complete
    codes = {e.code for e in validate_feature_result(fr)}
    assert "VALIDATION_UNCERTAIN_UNJUSTIFIED" in codes


# --- profile-level roll-up + schema still accepts uncertain w/o conflict ---


def test_uncertain_no_longer_requires_conflict_in_schema():
    fr = _fr("uncertain")
    fr["search_trace"]["access_gaps"] = ["blocked"]
    assert schema.validate("feature-result", fr) == []


def test_validate_feature_results_over_profile(valid_profile):
    assert validate_feature_results(valid_profile) == []
