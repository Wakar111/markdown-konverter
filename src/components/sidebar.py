"""
Sidebar-Komponente für KI-Anbieter-Konfiguration.
"""

import os
from typing import Optional

import streamlit as st

from ..config import UI_TEXT
from ..providers import (
    ProviderConfig,
    ProviderType,
    get_provider_options,
    get_provider_type_from_name,
    get_provider_info,
)


def _detect_env_provider() -> ProviderType:
    """Ermittelt den ersten Anbieter, für den ein Key/URL in .env gefunden wurde."""
    if os.getenv("GLM_API_KEY"):
        return ProviderType.GLM
    if os.getenv("GEMINI_API_KEY"):
        return ProviderType.GEMINI
    if os.getenv("OPENAI_API_KEY"):
        return ProviderType.OPENAI
    if os.getenv("CUSTOM_API_KEY"):
        return ProviderType.CUSTOM
    return ProviderType.NONE


def _render_env_overview() -> None:
    """Zeigt eine kompakte Übersicht, welche Anbieter-Keys in .env gefunden wurden."""
    checks = [
        ("Gemini", bool(os.getenv("GEMINI_API_KEY"))),
        ("GLM/NVIDIA", bool(os.getenv("GLM_API_KEY"))),
        ("OpenAI", bool(os.getenv("OPENAI_API_KEY"))),
        ("Andere", bool(os.getenv("CUSTOM_API_KEY"))),
    ]
    parts = [f"{'✅' if found else '⬜'} {name}" for name, found in checks]
    st.caption("**In .env gefunden:** " + " · ".join(parts))


def _get_env_key_for_provider(provider_type: ProviderType) -> Optional[str]:
    """Gibt den .env API-Key für einen Anbieter zurück (falls vorhanden)."""
    mapping = {
        ProviderType.GLM: os.getenv("GLM_API_KEY"),
        ProviderType.GEMINI: os.getenv("GEMINI_API_KEY"),
        ProviderType.OPENAI: os.getenv("OPENAI_API_KEY"),
        ProviderType.CUSTOM: os.getenv("CUSTOM_API_KEY"),
    }
    return mapping.get(provider_type) or None


def render_provider_selector(
    show_status: bool = True,
    widget_key_prefix: str = "",
    silent_default_model: Optional[str] = None,
) -> ProviderConfig:
    """
    Rendert die Anbieter-Auswahl + Konfiguration (ohne Sidebar-Wrapper).
    
    Wiederverwendbar auf jeder Seite (z.B. Konverter, Dokumentensuche).
    
    Wenn ein Anbieter-Key in .env gefunden wird, wird dieser automatisch und
    UNSICHTBAR im Hintergrund verwendet (kein API-Key im UI sichtbar). Nur wenn
    der Benutzer explizit einen anderen Anbieter/Modell/Key nutzen möchte,
    werden die entsprechenden Eingabefelder eingeblendet.
    
    Args:
        show_status: Ob die Status-Anzeige (aktiv/inaktiv) gerendert werden soll
        widget_key_prefix: Präfix für Widget-Keys, um Kollisionen bei Mehrfachnutzung
            auf derselben Seite zu vermeiden
        silent_default_model: Modell, das im automatischen .env-Modus verwendet
            werden soll (z.B. ein Vision- oder Text-Modell je nach Einsatzzweck).
            Wenn None, wird das erste Modell des Anbieters verwendet.
    
    Returns:
        ProviderConfig mit den vom Benutzer gewählten Einstellungen
    """
    env_provider = _detect_env_provider()
    
    if env_provider != ProviderType.NONE:
        env_key = _get_env_key_for_provider(env_provider)
        st.caption(f"✅ **{env_provider.value}**-Key in .env gefunden – wird automatisch verwendet")
        
        use_custom = st.checkbox(
            "🔧 Anderen Anbieter oder Modell verwenden",
            key=f"{widget_key_prefix}use_custom_provider",
        )
        
        if not use_custom:
            info = get_provider_info(env_provider)
            model_name = silent_default_model or (info.models[0] if info else None)
            base_url = info.default_base_url if info else None
            config = ProviderConfig(
                provider_type=env_provider,
                api_key=env_key,
                base_url=base_url,
                model_name=model_name,
            )
            if show_status:
                _render_status(config)
            return config
    
    # Manuelle Auswahl: kein .env-Key vorhanden ODER Benutzer möchte wechseln
    options = get_provider_options()
    default_index = options.index(env_provider.value) if env_provider.value in options else 0
    
    selected_provider_name = st.selectbox(
        "Anbieter wählen",
        options=options,
        index=default_index,
        key=f"{widget_key_prefix}provider_select",
        help="Wählen Sie einen KI-Anbieter"
    )
    
    provider_type = get_provider_type_from_name(selected_provider_name)
    
    # Konfiguration basierend auf Anbieter
    config = _render_provider_config(provider_type, widget_key_prefix)
    
    # Status-Anzeige
    if show_status:
        _render_status(config)
    
    return config


# Vision-fähiges Standardmodell für die automatische .env-Nutzung bei GLM/NVIDIA.
# (z-ai/glm-5.2 ist reines Text-Modell, daher hier explizit ein Vision-Modell.)
GLM_VISION_DEFAULT_MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"


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
        
        return render_provider_selector(silent_default_model=GLM_VISION_DEFAULT_MODEL)


def _render_provider_config(provider_type: ProviderType, widget_key_prefix: str = "") -> ProviderConfig:
    """Rendert die anbieterspezifische Konfiguration."""
    
    if provider_type == ProviderType.NONE:
        return ProviderConfig(provider_type=ProviderType.NONE)
    
    if provider_type == ProviderType.OPENAI:
        return _render_openai_config()
    
    if provider_type == ProviderType.GEMINI:
        return _render_gemini_config()
    
    if provider_type == ProviderType.GLM:
        return _render_glm_config()
    
    if provider_type == ProviderType.OLLAMA:
        return _render_ollama_config()
    
    if provider_type == ProviderType.CUSTOM:
        return _render_custom_config()
    
    return ProviderConfig(provider_type=ProviderType.NONE)


def _render_openai_config() -> ProviderConfig:
    """Rendert die OpenAI-Konfiguration."""
    info = get_provider_info(ProviderType.OPENAI)
    
    env_key = os.getenv("OPENAI_API_KEY", "")
    if env_key:
        st.caption(f"🔑 Key aus .env geladen (endet auf ...{env_key[-4:]})")
    
    api_key = st.text_input(
        "OpenAI API-Key",
        value=env_key,
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
    
    env_key = os.getenv("GEMINI_API_KEY", "")
    if env_key:
        st.caption(f"🔑 Key aus .env geladen (endet auf ...{env_key[-4:]})")
    
    api_key = st.text_input(
        "Gemini API-Key",
        value=env_key,
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


def _render_glm_config() -> ProviderConfig:
    """Rendert die NVIDIA NIM Konfiguration (GLM / Llama Vision)."""
    info = get_provider_info(ProviderType.GLM)
    
    env_key = os.getenv("GLM_API_KEY", "")
    if env_key:
        st.caption(f"🔑 Key aus .env geladen (endet auf ...{env_key[-4:]})")
    
    api_key = st.text_input(
        "GLM API-Key",
        value=env_key,
        type="password",
        placeholder=info.api_key_placeholder,
        help=info.api_key_help
    )
    
    model_name = st.text_input(
        "Modell-Name",
        value=os.getenv("GLM_MODEL", info.models[0]),
        help=f"Vision-fähige Modelle, z.B.: {', '.join(info.models)}"
    )
    
    base_url = st.text_input(
        "API Base URL",
        value=os.getenv("GLM_BASE_URL", info.default_base_url),
        help="Standard: " + info.default_base_url
    )
    
    if info.info_message:
        st.info(info.info_message)
    
    return ProviderConfig(
        provider_type=ProviderType.GLM,
        api_key=api_key if api_key else None,
        base_url=base_url if base_url else None,
        model_name=model_name if model_name else None
    )


def _render_ollama_config() -> ProviderConfig:
    """Rendert die Ollama-Konfiguration."""
    info = get_provider_info(ProviderType.OLLAMA)
    
    base_url = st.text_input(
        "Ollama URL",
        value=os.getenv("OLLAMA_BASE_URL", info.default_base_url),
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
    env_key = os.getenv("CUSTOM_API_KEY", "")
    if env_key:
        st.caption(f"🔑 Key aus .env geladen (endet auf ...{env_key[-4:]})")
    
    base_url = st.text_input(
        "API Base URL",
        value=os.getenv("CUSTOM_API_BASE_URL", ""),
        placeholder="https://api.example.com/v1",
        help="Die Basis-URL der OpenAI-kompatiblen API"
    )
    
    api_key = st.text_input(
        "API-Key",
        value=env_key,
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
