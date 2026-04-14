import os
import json
from protocol_x.encoder import ProtocolEncoder

# Konfiguration
SOURCE_DIR = "./data_to_analyze" # Ordner mit Texten/Code
DICT_PATH = "dictionary.json"

def run_benchmark():
    encoder = ProtocolEncoder(DICT_PATH)
    
    if not os.path.exists(SOURCE_DIR):
        os.makedirs(SOURCE_DIR)
        with open(f"{SOURCE_DIR}/test.txt", "w") as f:
            f.write("Die Halbleiterindustrie ist entscheidend für künstliche Intelligenz und QuantumScape.")
        print(f"Ordner '{SOURCE_DIR}' wurde erstellt. Pack dort deine Files rein!")

    total_orig = 0
    total_comp = 0
    file_count = 0

    print(f"{'Datei':<30} | {'Original':<10} | {'PX-Size':<10} | {'Ersparnis'}")
    print("-" * 70)

    for filename in os.listdir(SOURCE_DIR):
        if filename.endswith((".txt", ".py", ".md", ".log")):
            path = os.path.join(SOURCE_DIR, filename)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            compressed = encoder.encode(content)
            
            orig_len = len(content)
            comp_len = len(compressed)
            
            total_orig += orig_len
            total_comp += comp_len
            file_count += 1
            
            diff = orig_len - comp_len
            percent = (diff / orig_len) * 100 if orig_len > 0 else 0
            
            print(f"{filename[:30]:<30} | {orig_len:<10} | {comp_len:<10} | {percent:>8.1f}%")

    print("-" * 70)
    final_diff = total_orig - total_comp
    final_percent = (final_diff / total_orig) * 100 if total_orig > 0 else 0
    
    print(f"GESAMT ({file_count} Files):")
    print(f"Original Zeichen: {total_orig}")
    print(f"Protocol-X Zeichen: {total_comp}")
    print(f"Effektive Ersparnis: {final_percent:.2f}%")
    print(f"\nSlogan: 'Sparen Sie {int(final_percent)}% Ihrer API-Kosten mit Protocol-X!'")

if __name__ == "__main__":
    run_benchmark()