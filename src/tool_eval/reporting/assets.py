"""Load and verify the vendored, offline UI assets (D-013/D-014, R-10).

Bootstrap, the Capgemini theme, the vanilla JS, and the Montserrat fonts are
bundled under ``static/`` and pinned by SHA-256 in ``static/checksums.json``.
:func:`load_assets` reads them, verifies every checksum (tamper detection), and
returns CSS/JS ready to inline plus the fonts embedded as base64 ``data:`` URIs -
so the final report references no CDN and no external file (self-contained HTML).
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from tool_eval.errors import ErrorFamily, ToolEvalError

_STATIC_DIR = Path(__file__).parent / "static"
_CHECKSUMS = _STATIC_DIR / "checksums.json"

_FONT_URL_RE = re.compile(r'url\(\s*["\']?(fonts/[A-Za-z0-9_.-]+\.woff2)["\']?\s*\)')


@dataclass(frozen=True)
class BundledAssets:
    """Inline-ready UI assets for the self-contained report."""

    bootstrap_css: str
    theme_css: str
    app_js: str
    bootstrap_js: str


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_verified(rel_path: str, expected: str) -> bytes:
    path = _STATIC_DIR / rel_path
    if not path.is_file():
        raise ToolEvalError(
            code=f"{ErrorFamily.PUBLISH}_ASSET_MISSING",
            message=f"Vendored asset not found: {rel_path}",
            path=str(path),
        )
    data = path.read_bytes()
    actual = _sha256(data)
    if actual != expected:
        raise ToolEvalError(
            code=f"{ErrorFamily.PUBLISH}_ASSET_CHECKSUM_MISMATCH",
            message=(
                f"Checksum mismatch for {rel_path}: expected {expected}, got {actual}. "
                "The vendored asset may be corrupted or tampered with."
            ),
            path=str(path),
        )
    return data


def _load_checksums() -> dict[str, str]:
    if not _CHECKSUMS.is_file():
        raise ToolEvalError(
            code=f"{ErrorFamily.PUBLISH}_ASSET_MISSING",
            message=f"Asset checksum manifest not found: {_CHECKSUMS}",
            path=str(_CHECKSUMS),
        )
    return json.loads(_CHECKSUMS.read_text(encoding="utf-8"))


def _embed_fonts(theme_css: str, checksums: dict[str, str]) -> str:
    """Replace ``url("fonts/*.woff2")`` in the theme with base64 data URIs."""

    def _replace(match: "re.Match[str]") -> str:
        rel = match.group(1)
        expected = checksums.get(rel)
        if expected is None:
            raise ToolEvalError(
                code=f"{ErrorFamily.PUBLISH}_ASSET_MISSING",
                message=f"Font {rel!r} referenced by theme has no checksum entry.",
                path=rel,
            )
        data = _read_verified(rel, expected)
        b64 = base64.b64encode(data).decode("ascii")
        return f'url("data:font/woff2;base64,{b64}")'

    return _FONT_URL_RE.sub(_replace, theme_css)


def load_assets() -> BundledAssets:
    """Read + checksum-verify every bundled asset and inline the fonts."""
    checksums = _load_checksums()

    def text(rel: str) -> str:
        return _read_verified(rel, checksums[rel]).decode("utf-8")

    theme_css = _embed_fonts(text("theme-capgemini.css"), checksums)
    return BundledAssets(
        bootstrap_css=text("bootstrap.min.css"),
        theme_css=theme_css,
        app_js=text("app.js"),
        bootstrap_js=text("bootstrap.bundle.min.js"),
    )
