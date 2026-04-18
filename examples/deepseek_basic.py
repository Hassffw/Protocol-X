import os

from protocol_x import PXClient

client = PXClient.from_deepseek(api_key=os.environ.get("DEEPSEEK_API_KEY"))
response = client.chat.completions.create(
    model=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
    messages=[{"role": "user", "content": """Wie könnte man tokenoptimization per dynamisch allokiertem dictionary wie   "strategie-analyse": "AR",
  "berücksichtige": "AS", in openclaw einbauen um das context window gering zu halten
"""}],
)
print(response.content)
