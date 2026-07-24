---
id: REF-002
type: REF
title: Project Principles Reference
scope: Project
temporal_class: Standing
status: CURRENT
version: 1
created: 2026-01-20
author: human:pid, ai:claude

references:
  - id: DEC-20260120-114214
    relationship: DERIVES_FROM
  - id: THY-001
    relationship: REFERENCES

ref:
  catalogues:
    - PRI-001
  quick_lookup: true

tags:
  - reference
  - principles
  - standing
---

# REF-002: Project Principles Reference

## Purpose

This document catalogues **project principles**—standing guidance that actors should consult and apply during task execution. Principles are derived from design decisions and represent durable understanding about how work should be done.

**For actors**: Search this reference when executing tasks. Principles inform *how* to approach work, not just *what* to do.

**For humans**: This is the authoritative registry of principles. When establishing new principles, add them here and reference the originating decision.

---

## How to Use This Reference

### For AI Actors

When executing a task:
1. **Consult this reference** for principles relevant to the current work
2. **Apply applicable principles** to your approach
3. **Note in your output** when a principle influenced your approach

### For Human Actors

When making decisions:
1. **Check for relevant principles** before deciding
2. **If a principle applies**, follow it or explicitly note why you're deviating
3. **If a new principle emerges**, log as DEC-* then add here

---

## Principle Catalogue

### PRI-001: Progressive Value Delivery

**Source**: [DEC-20260120-114214](.dialogue/logs/decisions/DEC-20260120-114214.yaml)

**Statement**: Prioritise quick meaningful output over strict phase completion.

**Three components**:

| Component | Guidance |
|-----------|----------|
| **Non-blocking progression** | Allow phase advancement with incomplete items; mark deferred items explicitly rather than blocking |
| **Progressive disclosure** | Reveal functionality as users need it, not upfront; start QUICK, offer FULL when complexity emerges |
| **Learn by doing** | Guide users through processes with light touch so they learn the framework while producing value |

**Applies to**:
- Process design (PROC-*)
- User onboarding
- Phase progression logic
- AI facilitation behaviour

**Rationale**: Aligns with the framework's own tacit knowledge principles—understanding comes through practice, not documentation. Prevents the framework from becoming a bureaucratic gatekeeper.

**Related patterns**:
- QUICK/FULL modes in Phase 1 processes
- Deferred items tracking
- Straw Man pattern (capturing incomplete but useful artifacts)

---

## Adding New Principles

When a design decision establishes a durable principle:

1. **Log the decision** using `dialogue-log-decision` skill (type: DESIGN)
2. **Add to this catalogue** with:
   - Unique ID (PRI-NNN)
   - Source reference to DEC-*
   - Clear statement
   - Components/guidance
   - Applicability scope
   - Rationale
3. **Update quick_lookup** in frontmatter if needed

**Criteria for elevation to principle**:
- Applies across multiple contexts (not situation-specific)
- Represents durable understanding (not experimental)
- Guides actor behaviour (actionable, not just descriptive)
- Derived from explicit decision with rationale

---

## Principle Index

| ID | Name | Scope | Source |
|----|------|-------|--------|
| PRI-001 | Progressive Value Delivery | Process design, onboarding | DEC-20260120-114214 |

---

*Part of the Dialogue Framework*
