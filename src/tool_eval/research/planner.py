"""Deterministic bundle planner and worker-wave scheduler (D-010).

Planning rules (D-010):

- a typical bundle contains 2-4 related features from the same group;
- a complex, disputed, or especially expensive feature receives its own task
  (callers pass those feature_ids via ``isolate``);
- source discovery may run concurrently, but each feature still returns its own
  record - bundling is only about how work is grouped for a worker;
- after an error, a bundle is retried and, if the problem repeats, split into
  individual features (see :func:`split_bundle`);
- at most ``max_concurrent`` workers run in one wave.

Everything here is a pure function of its inputs so planning is reproducible
(focus area: determinism). No filesystem or model access.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable


@dataclass(frozen=True)
class Bundle:
    bundle_id: str
    group: str
    feature_ids: tuple[str, ...]
    isolated: bool = False

    def to_task_manifest(self, run_id: str, skill: str = "feature-research") -> dict[str, Any]:
        """Render a task.json manifest for this bundle (task.schema.json)."""
        return {
            "task_id": self.bundle_id,
            "run_id": run_id,
            "task_type": "feature-research",
            "skill": skill,
            "feature_ids": list(self.feature_ids),
            "inputs": {"group": self.group, "isolated": self.isolated},
            "output_path": "result.json",
        }


def _chunk_group(
    group: str, feature_ids: list[str], *, min_size: int, max_size: int
) -> list[list[str]]:
    """Chunk one group's features into bundles of size in [min_size, max_size].

    Deterministic and stable: features are taken in the order given. A trailing
    chunk smaller than ``min_size`` is rebalanced with the previous chunk so no
    bundle falls below ``min_size`` - unless the whole group has fewer than
    ``min_size`` features, in which case the group is a single (small) bundle.
    """
    n = len(feature_ids)
    if n == 0:
        return []
    if n <= max_size:
        # Fits in one bundle (covers the singleton / small-group case).
        return [list(feature_ids)]

    chunks = [feature_ids[i : i + max_size] for i in range(0, n, max_size)]
    if len(chunks[-1]) < min_size:
        # Pull items from the previous chunk to lift the tail up to min_size.
        deficit = min_size - len(chunks[-1])
        moved = chunks[-2][len(chunks[-2]) - deficit :]
        chunks[-2] = chunks[-2][: len(chunks[-2]) - deficit]
        chunks[-1] = moved + chunks[-1]
    return chunks


def plan_bundles(
    features: Iterable[dict[str, Any]],
    *,
    min_size: int,
    max_size: int,
    isolate: Iterable[str] = (),
) -> list[Bundle]:
    """Plan feature bundles from taxonomy features (D-010).

    ``features`` are taxonomy entries with at least ``feature_id`` and ``group``.
    ``isolate`` feature_ids each get their own single-feature bundle regardless
    of group size (complex/disputed/expensive features).
    """
    if min_size < 1 or max_size < min_size:
        raise ValueError(f"invalid bundle sizes: min={min_size} max={max_size}")

    isolate_set = set(isolate)

    # Group order and within-group order are stabilised by sorting on ids, so a
    # given taxonomy always yields the same plan (determinism).
    by_group: dict[str, list[str]] = {}
    isolated_ids: list[str] = []
    for feat in features:
        fid = feat["feature_id"]
        if fid in isolate_set:
            isolated_ids.append(fid)
            continue
        by_group.setdefault(feat["group"], []).append(fid)

    bundles: list[Bundle] = []

    for group in sorted(by_group):
        feature_ids = sorted(by_group[group])
        chunks = _chunk_group(group, feature_ids, min_size=min_size, max_size=max_size)
        for idx, chunk in enumerate(chunks, start=1):
            bundles.append(
                Bundle(
                    bundle_id=f"feat-{group}-{idx:02d}",
                    group=group,
                    feature_ids=tuple(chunk),
                )
            )

    for fid in sorted(isolated_ids):
        bundles.append(
            Bundle(
                bundle_id=f"feat-solo-{fid}",
                group=_group_of(features, fid),
                feature_ids=(fid,),
                isolated=True,
            )
        )

    return bundles


def _group_of(features: Iterable[dict[str, Any]], feature_id: str) -> str:
    for feat in features:
        if feat["feature_id"] == feature_id:
            return feat["group"]
    return "unknown"


def split_bundle(bundle: Bundle) -> list[Bundle]:
    """Split a bundle into individual single-feature bundles (D-010 retry path)."""
    return [
        Bundle(
            bundle_id=f"{bundle.bundle_id}-s{i:02d}",
            group=bundle.group,
            feature_ids=(fid,),
            isolated=True,
        )
        for i, fid in enumerate(bundle.feature_ids, start=1)
    ]


def plan_waves(bundles: list[Bundle], *, max_concurrent: int) -> list[list[Bundle]]:
    """Group bundles into sequential waves of at most ``max_concurrent`` each."""
    if max_concurrent < 1:
        raise ValueError(f"max_concurrent must be >= 1, got {max_concurrent}")
    return [
        bundles[i : i + max_concurrent] for i in range(0, len(bundles), max_concurrent)
    ]
