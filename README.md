# 📄 MarkItDown Konverter

Eine Web-Anwendung zur Konvertierung verschiedener Dateiformate in Markdown und zur KI-gestützten Dokumentensuche – powered by [Microsoft MarkItDown](https://github.com/microsoft/markitdown).

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

### 📄 Konverter
- **Drag & Drop Upload** – Dateien einfach per Drag & Drop oder Dateisuche hochladen
- **Viele Dateiformate** – PDF, Word, PowerPoint, Excel, Bilder, HTML, CSV, JSON und mehr
- **Live-Vorschau** – Sofortige Markdown-Vorschau nach der Konvertierung
- **Ein-Klick-Kopieren** – Markdown-Code direkt in die Zwischenablage kopieren
- **Download-Button** – Vollständigen Markdown-Inhalt direkt als Datei herunterladen
- **KI-gestützte OCR** – Bilder und Diagramme in PDFs erkennen mit Vision-Modellen
- **NVIDIA NIM Vision OCR** – NVIDIA NIM als Vision-Provider für hochwertige Bilderkennung
- **Performante Vorschau** – Sehr große Ausgaben (z.B. CSV mit vielen Zeilen) werden gekürzt angezeigt, um lange Browser-Ladezeiten zu vermeiden

### 🔍 Dokumentensuche (RAG)
- **Multi-Dokument-Upload** – Mehrere PDFs, Word-Dateien und Bilder gleichzeitig hochladen
- **Bild-Upload mit Vision OCR** – PNG/JPG/JPEG-Dateien werden per KI-Vision-Modell in Text umgewandelt und durchsuchbar
- **KI-gestützte Suche** – Stellen Sie Fragen zu Ihren Dokumenten im Chat-Interface
- **ChatGPT-style Chat-Fenster** – Scrollbares Chat-Fenster mit fester Hoehe, Input-Feld am Boden (wie bei ChatGPT/Copilot)
- **Quellenangaben** – Jede Antwort zeigt, aus welchem Dokument die Information stammt
- **Dokumenten-genaue Kontextbildung** – Mehrere Chunks derselben Datei werden zu einem Dokument zusammengefasst (korrekte Anzahl bei "Wie viele Dokumente siehst du?")
- **Token-effizient** – Durch RAG werden nur relevante Textabschnitte an die KI gesendet
- **Automatische Indexierung** – Dokumente werden nach dem Upload automatisch indexiert (idempotent, kein Button noetig)
- **Zuverlässiges Löschen** – Gelöschte Dokumente werden nicht mehr automatisch wieder hinzugefügt
- **Ideal fuer Buchhaltung** – Finden Sie schnell Steuersaetze, Adressen, Rechnungsdetails

### 🔄 Datei-Sharing zwischen Konverter & Dokumentensuche
- **Bidirektionale Übernahme** – Eine im Konverter konvertierte Datei erscheint automatisch in der Dokumentensuche und umgekehrt
- **Keine erneute Konvertierung** – Bereits konvertierter Markdown-Inhalt wird direkt übernommen (kein doppelter OCR-Aufruf)
- **Stale-Upload-Erkennung** – Content-Hash-Vergleich verhindert, dass eine alte, im Uploader "klebende" Datei eine neuere geteilte Datei blockiert

### ⚙️ Smarte .env-Konfiguration
- **Automatische Provider-Erkennung** – API-Keys aus .env werden automatisch erkannt und verwendet
- **API-Keys versteckt** – Keys aus .env werden im UI nicht angezeigt, nur ein Indikator zeigt deren Presence
- **Explizite Override-Moeglichkeit** – Per Checkbox kann der Benutzer eigene Provider/Modelle/Keys eingeben
- **Automatische Service-Initialisierung** – Bei .env-Defaults werden Services automatisch initialisiert (kein Button-Klick noetig)
- **Getrennte Embedding- & Chat-Provider** – Verschiedene Provider fuer Embeddings und Chat-Modelle waehlbar
- **Geteilter Vision-Provider** – Vision-Provider-Auswahl wird zwischen Konverter und Dokumentensuche synchronisiert

## 🛠️ Technologien

| Technologie | Verwendung |
|-------------|------------|
| **Python 3.10+** | Programmiersprache |
| **Streamlit** | Web-UI Framework |
| **Microsoft MarkItDown** | Datei-zu-Markdown Konvertierung |
| **ChromaDB** | Vektordatenbank fuer Dokumentensuche |
| **LangChain** | RAG-Framework & Text-Chunking |
| **OpenAI** | KI-Provider fuer OCR, Chat & Embeddings |
| **Google Gemini** | KI-Provider fuer OCR, Chat & Embeddings |
| **NVIDIA NIM** | KI-Provider fuer OCR, Chat & Embeddings |
| **Ollama** | Lokaler KI-Provider fuer Chat |

## 📁 Unterstützte Dateiformate

- **Dokumente:** PDF, Word (.docx, .doc), PowerPoint (.pptx), Excel (.xlsx)
- **Bilder:** PNG, JPG, JPEG (mit Vision OCR durchsuchbar)
- **Web & Daten:** HTML, CSV, JSON, XML
- **Andere:** ZIP-Archive, EPub, Outlook-Nachrichten (.msg)

## 🚀 Installation & Start

### Voraussetzungen

- Python 3.10 oder hoeher
- pip (Python Paketmanager)

### Lokale Installation

```bash
# 1. Repository klonen
git clone https://github.com/Wakar111/markdown-konverter.git
cd markdown-konverter

# 2. Virtuelle Umgebung erstellen und aktivieren
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# oder: venv\Scripts\activate  # Windows

# 3. Abhaengigkeiten installieren
pip install -r requirements.txt

# 4. .env-Datei erstellen (optional, fuer KI-Features)
cp .env.example .env
# Tragen Sie Ihre API-Keys ein

# 5. Anwendung starten
streamlit run app.py
```

Die Anwendung oeffnet sich automatisch im Browser unter `http://localhost:8501`.

### Schnellstart (wenn bereits installiert)

```bash
cd markdown-konverter
source venv/bin/activate
streamlit run app.py
```

## 🤖 KI-Integration

Die App unterstuetzt mehrere KI-Anbieter fuer **Vision OCR**, **Chat** und **Embeddings**.

### Unterstuetzte Anbieter

| Anbieter | Vision OCR | Chat | Embeddings | Kosten |
|----------|-----------|------|------------|-------|
| **NVIDIA NIM** | Ja | Ja | Ja | Freemium |
| **Google Gemini** | Ja | Ja | Ja | Kostenlos (Free Tier) |
| **OpenAI** | Ja | Ja | Ja | Bezahlt |
| **Ollama** | Nein | Ja | Ja (lokal) | Kostenlos (lokal) |
| **Lokal** | Nein | Nein | Ja (sentence-transformers) | Kostenlos (lokal) |

### .env-Konfiguration

Alle API-Keys koennen in einer `.env`-Datei gespeichert werden. Die App erkennt diese automatisch und verwendet sie als Standardwerte.

```bash
# Google Gemini (empfohlen, kostenloser Free Tier)
GEMINI_API_KEY=your_key_here

# OpenAI
OPENAI_API_KEY=your_key_here

# NVIDIA NIM
GLM_API_KEY=your_key_here
GLM_MODEL=nvidia/nemotron-3-nano-omni-30b-a3b-reasoning
GLM_BASE_URL=https://integrate.api.nvidia.com/v1

# Ollama (lokal, kein Key noetig)
OLLAMA_BASE_URL=http://localhost:11434/v1

# Andere OpenAI-kompatible Anbieter
CUSTOM_API_BASE_URL=your_url_here
CUSTOM_API_KEY=your_key_here
```

**Prioritaet der automatischen Erkennung:** NVIDIA NIM -> Google Gemini -> OpenAI -> Custom

### Standard-Modelle

| Provider | Chat-Modell | Embedding-Modell | Vision-Modell |
|----------|------------|-----------------|--------------|
| **NVIDIA NIM** | `meta/llama-3.1-8b-instruct` | `nvidia/nv-embedqa-e5-v5` | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` |
| **Google Gemini** | `gemini-2.0-flash` | `models/embedding-001` | `gemini-2.0-flash` |
| **OpenAI** | `gpt-4o-mini` | `text-embedding-3-small` | `gpt-4o` |
| **Ollama** | `llama3.2` | `all-MiniLM-L6-v2` (lokal) | – |
| **Lokal** | – | `all-MiniLM-L6-v2` | – |

### NVIDIA NIM einrichten

1. API-Key holen: https://build.nvidia.com
2. In `.env` eintragen: `GLM_API_KEY=your_key`
3. Die App erkennt den Key automatisch und initialisiert alle Services

### Google Gemini einrichten (kostenlos)

1. Kostenlosen API-Key holen: https://aistudio.google.com/app/apikey
2. In `.env` eintragen: `GEMINI_API_KEY=your_key`
3. Die App erkennt den Key automatisch

### Ollama einrichten (lokal & kostenlos)

1. Ollama installieren: https://ollama.com
2. Modell herunterladen:
   ```bash
   ollama pull llama3.2
   ```
3. In `.env` eintragen: `OLLAMA_BASE_URL=http://localhost:11434/v1`

## 📂 Projektstruktur

```
markdown-konverter/
├── app.py                      # Hauptanwendung (Einstiegspunkt)
├── requirements.txt            # Python-Abhaengigkeiten
├── .env                        # API-Keys (nicht im Git-Repo)
├── README.md                   # Diese Datei
├── PLAN.md                     # Entwicklungsplan
└── src/
    ├── __init__.py
    ├── config.py               # Konfiguration & UI-Texte
    ├── converter.py            # Konvertierungslogik
    ├── providers.py            # KI-Anbieter-Definitionen
    ├── components/
    │   ├── __init__.py
    │   ├── sidebar.py          # Sidebar-Komponente & Provider-Selector
    │   ├── file_upload.py      # Upload-Komponente
    │   ├── result_display.py   # Ergebnis-Anzeige
    │   └── document_search.py  # Dokumentensuche-UI & Chat-Interface
    └── rag/                     # RAG-Module
        ├── __init__.py
        ├── document_store.py   # Dokumentenverwaltung & Chunking
        ├── embeddings.py       # Embedding-Service (inkl. NVIDIA NIM)
        ├── retriever.py        # Vektor-Suche mit ChromaDB
        └── chat.py             # RAG-Chat-Logik (inkl. NVIDIA NIM)
```

## 🔧 Entwicklung

### Code-Struktur

Das Projekt folgt **Clean Code**-Prinzipien:
- **Separation of Concerns** – UI, Logik und Konfiguration sind getrennt
- **Single Responsibility** – Jedes Modul hat eine klare Aufgabe
- **Dependency Injection** – Flexible Konfiguration der KI-Anbieter
- **Provider-Pattern** – Einheitliche Schnittstelle fuer verschiedene KI-Anbieter

### Tests ausfuehren

```bash
pytest tests/
```

## 📝 Verwendung

### Konverter
1. **Anwendung starten** mit `streamlit run app.py`
2. **"📄 Konverter"** in der Navigation waehlen
3. **Optional: Vision-Provider** in der Sidebar waehlen (fuer Bild-OCR)
4. **Datei hochladen** per Drag & Drop oder Klick
5. **Ergebnis ansehen** in der Vorschau oder als Markdown-Code
6. **Kopieren** mit dem Kopier-Button im Markdown-Code Tab, oder **Download** als Datei

### Dateien zwischen Konverter & Dokumentensuche teilen
- Eine im **Konverter** konvertierte Datei erscheint automatisch beim Wechsel zu **"🔍 Dokumentensuche"** (kein erneuter Upload nötig)
- Umgekehrt: Eine in der **Dokumentensuche** hochgeladene Datei erscheint automatisch im **"📄 Konverter"**
- In beiden Fällen wird der bereits konvertierte Markdown-Inhalt übernommen – **keine erneute (ggf. teure OCR-)Konvertierung**

### Dokumentensuche
1. **"🔍 Dokumentensuche"** in der Navigation waehlen
2. **Services werden automatisch initialisiert** wenn .env-Keys vorhanden sind
3. **Dokumente hochladen** – PDFs, Word-Dateien, Bilder (PNG/JPG) gleichzeitig moeglich
4. **Indexierung erfolgt automatisch** nach dem Upload (idempotent)
5. **Fragen stellen** im ChatGPT-style Chat-Fenster, z.B.:
   - *"Welcher Steuersatz gilt fuer Kunde Mueller GmbH?"*
   - *"Was ist die Anschrift von Firma Schmidt?"*
   - *"Zeige mir alle Rechnungen an Kunde XY"*
6. **Quellen** werden bei jeder Antwort angezeigt (aufklappbar)

### Eigene Provider/Modelle verwenden
1. In der Sidebar der Dokumentensuche **Checkbox "Eigenen Provider waehlen"** aktivieren
2. Gewuenschten Embedding- und/oder Chat-Provider auswaehlen
3. Modell und API-Key eingeben
4. **"🚀 Services initialisieren"** klicken

## 🧠 Architektur: Embeddings vs. Chat-Modell

| Konzept | Zweck | Beispiel |
|---------|-------|---------|
| **Embedding-Modell** | Wandelt Text in Vektorrepraesentationen um, um semantische Aehnlichkeit zu finden | `nvidia/nv-embedqa-e5-v5` |
| **Chat-Modell (LLM)** | Generiert natuerliche Antworten basierend auf gefundenem Kontext | `meta/llama-3.1-8b-instruct` |
| **Vision-Modell (OCR)** | Extrahiert Text aus Bildern | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` |

## 🚧 Roadmap / Geplante Erweiterungen

### Kurzfristig
- [ ] **Persistenz** – Indexierte Dokumente speichern, sodass sie beim naechsten Start nicht erneut verarbeitet werden muessen
- [ ] **Fortschrittsanzeige** – Detaillierter Fortschritt bei der Indexierung vieler Dokumente
- [ ] **Dokumenten-Preview** – Vorschau der hochgeladenen Dokumente vor der Indexierung

### Mittelfristig
- [ ] **Ordner-Import** – Ganzen Ordner mit Dokumenten auf einmal importieren
- [ ] **Export-Funktion** – Chat-Verlauf als PDF/Markdown exportieren
- [ ] **Mehrsprachige Suche** – Dokumente in verschiedenen Sprachen durchsuchen
- [ ] **Dokumenten-Kategorien** – Dokumente nach Typ/Kunde/Jahr gruppieren

### Langfristig
- [ ] **Cloud-Speicher** – Integration mit Google Drive, Dropbox, OneDrive
- [ ] **Team-Funktionen** – Mehrere Benutzer, geteilte Dokumentenbasis
- [ ] **API-Endpunkt** – REST-API fuer Integration in andere Systeme
- [ ] **Automatische Aktualisierung** – Neue Dokumente in ueberwachten Ordnern automatisch indexieren

## 🤝 Beitragen

Pull Requests sind willkommen! Fuer groessere Aenderungen bitte zuerst ein Issue erstellen.

## 📄 Lizenz

MIT License – siehe [LICENSE](LICENSE) fuer Details.

## 🙏 Credits

- [Microsoft MarkItDown](https://github.com/microsoft/markitdown) – Die Konvertierungs-Engine
- [Streamlit](https://streamlit.io/) – Das Web-UI Framework
- [ChromaDB](https://www.trychroma.com/) – Vektordatenbank
- [LangChain](https://langchain.com/) – RAG-Framework
- [NVIDIA NIM](https://build.nvidia.com) – KI-Modelle
