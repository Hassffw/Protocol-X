import hashlib
import json
import os
from typing import Any, Dict, List, Optional, Set

from .decoder import ProtocolDecoder
from .encoder import ProtocolEncoder
from .optimizer import PXOptimizer
from .prompt_cleaner import clean_prompt_text
from .providers import (
    AnthropicChatProvider,
    ChatProvider,
    DeepSeekChatProvider,
    OpenAIChatProvider,
)
from .token_stats import TokenCounter
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

        self._cache: Dict[str, PXResponse] = {}

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
        """Baut einen Client für DeepSeek über das OpenAI SDK."""
        if client is None:
            from openai import OpenAI
            
            # DeepSeek ist OpenAI-kompatibel. Wir setzen einfach die base_url.
            client = OpenAI(
                api_key=api_key, 
                base_url="https://api.deepseek.com", 
                **client_kwargs
            )
        
        # Jetzt funktioniert dein DeepSeekChatProvider, 
        # weil er self.client.chat.completions.create aufrufen kann.
        provider = DeepSeekChatProvider(client)
        return cls(provider, dict_path=dict_path)

    # Internals -----------------------------------------------------------
    def _refresh_dictionary(self) -> None:
        self.encoder.reload_dictionary()
        self.decoder.reload_dictionary()

    def clear_cache(self) -> None:
        """Drop all cached provider responses."""
        self._cache.clear()

    @staticmethod
    def _normalise_for_cache(value: Any) -> Any:
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, dict):
            return {str(k): PXClient._normalise_for_cache(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
        if isinstance(value, (list, tuple)):
            return [PXClient._normalise_for_cache(v) for v in value]
        return str(value)

    def _build_cache_key(self, payload: Dict[str, Any]) -> Optional[str]:
        if payload.get('stream'):
            return None
        normalised = {k: self._normalise_for_cache(v) for k, v in payload.items()}
        wrapper = {
            'dict': self.encoder.dictionary_signature,
            'payload': normalised,
        }
        try:
            serialised = json.dumps(wrapper, sort_keys=True, ensure_ascii=False)
        except TypeError:
            return None
        return hashlib.sha1(serialised.encode('utf-8')).hexdigest()

    class _Chat:
        def __init__(self, parent: "PXClient"):
            self.completions = parent._Completions(parent)

    class _Completions:
        def __init__(self, parent: "PXClient"):
            self.parent = parent

        def create(self, **kwargs: Any) -> PXResponse:
            raw_messages = kwargs.get("messages", [])
            messages: List[Message] = [dict(m) for m in raw_messages]

            additions_total = []
            cleaned_messages: List[Message] = []

            for msg in messages:
                msg_copy = dict(msg)
                content = msg_copy.get("content")
                role = msg_copy.get("role")

                if isinstance(content, str) and role == "user":
                    cleaned = clean_prompt_text(content)
                    msg_copy["content"] = cleaned if cleaned else content.strip()

                    if msg_copy["content"]:
                        additions = self.parent.optimizer.learn_from_text(msg_copy["content"])
                        if additions:
                            additions_total.extend(additions)

                cleaned_messages.append(msg_copy)

            messages = cleaned_messages

            if additions_total:
                self.parent._refresh_dictionary()

            pre_encode_messages: List[Message] = [dict(m) for m in messages]
            encoded_messages: List[Message] = []
            used_words: Set[str] = set()

            for msg in pre_encode_messages:
                msg_copy = dict(msg)
                content = msg_copy.get("content")
                if isinstance(content, str) and msg_copy.get("role") in {"user", "assistant"}:
                    msg_copy["content"] = self.parent.encoder.encode(content, used_words)
                encoded_messages.append(msg_copy)

            mapping_instruction = self.parent.encoder.build_mapping_instruction(used_words)

            counter = TokenCounter(kwargs.get("model"))
            pre_user_stats = counter.count_messages(
                msg for msg in pre_encode_messages if msg.get("role") == "user"
            )
            post_user_stats = counter.count_messages(
                msg for msg in encoded_messages if msg.get("role") == "user"
            )

            pre_total_messages: List[Message] = []
            post_total_messages: List[Message] = []
            if mapping_instruction:
                mapping_msg = {"role": "system", "content": mapping_instruction}
                pre_total_messages.append(mapping_msg)
                post_total_messages.append(mapping_msg)

            for original, encoded in zip(pre_encode_messages, encoded_messages):
                pre_total_messages.append(original)
                post_total_messages.append(encoded)

            pre_total_stats = counter.count_messages(pre_total_messages)
            post_total_stats = counter.count_messages(post_total_messages)

            final_messages = encoded_messages
            if mapping_instruction:
                final_messages = [{"role": "system", "content": mapping_instruction}] + encoded_messages

            new_kwargs = dict(kwargs)
            new_kwargs["messages"] = final_messages

            cache_key = self.parent._build_cache_key(new_kwargs)
            if cache_key and cache_key in self.parent._cache:
                cached_response = self.parent._cache[cache_key]
                print("[PX] cache hit: reused response")
                self._report_savings(
                    pre_user_stats,
                    post_user_stats,
                    pre_total_stats,
                    post_total_stats,
                )
                return PXResponse(content=cached_response.content, raw=cached_response.raw)

            provider_response = self.parent.provider.create_chat_completion(
                **new_kwargs
            )

            provider_response.content = self.parent.decoder.decode(provider_response.content)

            if cache_key:
                self.parent._cache[cache_key] = PXResponse(
                    content=provider_response.content,
                    raw=provider_response.raw,
                )

            self._report_savings(
                pre_user_stats,
                post_user_stats,
                pre_total_stats,
                post_total_stats,
            )

            return provider_response
        @staticmethod
        def _report_savings(
            pre_user_stats,
            post_user_stats,
            pre_total_stats,
            post_total_stats,
        ) -> None:
            def _print(label: str, before_chars: int, after_chars: int, before_tokens, after_tokens) -> None:
                if before_tokens is not None and after_tokens is not None:
                    diff = before_tokens - after_tokens
                    percent = round((diff / before_tokens) * 100, 1) if before_tokens else 0
                    print(
                        f"[PX] {label}: {before_tokens} -> {after_tokens} tokens (saved {diff} | {percent}%)"
                    )
                else:
                    diff = before_chars - after_chars
                    percent = round((diff / before_chars) * 100, 1) if before_chars else 0
                    print(
                        f"[PX] {label}: {before_chars} -> {after_chars} chars (saved {diff} | {percent}%)"
                    )

            _print(
                "User content",
                pre_user_stats.characters,
                post_user_stats.characters,
                pre_user_stats.tokens,
                post_user_stats.tokens,
            )

            _print(
                "Total payload",
                pre_total_stats.characters,
                post_total_stats.characters,
                pre_total_stats.tokens,
                post_total_stats.tokens,
            )
