## Characteristics

GitHub Copilot is an AI coding assistant from GitHub (Microsoft) that spans inline code completion, a conversational assistant (Copilot Chat), and an autonomous "agent mode"/coding agent. It generates code from natural language, edits and refactors across multiple files, generates tests, reviews pull requests, and can plan and execute multi-step tasks. It is delivered as a cloud service and is available across several IDEs, a standalone CLI, the web, and mobile. Capabilities and limits vary by plan (Free, Pro, Pro+, Business, Enterprise) and, for newer capabilities, by release stage.

## Access methods

Copilot is officially supported across multiple editors and surfaces: Visual Studio Code, Visual Studio, JetBrains IDEs, Neovim, Xcode, and Eclipse; a standalone command-line interface; the web (Copilot Chat and immersive mode on github.com); and GitHub Mobile (iOS/Android). Availability of individual surfaces and features can depend on the active plan.

## Internal tools and mechanisms

Beyond inline suggestions, Copilot exposes agent mode (which selects files, proposes edits and terminal commands, and iterates until a task is complete), Copilot Edits with a reviewable accept/discard diff workflow, and a background coding agent that runs in an isolated GitHub Actions environment. It indexes repositories for meaning-based (semantic) codebase search, applies persistent custom instructions (e.g. repository- and organization-scoped instruction files) across sessions, and can be extended with external tools through the Model Context Protocol (MCP) and Copilot Extensions.

## Workflows and use cases

Documented workflows include: as-you-type inline completion; natural-language-to-code generation; coordinated multi-file changes; automated and instruction-driven refactoring; automated test generation; automated code review on pull requests; native git operations (commit-message generation, branch/commit automation via the coding agent); and pull-request creation, where the coding agent can open a PR and write its description. The autonomous coding agent can take a task and drive it to a proposed pull request.

## Integrations

Copilot documents an official extensibility and integration surface: the GitHub Marketplace catalog of Copilot-compatible apps and extensions, Copilot Extensions, and MCP-based integrations (including a curated GitHub MCP Registry of partner and community MCP servers) for connecting external tools and data sources.

## Security

For organizational use Copilot documents enterprise single sign-on (SAML SSO) with SCIM provisioning and role-based administration of Copilot policies; customer-facing controls to opt out of model-training use and to exclude repository content (content exclusion); a public-code duplication/"suggestions matching public code" filter together with IP indemnification for eligible Business/Enterprise plans; and audit logging plus usage metrics for administrators. Several of these controls are gated to Business or Enterprise plans.

## Constraints

Copilot is delivered only as a multi-tenant cloud (SaaS) service: no on-premises or dedicated private-cloud deployment of the Copilot service is documented (research status: not found across official documentation, product, pricing, and changelog sources). Many capabilities are gated by plan tier (notably Business/Enterprise for enterprise security and administrative controls) or are offered at a preview/beta release stage, and some features are specific to particular IDEs. Feature availability should be re-checked against the cited official sources, which change frequently.
