---
name: init-dialogue
description: Initialise the Dialogue Framework for this project. Creates .dialogue/ directory structure and config.yaml.
---

# Initialise Dialogue Framework

Set up the Dialogue Framework for first use in this project.

## Steps

1. **Check for existing initialisation**

   Check if `.dialogue/` directory exists in the project root.

   - If it exists AND contains `config.yaml`: inform the user the framework is already initialised and ask if they want to reinitialise (this will overwrite config.yaml)
   - If it exists but is empty or missing config.yaml: proceed with initialisation
   - If it doesn't exist: proceed with initialisation

2. **Create directory structure**

   Create the following directories:
   ```
   .dialogue/
   ├── logs/
   │   ├── decisions/
   │   └── observations/
   ├── tasks/
   └── users/
   ```

3. **Create config.yaml**

   Create `.dialogue/config.yaml` with this default content:

   ```yaml
   version: "0.1"

   # Interaction mode controls how Claude communicates (help verbosity, proactivity)
   # Options: human-led | partnership | ai-led
   # - human-led: Concise, on-demand help; minimal session start output
   # - partnership: Balanced help with hints; suggests next steps (default)
   # - ai-led: Verbose, proactive; recommends actions and explains features
   interaction_mode: partnership

   # Team mode controls collaboration features (FW-040)
   # Options: auto | solo | team
   # - auto: Detect from active user count (2+ users within 30 days = team)
   # - solo: Simplified mode - no user registration, single session memo, no sync reminders
   # - team: Full features - user tracking, per-user memos, git sync checks and reminders
   team_mode: auto

   # Project document locations (adjust paths to match your project)
   artifacts:
     adr:
       directory: "docs/decisions"
       pattern: "ADR-*.md"

   # Log locations (per-file directories)
   logs:
     decisions: "file://${CLAUDE_PROJECT_DIR}/.dialogue/logs/decisions/"
     observations: "file://${CLAUDE_PROJECT_DIR}/.dialogue/logs/observations/"

   # Tasks (per-file directory)
   tasks: "file://${CLAUDE_PROJECT_DIR}/.dialogue/tasks/"
   ```

4. **Create .gitkeep files**

   Create `.gitkeep` files in the empty directories to ensure they're tracked:

   - `.dialogue/logs/decisions/.gitkeep`
   - `.dialogue/logs/observations/.gitkeep`
   - `.dialogue/tasks/.gitkeep`
   - `.dialogue/users/.gitkeep`

5. **Confirm completion**

   Tell the user:
   - Dialogue Framework has been initialised
   - They can customise `.dialogue/config.yaml` to match their project structure
   - The framework will track decisions in `.dialogue/logs/decisions/`
   - The framework will track observations in `.dialogue/logs/observations/`
   - Tasks will be stored in `.dialogue/tasks/`
