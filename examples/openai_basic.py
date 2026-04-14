import os

from protocol_x import PXClient

client = PXClient.from_openai(api_key=os.environ.get("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
    messages=[{"role": "user", "content": """ERZÄHLE EINE SPANNENDE GESCHICHTE ÜBER EINE EXPEDITION:
Die Meeresbiologie steht vor einem Rätsel. Unsere Biolumineszenz-Forschung 
hat in der Tiefsee-Expedition völlig neue Lebensformen entdeckt. 
Besonders die Fortpflanzungsstrategie dieser Wesen ist faszinierend. 
Beschreibe die Entdeckung und wie die Biolumineszenz-Forschung dabei hilft, 
die Geheimnisse der Tiefsee-Expedition zu lüften. Sei kreativ und ausführlich"""}],
)
print(response.content)
