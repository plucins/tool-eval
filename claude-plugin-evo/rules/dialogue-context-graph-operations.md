---
paths:
  - ".dialogue/context-graph/**/*"
---

# Context Graph Operations

**Use the context-graph scripts for all graph operations.**

Do NOT manually edit node or edge YAML files in `.dialogue/context-graph/`.

## Available Scripts

Located in `.dialogue/context-graph/scripts/`:

| Script | Purpose |
|--------|---------|
| `graph-locate.sh` | Find nodes by ID or pattern |
| `graph-discover.sh` | Discover related nodes and edges |
| `graph-trace.sh` | Trace relationships between artifacts |
| `graph-invalidate.sh` | Mark nodes as invalidated |
| `bootstrap-node.sh` | Create a new node |
| `bootstrap-concept.sh` | Bootstrap a concept node |
| `bootstrap-logs.sh` | Bootstrap log entries into graph |
| `bootstrap-all-concepts.sh` | Bulk bootstrap concepts |

## Required Behaviour

```
To find a node:
CORRECT: Run .dialogue/context-graph/scripts/graph-locate.sh <id>
WRONG: Manually search through nodes/artifacts/*.yaml

To trace relationships:
CORRECT: Run .dialogue/context-graph/scripts/graph-trace.sh <id>
WRONG: Manually traverse edge files

To create a node:
CORRECT: Run .dialogue/context-graph/scripts/bootstrap-node.sh
WRONG: Manually create YAML file in nodes/
```

## Why Scripts

- Scripts maintain referential integrity between nodes and edges
- Scripts generate correct edge relationships
- Scripts validate node schema
- Manual edits risk orphaned edges or broken references

## Exceptions

MAY edit directly only for:
- Emergency repair when scripts are broken
- Schema evolution requiring bulk updates
- Explicit user instruction

When bypassing, state: "Editing context-graph directly because [reason]."
