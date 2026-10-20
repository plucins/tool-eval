# Using tool-eval with GitHub Copilot CLI

The Copilot adapter provides research, comparison, and safe resume alongside
the existing Claude Code adapter. Both use the same offline Python CLI,
configuration, schemas, profiles, and HTML renderer. No model SDK or separate
provider API key is added to the Python application. Copilot itself requires
an authenticated account with Copilot CLI access.

## Setup and launch

Install [GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli),
authenticate with `copilot login`, and install tool-eval as described in the
[User Guide](user-guide.md). From the repository root on Linux/macOS:

```bash
.venv/bin/python -m tool_eval config validate
copilot --agent copilot-tool-eval-orchestrator
```

On Windows, use `.venv\Scripts\python.exe` in place of `.venv/bin/python`.
There is no need to activate the existing virtual environment.

The repository supplies:

| Location | Purpose |
|---|---|
| `.github/copilot-instructions.md` | Repository conventions and CLI contract |
| `.github/agents/copilot-tool-eval-orchestrator.agent.md` | Main-session orchestration |
| `.github/agents/copilot-tool-eval-worker.agent.md` | Isolated worker with read/edit/web tools only |
| `.github/skills/copilot-tool-eval-*/SKILL.md` | Entry skills and Copilot workflow |

After adding the files to an already-running CLI session, restart Copilot to
load the agents. Use `/skills reload` to reload skills and
`/skills info copilot-tool-eval-research` to inspect their origin.
The worker is programmatic-only and is not intended for manual selection.

Copilot also discovers `.claude/skills/` and reads `CLAUDE.md`. The Copilot
adapter has distinct names so that neither harness shadows the other's
entries. It reuses the Claude worker's research/content rules as a read-only
reference while replacing its tool-specific restrictions. No Claude executable,
Flowbit plugin migration, or MCP server is required for this adapter.
Unrelated `.claude/` development skills are not ported by this change.

## Operations

In the main orchestrator session:

```text
/copilot-tool-eval-research "GitHub Copilot"
/copilot-tool-eval-compare claude_code cursor github_copilot
/copilot-tool-eval-resume research-20260724-053608-3e810720
```

Research discovers official sources, researches the taxonomy through isolated
workers, merges results, presents candidate accept/reject/defer decisions at
one checkpoint, researches accepted additions, writes content, validates, and
publishes. Successful output is `data/profiles/<tool_id>/profile.json` and
`description.md`. Names are normalized by Python; comparison needs the actual
published IDs, which `.venv/bin/python -m tool_eval profile list` can list.

`research build-profile` registers sources returned by the profile-writing
worker (or supplied through `--content`) alongside the merged feature sources.
Identical source definitions are deduplicated; conflicting definitions of the
same `source_id` block the build. Do not merge the profile-writing result or
edit the source registry manually.

Comparison never starts research or web access. It builds one self-contained
offline HTML file under `outputs/comparisons/`; missing profiles are errors,
while stale or old-revision profiles generate warnings.

Resume keeps the original Python run ID and revalidates existing task results.
Configuration mismatches refuse resume, except controlled taxonomy transitions
already recorded by the curation CLI. A run started by Claude can be resumed
only when its artifacts establish compatible progress and prior decisions.
Do not run two harness sessions against the same active run or taxonomy at
the same time. Copilot's built-in `/resume` resumes a conversation; it is not
the same as `/copilot-tool-eval-resume`.

## Permissions and safety

Keep normal tool approvals enabled. Workers allow Copilot's `web` tool alias
and explicitly list `web_search` and `web_fetch` for search and page fetching,
without shell or further delegation. They reuse
known official pages, store short excerpts rather than whole pages, and treat
source content as untrusted. Repository files and secrets must never be sent
to web search. Tool approval is not approval of candidate features.

Tool allowlists restrict tool categories, not filesystem paths. The worker's
single-result write boundary is an instruction contract reinforced by
orchestrator checks, not an OS sandbox guarantee. Use Copilot's sandbox/path
permissions when stronger filesystem isolation is required; do not use
`--allow-all` as a setup shortcut.

Python owns authoritative run state and publication. Adapter-only attempt
counts and decision checkpoints live in `copilot-checkpoint.json` within the
run. Feature repair rounds use the CLI counter; source/content repair rounds
also require the adapter counter because the current CLI has no content-only
repair operation. Combined repair rounds remain capped at three (or the lower
configured budget). Failures never justify publishing invalid data.

## Troubleshooting

| Problem | Action |
|---|---|
| Agent is missing | Restart from the repository root; inspect `/agent`. |
| Skill is missing or resolves to Claude | Reload skills and use the explicit `copilot-tool-eval-*` name. |
| Worker lacks web access | Restart Copilot after changing the agent allowlist; verify `web_search` and `web_fetch` are available and approved. Report remaining blockers instead of bypassing them with shell. |
| Curation cannot collect operator input | Use an interactive session; never auto-accept candidates in a headless run. |
| Resume progress or prior decisions are ambiguous | Resolve ownership/history with the operator; do not relaunch live writers or reset budgets. |
| `CONFIG_REVISION_MISMATCH` | Start a fresh research run; do not edit frozen state. |
| Interrupted publication | Use `.venv/bin/python -m tool_eval work recover`; do not move profile files manually. |

These files are instructions, not a guarantee of identical behavior across
Copilot versions. A full live research pass requires model/web access, tool
permissions, worker delegation, and interactive curation.

## Official Copilot references

- [Custom agents for CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli)
- [Agent skills for CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)
- [Agent tool aliases and configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
