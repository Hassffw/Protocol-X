import os

from protocol_x import PXClient

client = PXClient.from_deepseek(api_key=os.environ.get("DEEPSEEK_API_KEY"))
response = client.chat.completions.create(
    model=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
    messages=[{"role": "user", "content": """Analysiere den folgenden Sachverhalt extrem detailliert und erstelle eine Zusammenfassung unter Berücksichtigung der Token-Effizienz.

Sachverhalt:
Die industrielle Fertigung der Zukunft wird maßgeblich durch die Implementierung von Systemen der künstlichen Intelligenz beeinflusst. Künstliche Intelligenz ist nicht nur ein Trend, sondern künstliche Intelligenz ist das Fundament für die Industrie 4.0. In der Industrie 4.0 geht es darum, dass künstliche Intelligenz und maschinelles Lernen die Effizienz der Produktion steigern. Wenn wir über die Steigerung der Effizienz der Produktion sprechen, müssen wir beachten, dass die Effizienz der Produktion direkt mit der vorausschauenden Wartung verknüpft ist. 

Vorausschauende Wartung, oft auch Predictive Maintenance genannt, nutzt künstliche Intelligenz, um Ausfallzeiten zu minimieren. Die Minimierung von Ausfallzeiten ist essenziell für die industrielle Fertigung, da jede Minute Ausfallzeit in der industriellen Fertigung hohe Kosten verursacht. Ein weiterer Aspekt der künstlichen Intelligenz in der Industrie 4.0 ist die Optimierung der Lieferketten. Die Optimierung der Lieferketten erfordert eine Echtzeit-Datenanalyse. Echtzeit-Datenanalyse wird durch moderne Algorithmen ermöglicht, die auf künstlicher Intelligenz basieren.

Zusammenfassend lässt sich sagen:
1. Künstliche Intelligenz transformiert die industrielle Fertigung.
2. Die Industrie 4.0 basiert auf künstlicher Intelligenz.
3. Die Effizienz der Produktion wird durch künstliche Intelligenz gesteigert.
4. Vorausschauende Wartung reduziert Ausfallzeiten in der industriellen Fertigung.
5. Die Optimierung der Lieferketten braucht Echtzeit-Datenanalyse durch künstliche Intelligenz.

Bitte erkläre mir nun, warum künstliche Intelligenz in der Industrie 4.0 so wichtig ist und wie die Effizienz der Produktion durch vorausschauende Wartung und die Optimierung der Lieferketten genau verbessert wird. Nutze für deine Antwort eine sehr präzise Fachsprache."""}],
)
print(response.content)
