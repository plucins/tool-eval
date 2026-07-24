# Schema: Document Frontmatter

**Document Type**: SPC (Specification)
**Temporal Class**: Standing
**Scope**: Project
**Status**: DRAFT
**Version**: 1

---

## Purpose

This schema defines the YAML frontmatter structure for framework documents. All documents using the Document Type Classification Framework should include frontmatter conforming to this schema.

**Related documents**:
- [Framework Manual](./framework-manual.md) — Document types, scopes, temporal classes
- [REF-001](./ref_framework-concepts.md) — Example REF document
- [THY-001](./theory_framework.md) — Example THY document

---

## Schema Definition

### Required Fields

All documents MUST include these fields:

```yaml
---
id: string          # Unique identifier: [TYPE]-[NNN] e.g., THY-001, REF-001
type: enum          # Content domain from classification framework
title: string       # Human-readable document title
status: enum        # Lifecycle status
version: integer    # Monotonically increasing version number
---
```

#### Field Specifications

| Field | Type | Constraints | Example |
|-------|------|-------------|---------|
| `id` | string | Pattern: `[A-Z]{2,3}-[0-9]{3}` | `THY-001` |
| `type` | enum | One of: STR, SPC, DES, IMP, VAL, OPS, REF, THY, WRK, HST | `THY` |
| `title` | string | Non-empty, human-readable | `AI-Augmented SDLC Framework Theory` |
| `status` | enum | One of: DRAFT, CURRENT, SUPERSEDED, DISCARDED | `DRAFT` |
| `version` | integer | Positive integer, starts at 1 | `2` |

### Recommended Fields

Documents SHOULD include these fields where applicable:

```yaml
scope: enum              # Applicability breadth
temporal_class: enum     # Update frequency characteristic
created: ISO8601         # Creation timestamp
updated: ISO8601         # Last update timestamp
author: string           # Primary author identifier
```

#### Field Specifications

| Field | Type | Constraints | Example |
|-------|------|-------------|---------|
| `scope` | enum | One of: Organisational, Project, Task | `Project` |
| `temporal_class` | enum | One of: Standing, Dynamic, Ephemeral | `Standing` |
| `created` | string | ISO 8601 date or datetime | `2026-01-13` |
| `updated` | string | ISO 8601 date or datetime | `2026-01-14` |
| `author` | string | Actor identifier | `human:pidster` or `ai:claude` |

### Optional Fields

Documents MAY include these fields:

```yaml
references:              # Related documents
  - id: string           # Referenced document ID
    relationship: enum   # Relationship type

supersedes: string       # ID of document this supersedes
superseded_by: string    # ID of document that supersedes this

tags: string[]           # Categorisation tags
```

#### Reference Relationship Types

| Relationship | Semantics |
|--------------|-----------|
| `DERIVES_FROM` | Content synthesised or transformed from source |
| `TRACES_TO` | Formal traceability link |
| `REFERENCES` | Citation without derivation |
| `SUPERSEDES` | This document replaces another |
| `REQUIRES` | Must read referenced document first |
| `SYNTHESISES` | Integrates content from source |

---

## Type-Specific Guidance

### THY (Theory) Documents

THY documents SHOULD include coverage indicators:

```yaml
thy:
  covers:
    problem_mapping: boolean       # Section 1 present
    design_rationale: boolean      # Section 2 present
    modification_patterns: boolean # Section 3 present
    invalidation_conditions: boolean # Section 4 present
```

### REF (Reference) Documents

REF documents cataloguing other documents SHOULD include:

```yaml
ref:
  catalogues: string[]    # IDs of documents catalogued
  quick_lookup: boolean   # Has quick lookup section
```

### HST (Historical) Documents

HST documents SHOULD include:

```yaml
hst:
  rejected_date: ISO8601  # When alternative was rejected
  decision_id: string     # Related decision ID if logged
  reconsider_if: string   # Conditions for reconsideration
```

---

## Complete Example

### THY Document

```yaml
---
id: THY-001
type: THY
title: AI-Augmented SDLC Framework Theory
scope: Project
temporal_class: Standing
status: DRAFT
version: 2
created: 2026-01-13
updated: 2026-01-14
author: human:pidster

references:
  - id: REF-001
    relationship: REQUIRES
  - id: F-1
    relationship: SYNTHESISES
  - id: F-2
    relationship: SYNTHESISES
  - id: C-1
    relationship: SYNTHESISES

thy:
  covers:
    problem_mapping: true
    design_rationale: true
    modification_patterns: true
    invalidation_conditions: true

tags:
  - theory
  - framework
  - naur
---

# THY-001: AI-Augmented SDLC Framework Theory

[Markdown body content...]
```

### REF Document

```yaml
---
id: REF-001
type: REF
title: Framework Concepts Reference
scope: Project
temporal_class: Standing
status: CURRENT
version: 1
created: 2026-01-14
author: ai:claude

ref:
  catalogues:
    - F-1
    - F-2
    - F-3
    - C-1
    - C-2
  quick_lookup: true

tags:
  - reference
  - catalogue
---

# REF-001: Framework Concepts Reference

[Markdown body content...]
```

---

## Validation Rules

### Required Field Validation

1. All required fields must be present
2. `id` must match pattern `[A-Z]{2,3}-[0-9]{3}`
3. `type` must be a valid content domain code
4. `status` must be a valid lifecycle status
5. `version` must be a positive integer

### Consistency Validation

1. If `status` is SUPERSEDED, `superseded_by` SHOULD be present
2. If `supersedes` is present, referenced document SHOULD exist
3. All `references[].id` values SHOULD resolve to existing documents
4. `type` should match the ID prefix (e.g., THY-001 has type: THY)

### Type-Specific Validation

1. THY documents SHOULD have all four `thy.covers` fields
2. REF documents cataloguing concepts SHOULD list them in `ref.catalogues`
3. HST documents SHOULD have `hst.rejected_date`

---

## Parsing Guidance

### For Machines

1. Parse YAML between first `---` and second `---`
2. Validate against this schema
3. Extract `references` for graph construction
4. Body content follows second `---`

### For AI Agents

1. Frontmatter provides structured metadata for indexing and relationships
2. Body provides content for understanding and response
3. Use `references` to identify related documents to read
4. Use `type` to understand document purpose and expected structure

---

## Migration Notes

Existing documents without frontmatter should be updated to include it. Priority:
1. Implementation documents (THY, REF in `implementation/`)
2. Concept documents (if adopting frontmatter for `concepts/`)
3. Working documents (optional—ephemeral may not need)

---

## Validation Status

- ✓ **Core fields**: Aligned with Document Type Classification Framework
- ✓ **Relationship types**: Match framework relationship definitions
- ⚠ **Type-specific fields**: Initial specification; may need extension
- ⚠ **Validation tooling**: Schema defined; validator not yet implemented

---

*This schema enables machine-parseable metadata while preserving flexible Markdown content. It supports Context Graph construction through explicit relationship declarations.*
