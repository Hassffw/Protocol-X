import json
import os
import re

class ProtocolDecoder:
    def __init__(self, dict_path):
        """
        Initialisiert den Decoder und baut das Reverse-Mapping auf.
        """
        self.dict_path = dict_path
        self.reverse_dict = self._load_dict()

    def reload_dictionary(self):
        """Aktualisiert das Reverse-Mapping nach Dictionary-Updates."""
        self.reverse_dict = self._load_dict()

    def _strip_instruction_header(self, text):
        """Entfernt eventuelle PX-Header, falls das Modell sie widerspiegelt."""
        mode_marker = "PX!MAP "
        if text.startswith(mode_marker):
            pattern = re.compile(r"^PX!MAP\s+.*?>>\s*", re.DOTALL)
            return re.sub(pattern, "", text)

        prefix = "PX MAP active."
        if text.startswith(prefix):
            pattern = re.compile(r"^PX MAP active\..*?MAP:\s*.*?(?:\n|$)", re.DOTALL)
            return re.sub(pattern, "", text)

        short_prefix = "PX MAP:"
        if text.startswith(short_prefix):
            pattern = re.compile(r"^PX MAP:.*?(?:\n|$)", re.DOTALL)
            return re.sub(pattern, "", text).lstrip()

        return text

    def _load_dict(self):
        """
        Lädt das Dictionary und tauscht Keys mit Values für die Dekomprimierung.
        Beispiel: {"halbleiterindustrie": "§1"} -> {"§1": "halbleiterindustrie"}
        """
        if os.path.exists(self.dict_path):
            try:
                with open(self.dict_path, "r", encoding="utf-8") as f:
                    mapping = json.load(f)
                    # Umkehrung des Dictionarys
                    return {v: k for k, v in mapping.items()}
            except Exception as e:
                print(f"Fehler beim Laden des Dictionary für Decoder: {e}")
        return {}

    def decode(self, text):
        """
        Übersetzt Token-IDs zurück in Langtext.
        """
        if not text:
            return text
            
        # 1. Entferne PX-Header, falls die KI ihn in der Antwort wiederholt hat
        clean_text = text.replace("PX>> ", "").replace("RESPOND IN PX_STYLE: ", "")
        
        clean_text = self._strip_instruction_header(clean_text)

        # 2. Token-IDs durch Originalwörter ersetzen
        # Wir sortieren die IDs nach Länge (längste zuerst), um Teil-Ersetzungen zu vermeiden
        sorted_ids = sorted(self.reverse_dict.keys(), key=len, reverse=True)
        
        for token_id in sorted_ids:
            if token_id in clean_text:
                original_word = self.reverse_dict[token_id]
                clean_text = clean_text.replace(token_id, original_word)
        
        return clean_text

if __name__ == "__main__":
    # Test-Logik
    dec = ProtocolDecoder("../dictionary.json")
    test_reply = "Σ: §1 hat ↑, aber auch ↓."
    print(f"KI-Antwort: {test_reply}")
    print(f"Dekodiert:  {dec.decode(test_reply)}")