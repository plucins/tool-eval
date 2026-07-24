---
name: dialogue-infer-from-code
description: Infer requirements, decisions, and assumptions from code artifacts. Use after code generation or when the user has built something without prior elicitation. Enables "Build First" mode by reverse-capturing graph content from implementation. Triggers on "what did we just build", "capture from code", "infer requirements", "what assumptions did we make", "document what we built".
allowed-tools: Bash, Read, Glob, Grep
---

# Dialogue: Infer from Code

Reverse-capture graph content by analyzing code artifacts. This skill enables "Build First" mode — users who prefer to build first and document later can still populate the context graph with meaningful traceability.

## Framework Grounding

This skill operationalises:
- **Build-First workflow**: Capture from artifacts, not interrogation
- **Emergent information**: Implementation reveals understanding that didn't exist before
- **Information debt visibility**: Surface implicit decisions that should be explicit
- **Retroactive traceability**: Link implementations to inferred requirements

## Core Principle: Offer, Never Assume

**All inferences are proposals, not facts.**

The skill:
1. Analyzes code to identify likely requirements, decisions, assumptions
2. Presents inferences to the human with confidence levels
3. Logs only what the human confirms
4. Notes uncertainty for later validation

Never silently populate the graph. The human validates all inferences.

## When to Use

Use this skill:
- After AI generates code without prior requirements capture
- When reviewing code written by human without framework engagement
- When onboarding existing codebase to the framework
- When user asks "what did we just build?" or "document this"
- Periodically to surface undocumented decisions

## Inference Categories

### 1. Implicit Requirements

Code behavior implies requirements that were never explicitly stated.

| Code Pattern | Inferred Requirement |
|--------------|---------------------|
| Authentication middleware | "System must authenticate users" |
| Input validation | "System must validate [field] format" |
| Error handling | "System must handle [error type] gracefully" |
| Rate limiting | "System must prevent abuse via rate limiting" |
| Caching layer | "System must respond within [X] time" |
| Retry logic | "System must tolerate transient failures" |
| Audit logging | "System must log [action] for audit" |
| Access control | "System must restrict [resource] to [role]" |

### 2. Implicit Decisions

Code structure reveals design decisions that weren't documented.

| Code Pattern | Inferred Decision |
|--------------|------------------|
| Framework choice | "Decided to use [framework] for [purpose]" |
| Architecture pattern | "Decided on [pattern] architecture" |
| Data model shape | "Decided [entity] has [relationship] to [entity]" |
| API design | "Decided on [REST/GraphQL/RPC] for [service]" |
| State management | "Decided to manage state via [approach]" |
| Error strategy | "Decided to [fail fast/retry/fallback] on [error]" |
| Dependency choice | "Decided to use [library] for [capability]" |

### 3. Implicit Assumptions

Code makes assumptions that should be validated.

| Code Pattern | Inferred Assumption |
|--------------|---------------------|
| Hardcoded values | "Assumes [value] is constant/appropriate" |
| No null checks | "Assumes [value] is never null" |
| Sequential processing | "Assumes order doesn't matter / load is low" |
| In-memory storage | "Assumes data fits in memory" |
| Single instance | "Assumes single deployment instance" |
| Network availability | "Assumes [service] is always reachable" |
| Time handling | "Assumes single timezone / UTC everywhere" |
| Locale handling | "Assumes English / single locale" |

### 4. Emergent Observations

Code reveals discoveries made during implementation.

| Code Pattern | Inferred Observation |
|--------------|---------------------|
| TODO/FIXME comments | Discovery of deferred work |
| Workaround code | Discovery of constraint or limitation |
| Complex error handling | Discovery of edge case |
| Performance optimization | Discovery of bottleneck |
| Feature flag | Discovery of uncertainty |

## How to Infer

### Automatic Trigger (Post-Generation)

After AI generates significant code, automatically offer inference:

```
AI: [Generates auth service code]

AI: I've created the authentication service. Based on the code,
    I can infer some implicit requirements and decisions.

    Shall I capture what we built? This helps maintain traceability
    even when we build first and document later.

    [Yes, show me what you found] [No, just the code is fine]
```

### Manual Trigger

User explicitly requests inference:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-infer-from-code/scripts/infer-from-code.sh [path] [--scope recent|all|path]
```

**Parameters:**

| Parameter | Description |
|-----------|-------------|
| `path` | File or directory to analyze (default: recent changes) |
| `--scope recent` | Analyze files changed in current session |
| `--scope all` | Analyze entire codebase (slow, use for onboarding) |
| `--scope path` | Analyze specific path only |

### Interactive Flow

```
User: "What assumptions did we make in that code?"

AI: Analyzing src/services/auth/...

    I found 4 potential assumptions in the authentication service:

    HIGH CONFIDENCE (code strongly implies these):

      1. "JWT tokens are valid for 24 hours"
         Evidence: const TOKEN_EXPIRY = 86400 (line 23)
         [Capture as assumption] [Skip] [It's actually a requirement]

      2. "Refresh tokens are stored in httpOnly cookies"
         Evidence: res.cookie('refresh', token, { httpOnly: true }) (line 67)
         [Capture as decision] [Skip] [Need to discuss]

    MEDIUM CONFIDENCE (likely but less certain):

      3. "Single auth provider (no federation)"
         Evidence: No OAuth/SAML integration code present
         [Capture as assumption] [Skip] [Actually we plan to add SSO]

      4. "Password hashing uses bcrypt with cost factor 12"
         Evidence: bcrypt.hash(password, 12) (line 45)
         [Capture as decision] [Skip] [Should be configurable]

    Which would you like to capture?
```

## Analysis Techniques

### 1. Static Code Analysis

```bash
# Extract patterns from code
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-infer-from-code/scripts/analyze-patterns.sh <path>
```

**Detects:**
- Import statements → dependency decisions
- Class/function signatures → interface decisions
- Configuration values → assumptions
- Comments (TODO, FIXME, HACK) → observations
- Error handling patterns → reliability decisions

### 2. Git Diff Analysis

```bash
# Analyze recent changes
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-infer-from-code/scripts/analyze-diff.sh [since-commit]
```

**Detects:**
- New files → new capabilities (potential requirements)
- Deleted code → removed functionality (scope decisions)
- Changed logic → corrected understanding (observations)
- New dependencies → technology decisions

### 3. Structure Analysis

```bash
# Analyze code organization
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-infer-from-code/scripts/analyze-structure.sh <path>
```

**Detects:**
- Directory structure → architectural decisions
- Module boundaries → component decisions
- Shared utilities → cross-cutting concerns
- Test organization → quality decisions

### 4. Dependency Analysis

```bash
# Analyze package.json, requirements.txt, etc.
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-infer-from-code/scripts/analyze-deps.sh
```

**Detects:**
- Framework choices → major decisions
- Utility libraries → minor decisions
- Version constraints → compatibility assumptions
- Dev dependencies → tooling decisions

## Confidence Levels

Inferences are tagged with confidence based on evidence strength:

| Level | Meaning | Evidence Required |
|-------|---------|------------------|
| **HIGH** | Code explicitly implements this | Direct code pattern match |
| **MEDIUM** | Code strongly suggests this | Multiple indirect indicators |
| **LOW** | Code is consistent with this | Absence of contradicting patterns |
| **UNCERTAIN** | Could go either way | Ambiguous patterns |

### Confidence Factors

**Increases confidence:**
- Explicit implementation (authentication code → auth requirement)
- Configuration values (hardcoded constants → assumptions)
- Comments explaining intent
- Test cases asserting behavior
- Multiple consistent patterns

**Decreases confidence:**
- Generated/boilerplate code
- Copied patterns without customization
- Absence of feature (might be planned)
- Complex conditional logic
- Contradicting patterns elsewhere

## Output Format

### For Each Inference

```yaml
inference:
  type: REQUIREMENT | DECISION | ASSUMPTION | OBSERVATION
  confidence: HIGH | MEDIUM | LOW | UNCERTAIN
  statement: "Human-readable statement of what was inferred"
  evidence:
    - file: src/services/auth/index.ts
      line: 23
      pattern: "const TOKEN_EXPIRY = 86400"
      interpretation: "JWT expiry hardcoded to 24 hours"
    - file: src/services/auth/index.ts
      line: 67
      pattern: "httpOnly: true"
      interpretation: "Refresh token stored securely"
  suggested_artifact:
    type: REQUIREMENT | ASSUMPTION | DECISION
    title: "Suggested title for graph artifact"
    content_domain: SPC | DES | STR
  alternatives:
    - "This could also mean: [alternative interpretation]"
  questions:
    - "Is this intentional or should it be configurable?"
```

### Summary Output

```
Inference Summary for src/services/auth/

  Requirements (3 inferred):
    [HIGH]   System must authenticate users via JWT
    [HIGH]   System must support token refresh
    [MEDIUM] System must expire sessions after inactivity

  Decisions (4 inferred):
    [HIGH]   Use bcrypt for password hashing
    [HIGH]   Store refresh tokens in httpOnly cookies
    [MEDIUM] Use 24-hour token expiry
    [LOW]    Single auth provider (no federation)

  Assumptions (2 inferred):
    [MEDIUM] Token expiry of 24 hours is appropriate
    [LOW]    Single deployment instance

  Observations (1 inferred):
    [HIGH]   TODO: Add rate limiting to login endpoint

  Total: 10 inferences (5 high confidence, 3 medium, 2 low)

  Actions:
    - [Capture all high-confidence items]
    - [Review medium-confidence items]
    - [Dismiss low-confidence items]
    - [Capture specific item by number]
```

## Capture Flow

When user confirms an inference:

### For Requirements

```bash
# Logs requirement and creates graph node
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-log-observation/scripts/log-observation.sh \
  EVENT "ai:claude" \
  "Inferred requirement from code" \
  "REQ: System must authenticate users via JWT" \
  "Inferred from src/services/auth/index.ts" \
  "inference,requirements,auth"

# Then offer to create formal requirement
AI: "Shall I create a formal requirement artifact for this?
     It would be: REQ-NNN: User authentication via JWT"
```

### For Decisions

```bash
# Logs decision
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-log-decision/scripts/log-decision.sh \
  DESIGN "ai:claude" \
  "Password hashing approach" \
  "Use bcrypt with cost factor 12" \
  "Inferred from implementation in auth service" \
  "Code shows bcrypt.hash(password, 12) at line 45" \
  "inference,security,auth"
```

### For Assumptions

```bash
# Logs assumption requiring validation
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-log-observation/scripts/log-observation.sh \
  STATE "ai:claude" \
  "Unvalidated assumption identified" \
  "ASM: 24-hour token expiry is appropriate for this use case" \
  "Inferred from hardcoded TOKEN_EXPIRY = 86400" \
  "inference,assumption,auth,needs-validation"
```

## Integration with Build-First Workflow

### Automatic Post-Build Capture

When significant code is generated without prior requirements:

```
[Code generation completes]

AI: Done! The auth service is ready.

    I noticed we built this without capturing requirements first.
    That's fine — we can capture retroactively.

    Quick summary of what I inferred:
    - 3 implicit requirements (authentication, sessions, security)
    - 4 design decisions (JWT, bcrypt, cookies, expiry)
    - 2 assumptions that should be validated

    [Capture the important stuff] [Show me details] [Skip for now]
```

### Session End Capture

At session end, offer to capture undocumented work:

```
AI: Before we wrap up, I noticed some code changes that aren't
    reflected in the context graph:

    - New middleware in src/middleware/ (3 files)
    - Modified auth service (significant changes)
    - New test files (12 files)

    Want me to infer and capture what we built?

    [Yes, let's document it] [No, I'll do it later] [Show details first]
```

## Codebase Onboarding Mode

For existing codebases joining the framework:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/dialogue-infer-from-code/scripts/infer-from-code.sh --scope all --onboarding
```

**Onboarding flow:**

1. **Scan structure** — Identify major components
2. **Analyze dependencies** — Infer technology decisions
3. **Sample code patterns** — Infer architectural decisions
4. **Generate baseline** — Proposed initial graph population
5. **Human review** — Confirm/reject/modify inferences
6. **Populate graph** — Create confirmed artifacts

**Onboarding output:**

```
Codebase Onboarding Analysis

  Project: my-app
  Files analyzed: 347
  Lines of code: ~45,000

  Inferred Architecture:
    - Monolithic Node.js application
    - Express.js web framework
    - PostgreSQL database (via Prisma)
    - React frontend (separate build)

  Major Components Identified:
    1. API layer (src/api/) — 23 endpoints
    2. Business logic (src/services/) — 8 services
    3. Data access (src/repositories/) — 12 repositories
    4. Utilities (src/utils/) — 15 modules

  Technology Decisions Inferred: 12
  Architectural Decisions Inferred: 8
  Assumptions Inferred: 15

  Estimated review time: 30-45 minutes

  [Start guided review] [Export as draft] [Show all details]
```

## Limitations and Caveats

### What This Skill Cannot Infer

| Cannot Infer | Why | Alternative |
|--------------|-----|-------------|
| Business rationale | Not in code | Elicit from stakeholders |
| Rejected alternatives | Only chosen path visible | Ask "why not X?" |
| Future intentions | Code shows current state | Elicit roadmap |
| Stakeholder context | Technical artifact only | Run PROC-1.2 |
| Priority/value | Code doesn't encode this | Elicit from product owner |

### False Positive Risk

Some patterns have multiple interpretations:

```
Pattern: No input validation on internal API
Could mean:
  A) Assumption: Internal callers are trusted
  B) Decision: Validation happens at gateway
  C) Bug: Validation was forgotten
  D) Scope: Will add validation later

AI should: Present alternatives, let human choose interpretation
```

### Incomplete Picture Warning

Always note when inference is based on partial view:

```
Note: This analysis covers src/services/auth/ only.
      Related code in src/middleware/ and src/api/ may reveal
      additional requirements and decisions.

      [Expand analysis to related paths]
```

## Error Handling

### No Code Found

```
No code found at specified path.

Check:
- Path exists and is readable
- Path contains source files (not just config)
- Git status shows expected files

Try: infer-from-code --scope recent (analyzes uncommitted changes)
```

### Too Much Code

```
Analysis scope too large (>1000 files).

For large codebases, analyze incrementally:
- By component: infer-from-code src/services/auth/
- By recent changes: infer-from-code --scope recent
- In onboarding mode: infer-from-code --scope all --onboarding

This prevents overwhelming results and ensures quality inference.
```

### Unfamiliar Language/Framework

```
Limited analysis: Unfamiliar with [framework/language].

I can still detect:
- File structure patterns
- Dependency declarations
- Comment patterns
- Configuration files

For deeper analysis of [framework] code, consider:
- Adding framework-specific pattern rules
- Manual review of key files
```

---

## Script Implementation Notes

The `infer-from-code.sh` script should:

1. **Accept flexible scope** — Single file, directory, recent changes, or all
2. **Use appropriate analyzers** — Language-specific pattern matching
3. **Aggregate confidence** — Multiple evidence sources increase confidence
4. **Format for human review** — Clear, actionable presentation
5. **Support batch capture** — "Capture all high-confidence items"
6. **Track what's captured** — Don't re-infer already-captured items

### Language Support

Initial implementation should support:
- **TypeScript/JavaScript** — AST parsing, import analysis
- **Python** — Import analysis, docstring extraction
- **General** — Comment patterns, file structure, dependency files

Extensible via pattern definition files.

---

*Part of the Dialogue Framework — enabling Build-First workflow through retroactive capture*
