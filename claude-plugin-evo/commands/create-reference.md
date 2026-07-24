---
name: create-reference
description: Create a new Reference (REF) document. Reference documents provide conceptual models, glossaries, and structured explanations.
argument-hint: [subject]
---

# Create Reference Document

Create a new REF (Reference) document following the Document Type Classification Framework.

**Complementary skill:** `dialogue-create-reference` — activates autonomously on triggers like "create reference", "make glossary". See `${CLAUDE_PLUGIN_ROOT}/skills/dialogue-create-reference/SKILL.md` for content structuring guidance.

## About Reference Documents

Reference documents capture structured knowledge for lookup and understanding. They differ from Theory documents in that they explain *what* and *how* rather than the integrated *why*.

**REF documents contain:**
- Conceptual models and definitions
- Glossaries and terminology
- Catalogues of related items
- Structured explanations

**Typical characteristics:**
- Temporal Class: Standing (persists, updated as concepts evolve)
- Collaboration Pattern: Partnership to AI-Led (structure is more formal)

## Steps

1. **Gather information**

   Ask the user:
   - What does this reference document cover?
   - Is it a catalogue (listing other documents/concepts) or an explainer?
   - Who is the primary author? (default: human:$USER or ask)

2. **Determine the document ID**

   Check existing REF documents to find the next available ID:
   - Look in the artifacts.reference.directory from `.dialogue/config.yaml`
   - If not configured, check `docs/references/` or `implementation/`
   - Pattern: `REF-NNN` where NNN is zero-padded sequence number
   - Find highest existing REF-NNN and increment

3. **Create the document**

   Create the file at the configured reference directory with filename `ref_[slug].md` where slug is derived from the title.

   Use this template:

   ```markdown
   ---
   id: REF-NNN
   type: REF
   title: [Title from user]
   scope: Project
   temporal_class: Standing
   status: DRAFT
   version: 1
   created: [today's date ISO 8601]
   author: [author identifier]

   ref:
     catalogues: []
     quick_lookup: false

   references: []

   tags:
     - reference
   ---

   # REF-NNN: [Title]

   ## Purpose

   [Brief statement of what this reference document provides]

   ## Quick Lookup

   [If applicable: table or list for quick reference]

   ## Detailed Content

   [Main content sections as appropriate]

   ---

   *Reference document created by Dialogue Framework.*
   ```

4. **Log the observation**

   Use the **dialogue-log-observation** skill to record:
   - Type: STATE
   - Context: "Reference document creation"
   - Content: "Created REF-NNN: [title] as [catalogue|glossary|explainer]"
   - Observer: ai:claude

5. **Confirm and guide**

   Tell the user:
   - Document created at [path]
   - Document ID: REF-NNN
   - Offer to help structure the content based on whether it's a catalogue or explainer
