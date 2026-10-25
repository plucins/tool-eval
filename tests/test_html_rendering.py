"""Business rules for rendering the self-contained comparison HTML."""

from __future__ import annotations

import re
from html import escape
from html.parser import HTMLParser
from typing import Any

from tool_eval.comparison.freshness import FreshnessThresholds
from tool_eval.comparison.model import build_comparison_model
from tool_eval.reporting.html import render_comparison_html

GENERATED = "2026-07-24T00:00:00Z"
THRESHOLDS = FreshnessThresholds()

TAXONOMY: dict[str, Any] = {
    "groups": [{"id": "code_generation", "name": "Code Generation"}],
    "features": [
        {"feature_id": "inline_code_completion", "name": "Inline completion", "group": "code_generation", "definition": "Ghost text."},
    ],
}


def _profile(tool_id: str, status: str, **research: Any) -> dict[str, Any]:
    res = {
        "run_id": f"research-20260720-000000-{tool_id[:8]:0<8}",
        "researched_at": "2026-07-20T00:00:00Z",
        "taxonomy_revision": 4,
        "template_revision": 1,
        "source_policy_revision": 1,
        "profile_state": "current",
    }
    res.update(research)
    fr: dict[str, Any] = {
        "feature_id": "inline_code_completion",
        "status": status,
        "rationale": "See [[src_docs]].",
        "search_trace": {"protocol_complete": True, "queries": [], "source_classes_checked": []},
    }
    if status in ("has", "partial"):
        fr["evidence"] = [{"source_id": "src_docs", "excerpt": "yes"}]
    return {
        "schema_version": "1.0.0",
        "tool": {"tool_id": tool_id, "name": tool_id.replace("_", " ").title(), "vendor": "Acme"},
        "research": res,
        "sources": [{"source_id": "src_docs", "url": "https://docs.example.com/x", "title": "Docs",
                     "source_type": "documentation", "checked_at": "2026-07-20", "available": True, "official": True}],
        "feature_results": [fr],
    }


def _model_and_profiles(statuses: dict[str, str]):
    profiles = [_profile(tid, st) for tid, st in statuses.items()]
    model = build_comparison_model(profiles, TAXONOMY, THRESHOLDS, GENERATED)
    return model, profiles


def test_template_renders_group_tabs_and_feature_table():
    model, profiles = _model_and_profiles({"tool_a": "has", "tool_b": "not_found"})
    html = render_comparison_html(model, profiles)
    assert "Code Generation" in html
    assert "Inline completion" in html
    assert "Tool A" in html and "Tool B" in html


def test_capgemini_theme_tokens_are_applied():
    model, profiles = _model_and_profiles({"tool_a": "has"})
    html = render_comparison_html(model, profiles)
    assert "#0058ab" in html.lower()
    assert "cg-header" in html
    assert '"Ubuntu"' in html
    assert "Montserrat" not in html
    assert 'alt="Capgemini"' in html
    assert "cg-icon-brand-mark" not in html


def test_output_has_no_external_resource_references():
    model, profiles = _model_and_profiles({"tool_a": "has", "tool_b": "has"})
    html = render_comparison_html(model, profiles)
    class ResourceParser(HTMLParser):
        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            attributes = dict(attrs)
            for key in ("src", "srcset", "poster"):
                if attributes.get(key):
                    assert attributes[key].startswith("data:")
            if tag in {"link", "use"}:
                assert attributes.get("href", "").startswith(("data:", "#"))

    ResourceParser().feed(html)
    for url in re.findall(r"url\(\s*['\"]?([^)'\"\s]+)", html):
        assert url.startswith(("data:", "#"))
    assert "fonts/ubuntu" not in html


def test_navigation_and_details_are_keyboard_addressable():
    model, profiles = _model_and_profiles({"tool_a": "has", "tool_b": "partial"})
    html = render_comparison_html(model, profiles)
    assert 'aria-controls="page-profiles" aria-selected="false"' in html
    assert 'aria-labelledby="profile-tab-tool_a"' in html
    assert 'class="cg-feature-name" tabindex="0" data-bs-toggle="tooltip"' in html
    assert 'for="filter-code_generation"' in html
    assert 'role="region" aria-label="Code Generation comparison table" tabindex="0"' in html
    assert 'data-cg-open-profiles' in html
    assert 'data-cg-scroll-target' not in html


def test_research_notices_and_asset_attribution_remain_available():
    profiles = [_profile("tool_a", "uncertain", researched_at="2025-01-01T00:00:00Z")]
    model = build_comparison_model(profiles, TAXONOMY, THRESHOLDS, GENERATED)
    html = render_comparison_html(model, profiles)
    assert 'class="cg-warning"' in html
    assert "review freshness and coverage" in html
    assert "Stale" in html
    for warning in model.warnings:
        assert escape(warning) in html
    assert "UBUNTU FONT LICENCE Version 1.0" in html
    assert "not a Capgemini Research Institute publication" in html


def test_asset_licenses_remain_in_source_without_a_visible_report_section():
    model, profiles = _model_and_profiles({"tool_a": "has"})
    html = render_comparison_html(model, profiles)
    assert "About this report" not in html
    assert "cg-attribution" not in html
    comments: list[str] = []

    class LicenseParser(HTMLParser):
        def handle_comment(self, data: str) -> None:
            comments.append(data)

        def handle_data(self, data: str) -> None:
            assert "UBUNTU FONT LICENCE" not in data
            assert "Copyright 2011 Canonical" not in data

    LicenseParser().feed(html)
    assert any("UBUNTU FONT LICENCE Version 1.0" in comment for comment in comments)


def test_summary_distinguishes_features_from_results_and_counts_unresearched():
    model, profiles = _model_and_profiles({"tool_a": "has", "tool_b": "partial"})
    profiles[1]["feature_results"] = []
    model = build_comparison_model(profiles, TAXONOMY, THRESHOLDS, GENERATED)
    html = render_comparison_html(model, profiles)
    assert "Results across tools" in html
    assert "1 unresearched" in html
    assert 'aria-label="1 Has"' in html


def test_tool_names_and_custom_titles_are_preserved_and_escaped():
    profiles = [_profile("tool_a", "has")]
    profiles[0]["tool"]["name"] = 'lowerCASE <script>alert("x")</script>'
    model = build_comparison_model(profiles, TAXONOMY, THRESHOLDS, GENERATED)
    html = render_comparison_html(model, profiles, title="<Executive comparison>")
    assert "lowerCASE &lt;script&gt;" in html
    assert "<script>alert" not in html
    assert "&lt;Executive comparison&gt;" in html


def test_profile_tab_shows_description_and_facts():
    model, profiles = _model_and_profiles({"tool_a": "has"})
    profiles[0]["additional_facts"] = [
        {"fact_id": "pricing", "topic": "Pricing", "description": "Free tier.",
         "evidence": [{"source_id": "src_docs", "excerpt": "free"}]}
    ]
    html = render_comparison_html(model, profiles, descriptions={"tool_a": "## Overview\nGreat **tool**."})
    assert "Overview" in html
    assert "<strong>tool</strong>" in html
    assert "Pricing" in html


def test_summary_kpi_section_renders():
    model, profiles = _model_and_profiles({"tool_a": "has", "tool_b": "not_found"})
    html = render_comparison_html(model, profiles)
    assert "cg-kpi-card" in html
    assert "Tools compared" in html


def test_distribution_flag_renders_as_icon_with_tooltip():
    # A partial cell yields the "Varied implementation" flag with only two tools.
    model, profiles = _model_and_profiles({"tool_a": "has", "tool_b": "partial"})
    html = render_comparison_html(model, profiles)
    # Rendered as a colour-coded icon chip, not raw text.
    assert 'class="cg-flag-icon cg-flag-varied"' in html
    assert "#cg-icon-flag-varied" in html
    # The label is only revealed on hover (tooltip) and exposed to assistive tech.
    assert 'data-bs-toggle="tooltip" title="Varied implementation"' in html
    assert 'aria-label="Varied implementation"' in html
    # A legend decodes every flag icon.
    assert "cg-flag-legend" in html


def test_unresearched_cell_is_rendered_as_dash():
    profiles = [_profile("tool_a", "has")]
    # remove the only feature result -> unresearched
    profiles[0]["feature_results"] = []
    model = build_comparison_model(profiles, TAXONOMY, THRESHOLDS, GENERATED)
    html = render_comparison_html(model, profiles)
    assert "cg-status-requires_research" in html


def test_profile_tab_groups_feature_results_by_taxonomy_group():
    model, profiles = _model_and_profiles({"tool_a": "has"})
    html = render_comparison_html(model, profiles)
    assert '<h3 class="h6 mt-3">Features</h3>' in html
    assert "Code Generation" in html  # native taxonomy group heading, not just the grid tab


def test_profile_tab_shows_enriched_use_case_fields():
    model, profiles = _model_and_profiles({"tool_a": "has"})
    profiles[0]["use_cases"] = [
        {
            "use_case_id": "uc_inferred",
            "title": "Refactor at scale",
            "description": "Infer from completion capability.",
            "kind": "inferred",
            "rationale": "Because inline completion is present.",
            "supporting_features": ["inline_code_completion"],
        },
        {
            "use_case_id": "uc_documented",
            "title": "Onboarding",
            "description": "Documented onboarding flow.",
            "kind": "documented",
            "evidence": [{"source_id": "src_docs", "excerpt": "For onboarding."}],
        },
    ]
    html = render_comparison_html(model, profiles)
    assert "Because inline completion is present." in html
    assert "For onboarding." in html
    assert "Inferred" in html and "Documented" in html


def test_additional_facts_are_grouped_with_other_bucket_for_unmapped_topics():
    model, profiles = _model_and_profiles({"tool_a": "has"})
    profiles[0]["additional_facts"] = [
        {"fact_id": "pricing_note", "topic": "Pricing", "description": "Free tier.",
         "evidence": [{"source_id": "src_docs", "excerpt": "free"}]},
        {"fact_id": "roadmap_notes", "topic": "Roadmap notes", "description": "Unmapped topic.",
         "evidence": [{"source_id": "src_docs", "excerpt": "roadmap"}]},
    ]
    mapping = {
        "revision": 1,
        "sections": [{"heading": "Pricing & licensing", "fact_ids": [], "topics": ["Pricing"]}],
    }
    html = render_comparison_html(model, profiles, additional_fact_sections=mapping)
    assert "Pricing &amp; licensing" in html
    assert ">Other<" in html
    assert "Roadmap notes" in html


def test_release_history_renders_with_freshness_caveat_newest_first():
    model, profiles = _model_and_profiles({"tool_a": "has"})
    profiles[0]["release_history"] = [
        {"release_id": "r1", "version": "1.0.0", "release_date": "2026-01-01",
         "summary": "Initial release.", "evidence": [{"source_id": "src_docs", "excerpt": "1.0.0"}]},
        {"release_id": "r2", "version": "1.1.0", "release_date": "2026-06-01",
         "summary": "Adds foo.", "evidence": [{"source_id": "src_docs", "excerpt": "1.1.0"}]},
    ]
    html = render_comparison_html(model, profiles)
    assert "Release history reflects data available as of 20 Jul 2026" in html
    assert html.index("1.1.0") < html.index("1.0.0")  # newest first


def test_release_history_absent_renders_no_section():
    model, profiles = _model_and_profiles({"tool_a": "has"})
    html = render_comparison_html(model, profiles)
    assert "Release history" not in html


def test_release_history_renders_product_version_when_present():
    model, profiles = _model_and_profiles({"tool_a": "has"})
    profiles[0]["release_history"] = [
        {"release_id": "r1", "version": "Claude Opus 5 model availability",
         "product_version": "v1.73", "release_date": "2026-07-24",
         "summary": "Adds Claude Opus 5.", "evidence": [{"source_id": "src_docs", "excerpt": "x"}]},
    ]
    html = render_comparison_html(model, profiles)
    assert "Claude Opus 5 model availability</strong> &middot; 2026-07-24 &middot; v1.73" in html


def test_release_history_omits_product_version_when_absent():
    model, profiles = _model_and_profiles({"tool_a": "has"})
    profiles[0]["release_history"] = [
        {"release_id": "r1", "version": "Gemini 3.6 Flash is now available in GitHub Copilot",
         "release_date": "2026-07-21", "summary": "Adds Gemini 3.6 Flash.",
         "evidence": [{"source_id": "src_docs", "excerpt": "x"}]},
    ]
    html = render_comparison_html(model, profiles)
    assert "Gemini 3.6 Flash is now available in GitHub Copilot</strong> &middot; 2026-07-21" in html
    assert "2026-07-21 &middot;" not in html
