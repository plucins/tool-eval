# Post-MVP Backlog

Items deliberately out of scope for the Stage-1 MVP (`docs/implementation_plan_v1.md`
§4.2) plus findings surfaced during Increment-5 acceptance. These do **not** block MVP
acceptance; they are tracked for after the gate passes.

## Deferred scope (from plan §4.2)

- **Additional harnesses**: Codex CLI, GitHub Copilot CLI, and the adapter generator
  (MVP is Claude Code only; contracts kept harness-neutral to ease later extraction).
- **Direct LLM API access** (no provider SDK/key today; all reasoning via the harness).
- **Local research infrastructure**: crawler, local corpus, page archive, BM25,
  embeddings, vector DB. Research uses the harness web tools; full pages are not stored.
- **Web application / hosting / backend / telemetry.**
- **Profile and source history** (successful history is not retained).
- **Node.js as a mandatory dependency.**
- **Internationalization / non-English content** (system is English-only).
- **PDF export.**
- **Section B and effectiveness benchmarks.**

## Findings from Increment-5 acceptance

- **F-1 — credentials-in-URL not rejected.** The URL pattern `^https?://[^\s]+$` in
  `source.schema.json` / `profile.schema.json` (`tool.homepage`) accepts
  `https://user:pass@host`, contrary to `standards/global/security.md`. Recommended:
  tighten the pattern to forbid `@` in the authority (e.g. `^https?://[^\s@]+(/[^\s]*)?$`)
  or add a business-rule netloc check, plus a unit test. Consider a `standards-update`
  so "no credentials in URL" is explicitly enforced. See
  `docs/acceptance/security-adversarial-cases.md`.

## Calibration items (from plan §4.3, not blocking)

- Exact time/work budgets, final bundle sizes for hard features, need for an extra
  table/filtering library, and exact pinned dependency versions — to be tuned after
  the pilot on the acceptance tools.
