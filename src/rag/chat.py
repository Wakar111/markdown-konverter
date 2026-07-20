"""
Chat-Logik für RAG-basierte Dokumentenabfragen.

Kombiniert Retrieval mit LLM-Antwortgenerierung.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum

from openai import OpenAI

from .retriever import DocumentRetriever, RetrievalResult


class ChatProvider(Enum):
    """Verfügbare Chat-Provider."""
    
    OPENAI = "OpenAI"
    GEMINI = "Google Gemini"
    OLLAMA = "Ollama (lokal)"


@dataclass
class ChatConfig:
    """Konfiguration für den Chat-Service."""
    
    provider: ChatProvider
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_name: str = "gpt-4o-mini"


@dataclass
class ChatMessage:
    """Eine Chat-Nachricht."""
    
    role: str  # "user" oder "assistant"
    content: str
    sources: list[str] = None  # Quelldokumente
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = []


@dataclass
class ChatResponse:
    """Antwort des Chat-Systems."""
    
    answer: str
    sources: list[RetrievalResult]
    context_used: str


# System-Prompt für die Dokumentensuche
SYSTEM_PROMPT = """Du bist ein hilfreicher Assistent für die Dokumentensuche.
Du beantwortest Fragen basierend auf den bereitgestellten Dokumentenausschnitten.

Regeln:
1. Antworte NUR basierend auf den bereitgestellten Dokumentenausschnitten.
2. Wenn die Antwort nicht in den Dokumenten gefunden werden kann, sage das ehrlich.
3. Zitiere relevante Stellen und nenne die Quelldokumente.
4. Antworte auf Deutsch.
5. Sei präzise und hilfreich.

Dokumentenausschnitte:
{context}
"""


class RAGChat:
    """
    Chat-System mit Retrieval-Augmented Generation.
    
    Sucht relevante Dokumentenabschnitte und generiert
    Antworten basierend auf dem gefundenen Kontext.
    """
    
    def __init__(
        self,
        retriever: DocumentRetriever,
        config: ChatConfig
    ):
        """
        Initialisiert den RAG-Chat.
        
        Args:
            retriever: Der DocumentRetriever für die Suche
            config: Chat-Konfiguration
        """
        self._retriever = retriever
        self._config = config
        self._client = self._create_client()
        self._history: list[ChatMessage] = []
    
    @property
    def history(self) -> list[ChatMessage]:
        """Chat-Verlauf."""
        return self._history.copy()
    
    def ask(self, question: str, top_k: int = 5) -> ChatResponse:
        """
        Stellt eine Frage an die Dokumentenbasis.
        
        Args:
            question: Die Benutzerfrage
            top_k: Anzahl der zu verwendenden Dokumente
            
        Returns:
            ChatResponse mit Antwort und Quellen
        """
        # Relevante Dokumente suchen
        results = self._retriever.search(question, top_k=top_k)
        
        # Kontext aufbauen
        context = self._build_context(results)
        
        # Antwort generieren
        answer = self._generate_answer(question, context)
        
        # Quellen extrahieren
        source_files = list(set(r.source for r in results))
        
        # Historie aktualisieren
        self._history.append(ChatMessage(role="user", content=question))
        self._history.append(ChatMessage(
            role="assistant",
            content=answer,
            sources=source_files
        ))
        
        return ChatResponse(
            answer=answer,
            sources=results,
            context_used=context
        )
    
    def clear_history(self) -> None:
        """Löscht den Chat-Verlauf."""
        self._history.clear()
    
    def _create_client(self) -> OpenAI:
        """Erstellt den OpenAI-kompatiblen Client."""
        client_kwargs = {}
        
        if self._config.api_key:
            client_kwargs["api_key"] = self._config.api_key
        
        if self._config.base_url:
            client_kwargs["base_url"] = self._config.base_url
        
        # Provider-spezifische Anpassungen
        if self._config.provider == ChatProvider.GEMINI:
            client_kwargs["base_url"] = "https://generativelanguage.googleapis.com/v1beta/openai/"
        elif self._config.provider == ChatProvider.OLLAMA:
            client_kwargs["base_url"] = self._config.base_url or "http://localhost:11434/v1"
            client_kwargs["api_key"] = "ollama"
        
        return OpenAI(**client_kwargs)
    
    def _build_context(self, results: list[RetrievalResult]) -> str:
        """Baut den Kontext aus den Suchergebnissen auf."""
        if not results:
            return "Keine relevanten Dokumente gefunden."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[Dokument {i}: {result.source}]\n{result.content}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    def _generate_answer(self, question: str, context: str) -> str:
        """Generiert eine Antwort mit dem LLM."""
        system_message = SYSTEM_PROMPT.format(context=context)
        
        try:
            response = self._client.chat.completions.create(
                model=self._config.model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": question}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Fehler bei der Antwortgenerierung: {str(e)}"


def create_rag_chat(
    retriever: DocumentRetriever,
    provider: ChatProvider,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    base_url: Optional[str] = None
) -> RAGChat:
    """
    Factory-Funktion zum Erstellen eines RAGChat.
    
    Args:
        retriever: Der DocumentRetriever
        provider: Chat-Provider
        api_key: API-Key
        model_name: Modellname
        base_url: Optionale Base-URL
        
    Returns:
        Konfigurierter RAGChat
    """
    # Standard-Modelle für Provider
    default_models = {
        ChatProvider.OPENAI: "gpt-4o-mini",
        ChatProvider.GEMINI: "gemini-2.0-flash",
        ChatProvider.OLLAMA: "llama3.2",
    }
    
    config = ChatConfig(
        provider=provider,
        api_key=api_key,
        base_url=base_url,
        model_name=model_name or default_models.get(provider, "gpt-4o-mini")
    )
    
    return RAGChat(retriever, config)
