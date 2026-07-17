"""
Sidebar-Komponente für KI-Anbieter-Konfiguration.
"""

import streamlit as st

from ..config import UI_TEXT
from ..providers import (
    ProviderConfig,
    ProviderType,
    get_provider_options,
    get_provider_type_from_name,
    get_provider_info,
)


def render_sidebar() -> ProviderConfig:
    """
    Rendert die Sidebar und gibt die ausgewählte Anbieter-Konfiguration zurück.
    
    Returns:
        ProviderConfig mit den vom Benutzer gewählten Einstellungen
    """
    with st.sidebar:
        st.header(UI_TEXT.SETTINGS_HEADER)
        
        st.markdown(UI_TEXT.PROVIDER_HEADER)
        st.markdown(UI_TEXT.PROVIDER_DESCRIPTION)
        
        # Anbieter-Auswahl
        selected_provider_name = st.selectbox(
            "Anbieter wählen",
            options=get_provider_options(),
            help="Wählen Sie einen KI-Anbieter für erweiterte Bild-/Diagramm-Erkennung"
        )
        
        provider_type = get_provider_type_from_name(selected_provider_name)
        
        # Konfiguration basierend auf Anbieter
        config = _render_provider_config(provider_type)
        
        # Status-Anzeige
        _render_status(config)
        
        return config


def _render_provider_config(provider_type: ProviderType) -> ProviderConfig:
    """Rendert die anbieterspezifische Konfiguration."""
    
    if provider_type == ProviderType.NONE:
        return ProviderConfig(provider_type=ProviderType.NONE)
    
    if provider_type == ProviderType.OPENAI:
        return _render_openai_config()
    
    if provider_type == ProviderType.GEMINI:
        return _render_gemini_config()
    
    if provider_type == ProviderType.OLLAMA:
        return _render_ollama_config()
    
    if provider_type == ProviderType.CUSTOM:
        return _render_custom_config()
    
    return ProviderConfig(provider_type=ProviderType.NONE)


def _render_openai_config() -> ProviderConfig:
    """Rendert die OpenAI-Konfiguration."""
    info = get_provider_info(ProviderType.OPENAI)
    
    api_key = st.text_input(
        "OpenAI API-Key",
        type="password",
        placeholder=info.api_key_placeholder,
        help=info.api_key_help
    )
    
    model_name = st.selectbox(
        "Modell",
        options=info.models,
        help="Vision-fähiges Modell wählen"
    )
    
    return ProviderConfig(
        provider_type=ProviderType.OPENAI,
        api_key=api_key if api_key else None,
        model_name=model_name
    )


def _render_gemini_config() -> ProviderConfig:
    """Rendert die Google Gemini-Konfiguration."""
    info = get_provider_info(ProviderType.GEMINI)
    
    api_key = st.text_input(
        "Gemini API-Key",
        type="password",
        placeholder=info.api_key_placeholder,
        help=info.api_key_help
    )
    
    model_name = st.selectbox(
        "Modell",
        options=info.models,
        help="Gemini Flash ist kostenlos und schnell"
    )
    
    if info.info_message:
        st.info(info.info_message)
    
    return ProviderConfig(
        provider_type=ProviderType.GEMINI,
        api_key=api_key if api_key else None,
        base_url=info.default_base_url,
        model_name=model_name
    )


def _render_ollama_config() -> ProviderConfig:
    """Rendert die Ollama-Konfiguration."""
    info = get_provider_info(ProviderType.OLLAMA)
    
    base_url = st.text_input(
        "Ollama URL",
        value=info.default_base_url,
        help="Standard: http://localhost:11434/v1"
    )
    
    model_name = st.text_input(
        "Modell-Name",
        value=info.models[0],
        help=f"Vision-fähige Modelle: {', '.join(info.models)}"
    )
    
    if info.info_message:
        st.info(info.info_message)
    
    return ProviderConfig(
        provider_type=ProviderType.OLLAMA,
        api_key="ollama",  # Ollama benötigt keinen echten Key
        base_url=base_url if base_url else None,
        model_name=model_name if model_name else None
    )


def _render_custom_config() -> ProviderConfig:
    """Rendert die Konfiguration für benutzerdefinierte Anbieter."""
    base_url = st.text_input(
        "API Base URL",
        placeholder="https://api.example.com/v1",
        help="Die Basis-URL der OpenAI-kompatiblen API"
    )
    
    api_key = st.text_input(
        "API-Key",
        type="password",
        help="Ihr API-Key für diesen Anbieter"
    )
    
    model_name = st.text_input(
        "Modell-Name",
        placeholder="z.B. glm-4v, claude-3-sonnet",
        help="Name des Vision-fähigen Modells"
    )
    
    return ProviderConfig(
        provider_type=ProviderType.CUSTOM,
        api_key=api_key if api_key else None,
        base_url=base_url if base_url else None,
        model_name=model_name if model_name else None
    )


def _render_status(config: ProviderConfig) -> None:
    """Rendert die Status-Anzeige basierend auf der Konfiguration."""
    st.divider()
    
    if config.is_configured:
        st.success(UI_TEXT.STATUS_OCR_ACTIVE.format(provider=config.display_name))
    else:
        st.info(UI_TEXT.STATUS_STANDARD_MODE)
    
    st.markdown(UI_TEXT.STATUS_HINT)
