---
name: help
description: Get help with the Dialogue Framework. Lists commands, explains concepts, and guides usage.
argument-hint: [topic]
---

# /help Command

You are providing help for the Dialogue Framework. Be helpful and concise.

## Step 0: Read Interaction Mode

Check `.dialogue/config.yaml` for `interaction_mode` setting (default: `partnership`). Adapt verbosity:
- **human-led**: Be concise; answer directly without elaboration
- **partnership**: Balanced; provide context and suggest next steps
- **ai-led**: Verbose; explain concepts thoroughly and proactively offer guidance

Also check the user's session memo (`.dialogue/session-memo-{username}.yaml`) for `interaction_mode_preference` which overrides project config.

## Step 1: Determine the Topic

Check for a help topic in this order:

1. **Explicit argument**: If `$ARGUMENTS` is provided, that's the topic
2. **Recent context**: If the conversation makes the topic obvious, use that
3. **Ask the user**: If neither, ask: "What would you like help with? I can explain commands, skills, document types, phases, or help you get started."

## Step 2: Provide Help

Based on the topic, provide the relevant information below. Keep responses focused—don't dump everything at once.

---

## Topics

### "commands" / "what commands"

Present the available commands:

| Command | Purpose |
|---------|---------|
| `/init-dialogue` | Initialise framework for a project (creates `.dialogue/` directory) |
| `/create-theory` | Create THY document (integrated understanding, the "why") |
| `/create-reference` | Create REF document (catalogues, glossaries, explainers) |
| `/create-strategy` | Create STR document (decisions, rationale, business cases) |
| `/create-note` | Create NOT document (ephemeral notes, workshop outputs) |
| `/help [topic]` | This help command |

Mention: "The plugin also has skills that activate automatically—like logging decisions when you say 'I decided to...'"

### "overview" / "what is this" / general

The Dialogue Framework is an AI-augmented SDLC framework that uses structured dialogue, decisions, and observations to enhance project outcomes.

**Core insight:** most software knowledge is tacit—in developers' minds, not documents. The framework helps preserve what can be preserved:

- **Decision logging** — Recording choices and rationale
- **Observation logging** — Capturing states, events, measurements
- **Document creation** — Structured artefacts (Theory, Reference, Strategy, Working)
- **Process guidance** — Phase-aware collaboration patterns

Ask: "Would you like to know more about any of these areas?"

### "documents" / "document types"

| Type | Code | Purpose | Persistence |
|------|------|---------|-------------|
| Theory | THY | Integrated understanding, mental models | Standing |
| Reference | REF | Catalogues, glossaries, explainers | Standing |
| Strategy | STR | Decisions, rationale, business cases | Standing |
| Note | NOT | Notes, analysis, workshop outputs | Ephemeral |
| ADR | — | Architecture Decision Records | Standing |

**Standing** = persists and evolves. **Ephemeral** = captures a moment, may be archived.

### "phases" / "sdlc"

The framework uses a seven-phase SDLC model:

| Phase | Name | Tacit Knowledge |
|-------|------|-----------------|
| 1 | Initiation | High (75%) |
| 2 | Planning | High (55%) |
| 3 | Requirements | Medium (40%) |
| 4 | Design | Medium (35%) |
| 5 | Implementation | Lower (25%) |
| 6 | Testing | Lower (20%) |
| 7 | Operations | Medium (30%) |

**Key insight:** Early phases are tacit-heavy → require more human involvement. Middle phases are more formal → AI can assist more.

### "patterns" / "collaboration"

Five collaboration patterns based on information composition:

| Pattern | When to Use |
|---------|-------------|
| **Human-Only** | Sensitive stakeholder work, politics |
| **Human-Led** | Tacit-heavy phases (1, 2), strategic decisions |
| **Partnership** | Balanced work, design and architecture |
| **AI-Led** | Formal-heavy work, implementation, testing |
| **AI-Only** | Routine generation within constraints |

### "capabilities"

Eight framework capabilities:

| Capability | Description |
|------------|-------------|
| **Elicit** | Gather information from sources |
| **Analyse** | Examine for patterns or significance |
| **Synthesise** | Combine into integrated understanding |
| **Transform** | Convert between representations |
| **Validate** | Check against criteria |
| **Decide** | Choose among alternatives |
| **Generate** | Produce artefacts |
| **Preserve** | Capture for future use |

### "skills" / "list skills" / "what skills"

Point the user to the quick reference:

> The framework has 17 skills that activate automatically when you use trigger phrases.
>
> **Full list**: See `${CLAUDE_PLUGIN_ROOT}/references/quick-reference.md`

Briefly summarise the skill categories:
- **Document Creation**: Create THY, REF, STR, NOT, ADR documents
- **Logging & Tracking**: Log decisions, observations; manage tasks; save sessions
- **Assessment & Process**: Check phase readiness, problem framing, logging compliance
- **Discovery & Help**: Get help, resolve reference IDs

**Example triggers**: "I decided to...", "create task for...", "what's in progress", "save session"

In ai-led mode, list a few example trigger phrases for each category.

### "getting started" / "start" / "how do I"

**Discovery-first approach**: Start with what the user wants to accomplish.

Ask: "What do you want to create or accomplish? I can suggest the best approach."

If they need general orientation:

1. **Initialise** (if needed): Run `/init-dialogue` to create `.dialogue/` directory
2. **Just start working**: The framework captures context as you go
3. **Natural logging**: Say "I decided..." or "I noticed..." — the framework logs automatically
4. **Track work**: Say "status" or "create task for..." to manage tasks

**Concrete examples**:
- "I decided to use PostgreSQL instead of MongoDB" → Decision logged
- "Create task for implementing user auth" → Task created
- "What's in progress?" → Shows active tasks
- "Save session" → Preserves context for next session

**Quick reference**: `${CLAUDE_PLUGIN_ROOT}/references/quick-reference.md` lists all commands and skill triggers.

In ai-led mode, proactively suggest: "Would you like me to show you the most common workflows?"

### Specific command help

If the user asks about a specific command (e.g., "/create-theory"), read that command file and summarise:
- Commands: `${CLAUDE_PLUGIN_ROOT}/commands/[name].md`

### Something else

If the topic isn't covered above, check:
- Skills: `${CLAUDE_PLUGIN_ROOT}/skills/[name]/SKILL.md`
- Manual: `${CLAUDE_PLUGIN_ROOT}/references/framework-manual.md`

If you can't find relevant information, say so and ask if they'd like help with something else.

---

## Step 3: Offer Next Steps (Mode-Aware)

Adapt follow-up offers based on interaction mode:

**human-led**: Minimal follow-up
- End with a brief: "Ask if you need more."

**partnership**: Balanced follow-up
- "Would you like me to explain any of these in more detail?"
- "Want me to help you get started with [relevant action]?"

**ai-led**: Proactive follow-up
- Suggest specific next actions based on context
- "Based on what you're working on, I'd recommend..."
- Offer to demonstrate features: "Would you like me to walk you through [feature]?"
- Proactively mention related capabilities they might not know about
