"""YAML configuration loading, hashing, and revision extraction.

Per D-008/D-014: configuration is manually edited YAML, loaded exclusively
through `yaml.safe_load`. Per D-016, taxonomy and template revisions are
integers; this module also computes a content hash per file so a run can
freeze the exact configuration state it started with (D-011).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from tool_eval.errors import ErrorFamily, ToolEvalError

# Config files that must exist under <root>/config/ (Sec 3.3).
# `revision` is mandatory for files whose changes can invalidate resume/profiles;
# the others are plain settings and do not carry a revision.
REQUIRED_CONFIG_FILES: dict[str, bool] = {
    "feature-taxonomy.yaml": True,
    "source-policies.yaml": True,
    "profile-sections.yaml": True,
    "additional-fact-sections.yaml": True,
    "freshness.yaml": False,
    "runtime.yaml": False,
    "presentation.yaml": False,
}


@dataclass(frozen=True)
class ConfigFile:
    name: str
    path: Path
    data: dict[str, Any]
    sha256: str
    revision: int | None


@dataclass(frozen=True)
class ConfigBundle:
    root: Path
    files: dict[str, ConfigFile]

    def revisions(self) -> dict[str, int]:
        return {
            name: cf.revision
            for name, cf in self.files.items()
            if cf.revision is not None
        }

    def hashes(self) -> dict[str, str]:
        return {name: cf.sha256 for name, cf in self.files.items()}


def _load_yaml_file(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise ToolEvalError(
            code=f"{ErrorFamily.CONFIG}_MISSING_FILE",
            message=f"Required configuration file not found: {path}",
            path=str(path),
        ) from exc

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ToolEvalError(
            code=f"{ErrorFamily.CONFIG}_INVALID_YAML",
            message=f"Failed to parse YAML in {path}: {exc}",
            path=str(path),
        ) from exc

    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ToolEvalError(
            code=f"{ErrorFamily.CONFIG}_INVALID_SHAPE",
            message=f"Configuration file {path} must contain a YAML mapping at the top level",
            path=str(path),
        )
    return data


def load_config_bundle(root: Path) -> ConfigBundle:
    """Load, hash, and validate every required config file under <root>/config/."""
    config_dir = root / "config"
    if not config_dir.is_dir():
        raise ToolEvalError(
            code=f"{ErrorFamily.CONFIG}_MISSING_DIRECTORY",
            message=f"Configuration directory not found: {config_dir}",
            path=str(config_dir),
        )

    files: dict[str, ConfigFile] = {}
    for filename, revision_required in REQUIRED_CONFIG_FILES.items():
        path = config_dir / filename
        raw_bytes = path.read_bytes() if path.is_file() else b""
        data = _load_yaml_file(path)

        revision = data.get("revision")
        if revision_required:
            if not isinstance(revision, int):
                raise ToolEvalError(
                    code=f"{ErrorFamily.CONFIG}_MISSING_REVISION",
                    message=(
                        f"{filename} must declare an integer top-level 'revision' field"
                    ),
                    path=str(path),
                )

        files[filename] = ConfigFile(
            name=filename,
            path=path,
            data=data,
            sha256=hashlib.sha256(raw_bytes).hexdigest(),
            revision=revision if isinstance(revision, int) else None,
        )

    return ConfigBundle(root=root, files=files)
