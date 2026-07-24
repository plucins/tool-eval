"""Item 6: deterministic merge + completeness across all features (D-010)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tool_eval.research.merge import merge_results, verify_completeness
from tool_eval.research.tasks import create_feature_tasks
from tool_eval.research.pipeline import merge_run, taxonomy_feature_ids
from tool_eval.runs.manager import init_run, read_run


def _src(sid="src_docs", **kw):
    base = {
        "source_id": sid,
        "url": f"https://docs.example.com/{sid}",
        "title": "Doc",
        "source_type": "documentation",
        "checked_at": "2026-07-20",
        "available": True,
        "official": True,
    }
    base.update(kw)
    return base


def _fr(fid, status="has"):
    fr = {
        "feature_id": fid,
        "status": status,
        "rationale": "r",
        "search_trace": {
            "protocol_complete": True,
            "queries": ["q"],
            "source_classes_checked": ["documentation", "product_page", "changelog", "pricing"],
        },
    }
    if status in ("has", "partial"):
        fr["evidence"] = [{"source_id": "src_docs", "excerpt": "yes"}]
    return fr


def _worker(task_id, feature_ids, sources=None, candidates=None):
    return {
        "task_id": task_id,
        "run_id": "research-20260720-000000-abcd1234",
        "task_type": "feature-research",
        "sources": sources or [_src()],
        "feature_results": [_fr(f) for f in feature_ids],
        "candidates": candidates or [],
    }


# --- pure merge ------------------------------------------------------------


def test_merge_is_deterministic_and_dedups_sources():
    w1 = _worker("t1", ["a", "b"], sources=[_src("src_docs")])
    w2 = _worker("t2", ["c"], sources=[_src("src_docs"), _src("src_cl", source_type="changelog")])
    m1, e1 = merge_results([w1, w2])
    m2, e2 = merge_results([w2, w1])
    assert e1 == [] and e2 == []
    assert m1 == m2  # order-independent
    assert [s["source_id"] for s in m1["sources"]] == ["src_cl", "src_docs"]
    assert [f["feature_id"] for f in m1["feature_results"]] == ["a", "b", "c"]


def test_merge_flags_inconsistent_source_definition():
    w1 = _worker("t1", ["a"], sources=[_src("src_docs", title="A")])
    w2 = _worker("t2", ["b"], sources=[_src("src_docs", title="B")])
    _, errors = merge_results([w1, w2])
    assert any(e.code == "VALIDATION_SOURCE_CONFLICT" for e in errors)


def test_merge_flags_duplicate_feature_result():
    w1 = _worker("t1", ["a"])
    w2 = _worker("t2", ["a"])
    _, errors = merge_results([w1, w2])
    assert any(e.code == "VALIDATION_DUPLICATE_FEATURE_RESULT" for e in errors)


# --- completeness ----------------------------------------------------------


def test_completeness_passes_when_all_present():
    frs = [_fr("a"), _fr("b")]
    assert verify_completeness(frs, ["a", "b"]) == []


def test_completeness_flags_missing():
    errors = verify_completeness([_fr("a")], ["a", "b"])
    assert [e.code for e in errors] == ["VALIDATION_FEATURE_RESULT_MISSING"]
    assert errors[0].feature_id == "b"


def test_completeness_flags_foreign_feature():
    errors = verify_completeness([_fr("a"), _fr("x")], ["a"])
    assert any(e.code == "VALIDATION_FOREIGN_FEATURE_RESULT" for e in errors)


# --- integration through the run directory ---------------------------------


def _write_results(temp_project: Path, run_id: str):
    """Fill every task's result.json with fixture worker output for all features."""
    run_dir = temp_project / ".work" / "runs" / run_id
    for task_dir in sorted((run_dir / "tasks").iterdir()):
        manifest = json.loads((task_dir / "task.json").read_text())
        result = _worker(manifest["task_id"], manifest["feature_ids"])
        (task_dir / "result.json").write_text(json.dumps(result), encoding="utf-8")


def test_merge_run_completes_over_full_taxonomy(temp_project: Path):
    run = init_run(temp_project, operation="research")
    create_feature_tasks(temp_project, run.run_id)
    _write_results(temp_project, run.run_id)

    summary = merge_run(temp_project, run.run_id)
    assert summary["complete"] is True
    assert summary["merged_feature_count"] == len(taxonomy_feature_ids(temp_project))
    assert read_run(temp_project, run.run_id).state == "merged"

    merged_dir = temp_project / ".work" / "runs" / run.run_id / "merged"
    frs = json.loads((merged_dir / "feature-results.json").read_text())
    assert len(frs) == len(taxonomy_feature_ids(temp_project))


def test_merge_run_blocks_on_missing_result(temp_project: Path):
    from tool_eval.errors import ToolEvalError

    run = init_run(temp_project, operation="research")
    create_feature_tasks(temp_project, run.run_id)
    # deliberately do not write any result.json
    with pytest.raises(ToolEvalError) as exc:
        merge_run(temp_project, run.run_id)
    assert exc.value.code == "RESEARCH_MERGE_BLOCKED"
