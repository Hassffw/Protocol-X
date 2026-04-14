import json
import os
import re
import string
from collections import Counter


class PXOptimizer:
    def __init__(self, dict_path=None):
        if dict_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.dict_path = os.path.join(base_dir, "dictionary.json")
        else:
            self.dict_path = os.path.abspath(dict_path)

        display_path = self.dict_path.replace("\\", "/")
        print(f"--- PX-OPTIMIZER: Nutze Dictionary unter: {display_path}")

    def _ensure_dict_file(self):
        if not os.path.exists(self.dict_path):
            with open(self.dict_path, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

    def _load_dictionary(self):
        self._ensure_dict_file()
        with open(self.dict_path, "r", encoding="utf-8") as f:
            content = json.load(f)
            return content if isinstance(content, dict) else {}

    def _save_dictionary(self, dictionary):
        with open(self.dict_path, "w", encoding="utf-8") as f:
            json.dump(dictionary, f, indent=2, ensure_ascii=False)

    def _index_to_token(self, index):
        alphabet = string.ascii_uppercase
        base = len(alphabet)
        chars = []
        n = index
        while True:
            n, remainder = divmod(n, base)
            chars.append(alphabet[remainder])
            if n == 0:
                break
            n -= 1
        token = "".join(reversed(chars))
        return token if len(token) > 1 else f"A{token}"

    def _get_next_id(self, current_dict):
        """Find next free token ID (AA, AB, ...)."""
        used = {value for value in current_dict.values() if isinstance(value, str)}
        index = 0
        while True:
            candidate = self._index_to_token(index)
            if candidate not in used:
                return candidate
            index += 1

    def learn_from_text(
        self,
        text,
        min_length=6,
        top_n=12,
        min_length_single=12,
    ):
        """Analyze raw text and extend the dictionary with worthwhile terms."""
        if not text:
            return []

        dictionary = self._load_dictionary()
        lowered = text.lower()
        token_pattern = re.compile(r"[\w-]{%d,}" % min_length, re.UNICODE)
        tokens = token_pattern.findall(lowered)

        if not tokens:
            return []

        additions = []
        already_known = set(dictionary.keys())

        # 1) Prefer individual words by frequency and length
        word_counter = Counter(tokens)
        word_candidates = [
            (freq, len(word), word)
            for word, freq in word_counter.items()
            if word not in already_known and len(word) >= min_length
        ]
        word_candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)

        for freq, length, word in word_candidates:
            if len(additions) >= top_n:
                break
            if freq > 1 or length >= min_length_single:
                token_id = self._get_next_id(dictionary)
                dictionary[word] = token_id
                additions.append((word, token_id, freq))
                already_known.add(word)

        # 2) Add frequent multi-word phrases (2-3 tokens)
        if len(additions) < top_n:
            base_tokens = re.findall(r"[\w-]+", lowered, re.UNICODE)
            for n in (3, 2):  # longer phrases first
                if len(additions) >= top_n:
                    break
                if len(base_tokens) < n:
                    continue
                phrase_counter = Counter(
                    " ".join(base_tokens[i : i + n])
                    for i in range(len(base_tokens) - n + 1)
                )
                for phrase, freq in phrase_counter.most_common():
                    if len(additions) >= top_n:
                        break
                    compact_len = len(phrase.replace(" ", ""))
                    if (
                        freq < 2
                        or compact_len < (min_length * (n - 1))
                        or phrase in already_known
                    ):
                        continue
                    token_id = self._get_next_id(dictionary)
                    dictionary[phrase] = token_id
                    additions.append((phrase, token_id, freq))
                    already_known.add(phrase)

        if not additions:
            return []

        self._save_dictionary(dictionary)

        sample = ", ".join(f"{token}->{word}" for word, token, _ in additions[:3])
        print(f"[PX-Optimizer] +{len(additions)} Tokens ({sample})")

        return additions
