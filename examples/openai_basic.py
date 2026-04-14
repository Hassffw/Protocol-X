import os

from protocol_x import PXClient

client = PXClient.from_openai(api_key=os.environ.get("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
    messages=[{"role": "user", "content": "Gib mir drei Produktideen als Liste."}],
)
print(response.content)
