"""Structured error model shared by every tool_eval command.

Error codes are grouped into families per the implementation plan (D-011):
CONFIG_*, INPUT_*, HARNESS_*, RESEARCH_*, VALIDATION_*, BUDGET_*, PUBLISH_*.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class ErrorFamily:
    CONFIG = "CONFIG"
    INPUT = "INPUT"
    HARNESS = "HARNESS"
    RESEARCH = "RESEARCH"
    VALIDATION = "VALIDATION"
    BUDGET = "BUDGET"
    PUBLISH = "PUBLISH"

    ALL = (CONFIG, INPUT, HARNESS, RESEARCH, VALIDATION, BUDGET, PUBLISH)


@dataclass
class ToolEvalError(Exception):
    """A structured error record.

    `code` must be `<FAMILY>_<REASON>`, e.g. `CONFIG_INVALID_YAML`.
    `retryable` mirrors D-011: technical errors are retryable (bounded),
    structural/business-rule errors go through the repair loop instead.
    """

    code: str
    message: str
    retryable: bool = False
    feature_id: str | None = None
    path: str | None = None

    def __post_init__(self) -> None:
        Exception.__init__(self, self.message)
        family = self.code.split("_", 1)[0]
        if family not in ErrorFamily.ALL:
            raise ValueError(
                f"Unknown error family {family!r} in code {self.code!r}; "
                f"expected one of {ErrorFamily.ALL}"
            )

    def to_dict(self) -> dict[str, Any]:
        record: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
            "retryable": self.retryable,
        }
        if self.feature_id is not None:
            record["feature_id"] = self.feature_id
        if self.path is not None:
            record["path"] = self.path
        return record
