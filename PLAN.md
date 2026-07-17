## Finaler Plan: Universeller Datei-zu-Markdown-Konverter

Eine Web-App, die es Benutzern ermöglicht, verschiedene Dateitypen (Dokumente, Bilder, Audio etc.) per Dateisuche oder Drag & Drop hochzuladen, sie mit `markitdown` in Markdown zu konvertieren und das Ergebnis in einer Vorschau anzuzeigen und zu kopieren.

### Schritte

1.  **Projekt-Setup:**
    *   Ein neues Projektverzeichnis erstellen (z.B. `MarkItDown-App`).
    *   In diesem Verzeichnis eine virtuelle Python-Umgebung einrichten und aktivieren.
    *   Die erforderlichen Bibliotheken mit dem Befehl `pip install "streamlit>=1.30" "markitdown[all]"` installieren.

2.  **UI-Grundgerüst erstellen:**
    *   Eine Python-Datei namens `app.py` erstellen.
    *   Mit Streamlit einen Titel für die Anwendung und ein Dateiupload-Widget (`st.file_uploader`) hinzufügen. Dieses Widget unterstützt standardmäßig sowohl das Hochladen per Dateibrowser als auch per Drag & Drop.

3.  **Konvertierungslogik implementieren:**
    *   Eine Funktion schreiben, die das von Streamlit hochgeladene Dateiobjekt entgegennimmt.
    *   Innerhalb dieser Funktion eine Instanz von `markitdown.MarkItDown` erstellen.
    *   Die `convert()`-Methode aufrufen, um die Datei in Markdown umzuwandeln. `markitdown` erkennt den Dateityp automatisch.
    *   Den generierten Markdown-Text zurückgeben.

4.  **Ergebnis anzeigen und kopieren:**
    *   Wenn eine Datei hochgeladen wurde, die Konvertierungsfunktion innerhalb eines Ladeindikators (`st.spinner`) aufrufen.
    *   Den zurückgegebenen Markdown-Text in einem `st.text_area()` anzeigen. Dies dient als Vorschau und ermöglicht dem Benutzer das einfache manuelle Kopieren des gesamten Inhalts.

### Relevante Dateien

*   `app.py`: Die einzige Python-Datei, die die gesamte Logik der Streamlit-Anwendung enthält.
*   `requirements.txt`: Eine optionale Datei, um die Abhängigkeiten (`streamlit`, `markitdown[all]`) für eine spätere Bereitstellung festzuhalten.

### Verifizierung

1.  Die Anwendung lokal mit dem Befehl `streamlit run app.py` im Terminal starten.
2.  Eine Datei per Drag & Drop in den Upload-Bereich ziehen und das Ergebnis prüfen.
3.  Auf den Upload-Bereich klicken, eine Datei aus dem Dateibrowser auswählen und das Ergebnis prüfen.
4.  Verschiedene Dateitypen (z.B. eine PDF-, eine DOCX- und eine PNG-Datei) testen, um sicherzustellen, dass die Konvertierung für alle wie erwartet funktioniert.
