"""Item 5: candidates, single curation gate, waiting room, controlled revisions.

NOTE: the waiting-room persistence model (pending.json == waiting room) is the
recommended interpretation pending operator confirmation of the design gap;
these tests pin the recommended behaviour so it is easy to re-point if changed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import yaml

from tool_eval.errors import ToolEvalError
from tool_eval.research.curation import (
    accept_feature_into_taxonomy,
    curate_candidates,
    mark_other_profiles_requires_research,
)
from tool_eval.runs.manager import init_run, read_run


def _candidate(cid, group="code_authoring"):
    return {
        "candidate_id": cid,
        "name": cid.title(),
        "group": group,
        "definition": "some capability",
        "relevance_suggestion": "seems relevant",
    }


def _full_feature(fid, group="code_authoring"):
    return {
        "feature_id": fid,
        "name": "New Feature",
        "group": group,
        "definition": "A new capability.",
        "has_criteria": "criteria",
        "partial_criteria": "partial",
        "exclusions": "none",
        "aliases": ["x"],
        "research_question": "does it?",
    }


def _write_candidates(temp_project: Path, run_id: str, candidates):
    merged = temp_project / ".work" / "runs" / run_id / "merged"
    merged.mkdir(parents=True, exist_ok=True)
    (merged / "candidates.json").write_text(
        json.dumps({"candidates": candidates}), encoding="utf-8"
    )


# --- the single gate: every candidate must be resolved --------------------


def test_all_candidates_must_be_decided(temp_project: Path):
    run = init_run(temp_project, operation="research")
    _write_candidates(temp_project, run.run_id, [_candidate("c1"), _candidate("c2")])
    with pytest.raises(ToolEvalError) as exc:
        curate_candidates(temp_project, run.run_id, [{"candidate_id": "c1", "decision": "reject"}])
    assert exc.value.code == "VALIDATION_CANDIDATES_UNRESOLVED"


def test_unknown_candidate_id_rejected(temp_project: Path):
    run = init_run(temp_project, operation="research")
    _write_candidates(temp_project, run.run_id, [_candidate("c1")])
    with pytest.raises(ToolEvalError) as exc:
        curate_candidates(
            temp_project,
            run.run_id,
            [
                {"candidate_id": "c1", "decision": "reject"},
                {"candidate_id": "ghost", "decision": "reject"},
            ],
        )
    assert exc.value.code == "VALIDATION_CANDIDATES_UNRESOLVED"


# --- defer -> waiting room, reject -> rejected log -------------------------


def test_defer_goes_to_waiting_room(temp_project: Path):
    run = init_run(temp_project, operation="research")
    _write_candidates(temp_project, run.run_id, [_candidate("c1")])
    summary = curate_candidates(
        temp_project, run.run_id, [{"candidate_id": "c1", "decision": "defer"}]
    )
    assert summary["deferred"] == ["c1"]
    pending = json.loads(
        (temp_project / "data" / "feature-candidates" / "pending.json").read_text()
    )
    assert pending["candidates"][0]["candidate_id"] == "c1"


def test_reject_goes_to_rejected_log(temp_project: Path):
    run = init_run(temp_project, operation="research")
    _write_candidates(temp_project, run.run_id, [_candidate("c1")])
    summary = curate_candidates(
        temp_project, run.run_id, [{"candidate_id": "c1", "decision": "reject"}]
    )
    assert summary["rejected"] == ["c1"]
    rejected = json.loads(
        (temp_project / "data" / "feature-candidates" / "rejected.json").read_text()
    )
    assert rejected["candidates"][0]["candidate_id"] == "c1"


# --- accept -> controlled taxonomy revision + requires_research ------------


def test_accept_bumps_taxonomy_revision_and_is_controlled(temp_project: Path):
    run = init_run(temp_project, operation="research")
    before = read_run(temp_project, run.run_id).effective_revisions["feature-taxonomy.yaml"]
    _write_candidates(temp_project, run.run_id, [_candidate("new_cap")])

    summary = curate_candidates(
        temp_project,
        run.run_id,
        [{"candidate_id": "new_cap", "decision": "accept", "feature": _full_feature("new_cap")}],
    )
    assert summary["accepted"] == ["new_cap"]
    assert summary["taxonomy_revision"] == before + 1

    # taxonomy file updated on disk
    tax = yaml.safe_load((temp_project / "config" / "feature-taxonomy.yaml").read_text())
    assert tax["revision"] == before + 1
    assert any(f["feature_id"] == "new_cap" for f in tax["features"])

    # run records the controlled revision so resume is NOT invalidated
    reloaded = read_run(temp_project, run.run_id)
    assert reloaded.effective_revisions["feature-taxonomy.yaml"] == before + 1
    from tool_eval.runs.manager import resume_check

    assert resume_check(temp_project, run.run_id)["resumable"] is True


def test_accept_requires_complete_feature_definition(temp_project: Path):
    run = init_run(temp_project, operation="research")
    _write_candidates(temp_project, run.run_id, [_candidate("c1")])
    incomplete = {"feature_id": "c1", "name": "x", "group": "code_authoring"}
    with pytest.raises(ToolEvalError) as exc:
        curate_candidates(
            temp_project,
            run.run_id,
            [{"candidate_id": "c1", "decision": "accept", "feature": incomplete}],
        )
    assert exc.value.code == "INPUT_INCOMPLETE_FEATURE_DEFINITION"


def test_accept_marks_other_profiles_requires_research(temp_project: Path, valid_profile):
    # publish an active profile first
    from tool_eval.profiles.publication import publish_profile

    run0 = init_run(temp_project, operation="research")
    staging = temp_project / ".work" / "runs" / run0.run_id / "publish"
    staging.mkdir(parents=True, exist_ok=True)
    (staging / "profile.json").write_text(json.dumps(valid_profile), encoding="utf-8")
    (staging / "description.md").write_text("# d\n\n## Characteristics\n\nx\n", encoding="utf-8")
    publish_profile(temp_project, run0.run_id, "example_tool")

    run = init_run(temp_project, operation="research")
    _write_candidates(temp_project, run.run_id, [_candidate("new_cap2")])
    summary = curate_candidates(
        temp_project,
        run.run_id,
        [{"candidate_id": "new_cap2", "decision": "accept", "feature": _full_feature("new_cap2")}],
    )
    assert "example_tool" in summary["profiles_marked_requires_research"]
    active = json.loads(
        (temp_project / "data" / "profiles" / "example_tool" / "profile.json").read_text()
    )
    assert active["research"]["profile_state"] == "requires_research"


def test_accept_rejects_unknown_group(temp_project: Path):
    with pytest.raises(ToolEvalError) as exc:
        accept_feature_into_taxonomy(temp_project, _full_feature("z", group="not_a_group"))
    assert exc.value.code == "INPUT_UNKNOWN_GROUP"


def test_mixed_decisions_all_applied(temp_project: Path):
    run = init_run(temp_project, operation="research")
    _write_candidates(
        temp_project, run.run_id, [_candidate("a"), _candidate("b"), _candidate("c")]
    )
    summary = curate_candidates(
        temp_project,
        run.run_id,
        [
            {"candidate_id": "a", "decision": "accept", "feature": _full_feature("a")},
            {"candidate_id": "b", "decision": "defer"},
            {"candidate_id": "c", "decision": "reject"},
        ],
    )
    assert summary["accepted"] == ["a"]
    assert summary["deferred"] == ["b"]
    assert summary["rejected"] == ["c"]
