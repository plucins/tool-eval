"""Deterministic assembly of ``description.md`` from profile-sections config.

The *semantic* prose is produced by the LLM (D-007/D-016); Python does not
invent content. This module's job is the deterministic part: take the
LLM-provided text per section, enforce that every *required* section from
``profile-sections.yaml`` is present and non-empty, reject unknown sections
(additionalProperties:false spirit, D-016), and emit the sections in the
configured order with stable Markdown headers.

Rendering/sanitisation of this Markdown into HTML happens in Increment 3
(nh3 + markdown-it); here we only assemble trusted-structure Markdown text.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DescriptionError:
    code: str
    message: str
    section_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        record = {"code": self.code, "message": self.message}
        if self.section_id is not None:
            record["section_id"] = self.section_id
        return record


def _sections_from_config(sections_config: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not sections_config:
        raise ValueError("profile-sections config declares no sections")
    return sections_config


def assemble_description(
    sections_config: list[dict[str, Any]],
    section_texts: dict[str, str],
) -> tuple[str, list[DescriptionError]]:
    """Assemble description.md; return (markdown, errors).

    ``sections_config`` is the ``sections`` list from profile-sections.yaml.
    ``section_texts`` maps section id -> Markdown body (LLM-provided).
    """
    sections = _sections_from_config(sections_config)
    known_ids = {s["id"] for s in sections}
    errors: list[DescriptionError] = []

    for unknown in sorted(set(section_texts) - known_ids):
        errors.append(
            DescriptionError(
                code="VALIDATION_UNKNOWN_SECTION",
                message=f"description text supplied for unknown section {unknown!r}",
                section_id=unknown,
            )
        )

    for section in sections:
        sid = section["id"]
        text = section_texts.get(sid, "")
        if section.get("required") and (not isinstance(text, str) or not text.strip()):
            errors.append(
                DescriptionError(
                    code="VALIDATION_MISSING_REQUIRED_SECTION",
                    message=f"required description section {sid!r} is missing or empty",
                    section_id=sid,
                )
            )

    parts: list[str] = []
    for section in sections:
        sid = section["id"]
        text = section_texts.get(sid, "")
        if isinstance(text, str) and text.strip():
            parts.append(f"## {section['title']}\n\n{text.strip()}\n")

    return "\n".join(parts), errors
