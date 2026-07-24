"""Deterministic comparison view-model (requirements Sec 18-19).

Pure assembly of the comparison table from a set of already-loaded, validated
profiles plus the effective taxonomy. No filesystem, no clock, no rendering:
:func:`build_comparison_model` returns frozen dataclasses that the reporting
layer renders. Group and feature order follow the taxonomy; tool columns follow
the caller's requested order, so repeated builds are byte-for-byte identical
(Increment 3 gate: deterministic flags/dates/warnings).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tool_eval.comparison.flags import feature_flags
from tool_eval.comparison.freshness import (
    FRESHNESS_STALE,
    FreshnessThresholds,
    freshness_bucket,
    spread_warning,
)


@dataclass(frozen=True)
class ToolColumn:
    tool_id: str
    name: str
    vendor: str | None
    homepage: str | None
    researched_at: str
    freshness: str
    profile_state: str


@dataclass(frozen=True)
class Cell:
    tool_id: str
    status: str | None  # None => unresearched cell (excluded from flags)
    researched: bool
    rationale: str
    constraints: tuple[dict[str, Any], ...]
    evidence: tuple[dict[str, Any], ...]

    @property
    def has_constraints(self) -> bool:
        return bool(self.constraints)


@dataclass(frozen=True)
class FeatureRow:
    feature_id: str
    name: str
    definition: str
    cells: tuple[Cell, ...]
    flags: tuple[str, ...]


@dataclass(frozen=True)
class FeatureGroup:
    group_id: str
    name: str
    features: tuple[FeatureRow, ...]


@dataclass(frozen=True)
class ComparisonModel:
    generated_at: str
    tools: tuple[ToolColumn, ...]
    groups: tuple[FeatureGroup, ...]
    warnings: tuple[str, ...]


def _tool_column(profile: dict[str, Any], generated_at: str, thresholds: FreshnessThresholds) -> ToolColumn:
    tool = profile["tool"]
    research = profile["research"]
    researched_at = research["researched_at"]
    return ToolColumn(
        tool_id=tool["tool_id"],
        name=tool["name"],
        vendor=tool.get("vendor"),
        homepage=tool.get("homepage"),
        researched_at=researched_at,
        freshness=freshness_bucket(researched_at, generated_at, thresholds),
        profile_state=research["profile_state"],
    )


def _results_by_feature(profile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {fr["feature_id"]: fr for fr in profile.get("feature_results", [])}


def _cell(tool_id: str, result: dict[str, Any] | None) -> Cell:
    if result is None:
        return Cell(
            tool_id=tool_id,
            status=None,
            researched=False,
            rationale="",
            constraints=(),
            evidence=(),
        )
    return Cell(
        tool_id=tool_id,
        status=result["status"],
        researched=True,
        rationale=result.get("rationale", ""),
        constraints=tuple(result.get("constraints", []) or []),
        evidence=tuple(result.get("evidence", []) or []),
    )


def build_comparison_model(
    profiles: list[dict[str, Any]],
    taxonomy: dict[str, Any],
    thresholds: FreshnessThresholds,
    generated_at: str,
) -> ComparisonModel:
    """Assemble the comparison view-model. Tool order == ``profiles`` order."""
    tools = tuple(_tool_column(p, generated_at, thresholds) for p in profiles)
    results_per_tool = [_results_by_feature(p) for p in profiles]

    features_by_group: dict[str, list[dict[str, Any]]] = {}
    for feature in taxonomy.get("features", []):
        features_by_group.setdefault(feature["group"], []).append(feature)

    groups: list[FeatureGroup] = []
    for group in taxonomy.get("groups", []):
        gid = group["id"]
        rows: list[FeatureRow] = []
        for feature in features_by_group.get(gid, []):
            fid = feature["feature_id"]
            cells = tuple(
                _cell(tools[i].tool_id, results_per_tool[i].get(fid))
                for i in range(len(profiles))
            )
            flags = tuple(feature_flags([c.status for c in cells]))
            rows.append(
                FeatureRow(
                    feature_id=fid,
                    name=feature.get("name", fid),
                    definition=feature.get("definition", ""),
                    cells=cells,
                    flags=flags,
                )
            )
        groups.append(FeatureGroup(group_id=gid, name=group.get("name", gid), features=tuple(rows)))

    warnings = _warnings(profiles, tools, thresholds)
    return ComparisonModel(
        generated_at=generated_at,
        tools=tools,
        groups=tuple(groups),
        warnings=warnings,
    )


def _warnings(
    profiles: list[dict[str, Any]],
    tools: tuple[ToolColumn, ...],
    thresholds: FreshnessThresholds,
) -> tuple[str, ...]:
    warnings: list[str] = []
    dates = [t.researched_at for t in tools]
    if spread_warning(dates, thresholds):
        warnings.append(
            f"Profile research dates span more than {thresholds.date_spread_warning_days} days; "
            "compare freshness per tool."
        )
    for tool in tools:
        if tool.profile_state == "requires_research":
            warnings.append(
                f"{tool.name} is marked requires_research; unresearched cells are excluded from flags."
            )
        if tool.freshness == FRESHNESS_STALE:
            warnings.append(f"{tool.name} profile is stale (older than {thresholds.aging_max_days} days).")
    return tuple(warnings)
