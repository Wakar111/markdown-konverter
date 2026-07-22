"""
Embedding-Service für die Vektorisierung von Dokumenten.

Unterstützt verschiedene Embedding-Provider:
- OpenAI
- Google Gemini
- Lokale Modelle (sentence-transformers)
"""

from enum import Enum
from typing import Optional
from dataclasses import dataclass

from langchain_core.embeddings import Embeddings
from openai import OpenAI


class EmbeddingProvider(Enum):
    """Verfügbare Embedding-Provider."""
    
    LOCAL = "Lokal (kostenlos)"
    OPENAI = "OpenAI"
    GEMINI = "Google Gemini"
    NVIDIA = "NVIDIA NIM"


@dataclass
class EmbeddingConfig:
    """Konfiguration für den Embedding-Service."""
    
    provider: EmbeddingProvider
    api_key: Optional[str] = None
    model_name: Optional[str] = None


# Standard-Modelle für jeden Provider
DEFAULT_MODELS = {
    EmbeddingProvider.LOCAL: "all-MiniLM-L6-v2",
    EmbeddingProvider.OPENAI: "text-embedding-3-small",
    EmbeddingProvider.GEMINI: "models/embedding-001",
    EmbeddingProvider.NVIDIA: "nvidia/nv-embedqa-e5-v5",
}

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"


class NvidiaEmbeddings(Embeddings):
    """
    Embeddings-Wrapper für NVIDIA NIM asymmetrische Modelle
    (z.B. nv-embedqa-e5-v5), die einen 'input_type' Parameter
    benötigen: 'passage' für Dokumente, 'query' für Suchanfragen.
    """
    
    def __init__(self, api_key: str, model: str, base_url: str = NVIDIA_BASE_URL):
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = self._client.embeddings.create(
            input=texts,
            model=self._model,
            extra_body={"input_type": "passage"}
        )
        return [item.embedding for item in response.data]
    
    def embed_query(self, text: str) -> list[float]:
        response = self._client.embeddings.create(
            input=[text],
            model=self._model,
            extra_body={"input_type": "query"}
        )
        return response.data[0].embedding


class EmbeddingService:
    """
    Service für die Erstellung von Text-Embeddings.
    
    Embeddings sind numerische Repräsentationen von Text,
    die für die Ähnlichkeitssuche verwendet werden.
    """
    
    def __init__(self, config: Optional[EmbeddingConfig] = None):
        """
        Initialisiert den Embedding-Service.
        
        Args:
            config: Konfiguration für den Provider.
                   Wenn None, wird der lokale Provider verwendet.
        """
        if config is None:
            config = EmbeddingConfig(provider=EmbeddingProvider.LOCAL)
        
        self._config = config
        self._embeddings = self._create_embeddings()
    
    @property
    def embeddings(self) -> Embeddings:
        """Gibt das Embeddings-Objekt zurück."""
        return self._embeddings
    
    @property
    def provider_name(self) -> str:
        """Gibt den Namen des aktuellen Providers zurück."""
        return self._config.provider.value
    
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Erstellt Embeddings für eine Liste von Texten.
        
        Args:
            texts: Liste von Texten
            
        Returns:
            Liste von Embedding-Vektoren
        """
        return self._embeddings.embed_documents(texts)
    
    def embed_query(self, query: str) -> list[float]:
        """
        Erstellt ein Embedding für eine Suchanfrage.
        
        Args:
            query: Die Suchanfrage
            
        Returns:
            Embedding-Vektor
        """
        return self._embeddings.embed_query(query)
    
    def _create_embeddings(self) -> Embeddings:
        """Erstellt das passende Embeddings-Objekt basierend auf der Konfiguration."""
        provider = self._config.provider
        model_name = self._config.model_name or DEFAULT_MODELS.get(provider)
        
        if provider == EmbeddingProvider.LOCAL:
            return self._create_local_embeddings(model_name)
        
        if provider == EmbeddingProvider.OPENAI:
            return self._create_openai_embeddings(model_name)
        
        if provider == EmbeddingProvider.GEMINI:
            return self._create_gemini_embeddings(model_name)
        
        if provider == EmbeddingProvider.NVIDIA:
            return self._create_nvidia_embeddings(model_name)
        
        # Fallback zu lokalen Embeddings
        return self._create_local_embeddings(DEFAULT_MODELS[EmbeddingProvider.LOCAL])
    
    def _create_local_embeddings(self, model_name: str) -> Embeddings:
        """Erstellt lokale Embeddings mit sentence-transformers."""
        from langchain_community.embeddings import HuggingFaceEmbeddings
        
        return HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
    
    def _create_openai_embeddings(self, model_name: str) -> Embeddings:
        """Erstellt OpenAI Embeddings."""
        from langchain_openai import OpenAIEmbeddings
        
        if not self._config.api_key:
            raise ValueError("OpenAI API-Key erforderlich")
        
        return OpenAIEmbeddings(
            model=model_name,
            openai_api_key=self._config.api_key
        )
    
    def _create_gemini_embeddings(self, model_name: str) -> Embeddings:
        """Erstellt Google Gemini Embeddings."""
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        
        if not self._config.api_key:
            raise ValueError("Gemini API-Key erforderlich")
        
        return GoogleGenerativeAIEmbeddings(
            model=model_name,
            google_api_key=self._config.api_key
        )
    
    def _create_nvidia_embeddings(self, model_name: str) -> Embeddings:
        """Erstellt NVIDIA NIM Embeddings (asymmetrisches Modell mit input_type)."""
        if not self._config.api_key:
            raise ValueError("NVIDIA NIM API-Key erforderlich")
        
        return NvidiaEmbeddings(
            api_key=self._config.api_key,
            model=model_name,
            base_url=NVIDIA_BASE_URL
        )


def create_embedding_service(
    provider: EmbeddingProvider,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None
) -> EmbeddingService:
    """
    Factory-Funktion zum Erstellen eines EmbeddingService.
    
    Args:
        provider: Der gewünschte Provider
        api_key: API-Key (falls erforderlich)
        model_name: Optionaler Modellname
        
    Returns:
        Konfigurierter EmbeddingService
    """
    config = EmbeddingConfig(
        provider=provider,
        api_key=api_key,
        model_name=model_name
    )
    return EmbeddingService(config)
