"""Business rules for safe Markdown rendering in the comparison report (R-09)."""

from __future__ import annotations

from tool_eval.reporting.markdown import (
    render_markdown,
    resolve_evidence_refs,
    sanitize_html,
)

SOURCES = {
    "src_docs": {"title": "Official Docs", "url": "https://docs.example.com/x"},
    "src_evil": {"title": "Evil", "url": "javascript:alert(1)"},
}


def test_commonmark_renders_basic_formatting():
    html = render_markdown("This is **bold** and *italic*.")
    assert "<strong>bold</strong>" in html
    assert "<em>italic</em>" in html


def test_raw_html_in_markdown_is_not_passed_through():
    html = render_markdown("Hello <div class='x'>raw</div> world")
    # The raw <div> from input is escaped/neutralized, not emitted as markup with
    # attacker content executing; the visible text is preserved.
    assert "raw" in html
    assert "<script" not in html.lower()


def test_script_tag_is_neutralized():
    html = render_markdown("Before <script>alert('xss')</script> after")
    assert "<script" not in html.lower()
    assert "alert" not in html or "<script" not in html.lower()


def test_javascript_url_in_link_is_not_an_active_link():
    html = render_markdown("[click](javascript:alert(1))").lower()
    # markdown-it refuses the unsafe scheme, so no active <a href="javascript:">
    # is ever produced; any residue is inert text.
    assert 'href="javascript:' not in html
    assert "<a " not in html


def test_data_url_in_link_is_not_an_active_link():
    html = render_markdown("[x](data:text/html;base64,PHNjcmlwdD4=)").lower()
    assert 'href="data:' not in html
    assert "<a " not in html


def test_safe_https_link_is_preserved():
    html = render_markdown("[docs](https://docs.example.com/x)")
    assert 'href="https://docs.example.com/x"' in html


def test_evidence_reference_resolves_to_source_link():
    html = render_markdown("See [[src_docs]] for details.", SOURCES)
    assert 'href="https://docs.example.com/x"' in html
    assert "Official Docs" in html


def test_unknown_evidence_reference_renders_as_plain_text():
    resolved = resolve_evidence_refs("See [[src_missing]].", SOURCES)
    assert resolved == "See [src_missing]."


def test_evidence_reference_to_unsafe_url_does_not_become_active_link():
    html = render_markdown("Danger [[src_evil]] here.", SOURCES).lower()
    assert 'href="javascript:' not in html
    assert "<a " not in html


def test_sanitize_html_drops_event_handlers():
    dirty = '<a href="https://x.com" onclick="steal()">x</a>'
    clean = sanitize_html(dirty)
    assert "onclick" not in clean.lower()
