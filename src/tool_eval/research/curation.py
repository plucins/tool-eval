"""Single curation gate, waiting room, and controlled taxonomy revisions.

The run detects new-feature candidates and presents them all at *one*
interactive curation point (D-018; requirements Sec 8/16). The operator's
decision for each candidate is accept / reject / defer, and Python enforces
that *every* candidate is resolved before the run may proceed.

Effects of each decision:

- **accept** -> the full taxonomy entry (authored by the curator/LLM) is added
  to ``config/feature-taxonomy.yaml`` and the taxonomy ``revision`` is
  incremented. This is a *controlled* revision transition recorded in the run
  (D-011): it updates the run's effective revision/hash and is NOT treated as
  an external change that would block resume. Other tools' profiles are marked
  ``requires_research``. The accepted feature must be researched for the
  current tool before publication (enforced later by the completeness gate).
- **defer** -> the candidate is stored in the waiting room for a future run.
- **reject** -> the candidate is recorded so it is not re-proposed blindly.

WAITING-ROOM PERSISTENCE (open design question, flagged to the operator):
plan Sec 3.3 defines ``data/feature-candidates/{pending.json,rejected.json}``
but does not say whether ``pending.json`` *is* the waiting room. This module
implements the recommended interpretation: ``pending.json`` is the persistent
waiting room (deferred candidates accumulate there across runs) and
``rejected.json`` is the persistent rejected-candidate log. Accepted candidates
are NOT stored here - they are promoted into the taxonomy. If the operator
confirms a different model, only :func:`_append_waiting_room` /
:func:`_append_rejected` need to change.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from tool_eval.errors import ErrorFamily, ToolEvalError
from tool_eval.runs.manager import RunRecord, TransitionRecord, read_run, save_run
from tool_eval.validation import schema

_REQUIRED_TAXONOMY_FIELDS = (
    "feature_id",
    "name",
    "group",
    "definition",
    "has_criteria",
    "partial_criteria",
    "exclusions",
    "aliases",
    "research_question",
)


def _candidates_dir(root: Path) -> Path:
    d = root / "data" / "feature-candidates"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _load_json_list(path: Path, key: str) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get(key, []) if isinstance(data, dict) else []


def _append_waiting_room(root: Path, candidate: dict[str, Any]) -> None:
    path = _candidates_dir(root) / "pending.json"
    items = _load_json_list(path, "candidates")
    if not any(c.get("candidate_id") == candidate["candidate_id"] for c in items):
        items.append(candidate)
    path.write_text(json.dumps({"candidates": items}, indent=2), encoding="utf-8")


def _append_rejected(root: Path, candidate: dict[str, Any]) -> None:
    path = _candidates_dir(root) / "rejected.json"
    items = _load_json_list(path, "candidates")
    if not any(c.get("candidate_id") == candidate["candidate_id"] for c in items):
        items.append(candidate)
    path.write_text(json.dumps({"candidates": items}, indent=2), encoding="utf-8")


def _taxonomy_path(root: Path) -> Path:
    return root / "config" / "feature-taxonomy.yaml"


def mark_other_profiles_requires_research(root: Path) -> list[str]:
    """Set profile_state=requires_research on every active profile (Sec 7/8)."""
    profiles_dir = root / "data" / "profiles"
    marked: list[str] = []
    if not profiles_dir.is_dir():
        return marked
    for child in sorted(profiles_dir.iterdir()):
        profile_json = child / "profile.json"
        if child.name.startswith(".") or not profile_json.is_file():
            continue
        data = json.loads(profile_json.read_text(encoding="utf-8"))
        if data.get("research", {}).get("profile_state") != "requires_research":
            data.setdefault("research", {})["profile_state"] = "requires_research"
            profile_json.write_text(json.dumps(data, indent=2), encoding="utf-8")
            marked.append(child.name)
    return marked


def accept_feature_into_taxonomy(root: Path, feature: dict[str, Any]) -> int:
    """Append ``feature`` to the taxonomy and bump its revision. Returns new revision."""
    missing = [f for f in _REQUIRED_TAXONOMY_FIELDS if f not in feature]
    if missing:
        raise ToolEvalError(
            code=f"{ErrorFamily.INPUT}_INCOMPLETE_FEATURE_DEFINITION",
            message=(
                "accepting a candidate requires a complete taxonomy entry; "
                f"missing fields: {missing}"
            ),
        )

    path = _taxonomy_path(root)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    existing_ids = {f["feature_id"] for f in data.get("features", [])}
    if feature["feature_id"] in existing_ids:
        raise ToolEvalError(
            code=f"{ErrorFamily.INPUT}_DUPLICATE_FEATURE_ID",
            message=f"feature_id {feature['feature_id']!r} already in the taxonomy",
        )
    valid_groups = {g["id"] for g in data.get("groups", [])}
    if feature["group"] not in valid_groups:
        raise ToolEvalError(
            code=f"{ErrorFamily.INPUT}_UNKNOWN_GROUP",
            message=f"group {feature['group']!r} is not a taxonomy group",
        )

    data["features"].append(feature)
    data["revision"] = int(data.get("revision", 1)) + 1
    path.write_text(
        "# Feature taxonomy - Python-managed after curation edits (D-016).\n"
        + yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return data["revision"]


def _record_controlled_revision(record: RunRecord, root: Path, new_revision: int) -> None:
    """Record a controlled taxonomy revision transition on the run (D-011)."""
    record.effective_revisions["feature-taxonomy.yaml"] = new_revision
    path = _taxonomy_path(root)
    record.config_hashes["feature-taxonomy.yaml"] = hashlib.sha256(
        path.read_bytes()
    ).hexdigest()
    record.transitions.append(
        TransitionRecord(
            state=record.state,
            at=record.updated_at,
            detail=f"controlled taxonomy revision -> {new_revision} (curation accept)",
        ).__dict__
    )


def curate_candidates(
    root: Path, run_id: str, decisions: list[dict[str, Any]]
) -> dict[str, Any]:
    """Apply the operator's decisions to the run's candidate set (single gate).

    ``decisions`` is a list of ``{candidate_id, decision, feature?, note?}``.
    An ``accept`` decision must carry a complete ``feature`` taxonomy entry.
    Every candidate detected in the run must have exactly one decision.
    """
    run_dir = root / ".work" / "runs" / run_id
    candidates_path = run_dir / "merged" / "candidates.json"
    if not candidates_path.is_file():
        raise ToolEvalError(
            code=f"{ErrorFamily.INPUT}_NO_CANDIDATES",
            message="no merged/candidates.json; run merge before curation",
            path=str(candidates_path),
        )

    candidates = _load_json_list(candidates_path, "candidates")
    by_id = {c["candidate_id"]: c for c in candidates}
    decided_ids = [d["candidate_id"] for d in decisions]

    # Gate: exactly one decision per candidate, no unknown ids.
    undecided = sorted(set(by_id) - set(decided_ids))
    unknown = sorted(set(decided_ids) - set(by_id))
    duplicates = sorted({cid for cid in decided_ids if decided_ids.count(cid) > 1})
    if undecided or unknown or duplicates:
        raise ToolEvalError(
            code=f"{ErrorFamily.VALIDATION}_CANDIDATES_UNRESOLVED",
            message=(
                "every candidate needs exactly one decision "
                f"(undecided={undecided}, unknown={unknown}, duplicate={duplicates})"
            ),
        )

    record = read_run(root, run_id)
    accepted: list[str] = []
    deferred: list[str] = []
    rejected: list[str] = []
    new_revision = record.effective_revisions.get("feature-taxonomy.yaml")
    marked_profiles: list[str] = []

    for decision in decisions:
        cid = decision["candidate_id"]
        choice = decision["decision"]
        candidate = by_id[cid]
        if choice == "accept":
            new_revision = accept_feature_into_taxonomy(root, decision["feature"])
            _record_controlled_revision(record, root, new_revision)
            marked_profiles = sorted(set(marked_profiles) | set(mark_other_profiles_requires_research(root)))
            accepted.append(cid)
        elif choice == "defer":
            _append_waiting_room(root, candidate)
            deferred.append(cid)
        elif choice == "reject":
            _append_rejected(root, candidate)
            rejected.append(cid)
        else:
            raise ToolEvalError(
                code=f"{ErrorFamily.INPUT}_BAD_DECISION",
                message=f"unknown curation decision {choice!r} for {cid!r}",
            )

    # Persist decisions back onto the candidate set (schema-validated).
    curated = {"candidates": candidates, "decisions": [
        {k: v for k, v in d.items() if k in ("candidate_id", "decision", "decided_at", "note")}
        for d in decisions
    ]}
    schema_errors = schema.validate("candidates", curated)
    if schema_errors:
        raise ToolEvalError(
            code=f"{ErrorFamily.VALIDATION}_CANDIDATES_INVALID",
            message=f"curated candidate set failed schema: {schema_errors[0].message}",
        )
    candidates_path.write_text(json.dumps(curated, indent=2), encoding="utf-8")
    save_run(root, record)

    return {
        "run_id": run_id,
        "accepted": accepted,
        "deferred": deferred,
        "rejected": rejected,
        "taxonomy_revision": new_revision,
        "profiles_marked_requires_research": marked_profiles,
    }
