import os

from protocol_x import PXClient

client = PXClient.from_deepseek(api_key=os.environ.get("DEEPSEEK_API_KEY"))
response = client.chat.completions.create(
    model=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
    messages=[{"role": "user", "content": "Nenne ein Beispiel, wo Tokensparen besonders wichtig ist."}],
)
print(response.content)
