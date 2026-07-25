## Characteristics

Cursor is an AI-first code editor built on a VS Code base. Its agent plans and executes multi-step tasks, generates code from natural language, offers inline (Tab) completion, and edits coordinated changes across multiple files. It indexes the repository for codebase-wide semantic search and supports large-repository/long-context work, including a Max Mode for larger context windows on supported models.

## Access methods

Cursor is available as a standalone desktop editor (macOS, Windows, Linux), through an officially supported JetBrains integration, as a standalone CLI (including a headless mode for CI), and via browser and mobile access to its cloud agents. Users can choose between frontier models from multiple providers.

## Internal tools and mechanisms

The agent runs terminal commands under a configurable approval model and can execute in an OS-native sandbox (Seatbelt on macOS, Landlock/seccomp on Linux). It coordinates sub-agents in separate context windows and can run background/cloud agents asynchronously. Persistent Project Rules (.cursor/rules) and AGENTS.md carry project-scoped instructions across sessions.

## Workflows and use cases

Typical workflows include autonomous multi-file feature implementation with a reviewable diff before apply, automated pull-request review via Bugbot, large-scale codebase modernization using semantic search and multi-file editing, and governed enterprise rollouts with SSO, audit logging, and enforced privacy mode.

## Integrations

Cursor supports the Model Context Protocol (MCP) for connecting external tools and data sources, a first-party Plugins system on the Cursor Marketplace, and native git and GitHub integration (AI commit messages, and opening pull requests directly from background agents).

## Security

Cursor documents a customer-facing Privacy Mode (no code stored/trained on when enabled; enforced by default on Business/Enterprise), enterprise SSO (SAML/OIDC) with SCIM provisioning and role-based access control, admin audit logging, and self-hosted cloud agents that keep code and build execution in the customer's own infrastructure. An IP-indemnification commitment is documented in the enterprise agreement for eligible plans.

## Constraints

Several capabilities are plan-gated to Business/Enterprise (SSO/SCIM, audit logs, enforced privacy mode, self-hosted agents). The native mobile app is iOS-only and in beta; pull-request creation is GitHub-oriented and requires connecting the integration. Cursor does not offer a public-code duplication filter (only the indemnity limb of that criterion is met), and full platform on-premises deployment is not offered (only agent-execution self-hosting). Static-analysis-into-AI integration was left uncertain pending an official source.
