import hashlib
import json
import os
import re
from typing import Dict, Iterable, Optional, Set


class ProtocolEncoder:
    def __init__(self, dict_path: Optional[str] = None):
        if dict_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.dict_path = os.path.join(base_dir, "dictionary.json")
        else:
            self.dict_path = os.path.abspath(dict_path)

        self.dictionary = self._load_dict()
        self._signature = self._compute_signature()
        display_path = self.dict_path.replace("\\", "/")
        print(f"--- PX-ENCODER: Nutze Dictionary unter: {display_path}")

    def reload_dictionary(self) -> None:
        """Reload the on-disk dictionary."""
        self.dictionary = self._load_dict()
        self._signature = self._compute_signature()

    @property
    def dictionary_signature(self) -> str:
        return self._signature

    def build_mapping_instruction(self, words: Optional[Iterable[str]] = None) -> str:
        """Return a system instruction that only contains the requested mapping entries."""
        mapping = self._select_mapping(words)
        if not mapping:
            return ""

        ordered_items = sorted(mapping.items(), key=lambda item: item[1])
        mappings = " | ".join(f"{token}={word}" for word, token in ordered_items)
        return f"PX MAP: use tokens on matching words. {mappings}"

    def _select_mapping(self, words: Optional[Iterable[str]]) -> Dict[str, str]:
        if words is None:
            return dict(self.dictionary)

        selected: Dict[str, str] = {}
        for word in words:
            token_id = self.dictionary.get(word)
            if token_id is not None:
                selected[word] = token_id
        return selected

    def _load_dict(self) -> Dict[str, str]:
        if os.path.exists(self.dict_path):
            try:
                with open(self.dict_path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    return content if isinstance(content, dict) else {}
            except Exception as e:
                print(f"--- PX-DEBUG: Fehler beim Lesen: {e}")
        return {}

    def _compute_signature(self, mapping: Optional[Dict[str, str]] = None) -> str:
        data = mapping if mapping is not None else self.dictionary
        serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha1(serialized.encode("utf-8")).hexdigest()

    def _pattern_for_word(self, word: str) -> re.Pattern:
        if re.search(r"\W", word):
            return re.compile(re.escape(word), re.IGNORECASE)
        return re.compile(rf"(?<!\w){re.escape(word)}(?!\w)", re.IGNORECASE)

    def encode(self, text: str, used_words: Optional[Set[str]] = None) -> str:
        if not text or len(self.dictionary) == 0:
            return text

        compressed = text
        original_text = text
        sorted_words = sorted(self.dictionary.keys(), key=len, reverse=True)

        for word in sorted_words:
            token_id = self.dictionary[word]
            pattern = self._pattern_for_word(word)
            if used_words is not None and pattern.search(original_text):
                used_words.add(word)
            compressed = pattern.sub(token_id, compressed)

        return compressed

