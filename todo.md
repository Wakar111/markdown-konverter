# PDF-Schwärzung ("PDF Redaktion") Feature

Neue dritte Navigations-Seite neben "Konverter" und "Dokumentensuche", mit der Nutzer wiederkehrende Textstellen in einer großen PDF (z.B. mit ~20 Firmen-Abschnitten) per exaktem Text oder KI-Beschreibung finden, in einem Review-Schritt bestätigen und dann echt (nicht nur visuell) schwärzen lassen können – inklusive Unterstützung für gescannte Seiten via Tesseract-OCR.

## Anforderungen (aus Rückfragen)

- **Suchmodus:** Beides – exakter Text/Phrase UND freie KI-Beschreibung ("finde alle Stellen mit IBAN-Nummern")
- **Review-Schritt:** Gefundene Treffer werden vor der finalen Schwärzung angezeigt (Seite + Kontext), Nutzer kann einzelne Treffer ab-/auswählen
- **Schwärzungsart:** Echte Schwärzung – Text wird aus der PDF-Struktur entfernt (PyMuPDF `apply_redactions`), nicht nur schwarz überdeckt
- **PDF-Typen:** Sowohl digitale (durchsuchbare) als auch gescannte PDFs
- **OCR für gescannte Seiten:** Tesseract OCR (lokal, präzise Wort-Koordinaten) – erfordert `brew install tesseract` auf dem Mac zusätzlich zur Python-Bibliothek `pytesseract`

## Priorität: Bibliothek zuerst, OCR nur als Fallback

**Explizite Regel:** Pro Seite wird zuerst versucht, den Text rein über die Bibliothek (PyMuPDF `page.get_text()`) zu extrahieren. Nur wenn eine Seite **keinen bzw. praktisch keinen extrahierbaren Text** liefert (klassisches Merkmal einer gescannten/Bild-Seite), wird für **diese Seite** auf Tesseract-OCR zurückgegriffen. Seiten mit funktionierendem Text-Layer durchlaufen niemals OCR – das spart Zeit und vermeidet unnötige OCR-Fehler. Diese Entscheidung erfolgt unabhängig pro Seite (kein globaler Schalter für das gesamte Dokument).

## Neue Abhängigkeiten

| Paket | Zweck |
|---|---|
| `pymupdf` (fitz) | PDF-Text-Extraktion mit Koordinaten, echte Redaktion, Rendering von Seiten als Bild |
| `pytesseract` | OCR für gescannte Seiten mit Wort-Bounding-Boxes |
| `Pillow` | Bildverarbeitung (Seiten-Rendering, OCR-Vorbereitung) – ggf. bereits transitiv vorhanden |

**Wichtig:** Tesseract-Binary muss separat installiert werden (`brew install tesseract`). Dies wird dem Nutzer vor der Installation mitgeteilt; App zeigt einen Hinweis/Fehler an, falls Tesseract fehlt.

## Architektur

```
src/redaction/
  __init__.py
  pdf_analyzer.py     # Seiten klassifizieren (digital vs. gescannt), Text + Koordinaten extrahieren
  ocr_service.py       # Tesseract-Wrapper: Wort-Bounding-Boxes je Seite
  matcher.py           # Exakte Suche + KI-gestützte Beschreibungssuche (LLM liefert exakte Substrings)
  redactor.py          # Wendet PyMuPDF add_redact_annot/apply_redactions an; rasterisiert+schwärzt gescannte Seiten permanent
src/components/
  pdf_redaction.py     # Neue UI-Seite: Upload, Suchanfragen, Review, Download
app.py                 # Navigation um dritten Menüpunkt "🕶️ PDF Schwärzen" erweitern
```

## Ablauf im Detail

### 1. Analyse (`pdf_analyzer.py`)
- PDF mit PyMuPDF öffnen, pro Seite **zuerst die Bibliothek versuchen**: hat die Seite extrahierbaren Text (`page.get_text()`)?
  - Ja → **digitale Seite**: Text + Wort-Koordinaten direkt aus PyMuPDF (`page.get_text("words")`) – **OCR wird für diese Seite gar nicht aufgerufen**
  - Nein/kaum Text → **gescannte Seite** (Bibliothek liefert nichts): Seite als Bild rendern (`page.get_pixmap()`), erst jetzt als Fallback an `ocr_service.py` übergeben

### 2. OCR (`ocr_service.py`)
- Rendert Seite als Bild, `pytesseract.image_to_data()` liefert Wörter + Pixel-Bounding-Boxes
- Umrechnung Pixel-Koordinaten → PDF-Punkt-Koordinaten (Skalierungsfaktor aus Render-Auflösung)

### 3. Suche (`matcher.py`)
Zwei Modi, pro Suchanfrage wählbar:
- **Exakter Text:** Case-insensitive Substring-Suche über den Seitentext (digital) bzw. OCR-Text (gescannt, mit etwas Toleranz für OCR-Fehler)
- **KI-Beschreibung:** Seitentext wird (in Chunks) an das bereits konfigurierte LLM (wiederverwendet: `ProviderConfig` aus Sidebar/Providers) gesendet mit der Anweisung, exakte wortwörtliche Substrings zurückzugeben, die der Beschreibung entsprechen. Diese Substrings werden anschließend wie im exakten Modus im Seitentext lokalisiert (Koordinaten-Mapping)

Ergebnis: Liste von Treffern `{seite, bbox(en), gefundener_text, quelle (exakt/KI), suchanfrage}`

### 4. Review-UI (`pdf_redaction.py`)
- Treffer gruppiert nach Suchanfrage angezeigt, je mit Seitenzahl + Kontext-Ausschnitt (Text davor/danach)
- Checkbox pro Treffer (Standard: aktiviert), um einzelne Treffer abzuwählen
- Optionale Seiten-Vorschau mit rot markierten Boxen (Bild-Rendering der Seite) für Seiten mit Treffern

### 5. Schwärzung (`redactor.py`)
- **Digitale Seiten:** Für jeden bestätigten Treffer `page.add_redact_annot(rect, fill=(0,0,0))`, danach `page.apply_redactions()` – entfernt den Text dauerhaft aus der PDF-Struktur
- **Gescannte Seiten:** Seite wird als Bild gerendert, schwarze Rechtecke auf den bestätigten Koordinaten eingezeichnet, das Bild ersetzt den Seiteninhalt (Rasterisierung) – so ist auch hier keine Wiederherstellung möglich
- Ergebnis-PDF im Speicher zusammenbauen, Download-Button anbieten

## UI/UX (neue Seite "🕶️ PDF Schwärzen")

1. PDF hochladen
2. Suchanfragen hinzufügen (Liste, mehrere möglich): pro Zeile Auswahl "Exakter Text" oder "KI-Beschreibung" + Eingabefeld
3. Button "🔍 Stellen finden" → Analyse + Suche laufen (mit Spinner/Fortschritt)
4. Review-Bereich: Treffer je Suchanfrage mit Checkboxen
5. Button "🖍️ Schwärzung anwenden" → erzeugt finale PDF
6. Download-Button für geschwärzte PDF

## Offene technische Risiken
- OCR-Genauigkeit bei schlecht gescannten/schiefen Seiten kann Treffer verfehlen → Review-Schritt fängt das ab (Nutzer sieht ggf. fehlende Treffer und kann ergänzen/exakten Text nachschärfen)
- Sehr große PDFs (viele Seiten) → KI-Beschreibungssuche läuft seitenweise, kann bei vielen Seiten dauern; Fortschrittsanzeige einplanen
- Font-Verschiebungen nach `apply_redactions()` sind bei PyMuPDF nicht zu erwarten (Redaction ändert nur den betroffenen Bereich), aber wird beim Testen verifiziert
