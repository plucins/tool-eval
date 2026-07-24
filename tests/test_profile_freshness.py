"""Business rules for comparison freshness and date spread (requirements Sec 19)."""

from __future__ import annotations

from tool_eval.comparison.freshness import (
    FRESHNESS_AGING,
    FRESHNESS_CURRENT,
    FRESHNESS_STALE,
    FreshnessThresholds,
    age_in_days,
    date_spread_days,
    freshness_bucket,
    spread_warning,
)

GENERATED = "2026-07-24T00:00:00Z"
DEFAULTS = FreshnessThresholds()


def _days_before(days: int) -> str:
    from datetime import datetime, timedelta, timezone

    base = datetime(2026, 7, 24, tzinfo=timezone.utc) - timedelta(days=days)
    return base.strftime("%Y-%m-%dT%H:%M:%SZ")


def test_profile_within_30_days_is_current():
    assert freshness_bucket(_days_before(0), GENERATED, DEFAULTS) == FRESHNESS_CURRENT
    assert freshness_bucket(_days_before(30), GENERATED, DEFAULTS) == FRESHNESS_CURRENT


def test_profile_between_31_and_60_days_is_aging():
    assert freshness_bucket(_days_before(31), GENERATED, DEFAULTS) == FRESHNESS_AGING
    assert freshness_bucket(_days_before(60), GENERATED, DEFAULTS) == FRESHNESS_AGING


def test_profile_older_than_60_days_is_stale():
    assert freshness_bucket(_days_before(61), GENERATED, DEFAULTS) == FRESHNESS_STALE
    assert freshness_bucket(_days_before(365), GENERATED, DEFAULTS) == FRESHNESS_STALE


def test_research_date_after_generation_clamps_age_to_zero():
    future = "2026-08-01T00:00:00Z"
    assert age_in_days(future, GENERATED) == 0
    assert freshness_bucket(future, GENERATED, DEFAULTS) == FRESHNESS_CURRENT


def test_date_spread_over_14_days_raises_warning():
    dates = [_days_before(0), _days_before(20)]
    assert date_spread_days(dates) == 20
    assert spread_warning(dates, DEFAULTS) is True


def test_date_spread_within_threshold_has_no_warning():
    dates = [_days_before(0), _days_before(14)]
    assert spread_warning(dates, DEFAULTS) is False


def test_single_profile_has_no_spread_warning():
    assert date_spread_days([_days_before(0)]) == 0
    assert spread_warning([_days_before(0)], DEFAULTS) is False


def test_thresholds_are_configurable_from_yaml_mapping():
    thresholds = FreshnessThresholds.from_config(
        {"current_max_days": 7, "aging_max_days": 14, "date_spread_warning_days": 3}
    )
    assert freshness_bucket(_days_before(10), GENERATED, thresholds) == FRESHNESS_AGING
    assert spread_warning([_days_before(0), _days_before(5)], thresholds) is True
