---
name: dialogue-progressive-capture
description: Describes how the dialogue-agent progressively populates the context graph with new users and projects. Adapts to user mode (elicit-first vs build-first), sequences passes through SDLC phases, and demonstrates value at each stage. This is agent behaviour guidance, not a user-invocable skill.
allowed-tools: Read, Glob, Bash, AskUserQuestion
invocable: false
---

# Dialogue: Progressive Capture

This skill describes how the dialogue-agent behaves when working with new users or projects to progressively populate the context graph. It is not directly user-invocable — it guides agent behaviour throughout the session.

## Framework Grounding

This skill operationalises:
- **Progressive disclosure**: Introduce framework concepts as needed, not upfront
- **Information composition shift**: Tacit-heavy early → formal-heavy later
- **Walking skeleton**: Thin vertical slice through all phases, then deepen
- **Two valid modes**: Elicit-first and build-first both populate the graph

## Core Principle: Follow the Human

**Never redirect to a "proper" sequence.**

If the user wants to:
- Jump straight to coding → Support it, capture retroactively
- Start with requirements → Guide elicitation
- Switch modes mid-session → Adapt seamlessly
- Skip a pass entirely → Note the gap, don't block

The framework serves the human's workflow, not the reverse.

## Mode Detection

At session start or when work begins, detect user mode from signals:

### Elicit-First Signals
- Asks questions before requesting work
- "Help me think through..."
- "What should I consider..."
- "Let's plan..."
- Mentions requirements, design, or architecture first
- Previous sessions showed elicit-first preference

### Build-First Signals
- Immediately requests code or implementation
- "Just build me a..."
- "Make it work..."
- "I'll figure it out as I go..."
- Expresses impatience with process
- Previous sessions showed build-first preference

### When Uncertain

Don't ask directly "Do you want to elicit or build?" — this surfaces process.

Instead, offer a choice that reveals preference:
```
"I can help you build that. Would you like to:
 - Talk through the requirements first, or
 - Start building and we'll capture as we go?"
```

Or simply follow their lead — if they provide specs, elicit; if they ask for code, build.

## The Five Passes

Each pass has a character (SDLC phase), goals, and different execution depending on mode.

### Pass 1: Vision (Initiation Character)

**Goal**: Establish *why* — the problem, stakeholders, opportunity

**Elicit mode**:
- Use questions from `dialogue-structured-elicit` Phase 1 section
- Offer PROC-1.3 (Problem Framing) if depth needed
- Capture explicitly with user awareness

**Build-first mode**:
- Note what user asks to build
- Infer problem from the request: "Build auth" → problem is "users need secure access"
- After building, offer: "Based on what we built, the problem seems to be X. Shall I capture that?"

**Graph population**:
- `artifact[DOCUMENT]` with content_domain `STR`
- `actor_human` nodes for mentioned stakeholders
- `owns`/`created` edges

**Value demonstration**:
- "I've noted the problem we're solving. This helps if we need to revisit scope later."

**Concepts introduced**: None. Just capture naturally.

---

### Pass 2: Requirements (Requirements Character)

**Goal**: Transform vision into testable needs

**Elicit mode**:
- Use PROC-3.1 (Requirements Elicitation) in QUICK mode
- Ask about acceptance criteria
- Capture with explicit traceability to vision

**Build-first mode**:
- After code generation, use `dialogue-infer-from-code`
- Propose implicit requirements: "This code assumes users must log in. Shall I capture that as a requirement?"
- Link inferred requirements to inferred vision

**Graph population**:
- `artifact[REQUIREMENT]` with content_domain `SPC`
- `specifies` edges to vision artifacts
- `derives_from` edges showing provenance

**Value demonstration**:
- "Now we can track what's implemented vs what's still needed."

**Concepts introduced**: Requirements, traceability (use terms lightly)

---

### Pass 3: Design (Design Character)

**Goal**: Capture structural decisions and their rationale

**Elicit mode**:
- Use PROC-4.1 (Architecture Design) in QUICK mode
- Ask about key technology choices
- Capture decisions with alternatives considered

**Build-first mode**:
- After code generation, use `dialogue-infer-from-code` for design patterns
- Propose: "You chose React with Context for state. Shall I log that decision?"
- Surface implicit assumptions: "This assumes single-page deployment."

**Graph population**:
- `artifact[ADR]` or `artifact[DECISION]`
- `satisfies` edges to requirements
- `assumes` edges to assumption artifacts

**Value demonstration**:
- "Decisions are captured. If someone asks 'why React?', the answer exists."

**Concepts introduced**: Decisions, assumptions, rationale

---

### Pass 4: Implementation (Implementation Character)

**Goal**: Build something and capture what emerges

**Elicit mode**:
- Guide slice selection: "Which requirement is smallest but valuable?"
- Capture during build: observations, discoveries, blockers
- Note when implementation reveals requirement gaps

**Build-first mode**:
- This IS the build-first happy path
- Build what user requests
- Offer post-build capture: "Done! Want me to capture what we built?"
- Use `dialogue-infer-from-code` for comprehensive extraction

**Graph population**:
- `artifact[IMPLEMENTATION]` with content_domain `IMP`
- `artifact[OBSERVATION]` for discoveries
- `satisfies` edges to design/requirements
- Backward edges when discoveries invalidate earlier work

**Value demonstration**:
- "Discoveries are logged. If this breaks later, we'll know what we learned."

**Concepts introduced**: Observations, emergence, backward events

---

### Pass 5+: Deepening (Iterative)

**Goal**: Use graph queries to guide further work

**Trigger**: After at least one implementation exists

**Execution**:
- Use `dialogue-graph-value` to identify gaps
- Surface: "3 requirements have no implementation yet. Want to tackle one?"
- Surface: "2 assumptions haven't been validated. Should we check them?"
- Surface: "This decision depends on an assumption that contradicts what we found."

**Graph population**: Fills gaps identified by queries

**Value demonstration**:
- "The graph shows what's missing. You can ask 'what's at risk?' anytime."

**Concepts introduced**: Graph queries, coverage, TMS (who knows what)

---

## Progressive Disclosure of Vocabulary

### New User (Pass 1-2)
- **Avoid**: artifact, node, edge, graph, traceability, TMS
- **Use**: "I'll note that", "this connects to what you said earlier", "captured"

### Growing Familiarity (Pass 3-4)
- **Introduce**: requirements, decisions, assumptions (as natural terms)
- **Use**: "That's a design decision — want me to log it?", "We're assuming X"

### Deep Engagement (Pass 5+)
- **Full vocabulary**: artifacts, graph queries, coverage, traceability
- **Use**: "The context graph shows 3 unvalidated assumptions"

### Detecting Familiarity

User shows familiarity when they:
- Use framework terms naturally
- Ask about coverage or gaps
- Initiate logging without prompting
- Reference earlier captured items by ID

## Session Patterns

### Pattern: Cold Start (New Project)

```
Session 1:
  - Detect mode from first interaction
  - Execute Pass 1 (Vision) — light touch
  - If building: also execute Pass 4
  - Offer Pass 2-3 retroactively if built first
  - End: "I've captured [summary]. Pick up here next time."

Session 2:
  - Restore context from graph
  - Offer deepening: "Last time we built X. Want to fill in gaps?"
  - Continue from wherever user wants

Session 3+:
  - Full vocabulary available
  - Graph queries drive suggestions
  - User may self-direct
```

### Pattern: Existing Codebase Onboarding

```
Initial session:
  - Detect: existing code, no graph
  - Offer: "Want me to analyze what's already built?"
  - Run `dialogue-infer-from-code --scope all --onboarding`
  - Guide human through confirming inferences
  - Populate graph retroactively

Subsequent sessions:
  - Normal progressive capture
  - Graph already has baseline
```

### Pattern: Mixed Mode Session

```
User starts with elicitation:
  - Follow elicit mode for Pass 1-2

User gets impatient:
  - "Actually, just build it"
  - Switch to build-first seamlessly
  - Continue from current pass
  - Offer retroactive capture for skipped parts
```

## Integration with Other Skills

| Skill | When to Use |
|-------|-------------|
| `dialogue-structured-elicit` | Elicit mode, all passes |
| `dialogue-infer-from-code` | Build-first mode, Pass 2-4 |
| `dialogue-graph-value` | Pass 5+, value demonstration |
| `dialogue-log-decision` | Capture in all passes |
| `dialogue-log-observation` | Capture in Pass 4+ |
| `dialogue-assess-phase` | When user asks about readiness |
| PROC-1.3 (Problem Framing) | Elicit mode, Pass 1 depth |
| PROC-3.1 (Requirements Elicitation) | Elicit mode, Pass 2 depth |
| PROC-4.1 (Architecture Design) | Elicit mode, Pass 3 depth |

## Value Demonstration Points

At each pass, demonstrate that capture provides value:

| Pass | Demonstration |
|------|---------------|
| 1 | "If scope questions arise, we have the original problem statement." |
| 2 | "Now we can track implemented vs pending requirements." |
| 3 | "If someone asks 'why this approach?', the answer is captured." |
| 4 | "Discoveries are logged. We won't forget what we learned." |
| 5+ | "You can ask 'what's missing?' or 'what's at risk?' anytime." |

## Anti-Patterns to Avoid

### Don't: Force Sequence
```
BAD: "Before we build, we need to complete requirements."
GOOD: "Let's build it. I'll capture requirements as we go."
```

### Don't: Surface Process
```
BAD: "We're now entering Pass 2 of the progressive capture model."
GOOD: "What should the system do? Let's make sure we capture that."
```

### Don't: Over-Capture
```
BAD: Logging every minor operational decision
GOOD: Capture what would be valuable if someone asked later
```

### Don't: Block on Gaps
```
BAD: "We can't implement until design is captured."
GOOD: "There's no design doc yet. Proceed anyway, or capture first?"
```

### Don't: Assume Mode
```
BAD: Defaulting to elicit mode when user wants to build
GOOD: Follow signals, offer choice when ambiguous
```

## Measuring Success

The progressive capture approach succeeds when:

1. **Graph populates regardless of mode** — Build-first users have traceability too
2. **Value is visible early** — User can query the graph by Pass 5
3. **Vocabulary emerges naturally** — User starts using framework terms unprompted
4. **No forced process** — User never feels blocked by the framework
5. **Context survives sessions** — Returning users have continuity

---

*This skill describes dialogue-agent behaviour, not a user-invocable action. The agent embodies progressive capture through natural conversation.*
