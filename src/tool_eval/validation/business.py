"""Business-rule validation (D-016): status-dependent rules, referential
integrity, and completeness that JSON Schema cannot express.

Split from JSON Schema on purpose (D-016): the schema guarantees structure and
types; this module enforces the *cross-record* rules - every ``source_id`` a
record references must be a registered source, statuses must carry the evidence
or protocol they require (D-009), exactly one result must exist per feature
(D-010/completeness gate), and the D-009 ``not_found`` checklist must be
complete.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

# Source classes the D-009 protocol expects to have been considered before a
# `not_found` may be recorded. A worker need not have *found* each class, but a
# complete protocol must show it was checked or explicitly noted as an access
# gap. Kept aligned with source.schema.json `source_type` enum.
D009_RELEVANT_SOURCE_CLASSES: tuple[str, ...] = (
    "documentation",
    "product_page",
    "changelog",
    "pricing",
)


@dataclass(frozen=True)
class BusinessError:
    code: str
    message: str
    feature_id: str | None = None
    path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        record: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.feature_id is not None:
            record["feature_id"] = self.feature_id
        if self.path is not None:
            record["path"] = self.path
        return record


def _iter_evidence_source_ids(record: dict[str, Any]) -> Iterable[tuple[str, str]]:
    """Yield (source_id, json-ish path) for every source reference in a record."""
    for i, ev in enumerate(record.get("evidence", []) or []):
        yield ev["source_id"], f"evidence[{i}].source_id"
    for i, c in enumerate(record.get("constraints", []) or []):
        yield c["source_id"], f"constraints[{i}].source_id"
    conflict = record.get("conflict")
    if conflict:
        for i, ev in enumerate(conflict.get("conflicting_evidence", []) or []):
            yield ev["source_id"], f"conflict.conflicting_evidence[{i}].source_id"


def registered_source_ids(profile: dict[str, Any]) -> set[str]:
    return {s["source_id"] for s in profile.get("sources", []) or []}


def check_referential_integrity(profile: dict[str, Any]) -> list[BusinessError]:
    """Every ``source_id`` referenced anywhere must be a registered source (D-016)."""
    errors: list[BusinessError] = []
    known = registered_source_ids(profile)

    def _check(source_id: str, where: str, feature_id: str | None = None) -> None:
        if source_id not in known:
            errors.append(
                BusinessError(
                    code="VALIDATION_UNKNOWN_SOURCE_REF",
                    message=f"Reference to unregistered source_id {source_id!r} at {where}",
                    feature_id=feature_id,
                    path=where,
                )
            )

    for fr in profile.get("feature_results", []) or []:
        fid = fr.get("feature_id")
        for source_id, sub in _iter_evidence_source_ids(fr):
            _check(source_id, f"feature_results[{fid}].{sub}", fid)

    for i, fact in enumerate(profile.get("additional_facts", []) or []):
        for j, ev in enumerate(fact.get("evidence", []) or []):
            _check(ev["source_id"], f"additional_facts[{i}].evidence[{j}].source_id")

    for i, uc in enumerate(profile.get("use_cases", []) or []):
        for j, ev in enumerate(uc.get("evidence", []) or []):
            _check(ev["source_id"], f"use_cases[{i}].evidence[{j}].source_id")

    for i, rel in enumerate(profile.get("release_history", []) or []):
        for j, ev in enumerate(rel.get("evidence", []) or []):
            _check(ev["source_id"], f"release_history[{i}].evidence[{j}].source_id")

    for i, issue in enumerate(profile.get("unresolved_issues", []) or []):
        for sid in issue.get("related_source_ids", []) or []:
            _check(sid, f"unresolved_issues[{i}].related_source_ids")

    return errors


def _nonempty(text: Any) -> bool:
    return isinstance(text, str) and text.strip() != ""


def validate_feature_result(
    fr: dict[str, Any], sources_by_id: dict[str, dict[str, Any]] | None = None
) -> list[BusinessError]:
    """Enforce status-dependent D-009 rules on one feature result.

    JSON Schema guarantees the shape; this enforces the semantics D-009 and
    requirements Sec 9-12 require and that a schema cannot express:

    - ``has``/``partial`` need at least one non-empty evidence excerpt, backed
      by at least one *official* source (D-017: statuses rest only on official
      sources; requirements Sec 10);
    - ``not_found`` is only legal after a *complete* protocol: all relevant
      source classes checked, ``protocol_complete: true``, no access gaps, no
      unresolved conflict, and no positive evidence. Anything short of that is
      ``uncertain``, never ``not_found`` (D-009);
    - ``uncertain`` must be justified by a conflict, an access gap, or an
      explicitly incomplete protocol - it is not a silent default.
    """
    errors: list[BusinessError] = []
    fid = fr.get("feature_id")
    status = fr.get("status")
    evidence = fr.get("evidence", []) or []
    trace = fr.get("search_trace", {}) or {}
    access_gaps = trace.get("access_gaps", []) or []
    classes_checked = set(trace.get("source_classes_checked", []) or [])
    has_conflict = bool(fr.get("conflict"))

    def err(code: str, message: str) -> None:
        errors.append(BusinessError(code=code, message=message, feature_id=fid))

    if status in ("has", "partial"):
        if not evidence or not any(_nonempty(e.get("excerpt")) for e in evidence):
            err(
                "VALIDATION_EVIDENCE_REQUIRED",
                f"status {status!r} requires at least one non-empty evidence excerpt",
            )
        if sources_by_id is not None and evidence:
            referenced_official = any(
                sources_by_id.get(e.get("source_id"), {}).get("official") is True
                for e in evidence
            )
            if not referenced_official:
                err(
                    "VALIDATION_NO_OFFICIAL_SOURCE",
                    f"status {status!r} must cite at least one official source (D-017)",
                )

    elif status == "not_found":
        if trace.get("protocol_complete") is not True:
            err(
                "VALIDATION_PROTOCOL_INCOMPLETE",
                "not_found requires search_trace.protocol_complete=true; "
                "otherwise the status must be uncertain (D-009)",
            )
        missing = [c for c in D009_RELEVANT_SOURCE_CLASSES if c not in classes_checked]
        if missing:
            err(
                "VALIDATION_D009_SOURCE_CLASS_MISSING",
                f"not_found requires all relevant source classes checked; missing {missing}",
            )
        if access_gaps:
            err(
                "VALIDATION_D009_ACCESS_GAP",
                "not_found is not allowed when access gaps remain; use uncertain (D-009)",
            )
        if has_conflict:
            err(
                "VALIDATION_D009_UNRESOLVED_CONFLICT",
                "not_found is not allowed with an unresolved conflict; use uncertain (D-009)",
            )
        if evidence:
            err(
                "VALIDATION_NOT_FOUND_HAS_EVIDENCE",
                "not_found must not carry positive evidence; the trace is the evidence (D-009)",
            )

    elif status == "uncertain":
        justified = has_conflict or bool(access_gaps) or trace.get("protocol_complete") is False
        if not justified:
            err(
                "VALIDATION_UNCERTAIN_UNJUSTIFIED",
                "uncertain must be justified by a conflict, an access gap, or an "
                "incomplete protocol (D-009)",
            )

    return errors


def validate_feature_results(profile: dict[str, Any]) -> list[BusinessError]:
    """Run per-record D-009 rules across every feature result in a profile."""
    sources_by_id = {s["source_id"]: s for s in profile.get("sources", []) or []}
    errors: list[BusinessError] = []
    for fr in profile.get("feature_results", []) or []:
        errors.extend(validate_feature_result(fr, sources_by_id))
    return errors


def check_profile_content(profile: dict[str, Any]) -> list[BusinessError]:
    """Content-completeness rules for a publishable profile (criterion 14).

    A publishable profile must carry at least one additional fact and at least
    one use case of *each* kind - documented and inferred (requirements Sec 14;
    Stage-1 criterion 14).
    """
    errors: list[BusinessError] = []
    if not (profile.get("additional_facts") or []):
        errors.append(
            BusinessError(
                code="VALIDATION_NO_ADDITIONAL_FACTS",
                message="a publishable profile must contain at least one additional fact",
            )
        )
    kinds = {uc.get("kind") for uc in profile.get("use_cases", []) or []}
    for required_kind in ("documented", "inferred"):
        if required_kind not in kinds:
            errors.append(
                BusinessError(
                    code="VALIDATION_MISSING_USE_CASE_KIND",
                    message=f"a publishable profile must contain a {required_kind!r} use case",
                )
            )
    return errors


def check_use_case_supporting_features(profile: dict[str, Any]) -> list[BusinessError]:
    """Inferred use cases must reference feature_ids that exist in the profile."""
    errors: list[BusinessError] = []
    known_features = {fr.get("feature_id") for fr in profile.get("feature_results", []) or []}
    for i, uc in enumerate(profile.get("use_cases", []) or []):
        for fid in uc.get("supporting_features", []) or []:
            if fid not in known_features:
                errors.append(
                    BusinessError(
                        code="VALIDATION_UNKNOWN_FEATURE_REF",
                        message=(
                            f"use_cases[{i}] references unknown supporting feature {fid!r}"
                        ),
                        path=f"use_cases[{i}].supporting_features",
                    )
                )
    return errors
