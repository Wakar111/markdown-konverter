"""
Temporäres Debug-Skript zur Diagnose der PNG-Konvertierung mit Gemini.
Ausführen mit: python debug_png.py <pfad-zu-deiner.png>
"""
import sys
from src.providers import ProviderConfig, ProviderType
from src.converter import MarkdownConverter

if len(sys.argv) < 2:
    print("Nutzung: python debug_png.py <pfad-zur-png-datei>")
    sys.exit(1)

png_path = sys.argv[1]
api_key = input("Gemini API-Key eingeben: ").strip()
model_name = input("Modell (Enter für gemini-2.0-flash): ").strip() or "gemini-2.0-flash"

config = ProviderConfig(
    provider_type=ProviderType.GEMINI,
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    model_name=model_name,
)
print("is_configured:", config.is_configured)

converter = MarkdownConverter(config)
with open(png_path, "rb") as f:
    data = f.read()

result = converter.convert_bytes(data, png_path)
print("success:", result.success)
print("content repr:", repr(result.content))
print("error:", result.error_message)
