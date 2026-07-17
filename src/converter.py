"""
Kernlogik für die Datei-zu-Markdown-Konvertierung.

Dieses Modul enthält die Geschäftslogik, unabhängig von der UI.
"""

import os
import tempfile
from dataclasses import dataclass
from typing import Optional

from markitdown import MarkItDown

from .providers import ProviderConfig, create_openai_client


@dataclass
class ConversionResult:
    """Ergebnis einer Konvertierung."""
    
    success: bool
    content: str
    error_message: Optional[str] = None
    
    @classmethod
    def success_result(cls, content: str) -> "ConversionResult":
        """Erstellt ein erfolgreiches Ergebnis."""
        return cls(success=True, content=content)
    
    @classmethod
    def error_result(cls, error: str) -> "ConversionResult":
        """Erstellt ein Fehler-Ergebnis."""
        return cls(success=False, content="", error_message=error)


class MarkdownConverter:
    """
    Konvertiert verschiedene Dateiformate in Markdown.
    
    Diese Klasse kapselt die markitdown-Bibliothek und bietet
    eine einfache Schnittstelle für die Konvertierung.
    """
    
    def __init__(self, provider_config: Optional[ProviderConfig] = None):
        """
        Initialisiert den Konverter.
        
        Args:
            provider_config: Optionale KI-Anbieter-Konfiguration für OCR
        """
        self._provider_config = provider_config
        self._markitdown = self._create_markitdown_instance()
    
    def _create_markitdown_instance(self) -> MarkItDown:
        """Erstellt eine MarkItDown-Instanz basierend auf der Konfiguration."""
        if self._provider_config and self._provider_config.is_configured:
            client = create_openai_client(self._provider_config)
            return MarkItDown(
                enable_plugins=True,
                llm_client=client,
                llm_model=self._provider_config.model_name
            )
        return MarkItDown()
    
    def convert_bytes(self, file_bytes: bytes, filename: str) -> ConversionResult:
        """
        Konvertiert Dateiinhalt (als Bytes) in Markdown.
        
        Args:
            file_bytes: Der Dateiinhalt als Bytes
            filename: Der ursprüngliche Dateiname (für die Dateiendung)
            
        Returns:
            ConversionResult mit dem Markdown-Inhalt oder Fehlermeldung
        """
        temp_path = self._create_temp_file(file_bytes, filename)
        
        try:
            return self._convert_file(temp_path)
        finally:
            self._cleanup_temp_file(temp_path)
    
    def convert_file(self, file_path: str) -> ConversionResult:
        """
        Konvertiert eine Datei direkt von einem Pfad.
        
        Args:
            file_path: Der Pfad zur zu konvertierenden Datei
            
        Returns:
            ConversionResult mit dem Markdown-Inhalt oder Fehlermeldung
        """
        if not os.path.exists(file_path):
            return ConversionResult.error_result(f"Datei nicht gefunden: {file_path}")
        
        return self._convert_file(file_path)
    
    def _convert_file(self, file_path: str) -> ConversionResult:
        """Interne Methode zur Dateikonvertierung."""
        try:
            result = self._markitdown.convert(file_path)
            return ConversionResult.success_result(result.text_content)
        except Exception as e:
            return ConversionResult.error_result(str(e))
    
    @staticmethod
    def _create_temp_file(file_bytes: bytes, filename: str) -> str:
        """Erstellt eine temporäre Datei mit dem gegebenen Inhalt."""
        suffix = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(file_bytes)
            return tmp_file.name
    
    @staticmethod
    def _cleanup_temp_file(file_path: str) -> None:
        """Löscht eine temporäre Datei sicher."""
        try:
            os.unlink(file_path)
        except OSError:
            pass  # Ignoriere Fehler beim Löschen
