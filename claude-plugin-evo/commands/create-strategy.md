---
name: create-strategy
description: Create a new Strategy (STR) document. Strategy documents capture rationale, decisions, and business justification.
argument-hint: [subject]
---

# Create Strategy Document

Create a new STR (Strategy) document following the Document Type Classification Framework.

**Complementary skill:** `dialogue-create-strategy` — activates autonomously on triggers like "document strategy", "capture rationale". See `${CLAUDE_PLUGIN_ROOT}/skills/dialogue-create-strategy/SKILL.md` for decision logging integration.

## About Strategy Documents

Strategy documents capture the rationale behind decisions and directions. They record *what* was decided and *why*, but not necessarily the integrated understanding (that's THY).

**STR documents contain:**
- Business cases and justifications
- Project charters and scope definitions
- Strategic decisions and their rationale
- Direction-setting documents

**Note:** For formal architecture decisions with alternatives analysis, use the `dialogue-create-adr` skill instead—ADRs are a specialised form of strategy document.

**Typical characteristics:**
- Temporal Class: Standing (persists as record of decisions made)
- Collaboration Pattern: Human-Led (strategy requires human judgement)

## Steps

1. **Gather information**

   Ask the user:
   - What strategic decision or direction does this document capture?
   - What is the context that led to this decision?
   - Who is the primary author/decision-maker?

2. **Determine the document ID**

   Check existing STR documents to find the next available ID:
   - Look in the artifacts.strategy.directory from `.dialogue/config.yaml`
   - If not configured, check `docs/strategy/`
   - Pattern: `STR-NNN` where NNN is zero-padded sequence number
   - Find highest existing STR-NNN and increment

3. **Create the document**

   Create the file at the configured strategy directory with filename `str_[slug].md` where slug is derived from the title.

   Use this template:

   ```markdown
   ---
   id: STR-NNN
   type: STR
   title: [Title from user]
   scope: Project
   temporal_class: Standing
   status: DRAFT
   version: 1
   created: [today's date ISO 8601]
   author: [author identifier]

   references: []

   tags:
     - strategy
   ---

   # STR-NNN: [Title]

   ## Context

   [What situation prompted this strategic decision?]

   ## Decision

   [What was decided?]

   ## Rationale

   [Why was this decision made? What factors were considered?]

   ## Implications

   [What follows from this decision? What constraints does it create?]

   ## Review Conditions

   [When should this decision be revisited?]

   ---

   *Strategy document created by Dialogue Framework.*
   ```

4. **Log the decision**

   Use the **dialogue-log-decision** skill to record:
   - Type: DESIGN or TACTICAL (depending on scope)
   - Context: "Strategy document STR-NNN"
   - Decision: Brief statement of the strategic decision
   - Rationale: Summary of why
   - Actor: [decision-maker identifier]

5. **Confirm and guide**

   Tell the user:
   - Document created at [path]
   - Document ID: STR-NNN
   - Decision has been logged with reference to STR-NNN
   - If this warrants formal alternatives analysis, suggest creating an ADR instead
