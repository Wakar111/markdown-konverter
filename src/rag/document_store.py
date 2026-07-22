"""
Dokumentenspeicher für die Verwaltung und Verarbeitung von Dokumenten.

Verantwortlich für:
- Konvertierung von Dokumenten zu Markdown
- Aufteilen von Dokumenten in Chunks
- Verwaltung von Metadaten
"""

import os
import tempfile
import hashlib
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from markitdown import MarkItDown
from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass
class Document:
    """Repräsentiert ein verarbeitetes Dokument."""
    
    id: str
    filename: str
    content: str
    upload_date: datetime
    metadata: dict = field(default_factory=dict)
    
    @property
    def chunk_count(self) -> int:
        """Gibt die Anzahl der Chunks zurück (falls gesetzt)."""
        return self.metadata.get("chunk_count", 0)


@dataclass
class DocumentChunk:
    """Ein Textabschnitt aus einem Dokument."""
    
    id: str
    document_id: str
    content: str
    metadata: dict = field(default_factory=dict)
    
    @property
    def source_filename(self) -> str:
        """Gibt den Dateinamen des Quelldokuments zurück."""
        return self.metadata.get("filename", "Unbekannt")


class DocumentStore:
    """
    Verwaltet Dokumente und deren Chunks.
    
    Konvertiert Dokumente zu Markdown und teilt sie in 
    durchsuchbare Abschnitte auf.
    """
    
    DEFAULT_CHUNK_SIZE = 1000
    DEFAULT_CHUNK_OVERLAP = 200
    
    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        markitdown_instance: Optional[MarkItDown] = None
    ):
        """
        Initialisiert den DocumentStore.
        
        Args:
            chunk_size: Maximale Größe eines Chunks in Zeichen
            chunk_overlap: Überlappung zwischen Chunks
            markitdown_instance: Optionale MarkItDown-Instanz für OCR
        """
        self._documents: dict[str, Document] = {}
        self._chunks: list[DocumentChunk] = []
        self._markitdown = markitdown_instance or MarkItDown()
        
        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    @property
    def documents(self) -> list[Document]:
        """Liste aller gespeicherten Dokumente."""
        return list(self._documents.values())
    
    @property
    def chunks(self) -> list[DocumentChunk]:
        """Liste aller Chunks."""
        return self._chunks.copy()
    
    @property
    def document_count(self) -> int:
        """Anzahl der gespeicherten Dokumente."""
        return len(self._documents)
    
    @property
    def chunk_count(self) -> int:
        """Gesamtanzahl der Chunks."""
        return len(self._chunks)
    
    def add_document(self, file_bytes: bytes, filename: str) -> Document:
        """
        Fügt ein Dokument hinzu und verarbeitet es.
        
        Args:
            file_bytes: Dateiinhalt als Bytes
            filename: Originaler Dateiname
            
        Returns:
            Das verarbeitete Document-Objekt
        """
        # Dokument-ID generieren
        doc_id = self._generate_document_id(file_bytes, filename)
        
        # Prüfen ob Dokument bereits existiert
        if doc_id in self._documents:
            return self._documents[doc_id]
        
        # Dokument zu Markdown konvertieren
        markdown_content = self._convert_to_markdown(file_bytes, filename)
        
        # Document-Objekt erstellen
        document = Document(
            id=doc_id,
            filename=filename,
            content=markdown_content,
            upload_date=datetime.now(),
            metadata={"original_size": len(file_bytes)}
        )
        
        # Chunks erstellen
        chunks = self._create_chunks(document)
        document.metadata["chunk_count"] = len(chunks)
        
        # Speichern
        self._documents[doc_id] = document
        self._chunks.extend(chunks)
        
        return document
    
    def add_document_from_content(
        self,
        file_bytes: bytes,
        filename: str,
        markdown_content: str
    ) -> Document:
        """
        Fügt ein Dokument mit bereits vorhandenem Markdown-Inhalt hinzu.
        
        Nützlich, wenn die Datei bereits an anderer Stelle (z.B. im
        Konverter) konvertiert wurde und keine erneute (ggf. teure OCR-)
        Konvertierung nötig ist.
        
        Args:
            file_bytes: Dateiinhalt als Bytes (für die Dokument-ID)
            filename: Originaler Dateiname
            markdown_content: Bereits konvertierter Markdown-Inhalt
            
        Returns:
            Das verarbeitete Document-Objekt
        """
        doc_id = self._generate_document_id(file_bytes, filename)
        
        if doc_id in self._documents:
            return self._documents[doc_id]
        
        document = Document(
            id=doc_id,
            filename=filename,
            content=markdown_content,
            upload_date=datetime.now(),
            metadata={"original_size": len(file_bytes)}
        )
        
        chunks = self._create_chunks(document)
        document.metadata["chunk_count"] = len(chunks)
        
        self._documents[doc_id] = document
        self._chunks.extend(chunks)
        
        return document
    
    def remove_document(self, document_id: str) -> bool:
        """
        Entfernt ein Dokument und dessen Chunks.
        
        Args:
            document_id: ID des zu entfernenden Dokuments
            
        Returns:
            True wenn erfolgreich, False wenn nicht gefunden
        """
        if document_id not in self._documents:
            return False
        
        # Chunks entfernen
        self._chunks = [c for c in self._chunks if c.document_id != document_id]
        
        # Dokument entfernen
        del self._documents[document_id]
        
        return True
    
    def clear(self) -> None:
        """Entfernt alle Dokumente und Chunks."""
        self._documents.clear()
        self._chunks.clear()
    
    def get_document(self, document_id: str) -> Optional[Document]:
        """Gibt ein Dokument anhand seiner ID zurück."""
        return self._documents.get(document_id)
    
    def get_chunks_for_document(self, document_id: str) -> list[DocumentChunk]:
        """Gibt alle Chunks eines bestimmten Dokuments zurück."""
        return [c for c in self._chunks if c.document_id == document_id]
    
    def update_markitdown(self, markitdown_instance: MarkItDown) -> None:
        """Aktualisiert die MarkItDown-Instanz (z.B. für OCR)."""
        self._markitdown = markitdown_instance
    
    def _convert_to_markdown(self, file_bytes: bytes, filename: str) -> str:
        """Konvertiert eine Datei zu Markdown."""
        suffix = os.path.splitext(filename)[1]
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_path = tmp_file.name
        
        try:
            result = self._markitdown.convert(tmp_path)
            return result.text_content
        finally:
            os.unlink(tmp_path)
    
    def _create_chunks(self, document: Document) -> list[DocumentChunk]:
        """Teilt ein Dokument in Chunks auf."""
        texts = self._text_splitter.split_text(document.content)
        
        chunks = []
        for i, text in enumerate(texts):
            chunk = DocumentChunk(
                id=f"{document.id}_chunk_{i}",
                document_id=document.id,
                content=text,
                metadata={
                    "filename": document.filename,
                    "chunk_index": i,
                    "total_chunks": len(texts)
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    @staticmethod
    def _generate_document_id(file_bytes: bytes, filename: str) -> str:
        """Generiert eine eindeutige ID für ein Dokument."""
        content_hash = hashlib.md5(file_bytes).hexdigest()[:8]
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        return f"{safe_filename}_{content_hash}"
