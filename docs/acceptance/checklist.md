# Stage-1 MVP Acceptance Checklist

**Increment 5 — manual acceptance.** Source of truth: `docs/implementation_plan_v1.md`
section 7 (15-criterion coverage matrix) and the Increment-5 gate (§5).

**Rule (gate):** every criterion must be `pass`; `accepted limitation` is not a
passing result; no unvalidated profile may be published; the comparison HTML must
work offline; documentation must carry the operator through the whole flow.

Legend: ✅ pass · ⚠️ pass with scope note · ❌ fail.

**Acceptance corpus:** `cursor` (new, live-researched), `windsurf` (new,
live-researched), `github_copilot` + `claude_code` (existing profiles; re-research
performed at the source-discovery level — known ∪ new sources accepted).
Interpreter: `.venv` (Python 3.14.5). Baseline: **187 tests pass**.

| # | Criterion | Result | Evidence |
|---:|---|:--:|---|
| 1 | Research creates a new tool profile. | ✅ | `data/profiles/cursor/` and `data/profiles/windsurf/` published live end-to-end (`PROFILE_PUBLISHED`, `PROFILE_VALID`); both `profile.json` + `description.md`. |
| 2 | Re-research reuses known sources and finds new. | ⚠️ | `claude_code` re-research reused 14 known + found 7 new official sources; `github_copilot` reused 6 known + found 11 new — both accepted (`SOURCES_ACCEPTED`). Full feature-level *republish* of the existing tools deferred by operator decision (finalize without full re-research). Mechanism proven at the discovery gate. |
| 3 | Each feature has exactly one valid result. | ✅ | `research merge` for cursor and windsurf both `MERGE_COMPLETE`, 29/29 features, no missing/duplicate/foreign (`verify_completeness`); unit `tests/test_item6_merge.py`. |
| 4 | Every result carries evidence or the not-found protocol. | ✅ | All four statuses observed live — has, partial (cursor IP/on-prem), **not_found** (windsurf mobile/web/sandbox, protocol_complete), **uncertain** (cursor static-analysis, windsurf CLI). D-009 enforced by `business.validate_feature_result`; `tests/test_item3_d009.py`. |
| 5 | Constraints are structural, source-backed, and visible. | ✅ | Constraints stored as `{type,description,source_id}`; rendered in the comparison HTML (136 card blocks, constraints section per tool). |
| 6 | Official integration may yield `has`; community may not. | ✅ | Workers cited only official sources for has/partial and explicitly excluded community forums; `VALIDATION_NO_OFFICIAL_SOURCE` enforced (D-017). |
| 7 | Candidates curated together or deferred. | ✅ | One gate: accept + reject + defer applied together (`CANDIDATES_CURATED`); incomplete decisions → `VALIDATION_CANDIDATES_UNRESOLVED`. |
| 8 | A taxonomy change flags older profiles. | ✅ | Accept bumped taxonomy revision 4→5 and marked cursor/github_copilot/windsurf `requires_research`; external config change → `CONFIG_REVISION_MISMATCH`; comparison surfaces stale-revision + `requires_research` warnings. (Test reverted afterward.) |
| 9 | Validator reports errors and ≤3 repairs. | ✅ | Structured `VALIDATION_*` errors returned throughout live validation (constraint/evidence/warnings slips caught and repaired); repair-round cap unit-tested (`tests/test_item7_repair.py`). |
| 10 | Failed research never changes the active profile/date. | ✅ | Staging built, `run fail`; run moved to `.work/failed-runs/`; cursor `profile.json` hash **and** `researched_at` byte-identical before/after. |
| 11 | Compare builds a self-contained offline HTML. | ✅ | `compare build` over 4 tools → 544 KB file; **0 external resource-load tags**; 3 embedded base64 fonts, inline styles; Bootstrap cards/tabs/tooltips present; `tests/test_html_rendering.py`. |
| 12 | Flags deterministic; incomplete features excluded. | ✅ | Two builds **byte-for-byte identical**; `requires_research`/stale cells excluded with warnings; `tests/test_comparison_flags.py`. |
| 13 | HTML shows dates, age, and spread. | ✅ | Comparison renders per-tool UTC dates (2026-07-25 / 2026-07-24), age in days, freshness + date-spread warnings; `tests/test_profile_freshness.py`. |
| 14 | Profile has description, facts, both use-case kinds. | ✅ | cursor & windsurf built with `additional_facts` + documented **and** inferred use cases (`check_profile_content` passed at build; `profile validate --check-completeness` → `PROFILE_VALID`). |
| 15 | A page cannot steer the agent or execute code. | ✅ | Sanitizer neutralizes script/`onerror`/`onclick`/`javascript:` (escaped inert); safe `https` kept; **live** prompt-injection attempts recorded as `warnings` (3 across runs), never obeyed; 25 security tests pass. See `security-adversarial-cases.md` (finding F-1 = credentials-in-URL hardening, gate still met). |

## Verdict

**14 of 15 criteria fully proven live end-to-end.** Criterion 2 is proven at the
source-discovery level for both existing tools (known ∪ new sources accepted); the
operator elected to finalize without the full feature-level republish of the two
existing tools, so criterion 2 carries a scope note rather than an unconditional
pass. See `acceptance-report.md` for the executive summary and recommendation.
