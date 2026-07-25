# External Best-Practice Findings: Sections in Credible AI-Coding-Tool Overview/Comparison Reports

**Category**: external-best-practice
**Method**: WebSearch (network access available; no WebFetch tool available in this
environment, so findings are based on search-result snippets rather than full-page
fetches — each finding below still cites the concrete source URL surfaced by the
search, but exact page structure/headings were not directly rendered and verified
via a full fetch). Search date: 2026-07-25 (per environment clock).

**Scope reminder**: this file only corroborates *which section types* recur across
public vendor pages and independent comparisons. It does not assert specific
tool facts for use as profile data — those must go through the project's own
research-protocol/curation pipeline, not be lifted from generic comparison blogs.

---

## Confirmed recurring section types (with sources)

### 1. Use cases / workflows the tool is designed for
Confirmed common — both vendor pages and comparison posts frame tools around
"best use cases" as a named section.
- Anthropic's Claude Code product page frames the tool around workflows: "runs in
  your terminal and works alongside your preferred IDE," used for agentic
  engineering workflows (source: Claude Code product page, via search result
  "Claude Code by Anthropic | AI Coding Agent, Terminal, IDE",
  https://claude.com/product/claude-code).
- "8 Best AI Coding Assistants and Their Best Use Cases" — Augment Code, explicitly
  structures the article per-tool around a "best use cases" section:
  https://www.augmentcode.com/tools/8-top-ai-coding-assistants-and-their-best-use-cases
- "2026 Round Up: Top 10 AI Coding Assistants Compared (Features, Pricing, Best Use
  Cases)" — Amplifi Labs, use cases named as one of three comparison axes in the
  title itself: https://www.amplifilabs.com/post/2026-round-up-the-top-10-ai-coding-assistants-compared-features-pricing-best-use-cases

### 2. Built-in tools / agents / capabilities
Confirmed common, and Anthropic's own docs describe this as a first-class
concept ("server tools"/"agentic capabilities").
- Anthropic tool-use docs list built-in "server tools" running on Anthropic's
  infrastructure: web_search, web_fetch, code_execution, tool_search (source:
  "Tool use with Claude - Claude Platform Docs",
  https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview).
- Claude Code is described as having sub-agents, MCP server integration, hooks,
  and headless execution, where the primary agent can spawn sub-agents for
  research/tests/scoped tasks (source: comparison synthesis citing
  https://www.buildthisnow.com/blog/tools/extensions/cursor-vs-windsurf-vs-claude-code
  and https://houseofmvps.com/blog/tools/ai-coding-agents-comparison).
- Anthropic's plugins announcement documents "custom collections of slash
  commands, agents, MCP servers, and hooks" as extension points (source:
  "claude code plugins", https://www.anthropic.com/news/claude-code-plugins).

### 3. Supported IDEs/editors and languages
Confirmed common — treated as a distinct comparison axis, not folded into
"features."
- "IDE breadth is Copilot's first advantage... Copilot works in VS Code,
  JetBrains, IntelliJ, PyCharm, WebStorm, GoLand, Xcode, Neovim, Eclipse, Visual
  Studio, and even SQL Server Management Studio," while "Cursor is a fork of
  Visual Studio Code, and Windsurf is built on top of Visual Studio Code"
  (source: https://kanerika.com/blogs/github-copilot-vs-claude-code-vs-cursor-vs-windsurf/,
  corroborated by https://www.builder.io/blog/cursor-vs-windsurf-vs-github-copilot).

### 4. Pricing & licensing model
Confirmed as one of the most consistently present sections across every source
found — often the top-level differentiator in article titles.
- Tiered/per-seat models with enterprise tiers are the norm; illustrative
  (non-authoritative, third-party-reported) figures found: GitHub Copilot Pro
  from ~$10/month, Business ~$19/user/month; Cursor ~$40/seat plus
  usage-based overage; Windsurf ~$15/month (source:
  https://kanerika.com/blogs/github-copilot-vs-claude-code-vs-cursor-vs-windsurf/,
  https://www.nxcode.io/resources/news/ai-coding-tools-pricing-comparison-2026).
  **Caution**: these are third-party-reported snapshot figures from
  comparison blogs, not vendor pricing pages fetched directly — treat as
  qualitative evidence that "pricing/licensing" is a standard section, not as
  verified current prices for use in a tool's actual profile.
- "Free tiers are genuinely usable in 2026" is called out as a distinct sub-topic
  (free tier vs. paid vs. enterprise) (source:
  https://www.tembo.io/blog/top-ai-coding-assistants).

### 5. Deployment model (cloud-only, on-prem, self-hosted, SSO/enterprise controls)
Confirmed common, particularly in enterprise-oriented comparisons.
- "Tabnine's Code Assistant Platform... supports cloud, on-premises, and
  air-gapped deployment options for teams needing stricter control" (source:
  https://www.tembo.io/blog/top-ai-coding-assistants).
- "GitHub Copilot Enterprise is backed by Microsoft's existing enterprise
  agreements, SOC 2, IP indemnity, audit logs, SAML SSO" (source:
  https://kanerika.com/blogs/github-copilot-vs-claude-code-vs-cursor-vs-windsurf/).

### 6. Security & data-handling posture (training opt-out, retention, compliance)
Confirmed common and treated as a distinct, high-attention section — enough
that it drives its own dedicated articles, not just a subsection.
- GitHub Copilot: "Starting April 24, 2026, GitHub Copilot trains on your code
  by default, with a 30-day opt-out window... Copilot Business and Copilot
  Enterprise customers are contractually exempt, and their interaction data is
  never used for model training" (source:
  https://dev.to/max_quimby/github-copilot-is-now-training-on-your-code-heres-your-30-day-window-to-stop-it-4dmj,
  corroborated by https://dev.to/pooyagolchian/github-copilot-data-policy-changes-what-developers-must-know-in-2026-4e81).
- Cursor: "Privacy Mode is off by default on Free and Pro plans... Business
  plans... offer true zero data retention" (source: search synthesis citing
  comparison articles collected under the query on Cursor/Copilot/Claude Code
  data retention — corroborate directly against Cursor's own privacy/security
  page before using in a profile, this was not fetched first-hand).
- Compliance certifications (SOC 2, IP indemnity) appear as named checklist
  items in enterprise-focused comparisons (source:
  https://kanerika.com/blogs/github-copilot-vs-claude-code-vs-cursor-vs-windsurf/).

### 7. Extensibility (MCP servers, plugins, custom agents/rules)
Confirmed common and increasingly its own comparison axis as MCP adoption
spreads.
- "Claude Code has the deepest MCP integration, with MCP servers being
  first-class citizens... Windsurf's MCP support is present but feels like a
  port rather than a native feature" (source:
  https://www.buildthisnow.com/blog/tools/extensions/cursor-vs-windsurf-vs-claude-code,
  https://houseofmvps.com/blog/tools/ai-coding-agents-comparison).
- Claude Code plugins bundle "slash commands, agents, MCP servers, and hooks"
  as the extensibility surface (source:
  https://www.anthropic.com/news/claude-code-plugins).

### 8. Known limitations / common complaints
Confirmed common — independent comparison posts and community-sourced
articles consistently include a limitations/gotchas section distinct from
the feature list.
- GitHub Copilot: "context loss at file boundaries... quality inconsistency
  on complex codebases with non-standard patterns... rate limits" (source:
  https://medium.com/@kanerika/github-copilot-vs-claude-code-vs-cursor-vs-windsurf-2026-c54f8a5cc051).
- Cursor: reported issues reading multi-file context and screenshots reliably
  in some community reports (source:
  https://stevethoughts.substack.com/p/from-cursor-github-copilot-to-windsurf).
- Windsurf: "credit consumption... burning through monthly credits in days on
  intensive sprints... doesn't let you directly apply updated code" (source:
  https://www.verdent.ai/guides/windsurf-vs-cursor-ai-ide-2026,
  https://codegen.com/comparisons/copilot-vs-windsurf/).
- **Confidence note**: these are self-reported community/blog claims about
  specific tool behavior at a point in time, not vendor-acknowledged
  limitations — appropriate as evidence that a "limitations" section type is
  standard, but individual claims would need independent verification before
  being asserted as fact in an actual tool profile.

### 9. Target audience / team size fit
Confirmed common — multiple sources structure entire articles around this
axis rather than treating it as a footnote.
- "Best AI Coding Assistants for Every Team Size" (source:
  https://www.augmentcode.com/tools/best-ai-coding-assistants-for-every-team-size).
- "Best AI Coding Assistants for Solo Developers in 2026" as a distinct
  article/category (source:
  https://learn.builtthisweek.com/ai-coding-tools/best-ai-coding-assistants-for-solo-developers-in-2026).
- "Large enterprises need security and scale above everything else... a tool
  that feels fast and convenient on day one can become expensive, noisy, or
  difficult to govern at scale" — explicit framing that tool fit varies by
  org size (source: search synthesis of the above two articles).

### 10. Independent benchmarks / evaluation results
Confirmed present, but with an important credibility caveat that should
inform how (or whether) this project surfaces it.
- SWE-bench Verified / SWE-bench Pro are the most commonly cited independent
  benchmarks, e.g. "SWE-bench Leaderboard 2026: All Model Scores, Rankings &
  What They Actually Mean" (source: https://codeant.ai/blogs/swe-bench-scores).
- **Material caveat found**: "On February 23, 2026, OpenAI's Frontier Evals
  team published a detailed post explaining why it had stopped reporting
  SWE-bench Verified scores. Their auditors reviewed 138 of the hardest
  problems across 64 independent runs and found that 59.4% had fundamentally
  flawed or unsolvable test cases... every major frontier model... could
  reproduce the gold-patch solutions verbatim from memory using only the task
  ID, confirming systematic training data contamination" (source:
  https://www.marktechpost.com/2026/05/15/best-ai-agents-for-software-development-ranked-a-benchmark-driven-look-at-the-current-field/,
  corroborated by https://www.layer3labs.io/guides/ai-coding-benchmarks).
- Recommendation implication for this project (analysis, not a sourced fact):
  if a "benchmarks" section is proposed, it should either (a) be scoped to the
  underlying *model* powering a tool rather than the tool product itself
  (benchmarks measure model coding ability, not IDE/agent product quality),
  or (b) be omitted/flagged low-confidence, since even independent evaluators
  now publicly dispute the reliability of the leading benchmark. "For
  enterprise evaluation, the most reliable signal is testing a model on your
  own repository" is the evaluators' own stated conclusion (source:
  https://www.layer3labs.io/guides/ai-coding-benchmarks).

---

## Additional section type surfaced beyond the plan's seed list

### 11. Vendor positioning / competitive framing ("who wins for what")
Not in the original seed list, but every comparison source found ends with an
explicit verdict/recommendation section mapping tool → best-fit scenario
(e.g. "Cursor wins for teams doing complex, multi-file agentic coding...
GitHub Copilot wins for enterprise teams that need compliance... Windsurf
wins on value" — source:
https://www.digitalapplied.com/blog/github-copilot-vs-cursor-vs-windsurf-ai-coding-assistants).
This is really a synthesis of sections 9 (target audience) + 4 (pricing) + 6
(security), so it does not obviously need its own schema field, but is worth
noting as a pattern: comparison content is usually capped with an explicit
"best for X" framing rather than left as a flat feature list.

---

## Cross-tool corroboration summary

| Section type | Claude Code | Cursor | GitHub Copilot | Windsurf | Corroborating sources (count) |
|---|---|---|---|---|---|
| Use cases/workflows | Yes (agentic terminal workflows) | Yes | Yes | Yes | 3+ |
| Built-in tools/agents | Yes (sub-agents, server tools) | Partial (agent mode) | Partial | Partial | 4+ |
| IDE/language support | CLI/terminal-first, IDE-agnostic | VS Code fork | Widest (VS Code, JetBrains, Xcode, etc.) | VS Code-based | 2 |
| Pricing/licensing | Usage/API-based | Per-seat + usage overage | Per-seat tiers + free | Per-seat, credit-based | 3+ |
| Deployment/enterprise controls | API-key/org controlled | Business plan controls | Enterprise (SSO, SOC2, IP indemnity) | Business plan | 2 |
| Security/data handling | User-controlled data flow | Privacy Mode (plan-dependent) | Opt-out training policy (2026 change) | Not detailed in results | 3+ |
| Extensibility (MCP/plugins) | Deepest (native MCP, plugins) | Near-parity (model-dependent) | Least emphasized in results | Present, "port not native" | 2 |
| Known limitations | Not surfaced in results (less community complaint volume found) | Multi-file/context reading complaints | File-boundary context loss, rate limits | Credit burn, manual diff apply | 3 |
| Target audience/team fit | Positioned toward engineering-heavy/agentic teams | Positioned toward power users doing complex refactors | Positioned toward enterprise/regulated orgs (Microsoft ecosystem) | Positioned toward value-conscious/smaller teams | 2 |
| Benchmarks | Cited (Opus scores) but see integrity caveat above | Not directly benchmarked as a product | Not directly benchmarked as a product | Not directly benchmarked as a product | 2 (with major caveat) |

Gaps in this table (e.g. "Not detailed in results" for Windsurf security) are
gaps in *what this search pass surfaced*, not confirmed absences in the
vendor's actual documentation — flagging per research-protocol rather than
treating silence as evidence of absence.

---

## Gaps / limitations of this gathering pass

1. **No WebFetch tool was available** in this environment — all evidence above
   comes from WebSearch result snippets/summaries, not full first-hand page
   reads. Anyone using these citations to source actual profile facts (as
   opposed to corroborating "this section type is common") must re-verify
   against the primary page directly, per the research-protocol's
   documented-vs-inferred distinction.
2. Pricing figures and specific percentages (e.g. SWE-bench scores) quoted
   above are **third-party-reported and explicitly flagged as unverified** —
   they are included only to evidence that "pricing" and "benchmarks" are
   common section *types*, not as authoritative values for use in tool.eval
   profiles.
3. No official Windsurf security/data-handling page was directly surfaced in
   this pass; this is a gap in the search results obtained, not a claim that
   Windsurf lacks such documentation.
4. This gathering pass did not attempt to verify report *structure*
   (heading hierarchy, section ordering) against a rendered vendor page —
   only section *presence/topic* was corroborated.

## Confidence

- **High confidence** (multiple independent sources, consistent framing):
  use cases, built-in tools/agents, pricing & licensing, security & data
  handling, extensibility (MCP/plugins), known limitations, target
  audience/team fit.
- **Medium confidence** (present but thinner/less corroborated in this pass):
  supported IDEs/languages as a *standalone* section (often folded into
  "features" rather than broken out), deployment model as distinct from
  security.
- **Low confidence / caveated**: independent benchmarks as a trustworthy,
  stable section (industry-acknowledged integrity problems with the leading
  benchmark, per OpenAI's own evaluators as reported above).
