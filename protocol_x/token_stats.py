from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

try:
    import tiktoken  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    tiktoken = None


Message = Dict[str, Any]


@dataclass
class TokenMeasurement:
    characters: int
    tokens: Optional[int]


class TokenCounter:
    """Best-effort token estimator with OpenAI tiktoken support."""

    def __init__(self, model_hint: Optional[str] = None):
        self.model_hint = model_hint
        self._encoding = self._resolve_encoding(model_hint)

    @property
    def available(self) -> bool:
        return self._encoding is not None

    def count_messages(self, messages: Iterable[Message]) -> TokenMeasurement:
        total_chars = 0
        total_tokens: Optional[int]
        token_sum = 0
        has_encoding = self._encoding is not None

        for msg in messages:
            content = msg.get("content")
            if not content:
                continue
            text = str(content)
            total_chars += len(text)
            if has_encoding:
                token_sum += len(self._encoding.encode(text))

        total_tokens = token_sum if has_encoding else None
        return TokenMeasurement(characters=total_chars, tokens=total_tokens)

    def _resolve_encoding(self, model_hint: Optional[str]):
        if tiktoken is None:
            return None

        if model_hint:
            try:
                return tiktoken.encoding_for_model(model_hint)
            except KeyError:
                pass

        try:
            return tiktoken.get_encoding("cl100k_base")
        except Exception:
            return None
