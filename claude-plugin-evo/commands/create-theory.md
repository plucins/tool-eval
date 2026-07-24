---
name: create-theory
description: Create a new Theory (THY) document. Theory documents capture integrated understanding—the "why" that enables coherent system modification.
argument-hint: [theory]
---

# Create Theory Document

Create a new THY (Theory) document following the Document Type Classification Framework.

**Complementary skill:** `dialogue-create-theory` — activates autonomously on triggers like "capture theory", "document understanding". See `${CLAUDE_PLUGIN_ROOT}/skills/dialogue-create-theory/SKILL.md` for elicitation guidance.

## About Theory Documents

Theory documents are special. They attempt to capture what Naur (1985) called the "theory" that developers build—the integrated understanding that enables modification. Reading a THY document doesn't transfer theory; it provides a scaffold for rebuilding it.

**THY documents contain:**
- The problem understanding that shaped the solution
- Why the system is structured the way it is (integrated picture, not individual decisions)
- The mental model that enables modification
- Key tensions and how they were resolved
- What would invalidate the current approach

**Typical characteristics:**
- Temporal Class: Standing (persists and evolves)
- Collaboration Pattern: Partnership (human holds theory; AI assists structure)

## Steps

1. **Gather information**

   Ask the user:
   - What system, component, or concept does this theory document cover?
   - What is the core insight or understanding to capture?
   - Who is the primary author? (default: human:$USER or ask)

2. **Determine the document ID**

   Check existing THY documents to find the next available ID:
   - Look in the artifacts.theory.directory from `.dialogue/config.yaml`
   - If not configured, check `docs/theory/` or `implementation/`
   - Pattern: `THY-NNN` where NNN is zero-padded sequence number
   - Find highest existing THY-NNN and increment

3. **Create the document**

   Create the file at the configured theory directory with filename `theory_[slug].md` where slug is derived from the title.

   Use this template:

   ```markdown
   ---
   id: THY-NNN
   type: THY
   title: [Title from user]
   scope: Project
   temporal_class: Standing
   status: DRAFT
   version: 1
   created: [today's date ISO 8601]
   author: [author identifier]

   thy:
     covers:
       problem_mapping: false
       design_rationale: false
       modification_patterns: false
       invalidation_conditions: false

   references: []

   tags:
     - theory
   ---

   # THY-NNN: [Title]

   > **Theory documents capture integrated understanding.** This document attempts to articulate the mental model that enables coherent modification of [subject]. Reading it provides a scaffold for rebuilding theory, not the theory itself.

   ## 1. Problem Mapping

   *What problem does this address? What understanding shaped the solution?*

   [To be completed]

   ## 2. Design Rationale

   *Why is it structured this way? What's the integrated picture?*

   [To be completed]

   ## 3. Modification Patterns

   *How should this be extended or modified? What mental model enables change?*

   [To be completed]

   ## 4. Invalidation Conditions

   *What would invalidate this approach? When should this be reconsidered?*

   [To be completed]

   ---

   *Document created by Dialogue Framework. Theory documents are living artefacts—update as understanding deepens.*
   ```

4. **Update frontmatter coverage**

   As sections are completed, update the `thy.covers` fields to `true`.

5. **Log the observation**

   Use the **dialogue-log-observation** skill to record:
   - Type: STATE
   - Context: "Theory document creation"
   - Content: "Created THY-NNN: [title] to capture understanding of [subject]"
   - Observer: ai:claude

6. **Confirm and guide**

   Tell the user:
   - Document created at [path]
   - Document ID: THY-NNN
   - Remind them that theory documents work best when written by theory-holders reflecting on their understanding
   - Offer to help them work through each section
