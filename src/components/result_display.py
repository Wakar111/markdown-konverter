"""
Komponente zur Anzeige der Konvertierungsergebnisse.
"""

import streamlit as st

from ..config import UI_TEXT
from ..converter import ConversionResult

# Ab dieser Zeichenanzahl wird die Vorschau gekürzt, um lange
# Render-Zeiten im Browser (z.B. bei riesigen CSV-Markdown-Tabellen) zu vermeiden.
PREVIEW_CHAR_LIMIT = 20_000


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
    
    st.download_button(
        UI_TEXT.DOWNLOAD_BUTTON_LABEL,
        data=markdown_content,
        file_name="konvertiert.md",
        mime="text/markdown"
    )
    
    # Tabs für Vorschau und Markdown-Code
    tab_preview, tab_code = st.tabs([UI_TEXT.TAB_PREVIEW, UI_TEXT.TAB_MARKDOWN])
    
    with tab_preview:
        _render_preview(markdown_content)
    
    with tab_code:
        _render_code_view(markdown_content)


def _render_preview(content: str) -> None:
    """Rendert die Markdown-Vorschau.
    
    Bei sehr großen Inhalten (z.B. CSV mit vielen Zeilen) wird die Vorschau
    gekürzt, da das Rendern einer riesigen HTML-Tabelle im Browser lange
    dauern und wie ein "Hängenbleiben" wirken kann.
    """
    if len(content) > PREVIEW_CHAR_LIMIT:
        st.warning(
            UI_TEXT.LARGE_CONTENT_WARNING.format(
                length=len(content),
                limit=PREVIEW_CHAR_LIMIT
            )
        )
        st.markdown(content[:PREVIEW_CHAR_LIMIT])
    else:
        st.markdown(content)


def _render_code_view(content: str) -> None:
    """Rendert die Code-Ansicht mit Kopier-Button.
    
    Bei sehr großen Inhalten wird ebenfalls gekürzt, da st.code() mit
    Zeilennummern bei riesigen Texten im Browser stark verzögert rendert.
    """
    if len(content) > PREVIEW_CHAR_LIMIT:
        st.warning(
            UI_TEXT.LARGE_CONTENT_WARNING.format(
                length=len(content),
                limit=PREVIEW_CHAR_LIMIT
            )
        )
        # st.code hat einen eingebauten Kopier-Button oben rechts
        st.code(content[:PREVIEW_CHAR_LIMIT], language="markdown", line_numbers=True)
    else:
        st.code(content, language="markdown", line_numbers=True)


def _render_error(error_message: str) -> None:
    """Rendert eine Fehlermeldung."""
    st.error(UI_TEXT.CONVERSION_ERROR.format(error=error_message))
    st.info(UI_TEXT.CONVERSION_ERROR_HINT)
