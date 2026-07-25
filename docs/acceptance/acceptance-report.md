# Stage-1 MVP Acceptance Report

**Increment 5 — manual acceptance.** Date: 2026-07-25. Harness: Claude Code
(`.venv`, Python 3.14.5). Prepared by: acceptance run (orchestrator + isolated
`tool-eval-worker` subagents).

## Executive summary

The tool-eval MVP was exercised end-to-end in live Claude Code sessions against the
15 Stage-1 acceptance criteria. **Two AI coding tools (Cursor and Windsurf) were
researched from scratch and published as validated profiles**, and a **four-tool
offline comparison** (Cursor, Windsurf, GitHub Copilot, Claude Code) was generated
and verified. The deterministic Python core enforced every gate as designed:
schema + business validation, the single curation gate, completeness, bounded
repairs, safe publication with an untouched active profile on failure, resume
revision-safety, and self-contained sanitized HTML.

**Result: 14 of 15 criteria proven live end-to-end; 1 (re-research) proven at the
source-discovery level with the full existing-tool republish deferred by operator
decision.** No unvalidated profile was published; the comparison works offline; the
operator documentation carries the whole flow. One low-severity hardening finding
(F-1, credentials-in-URL) was recorded; it does not breach the criterion-15 gate.

This is an engineering acceptance record. A final **non-implementer documentation
walkthrough** (criterion-9/§Przyrost-5 step 9) remains the one recommended human
sign-off before declaring `MVP accepted`.

## What was executed live

| Area | Evidence |
|---|---|
| Source discovery (4 tools) | cursor 14, windsurf 13, claude_code 21 (14 known+7 new), github_copilot 17 (6 known+11 new) official sources accepted. |
| Feature research | 22 `tool-eval-worker` subagents (2 tools × 11 bundles), ≤4 concurrent (D-010), each result schema+business validated. |
| Full taxonomy coverage | cursor & windsurf: 29/29 features, exactly one result each (`MERGE_COMPLETE`). |
| All four statuses | has, partial, not_found (protocol-complete), uncertain (justified) — all observed. |
| Publication | cursor & windsurf `PROFILE_PUBLISHED` + `PROFILE_VALID`; content-completeness gate (facts + documented + inferred use cases) enforced. |
| Controlled failure | `run fail` moved the run to `.work/failed-runs/`; active profile hash + date unchanged. |
| Curation | accept/reject/defer in one gate; revision 4→5 bump; `requires_research` marking; unresolved gate enforced (then reverted). |
| Resume safety | `RUN_RESUMABLE` on match; `CONFIG_REVISION_MISMATCH` after external config change. |
| Comparison | 4-tool 544 KB offline HTML; two builds byte-identical; no external resource loads; dates/age/spread/warnings shown. |
| Security | 25 adversarial tests pass; live prompt-injection attempts logged as warnings, never obeyed; manual URL-safety probes. |

## Criterion results

See `checklist.md` for the full 15-row table. Summary: **✅ 1,3,4,5,6,7,8,9,10,11,12,
13,14,15**; **⚠️ 2** (source-level re-research proven; full existing-tool republish
deferred per operator).

## Scope decision (operator)

The operator chose to **finalize without the full feature-level re-research** of the
two pre-existing tools (github_copilot, claude_code). Their re-research was performed
and accepted at the source-discovery level (known ∪ new sources), and their existing
validated profiles were used for the comparison. Closing criterion 2 to an
unconditional pass requires running the remaining feature-research waves for one
existing tool through to a republished profile (the same proven pipeline used for
cursor/windsurf).

## Findings

- **F-1 (low) — credentials-in-URL not rejected.** `^https?://[^\s]+$` accepts
  `https://user:pass@host`. Criterion-15 gate (no code execution / no agent steering)
  is still met. Recommended fix + `standards-update` in `post-mvp-backlog.md` and
  `security-adversarial-cases.md`.
- **Worker WebFetch unavailable.** Feature workers gathered excerpts via
  domain-restricted WebSearch rather than raw-page WebFetch; several workers flagged
  that verbatim excerpts should be re-verified against live pages before external
  publication. This does not affect status determinations but is noted for data
  provenance.

## Recommendation

Treat the MVP as **substantively accepted**: the full pipeline and all safety gates
are demonstrated on real tools with real data. Before a formal `MVP accepted`
sign-off, (a) complete the non-implementer documentation walkthrough, and
(b) optionally close criterion 2 by republishing one re-researched existing-tool
profile. Post-MVP items and F-1 are tracked in `post-mvp-backlog.md`.

> Note (AI-generated deliverable): this report and the generated profiles/HTML
> should be reviewed and validated by a person before any external use.
