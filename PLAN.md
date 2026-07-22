# Entwicklungsplan: MarkItDown Konverter

## Uebersicht

Eine Web-App, die es Benutzern ermoeglicht, verschiedene Dateitypen per Drag & Drop hochzuladen, mit `markitdown` in Markdown zu konvertieren und eine KI-gestuetzte Dokumentensuche (RAG) durchzufuehren.

---

## ✅ Implementierte Features

### Phase 1: Grundgeruest & Konverter
- [x] **Projekt-Setup** – Python venv, Streamlit, MarkItDown installiert
- [x] **UI-Grundgeruest** – Navigation mit Konverter und Dokumentensuche
- [x] **Datei-Upload** – Drag & Drop & Dateibrowser (`st.file_uploader`)
- [x] **Konvertierungslogik** – `MarkItDown.convert()` fuer alle Dateitypen
- [x] **Ergebnis-Anzeige** – Markdown-Vorschau & Code-Ansicht mit Kopier-Button
- [x] **Multi-Format-Support** – PDF, Word, PowerPoint, Excel, HTML, CSV, JSON, Bilder

### Phase 2: KI-Integration (Vision OCR)
- [x] **Vision-Provider in Sidebar** – Provider-Auswahl fuer KI-gestuetzte OCR
- [x] **Unterstuetzte Vision-Provider:**
  - [x] Google Gemini (`gemini-2.0-flash`)
  - [x] OpenAI (`gpt-4o`)
  - [x] NVIDIA NIM (`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`)
  - [x] Ollama (lokal, `llava`)
  - [x] Custom (OpenAI-kompatibel)
- [x] **MarkItDown LLM-Integration** – Vision-Client an MarkItDown uebergeben

### Phase 3: Dokumentensuche (RAG)
- [x] **RAG-Modul erstellt** – `src/rag/` mit document_store, embeddings, retriever, chat
- [x] **DocumentStore** – Dokumentenverwaltung, Chunking (LangChain RecursiveCharacterTextSplitter)
- [x] **Embedding-Service** – Vektorisierung mit mehreren Providern:
  - [x] Lokal (`all-MiniLM-L6-v2`, sentence-transformers)
  - [x] OpenAI (`text-embedding-3-small`)
  - [x] Google Gemini (`models/embedding-001`)
  - [x] NVIDIA NIM (`nvidia/nv-embedqa-e5-v5`) – mit custom `NvidiaEmbeddings` Klasse
- [x] **NVIDIA NIM Embedding-Fixes:**
  - [x] `check_embedding_ctx_length=False` – verhindert Tokenisierung als Liste
  - [x] `NvidiaEmbeddings` custom class – setzt `input_type` ("passage"/"query") fuer asymmetrische Modelle
- [x] **DocumentRetriever** – ChromaDB Vektor-Suche, idempotente Indexierung
- [x] **RAG-Chat** – LLM-basierte Antwortgenerierung mit Kontext und Quellenangaben
- [x] **Chat-Provider:**
  - [x] OpenAI (`gpt-4o-mini`)
  - [x] Google Gemini (`gemini-2.0-flash`)
  - [x] NVIDIA NIM (`meta/llama-3.1-8b-instruct`)
  - [x] Ollama (`llama3.2`)

### Phase 4: Bild-Upload in Dokumentensuche
- [x] **PNG/JPG/JPEG Upload** – Bild-Dateitypen in Dokumentensuche erlaubt
- [x] **Vision OCR fuer Bilder** – Bilder werden per Vision-Provider in Text umgewandelt
- [x] **Vision-Provider geteilt** – Auswahl zwischen Konverter und Dokumentensuche synchronisiert

### Phase 5: Smarte .env-Konfiguration & UX
- [x] **Automatische Provider-Erkennung** – `.env`-Keys werden automatisch erkannt
- [x] **Provider-Prioritaet** – NVIDIA NIM > Gemini > OpenAI > Custom
- [x] **API-Keys versteckt** – Keys aus `.env` werden im UI nicht angezeigt
- [x] **Override-Checkbox** – Benutzer kann explizit eigene Provider/Modelle/Keys eingeben
- [x] **Automatische Service-Initialisierung** – Bei `.env`-Defaults: kein Button-Klick noetig
- [x] **"Services initialisieren" Button** – Nur sichtbar bei Custom-Konfiguration
- [x] **Getrennte Embedding- & Chat-Sektionen** – Unabhaengige Provider-Wahl
- [x] **Status-Anzeige** – Kompakte Status-Indikatoren (initialisiert / nicht initialisiert)

### Phase 6: Automatisierung & Chat-UX
- [x] **Automatische Indexierung** – Kein "Dokumente indexieren" Button mehr; Indexierung laeuft automatisch nach Upload (idempotent)
- [x] **ChatGPT-style Chat-Fenster** – Scrollbares Chat-Fenster mit fester Hoehe (`st.container(height=500)`)
- [x] **Chat-Input am Boden** – `st.chat_input` klebt am Seitenende
- [x] **Chat-Loeschen-Button** – In der Header-Zeile, nur sichtbar bei vorhandenen Nachrichten
- [x] **Leerzustand-Anzeige** – Platzhalter-Text im leeren Chat-Fenster
- [x] **Status-Hinweise** – Kompakt ueber dem Chat-Fenster (Services/Upload-Status)

### Phase 7: Bugfixes & Stabilitaet
- [x] **NVIDIA Chat Timeout fix** – Default-Modell von `z-ai/glm-5.2` (timeout) zu `meta/llama-3.1-8b-instruct` geaendert
- [x] **Client-Timeout** – `timeout=60.0` im OpenAI-Client gegen endloses Haengen
- [x] **Gemini Rate-Limit umgangen** – Provider-Prioritaet auf NVIDIA NIM gesetzt
- [x] **NVIDIA Embedding `list.strip` Error** – `check_embedding_ctx_length=False`
- [x] **NVIDIA Embedding `input_type` Error** – Custom `NvidiaEmbeddings` Klasse mit `input_type` Parameter

### Phase 8: RAG-Genauigkeit & Upload-Bugfixes
- [x] **Geloeschte Dokumente kamen zurueck** – `st.file_uploader` behaelt Dateien im Widget-State ueber Reruns; neues `removed_filenames`-Set in `document_search.py` verhindert automatisches Wieder-Hinzufuegen explizit geloeschter Dateien
- [x] **Falsche Dokumentenanzahl bei Meta-Fragen** – `_build_context()` in `chat.py` gruppiert Chunks jetzt nach Quelldatei statt jeden Chunk als eigenes "Dokument" zu labeln
- [x] **top_k erhoeht** – Default von 5 auf 10 (Chat) / 15 (UI-Aufruf), damit bei kleineren Dokumentenmengen alle Chunks in den Kontext einfliessen
- [x] **CSV/grosse Dateien: "Erfolg" vor sichtbarem Inhalt** – Spinner deckt jetzt auch `render_result()` ab (nicht nur die Konvertierung), da das Client-seitige Rendering grosser Markdown-Tabellen lange dauert
- [x] **Vorschau-Truncation** – Inhalte > 20.000 Zeichen werden in Vorschau/Code-Ansicht gekuerzt (mit Warnhinweis), Download-Button fuer vollstaendigen Inhalt hinzugefuegt
- [x] **Bidirektionaler Datei-Transfer Konverter ↔ Dokumentensuche:**
  - [x] `DocumentStore.add_document_from_content()` – neue Methode, um bereits konvertierten Markdown-Inhalt ohne erneute (teure OCR-)Konvertierung zu uebernehmen
  - [x] Konverter → Dokumentensuche: `shared_converted_file` im Session-State, automatischer Import via `_import_shared_converter_file()`
  - [x] Dokumentensuche → Konverter: `shared_search_file` im Session-State, Anzeige ohne erneute Konvertierung
  - [x] **Stale-Upload-Bug behoben** – Content-Hash (`hashlib.md5`) erkennt, ob die Datei im Konverter-Uploader wirklich neu ist; verhindert, dass eine alte "klebende" Datei im Widget dauerhaft Vorrang vor einer neueren geteilten Datei hat

---

## 📋 Technische Details

### Architektur
```
app.py (Einstiegspunkt)
  -> src/components/ (UI)
    -> sidebar.py (Provider-Selector, .env-Erkennung)
    -> document_search.py (Chat-UI, Upload, Auto-Indexierung)
  -> src/rag/ (RAG-Logik)
    -> embeddings.py (Embedding-Service + NvidiaEmbeddings)
    -> retriever.py (ChromaDB Vektor-Suche)
    -> chat.py (LLM Chat-Completions)
  -> src/providers.py (Provider-Definitionen)
  -> src/converter.py (MarkItDown Konvertierung)
```

### .env-Variablen
| Variable | Zweck |
|----------|-------|
| `GLM_API_KEY` | NVIDIA NIM API-Key |
| `GLM_MODEL` | NVIDIA NIM Standard-Modell |
| `GLM_BASE_URL` | NVIDIA NIM Base URL |
| `GEMINI_API_KEY` | Google Gemini API-Key |
| `OPENAI_API_KEY` | OpenAI API-Key |
| `OLLAMA_BASE_URL` | Ollama Base URL (lokal) |
| `CUSTOM_API_BASE_URL` | Custom Provider Base URL |
| `CUSTOM_API_KEY` | Custom Provider API-Key |

### Standard-Modelle
| Provider | Chat | Embedding | Vision |
|----------|------|-----------|--------|
| NVIDIA NIM | `meta/llama-3.1-8b-instruct` | `nvidia/nv-embedqa-e5-v5` | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` |
| Google Gemini | `gemini-2.0-flash` | `models/embedding-001` | `gemini-2.0-flash` |
| OpenAI | `gpt-4o-mini` | `text-embedding-3-small` | `gpt-4o` |
| Ollama | `llama3.2` | `all-MiniLM-L6-v2` (lokal) | – |

---

## 🚧 Geplante Erweiterungen

### Kurzfristig
- [ ] **Persistenz** – Indexierte Dokumente ueber Sessions hinweg speichern
- [ ] **Fortschrittsanzeige** – Detaillierter Fortschritt bei Indexierung
- [x] **Dokumenten-Preview** – Grosse Inhalte werden gekuerzt angezeigt, Download-Button fuer Volltext

### Mittelfristig
- [ ] **Ordner-Import** – Ganzen Ordner importieren
- [ ] **Export-Funktion** – Chat-Verlauf als PDF/Markdown
- [ ] **Mehrsprachige Suche** – Dokumente in verschiedenen Sprachen
- [ ] **Dokumenten-Kategorien** – Gruppierung nach Typ/Kunde/Jahr

### Langfristig
- [ ] **Cloud-Speicher** – Google Drive, Dropbox, OneDrive Integration
- [ ] **Team-Funktionen** – Mehrere Benutzer, geteilte Dokumentenbasis
- [ ] **API-Endpunkt** – REST-API fuer externe Integrationen
- [ ] **Automatische Ordnerueberwachung** – Neue Dokumente automatisch indexieren
