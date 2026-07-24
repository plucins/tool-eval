# Dialogue: an AI-Augmented SDLC Framework

## What Is This?

A **complete, executable framework** for human-AI collaboration across the entire software development lifecycle. The framework operationalises theoretical foundations (Naur's theory-building, Wegner's transactive memory, socio-technical systems theory) into practical process definitions that can guide AI behaviour in real software projects.

## Core Capability

**Phase-Aware AI Collaboration**: The framework recognises that software development phases have fundamentally different information compositions, and adapts AI involvement accordingly:

- **Early phases** (Initiation, Planning): 75-55% tacit knowledge → Human-Led, AI assists
- **Middle phases** (Analysis, Design): 35-50% formal → Partnership, AI generates with validation
- **Implementation phases** (Coding, Testing): 60-65% formal → AI-Led/AI-Only, humans review
- **Operational phase** (Deployment): Returns to 30% tacit → Partnership, operational experience matters

## Novel Features

### 1. Information Composition-Driven Pattern Selection

Unlike approaches that treat AI as uniformly applicable, this framework explicitly models *why* AI can be more or less autonomous in different contexts. The formal/tacit/emergent percentages aren't arbitrary - they derive from the nature of knowledge in each phase and directly determine collaboration patterns.

### 2. Escalation Architecture with Semantic Triggers

Every process step has escalation triggers with:
- **Condition**: What circumstance triggers escalation
- **Severity**: HIGH/MEDIUM/LOW for prioritisation
- **Action**: ESCALATE, RETURN, BLOCK, DEFER
- **Target**: Where control goes (human, another process, specific step)
- **Context**: Natural language explaining the situation

This creates predictable, auditable decision points rather than opaque AI judgement.

### 3. Human-Only Pattern (Exit and Observer Modes)

The Human-Only pattern has two modes:
- **Exit mode**: AI absent entirely; for sensitive conversations where AI presence would inhibit
- **Observer mode**: AI present but passive; prepares materials, records outcomes, synthesises notes

Both modes ensure human has sole execution responsibility. The distinction from Human-Led is that AI does not actively participate — it either exits or provides only ambient support.

### 4. Progressive Value Delivery (QUICK/FULL Modes)

Every process supports two modes:
- **QUICK**: Lightweight execution for straightforward cases
- **FULL**: Comprehensive execution when complexity emerges

Upgrade triggers are defined per-process, preventing over-engineering while ensuring thoroughness when needed.

### 5. Theory-Building Preservation

The framework explicitly preserves human theory-building (Naur's insight that software knowledge lives in developers' minds) by:
- Keeping humans substantive in tacit-heavy phases
- Using AI to *accelerate* rather than *replace* understanding
- Documenting decisions and rationale for knowledge preservation

## Framework Statistics

| Metric | Value |
|--------|-------|
| Phases | 7 |
| Processes | 28 |
| Steps | 168 |
| Escalation triggers | 197 |
| Behaviour rules files | 7 |
| Capabilities used | 8 (Elicit, Analyse, Synthesise, Transform, Validate, Decide, Generate, Preserve) |
| Collaboration patterns | 4 active (Human-Led, Partnership, AI-Led, AI-Only) |

## Practical Application

The framework provides:

1. **For AI assistants**: Clear behavioural guidance per phase - when to generate confidently, when to defer, what to escalate
2. **For developers**: Predictable AI collaboration with transparent decision points
3. **For organisations**: Auditable process execution with preserved rationale
4. **For the field**: A research-grounded alternative to ad-hoc AI integration

## Theoretical Contribution

This work bridges the gap between:
- Academic understanding of software development as theory-building
- Practical need for AI integration in development workflows
- Socio-technical systems principles of joint optimisation

The result is a framework that treats AI as a *capability* to be orchestrated rather than an *agent* to be unleashed - respecting both what AI can do well (formal, generative tasks) and what humans must retain (tacit knowledge, theory-building, critical decisions).
