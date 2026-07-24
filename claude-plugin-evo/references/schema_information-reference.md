# Schema: Information Reference

**Document Type**: SPC (Specification)
**Temporal Class**: Standing
**Scope**: Project
**Status**: DRAFT
**Version**: 2

---

## Purpose

This schema defines how to reference information across the framework. References are identifiers that resolvers translate to content.

**Related documents**:
- [Document Frontmatter Schema](./schema_document-frontmatter.md) — Uses references in frontmatter
- [Framework Manual](./framework-manual.md) — Process capability flow model

---

## Design Principle: IDs Are Self-Describing

References are simply **identifiers**. The ID pattern tells you what type of thing is being referenced. Resolvers handle the complexity of finding and retrieving content.

```
THY-001          → Document (theory)
DEC-20260114-091633  → Decision
human:pidster    → Human actor
https://...      → External URL
```

No scheme prefixes. No type discriminators. Just IDs.

---

## Reference Formats

### Documents

Documents use their natural IDs:

| Pattern | Type | Examples |
|---------|------|----------|
| `THY-NNN` | Theory | `THY-001`, `THY-002` |
| `REF-NNN` | Reference | `REF-001` |
| `STR-NNN` | Strategy | `STR-001` |
| `F-N` | Foundation | `F-1`, `F-2` |
| `C-N` | Concept | `C-1`, `C-8` |
| `O-N` | Operational | `O-1`, `O-3` |
| `I-N` | Integration | `I-1`, `I-3` |
| `G-N` | Guidance | `G-1`, `G-3` |
| `E-N` | Example | `E-1`, `E-2` |

### Decisions and Observations

Timestamp-based IDs:

| Pattern | Type | Example |
|---------|------|---------|
| `DEC-YYYYMMDD-HHMMSS` | Decision | `DEC-20260114-091633` |
| `OBS-YYYYMMDD-HHMMSS` | Observation | `OBS-20260114-094825` |

### tasks

Prefix-based IDs:

| Pattern | Type | Example |
|---------|------|---------|
| `SH-NNN` | Self-Hosting | `SH-001` |
| `CD-NNN` | Conceptual Debt | `CD-001` |
| `FW-NNN` | Framework | `FW-001` |

### Processes and Steps

Hierarchical IDs:

| Pattern | Type | Example |
|---------|------|---------|
| `PROC-P.S` | Process | `PROC-3.1` |
| `P.S.N` | Step | `3.1.4` |

### Actors

Colon-prefixed IDs:

| Pattern | Type | Example |
|---------|------|---------|
| `human:<id>` | Human | `human:pidster` |
| `ai:<id>` | AI | `ai:claude`, `ai:process-architect` |

### External Resources

URLs are references:

```
https://example.com/doc
https://github.com/org/repo/issues/123
```

---

## Reference Objects

When references appear in structured data with metadata:

### Simple Form

```yaml
ref: THY-001
```

### With Relationship

```yaml
reference:
  id: THY-001
  relationship: DERIVES_FROM
```

### With Context

```yaml
reference:
  id: THY-001
  relationship: DERIVES_FROM
  context: "Theoretical grounding for capability model"
```

---

## Relationship Types

| Relationship | Semantics |
|--------------|-----------|
| `DERIVES_FROM` | Content synthesised from source |
| `TRACES_TO` | Formal traceability link |
| `REFERENCES` | Citation without derivation |
| `SUPERSEDES` | This replaces that |
| `REQUIRES` | Must read/complete first |
| `BLOCKS` | Must complete before |
| `INFORMS` | Provides context for |

---

## Version References

When a specific version is needed, append `@vN`:

```yaml
ref: THY-001@v2
```

Default (no version specifier) means current version.

---

## Fragment References

When pointing to a section within a document, append `#section`:

```yaml
ref: THY-001#design-rationale
```

Fragments are optional and type-dependent (headings for markdown, paths for YAML).

---

## Resolution

Resolvers translate IDs to content. The resolver:
1. Parses the ID to determine type (from pattern)
2. Looks up location (from registry or convention)
3. Retrieves content
4. Returns result or error

Resolution is defined in SH-002. This schema only defines the ID formats.

---

## Validation Rules

1. IDs must match a known pattern
2. Actor references must have colon separator
3. URLs must be valid
4. Version specifiers must be `@vN` format
5. Fragments must not contain spaces

---

## Validation Status

- ✓ **ID patterns**: Simple, self-describing
- ✓ **Relationship types**: Consistent with frontmatter schema
- ✓ **Backward compatible**: Existing IDs work unchanged
- ⚠ **Resolution**: Defined conceptually; implementation in SH-002

---

*References are just IDs. Resolvers handle the rest.*
