## Characteristics

Devin is Cognition's AI software engineering agent, now spanning four unified surfaces: the original autonomous cloud agent (web-hosted, plans and executes multi-step tasks end-to-end), Devin CLI ("Devin for Terminal", a standalone terminal-native agent), Devin Desktop (the AI IDE formerly known as Windsurf, rebranded June 2, 2026), and Devin Local (Desktop's local multi-file agent, successor to the retired Cascade agent). It generates code from natural language, edits across multiple files, offers inline Autocomplete, and indexes the codebase for meaning-based retrieval (RAG, Fast Context, DeepWiki), with remote indexing for large or multi-repo teams.

## Access methods

Devin is reachable through a browser (app.devin.ai, sign-in required, no local install), a standalone CLI installed via cli.devin.ai, the standalone Devin Desktop editor (macOS/Windows/Linux), and Windsurf Plugins for JetBrains, VS Code, Visual Studio, Vim/NeoVim, Jupyter, and Chrome (the VS Code plugin is in maintenance mode; Desktop or the JetBrains local plugin is recommended for current agentic capability). Mobile access is limited to an installable Progressive Web App wrapper of the web app (Chrome/Edge desktop install, iOS Safari "Add to Home Screen"); there is no dedicated native mobile app, and Devin Desktop itself ships desktop-only.

## Internal tools and mechanisms

Cloud Devin sessions and CLI/Desktop `--sandbox` runs execute inside isolated environments torn down at session end (the cloud "Devbox" VM; OS-level bubblewrap/Seatbelt/WSL2 sandboxing locally), with terminal commands gated by a configurable confirmation model (CLI y/n approval vs. Bypass/Autonomous modes; Desktop auto-execution levels plus allow/deny lists). Managed Devins (cloud) and Subagents (CLI/Desktop, preview) let one agent coordinate and delegate to child agent sessions running in parallel. Devin Local persists Knowledge entries and `.devin/rules/` (with legacy `.windsurf/rules/` and `.windsurfrules` fallbacks) automatically across sessions, though Desktop does not carry forward free-form conversational memory between sessions.

## Workflows and use cases

Typical workflows include autonomous ticket-to-PR delivery from Linear/Jira with the cloud agent, agentic multi-file builds in Devin Desktop/Devin Local with diff-zone review, automated GitHub/GitLab PR reviews via Devin Review, large-scale multi-file migrations and refactors, and enterprise rollouts using SSO/RBAC, audit logging, and VPC deployment.

## Integrations

Devin natively documents integrations with GitHub, GitLab, Bitbucket, and Azure DevOps for source control, Jira and Linear for project management, and Slack and Microsoft Teams for communication, plus a first-class Model Context Protocol implementation across the CLI, Desktop, and cloud chat surfaces, with a one-click MCP marketplace covering thousands of tools (e.g. Vercel, Atlassian, Notion, Sentry, Neon, Asana). Git-native operation includes pushing branches, GPG-signed commits, and opening pull/merge requests directly as a repository contributor.

## Security

Devin documents customer-facing data-retention/training opt-out (Zero Data Retention on paid plans; Enterprise gets a contractual no-train-without-consent guarantee), enterprise SSO via SAML 2.0 and OIDC with IdP-group role mapping, a two-level custom-roles/RBAC system, an Enterprise API exposing per-event audit logs and usage metrics, a public-code duplication/attribution filter (inherited from the pre-rebrand Windsurf/Codeium completion engine) plus an IP-infringement indemnification commitment for paid tiers, and three deployment models spanning shared Enterprise Cloud, a Cognition-hosted single-tenant VPC, and a fully customer-hosted "Your VPC" with a stateless, no-data-at-rest-outside-environment guarantee.

## Constraints

Several governance capabilities (SSO/RBAC, audit logs/usage-metrics API, VPC/dedicated deployment) are gated to the Enterprise tier and its own API surface. Devin CLI Subagents remain behind a "Subagents (Preview)" toggle, distinct from the generally-available Managed Devins on the cloud agent. Mobile access is a PWA wrapper only (no native app, no confirmed Android install path), and Devin Desktop/Devin Local ship desktop-only. Windows lacks OS-level CLI sandboxing. Some legacy documentation (the duplication filter, Windsurf Plugins, the `.windsurf/rules/` fallback) still carries pre-rebrand "Windsurf"/"Codeium" naming, and worker research flagged several pages (the pricing title, two enterprise-security page titles, the VPC/deployment page relationship) as reconstructed from search snippets rather than a direct page fetch, pending spot-check.
