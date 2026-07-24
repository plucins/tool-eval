"""Canonical CLI: `python -m tool_eval <command>`.

Every command prints exactly one JSON envelope to stdout:
{"status", "code", "run_id", "next_action", "artifacts", "errors"}
Diagnostics and progress go to stderr via `logging`, never stdout, so agents
parsing stdout never have to separate log noise from the result (Sec 3.5).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Callable

from tool_eval.comparison.builder import build_comparison
from tool_eval.config import load_config_bundle
from tool_eval.errors import ToolEvalError
from tool_eval.paths import discover_project_root, ensure_runtime_dirs
from tool_eval.profiles.publication import list_profiles, publish_profile, recover
from tool_eval.profiles.validate import validate_profile
from tool_eval.profiles.build import build_profile
from tool_eval.research.pipeline import merge_run, taxonomy_feature_ids
from tool_eval.research.curation import curate_candidates
from tool_eval.research.repair import prepare_repair
from tool_eval.research.sources import accept_sources, create_source_task
from tool_eval.research.task_validation import validate_task
from tool_eval.research.tasks import create_feature_tasks
from tool_eval.runs.manager import fail_run, init_run, resume_check, run_status
from tool_eval.runs.retention import cleanup_failed_runs

logger = logging.getLogger("tool_eval")


def _envelope(
    status: str,
    code: str,
    run_id: str | None = None,
    next_action: str | None = None,
    artifacts: list[str] | None = None,
    errors: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "code": code,
        "run_id": run_id,
        "next_action": next_action,
        "artifacts": artifacts or [],
        "errors": errors or [],
    }


def _not_implemented(command: str) -> dict[str, Any]:
    return _envelope(
        status="error",
        code="INPUT_NOT_IMPLEMENTED",
        next_action=f"'{command}' is defined for a later increment and is not implemented yet.",
    )


# --- config ------------------------------------------------------------


def cmd_config_validate(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_project_root()
    bundle = load_config_bundle(root)
    return _envelope(
        status="ok",
        code="CONFIG_VALID",
        next_action="Configuration is valid; safe to run `run init`.",
        artifacts=[str(cf.path) for cf in bundle.files.values()],
    )


# --- run -----------------------------------------------------------------


def cmd_run_init(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_project_root()
    ensure_runtime_dirs(root)
    record = init_run(root, operation=args.operation)
    return _envelope(
        status="ok",
        code="RUN_INITIALIZED",
        run_id=record.run_id,
        next_action="Proceed with the next phase for this operation.",
        artifacts=[str(root / ".work" / "runs" / record.run_id / "run.json")],
    )


def cmd_run_status(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_project_root()
    status = run_status(root, args.run_id)
    return _envelope(
        status="ok",
        code="RUN_STATUS",
        run_id=args.run_id,
        next_action=None,
        artifacts=[json.dumps(status)],
    )


def cmd_run_resume_check(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_project_root()
    result = resume_check(root, args.run_id)
    return _envelope(
        status="ok" if result["resumable"] else "error",
        code="RUN_RESUMABLE" if result["resumable"] else "CONFIG_REVISION_MISMATCH",
        run_id=args.run_id,
        next_action=(
            "Resume is safe." if result["resumable"] else "Start a new run instead of resuming."
        ),
        artifacts=[json.dumps(result)],
    )


def cmd_run_fail(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_project_root()
    report = fail_run(root, args.run_id, reason=args.reason)
    return _envelope(
        status="ok",
        code="RUN_FAILED_RECORDED",
        run_id=args.run_id,
        next_action="Run moved to .work/failed-runs/; active profile untouched.",
        artifacts=[json.dumps(report)],
    )


# --- research ------------------------------------------------------------


def cmd_research_create_feature_tasks(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_project_root()
    summary = create_feature_tasks(root, args.run_id, isolate=args.isolate or [])
    return _envelope(
        status="ok",
        code="FEATURE_TASKS_CREATED",
        run_id=args.run_id,
        next_action=(
            f"Delegate {summary['bundle_count']} feature tasks in "
            f"{summary['wave_count']} wave(s) of up to {summary['max_concurrent']} workers."
        ),
        artifacts=[json.dumps(summary)],
    )


def cmd_research_create_source_task(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_project_root()
    summary = create_source_task(root, args.run_id, args.tool_name)
    return _envelope(
        status="ok",
        code="SOURCE_TASK_CREATED",
        run_id=args.run_id,
        next_action=(
            f"Delegate the source-discovery task for {summary['tool_id']!r} to a worker, "
            "then run `research accept-sources`."
        ),
        artifacts=[json.dumps(summary)],
    )


def cmd_research_accept_sources(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_project_root()
    summary = accept_sources(root, args.run_id)
    return _envelope(
        status="ok",
        code="SOURCES_ACCEPTED",
        run_id=args.run_id,
        next_action=(
            f"Registry accepted with {summary['source_count']} source(s), "
            f"{summary['official_count']} official; feature research is unblocked."
        ),
        artifacts=[json.dumps(summary)],
    )


def cmd_research_validate_task(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_project_root()
    report = validate_task(root, args.run_id, args.task_id)
    valid = report["valid"]
    return _envelope(
        status="ok" if valid else "error",
        code="TASK_VALID" if valid else "VALIDATION_TASK_INVALID",
        run_id=args.run_id,
        next_action=(
            "Task result is valid; include it in the merge."
            if valid
            else f"{len(report['errors'])} error(s); retry/split or repair the task."
        ),
        artifacts=[json.dumps(report)],
        errors=report["errors"] or None,
    )


def cmd_research_build_profile(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_project_root()
    summary = build_profile(
        root,
        args.run_id,
        tool_id=args.tool_id,
        tool_name=args.tool_name,
        content_path=Path(args.content) if args.content else None,
        sections_path=Path(args.sections) if args.sections else None,
    )
    built = summary["built"]
    return _envelope(
        status="ok" if built else "error",
        code="PROFILE_BUILT" if built else "VALIDATION_PROFILE_INVALID",
        run_id=args.run_id,
        next_action=(
            "Staged profile.json + description.md are valid; run `profile publish`."
            if built
            else f"{len(summary['errors'])} validation error(s); repair before publishing."
        ),
        artifacts=summary.get("artifacts", []) or [json.dumps(summary)],
        errors=summary["errors"] or None,
    )


def cmd_research_merge(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_project_root()
    summary = merge_run(root, args.run_id)
    complete = summary["complete"]
    return _envelope(
        status="ok" if complete else "error",
        code="MERGE_COMPLETE" if complete else "VALIDATION_INCOMPLETE_MERGE",
        run_id=args.run_id,
        next_action=(
            "All features have exactly one result; proceed to candidate curation."
            if complete
            else "Merge has gaps/duplicates; repair the flagged features and re-merge."
        ),
        artifacts=[json.dumps(summary)],
        errors=summary["errors"] or None,
    )


def cmd_research_curate_candidates(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_project_root()
    decisions = json.loads(Path(args.decisions_file).read_text(encoding="utf-8"))
    summary = curate_candidates(root, args.run_id, decisions)
    return _envelope(
        status="ok",
        code="CANDIDATES_CURATED",
        run_id=args.run_id,
        next_action=(
            f"Accepted {len(summary['accepted'])}, deferred {len(summary['deferred'])}, "
            f"rejected {len(summary['rejected'])}. "
            + (
                f"Taxonomy now at revision {summary['taxonomy_revision']}; research accepted "
                "feature(s) for the current tool before publishing."
                if summary["accepted"]
                else "No taxonomy change."
            )
        ),
        artifacts=[json.dumps(summary)],
    )


def cmd_research_prepare_repair(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_project_root()
    summary = prepare_repair(root, args.run_id, args.feature_id or [])
    return _envelope(
        status="ok",
        code="REPAIR_ROUND_OPENED",
        run_id=args.run_id,
        next_action=(
            f"Repair round {summary['round']}/{summary['max_rounds']}: re-research "
            f"{len(summary['feature_ids'])} feature(s), then re-validate the whole profile."
        ),
        artifacts=[json.dumps(summary)],
    )


# --- profile -------------------------------------------------------------


def cmd_profile_validate(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_project_root()
    profile = json.loads(Path(args.profile_path).read_text(encoding="utf-8"))
    tax = taxonomy_feature_ids(root) if args.check_completeness else None
    errors = validate_profile(profile, taxonomy_feature_ids=tax)
    return _envelope(
        status="ok" if not errors else "error",
        code="PROFILE_VALID" if not errors else "VALIDATION_PROFILE_INVALID",
        next_action=(
            "Profile is valid and publishable."
            if not errors
            else f"{len(errors)} validation error(s); repair before publishing."
        ),
        errors=errors or None,
    )


def cmd_profile_publish(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_project_root()
    tax = taxonomy_feature_ids(root) if args.check_completeness else None
    result = publish_profile(root, args.run_id, args.tool_id, taxonomy_feature_ids=tax)
    return _envelope(
        status="ok" if result.published else "error",
        code="PROFILE_PUBLISHED" if result.published else "PUBLISH_VALIDATION_FAILED",
        run_id=args.run_id,
        next_action=(
            f"Active profile replaced at {result.target}."
            if result.published
            else "Staged profile failed validation; active profile untouched."
        ),
        artifacts=[result.target],
        errors=result.validation_errors or None,
    )


def cmd_profile_list(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_project_root()
    return _envelope(
        status="ok",
        code="PROFILE_LIST",
        artifacts=[json.dumps(list_profiles(root))],
    )


# --- compare --------------------------------------------------------------


def cmd_compare_build(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_project_root()
    build = build_comparison(root, args.tools, output_name=args.out)
    warnings = [{"code": "INPUT_COMPARE_WARNING", "message": w} for w in build.warnings]
    return _envelope(
        status="ok",
        code="COMPARISON_BUILT",
        next_action=(
            f"Open the self-contained report offline: {build.output_path}."
            + (f" {len(build.warnings)} warning(s) attached." if build.warnings else "")
        ),
        artifacts=[str(build.output_path)],
        errors=warnings or None,
    )


# --- work ----------------------------------------------------------------


def cmd_work_recover(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_project_root()
    actions = recover(root)
    return _envelope(
        status="ok",
        code="RECOVERY_COMPLETE",
        next_action=(
            "No interrupted publications found."
            if not actions
            else f"Recovered {len(actions)} interrupted publication(s)."
        ),
        artifacts=[json.dumps(actions)],
    )


def cmd_work_cleanup(args: argparse.Namespace) -> dict[str, Any]:
    root = discover_project_root()
    summary = cleanup_failed_runs(root)
    return _envelope(
        status="ok",
        code="CLEANUP_COMPLETE",
        next_action=(
            f"Removed {len(summary['removed'])} failed run(s); "
            f"kept {len(summary['kept'])} within retention."
        ),
        artifacts=[json.dumps(summary)],
    )


# --- stub command groups (later increments) ------------------------------


def _stub(name: str) -> Callable[[argparse.Namespace], dict[str, Any]]:
    def handler(_args: argparse.Namespace) -> dict[str, Any]:
        return _not_implemented(name)

    return handler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tool_eval")
    subparsers = parser.add_subparsers(dest="group", required=True)

    config_parser = subparsers.add_parser("config", help="Configuration operations")
    config_sub = config_parser.add_subparsers(dest="action", required=True)
    config_sub.add_parser("validate").set_defaults(handler=cmd_config_validate)

    run_parser = subparsers.add_parser("run", help="Run lifecycle operations")
    run_sub = run_parser.add_subparsers(dest="action", required=True)

    run_init_parser = run_sub.add_parser("init")
    run_init_parser.add_argument("operation", choices=["research", "compare", "resume"])
    run_init_parser.set_defaults(handler=cmd_run_init)

    run_status_parser = run_sub.add_parser("status")
    run_status_parser.add_argument("run_id")
    run_status_parser.set_defaults(handler=cmd_run_status)

    run_resume_check_parser = run_sub.add_parser("resume-check")
    run_resume_check_parser.add_argument("run_id")
    run_resume_check_parser.set_defaults(handler=cmd_run_resume_check)

    run_fail_parser = run_sub.add_parser("fail")
    run_fail_parser.add_argument("run_id")
    run_fail_parser.add_argument("reason")
    run_fail_parser.set_defaults(handler=cmd_run_fail)

    research_parser = subparsers.add_parser("research", help="Research pipeline operations")
    research_sub = research_parser.add_subparsers(dest="action", required=True)

    rc_feature_tasks = research_sub.add_parser("create-feature-tasks")
    rc_feature_tasks.add_argument("run_id")
    rc_feature_tasks.add_argument(
        "--isolate",
        action="append",
        help="Feature id to research as its own single-feature task (repeatable).",
    )
    rc_feature_tasks.set_defaults(handler=cmd_research_create_feature_tasks)

    rc_merge = research_sub.add_parser("merge")
    rc_merge.add_argument("run_id")
    rc_merge.set_defaults(handler=cmd_research_merge)

    rc_repair = research_sub.add_parser("prepare-repair")
    rc_repair.add_argument("run_id")
    rc_repair.add_argument(
        "--feature-id", action="append", help="Feature id needing repair (repeatable)."
    )
    rc_repair.set_defaults(handler=cmd_research_prepare_repair)

    rc_curate = research_sub.add_parser("curate-candidates")
    rc_curate.add_argument("run_id")
    rc_curate.add_argument(
        "decisions_file", help="Path to a JSON list of accept/reject/defer decisions."
    )
    rc_curate.set_defaults(handler=cmd_research_curate_candidates)

    rc_source_task = research_sub.add_parser("create-source-task")
    rc_source_task.add_argument("run_id")
    rc_source_task.add_argument("tool_name", help="Free-text tool name to research.")
    rc_source_task.set_defaults(handler=cmd_research_create_source_task)

    rc_accept_sources = research_sub.add_parser("accept-sources")
    rc_accept_sources.add_argument("run_id")
    rc_accept_sources.set_defaults(handler=cmd_research_accept_sources)

    rc_validate_task = research_sub.add_parser("validate-task")
    rc_validate_task.add_argument("run_id")
    rc_validate_task.add_argument("task_id")
    rc_validate_task.set_defaults(handler=cmd_research_validate_task)

    rc_build_profile = research_sub.add_parser("build-profile")
    rc_build_profile.add_argument("run_id")
    rc_build_profile.add_argument("--tool-id", dest="tool_id")
    rc_build_profile.add_argument("--tool-name", dest="tool_name")
    rc_build_profile.add_argument("--content", help="JSON file of additional_facts/use_cases.")
    rc_build_profile.add_argument("--sections", help="JSON file mapping section id -> Markdown.")
    rc_build_profile.set_defaults(handler=cmd_research_build_profile)

    profile_parser = subparsers.add_parser("profile", help="Profile operations")
    profile_sub = profile_parser.add_subparsers(dest="action", required=True)

    p_validate = profile_sub.add_parser("validate")
    p_validate.add_argument("profile_path")
    p_validate.add_argument("--check-completeness", action="store_true")
    p_validate.set_defaults(handler=cmd_profile_validate)

    p_publish = profile_sub.add_parser("publish")
    p_publish.add_argument("run_id")
    p_publish.add_argument("tool_id")
    p_publish.add_argument("--check-completeness", action="store_true")
    p_publish.set_defaults(handler=cmd_profile_publish)

    profile_sub.add_parser("list").set_defaults(handler=cmd_profile_list)

    compare_parser = subparsers.add_parser("compare", help="Comparison operations")
    compare_sub = compare_parser.add_subparsers(dest="action", required=True)
    c_build = compare_sub.add_parser("build", help="Build a self-contained HTML comparison")
    c_build.add_argument("--tools", nargs="+", required=True, metavar="TOOL_ID",
                         help="Two or more tool_ids with published active profiles.")
    c_build.add_argument("--out", help="Output filename under outputs/comparisons/.")
    c_build.set_defaults(handler=cmd_compare_build)

    work_parser = subparsers.add_parser("work", help="Maintenance operations")
    work_sub = work_parser.add_subparsers(dest="action", required=True)

    w_recover = work_sub.add_parser("recover")
    w_recover.set_defaults(handler=cmd_work_recover)

    w_cleanup = work_sub.add_parser("cleanup")
    w_cleanup.set_defaults(handler=cmd_work_cleanup)

    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(levelname)s %(message)s")
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = args.handler(args)
    except ToolEvalError as exc:
        logger.error("%s: %s", exc.code, exc.message)
        result = _envelope(
            status="error",
            code=exc.code,
            errors=[exc.to_dict()],
        )
    except Exception as exc:  # unexpected failure: still return a valid envelope
        logger.exception("Unhandled error")
        result = _envelope(
            status="error",
            code="HARNESS_UNEXPECTED_ERROR",
            errors=[{"code": "HARNESS_UNEXPECTED_ERROR", "message": str(exc), "retryable": False}],
        )

    print(json.dumps(result))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
