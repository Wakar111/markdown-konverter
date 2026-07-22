"""
Konfiguration und Konstanten für die MarkItDown-Anwendung.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    """Unveränderliche Anwendungskonfiguration."""
    
    PAGE_TITLE: str = "MarkItDown Konverter"
    PAGE_ICON: str = "📄"
    LAYOUT: str = "wide"


@dataclass(frozen=True)
class UIText:
    """Alle UI-Texte zentral verwaltet für einfache Lokalisierung."""
    
    # Header
    APP_TITLE: str = "📄 MarkItDown Konverter"
    APP_DESCRIPTION: str = "Laden Sie eine Datei hoch (per Drag & Drop oder Dateisuche), um sie in Markdown zu konvertieren."
    
    # Sidebar
    SETTINGS_HEADER: str = "⚙️ Einstellungen"
    PROVIDER_HEADER: str = "### 🤖 KI-Anbieter (Optional)"
    PROVIDER_DESCRIPTION: str = (
        "Für bessere Ergebnisse bei **Bildern und Diagrammen** können Sie "
        "einen KI-Anbieter mit Vision-Modell konfigurieren."
    )
    
    # Status Messages
    STATUS_OCR_ACTIVE: str = "✅ OCR mit {provider} aktiviert"
    STATUS_STANDARD_MODE: str = "ℹ️ Standard-Modus (nur Text-Extraktion)"
    STATUS_HINT: str = (
        "**Hinweis:** Ohne KI-Anbieter werden nur Textinhalte extrahiert. "
        "Bilder und Diagramme in PDFs werden übersprungen."
    )
    
    # File Upload
    UPLOAD_LABEL: str = "Datei hier ablegen oder klicken zum Hochladen"
    UPLOAD_HELP: str = "Unterstützt verschiedene Dateiformate wie PDF, DOCX, PPTX, XLSX, Bilder und mehr."
    
    # Conversion
    CONVERTING_MESSAGE: str = "Konvertiere '{filename}'..."
    CONVERSION_SUCCESS: str = "✅ Konvertierung erfolgreich!"
    CONVERSION_ERROR: str = "❌ Fehler bei der Konvertierung: {error}"
    CONVERSION_ERROR_HINT: str = "Stellen Sie sicher, dass das Dateiformat unterstützt wird."
    
    # Result Display
    TAB_PREVIEW: str = "📖 Vorschau"
    TAB_MARKDOWN: str = "📝 Markdown-Code"
    TEXTAREA_LABEL: str = "Markdown-Inhalt"
    TEXTAREA_HELP: str = "Nutzen Sie den Kopieren-Button oben rechts für den gesamten Inhalt"
    LARGE_CONTENT_WARNING: str = (
        "⚠️ Große Ausgabe ({length:,} Zeichen) – die Vorschau zeigt nur die ersten "
        "{limit:,} Zeichen an, um lange Ladezeiten im Browser zu vermeiden. "
        "Den vollständigen Inhalt finden Sie im Tab **Markdown-Code** oder über den Download-Button."
    )
    DOWNLOAD_BUTTON_LABEL: str = "⬇️ Markdown als Datei herunterladen"
    
    # Supported Formats
    FORMATS_EXPANDER: str = "📋 Unterstützte Dateiformate"
    FORMATS_LIST: str = """
- **Dokumente:** PDF, Word (.docx), PowerPoint (.pptx), Excel (.xlsx)
- **Bilder:** PNG, JPG, JPEG, GIF, BMP, TIFF (Text wird per OCR extrahiert)
- **Web & Daten:** HTML, CSV, JSON, XML
- **Andere:** ZIP-Archive, EPub, Outlook-Nachrichten (.msg)

💡 **Tipp:** Mit einem KI-Anbieter (in der Sidebar) können auch Bilder und Diagramme in PDFs erkannt werden!
"""
    
    # Footer
    FOOTER_HTML: str = (
        "<div style='text-align: center; color: gray;'>"
        "Powered by <a href='https://github.com/microsoft/markitdown'>Microsoft MarkItDown</a>"
        "</div>"
    )


# Singleton-Instanzen für einfachen Import
APP_CONFIG = AppConfig()
UI_TEXT = UIText()
