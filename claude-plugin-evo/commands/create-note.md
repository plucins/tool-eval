---
name: create-note
description: Create a new Note (NOT) document. Note documents capture transient process artefacts like analysis notes and workshop output.
argument-hint: [subject]
---

# Create Note Document

Create a new NOT (Note) document following the Document Type Classification Framework.

**Complementary skill:** `dialogue-create-note` — activates autonomously on triggers like "capture notes", "record workshop". See `${CLAUDE_PLUGIN_ROOT}/skills/dialogue-create-note/SKILL.md` for capture window guidance.

## About Note Documents

Note documents are ephemeral artefacts created during processes. They capture information at a moment in time that may be synthesised into standing documents later.

**NOT documents contain:**
- Interview notes
- Workshop outputs
- Analysis notes
- Meeting minutes
- Exploration results

**Critical:** Note documents have a **capture window**. If tacit understanding isn't recorded at creation time, it's permanently lost. Record context and insights immediately.

**Typical characteristics:**
- Temporal Class: Ephemeral (single use, short lifespan)
- Collaboration Pattern: Partnership to AI-Led (capture assistance)

## Steps

1. **Gather information**

   Ask the user:
   - What kind of note document is this? (interview notes, analysis, workshop output, etc.)
   - What process or activity produced this?
   - What is the key context that must be captured now?

2. **Determine the document ID**

   Note documents use date-based IDs for uniqueness:
   - Pattern: `NOT-YYYYMMDD-NN` where NN is sequence for that day
   - Check existing NOT documents for today to determine sequence

3. **Create the document**

   Create the file in the notes location (`.dialogue/notes/` or as configured) with filename `not_[date]_[slug].md`.

   Use this template:

   ```markdown
   ---
   id: NOT-YYYYMMDD-NN
   type: NOT
   title: [Title from user]
   scope: Task
   temporal_class: Ephemeral
   status: DRAFT
   version: 1
   created: [now, ISO 8601 datetime]
   author: [author identifier]

   not:
     activity_type: [interview | workshop | analysis | meeting | exploration]
     participants: []
     contributes_to: []

   tags:
     - note
   ---

   # NOT-YYYYMMDD-NN: [Title]

   ## Capture Context

   **Activity:** [What activity produced this?]
   **Date/Time:** [When did this occur?]
   **Participants:** [Who was involved?]
   **Purpose:** [What was the goal?]

   ## Raw Content

   [Capture the content immediately—notes, outputs, observations]

   ## Key Insights

   [What tacit understanding emerged? Capture this NOW before it's lost]

   ## Follow-up Actions

   - [ ] [Any actions arising]

   ## Contribution Target

   [Which standing document(s) should this contribute to?]

   ---

   *Note document created by Dialogue Framework. Ephemeral documents have limited retention—extract key insights to standing documents.*
   ```

4. **Log the observation**

   Use the **dialogue-log-observation** skill to record:
   - Type: EVENT
   - Context: "Note document creation"
   - Content: "Created NOT-[ID]: [activity type] - [brief description]"
   - Observer: ai:claude

5. **Prompt for key insights**

   Ask the user:
   - "What's the most important thing that emerged from this?"
   - "What tacit understanding do you have right now that won't be obvious later?"

   Record answers in the Key Insights section of the document.

6. **Remind about capture window**

   Tell the user:
   - Document created at [path]
   - Document ID: NOT-YYYYMMDD-NN
   - **Important:** Capture insights and context NOW—ephemeral documents lose tacit knowledge quickly
   - Ask: What standing document should this contribute to?
