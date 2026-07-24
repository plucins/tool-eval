"""Item 1: complete profile model + schemas + references between records.

Grounded in D-016 (profile sections, same feature-record format, source
referencing, additionalProperties:false, omit-not-null) and the requirements
(use cases documented/inferred, additional facts source-backed).
"""

from __future__ import annotations

import copy

import pytest

from tool_eval.validation import schema
from tool_eval.validation import business


# --- schema registry loads and resolves cross-file $ref --------------------


def test_all_named_schemas_load_and_compile():
    for name in schema.SCHEMA_FILES:
        # Building a validator forces $ref resolution against the registry.
        assert schema._validator_for(name) is not None


def test_profile_schema_embeds_feature_records_via_ref(valid_profile):
    assert schema.validate("profile", valid_profile) == []


# --- structural rules from D-016 -------------------------------------------


def test_profile_rejects_additional_properties(valid_profile):
    valid_profile["surprise"] = True
    errors = schema.validate("profile", valid_profile)
    assert any("surprise" in e.message or "additional" in e.message.lower() for e in errors)


def test_profile_requires_core_sections(valid_profile):
    del valid_profile["feature_results"]
    errors = schema.validate("profile", valid_profile)
    assert any("feature_results" in e.message for e in errors)


def test_schema_version_must_be_semver(valid_profile):
    valid_profile["schema_version"] = "1.0"
    assert schema.validate("profile", valid_profile)


def test_profile_state_enum(valid_profile):
    valid_profile["research"]["profile_state"] = "stale"
    assert schema.validate("profile", valid_profile)


# --- use cases: documented vs inferred (requirements Sec 14) ---------------


def test_documented_use_case_requires_evidence():
    uc = {
        "use_case_id": "x",
        "title": "T",
        "description": "D",
        "kind": "documented",
    }
    assert schema.validate("use-case", uc)  # missing evidence


def test_inferred_use_case_requires_rationale_and_supporting_features():
    uc = {
        "use_case_id": "x",
        "title": "T",
        "description": "D",
        "kind": "inferred",
    }
    assert schema.validate("use-case", uc)


def test_inferred_use_case_valid_with_rationale_and_features():
    uc = {
        "use_case_id": "x",
        "title": "T",
        "description": "D",
        "kind": "inferred",
        "rationale": "because",
        "supporting_features": ["inline_code_completion"],
    }
    assert schema.validate("use-case", uc) == []


# --- additional facts -------------------------------------------------------


def test_additional_fact_valid():
    fact = {"fact_id": "f1", "topic": "T", "description": "D"}
    assert schema.validate("additional-fact", fact) == []


# --- candidates / unresolved-issues / subagent-result ----------------------


def test_candidate_requires_relevance_suggestion():
    cand = {"candidate_id": "c1", "name": "C", "group": "grp", "definition": "def"}
    assert schema.validate("candidate", cand)


def test_candidates_set_with_decisions():
    doc = {
        "candidates": [
            {
                "candidate_id": "c1",
                "name": "C",
                "group": "code_generation",
                "definition": "def",
                "relevance_suggestion": "relevant",
            }
        ],
        "decisions": [{"candidate_id": "c1", "decision": "accept"}],
    }
    assert schema.validate("candidates", doc) == []


def test_unresolved_issues_valid():
    doc = {"issues": [{"issue_id": "i1", "kind": "conflict", "description": "d"}]}
    assert schema.validate("unresolved-issues", doc) == []


def test_subagent_result_uses_same_feature_record_format(make_feature_result):
    doc = {
        "task_id": "t-1",
        "run_id": "research-20260720-000000-abcd1234",
        "task_type": "feature-research",
        "sources": [
            {
                "source_id": "src_docs",
                "url": "https://docs.example.com/x",
                "title": "Doc",
                "source_type": "documentation",
                "checked_at": "2026-07-20",
                "available": True,
                "official": True,
            }
        ],
        "feature_results": [make_feature_result("inline_code_completion", "has")],
    }
    assert schema.validate("subagent-result", doc) == []


# --- references between records (business rules) ---------------------------


def test_referential_integrity_passes_for_valid_profile(valid_profile):
    assert business.check_referential_integrity(valid_profile) == []


def test_referential_integrity_flags_unknown_source(valid_profile):
    valid_profile["feature_results"][0]["evidence"][0]["source_id"] = "src_missing"
    errors = business.check_referential_integrity(valid_profile)
    assert len(errors) == 1
    assert errors[0].code == "VALIDATION_UNKNOWN_SOURCE_REF"
    assert errors[0].feature_id == "inline_code_completion"


def test_referential_integrity_checks_facts_and_use_cases(valid_profile):
    valid_profile["additional_facts"][0]["evidence"][0]["source_id"] = "nope"
    valid_profile["use_cases"][0]["evidence"][0]["source_id"] = "nope2"
    errors = business.check_referential_integrity(valid_profile)
    assert {e.code for e in errors} == {"VALIDATION_UNKNOWN_SOURCE_REF"}
    assert len(errors) == 2


def test_use_case_supporting_features_must_exist(valid_profile):
    valid_profile["use_cases"][1]["supporting_features"] = ["ghost_feature"]
    errors = business.check_use_case_supporting_features(valid_profile)
    assert len(errors) == 1
    assert errors[0].code == "VALIDATION_UNKNOWN_FEATURE_REF"
