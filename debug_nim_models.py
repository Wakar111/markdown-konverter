"""
Temporäres Debug-Skript: Listet verfügbare Modelle für deinen NVIDIA NIM API-Key,
gefiltert nach "glm", um die korrekte Modell-ID zu finden.

Ausführen mit: python debug_nim_models.py
"""
from openai import OpenAI

api_key = input("NVIDIA NIM API-Key eingeben: ").strip()

client = OpenAI(
    api_key=api_key,
    base_url="https://integrate.api.nvidia.com/v1",
)

models = client.models.list()
print("\nGefundene Modelle mit 'glm' im Namen:\n")
for m in models.data:
    if "glm" in m.id.lower():
        print(" -", m.id)

print("\nAlle verfügbaren Modelle (falls kein GLM-Treffer oben):\n")
for m in models.data:
    print(" -", m.id)
