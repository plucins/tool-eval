"""Deterministic freshness and date-spread calculations (requirements Sec 19).

Pure functions only - no filesystem, no clock. The comparison's generation date
and each profile's research date are passed in, so results are fully
reproducible (Increment 3 gate: deterministic dates/warnings). Thresholds come
from ``config/freshness.yaml`` and are passed in as a plain mapping.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

FRESHNESS_CURRENT = "current"
FRESHNESS_AGING = "aging"
FRESHNESS_STALE = "stale"


@dataclass(frozen=True)
class FreshnessThresholds:
    """Configurable day thresholds (requirements Sec 19)."""

    current_max_days: int = 30
    aging_max_days: int = 60
    date_spread_warning_days: int = 14

    @classmethod
    def from_config(cls, data: dict[str, Any]) -> "FreshnessThresholds":
        return cls(
            current_max_days=int(data.get("current_max_days", 30)),
            aging_max_days=int(data.get("aging_max_days", 60)),
            date_spread_warning_days=int(data.get("date_spread_warning_days", 14)),
        )


def _parse_instant(value: str) -> datetime:
    """Parse an ISO 8601 timestamp (``...Z`` or offset) into an aware UTC datetime."""
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def age_in_days(researched_at: str, generated_at: str) -> int:
    """Whole days between a profile's research date and the comparison date.

    Never negative: a research date after the generation date clamps to 0.
    """
    delta = _parse_instant(generated_at) - _parse_instant(researched_at)
    days = delta.days
    return days if days > 0 else 0


def freshness_bucket(
    researched_at: str, generated_at: str, thresholds: FreshnessThresholds
) -> str:
    """Bucket a profile as ``current`` / ``aging`` / ``stale`` (Sec 19).

    0..current_max_days => current; current_max+1..aging_max => aging;
    strictly greater than aging_max => stale.
    """
    days = age_in_days(researched_at, generated_at)
    if days <= thresholds.current_max_days:
        return FRESHNESS_CURRENT
    if days <= thresholds.aging_max_days:
        return FRESHNESS_AGING
    return FRESHNESS_STALE


def date_spread_days(researched_dates: list[str]) -> int:
    """Whole-day spread between the oldest and newest research dates."""
    if len(researched_dates) < 2:
        return 0
    instants = [_parse_instant(d) for d in researched_dates]
    spread = max(instants) - min(instants)
    return spread.days


def spread_warning(researched_dates: list[str], thresholds: FreshnessThresholds) -> bool:
    """True when the profile date spread exceeds the configured threshold (Sec 19)."""
    return date_spread_days(researched_dates) > thresholds.date_spread_warning_days
