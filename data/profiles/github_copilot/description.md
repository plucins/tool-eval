## Characteristics

GitHub Copilot is GitHub's AI coding assistant, spanning inline completions (ghost text accepted with Tab), chat, agent mode in IDEs, a standalone terminal agent (Copilot CLI), a cloud agent that works in the background on GitHub.com, and automated pull request review. It supports natural-language code generation, multi-file edits from a single high-level prompt, test generation, image-to-code via attached mockups or screenshots (model-dependent), and semantic repository search. Autonomy is graduated: CLI plan mode previews work before code is written, Autopilot carries tasks through multiple steps, and granular allow/deny permissions control tool use. Statuses are drawn from official documentation; the diff review/apply workflow and encryption statements could not be confirmed and remain uncertain.

## Access methods

Copilot is reachable from many surfaces: IDE extensions (Visual Studio Code, Visual Studio, JetBrains IDEs, Eclipse, Xcode, plus completions in Vim/Neovim), the standalone Copilot CLI (Linux, macOS, Windows via PowerShell and WSL), GitHub.com (chat and cloud agent with no local installation), and GitHub Mobile for chat. A Copilot SDK lets developers build applications on the same agent runtime. Feature availability differs per client; GitHub publishes a feature matrix for comparison. Individual plans (Free, Student, Pro, Pro+, Max) and organization plans (Business, Enterprise) exist, with Business/Enterprise features subject to administrator policy.

## Internal tools and mechanisms

Copilot CLI runs shell commands and file edits under a per-tool approval model (--allow-tool/--deny-tool, deny rules take precedence), with plan mode, Autopilot, /fleet for parallel subagents, background promotion, and multiple concurrent sessions. Custom agents are Markdown .agent.md profiles with YAML frontmatter at repository, organization or personal level. Lifecycle hooks (sessionStart, preToolUse, postToolUse and others) can run custom commands and approve or deny tool calls. Context is managed through semantic repository indexing, automatic compaction near 80% of the context window in the CLI, and persistent custom instructions and Copilot Memory (public preview). In VS Code, checkpoints restore workspace files and conversation to a prior request. Cloud agent runs CodeQL and secret scanning on generated code, and dependency checks against the GitHub Advisory Database.

## Workflows and use cases

Documented workflows include generating tests, asking the cloud agent to implement tasks in the background and return a pull request, CLI-driven issue-to-branch-to-PR flows, automatic PR review with suggested fixes, and scheduled automations such as nightly failing-test fixes (Pro and above, private/internal repositories). Headless programmatic CLI mode supports scripts and GitHub Actions. Inferred (not vendor-described) uses include isolated-environment CLI use with local models and centrally governed organizational rollout.

## Integrations

Copilot supports MCP servers in IDEs, the CLI, the Copilot app and cloud agent, with a GitHub MCP Registry of partner and community servers and a CLI plugin system. GitHub Marketplace lists Copilot Extensions from third parties (e.g. Linear, Slack, Snyk, SonarQube Cloud). A GitHub app in Microsoft Teams lets users trigger Copilot from notifications (per the October 2026 changelog). The Copilot SDK allows registration of custom tools independent of MCP. Business/Enterprise MCP use requires an organization policy that is disabled by default.

## Security

Business and Enterprise data is not used to train models, individual users can opt out of training, and IDE chat/completion prompts are not retained (other access paths: 28 days). A Data Protection Agreement is available, GitHub publishes a subprocessor list, and an optional duplication filter plus IP indemnity (organization plans, unmodified suggestions with filtering enabled) is offered. Cloud agent and code review run behind a default-on firewall; local and cloud sandboxes exist (cloud in public preview, local off by default). Enterprise audit logs and usage metrics support oversight, though client prompt data is not in the audit log. Data residency (EU, Australia, US, Japan) via GHE.com covers storage, with some data possibly stored or transferred outside the region. Encryption claims and inference-region guarantees were not verified.

## Constraints

Many capabilities are surface-specific: firewall and security scanning apply to the cloud agent; offline mode, permission granularity, plan mode and /fleet are documented for the CLI; checkpoints for VS Code only. Several features are preview or experimental (cloud sandboxes, Copilot Memory, CLI /every and /after, air-gapped GHES CLI technical preview, VS Code hooks). Organization policies can disable agent mode, MCP, code review or mobile chat, and agent usage consumes GitHub AI Credits. Copilot is not available for GitHub Enterprise Server, and it is cloud-hosted rather than self-hosted. Image input needs a vision-capable model, and automations are limited to private/internal repositories. Release-history coverage is limited to entries since 2026-10-10 from the GitHub changelog.
