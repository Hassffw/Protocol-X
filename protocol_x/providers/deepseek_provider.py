from __future__ import annotations

from typing import Any, Dict, List

from ..types import PXResponse
from .base import ChatProvider

Message = Dict[str, Any]

class DeepSeekChatProvider(ChatProvider):
    """Adapter für DeepSeek APIs, die das OpenAI-Schema spiegeln."""

    def __init__(self, client: Any):
        self.client = client

    def create_chat_completion(self, messages: List[Message], **kwargs: Any) -> PXResponse:
        response = self.client.chat.completions.create(messages=messages, **kwargs)
        content = response.choices[0].message.content
        return PXResponse(content=content, raw=response)
