"""
Chat-Interface-Komponente für die Dokumentensuche.
"""

import streamlit as st
from typing import Optional

from ..rag.document_store import DocumentStore
from ..rag.embeddings import EmbeddingService, EmbeddingConfig, EmbeddingProvider
from ..rag.retriever import DocumentRetriever
from ..rag.chat import RAGChat, ChatConfig, ChatProvider


def render_document_search_page():
    """Rendert die komplette Dokumentensuche-Seite."""
    st.title("🔍 Dokumentensuche")
    st.markdown("Laden Sie Ihre Dokumente hoch und stellen Sie Fragen zu deren Inhalt.")
    
    # Session State initialisieren
    _init_session_state()
    
    # Sidebar für Einstellungen
    _render_search_sidebar()
    
    # Hauptbereich
    col1, col2 = st.columns([1, 2])
    
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


def _render_search_sidebar():
    """Rendert die Sidebar für die Dokumentensuche."""
    with st.sidebar:
        st.header("🤖 KI-Einstellungen")
        
        # Embedding-Provider
        st.subheader("Embeddings")
        embedding_provider = st.selectbox(
            "Embedding-Provider",
            options=["Lokal (kostenlos)", "OpenAI", "Google Gemini"],
            help="Lokal ist kostenlos, aber langsamer beim ersten Start"
        )
        
        # Chat-Provider
        st.subheader("Chat-Modell")
        chat_provider = st.selectbox(
            "Chat-Provider",
            options=["OpenAI", "Google Gemini", "Ollama (lokal)"],
            help="Wählen Sie den Provider für die Antwortgenerierung"
        )
        
        # API-Key (falls benötigt)
        api_key = None
        if chat_provider in ["OpenAI", "Google Gemini"] or embedding_provider in ["OpenAI", "Google Gemini"]:
            api_key = st.text_input(
                "API-Key",
                type="password",
                help="Ihr API-Key für den gewählten Provider"
            )
        
        # Chat-Modell
        model_name = None
        if chat_provider == "OpenAI":
            model_name = st.selectbox(
                "Modell",
                options=["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"]
            )
        elif chat_provider == "Google Gemini":
            model_name = st.selectbox(
                "Modell",
                options=["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
            )
        elif chat_provider == "Ollama (lokal)":
            model_name = st.text_input(
                "Modell-Name",
                value="llama3.2",
                help="z.B. llama3.2, mistral, phi3"
            )
        
        st.divider()
        
        # Services initialisieren Button
        if st.button("🚀 Services initialisieren", use_container_width=True):
            _initialize_services(embedding_provider, chat_provider, api_key, model_name)
        
        # Status anzeigen
        _render_service_status()


def _initialize_services(
    embedding_provider: str,
    chat_provider: str,
    api_key: Optional[str],
    model_name: Optional[str]
):
    """Initialisiert die RAG-Services."""
    try:
        with st.spinner("Initialisiere Embedding-Service..."):
            # Embedding-Provider mappen
            emb_provider_map = {
                "Lokal (kostenlos)": EmbeddingProvider.LOCAL,
                "OpenAI": EmbeddingProvider.OPENAI,
                "Google Gemini": EmbeddingProvider.GEMINI,
            }
            emb_provider = emb_provider_map.get(embedding_provider, EmbeddingProvider.LOCAL)
            
            emb_config = EmbeddingConfig(
                provider=emb_provider,
                api_key=api_key if emb_provider != EmbeddingProvider.LOCAL else None
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
                "Ollama (lokal)": ChatProvider.OLLAMA,
            }
            ch_provider = chat_provider_map.get(chat_provider, ChatProvider.OPENAI)
            
            chat_config = ChatConfig(
                provider=ch_provider,
                api_key=api_key,
                model_name=model_name or "gpt-4o-mini"
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


def _render_document_upload():
    """Rendert den Dokumenten-Upload-Bereich."""
    st.subheader("📁 Dokumente")
    
    # Multi-File-Upload
    uploaded_files = st.file_uploader(
        "Dokumente hochladen",
        type=["pdf", "docx", "doc", "xlsx", "pptx", "txt", "csv", "json", "html"],
        accept_multiple_files=True,
        help="Laden Sie Ihre Rechnungen, Verträge und andere Dokumente hoch"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
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
                        st.session_state.documents_indexed = False
                    except Exception as e:
                        st.error(f"Fehler bei {uploaded_file.name}: {str(e)}")
    
    # Dokumente indexieren
    if st.session_state.doc_store.document_count > 0:
        if st.button("🔄 Dokumente indexieren", use_container_width=True):
            if st.session_state.retriever:
                with st.spinner("Indexiere Dokumente..."):
                    indexed = st.session_state.retriever.index_documents()
                    st.success(f"✅ {indexed} Chunks indexiert")
                    st.session_state.documents_indexed = True
            else:
                st.warning("Bitte erst Services initialisieren!")
    
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
                st.rerun()


def _render_chat_interface():
    """Rendert das Chat-Interface."""
    st.subheader("💬 Fragen stellen")
    
    # Chat-Verlauf anzeigen
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("sources"):
                    with st.expander("📚 Quellen"):
                        for source in msg["sources"]:
                            st.text(f"• {source}")
    
    # Chat-Input
    if prompt := st.chat_input("Stellen Sie eine Frage zu Ihren Dokumenten..."):
        if not st.session_state.rag_chat:
            st.error("Bitte erst Services initialisieren!")
            return
        
        if not st.session_state.documents_indexed:
            st.warning("Bitte erst Dokumente indexieren!")
            return
        
        # User-Nachricht anzeigen
        st.session_state.chat_messages.append({
            "role": "user",
            "content": prompt
        })
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Antwort generieren
        with st.chat_message("assistant"):
            with st.spinner("Suche in Dokumenten..."):
                response = st.session_state.rag_chat.ask(prompt)
            
            st.markdown(response.answer)
            
            # Quellen anzeigen
            if response.sources:
                sources = list(set(r.source for r in response.sources))
                with st.expander("📚 Quellen"):
                    for source in sources:
                        st.text(f"• {source}")
                
                # Nachricht speichern
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": response.answer,
                    "sources": sources
                })
            else:
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": response.answer
                })
    
    # Chat löschen Button
    if st.session_state.chat_messages:
        if st.button("🗑️ Chat löschen"):
            st.session_state.chat_messages = []
            if st.session_state.rag_chat:
                st.session_state.rag_chat.clear_history()
            st.rerun()
