"""JSON Schema loading and validation (D-016: JSON Schema is the source of truth).

All schemas live under ``schemas/`` and reference one another by ``$id``
(e.g. profile.json embeds feature records and sources). We load every schema
into a :mod:`referencing` registry once, so cross-file ``$ref`` resolves
deterministically and offline, with no network access.

JSON Schema validates *structure, types, and simple dependencies* only; the
status-dependent rules and referential integrity live in
:mod:`tool_eval.validation.business` (D-016).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from tool_eval.errors import ErrorFamily, ToolEvalError

_SCHEMA_DIR = Path(__file__).parent / "schemas"

# Logical name -> schema file. `name` is what callers pass to `validate`.
SCHEMA_FILES: dict[str, str] = {
    "run": "run.schema.json",
    "task": "task.schema.json",
    "source": "source.schema.json",
    "feature-result": "feature-result.schema.json",
    "candidate": "candidate.schema.json",
    "candidates": "candidates.schema.json",
    "unresolved-issues": "unresolved-issues.schema.json",
    "subagent-result": "subagent-result.schema.json",
    "additional-fact": "additional-fact.schema.json",
    "use-case": "use-case.schema.json",
    "release-history-entry": "release-history-entry.schema.json",
    "profile": "profile.schema.json",
}


@dataclass(frozen=True)
class SchemaError:
    """A single JSON Schema violation, rendered for the CLI error envelope."""

    path: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {"code": "VALIDATION_SCHEMA", "message": self.message, "path": self.path}


def _load_all_schemas() -> dict[str, dict[str, Any]]:
    schemas: dict[str, dict[str, Any]] = {}
    for name, filename in SCHEMA_FILES.items():
        path = _SCHEMA_DIR / filename
        if not path.is_file():
            raise ToolEvalError(
                code=f"{ErrorFamily.VALIDATION}_SCHEMA_MISSING",
                message=f"Schema file not found: {path}",
                path=str(path),
            )
        schemas[name] = json.loads(path.read_text(encoding="utf-8"))
    return schemas


@lru_cache(maxsize=1)
def _registry() -> Registry:
    """Build a referencing registry keyed by each schema's ``$id`` (cached)."""
    resources = []
    for schema in _load_all_schemas().values():
        resources.append((schema["$id"], Resource.from_contents(schema)))
    return Registry().with_resources(resources)


@lru_cache(maxsize=None)
def _validator_for(name: str) -> Draft202012Validator:
    schemas = _load_all_schemas()
    if name not in schemas:
        raise ToolEvalError(
            code=f"{ErrorFamily.VALIDATION}_SCHEMA_UNKNOWN",
            message=f"Unknown schema name {name!r}; known: {sorted(schemas)}",
        )
    return Draft202012Validator(schemas[name], registry=_registry())


def _format_path(error_path: Any) -> str:
    parts = [str(p) for p in error_path]
    return "$" + "".join(f"[{p!r}]" if isinstance(p, str) else f"[{p}]" for p in parts)


def validate(name: str, instance: Any) -> list[SchemaError]:
    """Validate ``instance`` against the named schema; return all violations.

    An empty list means the instance is schema-valid. This never raises for a
    data problem - callers decide how to surface a non-empty list.
    """
    validator = _validator_for(name)
    errors: list[SchemaError] = []
    for err in sorted(validator.iter_errors(instance), key=lambda e: list(e.path)):
        errors.append(SchemaError(path=_format_path(err.path), message=err.message))
    return errors


def is_valid(name: str, instance: Any) -> bool:
    return not validate(name, instance)
