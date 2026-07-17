"""
MarkItDown Konverter - Modulpaket

Eine Streamlit-Anwendung zur Konvertierung verschiedener Dateiformate in Markdown.
"""

from .config import AppConfig, UIText, APP_CONFIG, UI_TEXT
from .converter import MarkdownConverter, ConversionResult
from .providers import ProviderConfig, ProviderType

__all__ = [
    "AppConfig",
    "UIText",
    "APP_CONFIG",
    "UI_TEXT",
    "MarkdownConverter",
    "ConversionResult",
    "ProviderConfig",
    "ProviderType",
]
