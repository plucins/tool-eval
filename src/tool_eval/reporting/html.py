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

from tool_eval.comparison import flags as _flags
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
# Maps each distribution flag label (from :mod:`tool_eval.comparison.flags`) to a
# short slug used by the template to pick the flag's icon (``#cg-icon-flag-<key>``)
# and colour class (``cg-flag-<key>``). Kept in sync with the flag constants so a
# renamed label surfaces here instead of silently losing its icon; unknown labels
# fall back to the neutral ``other`` glyph in the template.
FLAG_META: dict[str, str] = {
    _flags.FLAG_COMMON: "common",
    _flags.FLAG_ONLY_ONE_LACKS_IT: "only_lacks",
    _flags.FLAG_ONLY_ONE_HAS_IT: "only_has",
    _flags.FLAG_RARE: "rare",
    _flags.FLAG_SPLIT: "split",
    _flags.FLAG_VARIED: "varied",
}
# Presentational icon/description lookup for the fixed feature-taxonomy groups
# (config/feature-taxonomy.yaml). Purely cosmetic: an unknown group_id (e.g. a
# future taxonomy revision, or a test fixture's ad-hoc group) falls back to the
# neutral "other" icon and an empty description rather than failing to render.
GROUP_ICONS: dict[str, str] = {
    "code_authoring": "code_authoring",
    "agentic_execution": "agentic_execution",
    "agent_customization_orchestration": "agent_customization_orchestration",
    "context_quality": "context_quality",
    "workflow_ecosystem": "workflow_ecosystem",
    "security_governance": "security_governance",
}
GROUP_DESCRIPTIONS: dict[str, str] = {
    "code_authoring": "Compare inline completion and code generation capabilities",
    "agentic_execution": "Compare autonomous task execution and runtime behaviour",
    "agent_customization_orchestration": "Compare agent customization and multi-agent orchestration",
    "context_quality": "Compare context handling, search, and code quality tooling",
    "workflow_ecosystem": "Compare workflow integration and ecosystem reach",
    "security_governance": "Compare security capabilities and governance features",
}


def _environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _summary_stats(model: ComparisonModel) -> dict[str, Any]:
    """Derive KPI counts for the report's summary row from the view-model."""
    status_counts: dict[str, int] = {"has": 0, "partial": 0, "not_found": 0, "uncertain": 0, "unresearched": 0}
    freshness_counts: dict[str, int] = {"current": 0, "aging": 0, "stale": 0}
    feature_count = 0
    flagged_feature_count = 0
    for group in model.groups:
        for feature in group.features:
            feature_count += 1
            if feature.flags:
                flagged_feature_count += 1
            for cell in feature.cells:
                key = cell.status if cell.researched and cell.status else "unresearched"
                status_counts[key] = status_counts.get(key, 0) + 1
    for tool in model.tools:
        freshness_counts[tool.freshness] = freshness_counts.get(tool.freshness, 0) + 1
    return {
        "tool_count": len(model.tools),
        "group_count": len(model.groups),
        "feature_count": feature_count,
        "flagged_feature_count": flagged_feature_count,
        "warning_count": len(model.warnings),
        "status_counts": status_counts,
        "freshness_counts": freshness_counts,
    }


def _tool_feature_sections(model: ComparisonModel, tool_id: str) -> list[dict[str, Any]]:
    """Group one tool's researched feature_results under native taxonomy headings.

    Reuses the multi-tool grouping already built into ``model.groups`` (ADR-002:
    "zero new mechanism" for feature_results) rather than re-deriving group
    membership. An unresearched placeholder cell has nothing to show in a
    single-tool report, so only researched cells are included.
    """
    sections: list[dict[str, Any]] = []
    for group in model.groups:
        rows = [
            {"feature": feature, "cell": cell}
            for feature in group.features
            for cell in feature.cells
            if cell.tool_id == tool_id and cell.researched
        ]
        if rows:
            sections.append({"name": group.name, "rows": rows})
    return sections


def _fact_section_lookup(
    mapping_data: dict[str, Any] | None,
) -> tuple[list[str], dict[str, str], dict[str, str]]:
    headings: list[str] = []
    by_fact_id: dict[str, str] = {}
    by_topic: dict[str, str] = {}
    for section in (mapping_data or {}).get("sections", []) or []:
        heading = section["heading"]
        headings.append(heading)
        for fid in section.get("fact_ids", []) or []:
            by_fact_id[fid] = heading
        for topic in section.get("topics", []) or []:
            by_topic[topic.strip().lower()] = heading
    return headings, by_fact_id, by_topic


def _group_additional_facts(
    facts: list[dict[str, Any]], mapping_data: dict[str, Any] | None
) -> list[tuple[str, list[dict[str, Any]]]]:
    """Bucket a tool's additional_facts into named sections (ADR-002).

    Order follows the config mapping; a fact matching neither a ``fact_id`` nor
    a ``topic`` in the mapping lands in a trailing "Other" bucket so a stale
    mapping table stays visible in the report, not silent.
    """
    headings, by_fact_id, by_topic = _fact_section_lookup(mapping_data)
    buckets: dict[str, list[dict[str, Any]]] = {h: [] for h in headings}
    other: list[dict[str, Any]] = []
    for fact in facts:
        heading = by_fact_id.get(fact.get("fact_id")) or by_topic.get(
            (fact.get("topic") or "").strip().lower()
        )
        (buckets[heading] if heading is not None else other).append(fact)
    grouped = [(h, buckets[h]) for h in headings if buckets[h]]
    if other:
        grouped.append(("Other", other))
    return grouped


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
    additional_fact_sections: dict[str, Any] | None = None,
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
    tool_feature_sections = {
        tool.tool_id: _tool_feature_sections(model, tool.tool_id) for tool in model.tools
    }
    tool_fact_sections = {
        tool_id: _group_additional_facts(
            profile.get("additional_facts", []) or [], additional_fact_sections
        )
        for tool_id, profile in profiles_by_id.items()
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
        flag_meta=FLAG_META,
        group_icons=GROUP_ICONS,
        group_descriptions=GROUP_DESCRIPTIONS,
        summary=_summary_stats(model),
        tool_feature_sections=tool_feature_sections,
        tool_fact_sections=tool_fact_sections,
    )
