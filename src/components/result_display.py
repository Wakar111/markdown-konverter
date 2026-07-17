"""
Komponente zur Anzeige der Konvertierungsergebnisse.
"""

import streamlit as st

from ..config import UI_TEXT
from ..converter import ConversionResult


def render_result(result: ConversionResult) -> None:
    """
    Rendert das Konvertierungsergebnis.
    
    Args:
        result: Das Ergebnis der Konvertierung
    """
    if result.success:
        _render_success(result.content)
    else:
        _render_error(result.error_message)


def _render_success(markdown_content: str) -> None:
    """Rendert ein erfolgreiches Ergebnis."""
    st.success(UI_TEXT.CONVERSION_SUCCESS)
    
    # Tabs für Vorschau und Markdown-Code
    tab_preview, tab_code = st.tabs([UI_TEXT.TAB_PREVIEW, UI_TEXT.TAB_MARKDOWN])
    
    with tab_preview:
        _render_preview(markdown_content)
    
    with tab_code:
        _render_code_view(markdown_content)


def _render_preview(content: str) -> None:
    """Rendert die Markdown-Vorschau."""
    st.markdown(content)


def _render_code_view(content: str) -> None:
    """Rendert die Code-Ansicht mit Kopier-Button."""
    # st.code hat einen eingebauten Kopier-Button oben rechts
    st.code(content, language="markdown", line_numbers=True)


def _render_error(error_message: str) -> None:
    """Rendert eine Fehlermeldung."""
    st.error(UI_TEXT.CONVERSION_ERROR.format(error=error_message))
    st.info(UI_TEXT.CONVERSION_ERROR_HINT)
