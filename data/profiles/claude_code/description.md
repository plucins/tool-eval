## Characteristics

Claude Code is Anthropic's agentic coding tool that lives in the terminal, understands your codebase, and carries out routine development tasks through natural-language commands. Rather than offering as-you-type completions, it acts as an autonomous agent: given a plain-language goal it searches for relevant files, reads them for context, makes coordinated edits across the project, runs commands and tests to verify its work, and can commit the result when asked. It works across multiple files and tools to complete multi-step tasks, and it can delegate focused subtasks to separate subagent instances.

## Access methods

Claude Code is primarily a command-line tool that runs in your terminal and works alongside your existing IDE without changing your workflow. Native IDE extensions are available for VS Code (plus VS Code forks such as Cursor and Devin Desktop) and for JetBrains IDEs, and a browser-based experience, Claude Code on the web, runs coding tasks on Anthropic-managed cloud infrastructure at claude.ai/code. It is available across Anthropic's Pro, Max, Team, and Enterprise plans, with some newer surfaces (such as the web app) offered as research previews to specific tiers.

## Internal tools and mechanisms

Claude Code operates through a set of built-in tools: it reads and edits files, and executes Bash commands under a permission-based model where read-only commands run without a prompt while system-modifying commands require explicit approval. It supports running commands in the background so long-running processes do not block work, and it can spawn subagents to isolate context and run analyses in parallel. Behavior can be extended and governed with hooks (for example running a linter after edits and feeding results back to the model) and with Model Context Protocol (MCP) servers that connect external tools, databases, and APIs. Project guidance persists across sessions through CLAUDE.md memory files and an auto-memory system.

## Workflows and use cases

Representative workflows include refactoring legacy code across many files from a single instruction, generating and running unit tests then fixing failures, and handling git operations such as creating commits with generated messages and opening pull requests via the GitHub CLI. On Team and Enterprise plans it can perform automated pull request reviews on GitHub, posting inline comments about logic errors, security issues, and regressions. It is also designed for large-codebase and monorepo work, using agentic search and long-context handling to explore and answer questions across an entire repository.

## Integrations

Claude Code connects to hundreds of external tools and data sources through the Model Context Protocol (MCP), an open standard for AI-tool integrations that exposes issue trackers, monitoring dashboards, databases, and other services. It integrates with GitHub through the gh CLI for creating issues, opening pull requests, and reading comments, and it supports the automated Code Review workflow on GitHub PRs. For enterprise deployment, it can run against Claude models hosted in a customer's existing Amazon Bedrock, Google Cloud Vertex AI, or Microsoft Foundry instances.

## Security

Claude Code uses a permission-based execution model and, by default, shows each proposed file edit as a side-by-side diff for accept/reject before writing to disk. It can run commands inside OS-level sandboxes (Seatbelt on macOS, bubblewrap on Linux and WSL2) and in more isolated environments up to full VMs or Anthropic-managed cloud sandboxes. Under commercial terms, code and prompts are not used to train Anthropic's models unless the customer opts in, and Enterprise organizations can configure custom data-retention and zero-data-retention arrangements. Enterprise and Team plans add SSO (SAML/OIDC), role-based permissions, SCIM provisioning, and organization-wide managed policy settings that override local configuration.

## Constraints

Claude Code does not provide as-you-type inline code completion; it is an agent driven by explicit natural-language instructions. It deliberately builds no semantic/embedding index of the codebase, instead using live agentic search (file reads, grep/glob, and LSP symbol lookups), so external code-search or RAG indexes must be added via MCP. Several capabilities are gated by plan or release stage: managed Code Review is a research preview limited to Team and Enterprise subscriptions, Claude Code on the web is a research preview for specific tiers, the extended 1M-token context window is available only on certain newer models, and private deployment relies on the customer's own Bedrock/Vertex/Foundry cloud rather than a fully air-gapped self-hosted product.
