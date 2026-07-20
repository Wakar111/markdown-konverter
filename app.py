"""
MarkItDown Konverter - Hauptanwendung

Eine Streamlit-Anwendung zur Konvertierung verschiedener Dateiformate in Markdown
und zur KI-gestützten Dokumentensuche.
"""

import streamlit as st

from src.config import APP_CONFIG, UI_TEXT
from src.converter import MarkdownConverter
from src.components import render_sidebar, render_file_upload, render_result
from src.components.document_search import render_document_search_page


def configure_page() -> None:
    """Konfiguriert die Streamlit-Seite."""
    st.set_page_config(
        page_title=APP_CONFIG.PAGE_TITLE,
        page_icon=APP_CONFIG.PAGE_ICON,
        layout=APP_CONFIG.LAYOUT
    )


def render_header() -> None:
    """Rendert den Header der Anwendung."""
    st.title(UI_TEXT.APP_TITLE)
    st.markdown(UI_TEXT.APP_DESCRIPTION)


def render_footer() -> None:
    """Rendert den Footer der Anwendung."""
    st.divider()
    st.markdown(UI_TEXT.FOOTER_HTML, unsafe_allow_html=True)


def render_converter_page(provider_config) -> None:
    """Rendert die Konverter-Seite."""
    # Header rendern
    render_header()
    
    # Datei-Upload rendern
    uploaded_file = render_file_upload()
    
    # Konvertierung durchführen, wenn Datei hochgeladen
    if uploaded_file is not None:
        st.divider()
        
        with st.spinner(UI_TEXT.CONVERTING_MESSAGE.format(filename=uploaded_file.name)):
            converter = MarkdownConverter(provider_config)
            result = converter.convert_bytes(
                uploaded_file.getvalue(),
                uploaded_file.name
            )
        
        render_result(result)
    
    # Footer rendern
    render_footer()


def main() -> None:
    """Hauptfunktion der Anwendung."""
    # Seite konfigurieren
    configure_page()
    
    # Navigation
    page = st.sidebar.radio(
        "📌 Navigation",
        options=["📄 Konverter", "🔍 Dokumentensuche"],
        index=0
    )
    
    st.sidebar.divider()
    
    if page == "📄 Konverter":
        # Sidebar für Konverter rendern und Konfiguration erhalten
        provider_config = render_sidebar()
        render_converter_page(provider_config)
    else:
        # Dokumentensuche-Seite
        render_document_search_page()


if __name__ == "__main__":
    main()
