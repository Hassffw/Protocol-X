# Protocol-X

Token-sparende Prompting-Infrastruktur für beliebige Chat-Modelle.
Die Bibliothek komprimiert Eingaben über ein lernendes Dictionary, instruiert das Mapping einmal pro Session
und dekomprimiert Antworten wieder in Klartext.

## Features
- Automatische Komprimierung inklusive PX-Header-Management
- Pluggable Provider: OpenAI, Anthropic (Claude) und DeepSeek
- Self-Learning Optimizer für neue Begriffe und Phrasen
- CLI (python -m protocol_x) und Beispiel-Scripte unter examples/

## Installation
~~~bash
pip install -e .[openai]
~~~
Wähle je nach Zielanbieter die passenden Extras ([openai], [anthropic], [deepseek], [all]).

## Verwendung
~~~python
import os
from protocol_x import PXClient

client = PXClient.from_openai(api_key=os.environ["OPENAI_API_KEY"])
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Fasse PX in drei Bulletpoints zusammen."}],
)
print(response.content)
~~~

### CLI
~~~bash
export OPENAI_API_KEY=sk-...
python -m protocol_x --provider openai --model gpt-4o-mini --message "Fasse PX zusammen"
~~~

## Beispiele
- examples/openai_basic.py
- examples/anthropic_basic.py
- examples/deepseek_basic.py

## Aufbau
~~~
protocol_x/
  client.py        # PXClient mit Provider-Factories
  encoder.py       # Tokenisierung
  decoder.py       # Rückübersetzung
  optimizer.py     # Dictionary-Lernlogik
  providers/       # API-spezifische Adapter
  cli.py           # CLI-Entry-Point
~~~

## Erweiterungen
- Weitere Provider (Azure OpenAI, Gemini)
- Persistente Dictionaries pro Projekt
- Tests mit Mock-Providern

PRs willkommen!
