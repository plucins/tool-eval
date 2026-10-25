## Characteristics

Claude Code is Anthropic's agentic coding tool. Rather than offering as-you-type completion (not documented in the pages reviewed), it works as an agent loop: it plans a task, writes code across multiple files, runs commands and tests, reads failures and re-runs them until the work verifies, while the user can interrupt at any time. Context is carried across sessions with CLAUDE.md files at managed, user, project and local scopes plus auto memory. A plan mode blocks edits until the user approves a plan, and every prompt creates a checkpoint that /rewind can restore (file-tool edits only; Bash-only changes are not restored). Parallel work is supported through git worktrees, subagents and agent teams.

## Access methods

Claude Code is available as a terminal CLI, a VS Code extension (also installable in Cursor), a JetBrains plugin (listed as beta), a desktop app, a browser surface at claude.ai/code, and a Code tab in the Claude iOS and Android app (which starts and steers cloud or Remote Control sessions; code does not run on the phone). Most surfaces need a Claude subscription or Anthropic Console account, and the CLI, VS Code and JetBrains can also use a supported third-party provider such as Amazon Bedrock. Non-interactive use is available through `claude -p` and the Agent SDK. Mobile access requires a claude.ai account.

## Internal tools and mechanisms

The agent has search, file-editing and execution tools; execution runs shell commands, starts servers, runs tests and uses git. Permission modes (default, acceptEdits, plan, auto, dontAsk, bypassPermissions) set the baseline, with allow/ask/deny rules layered per tool. Lifecycle hooks (shell commands, HTTP endpoints, MCP tool calls, prompts or subagents) fire around tool use and can return decisions. The newer mods API lets plugins register in-process tools and hooks. Custom subagents are markdown files with frontmatter. Ctrl+B backgrounds commands and agents, and scheduled tasks run via /loop, Desktop tasks or cloud routines. Code intelligence plugins add language-server diagnostics and symbol navigation, and a Bash sandbox can restrict shell commands.

## Workflows and use cases

Documented workflows include natural-language multi-file code generation, refactoring, generating tests that match project conventions, turning design images into code, committing and creating pull requests (via gh or glab), managed and local code review, headless CI runs, and scheduled recurring tasks. Long-running work can be handed to cloud sessions and monitored from the web or phone. See the use cases listed in the profile for documented versus inferred scenarios.

## Integrations

Integrations are mainly delivered through the Model Context Protocol: the official docs cite examples such as JIRA, GitHub, Sentry, PostgreSQL, Figma, Slack, Gmail and Notion, and point to a vendor-run Anthropic Directory of reviewed connectors. Plugins can bundle skills, hooks, subagents and MCP servers. GitHub is the main code host for the managed Code Review service and cloud sessions, with a GitHub Actions workflow available; GitLab is supported for merge requests via the local review command and glab. MCP servers must be installed and trusted by the user. Claude Code can also be routed through enterprise gateways to Bedrock, Google Cloud or Microsoft Foundry.

## Security

Controls include an OS-enforced Bash sandbox with filesystem limits and a domain allow/deny proxy for network egress (off by default; macOS, Linux and WSL2 only), configurable network access for cloud sessions, permission modes and rules, and enforceable managed settings. Audit-oriented capabilities include a 180-day organization audit log export, analytics, and OpenTelemetry export. Traffic is encrypted in transit with TLS 1.2+, with at-rest encryption depending on the model provider. Anthropic publishes a DPA incorporated into its Commercial Terms and a subprocessor list (the itemized list could not be read in this run). Commercial-terms data is not used for training, and Zero Data Retention is available to qualified Enterprise accounts. Secret redaction is only documented for optionally uploaded feedback transcripts.

## Constraints

Several capabilities depend on plan or environment. The managed Code Review service requires Team or Enterprise, GitHub-hosted repositories and the Claude GitHub App, and is unavailable with ZDR. Self-hosted environments are in public beta on Team and Enterprise; the Claude apps gateway needs an OIDC identity provider and an upstream provider, and inference is never run on-premises, so full on-premises deployment is only partial. The sandbox does not run on native Windows and covers shell commands only. Checkpoints do not restore Bash-only changes and are kept for the 100 most recent per session. Data region control is only partially documented for Claude Code itself. Full offline operation, local/non-Claude model support, inline completion, semantic codebase search and built-in dependency vulnerability scanning could not be confirmed (status uncertain, not confirmed absent). The release history here covers only releases from 2.1.302 to 2.1.310.
