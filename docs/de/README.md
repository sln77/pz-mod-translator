# Projekt Zomboid Mod Übersetzer

<p align="center">
  <a href="#features">Funktionen</a> ·
  <a href="#requirements">Anforderungen</a> ·
  <a href="#configuration-configjson">Konfiguration</a> ·
  <a href="#usage">Verwendung</a> ·
  <a href="#how-it-works">Wie es funktioniert</a>
</p>

<p align="center">
  <b>Englisch</b> ·
  <a href="docs/ru/README.md">Русский</a> ·
  <a href="docs/zh/README.md">简体中文</a> ·
  <a href="docs/zh-TW/README.md">繁體中文</a> ·
  <a href="docs/ja/README.md">日本語</a> ·
  <a href="docs/ko/README.md">한국어</a> ·
  <a href="docs/de/README.md">Deutsch</a> ·
  <a href="docs/fr/README.md">Französisch</a> ·
  <a href="docs/es/README.md">Español</a> ·
  <a href="docs/it/README.md">Italienisch</a> ·
  <a href="docs/pt-BR/README.md">Português</a> ·
  <a href="docs/tr/README.md">Türkçe</a> ·
  <a href="docs/uk/README.md">Українська</a> ·
  <a href="docs/pl/README.md">Polnisch</a>
</p>

Ein CLI-Tool zur Lokalisierung von **Project Zomboid (Build 42.15+)** Mods unter Verwendung eines lokalen `llama.cpp`-Servers (`llama-server`), der von **TranslateGemma** betrieben wird.

Es scannt den Steam Workshop oder lokale Mod-Ordner nach Dateien vom Typ `Translate/EN/*.json`, schätzt die Übersetzungsvolumen (Anzahl der Zeilen und Zeichen), übersetzt fehlende oder aktualisierte Zeichenketten und speichert jede generierte Übersetzung lokal, sodass Sie Übersetzungs-Mods einfach als eigenständige Pakete erstellen oder Dateien nach Steam-Updates wiederherstellen können.

---

## Funktionen

- **Unterstützung für JSON-Format (Version 42.15+):** Funktioniert mit dem modernen `.json`-Übersetzungsformat, das in Project Zomboid B42.15+ verwendet wird (alte `.txt`-basierte Mods werden während des Scans sicher übersprungen).
- **Reichhaltige Terminal-Schnittstelle:** Saubere, farbige Tabellen, Status-Badges und dynamische Fortschrittsbalken mit vergangenem/verbleibendem Zeit, mithilfe von `rich`.
- **Mehrsprachige Befehlszeilenschnittstelle (`i18n`):** Standardmäßig auf Englisch eingestellt und beim interaktiven Start zur Auswahl der Benutzersprache aus `cli_locales/*.json` aufgefordert.
- **3 Betriebsmodi:**
  - **Modus 1:** Übersetzen Sie ein einzelnes, angegebenes Mod (oder seinen `Translate` / `EN`-Ordner).
  - **Modus 2:** Scannen Sie das gesamte Workshop-Verzeichnis, überprüfen Sie den Übersetzungsstatus und das Zeichenvolumen pro Mod, und wählen Sie Module anhand von Nummern (`1,3,5`), Bereichen (`1-4`) oder `alle` aus.
  - **Modus 3:** Verwaltung gespeicherter Fortschritte – Erkennen von Mod-Updates, Übersetzung nur neuer/geänderter Strings, Überschreiben von Grund auf, Wiederherstellung von einem Spiegel, oder sauberes Löschen generierter Dateien.
- **Erkennung von Aktualisierungen und Fortschrittsverfolgung:** Speichert SHA-1-Hashes der ursprünglichen englischen Zeichenketten pro Schlüssel in `pz_translator_state.json`. Wenn eine Mod-Aktualisierung im Steam Workshop erfolgt, werden nur neu hinzugefügte oder geänderte englische Schlüssel für die Übersetzung in die Warteschlange gestellt.
- **Lokales Spiegelbild (`pz_translator_mods/`):** Speichert eine Kopie jeder übersetzten Datei und bewahrt die relative Verzeichnisstruktur (was die Erstellung eigenständiger Modifikationen, die nur Übersetzungen enthalten, erleichtert).
- **Sicher und fehlertolerant:**
  - Vorhandene Übersetzungen von Autoren mit `0` ausstehenden Schlüsseln werden niemals verändert, überschrieben oder verfolgt.
  - Behandelt UTF-8-BOM, nachgestellte Kommas in von Hand bearbeiteten Mod-JSONs und bewahrt `$schema` und leere Strings.
  - Automatische Speicherung des Fortschritts periodisch (`save_every`) und bei `Ctrl+C`.

---

## Anforderungen

- **Python 3.9+**
- **llama.cpp** (`llama-server`), das ein **TranslateGemma** GGUF-Modell auf dem konfigurierten Host/Port ausführt (Standard: `http://127.0.0.1:8734`).
- Python-Abhängigkeiten:

```bash
pip install -r requirements.txt
```

---

## Konfiguration (`config.json`)

Beim ersten Ausführen (oder über die mitgelieferte `config.json`-Datei) verwendet das Skript die folgenden Einstellungen:

```json
{
    "llamacpp_host": "127.0.0.1",
    "llamacpp_port": 8734,
    "mods_path": "Z:\\steam\\steamapps\\workshop\\content\\108600",
    "default_source_lang": "EN",
    "default_target_lang": "RU",
    "ui_lang": "en",
    "mirror_dir": "pz_translator_mods",
    "state_file": "pz_translator_state.json",
    "save_every": 20
}
```

| Schlüssel | Beschreibung |
| --- | --- |
| `llamacpp_host` | IP-Adresse des laufenden `llama-server` |
| `llamacpp_port` | Port Ihres laufenden `llama-server` |
| `mods_path` | Standard-Wurzelverzeichnis wird im Modus 2 gescannt (z. B. Ordner `108600` im Steam Workshop). |
| `default_source_lang` | Name des Ordners für die Quelübersetzung (Standard: `EN`) |
| `default_target_lang` | Standard-Ziel-Sprachcode (z. B. `RU`, `DE`, `CN`, `JP`, `PTBR`) |
| `ui_lang` | Standard-Sprachcode für die Benutzeroberfläche aus `cli_locales/` |
| `mirror_dir` | Lokaler Ordner, in dem vollständige Pfad-Kopien der generierten Übersetzungen gespeichert werden. |
| `state_file` | JSON-Datei, die die Übersetzungsgeschichte und Hash-Werte der ursprünglichen Strings speichert |
| `save_every` | Speichern des Fortschritts auf der Festplatte und Spiegeln aller N übersetzten Schlüssel |

---

## Verwendung

### Interaktiver Modus

Beginnen Sie zuerst mit dem Start von `llama-server`, und führen Sie dann aus:

```bash
python pz_translate.py
```

1. **Auswahl der Benutzersprache:** Wählen Sie aus den verfügbaren Sprachen in `cli_locales/` (Standard: `en`).
2. **Auswahlmodus:**
   - `1` — Übersetzen eines bestimmten Mod-Pfads.
   - `2` – Alle Mods im `mods_path` scannen, die Tabelle mit Zeichen-/Zeichenanzahl anzeigen und Mod-Nummern eingeben (z.B. `1,3,5`, `1-4` oder `alle`).
   - `3` — Verwaltung gespeicherter Fortschritte (aktualisieren von geänderten/neuen Schlüsseln, erneutes Übersetzen von Grund auf, Wiederherstellen aus `pz_translator_mods/`, oder Löschen von Übersetzungen).
   - `4` — Sprache der Benutzeroberfläche ändern.
   - `0` — Beenden.

### Kommandozeilenargumente

Sie können das interaktive Menü mithilfe von Befehlszeilen-Flags (CLI-Argumente überschreiben `config.json`):

| Flagge | Beschreibung |
| --- | --- |
| `--config <Pfad>` | Pfad zu einer benutzerdefinierten `config.json`-Datei |
| `--mode {1, 2, 3}` | `1` = einzelner Modus, `2` = Verzeichnis scannen, `3` = gespeicherten Fortschritt verwalten |
| `--path <Pfad>` | Pfad zu einem Mod-Ordner (Modus 1) oder zum Stammordner für Mods (Modus 2) |
| `--lang <code>` | Zielsprache als PZ-Ordnercode (`RU`, `CN`, `PTBR`) oder ISO-Code (`ru`, `zh`, `pt-BR`) |
| `--source-lang <code>` | Überschreiben des Quell-Sprach-Ordners (Standard: `EN`) |
| `--host <host>` | Überschreiben von `llamacpp_host` |
| `--port <port>` | Überschreiben von `llamacpp_port` |
| `--ui-lang <code>` | Sprachcode der Schnittstelle (z.B. `en`, `ru`) |
| `--force` | Überschreiben bereits vorhandene Übersetzungen |

#### Beispiele

```bash
# Translate a single mod to Russian
python pz_translate.py --mode 1 --path "Z:\steam\steamapps\workshop\content\108600\3268487204" --lang RU

# Force re-translation of a single mod to German
python pz_translate.py --mode 1 --path "Z:\steam\steamapps\workshop\content\108600\3268487204" --lang DE --force

# Scan all Workshop mods and pick mods interactively in Russian UI
python pz_translate.py --mode 2 --lang RU --ui-lang ru --port 8734

# Open the progress manager
python pz_translate.py --mode 3
```

---

## Wie es funktioniert

1. **Mod-Entdeckung:** Durchsucht rekursiv Verzeichnisse vom Typ `Translate/<SOURCE_LANG>`, die `.json`-Dateien enthalten, und extrahiert Mod-Namen aus den `mod.info`-Dateien und den Verzeichnisstrukturen des Workshop-Ordners (`mods/<ModName>/<Version>`).
2. **Differenz und Volumenabschätzung:** Vergleicht Schlüssel in `EN/*.json` mit vorhandenen Zieldateien (`<TARGET_LANG>/*.json`) und gespeicherten SHA-1-Hashes in `pz_translator_state.json`. Nur fehlende Schlüssel oder Schlüssel, deren englischer Quelltext seit der letzten Übersetzung geändert wurde, werden in die Warteschlange gestellt.
3. **Übersetzung mit LLM:** Sendet jeden String an `http://<host>:<port>/completion` unter Verwendung des Formats für den Chat-Dialog von TranslateGemma.
4. **Dualer Ausgab:** Jeder `save_every`-Schlüssel (und bei Abschluss oder `Ctrl+C`) schreibt gültiges UTF-8-JSON an:
   - Das Zielverzeichnis für die Mod-Datei: `...\Translate\<LANG>\<file>.json`
   - Das lokale Mirror-Ordner: `pz_translator_mods\<vollständiger_Pfad_ohne_laufwerksbuchstabe>\Translate\<LANG>\<Datei>.json`

---

## Hinweise & Einschränkungen

- **Unterstütztes Format:** Nur die `.json`-Lokalisierungsdateien von Project Zomboid **Build 42.15+** werden verarbeitet. Alte `.txt`-Übersetzungsdateien werden ignoriert, da B42.15+ sie nicht mehr lädt.
- **Mehrspieler (`DoLuaChecksum`):** Da die `Translate`-Ordner sich innerhalb von `media/lua/shared/` befinden, kann das direkte Hinzufügen von Übersetzungsdateien in die Steam Workshop-Ordner zu Inkonsistenzen bei den Checksummen auf Mehrspielerservern mit `DoLuaChecksum=true` führen. Für öffentliche Mehrspielerserver: Entweder die spiegelnden Dateien aus `pz_translator_mods/` als separate Mod, die nur Übersetzungen enthält, verpacken, oder im Einzelspieler-/Server-Modus mit `DoLuaChecksum=false` spielen.
```
