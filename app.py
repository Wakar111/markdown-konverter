"""
MarkItDown Konverter - Hauptanwendung

Eine Streamlit-Anwendung zur Konvertierung verschiedener Dateiformate in Markdown
und zur KI-gestützten Dokumentensuche.
"""

import hashlib

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from src.config import APP_CONFIG, UI_TEXT
from src.converter import MarkdownConverter, ConversionResult
from src.components import render_sidebar, render_file_upload, render_result
from src.components.document_search import render_document_search_page


def configure_page() -> None:
    """Konfiguriert die Streamlit-Seite."""
    st.set_page_config(
        page_title=APP_CONFIG.PAGE_TITLE,
        page_icon=APP_CONFIG.PAGE_ICON,
        layout=APP_CONFIG.LAYOUT
    )


def render_header(provider_config=None) -> None:
    """Rendert den Header der Anwendung."""
    st.title(UI_TEXT.APP_TITLE)
    st.markdown(UI_TEXT.APP_DESCRIPTION)
    
    if provider_config is not None:
        if provider_config.is_configured:
            st.success(
                f"🤖 Aktiver KI-Anbieter: **{provider_config.display_name}** "
                f"(Modell: `{provider_config.model_name}`)"
            )
        else:
            st.info("ℹ️ Kein KI-Anbieter aktiv – nur Text-Extraktion ohne Bild-OCR.")


def render_footer() -> None:
    """Rendert den Footer der Anwendung."""
    st.divider()
    st.markdown(UI_TEXT.FOOTER_HTML, unsafe_allow_html=True)


def render_converter_page(provider_config) -> None:
    """Rendert die Konverter-Seite."""
    # Header rendern
    render_header(provider_config)
    
    # Datei-Upload rendern
    uploaded_file = render_file_upload()
    
    # Streamlit behält eine hochgeladene Datei im file_uploader-Widget über
    # Seitenwechsel/Reruns hinweg, auch wenn der Nutzer sie längst "vergessen"
    # hat. Damit eine alte, weiterhin im Widget "klebende" Datei nicht dauerhaft
    # Vorrang vor einer neueren Datei aus der Dokumentensuche hat, wird per
    # Content-Hash erkannt, ob es sich um einen wirklich NEUEN Upload handelt.
    own_upload_is_new = False
    file_key = None
    if uploaded_file is not None:
        file_key = f"{uploaded_file.name}_{hashlib.md5(uploaded_file.getvalue()).hexdigest()[:8]}"
        own_upload_is_new = file_key != st.session_state.get("converter_processed_key")
    
    if uploaded_file is not None and own_upload_is_new:
        st.divider()
        
        with st.spinner(UI_TEXT.CONVERTING_MESSAGE.format(filename=uploaded_file.name)):
            converter = MarkdownConverter(provider_config)
            result = converter.convert_bytes(
                uploaded_file.getvalue(),
                uploaded_file.name
            )
            
            # Rendering (v.a. bei großen Dateien wie CSV mit vielen Zeilen) kann
            # selbst einige Zeit dauern. Deshalb bleibt der Spinner sichtbar, bis
            # auch die Vorschau/Code-Ansicht vollständig aufgebaut ist.
            render_result(result)
        
        # Konvertiertes Ergebnis für die Dokumentensuche merken, damit die Datei
        # dort ohne erneuten Upload/Konvertierung übernommen werden kann.
        if result.success:
            st.session_state.converter_processed_key = file_key
            st.session_state.shared_converted_file = {
                "filename": uploaded_file.name,
                "file_bytes": uploaded_file.getvalue(),
                "markdown_content": result.content,
            }
            st.session_state.converter_last_shown_filename = uploaded_file.name
    else:
        # Kein NEUER eigener Upload: entweder gar keine Datei im Uploader,
        # oder dieselbe (bereits verarbeitete) Datei "klebt" noch dort.
        # In diesem Fall hat eine neuere Datei aus der Dokumentensuche Vorrang.
        shared_search_file = st.session_state.get("shared_search_file")
        if (
            shared_search_file
            and shared_search_file["filename"] != st.session_state.get("converter_last_shown_filename")
        ):
            st.divider()
            st.info(f"📄 Aus Dokumentensuche übernommen: **{shared_search_file['filename']}**")
            result = ConversionResult.success_result(shared_search_file["markdown_content"])
            render_result(result)
            st.session_state.converter_last_shown_filename = shared_search_file["filename"]
        elif uploaded_file is not None:
            # Keine neuere Datei aus der Dokumentensuche vorhanden: weiterhin
            # das Ergebnis der (alten) eigenen Upload-Datei anzeigen.
            st.divider()
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
