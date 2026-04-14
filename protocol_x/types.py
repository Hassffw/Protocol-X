from dataclasses import dataclass
from typing import Any, List

@dataclass
class PXAssistantMessage:
    content: str

@dataclass
class PXChoice:
    message: PXAssistantMessage

@dataclass
class PXResponse:
    content: str
    raw: Any = None

    @property
    def choices(self) -> List[PXChoice]:
        return [PXChoice(PXAssistantMessage(self.content))]
