# Actor Context Awareness Rules

These rules apply to all AI actors operating within the Dialogue Framework. They ensure actors leverage Reference documents for informed task execution.

## Core Principle

**Actors should be context-aware, not context-dependent.**

Don't rely on conversation memory for standing knowledge. Instead, actively consult REF documents to discover relevant context.

## Rule 1: Consult REF Before Significant Actions

Before executing significant tasks, search Reference (REF-*) documents for relevant principles and guidance.

**When to consult REF:**
- Starting a new task or process
- Making design decisions
- Uncertain about approach
- Work spans multiple sessions

**How to consult REF:**
```
1. Identify the task domain (e.g., "process design", "Phase 1", "architecture")
2. Search ${CLAUDE_PLUGIN_ROOT}/references/ref_*.md for relevant references
3. Check REF-002 (Project Principles) for applicable principles
4. Apply discovered guidance to your approach
5. Note in output when principles influenced your work
```

**Key REF documents:**
| Document | Location | Purpose |
|----------|----------|---------|
| REF-002 | `${CLAUDE_PLUGIN_ROOT}/references/ref_project-principles.md` | Project principles |

## Rule 2: Don't Memorize, Discover

Standing knowledge should not be embedded in conversation context. Instead:

```
✗ "I remember that we decided X last session"
✓ "Let me check the decision logs and principles for guidance"

✗ Assume principles from prior conversation
✓ Consult REF-002 for current principles
```

**Rationale:** Principles may evolve. Decisions may be superseded. The source of truth is the documented artifacts, not conversation memory.

## Rule 3: Reference Traceability

When principles or guidance influence your work:

```
1. Note the reference: "Per PRI-001 (Progressive Value Delivery)..."
2. Link to source if relevant
3. This creates audit trail for why decisions were made
```

## Implementation Notes

### For Process Executor

When executing PROC-* processes:
1. At process start, check REF-002 for relevant principles
2. Apply principles to execution approach (e.g., QUICK mode default per PRI-001)
3. Log principle application as OBS-* if significant

### For General Agents

When handling user requests:
1. If task is non-trivial, quick-scan REF documents
2. Apply relevant principles to approach
3. Mention when principles guide your response

---

*Part of the Dialogue Framework — DEC-20260120-163702*
