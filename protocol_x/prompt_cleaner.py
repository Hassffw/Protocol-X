"""Utilities for trimming redundant phrasing from prompts."""

import re
from typing import Iterable

FILLER_PATTERNS: Iterable[str] = (
    r"\bplease\b",
    r"\bplease,",
    r"\bkindly\b",
    r"\bkindly,",
    r"\bcould you\b",
    r"\bcan you\b",
    r"\bwould you mind\b",
    r"\bi would appreciate\b",
    r"\bare you able to\b",
    r"\bit would be great if you could\b",
    r"\bif you could\b",
    r"\bmay you\b",
    r"\bthanks\b",
    r"\bthank you\b",
)

_WHITESPACE_RE = re.compile(r"\s+")


def clean_prompt_text(text: str) -> str:
    """Strip common filler phrases while keeping the request readable."""
    if not isinstance(text, str):
        return text

    cleaned = text
    for pattern in FILLER_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)

    cleaned = _WHITESPACE_RE.sub(" ", cleaned).strip()

    # Avoid returning an empty string if we stripped everything relevant.
    return cleaned if cleaned else text.strip()

