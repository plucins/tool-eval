"""Business rules for rendering the self-contained comparison HTML."""

from __future__ import annotations

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
    assert "#0070ad" in html.lower()          # Capgemini blue
    assert "cg-header" in html                 # gradient header applied
    assert "Montserrat" in html                # typography


def test_output_has_no_external_resource_references():
    model, profiles = _model_and_profiles({"tool_a": "has", "tool_b": "has"})
    html = render_comparison_html(model, profiles)
    # No CDN/network references for styles, scripts, or fonts.
    assert "https://cdn" not in html.lower()
    assert 'src="http' not in html.lower()
    assert 'href="http' not in html.lower() or "docs.example.com" in html  # only profile links may be http(s)
    assert "fonts/montserrat" not in html      # fonts are inlined as data: URIs


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


def test_unresearched_cell_is_rendered_as_dash():
    profiles = [_profile("tool_a", "has")]
    # remove the only feature result -> unresearched
    profiles[0]["feature_results"] = []
    model = build_comparison_model(profiles, TAXONOMY, THRESHOLDS, GENERATED)
    html = render_comparison_html(model, profiles)
    assert "cg-status-requires_research" in html
