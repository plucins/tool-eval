"""Item 4: additional facts, documented/inferred use cases, description.md."""

from __future__ import annotations

import pytest

from tool_eval.profiles.description import assemble_description
from tool_eval.validation.business import check_profile_content

SECTIONS = [
    {"id": "characteristics", "title": "Characteristics", "required": True},
    {"id": "access", "title": "Access methods", "required": True},
    {"id": "internal_tools", "title": "Internal tools and mechanisms", "required": False},
    {"id": "constraints", "title": "Constraints", "required": True},
]


def _full_texts():
    return {
        "characteristics": "It is fast.",
        "access": "CLI and IDE.",
        "constraints": "Enterprise plan for SSO.",
    }


def test_assemble_orders_by_config_and_emits_headers():
    md, errors = assemble_description(SECTIONS, _full_texts())
    assert errors == []
    assert md.index("## Characteristics") < md.index("## Access methods")
    assert md.index("## Access methods") < md.index("## Constraints")
    assert "## Internal tools" not in md  # optional + absent -> omitted


def test_missing_required_section_flagged():
    texts = _full_texts()
    del texts["constraints"]
    md, errors = assemble_description(SECTIONS, texts)
    codes = {(e.code, e.section_id) for e in errors}
    assert ("VALIDATION_MISSING_REQUIRED_SECTION", "constraints") in codes


def test_empty_required_section_flagged():
    texts = _full_texts()
    texts["access"] = "   "
    _, errors = assemble_description(SECTIONS, texts)
    assert any(e.section_id == "access" for e in errors)


def test_unknown_section_rejected():
    texts = _full_texts()
    texts["mystery"] = "content"
    _, errors = assemble_description(SECTIONS, texts)
    assert any(e.code == "VALIDATION_UNKNOWN_SECTION" for e in errors)


def test_optional_section_included_when_present():
    texts = _full_texts()
    texts["internal_tools"] = "Uses an internal indexer."
    md, errors = assemble_description(SECTIONS, texts)
    assert errors == []
    assert "## Internal tools and mechanisms" in md


def test_empty_config_raises():
    with pytest.raises(ValueError):
        assemble_description([], {})


# --- content completeness (criterion 14) -----------------------------------


def test_profile_content_ok(valid_profile):
    assert check_profile_content(valid_profile) == []


def test_profile_without_facts_flagged(valid_profile):
    valid_profile["additional_facts"] = []
    codes = {e.code for e in check_profile_content(valid_profile)}
    assert "VALIDATION_NO_ADDITIONAL_FACTS" in codes


def test_profile_missing_inferred_use_case_flagged(valid_profile):
    valid_profile["use_cases"] = [uc for uc in valid_profile["use_cases"] if uc["kind"] != "inferred"]
    errors = check_profile_content(valid_profile)
    assert any("inferred" in e.message for e in errors)


def test_profile_missing_documented_use_case_flagged(valid_profile):
    valid_profile["use_cases"] = [uc for uc in valid_profile["use_cases"] if uc["kind"] != "documented"]
    errors = check_profile_content(valid_profile)
    assert any("documented" in e.message for e in errors)


def test_real_profile_sections_config_assembles(temp_project):
    import yaml

    cfg = yaml.safe_load((temp_project / "config" / "profile-sections.yaml").read_text())
    required = [s["id"] for s in cfg["sections"] if s.get("required")]
    texts = {sid: f"Text for {sid}." for sid in required}
    md, errors = assemble_description(cfg["sections"], texts)
    assert errors == []
    for sid in required:
        assert f"Text for {sid}." in md
