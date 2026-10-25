## Characteristics

Cursor combines an AI-enabled editor with agents that search project files, generate and refactor code across multiple files, run terminal commands, generate tests, and iterate on feedback. Tab supplies inline suggestions while typing; Agent handles larger plain-language tasks. Image-based UI implementation is documented with a vision-capable model. These capabilities are established in the merged feature results, not promises of error-free or behavior-preserving output.

The product has several distinct execution surfaces: local editor/CLI work, managed Cloud Agents, and self-hosted tool workers connected to Cursor's cloud agent loop. Parallel independent agents are different from coordinated subagents: the former handle separate tasks, while the latter return delegated results to a parent conversation. Long-session mechanisms include summarized context and isolated exploration. The semantic-search feature remains uncertain because current exact-match/regex documentation and older embedding-based research claims have not been reconciled.

Plan Mode provides a reviewable implementation plan before code-writing when explicitly selected. It is not a universal pre-apply gate: ordinary Agent workspace edits save immediately, so later diff review must not be described as approval before disk writes.

## Access methods

The native Cursor editor installs on macOS, Windows, and Linux and requires a Cursor account. The standalone CLI supports terminal-based interactive work and non-interactive print automation, with documented installation routes for macOS, Linux, WSL, and native Windows. CI use requires authentication and Internet access; JSON and stream-json output are available, but failures may end without a well-formed final JSON result.

Cursor Web starts and manages Cloud Agents without a locally installed editor. Paid plans are required for Cloud Agent runs, which incur model-based usage charges. Existing-repository work requires an administrator-connected source-control provider and the user's read-write repository access. A documented start-from-scratch route is an alternative, subject to paid-plan and Origin setup or administrator settings, not a waiver of existing-repository permissions.

The native iPhone/iPad app directs agents, streams progress, accepts follow-ups, and supports PR review rather than providing a full editor, terminal, or file browser. The merged research records iOS/iPadOS 26.0+, paid-plan requirements for starting runs, an English-only interface, and availability excluding mainland China. Native Android is planned; browser/PWA access is distinct. The October 6 changelog also documents remote control of local agents, which requires the computer to remain powered on and online and Enterprise administrator enablement.

Cursor's agent can also run in supported JetBrains IDEs through ACP, with AI Assistant enabled in version 2025.1+ and a paid Cursor plan. This establishes agent access in those IDEs, not parity with every native-editor feature such as Tab.

## Internal tools and mechanisms

Agent's verified mechanisms include file search, coordinated file editing, terminal execution, linter feedback, checkpoints, and delegated subagents. Explore and Browser are the two documented built-in subagent roles; custom role files can specify prompts, models, and read-only restrictions. Subagents have independent context windows but share the parent's checkout by default, so concurrent writes can conflict. Requested isolation can use separate worktrees or cloud environments; nesting, Task access, policy, and model billing constraints still apply.

Project .mdc rules and scoped AGENTS.md instructions persist repository guidance. The documented instruction hierarchy merges applicable Team, Project, and User rules, with earlier sources taking precedence in conflicts. These rules are scoped Agent guidance, not model memory or a guarantee that every AI feature receives the same instructions. Tab and Bugbot have different scope; Bugbot uses separate repository instructions.

Lifecycle hooks can observe, block, or modify actions, with cloud-specific event and configuration limitations. Explicit blocking and invalid permission outputs differ from other hook failures that may proceed by default. MCP enables external tools and custom servers. The SDK's customTools path is explicitly MCP-backed, so this profile does not assert an independent native function-registration interface.

Agent checkpoints restore modified files across a session, but do not roll back conversation history, external command effects, or the whole environment. Linter feedback integration is documented for JavaScript/TypeScript with installed linter extensions; it is not evidence of a bundled universal formatter or analyzer.

## Workflows and use cases

Vendor-documented workflows include planning a feature before implementation, test-driven development, generating characterization tests before refactoring, turning mockups into UI, scheduled codebase summaries, event-driven bug triage, and continuous PR review with Bugbot. Verification should include suitable tests, type checking, linting, and visual checks rather than accepting generated code solely because an agent reports completion.

Cloud Agents can work in the background on branches and create PRs, while the Agents Window manages many independent tasks. Automatic fixes of CI failures in agent-created PRs are documented for Teams and GitHub Actions, with skip conditions and a ten-follow-up cap; this is not unrestricted automatic repair of every CI system. Long-running agents also have team controls and are not available for multi-repo environments in the merged research.

The use-case records distinguish documented flows from inferred combinations. Parallel maintenance with human merge review, a narrowly scoped headless CI maintenance gate, and team-standardized agent work are inferred from established features, not vendor guarantees. Automated review also needs a deliberate merge policy: Bugbot findings default to a neutral check, so requiring the check alone does not block merges on unresolved findings.

## Integrations

Official documentation establishes integrations with GitHub, Slack, Linear, and Notion, and names other source-control providers and JetBrains. This is a confirmed set, not an exhaustive marketplace count. GitHub app installation and organization administration govern repository and PR permissions. Slack and Linear require connected workspaces and Cloud Agent setup. Notion's integration is beta, requires a Notion Business or Enterprise plan, and has additional connection/API-key setup; Cloud Agent usage is still billed.

MCP provides an open extension route with custom servers, local or remote transports, and optional OAuth for remote servers. Enterprise administrators can restrict allowed servers and tools. External integration credentials, permissions, provider policies, and model-boundary exposure must be evaluated separately from Cursor's own controls.

Source-control support varies by capability. Bugbot review, automatic CI fixes, Automation triggers, and multi-repo/long-running execution should not be assumed to have identical provider coverage. The merged research retains public-beta and Data Center limitations for some review integrations. Marketplace dependency-security descriptions do not yet establish the precise vulnerability-database matching criterion.

## Security

The merged research confirms Privacy Mode, encryption in transit and at rest, organizational SSO and roles, local sandbox controls, and isolated Cloud Agent VMs. Privacy Mode is an actionable training opt-out, including individual/free users, with team enforcement available. It is not blanket zero retention: abuse investigations, explicitly enabled non-ZDR models, customer-supplied provider keys, and temporary Cloud Agent storage have scoped exceptions. The separate Grok Bot surface must not inherit editor privacy guarantees by assumption.

Terminal commands require local approval by default, but configured Run Modes can reduce approval or run everything. Desktop allowlists and classifier guidance are best-effort convenience, not a security boundary. Local sandboxing is conditional on supported macOS/Linux versions and mode; Run Everything is not sandboxed, and approved escalation can leave sandbox restrictions. Egress policies verified for local sandboxed terminal commands must not be generalized to every tool or Cloud Agent surface.

Configured Cloud Agent Runtime Secrets are redacted from model-visible results and related records. This is partial secret protection, not established discovery of arbitrary credentials in repository files or prompts. Ordinary environment variables remain visible to the agent, and Runtime Secret values remain accessible through the environment terminal.

Teams and Enterprise have SSO and roles; SCIM, per-event audit logs, and programmatic analytics have Enterprise restrictions. Audit logs do not capture every prompt, generated artifact, failed sign-in, or automation run. US-only residency is Enterprise, enabled per team, and limited to eligible models and in-scope features; external integrations, BYOK/custom gateways, and other documented exceptions remain. EU + Iceland availability is inference-only on request, not an equivalent full storage-and-processing commitment.

Public DPA coverage applies to Teams/Enterprise business contracts, not individual plans. The MSA's suggestion IP indemnity is partial under the combined criterion because a built-in public-code duplication-blocking filter was not verified. The itemized subprocessor list remains uncertain after an access denial in the merged research; no vendor list is reconstructed from memory.

## Constraints

### Deployment and connectivity
Full offline AI operation and a customer-hosted deployment of the whole Cursor service were not found under the completed protocols in the merged feature results. Self-Hosted Machines move tool execution to customer machines while Cursor retains inference, planning, and the agent loop. Selected file contents, outputs, diffs, screenshots, MCP results, and metadata still leave the worker, and outbound HTTPS is required. BYOK also routes through Cursor's backend. Supported local/self-hosted inference remains uncertain despite documentation mentioning a compatible base-URL override.

### Plans, models, and platforms
The checked pricing page displays Pro at US$20/month and Teams Standard at US$40/user/month, with custom Enterprise pricing and a limited free Hobby tier; taxes and model usage are separate considerations. Pro/Pro Plus/Ultra have distinct Cursor Models and Other Models pools, while the India-focused Start plan does not include Other Models. Cloud Agent and Automation usage is metered. Model eligibility, administrative restrictions, vision support, context size, and subagent token consumption can change which workflows are available or economical. Desktop, CLI, mobile, browser, and ACP integration capabilities are not interchangeable.

Local sandboxing requires the documented macOS or supported Linux environment; no Windows sandbox parity is asserted. Paid Cloud Agent VMs, self-hosted workers, local Run Modes, and enterprise egress controls have different boundaries. Long-running and multi-repo limitations, repository permissions, and provider-specific review/CI support should be checked before deployment.

### Partial and unresolved criteria
Audit logging and DPA availability are partial because of plan/contract restrictions. Runtime Secret redaction is partial because it protects configured values rather than arbitrary secrets. IP protection is partial because MSA indemnification is established but a built-in duplication filter is not. Semantic retrieval, pre-disk-write granular diff approval, MCP-independent custom function registration, supported local/self-hosted inference, database-backed dependency vulnerability scanning, and inspection of the subprocessor list remain uncertain. None is silently promoted to supported or unsupported by this synthesis.

### Release and pricing coverage
Release history captures five dated announcements newer than July 10, 2026 from the already-registered official changelog root. Dates were checked in the original HTML, not inferred from slugs, relative wording, or search summaries. The root links to older pagination that is not in the final source registry; releases requiring those pages are omitted and the since-date interval is explicitly incomplete. The pricing extraction initially omitted tier cards, so selected monthly prices were recovered from the original HTML. No exact annual discounts, complete paid-tier allowance table, or numeric free quota is supplied without verified coverage.
