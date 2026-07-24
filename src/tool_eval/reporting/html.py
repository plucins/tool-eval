"""Render the comparison view-model into one self-contained HTML string.

Jinja2 is configured with ``autoescape`` and ``StrictUndefined`` (D-014): every
value is HTML-escaped unless it has already been sanitized by
:mod:`tool_eval.reporting.markdown`, and any missing template variable raises
instead of rendering blank. All CSS/JS/fonts are inlined from
:mod:`tool_eval.reporting.assets`, so the output references no CDN or external
file (Increment 3 gate: works offline; R-09/R-10).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markupsafe import Markup

from tool_eval.comparison.model import ComparisonModel
from tool_eval.reporting.assets import BundledAssets, load_assets
from tool_eval.reporting.markdown import render_markdown

_TEMPLATE_DIR = Path(__file__).parent / "templates"
_TEMPLATE_NAME = "comparison.html.j2"

STATUS_LABELS: dict[str, str] = {
    "has": "Has",
    "partial": "Partial",
    "not_found": "Not found",
    "uncertain": "Uncertain",
}
FRESHNESS_LABELS: dict[str, str] = {
    "current": "Current",
    "aging": "Aging",
    "stale": "Stale",
}


def _environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _sources_by_id(profiles: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    registry: dict[str, dict[str, Any]] = {}
    for profile in profiles:
        for source in profile.get("sources", []) or []:
            registry.setdefault(source["source_id"], source)
    return registry


def _safe_markdown(text: str, sources_by_id: dict[str, dict[str, Any]]) -> Markup:
    """Render Markdown to sanitized HTML and mark it safe for the template."""
    return Markup(render_markdown(text, sources_by_id))


def render_comparison_html(
    model: ComparisonModel,
    profiles: list[dict[str, Any]],
    descriptions: dict[str, str] | None = None,
    *,
    assets: BundledAssets | None = None,
    title: str = "AI Coding Tool Comparison",
) -> str:
    """Render the full self-contained HTML document for a comparison."""
    bundle = assets or load_assets()
    sources_by_id = _sources_by_id(profiles)
    descriptions = descriptions or {}

    profiles_by_id = {p["tool"]["tool_id"]: p for p in profiles}
    rendered_descriptions = {
        tool_id: _safe_markdown(text, sources_by_id)
        for tool_id, text in descriptions.items()
    }

    env = _environment()
    env.filters["md"] = lambda text: _safe_markdown(text or "", sources_by_id)
    template = env.get_template(_TEMPLATE_NAME)

    return template.render(
        title=title,
        model=model,
        assets=bundle,
        profiles_by_id=profiles_by_id,
        descriptions=rendered_descriptions,
        status_labels=STATUS_LABELS,
        freshness_labels=FRESHNESS_LABELS,
    )
