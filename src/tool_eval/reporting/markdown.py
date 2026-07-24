"""Safe Markdown rendering for the comparison report (Increment 3, R-09).

CommonMark is rendered with raw HTML disabled (``markdown-it-py``) and the
result is sanitized with ``nh3`` as defense in depth, so no profile or source
data can inject markup or execute as code. Only ``http`` / ``https`` / ``mailto``
and in-document anchors survive as links; everything else (``javascript:``,
``data:``, ...) is stripped. Evidence references of the form ``[[src_id]]`` are
resolved to safe links against the profile's source registry before rendering.
"""

from __future__ import annotations

import re
from typing import Any

import nh3
from markdown_it import MarkdownIt

# Tags we allow in rendered descriptions/rationales. No script/style/iframe/etc.
_ALLOWED_TAGS: set[str] = {
    "p", "br", "hr", "span", "div",
    "strong", "em", "b", "i", "u", "code", "pre", "blockquote",
    "ul", "ol", "li", "dl", "dt", "dd",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "a", "table", "thead", "tbody", "tr", "th", "td",
}
_ALLOWED_ATTRS: dict[str, set[str]] = {
    "a": {"href", "title"},
    "span": {"class"},
    "div": {"class"},
    "code": {"class"},
    "th": {"scope"},
}
_ALLOWED_URL_SCHEMES: set[str] = {"http", "https", "mailto"}

_EVIDENCE_REF = re.compile(r"\[\[([a-z][a-z0-9_]*)\]\]")

_MD = MarkdownIt("commonmark", {"html": False, "linkify": False})


def sanitize_html(html: str) -> str:
    """Sanitize an HTML fragment: drop unsafe tags/attrs and unsafe URL schemes."""
    return nh3.clean(
        html,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRS,
        url_schemes=_ALLOWED_URL_SCHEMES,
        link_rel="noopener noreferrer nofollow",
        strip_comments=True,
    )


def resolve_evidence_refs(text: str, sources_by_id: dict[str, dict[str, Any]]) -> str:
    """Replace ``[[source_id]]`` tokens with a Markdown link to the source URL.

    Unknown ids render as plain ``[source_id]`` text. URLs are re-checked at
    sanitization time, so an unsafe source URL cannot become an active link.
    """

    def _replace(match: "re.Match[str]") -> str:
        sid = match.group(1)
        source = sources_by_id.get(sid)
        if source is None:
            return f"[{sid}]"
        title = str(source.get("title", sid)).replace("]", " ").replace("[", " ")
        url = str(source.get("url", ""))
        return f"[{title}]({url})"

    return _EVIDENCE_REF.sub(_replace, text)


def render_markdown(text: str, sources_by_id: dict[str, dict[str, Any]] | None = None) -> str:
    """Render CommonMark to a sanitized HTML fragment.

    Raw HTML in the input is not passed through (``html=False``); evidence
    references are resolved first when a source registry is supplied.
    """
    if not text:
        return ""
    if sources_by_id:
        text = resolve_evidence_refs(text, sources_by_id)
    rendered = _MD.render(text)
    return sanitize_html(rendered)
