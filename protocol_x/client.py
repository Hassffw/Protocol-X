import os
from typing import Any, Dict, List, Optional

from .decoder import ProtocolDecoder
from .encoder import ProtocolEncoder
from .optimizer import PXOptimizer
from .providers import (
    AnthropicChatProvider,
    ChatProvider,
    DeepSeekChatProvider,
    OpenAIChatProvider,
)
from .types import PXResponse

Message = Dict[str, Any]

class PXClient:
    """Wrapper, der Eingaben/Ausgaben per PX-Dictionary komprimiert."""

    def __init__(self, provider: ChatProvider, dict_path: Optional[str] = None):
        self.provider = provider

        if dict_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            dict_path = os.path.join(base_dir, "dictionary.json")

        self.dict_path = dict_path

        self.encoder = ProtocolEncoder(self.dict_path)
        self.decoder = ProtocolDecoder(self.dict_path)
        self.optimizer = PXOptimizer(self.dict_path)

        self._dict_signature = self.encoder.dictionary_signature
        self._mapping_instruction = self.encoder.build_mapping_instruction()
        self._mapping_sent_signature: Optional[str] = None

        self.chat = self._Chat(self)

    # Factories -----------------------------------------------------------
    @classmethod
    def from_openai(
        cls,
        api_key: Optional[str] = None,
        *,
        client: Optional[Any] = None,
        dict_path: Optional[str] = None,
        **client_kwargs: Any,
    ) -> "PXClient":
        """Baut einen Client auf Basis des offiziellen OpenAI SDK."""
        if client is None:
            from openai import OpenAI

            client = OpenAI(api_key=api_key, **client_kwargs)
        provider = OpenAIChatProvider(client)
        return cls(provider, dict_path=dict_path)

    @classmethod
    def from_anthropic(
        cls,
        api_key: Optional[str] = None,
        *,
        client: Optional[Any] = None,
        dict_path: Optional[str] = None,
        **client_kwargs: Any,
    ) -> "PXClient":
        """Baut einen Client für Anthropic Claude."""
        if client is None:
            from anthropic import Anthropic

            client = Anthropic(api_key=api_key, **client_kwargs)
        provider = AnthropicChatProvider(client)
        return cls(provider, dict_path=dict_path)

    @classmethod
    def from_deepseek(
        cls,
        api_key: Optional[str] = None,
        *,
        client: Optional[Any] = None,
        dict_path: Optional[str] = None,
        **client_kwargs: Any,
    ) -> "PXClient":
        """Baut einen Client für DeepSeek (OpenAI-kompatible APIs)."""
        if client is None:
            import deepseek

            client = deepseek.DeepSeek(api_key=api_key, **client_kwargs)
        provider = DeepSeekChatProvider(client)
        return cls(provider, dict_path=dict_path)

    # Internals -----------------------------------------------------------
    def _refresh_dictionary(self) -> None:
        self.encoder.reload_dictionary()
        self.decoder.reload_dictionary()
        self._dict_signature = self.encoder.dictionary_signature
        self._mapping_instruction = self.encoder.build_mapping_instruction()
        self._mapping_sent_signature = None

    class _Chat:
        def __init__(self, parent: "PXClient"):
            self.completions = parent._Completions(parent)

    class _Completions:
        def __init__(self, parent: "PXClient"):
            self.parent = parent

        def create(self, **kwargs: Any) -> PXResponse:
            messages: List[Message] = [dict(m) for m in kwargs.get("messages", [])]

            orig_len = sum(
                len(m["content"])
                for m in messages
                if m.get("role") == "user" and m.get("content")
            )

            additions_total = []
            for msg in messages:
                if msg.get("role") == "user" and msg.get("content"):
                    additions = self.parent.optimizer.learn_from_text(msg["content"])
                    if additions:
                        additions_total.extend(additions)

            if additions_total:
                self.parent._refresh_dictionary()

            if (
                self.parent._mapping_instruction
                and self.parent._mapping_sent_signature != self.parent._dict_signature
            ):
                messages.insert(
                    0,
                    {
                        "role": "system",
                        "content": self.parent._mapping_instruction,
                    },
                )
                self.parent._mapping_sent_signature = self.parent._dict_signature

            encoded_messages: List[Message] = []
            for msg in messages:
                msg_copy = dict(msg)
                if msg_copy.get("content") and msg_copy.get("role") in {"user", "assistant"}:
                    msg_copy["content"] = self.parent.encoder.encode(msg_copy["content"])
                encoded_messages.append(msg_copy)

            comp_len = sum(
                len(m["content"])
                for m in encoded_messages
                if m.get("role") == "user" and m.get("content")
            )

            new_kwargs = dict(kwargs)
            new_kwargs["messages"] = encoded_messages

            provider_response = self.parent.provider.create_chat_completion(
                **new_kwargs
            )

            provider_response.content = self.parent.decoder.decode(provider_response.content)

            savings = orig_len - comp_len
            percent = round((savings / orig_len) * 100, 1) if orig_len else 0
            print(f"⚡ PX-Stats: {orig_len} -> {comp_len} chars (Saved {percent}%)")

            return provider_response
