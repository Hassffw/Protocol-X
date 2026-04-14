import argparse
from pathlib import Path

from protocol_x.encoder import ProtocolEncoder
from protocol_x.token_stats import TokenCounter


def _format(label: str, before, after):
    if before.tokens is not None and after.tokens is not None:
        diff = before.tokens - after.tokens
        percent = round((diff / before.tokens) * 100, 1) if before.tokens else 0
        print(f"{label}: {before.tokens} -> {after.tokens} tokens (saved {diff} | {percent}%)")
    else:
        diff = before.characters - after.characters
        percent = round((diff / before.characters) * 100, 1) if before.characters else 0
        print(f"{label}: {before.characters} -> {after.characters} chars (saved {diff} | {percent}%)")


def main():
    parser = argparse.ArgumentParser(description="Measure Protocol-X compression for a single message.")
    parser.add_argument("text", help="User message to encode")
    parser.add_argument("--dictionary", default=Path(__file__).resolve().parents[1] / "dictionary.json", type=Path)
    parser.add_argument("--model", help="Model name hint for token counting (e.g. gpt-4o-mini)")
    args = parser.parse_args()

    encoder = ProtocolEncoder(str(args.dictionary))
    mapping_instruction = encoder.build_mapping_instruction()
    encoded_text = encoder.encode(args.text)

    counter = TokenCounter(args.model)

    before_user = counter.count_messages([{ "role": "user", "content": args.text }])
    after_user = counter.count_messages([{ "role": "user", "content": encoded_text }])

    before_total = counter.count_messages([
        { "role": "system", "content": mapping_instruction },
        { "role": "user", "content": args.text },
    ])
    after_total = counter.count_messages([
        { "role": "system", "content": mapping_instruction },
        { "role": "user", "content": encoded_text },
    ])

    print("--- Encoded message ---")
    print(encoded_text)
    print("--- Savings ---")
    _format("User content", before_user, after_user)
    _format("Total payload", before_total, after_total)


if __name__ == "__main__":
    main()
