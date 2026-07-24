"""End-to-end comparison build: load -> model -> render -> write (Sec 18-19).

The single IO wrapper the CLI calls. It loads and validates the requested active
profiles, builds the deterministic view-model, renders the self-contained HTML,
and writes one file under ``outputs/comparisons/``. It performs no research and
no network access (Sec 3.7); reasoning stays in the harness, determinism here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tool_eval.comparison.freshness import FreshnessThresholds
from tool_eval.comparison.loader import load_comparison
from tool_eval.comparison.model import build_comparison_model
from tool_eval.config import load_config_bundle
from tool_eval.errors import ErrorFamily, ToolEvalError
from tool_eval.paths import ensure_runtime_dirs, resolve_within
from tool_eval.reporting.html import render_comparison_html


@dataclass(frozen=True)
class ComparisonBuild:
    output_path: Path
    tool_ids: list[str]
    warnings: list[str]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _default_output_name(tool_ids: list[str]) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    slug = "-".join(tool_ids)
    return f"compare-{slug}-{stamp}.html"


def _freshness_thresholds(root: Path) -> FreshnessThresholds:
    bundle = load_config_bundle(root)
    data = bundle.files["freshness.yaml"].data if "freshness.yaml" in bundle.files else {}
    return FreshnessThresholds.from_config(data or {})


def _taxonomy(root: Path) -> dict[str, Any]:
    bundle = load_config_bundle(root)
    return bundle.files["feature-taxonomy.yaml"].data


def build_comparison(
    root: Path,
    tool_ids: list[str],
    *,
    output_name: str | None = None,
    generated_at: str | None = None,
) -> ComparisonBuild:
    """Build one self-contained HTML comparison for ``tool_ids``.

    ``output_name`` is a filename (not a path) written under
    ``outputs/comparisons/``; it is validated to stay inside that directory
    (D-017). ``generated_at`` is injectable for deterministic tests.
    """
    ensure_runtime_dirs(root)
    generated_at = generated_at or _utc_now_iso()

    loaded = load_comparison(root, tool_ids)
    thresholds = _freshness_thresholds(root)
    model = build_comparison_model(loaded.profiles, _taxonomy(root), thresholds, generated_at)

    html = render_comparison_html(model, loaded.profiles, loaded.descriptions)

    comparisons_dir = root / "outputs" / "comparisons"
    name = output_name or _default_output_name(tool_ids)
    if "/" in name or "\\" in name:
        raise ToolEvalError(
            code=f"{ErrorFamily.INPUT}_INVALID_OUTPUT_NAME",
            message=f"--out must be a filename, not a path: {name!r}.",
        )
    output_path = resolve_within(comparisons_dir, name)
    output_path.write_text(html, encoding="utf-8")

    # Loader warnings (revisions) + model warnings (freshness/spread/state),
    # de-duplicated while preserving order.
    all_warnings: list[str] = []
    for warning in [*loaded.warnings, *model.warnings]:
        if warning not in all_warnings:
            all_warnings.append(warning)

    return ComparisonBuild(output_path=output_path, tool_ids=list(tool_ids), warnings=all_warnings)
