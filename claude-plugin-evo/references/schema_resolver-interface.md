# Schema: Resolver Interface

**Document Type**: SPC (Specification)
**Temporal Class**: Standing
**Scope**: Project
**Status**: DRAFT
**Version**: 1

---

## Purpose

This schema defines the abstract interface for resolving information references to content. Resolvers translate self-describing IDs (from schema_information-reference.md) into retrievable content.

**Related documents**:
- [Information Reference Schema](./schema_information-reference.md) — Defines ID formats
- [Document Frontmatter Schema](./schema_document-frontmatter.md) — Document metadata
- [Framework Manual](./framework-manual.md) — Transactive memory concepts

---

## Design Principles

### 1. Location Agnosticism

Resolvers abstract away storage location. The same reference ID works regardless of whether content lives in:
- Local filesystem
- Enterprise systems (Confluence, Jira, GitHub)
- External sources (standards, vendor docs)
- Graph databases (future: Kuzu, Memgraph)

### 2. Self-Describing IDs

The ID pattern determines resolution strategy. No scheme prefixes or type discriminators needed—the resolver infers type from pattern.

### 3. Graceful Degradation

Resolution failures return structured errors, not crashes. Partial results are valid (e.g., ID recognised but content not found).

---

## Resolution Operations

### Core Operation: `resolve(id) → Result`

```
Input:  Reference ID (string)
Output: Resolution result (structured)
```

The resolver:
1. **Parses** the ID to determine type (from pattern matching)
2. **Locates** the content source (from registry or convention)
3. **Retrieves** the content (type-specific fetch)
4. **Returns** structured result with content and metadata

---

## Resolution Result Schema

### Success Result

```yaml
status: RESOLVED
id: "THY-001"
type: DOCUMENT
location: "implementation/theory_framework.md"
content_type: "text/markdown"
content: |
  # THY-001: Framework Theory
  ...
metadata:
  title: "Framework Theory"
  temporal_class: Standing
  last_modified: "2026-01-13T18:00:00Z"
```

### Not Found Result

```yaml
status: NOT_FOUND
id: "THY-999"
type: DOCUMENT
error: "No document matching pattern THY-999 found"
searched:
  - "implementation/theory_*.md"
```

### Not Supported Result (Framework Source)

```yaml
status: NOT_SUPPORTED
id: "C-1"
type: CONCEPT
error: "Framework source reference - not available in deployed framework"
note: "F-N, C-N, I-N, G-N, E-N reference framework documentation, not project artifacts."
```

### Invalid ID Result

```yaml
status: INVALID_ID
id: "UNKNOWN-123"
error: "ID does not match any known pattern"
known_patterns:
  - "THY-NNN: Theory documents"
  - "REF-NNN: Reference documents"
  - "DEC-YYYYMMDD-HHMMSS: Decision log entries"
```

### External Reference Result

```yaml
status: EXTERNAL
id: "https://example.com/doc"
type: URL
note: "External URLs are not resolved; use WebFetch"
```

### Actor Reference Result

```yaml
status: RESOLVED
id: "human:pidster"
type: ACTOR_HUMAN
metadata:
  actor_type: human
  identifier: pidster
note: "Actor references resolve to metadata only, not content"
```

---

## Reference Type Resolution

### Deployment Model

The resolver distinguishes between:

1. **Runtime artifacts** — Available in deployed projects using the framework
   - Project documents (THY, REF, STR, ADR)
   - Log entries (DEC, OBS)
   - tasks (SH, CD, FW)
   - Actors

2. **Framework source artifacts** — Only in framework source, NOT deployed
   - Foundation documents (F-N)
   - Concept documents (C-N)
   - Integration documents (I-N)
   - Guidance documents (G-N)
   - Example documents (E-N)

Framework source references return `NOT_SUPPORTED` status.

### Project Document References (Resolvable)

| Pattern | Type | Search Strategy |
|---------|------|-----------------|
| `THY-NNN` | Theory | `implementation/theory_*.md`, match NNN |
| `REF-NNN` | Reference | `implementation/ref_*.md`, match NNN |
| `STR-NNN` | Strategy | `implementation/str_*.md`, match NNN |
| `ADR-NNN` | ADR | `decisions/ADR-NNN-*.md` |

### Framework Source References (NOT Resolvable in Deployment)

| Pattern | Type | Status |
|---------|------|--------|
| `F-N` | Foundation | `NOT_SUPPORTED` |
| `C-N` | Concept | `NOT_SUPPORTED` |
| `O-N` | Operational | `NOT_SUPPORTED` |
| `I-N` | Integration | `NOT_SUPPORTED` |
| `G-N` | Guidance | `NOT_SUPPORTED` |
| `E-N` | Example | `NOT_SUPPORTED` |

### Log Entry References

| Pattern | Type | Search Strategy |
|---------|------|-----------------|
| `DEC-YYYYMMDD-HHMMSS` | Decision | `.dialogue/logs/decisions/<id>.yaml` |
| `OBS-YYYYMMDD-HHMMSS` | Observation | `.dialogue/logs/observations/<id>.yaml` |

### Task References

| Pattern | Type | Search Strategy |
|---------|------|-----------------|
| `SH-NNN` | Self-Hosting | `.dialogue/tasks/<id>.yaml` |
| `CD-NNN` | Conceptual Debt | `.dialogue/tasks/<id>.yaml` |
| `FW-NNN` | Framework | `.dialogue/tasks/<id>.yaml` |

### Actor References

| Pattern | Type | Resolution |
|---------|------|------------|
| `human:<id>` | Human Actor | Metadata only (no content retrieval) |
| `ai:<id>` | AI Actor | Metadata only (no content retrieval) |

### External References

| Pattern | Type | Resolution |
|---------|------|------------|
| `https://...` | URL | Not resolved (return EXTERNAL status) |
| `http://...` | URL | Not resolved (return EXTERNAL status) |

---

## Version and Fragment Resolution

### Version Specifier

When ID includes `@vN` suffix:
1. Parse version number
2. Look for versioned file or section
3. If not found, return error with available versions

```yaml
# Request: THY-001@v2
status: NOT_FOUND
id: "THY-001@v2"
error: "Version 2 not found"
available_versions: [1]
```

### Fragment Specifier

When ID includes `#section` suffix:
1. Resolve base document first
2. Extract fragment (heading for markdown, path for YAML)
3. Return fragment content with base document metadata

```yaml
# Request: THY-001#design-rationale
status: RESOLVED
id: "THY-001#design-rationale"
type: DOCUMENT_FRAGMENT
location: "implementation/theory_framework.md#design-rationale"
content: |
  ## Design Rationale
  ...
```

---

## Error Handling

### Error Categories

| Category | Meaning | Recovery |
|----------|---------|----------|
| `INVALID_ID` | ID doesn't match any pattern | Show known patterns |
| `NOT_FOUND` | Pattern matched but content not found | Show searched locations |
| `NOT_SUPPORTED` | Framework source reference | Direct to framework docs |
| `AMBIGUOUS` | Multiple matches for ID | List all matches |
| `ACCESS_ERROR` | Permission or I/O error | Include system error |
| `EXTERNAL` | URL reference (not resolved) | Note to use WebFetch |

### Ambiguous Resolution

When multiple files match:

```yaml
status: AMBIGUOUS
id: "THY-1"
type: DOCUMENT
error: "Multiple documents match pattern"
matches:
  - "implementation/theory_framework.md"
  - "implementation/theory_framework-resilience.md"
resolution_hint: "Use full filename or more specific reference"
```

---

## Implementation Requirements

### Filesystem Resolver (Initial Implementation)

The filesystem resolver MUST:

1. **Pattern Recognition**: Match ID against known patterns using regex
2. **Convention-Based Lookup**: Use directory conventions to locate files
3. **YAML Parsing**: Extract entries from log files and tasks
4. **Markdown Extraction**: Read and optionally parse markdown documents
5. **Structured Output**: Return JSON/YAML result conforming to schema

### Future Resolvers

Alternative resolvers (e.g., Kuzu graph, enterprise systems) MUST:

1. Implement the same `resolve(id) → Result` interface
2. Return results conforming to this schema
3. Handle all reference types (or return NOT_SUPPORTED for unsupported types)
4. Be selectable via configuration

---

## TMS Alignment

This resolver implements the **Retrieval** operation from Transactive Memory:

| TMS Operation | Resolver Equivalent |
|---------------|---------------------|
| Retrieval | `resolve(id)` — fetch content by reference |
| Directory | Pattern matching — know what type from ID |
| Allocation | Not applicable (resolvers read, not write) |

The resolver enables the Context Graph to answer "where is this?" and "what does it contain?" — core TMS retrieval functions.

---

## Validation Status

- ✓ **Result schema**: Complete for all reference types
- ✓ **Error handling**: Categories defined with recovery guidance
- ✓ **TMS alignment**: Mapped to retrieval operation
- ⚠ **Filesystem implementation**: Pending (SH-002 scope)
- ⚠ **Index-based resolution** (F-N, C-N): Requires document ordering convention

---

*Resolvers translate IDs to content. The interface is stable; implementations vary.*
