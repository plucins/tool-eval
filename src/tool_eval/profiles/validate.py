"""Full-profile validation: JSON Schema + all business rules (D-016).

This is the single gate a profile must pass before it can be published
(D-012) and is reused by ``profile validate`` and by the publisher. It returns
a flat list of error dicts suitable for the CLI envelope / validation-errors.json.
"""

from __future__ import annotations

from typing import Any

from tool_eval.validation import business, schema


def validate_profile(
    profile: dict[str, Any],
    *,
    require_content: bool = True,
    taxonomy_feature_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Validate a full profile. Empty list => publishable.

    ``require_content`` toggles the criterion-14 content rules (facts + both
    use-case kinds); ``taxonomy_feature_ids`` (if given) additionally enforces
    completeness - exactly one result per effective-taxonomy feature.
    """
    errors: list[dict[str, Any]] = []

    # 1. Structure/types (JSON Schema, source of truth).
    schema_errors = schema.validate("profile", profile)
    errors.extend(e.to_dict() for e in schema_errors)
    if schema_errors:
        # Business rules assume a well-formed shape; stop here if structure is broken.
        return errors

    # 2. Referential integrity + status-dependent D-009 rules.
    errors.extend(e.to_dict() for e in business.check_referential_integrity(profile))
    errors.extend(e.to_dict() for e in business.check_use_case_supporting_features(profile))
    errors.extend(e.to_dict() for e in business.validate_feature_results(profile))

    # 3. Content completeness (criterion 14).
    if require_content:
        errors.extend(e.to_dict() for e in business.check_profile_content(profile))

    # 4. Taxonomy completeness (exactly one result per feature).
    if taxonomy_feature_ids is not None:
        from tool_eval.research.merge import verify_completeness

        errors.extend(
            e.to_dict()
            for e in verify_completeness(
                profile.get("feature_results", []), taxonomy_feature_ids
            )
        )

    return errors
