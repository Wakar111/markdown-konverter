"""
Chat-Interface-Komponente für die Dokumentensuche.
"""

import os

import streamlit as st
from typing import Optional

from markitdown import MarkItDown

from ..rag.document_store import DocumentStore
from ..rag.embeddings import EmbeddingService, EmbeddingConfig, EmbeddingProvider
from ..rag.retriever import DocumentRetriever
from ..rag.chat import RAGChat, ChatConfig, ChatProvider
from ..providers import create_openai_client
from .sidebar import render_provider_selector, GLM_VISION_DEFAULT_MODEL

# Priorisierte .env-Erkennung für Embedding- und Chat-Provider (gleiche Reihenfolge
# wie beim Vision-Provider): NVIDIA/GLM > Gemini > OpenAI.
_ENV_PROVIDER_CANDIDATES = {
    "GLM_API_KEY": "NVIDIA NIM",
    "GEMINI_API_KEY": "Google Gemini",
    "OPENAI_API_KEY": "OpenAI",
}

_CHAT_DEFAULT_MODELS = {
    "OpenAI": "gpt-4o-mini",
    "Google Gemini": "gemini-2.0-flash",
    "NVIDIA NIM": "meta/llama-3.1-8b-instruct",
    "Ollama (lokal)": "llama3.2",
}


def render_document_search_page():
    """Rendert die komplette Dokumentensuche-Seite."""
    st.title("🔍 Dokumentensuche")
    st.markdown("Laden Sie Ihre Dokumente hoch und stellen Sie Fragen zu deren Inhalt.")
    
    # Session State initialisieren
    _init_session_state()
    
    # Sidebar für Einstellungen
    _render_search_sidebar()
    
    # Hauptbereich: links Dokumente, rechts Chat (ChatGPT-style)
    col1, col2 = st.columns([1, 2], gap="medium")
    
    with col1:
        _render_document_upload()
    
    with col2:
        _render_chat_interface()


def _init_session_state():
    """Initialisiert den Session State."""
    if "doc_store" not in st.session_state:
        st.session_state.doc_store = DocumentStore()
    
    if "embedding_service" not in st.session_state:
        st.session_state.embedding_service = None
    
    if "retriever" not in st.session_state:
        st.session_state.retriever = None
    
    if "rag_chat" not in st.session_state:
        st.session_state.rag_chat = None
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    if "documents_indexed" not in st.session_state:
        st.session_state.documents_indexed = False
    
    if "vision_provider_config" not in st.session_state:
        st.session_state.vision_provider_config = None
    
    if "removed_filenames" not in st.session_state:
        st.session_state.removed_filenames = set()


def _detect_env_provider_label() -> Optional[str]:
    """Ermittelt den ersten Anbieter, für den ein Key in .env gefunden wurde."""
    for env_var, label in _ENV_PROVIDER_CANDIDATES.items():
        if os.getenv(env_var):
            return label
    return None


def _get_env_key_for_label(label: Optional[str]) -> Optional[str]:
    """Gibt den .env API-Key für einen Anbieter-Label zurück."""
    reverse = {v: k for k, v in _ENV_PROVIDER_CANDIDATES.items()}
    env_var = reverse.get(label)
    return os.getenv(env_var) if env_var else None


def _render_embedding_section() -> tuple[str, Optional[str], bool]:
    """
    Rendert die Embedding-Provider-Auswahl.
    
    .env-Keys werden automatisch und unsichtbar verwendet. Nur bei explizitem
    Wechsel wird die volle Auswahl (Anbieter + eigener Key) eingeblendet.
    
    Returns:
        Tuple aus (embedding_provider_label, api_key, is_auto)
    """
    st.subheader("Embeddings")
    env_provider = _detect_env_provider_label()
    
    if env_provider:
        st.caption(f"✅ **{env_provider}**-Key in .env gefunden – wird automatisch verwendet")
        use_custom = st.checkbox("🔧 Anderen Embedding-Anbieter verwenden", key="use_custom_embedding")
        
        if not use_custom:
            return env_provider, _get_env_key_for_label(env_provider), True
    else:
        use_custom = True
    
    embedding_options = ["Lokal (kostenlos)", "OpenAI", "Google Gemini", "NVIDIA NIM"]
    default_index = embedding_options.index(env_provider) if env_provider in embedding_options else 0
    embedding_provider = st.selectbox(
        "Embedding-Provider",
        options=embedding_options,
        index=default_index,
        help="Lokal ist kostenlos, aber langsamer beim ersten Start"
    )
    
    api_key = None
    if embedding_provider != "Lokal (kostenlos)":
        api_key = st.text_input(
            "Embedding API-Key",
            type="password",
            placeholder="Eigenen Key eingeben (sonst wird .env-Key verwendet)",
            help="Leer lassen, um den .env-Key für diesen Anbieter zu verwenden",
            key="embedding_api_key_input"
        )
        api_key = api_key.strip() if api_key else _get_env_key_for_label(embedding_provider)
    
    return embedding_provider, api_key, False


def _render_chat_section() -> tuple[str, Optional[str], Optional[str], bool]:
    """
    Rendert die Chat-Provider-Auswahl.
    
    .env-Keys werden automatisch und unsichtbar verwendet (derselbe Key wie
    für Embeddings/Vision-OCR, wenn vom selben Anbieter). Nur bei explizitem
    Wechsel wird die volle Auswahl (Anbieter + Modell + eigener Key) eingeblendet.
    
    Returns:
        Tuple aus (chat_provider_label, api_key, model_name, is_auto)
    """
    st.subheader("Chat-Modell")
    env_provider = _detect_env_provider_label()
    
    if env_provider:
        st.caption(f"✅ **{env_provider}**-Key in .env gefunden – wird automatisch verwendet")
        use_custom = st.checkbox("🔧 Anderen Chat-Anbieter oder Modell verwenden", key="use_custom_chat")
        
        if not use_custom:
            model_name = _CHAT_DEFAULT_MODELS.get(env_provider, "gpt-4o-mini")
            return env_provider, _get_env_key_for_label(env_provider), model_name, True
    else:
        use_custom = True
    
    chat_options = ["OpenAI", "Google Gemini", "NVIDIA NIM", "Ollama (lokal)"]
    default_index = chat_options.index(env_provider) if env_provider in chat_options else 0
    chat_provider = st.selectbox(
        "Chat-Provider",
        options=chat_options,
        index=default_index,
        help="Wählen Sie den Provider für die Antwortgenerierung"
    )
    
    api_key = None
    if chat_provider != "Ollama (lokal)":
        api_key = st.text_input(
            "Chat API-Key",
            type="password",
            placeholder="Eigenen Key eingeben (sonst wird .env-Key verwendet)",
            help="Leer lassen, um den .env-Key für diesen Anbieter zu verwenden",
            key="chat_api_key_input"
        )
        api_key = api_key.strip() if api_key else _get_env_key_for_label(chat_provider)
    
    if chat_provider == "OpenAI":
        model_name = st.selectbox("Modell", options=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"])
    elif chat_provider == "Google Gemini":
        model_name = st.selectbox("Modell", options=["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"])
    elif chat_provider == "NVIDIA NIM":
        model_name = st.text_input(
            "Modell-Name",
            value=_CHAT_DEFAULT_MODELS["NVIDIA NIM"],
            help="z.B. meta/llama-3.1-8b-instruct (schnell), meta/llama-3.1-70b-instruct, nvidia/nemotron-3-nano-omni-30b-a3b-reasoning (Vision)"
        )
    else:
        model_name = st.text_input(
            "Modell-Name",
            value=_CHAT_DEFAULT_MODELS["Ollama (lokal)"],
            help="z.B. llama3.2, mistral, phi3"
        )
    
    return chat_provider, api_key, model_name, False


def _render_search_sidebar():
    """Rendert die Sidebar für die Dokumentensuche."""
    with st.sidebar:
        st.header("🤖 KI-Einstellungen")
        
        # Vision-Provider für Bild-OCR (PNG/JPG durchsuchbar machen)
        with st.expander("🖼️ Bild-OCR (für PNG/JPG-Upload)", expanded=False):
            st.caption(
                "Ohne Vision-Anbieter werden Bilder nur mit Metadaten indexiert "
                "(kein durchsuchbarer Bildinhalt)."
            )
            # Gleicher Widget-Key wie im Konverter -> Auswahl wird zwischen
            # den Seiten geteilt und muss nicht doppelt vorgenommen werden.
            vision_config = render_provider_selector(
                show_status=True, silent_default_model=GLM_VISION_DEFAULT_MODEL
            )
            st.session_state.vision_provider_config = vision_config
        
        st.divider()
        
        embedding_provider, embedding_api_key, embedding_is_auto = _render_embedding_section()
        chat_provider, chat_api_key, chat_model_name, chat_is_auto = _render_chat_section()
        
        st.divider()
        
        if embedding_is_auto and chat_is_auto:
            # Standard-.env-Konfiguration -> automatisch initialisieren,
            # kein manueller Klick nötig. Nur bei Konfigurationsänderung neu laden.
            fingerprint = (embedding_provider, embedding_api_key, chat_provider, chat_api_key, chat_model_name)
            if st.session_state.get("_auto_init_fingerprint") != fingerprint:
                _initialize_services(
                    embedding_provider, embedding_api_key,
                    chat_provider, chat_api_key, chat_model_name
                )
                st.session_state._auto_init_fingerprint = fingerprint
        else:
            # Custom-Anbieter/Modell -> erst nach explizitem Klick initialisieren
            if st.button("🚀 Services initialisieren", use_container_width=True):
                _initialize_services(
                    embedding_provider, embedding_api_key,
                    chat_provider, chat_api_key, chat_model_name
                )
        
        # Status anzeigen
        _render_service_status()


def _initialize_services(
    embedding_provider: str,
    embedding_api_key: Optional[str],
    chat_provider: str,
    chat_api_key: Optional[str],
    chat_model_name: Optional[str]
):
    """Initialisiert die RAG-Services."""
    try:
        with st.spinner("Initialisiere Embedding-Service..."):
            # Embedding-Provider mappen
            emb_provider_map = {
                "Lokal (kostenlos)": EmbeddingProvider.LOCAL,
                "OpenAI": EmbeddingProvider.OPENAI,
                "Google Gemini": EmbeddingProvider.GEMINI,
                "NVIDIA NIM": EmbeddingProvider.NVIDIA,
            }
            emb_provider = emb_provider_map.get(embedding_provider, EmbeddingProvider.LOCAL)
            
            emb_config = EmbeddingConfig(
                provider=emb_provider,
                api_key=embedding_api_key if emb_provider != EmbeddingProvider.LOCAL else None
            )
            st.session_state.embedding_service = EmbeddingService(emb_config)
        
        with st.spinner("Initialisiere Retriever..."):
            st.session_state.retriever = DocumentRetriever(
                document_store=st.session_state.doc_store,
                embedding_service=st.session_state.embedding_service
            )
        
        with st.spinner("Initialisiere Chat..."):
            # Chat-Provider mappen
            chat_provider_map = {
                "OpenAI": ChatProvider.OPENAI,
                "Google Gemini": ChatProvider.GEMINI,
                "NVIDIA NIM": ChatProvider.NVIDIA,
                "Ollama (lokal)": ChatProvider.OLLAMA,
            }
            ch_provider = chat_provider_map.get(chat_provider, ChatProvider.OPENAI)
            
            chat_config = ChatConfig(
                provider=ch_provider,
                api_key=chat_api_key,
                model_name=chat_model_name or "gpt-4o-mini"
            )
            st.session_state.rag_chat = RAGChat(
                retriever=st.session_state.retriever,
                config=chat_config
            )
        
        st.success("✅ Services erfolgreich initialisiert!")
        
    except Exception as e:
        st.error(f"Fehler bei der Initialisierung: {str(e)}")


def _render_service_status():
    """Zeigt den Status der Services an."""
    st.subheader("📊 Status")
    
    doc_count = st.session_state.doc_store.document_count
    chunk_count = st.session_state.doc_store.chunk_count
    indexed_count = st.session_state.retriever.indexed_count if st.session_state.retriever else 0
    
    st.metric("Dokumente", doc_count)
    st.metric("Chunks", chunk_count)
    st.metric("Indexiert", indexed_count)
    
    if st.session_state.embedding_service:
        st.success(f"Embedding: {st.session_state.embedding_service.provider_name}")
    else:
        st.warning("Embedding: Nicht initialisiert")
    
    if st.session_state.rag_chat:
        st.success("Chat: Bereit")
    else:
        st.warning("Chat: Nicht initialisiert")


def _sync_document_store_markitdown() -> None:
    """Aktualisiert die MarkItDown-Instanz des DocumentStore mit dem Vision-Provider."""
    config = st.session_state.vision_provider_config
    
    if config and config.is_configured:
        client = create_openai_client(config)
        markitdown_instance = MarkItDown(
            enable_plugins=True,
            llm_client=client,
            llm_model=config.model_name
        )
    else:
        markitdown_instance = MarkItDown()
    
    st.session_state.doc_store.update_markitdown(markitdown_instance)


def _import_shared_converter_file() -> None:
    """Übernimmt eine im Konverter bereits konvertierte Datei automatisch,
    ohne dass die Datei erneut hochgeladen/konvertiert werden muss."""
    shared = st.session_state.get("shared_converted_file")
    if not shared:
        return
    
    filename = shared["filename"]
    existing_docs = [d.filename for d in st.session_state.doc_store.documents]
    
    if filename in existing_docs or filename in st.session_state.removed_filenames:
        return
    
    try:
        doc = st.session_state.doc_store.add_document_from_content(
            shared["file_bytes"],
            filename,
            shared["markdown_content"]
        )
        st.success(f"📄 Aus Konverter übernommen: {doc.filename} ({doc.chunk_count} Chunks)")
    except Exception as e:
        st.error(f"Fehler beim Übernehmen von {filename}: {str(e)}")


def _render_document_upload():
    """Rendert den Dokumenten-Upload-Bereich."""
    st.subheader("📁 Dokumente")
    
    _sync_document_store_markitdown()
    _import_shared_converter_file()
    
    # Multi-File-Upload
    uploaded_files = st.file_uploader(
        "Dokumente hochladen",
        type=["pdf", "docx", "doc", "xlsx", "pptx", "txt", "csv", "json", "html", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help="Laden Sie Ihre Rechnungen, Verträge, Bilder und andere Dokumente hoch"
    )
    
    # Nur Dateinamen, die noch im Uploader angezeigt werden, in "removed_filenames"
    # behalten. Sobald der Nutzer das Chip aus dem Uploader entfernt, wird der
    # Name freigegeben (kann dann erneut hochgeladen werden).
    current_upload_names = {f.name for f in uploaded_files} if uploaded_files else set()
    st.session_state.removed_filenames &= current_upload_names
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Explizit gelöschte Dateien nicht automatisch wieder hinzufügen,
            # solange sie noch im Uploader-Widget "kleben".
            if uploaded_file.name in st.session_state.removed_filenames:
                continue
            
            # Prüfen ob bereits hinzugefügt
            existing_docs = [d.filename for d in st.session_state.doc_store.documents]
            if uploaded_file.name not in existing_docs:
                with st.spinner(f"Verarbeite {uploaded_file.name}..."):
                    try:
                        doc = st.session_state.doc_store.add_document(
                            uploaded_file.getvalue(),
                            uploaded_file.name
                        )
                        st.success(f"✅ {doc.filename} ({doc.chunk_count} Chunks)")
                        # Für den Konverter merken, damit die Datei dort ohne
                        # erneuten Upload/Konvertierung angezeigt werden kann.
                        st.session_state.shared_search_file = {
                            "filename": doc.filename,
                            "markdown_content": doc.content,
                        }
                    except Exception as e:
                        st.error(f"Fehler bei {uploaded_file.name}: {str(e)}")
    
    # Automatische Indexierung: läuft bei jedem Rerun, sobald Services bereit sind.
    # index_documents() ist idempotent (indexiert nur neue Chunks) -> kein Button nötig.
    if st.session_state.doc_store.document_count > 0:
        if st.session_state.retriever is None:
            st.warning("⚠️ Bitte zuerst in der Sidebar auf **'🚀 Services initialisieren'** klicken!")
        else:
            newly_indexed = st.session_state.retriever.index_documents()
            if newly_indexed:
                st.success(f"✅ {newly_indexed} Chunks automatisch indexiert")
            st.session_state.documents_indexed = st.session_state.retriever.indexed_count > 0
    
    # Liste der Dokumente
    st.divider()
    st.markdown("**Hochgeladene Dokumente:**")
    
    for doc in st.session_state.doc_store.documents:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.text(f"📄 {doc.filename}")
        with col2:
            if st.button("🗑️", key=f"del_{doc.id}"):
                st.session_state.doc_store.remove_document(doc.id)
                if st.session_state.retriever:
                    st.session_state.retriever.remove_document(doc.id)
                st.session_state.removed_filenames.add(doc.filename)
                st.rerun()


def _render_chat_interface():
    """Rendert das Chat-Interface (ChatGPT-style mit scrollbarem Chat-Fenster)."""

    # Header mit Titel und Chat-loeschen-Button in einer Zeile
    header_col1, header_col2 = st.columns([5, 1])
    with header_col1:
        st.subheader("💬 Fragen stellen")
    with header_col2:
        if st.session_state.chat_messages:
            if st.button("🗑️ Chat löschen", key="clear_chat"):
                st.session_state.chat_messages = []
                if st.session_state.rag_chat:
                    st.session_state.rag_chat.clear_history()
                st.rerun()

    # Status-Hinweise (kompakt, nicht im scrollbaren Bereich)
    if not st.session_state.rag_chat:
        st.info("ℹ️ Services werden automatisch initialisiert – bitte kurz warten.")
    elif not st.session_state.documents_indexed and st.session_state.doc_store.document_count == 0:
        st.info("ℹ️ Laden Sie links Dokumente hoch, um Fragen zu stellen.")

    # Scrollbarer Chat-Verlauf (feste Höhe wie bei ChatGPT/Copilot)
    chat_container = st.container(height=500)

    with chat_container:
        if not st.session_state.chat_messages:
            st.markdown(
                "_Stellen Sie eine Frage zu Ihren hochgeladenen Dokumenten..._"
            )

        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("sources"):
                    with st.expander("📚 Quellen"):
                        for source in msg["sources"]:
                            st.text(f"• {source}")

    # Chat-Input (Streamlit klebt diesen automatisch ans Seitenende)
    if prompt := st.chat_input("Stellen Sie eine Frage zu Ihren Dokumenten..."):
        if not st.session_state.rag_chat:
            st.error("Bitte erst Services initialisieren!")
            return

        if not st.session_state.documents_indexed:
            st.warning("Bitte erst Dokumente indexieren!")
            return

        # User-Nachricht zum Verlauf hinzufügen
        st.session_state.chat_messages.append({
            "role": "user",
            "content": prompt
        })

        # Antwort generieren (im scrollbaren Container anzeigen)
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Suche in Dokumenten..."):
                    response = st.session_state.rag_chat.ask(prompt, top_k=15)

                st.markdown(response.answer)

                if response.sources:
                    sources = list(set(r.source for r in response.sources))
                    with st.expander("📚 Quellen"):
                        for source in sources:
                            st.text(f"• {source}")
                else:
                    sources = None

        # Nachricht speichern
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": response.answer,
            "sources": sources if response.sources else None
        })
        st.rerun()

