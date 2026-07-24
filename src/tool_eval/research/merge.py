"""Deterministic merge of worker results + completeness verification (D-010).

Merging is a single-writer Python operation (D-004): the lead agent waits for
every mandatory task, then Python combines the validated worker results into
one canonical set. No semantic transformation happens - workers already emit
the profile's feature-record format (D-016) - so merge is pure set/dedup logic
and is fully deterministic (focus area).

The completeness gate (Increment 2 gate; requirements Sec 16) requires exactly
one result for every feature in the effective taxonomy revision: missing,
duplicate, or foreign feature_ids are all errors.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class MergeError:
    code: str
    message: str
    feature_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        record = {"code": self.code, "message": self.message}
        if self.feature_id is not None:
            record["feature_id"] = self.feature_id
        return record


def _merge_sources(
    worker_results: list[dict[str, Any]], errors: list[MergeError]
) -> list[dict[str, Any]]:
    """Register each source once (D-016). Same id with different data is a conflict."""
    registry: dict[str, dict[str, Any]] = {}
    for wr in worker_results:
        for src in wr.get("sources", []) or []:
            sid = src["source_id"]
            existing = registry.get(sid)
            if existing is None:
                registry[sid] = src
            elif existing != src:
                errors.append(
                    MergeError(
                        code="VALIDATION_SOURCE_CONFLICT",
                        message=(
                            f"source_id {sid!r} defined inconsistently across workers"
                        ),
                    )
                )
    # Deterministic order: sorted by source_id.
    return [registry[sid] for sid in sorted(registry)]


def _merge_feature_results(
    worker_results: list[dict[str, Any]], errors: list[MergeError]
) -> list[dict[str, Any]]:
    by_feature: dict[str, dict[str, Any]] = {}
    for wr in worker_results:
        for fr in wr.get("feature_results", []) or []:
            fid = fr["feature_id"]
            if fid in by_feature:
                errors.append(
                    MergeError(
                        code="VALIDATION_DUPLICATE_FEATURE_RESULT",
                        message=f"more than one result returned for feature {fid!r}",
                        feature_id=fid,
                    )
                )
                continue
            by_feature[fid] = fr
    return [by_feature[fid] for fid in sorted(by_feature)]


def _merge_named(
    worker_results: list[dict[str, Any]], key: str, id_field: str
) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for wr in worker_results:
        for item in wr.get(key, []) or []:
            seen.setdefault(item[id_field], item)
    return [seen[i] for i in sorted(seen)]


def merge_results(worker_results: list[dict[str, Any]]) -> tuple[dict[str, Any], list[MergeError]]:
    """Merge validated worker results into one canonical set.

    Returns (merged, errors). ``merged`` has keys ``sources``,
    ``feature_results``, ``candidates`` and ``unresolved_issues``.
    """
    errors: list[MergeError] = []
    merged = {
        "sources": _merge_sources(worker_results, errors),
        "feature_results": _merge_feature_results(worker_results, errors),
        "candidates": _merge_named(worker_results, "candidates", "candidate_id"),
        "unresolved_issues": [],
    }
    return merged, errors


def verify_completeness(
    feature_results: Iterable[dict[str, Any]],
    taxonomy_feature_ids: Iterable[str],
) -> list[MergeError]:
    """Exactly one result per taxonomy feature; no missing/duplicate/foreign ids."""
    errors: list[MergeError] = []
    expected = set(taxonomy_feature_ids)

    counts: dict[str, int] = {}
    for fr in feature_results:
        fid = fr["feature_id"]
        counts[fid] = counts.get(fid, 0) + 1

    for fid in sorted(expected - set(counts)):
        errors.append(
            MergeError(
                code="VALIDATION_FEATURE_RESULT_MISSING",
                message=f"no result for taxonomy feature {fid!r}",
                feature_id=fid,
            )
        )
    for fid in sorted(set(counts) - expected):
        errors.append(
            MergeError(
                code="VALIDATION_FOREIGN_FEATURE_RESULT",
                message=f"result for {fid!r} which is not in the effective taxonomy",
                feature_id=fid,
            )
        )
    for fid, n in sorted(counts.items()):
        if n > 1 and fid in expected:
            errors.append(
                MergeError(
                    code="VALIDATION_DUPLICATE_FEATURE_RESULT",
                    message=f"{n} results for feature {fid!r}; exactly one required",
                    feature_id=fid,
                )
            )
    return errors
