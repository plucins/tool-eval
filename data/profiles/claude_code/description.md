## Characteristics

Claude Code is Anthropic's task-oriented coding agent: it reads project files, generates and edits implementation code across files, executes commands, and iterates on results. Its verified strengths include natural-language feature implementation, test generation, refactoring, Git operations, and execution-based error recovery. It is an agentic workflow tool, not merely a source of code snippets. These capabilities describe supported workflows, not guaranteed correctness or performance. [Overview](https://code.claude.com/docs/en/overview)

The final merged research distinguishes broad positive capabilities from unresolved ones. Code-editor inline completion and repository-wide meaning-based, relevance-ranked semantic search remain **uncertain**; prompt autocomplete, grep, and LSP navigation must not be presented as confirmation of those features. Supported local-model inference and full zero-network operation were **not found** under the completed negative protocols.

## Access methods

Access spans a standalone CLI, the VS Code extension with a documented Cursor installation path, a JetBrains plugin, Claude Desktop's Code tab, and browser cloud sessions at claude.ai/code. The Claude iOS and Android apps can start, monitor, and steer remote coding work; code executes in cloud infrastructure or on a connected computer, not on the phone. JetBrains requires a separately installed CLI and retains a Beta label. Desktop includes the engine without a separate CLI; Ubuntu/Debian Desktop support is beta. [Overview](https://code.claude.com/docs/en/overview)

The CLI supports macOS, Linux/WSL, and native Windows. Browser onboarding requires GitHub authorization and repository access; eligible Team/Enterprise organizations can use GitHub Enterprise Server. Cloud sessions require Pro, Max, Team, or eligible Enterprise seats, while Console and supported third-party provider access are documented for local CLI/IDE surfaces, not as interchangeable credentials for mobile or cloud sessions. The free Claude chat plan does not include Claude Code.

Exact Pro monthly or annual, Max, and organizational seat prices are not asserted: the registered pricing page's fetched content confirmed usage terms but did not expose paid-plan price cards. Subscription activity across Claude surfaces shares limits; API session cost estimates are not subscription invoices. [Usage FAQ](https://claude.com/pricing)

## Internal tools and mechanisms

The execution loop combines file reading/searching, file edits, shell commands, tests, and Git with feedback from tool results. Plan mode exposes a proposed implementation plan before editing, and per-tool allow/ask/deny rules provide more granular control than a single autonomy switch. Auto mode removes routine prompts using a model-dependent classifier; it is not equivalent to removing all safeguards. In VS Code Manual mode, side-by-side proposed edits can be accepted or rejected per change on supported versions.

Project CLAUDE.md and auto memory carry context across sessions. Nested/path-scoped instructions, isolated subagent research, and compaction help manage large repositories, but do not establish a repository-size performance guarantee or an embedding index. Instruction scopes are concatenated, with **partial**, not guaranteed, conflict precedence; managed settings enforcement is a separate mechanism.

Built-in Explore, Plan, and General-purpose agents cover read-only research and broader multi-step work. Custom subagents can define prompts, tools, permissions, hooks, and skills, subject to plugin-specific restrictions. Lifecycle hooks can enforce decisions around actions; skills package repeatable procedures. Native mods can register callable tools without a separate MCP server on supported engine versions. Formatting and linting examples use hooks/project tooling rather than establishing a universal bundled formatter. [Subagents](https://code.claude.com/docs/en/sub-agents)

Checkpoint rewind can restore tracked code and conversation together, but shell side effects, most subagent edits, external changes, and skipped linked paths are outside its restoration scope. It complements, rather than replaces, version control.

## Workflows and use cases

Documented workflows include implementing a feature across files, exploring an unfamiliar codebase, diagnosing a reported bug, modernizing legacy APIs, generating edge-case tests, and iterating after test failures. Images and mockups can be used to request CSS or HTML structure. Git workflows stage changes, write commits, create branches, and open PRs; local GitHub/GitLab submission requires configured hosting CLIs and credentials. [Common workflows](https://code.claude.com/docs/en/common-workflows)

For automation, headless print mode provides non-interactive runs, structured output, and documented exit semantics when credentials and permissions are provisioned. Background agent view can monitor independent local sessions; cloud sessions continue after the client disconnects. Parallel independent tasks are distinct from subagents collaborating on one task. Cloud routines provide scheduled/event-driven work, while Desktop scheduling requires an open app and awake computer.

Managed GitHub Code Review posts inline findings on configured PR events for Team/Enterprise organizations in research preview. It neither approves PRs nor blocks merging. The documented MCP issue-tracker workflow can turn an issue into implementation and a PR, but requires the relevant connector.

**Inferred deployment pattern:** a controlled team pilot can combine approved plans, narrow permissions, shell sandboxing, headless execution, and customer-operated telemetry. This is a synthesis of verified features, not a vendor promise of safe autonomous operation or a compliance certification.

## Integrations

The verified official integration catalog covers Chrome, GitHub Actions, GitLab CI/CD, and Slack, with dedicated documentation; this is a conservative set of confirmed examples, not an exhaustive ecosystem inventory. GitLab CI/CD is beta and maintained by GitLab. Chrome access has plan, login, browser, extension-version, and WSL restrictions. The earlier per-user Slack integration serves Pro/Max channel mentions, while Team/Enterprise use a separate Claude Tag setup path; the two should not be conflated. [Platforms and integrations](https://code.claude.com/docs/en/platforms)

MCP connects remote HTTP or local stdio servers for tools, databases, and APIs, including customer-authored servers. The documentation points to reviewed Directory connectors and a first-party server-scaffolding plugin, but extraction limitations prevent an exhaustive catalog claim. External content and servers still require trust assessment. [MCP reference](https://code.claude.com/docs/en/mcp)

Static analysis can feed language-server diagnostics into the agent through a code-intelligence plugin and separately installed server binary; the verified LSP path does not run in cloud sessions. Dependency vulnerability scanning is **available through Snyk MCP**, which queries Snyk's vulnerability database, rather than a confirmed native Claude CVE scanner. Snyk requires its own setup/authentication and may run ecosystem tools.

## Security

Verified controls include per-tool allow/ask/deny permissions, lifecycle decision hooks, local OS-enforced shell sandboxing, network-domain rules, organization SSO/access management, and centrally configured OpenTelemetry export. The sandbox is **off by default**, available on macOS/Linux/WSL2 rather than native Windows, and limits shell commands and descendants—not every file/web tool, hook, MCP server, or mod. Excluded commands and unsandboxed retries require additional policy decisions. Customer-operated telemetry export is not a vendor-hosted immutable audit archive.

Prompts and outputs travel over the network with TLS 1.2+; Anthropic API infrastructure documents AES-256 disk encryption at rest, with provider-specific alternatives. Local session transcripts are plaintext. Commercial use is not used for generative-model training by default unless the customer opts in; consumer accounts have a model-improvement preference, with thirty-day retention when disabled rather than zero retention. Qualified Enterprise ZDR is separately enabled and excludes several cloud workflows. Feedback and optional survey transcript-sharing have separate retention rules. [Data usage](https://code.claude.com/docs/en/data-usage)

Secret detection/redaction is **partial**: known-pattern protections are verified in diagnostic, feedback, debug, and shared-transcript paths, not comprehensive filtering of ordinary prompts or generated source. Commercial-contract IP indemnification is confirmed with material exclusions, but a configurable public-code duplication filter is not established. A public DPA applies through Commercial Terms to Team/Enterprise/API use, not automatically to consumer Pro/Max. The DPA links an official subprocessor list, but original-page itemized disclosure could not be verified; that feature remains **uncertain**.

API workspace geography can constrain inference to US infrastructure on supported models, with separate workspace-storage geography and pricing implications. This does not establish EU first-party residency or a subscription-wide guarantee covering every cloud/telemetry flow. Self-hosted environments host execution on customer runners, not a fully private or offline model service; session content still reaches Anthropic.

## Constraints

Availability is surface-, plan-, provider-, model-, and version-dependent. Agent view, cloud routines, and managed Code Review are research previews; self-hosted environments are public beta and disabled by default. Self-hosted runners require Team/Enterprise enablement and customer-managed isolation, egress, and credentials. They retain Anthropic control-plane/session-streaming connectivity and are unavailable for organizations with ZDR or HIPAA configuration. Cloud sessions and managed Code Review also have ZDR/HIPAA restrictions; Code Review is not covered by Anthropic's BAA.

VS Code requires 1.94.0 or later, and verified per-change edit review requires Claude Code 2.1.275+; diffs over 100 changes fall back to whole-file review. Mods require documented engine minimums of 2.1.287 in the terminal and 2.1.286 in Desktop, and are not sandboxed. Local Desktop schedules require Desktop 1.1.5368+ and an awake machine. Auto mode has model/provider eligibility rules and can be disabled by administrators. Not all local configuration, plugin language servers, or credentials transfer into cloud sessions.

Internet access and a supported region are documented setup requirements. Local execution and self-hosted runners do not imply supported local/offline inference. Generated changes, test repair, refactoring, and PR findings need human review and suitable test/build dependencies. Checkpoints cannot reverse arbitrary shell or external side effects, and conflicting custom instructions have no guaranteed scope override.

Subscription limits are shared across surfaces; background work and parallel agents still consume capacity. Exact Pro monthly and annual, Max, Team, and Enterprise prices were not verified from the registered pricing page's paid-plan cards and are intentionally omitted. Connector-directory and marketplace extraction gaps remain relevant to the **uncertain** semantic-search result; inline editor completion and public itemized subprocessor disclosure also remain **uncertain**, not absent. The captured release history is limited to the ten most recent official changelog entries checked on October 11, 2026, ending at 2.1.296; an installation on the stable update channel may lag that version.
