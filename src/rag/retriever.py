"""
Document Retriever für die Ähnlichkeitssuche in Dokumenten.

Verwendet ChromaDB als Vektordatenbank für effiziente Suche.
"""

import os
from typing import Optional
from dataclasses import dataclass

import chromadb
from chromadb.config import Settings

from .document_store import DocumentStore, DocumentChunk
from .embeddings import EmbeddingService


@dataclass
class RetrievalResult:
    """Ergebnis einer Suchanfrage."""
    
    chunk: DocumentChunk
    score: float
    
    @property
    def content(self) -> str:
        """Der Textinhalt des Chunks."""
        return self.chunk.content
    
    @property
    def source(self) -> str:
        """Die Quelldatei."""
        return self.chunk.source_filename


class DocumentRetriever:
    """
    Sucht relevante Dokumentenabschnitte basierend auf einer Anfrage.
    
    Verwendet ChromaDB für die Vektorspeicherung und -suche.
    """
    
    COLLECTION_NAME = "documents"
    
    def __init__(
        self,
        document_store: DocumentStore,
        embedding_service: EmbeddingService,
        persist_directory: Optional[str] = None
    ):
        """
        Initialisiert den Retriever.
        
        Args:
            document_store: Der DocumentStore mit den Chunks
            embedding_service: Service für Embeddings
            persist_directory: Optionales Verzeichnis für Persistenz
        """
        self._document_store = document_store
        self._embedding_service = embedding_service
        self._persist_directory = persist_directory
        
        # ChromaDB Client erstellen
        self._client = self._create_client()
        self._collection = self._get_or_create_collection()
        
        # Bereits indexierte Chunk-IDs
        self._indexed_chunks: set[str] = set()
    
    @property
    def indexed_count(self) -> int:
        """Anzahl der indexierten Chunks."""
        return len(self._indexed_chunks)
    
    def index_documents(self) -> int:
        """
        Indexiert alle neuen Chunks aus dem DocumentStore.
        
        Returns:
            Anzahl der neu indexierten Chunks
        """
        chunks = self._document_store.chunks
        new_chunks = [c for c in chunks if c.id not in self._indexed_chunks]
        
        if not new_chunks:
            return 0
        
        # Embeddings erstellen
        texts = [chunk.content for chunk in new_chunks]
        embeddings = self._embedding_service.embed_texts(texts)
        
        # Zu ChromaDB hinzufügen
        self._collection.add(
            ids=[chunk.id for chunk in new_chunks],
            embeddings=embeddings,
            documents=texts,
            metadatas=[chunk.metadata for chunk in new_chunks]
        )
        
        # Indexed-Set aktualisieren
        for chunk in new_chunks:
            self._indexed_chunks.add(chunk.id)
        
        return len(new_chunks)
    
    def search(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        """
        Sucht nach relevanten Dokumentenabschnitten.
        
        Args:
            query: Die Suchanfrage
            top_k: Maximale Anzahl der Ergebnisse
            
        Returns:
            Liste von RetrievalResult-Objekten
        """
        if self.indexed_count == 0:
            return []
        
        # Query-Embedding erstellen
        query_embedding = self._embedding_service.embed_query(query)
        
        # In ChromaDB suchen
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.indexed_count)
        )
        
        # Ergebnisse in RetrievalResult umwandeln
        retrieval_results = []
        
        if results["ids"] and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                # Chunk aus DocumentStore holen
                chunk = self._find_chunk_by_id(chunk_id)
                if chunk:
                    # Distance zu Score umwandeln (niedrigere Distance = höherer Score)
                    distance = results["distances"][0][i] if results["distances"] else 0
                    score = 1.0 / (1.0 + distance)
                    
                    retrieval_results.append(RetrievalResult(
                        chunk=chunk,
                        score=score
                    ))
        
        return retrieval_results
    
    def clear_index(self) -> None:
        """Löscht den gesamten Index."""
        self._client.delete_collection(self.COLLECTION_NAME)
        self._collection = self._get_or_create_collection()
        self._indexed_chunks.clear()
    
    def remove_document(self, document_id: str) -> int:
        """
        Entfernt ein Dokument aus dem Index.
        
        Args:
            document_id: ID des zu entfernenden Dokuments
            
        Returns:
            Anzahl der entfernten Chunks
        """
        # Chunks finden, die zu diesem Dokument gehören
        chunks_to_remove = [
            chunk_id for chunk_id in self._indexed_chunks
            if chunk_id.startswith(document_id)
        ]
        
        if not chunks_to_remove:
            return 0
        
        # Aus ChromaDB entfernen
        self._collection.delete(ids=chunks_to_remove)
        
        # Aus indexed_chunks entfernen
        for chunk_id in chunks_to_remove:
            self._indexed_chunks.discard(chunk_id)
        
        return len(chunks_to_remove)
    
    def _create_client(self) -> chromadb.Client:
        """Erstellt den ChromaDB Client."""
        if self._persist_directory:
            os.makedirs(self._persist_directory, exist_ok=True)
            return chromadb.PersistentClient(
                path=self._persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
        
        return chromadb.Client(Settings(anonymized_telemetry=False))
    
    def _get_or_create_collection(self) -> chromadb.Collection:
        """Holt oder erstellt die Collection."""
        return self._client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    
    def _find_chunk_by_id(self, chunk_id: str) -> Optional[DocumentChunk]:
        """Findet einen Chunk anhand seiner ID."""
        for chunk in self._document_store.chunks:
            if chunk.id == chunk_id:
                return chunk
        return None
