import json
import os
import re
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

    def _get_next_id(self, current_dict):
        """Findet die nächste freie ID (z.B. §12)."""
        if not current_dict:
            return "§1"
        ids = []
        for value in current_dict.values():
            if isinstance(value, str) and value.startswith("§"):
                try:
                    ids.append(int(value[1:]))
                except ValueError:
                    continue
        return f"§{max(ids) + 1}" if ids else f"§{len(current_dict) + 1}"

    def learn_from_text(
        self,
        text,
        min_length=6,
        top_n=12,
        min_length_single=12,
    ):
        """Analysiert Text und erweitert das Dictionary um lohnende Tokens."""
        if not text:
            return []

        dictionary = self._load_dictionary()
        lowered = text.lower()
        token_pattern = re.compile(r"[a-zäöüß0-9-]{%d,}" % min_length)
        tokens = token_pattern.findall(lowered)

        if not tokens:
            return []

        additions = []
        already_known = set(dictionary.keys())

        # 1) Einzelwörter priorisieren nach Häufigkeit und Länge
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

        # 2) Häufige Phrasen (2-3 Tokens) aufnehmen
        if len(additions) < top_n:
            base_tokens = re.findall(r"[a-zäöüß0-9-]+", lowered)
            for n in (3, 2):  # längere Phrasen zuerst
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

        sample = ", ".join(f"{token}→{word}" for word, token, _ in additions[:3])
        print(f"🧠 PX-Optimizer: +{len(additions)} Tokens ({sample})")

        return additions
