"""Shared pytest fixtures and builders for the tool_eval test suite.

Everything here is deterministic and offline: no model API, no network. Worker
/ LLM-dependent inputs are represented as fixture dicts, per the Increment 2
testing requirement.
"""

from __future__ import annotations

import copy
import shutil
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """A throwaway project root: real config/ copied in, plus a pyproject marker.

    Lets run-lifecycle and research code run against an isolated .work/ tree
    without touching the developer's real runs (determinism + isolation).
    """
    shutil.copytree(_REPO_ROOT / "config", tmp_path / "config")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='t'\n", encoding="utf-8")
    from tool_eval.paths import ensure_runtime_dirs

    ensure_runtime_dirs(tmp_path)
    return tmp_path


def _source(source_id: str, **overrides: Any) -> dict[str, Any]:
    base = {
        "source_id": source_id,
        "url": f"https://docs.example.com/{source_id}",
        "title": f"Doc {source_id}",
        "source_type": "documentation",
        "checked_at": "2026-07-20",
        "available": True,
        "official": True,
    }
    base.update(overrides)
    return base


def _feature_result(feature_id: str, status: str = "has", **overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "feature_id": feature_id,
        "status": status,
        "rationale": f"Rationale for {feature_id}.",
        "search_trace": {
            "protocol_complete": True,
            "queries": [f"{feature_id} docs"],
            "source_classes_checked": ["documentation", "product_page", "changelog", "pricing"],
        },
    }
    if status in ("has", "partial"):
        base["evidence"] = [{"source_id": "src_docs", "excerpt": "It supports this."}]
    if status == "uncertain":
        base["conflict"] = {
            "reason": "Sources disagree.",
            "conflicting_evidence": [
                {"source_id": "src_docs", "excerpt": "Yes."},
                {"source_id": "src_changelog", "excerpt": "Removed."},
            ],
        }
    base.update(overrides)
    return base


@pytest.fixture
def make_source():
    return _source


@pytest.fixture
def make_feature_result():
    return _feature_result


@pytest.fixture
def valid_profile() -> dict[str, Any]:
    return copy.deepcopy(_VALID_PROFILE)


_VALID_PROFILE: dict[str, Any] = {
    "schema_version": "1.0.0",
    "tool": {"tool_id": "example_tool", "name": "Example Tool", "vendor": "Example Inc"},
    "research": {
        "run_id": "research-20260720-000000-abcd1234",
        "researched_at": "2026-07-20T00:00:00Z",
        "taxonomy_revision": 1,
        "template_revision": 1,
        "source_policy_revision": 1,
        "profile_state": "current",
    },
    "sources": [
        _source("src_docs"),
        _source("src_changelog", source_type="changelog"),
    ],
    "feature_results": [
        _feature_result("inline_code_completion", "has"),
        _feature_result("standalone_cli", "not_found", evidence=None),
    ],
    "additional_facts": [
        {
            "fact_id": "pricing_note",
            "topic": "Pricing",
            "description": "Free tier available.",
            "evidence": [{"source_id": "src_docs", "excerpt": "Free tier."}],
        }
    ],
    "use_cases": [
        {
            "use_case_id": "onboarding",
            "title": "Onboarding new devs",
            "description": "Helps new developers.",
            "kind": "documented",
            "evidence": [{"source_id": "src_docs", "excerpt": "For onboarding."}],
        },
        {
            "use_case_id": "refactor_flow",
            "title": "Refactoring at scale",
            "description": "Infer from completion capability.",
            "kind": "inferred",
            "rationale": "Because inline completion is present.",
            "supporting_features": ["inline_code_completion"],
        },
    ],
    "unresolved_issues": [],
}


# `not_found` results carry no evidence key; strip the None the builder leaves.
for _fr in _VALID_PROFILE["feature_results"]:
    if _fr.get("evidence") is None:
        _fr.pop("evidence", None)
