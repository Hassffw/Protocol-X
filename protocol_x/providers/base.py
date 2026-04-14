from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ..types import PXResponse

Message = Dict[str, Any]

class ChatProvider(ABC):
    """Abstrakte Schnittstelle für Chat-API-Anbieter."""

    @abstractmethod
    def create_chat_completion(self, messages: List[Message], **kwargs: Any) -> PXResponse:
        """Sendet eine Chat-Anfrage und gibt die Antwort zurück."""
        raise NotImplementedError
