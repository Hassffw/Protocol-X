import argparse
import os
import sys
from typing import Any, Dict, List

from . import PXClient, PXResponse

Message = Dict[str, Any]


def _read_prompt(args: argparse.Namespace) -> str:
    if args.message:
        return args.message
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return input("User message: ")


def build_client(provider: str, dict_path: str | None) -> PXClient:
    provider = provider.lower()
    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise SystemExit("OPENAI_API_KEY fehlt.")
        return PXClient.from_openai(api_key=api_key, dict_path=dict_path)
    if provider == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise SystemExit("ANTHROPIC_API_KEY fehlt.")
        return PXClient.from_anthropic(api_key=api_key, dict_path=dict_path)
    if provider == "deepseek":
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise SystemExit("DEEPSEEK_API_KEY fehlt.")
        return PXClient.from_deepseek(api_key=api_key, dict_path=dict_path)
    raise SystemExit(f"Unbekannter Provider: {provider}")


def run() -> None:
    parser = argparse.ArgumentParser(description="PX Protocol CLI")
    parser.add_argument("--provider", default="openai", choices=["openai", "anthropic", "deepseek"], help="Welcher API-Anbieter verwendet wird")
    parser.add_argument("--model", required=True, help="Model-ID des Anbieters")
    parser.add_argument("--dict", dest="dict_path", default=None, help="Pfad zur dictionary.json")
    parser.add_argument("--message", help="Prompt-Text (ansonsten stdin oder Eingabe)")
    parser.add_argument("--max-tokens", dest="max_tokens", type=int, default=None, help="max_tokens Parameter")

    args = parser.parse_args()

    prompt = _read_prompt(args).strip()
    if not prompt:
        raise SystemExit("Leere Eingabe.")

    client = build_client(args.provider, args.dict_path)

    messages: List[Message] = [{"role": "user", "content": prompt}]
    kwargs: Dict[str, Any] = {"model": args.model, "messages": messages}
    if args.max_tokens is not None:
        kwargs["max_tokens"] = args.max_tokens

    response: PXResponse = client.chat.completions.create(**kwargs)
    print(response.content)


if __name__ == "__main__":
    run()
