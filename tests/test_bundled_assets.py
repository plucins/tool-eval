"""Business rules for loading and verifying the vendored offline assets."""

from __future__ import annotations

import base64
import hashlib
from xml.etree import ElementTree

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


def test_ubuntu_fonts_are_embedded_as_base64_data_uris():
    bundle = load_assets()
    # No relative font URL remains; each @font-face uses an inline data: URI.
    assert "fonts/ubuntu" not in bundle.theme_css
    assert "Montserrat" not in bundle.theme_css
    assert bundle.theme_css.count("data:font/woff2;base64,") == 8
    assert "UBUNTU FONT LICENCE Version 1.0" in bundle.font_license


def test_theme_contains_capgemini_palette_tokens():
    bundle = load_assets()
    assert "#0058ab" in bundle.theme_css.lower()
    assert "#12abdb" in bundle.theme_css.lower()


def test_official_logo_is_embedded_without_modification_or_active_content():
    bundle = load_assets()
    prefix = "data:image/svg+xml;base64,"
    assert bundle.logo_uri.startswith(prefix)
    svg = base64.b64decode(bundle.logo_uri[len(prefix):], validate=True)
    assert hashlib.sha256(svg).hexdigest() == (
        "306dda528f78702c4d16ee6c524e0f549e481d3de984d11986619cceb9ec52cb"
    )
    root = ElementTree.fromstring(svg)
    assert root.attrib["viewBox"] == "0 0 285 65"
    for element in root.iter():
        assert element.tag in {
            "{http://www.w3.org/2000/svg}svg",
            "{http://www.w3.org/2000/svg}path",
        }
        assert set(element.attrib) <= {"width", "height", "viewBox", "fill", "d"}


@pytest.mark.parametrize("asset", ["capgemini-white.svg", "fonts/UFL.txt"])
def test_required_brand_asset_checksum_entry_is_mandatory(monkeypatch, asset):
    checksums = assets_mod._load_checksums()
    del checksums[asset]
    monkeypatch.setattr(assets_mod, "_load_checksums", lambda: checksums)
    with pytest.raises(ToolEvalError) as exc:
        load_assets()
    assert exc.value.code == "PUBLISH_ASSET_MISSING"
    assert exc.value.path == asset


def test_logo_checksum_mismatch_is_detected(monkeypatch):
    checksums = assets_mod._load_checksums()
    checksums["capgemini-white.svg"] = "0" * 64
    monkeypatch.setattr(assets_mod, "_load_checksums", lambda: checksums)
    with pytest.raises(ToolEvalError) as exc:
        load_assets()
    assert exc.value.code == "PUBLISH_ASSET_CHECKSUM_MISMATCH"


def test_missing_logo_file_is_reported(monkeypatch, tmp_path):
    static = assets_mod._STATIC_DIR
    for path in static.rglob("*"):
        if path.is_file() and path.name != "capgemini-white.svg":
            destination = tmp_path / path.relative_to(static)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(path.read_bytes())
    monkeypatch.setattr(assets_mod, "_STATIC_DIR", tmp_path)
    with pytest.raises(ToolEvalError) as exc:
        load_assets()
    assert exc.value.code == "PUBLISH_ASSET_MISSING"


def test_every_shipped_font_and_logo_has_a_matching_checksum():
    checksums = assets_mod._load_checksums()
    for path in assets_mod._STATIC_DIR.rglob("*"):
        if path.suffix in {".woff2", ".svg"}:
            key = path.relative_to(assets_mod._STATIC_DIR).as_posix()
            assert hashlib.sha256(path.read_bytes()).hexdigest() == checksums[key]


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
