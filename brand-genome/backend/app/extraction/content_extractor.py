"""
Content extraction (Section 20 of the architecture doc).

trafilatura first (tuned for article/body-copy extraction, handles boilerplate
removal well). Falls back to a plain BeautifulSoup text dump only when
trafilatura finds nothing usable -- e.g. non-article pages (product grids,
nav-heavy landing pages) where trafilatura's heuristics correctly decide
"there's no article here" but there's still real page text worth keeping.
Never fabricates content; an empty/near-empty result is a legitimate outcome,
not an error to paper over.
"""

import trafilatura
from bs4 import BeautifulSoup

# Below this many characters, extracted_text is treated as "thin" -- likely a
# JS-rendered shell that plain HTTP couldn't see through. Used by
# CrawlerRouter to decide whether a browser-render fallback is worth trying.
MIN_CONTENT_CHARS = 200


def extract_content(html: str, url: str) -> str:
    text = trafilatura.extract(
        html,
        url=url,
        include_comments=False,
        include_tables=True,
        favor_recall=True,
    )
    if text and len(text.strip()) >= 40:
        return text.strip()

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "template"]):
        tag.decompose()
    fallback_text = " ".join(soup.get_text(separator=" ").split())
    return fallback_text.strip()


def is_thin_content(text: str) -> bool:
    return len(text.strip()) < MIN_CONTENT_CHARS