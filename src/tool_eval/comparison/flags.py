"""Deterministic distribution flags for a feature across the compared tools.

Pure functions implementing requirements Sec 18. Flags always describe the
*compared set*, never the wider market. Given the per-tool cell statuses for one
feature, :func:`feature_flags` returns the display labels that apply.

Rules (Sec 18):
- ``has`` with a constraint still counts as ``has`` (the caller passes the
  normalized status; constraints are tracked separately).
- ``partial`` counts as neither ``has`` nor ``not_found``.
- an ``uncertain`` or unresearched cell (``None``) excludes the feature from all
  flags.
- any ``partial`` produces ``Varied implementation``.
- the five distribution flags require at least four tools and a complete set of
  unambiguous results (every cell ``has`` or ``not_found`` - no partial /
  uncertain / unresearched).
Flags may coexist.
"""

from __future__ import annotations

STATUS_HAS = "has"
STATUS_PARTIAL = "partial"
STATUS_NOT_FOUND = "not_found"
STATUS_UNCERTAIN = "uncertain"

FLAG_ONLY_ONE_HAS_IT = "Only one has it"
FLAG_ONLY_ONE_LACKS_IT = "Only one lacks it"
FLAG_RARE = "Rare"
FLAG_COMMON = "Common in this comparison"
FLAG_SPLIT = "Split"
FLAG_VARIED = "Varied implementation"

MIN_TOOLS_FOR_DISTRIBUTION = 4


def is_excluded(cells: list[str | None]) -> bool:
    """A feature is excluded from flags if any cell is uncertain or unresearched."""
    return any(cell is None or cell == STATUS_UNCERTAIN for cell in cells)


def feature_flags(cells: list[str | None]) -> list[str]:
    """Return every flag label that applies to one feature's row of cells.

    ``cells`` holds one entry per compared tool: a status string
    (``has`` / ``partial`` / ``not_found`` / ``uncertain``) or ``None`` for an
    unresearched cell. Order of the returned labels is stable.
    """
    if is_excluded(cells):
        return []

    flags: list[str] = []
    has = cells.count(STATUS_HAS)
    not_found = cells.count(STATUS_NOT_FOUND)
    partial = cells.count(STATUS_PARTIAL)
    n = len(cells)

    unambiguous = partial == 0  # every remaining cell is has or not_found
    if n >= MIN_TOOLS_FOR_DISTRIBUTION and unambiguous:
        if has == 1 and not_found == n - 1:
            flags.append(FLAG_ONLY_ONE_HAS_IT)
        if not_found == 1 and has == n - 1:
            flags.append(FLAG_ONLY_ONE_LACKS_IT)
        if has == 2 and not_found == n - 2:
            flags.append(FLAG_RARE)
        if has == n or not_found == 1:
            flags.append(FLAG_COMMON)
        if abs(has - not_found) <= 1:
            flags.append(FLAG_SPLIT)

    if partial > 0:
        flags.append(FLAG_VARIED)

    return flags
