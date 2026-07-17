"""
KI-Anbieter-Konfiguration für Vision-basierte OCR.

Unterstützt verschiedene OpenAI-kompatible APIs.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ProviderType(Enum):
    """Verfügbare KI-Anbieter."""
    
    NONE = "Keiner (Standard)"
    OPENAI = "OpenAI"
    GEMINI = "Google Gemini"
    OLLAMA = "Ollama (lokal)"
    CUSTOM = "Andere (OpenAI-kompatibel)"


@dataclass
class ProviderConfig:
    """Konfiguration für einen KI-Anbieter."""
    
    provider_type: ProviderType
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_name: Optional[str] = None
    
    @property
    def is_configured(self) -> bool:
        """Prüft, ob der Anbieter vollständig konfiguriert ist."""
        if self.provider_type == ProviderType.NONE:
            return False
        return bool(self.api_key and self.model_name)
    
    @property
    def display_name(self) -> str:
        """Gibt den Anzeigenamen des Anbieters zurück."""
        return self.provider_type.value


@dataclass(frozen=True)
class ProviderInfo:
    """Informationen über einen Anbieter für die UI."""
    
    provider_type: ProviderType
    models: tuple[str, ...]
    default_base_url: Optional[str]
    api_key_placeholder: str
    api_key_help: str
    info_message: Optional[str]
    
    
# Vordefinierte Anbieter-Informationen
PROVIDER_INFO: dict[ProviderType, ProviderInfo] = {
    ProviderType.OPENAI: ProviderInfo(
        provider_type=ProviderType.OPENAI,
        models=("gpt-4o", "gpt-4o-mini", "gpt-4-turbo"),
        default_base_url=None,
        api_key_placeholder="sk-...",
        api_key_help="Ihr OpenAI API-Key",
        info_message=None,
    ),
    ProviderType.GEMINI: ProviderInfo(
        provider_type=ProviderType.GEMINI,
        models=("gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"),
        default_base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key_placeholder="AIza...",
        api_key_help="Kostenlos erhältlich unter: https://aistudio.google.com/app/apikey",
        info_message="💡 Gemini bietet einen großzügigen kostenlosen Tarif!",
    ),
    ProviderType.OLLAMA: ProviderInfo(
        provider_type=ProviderType.OLLAMA,
        models=("llava", "bakllava", "llava-llama3"),
        default_base_url="http://localhost:11434/v1",
        api_key_placeholder="",
        api_key_help="",
        info_message="💡 Ollama ist komplett kostenlos und läuft lokal!",
    ),
}


def get_provider_options() -> list[str]:
    """Gibt die Liste aller Anbieter-Optionen für die UI zurück."""
    return [provider.value for provider in ProviderType]


def get_provider_type_from_name(name: str) -> ProviderType:
    """Konvertiert einen Anbieter-Namen in den entsprechenden Enum-Wert."""
    for provider in ProviderType:
        if provider.value == name:
            return provider
    return ProviderType.NONE


def get_provider_info(provider_type: ProviderType) -> Optional[ProviderInfo]:
    """Gibt die Anbieter-Informationen für einen bestimmten Anbieter zurück."""
    return PROVIDER_INFO.get(provider_type)


def create_openai_client(config: ProviderConfig):
    """
    Erstellt einen OpenAI-kompatiblen Client basierend auf der Konfiguration.
    
    Args:
        config: Die Anbieter-Konfiguration
        
    Returns:
        Ein OpenAI-Client oder None, wenn nicht konfiguriert
    """
    if not config.is_configured:
        return None
    
    from openai import OpenAI
    
    client_kwargs = {"api_key": config.api_key}
    if config.base_url:
        client_kwargs["base_url"] = config.base_url
    
    return OpenAI(**client_kwargs)
