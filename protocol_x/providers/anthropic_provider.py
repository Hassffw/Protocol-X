from __future__ import annotations

from typing import Any, Dict, List

try:
    from anthropic import Anthropic
except ImportError:  # pragma: no cover
    Anthropic = Any  # type: ignore

from ..types import PXResponse
from .base import ChatProvider

Message = Dict[str, Any]


class AnthropicChatProvider(ChatProvider):
    """Adapter für Anthropic Claude (Messages API)."""

    def __init__(self, client: Anthropic):
        self.client = client

    def create_chat_completion(self, messages: List[Message], **kwargs: Any) -> PXResponse:
        converted: List[Message] = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "system":
                converted.append({"role": "assistant", "content": content})
            else:
                converted.append({"role": role, "content": content})

        response = self.client.messages.create(messages=converted, **kwargs)
        parts: List[str] = []
        for block in getattr(response, "content", []) or []:
            text = getattr(block, "text", None)
            if text:
                parts.append(text)
        content = " ".join(parts) if parts else ""
        return PXResponse(content=content, raw=response)
