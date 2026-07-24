"""Business rules for loading and verifying the vendored offline assets."""

from __future__ import annotations

import base64

import pytest

from tool_eval.errors import ToolEvalError
from tool_eval.reporting import assets as assets_mod
from tool_eval.reporting.assets import load_assets


def test_assets_load_from_package_data():
    bundle = load_assets()
    assert "bootstrap" in bundle.bootstrap_css.lower()
    assert "--cg-blue" in bundle.theme_css
    assert bundle.bootstrap_js
    assert bundle.app_js


def test_montserrat_fonts_are_embedded_as_base64_data_uris():
    bundle = load_assets()
    # No relative font URL remains; each @font-face uses an inline data: URI.
    assert "fonts/montserrat" not in bundle.theme_css
    assert "data:font/woff2;base64," in bundle.theme_css


def test_theme_contains_capgemini_palette_tokens():
    bundle = load_assets()
    assert "#0070ad" in bundle.theme_css.lower()
    assert "#12abdb" in bundle.theme_css.lower()


def test_asset_checksum_mismatch_is_detected(monkeypatch):
    real = assets_mod._load_checksums()
    tampered = dict(real)
    tampered["app.js"] = "0" * 64
    monkeypatch.setattr(assets_mod, "_load_checksums", lambda: tampered)
    with pytest.raises(ToolEvalError) as exc:
        load_assets()
    assert exc.value.code == "PUBLISH_ASSET_CHECKSUM_MISMATCH"


def test_missing_asset_is_reported(monkeypatch):
    real = assets_mod._load_checksums()
    extra = dict(real)
    extra["does-not-exist.css"] = "a" * 64
    monkeypatch.setattr(assets_mod, "_load_checksums", lambda: extra)
    # Loading still works for present assets; the missing entry only fails if read.
    with pytest.raises(ToolEvalError) as exc:
        assets_mod._read_verified("does-not-exist.css", "a" * 64)
    assert exc.value.code == "PUBLISH_ASSET_MISSING"
