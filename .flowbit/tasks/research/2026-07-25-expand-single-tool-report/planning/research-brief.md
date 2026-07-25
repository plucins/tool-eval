# Research Brief: Expand Single-Tool Report Content Model

## Original request (user, Polish)

> Potrzebuję rozbudować raport pojedynczego narzędzia o bardziej szczegółowe
> informacje - chcę wiedzieć patrząc na ten raport jakie są use case tego
> narzędzia, jakie są wbudowane narzędzia tego rozwiązania oraz inne, które mi
> zaproponuj, co może zawierać taki raport żeby mieć pełen przegląd narzędzia AI.

## Research question

What content should the single-tool profile/report in tool-eval contain to
give a full overview of an AI coding tool — specifically its **use cases**
and **built-in tools/capabilities** — and what other sections should be
proposed for a complete AI-tool overview?

## Research type

**Mixed** — combines:
- **Technical**: what the current `profile.schema.json` / `use-case.schema.json`
  / `feature-taxonomy.yaml` / reporting layer already capture and render, and
  where the single-tool view actually lives today (there is currently no
  dedicated single-tool HTML template — only `comparison.html.j2`).
- **Literature**: industry practice for what a comprehensive AI coding
  assistant evaluation/comparison writeup typically covers (use cases,
  built-in tooling, integrations, pricing/licensing, security posture, etc.).

## Scope

**Included**
- Current profile schema family (`profile`, `use-case`, `feature-result`,
  `additional-fact` schemas) and `config/feature-taxonomy.yaml`.
- Reporting/rendering layer: `reporting/html.py`, `reporting/markdown.py`,
  `reporting/templates/comparison.html.j2`, `profiles/description.py`.
- Example published profiles under `data/profiles/*/profile.json`.
- `docs/user-guide.md` for how reports are currently described to users.
- External best-practice references for AI coding tool comparison/evaluation
  reports (use cases, built-in tools, ecosystem/integrations, pricing model,
  security/data handling, limitations, target audience, etc.).

**Excluded**
- Actually implementing schema/template changes (this phase is research +
  recommendation; implementation would be a follow-up `/flowbit-development`
  task).
- Live scoring, benchmarking execution, or any network/LLM calls inside the
  Python core — the core must remain deterministic and offline.

**Constraints**
- JSON Schema remains the source of truth for any new profile fields (D-016).
- Any new report content must be sourced from research already gathered
  (source-backed "documented" facts, or labelled "inferred" facts with
  rationale) — never fabricated at render time.
- Python core stays deterministic/offline; LLM reasoning stays in `.claude/`.

## Success criteria

Produce a research report that:
1. Documents what the current single-tool report/profile already contains
   (including the existing `use_cases` schema, which already supports this).
2. Identifies what "built-in tools" would mean for this domain (e.g. embedded
   linters/formatters, built-in agents/subagents, MCP/tool-use support,
   terminal/execution sandboxes) and how/where that should be captured.
3. Proposes a concrete, prioritized list of additional sections for a "full
   overview of an AI tool" report, each with a rationale and a note on
   schema/rendering impact.
4. Flags any gaps between what research workers can realistically source
   (official docs, changelogs, vendor pages) and what would require
   speculation — per the research-protocol standard (no fabricated facts).
