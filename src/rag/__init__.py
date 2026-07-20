"""
RAG (Retrieval-Augmented Generation) Modul für Dokumentensuche.

Ermöglicht das Hochladen mehrerer Dokumente und die Beantwortung
von Fragen basierend auf dem Dokumenteninhalt.
"""

from .document_store import DocumentStore
from .embeddings import EmbeddingService, EmbeddingProvider
from .retriever import DocumentRetriever
from .chat import RAGChat

__all__ = [
    "DocumentStore",
    "EmbeddingService",
    "EmbeddingProvider",
    "DocumentRetriever",
    "RAGChat",
]
