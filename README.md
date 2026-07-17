# 📄 MarkItDown Konverter

Eine Web-Anwendung zur Konvertierung verschiedener Dateiformate in Markdown – powered by [Microsoft MarkItDown](https://github.com/microsoft/markitdown).

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

- **Drag & Drop Upload** – Dateien einfach per Drag & Drop oder Dateisuche hochladen
- **Viele Dateiformate** – PDF, Word, PowerPoint, Excel, Bilder, HTML, CSV, JSON und mehr
- **Live-Vorschau** – Sofortige Markdown-Vorschau nach der Konvertierung
- **Ein-Klick-Kopieren** – Markdown-Code direkt in die Zwischenablage kopieren
- **Optional: KI-gestützte OCR** – Bilder und Diagramme in PDFs erkennen mit Vision-Modellen

## 🛠️ Technologien

| Technologie | Verwendung |
|-------------|------------|
| **Python 3.10+** | Programmiersprache |
| **Streamlit** | Web-UI Framework |
| **Microsoft MarkItDown** | Datei-zu-Markdown Konvertierung |
| **OpenAI API** (optional) | Vision-basierte OCR für Bilder/Diagramme |

## 📁 Unterstützte Dateiformate

- **Dokumente:** PDF, Word (.docx), PowerPoint (.pptx), Excel (.xlsx)
- **Bilder:** PNG, JPG, JPEG, GIF, BMP, TIFF
- **Web & Daten:** HTML, CSV, JSON, XML
- **Andere:** ZIP-Archive, EPub, Outlook-Nachrichten (.msg)

## 🚀 Installation & Start

### Voraussetzungen

- Python 3.10 oder höher
- pip (Python Paketmanager)

### Lokale Installation

```bash
# 1. Repository klonen
git clone https://github.com/YOUR_USERNAME/MarkItDown.git
cd MarkItDown

# 2. Virtuelle Umgebung erstellen und aktivieren
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# oder: venv\Scripts\activate  # Windows

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. Anwendung starten
streamlit run app.py
```

Die Anwendung öffnet sich automatisch im Browser unter `http://localhost:8501`.

### Schnellstart (wenn bereits installiert)

```bash
cd MarkItDown
source venv/bin/activate
streamlit run app.py
```

## 🤖 KI-Integration (Optional)

Für bessere Ergebnisse bei **Bildern und Diagrammen** in PDFs können Sie einen KI-Anbieter konfigurieren. Die App unterstützt mehrere Anbieter:

### Unterstützte Anbieter

| Anbieter | Kosten | Beschreibung |
|----------|--------|--------------|
| **Google Gemini** | Kostenlos | Großzügiger Free Tier, empfohlen! |
| **Ollama** | Kostenlos | Läuft komplett lokal auf Ihrem Rechner |
| **OpenAI** | Bezahlt | GPT-4o Vision |
| **Andere** | Variiert | Jede OpenAI-kompatible API |

### Google Gemini einrichten (kostenlos)

1. Kostenlosen API-Key holen: https://aistudio.google.com/app/apikey
2. In der App-Sidebar "Google Gemini" auswählen
3. API-Key eingeben
4. Modell wählen (z.B. `gemini-2.0-flash`)

### Ollama einrichten (lokal & kostenlos)

1. Ollama installieren: https://ollama.com
2. Vision-Modell herunterladen:
   ```bash
   ollama pull llava
   ```
3. In der App-Sidebar "Ollama (lokal)" auswählen
4. Standard-URL belassen: `http://localhost:11434/v1`

## 📂 Projektstruktur

```
MarkItDown/
├── app.py                      # Hauptanwendung (Einstiegspunkt)
├── requirements.txt            # Python-Abhängigkeiten
├── README.md                   # Diese Datei
├── PLAN.md                     # Entwicklungsplan
└── src/
    ├── __init__.py
    ├── config.py               # Konfiguration & UI-Texte
    ├── converter.py            # Konvertierungslogik
    ├── providers.py            # KI-Anbieter-Definitionen
    └── components/
        ├── __init__.py
        ├── sidebar.py          # Sidebar-Komponente
        ├── file_upload.py      # Upload-Komponente
        └── result_display.py   # Ergebnis-Anzeige
```

## 🔧 Entwicklung

### Code-Struktur

Das Projekt folgt **Clean Code**-Prinzipien:
- **Separation of Concerns** – UI, Logik und Konfiguration sind getrennt
- **Single Responsibility** – Jedes Modul hat eine klare Aufgabe
- **Dependency Injection** – Flexible Konfiguration der KI-Anbieter

### Tests ausführen

```bash
# (Tests noch nicht implementiert)
pytest tests/
```

## 📝 Verwendung

1. **Anwendung starten** mit `streamlit run app.py`
2. **Datei hochladen** per Drag & Drop oder Klick
3. **Ergebnis ansehen** in der Vorschau oder als Markdown-Code
4. **Kopieren** mit dem Kopier-Button im Markdown-Code Tab

## 🤝 Beitragen

Pull Requests sind willkommen! Für größere Änderungen bitte zuerst ein Issue erstellen.

## 📄 Lizenz

MIT License – siehe [LICENSE](LICENSE) für Details.

## 🙏 Credits

- [Microsoft MarkItDown](https://github.com/microsoft/markitdown) – Die Konvertierungs-Engine
- [Streamlit](https://streamlit.io/) – Das Web-UI Framework
