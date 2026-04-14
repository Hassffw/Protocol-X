import os

from protocol_x import PXClient

client = PXClient.from_anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
response = client.chat.completions.create(
    model=os.environ.get("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
    messages=[{"role": "user", "content": "Fasse den PX Ansatz in zwei Sätzen zusammen."}],
    max_tokens=600,
)
print(response.content)
