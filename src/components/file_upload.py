"""
Datei-Upload-Komponente.
"""

from typing import Optional

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from ..config import UI_TEXT


def render_file_upload() -> Optional[UploadedFile]:
    """
    Rendert den Datei-Upload-Bereich.
    
    Returns:
        Die hochgeladene Datei oder None
    """
    # Unterstützte Dateitypen anzeigen
    with st.expander(UI_TEXT.FORMATS_EXPANDER):
        st.markdown(UI_TEXT.FORMATS_LIST)
    
    # Datei-Upload Widget
    uploaded_file = st.file_uploader(
        UI_TEXT.UPLOAD_LABEL,
        type=None,  # Alle Dateitypen akzeptieren
        help=UI_TEXT.UPLOAD_HELP
    )
    
    return uploaded_file
