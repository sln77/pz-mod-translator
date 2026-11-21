# Übersetzer für den Project Zomboid Mod

Ein Kommandozeilen-Tool zur Lokalisierung von **Project Zomboid (Version 42.15+)** Mods unter Verwendung eines lokalen `llama.cpp`-Servers (`llama-server`), der von **TranslateGemma** betrieben wird.

Es durchsucht den Steam Workshop oder lokale Mod-Ordner nach Dateien mit der Erweiterung `Translate/EN/*.json`, schätzt die Übersetzungsvolumen (Anzahl der Zeilen und Zeichen), übersetzt fehlende oder aktualisierte Texte, validiert Variablen und UI-Markup-Tags und speichert jede generierte Übersetzung lokal, sodass Sie problemlos eigenständige Übersetzungsmodifikationen erstellen oder Dateien nach Steam-Updates wiederherstellen können.

---

## Eigenschaften

- **Unterstützung für JSON-Dateien (Version 42.15+):** Funktioniert mit dem modernen `.json`-Format, das in Project Zomboid B42.15+ verwendet wird (alte `.txt`-basierte Mods werden während der Scans sicher übersprungen).
- **Reichhaltige Terminal-Schnittstelle:** Saubere, farbige Tabellen, Status-Symbole und dynamische Fortschrittsbalken mit verbleibender/vergangener Zeit, basierend auf der `rich`-Bibliothek.
- **Mehrsprachige Kommandozeile (`i18n`):** Standardmäßig auf Englisch eingestellt und bietet bei interaktivem Start die Möglichkeit, die Benutzersprache aus `cli_locales/*.json` auszuwählen.
- **3 Betriebsmodi:**
  - **Modus 1:** Übersetzen Sie ein einzelnes, angegebenes Mod (oder seinen `Translate` / `EN`-Ordner).
  - **Modus 2:** Scannen Sie das gesamte Verzeichnis Ihres Arbeitsbereichs, überprüfen Sie den Status der Übersetzungen und die Anzahl der Zeichen pro Modul, und wählen Sie Module anhand von Nummern (`1,3,5`), Bereichen (`1-4`) oder `all` aus.
  - **Modus 3:** Verwaltung gespeicherter Fortschritte – Erkennen von Mod-Updates, Übersetzung neuer/geänderter/fehlerhafter Token-Strings, Neuaufbau von Grund auf, Wiederherstellung aus einem Spiegel, sauberes Löschen generierter Dateien oder Ausführen eines Berichts zur Überprüfung der Token-Funktionalität.
- **Platzhalter und Markup-Validierung (`token_rules.json`):** Extrahiert Mod-Platzhalter (`{name}`, `%1`) und Project Zomboid RichText-Tags (`<LINE>`, `<RGB:...>`, `<IMAGE:...>`, usw.) mithilfe konfigurierbarer regulären Ausdrücke und überprüft eine exakte Übereinstimmung nach der Übersetzung. Bei einer Diskrepanz werden alternative Versuche mit unterschiedlichen Seeds (`max_retries`) durchgeführt. Wenn alle Versuche fehlschlagen, behält die ursprüngliche englische Zeichenkette, kennzeichnet den Mod-Status als `EN/<LANG>`, und protokolliert Details in `pz_translator_issues.log`.
- **Erkennung von Aktualisierungen und Fortschrittsverfolgung:** Speichert SHA-1-Hashes der ursprünglichen englischen Zeichenketten pro Schlüssel in der Datei `pz_translator_state.json`. Wenn eine Mod-Aktualisierung im Steam Workshop erfolgt, werden nur neu hinzugefügte, geänderte oder fehlerhafte Schlüssel für die Übersetzung in eine Warteschlange gestellt.
- **Lokales Spiegelbild (`pz_translator_mods/`):** Speichert eine Kopie jeder übersetzten Datei und bewahrt dabei die relative Verzeichnisstruktur (was die Erstellung von eigenständigen Modulen erleichtert, die ausschließlich für die Übersetzung verwendet werden).
- **Sicher und fehlerverträglich:**
  - Vorhandene Übersetzungen von Autoren (sowohl unveränderte Mods als auch individuelle Übersetzungen, die nicht in der Datei `pz_translator_state.json` erfasst werden), werden niemals von Token-Regeln analysiert, verändert oder überschrieben.
  - Unterstützt die UTF-8-Byte-Order-Marke, abschließende Kommas in handbearbeiteten Mod-JSON-Dateien und bewahrt die `$schema`-Angabe sowie leere Zeichenketten.
  - Die automatische Speicherung erfolgt periodisch (`save_every`) und zusätzlich bei `Ctrl+C`.

---

## Anforderungen

- **Python 3.9 oder höher**
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
    "token_rules_file": "token_rules.json",
    "save_every": 20
}
```

| Schlüssel | Beschreibung |
| --- | --- |
| `llamacpp_host` | Adresse des Servers, auf dem Ihr `llama-server` läuft |
| `llamacpp_port` | Starten Sie Ihren `llama-server`. |
| `mods_path` | Standard-Wurzelverzeichnis wird im Modus 2 gescannt (z. B. das Verzeichnis `108600` im Steam Workshop). |
| `default_source_lang` | Name des Ordners für die Quelldateien (Standard: `EN`) |
| `default_target_lang` | Standard-Sprachcode (z.B. `RU`, `DE`, `CN`, `JP`, `PTBR`) |
| `ui_lang` | Standard-Sprachcode für die Benutzeroberfläche aus dem Verzeichnis `cli_locales/` |
| `mirror_dir` | Lokales Verzeichnis, in dem vollständige Pfad-Kopien der generierten Übersetzungen gespeichert werden. |
| `state_file` | JSON-Datei, die die Übersetzungsgeschichte und die Hashes der ursprünglichen Zeichenketten speichert |
| `token_rules_file` | JSON-Datei mit regulären Ausdrücken und Einstellungen für Wiederholungsversuche zur Validierung von Platzhaltern/Tags |
| `save_every` | Fortschritt speichern auf der Festplatte und alle N übersetzten Schlüssel synchronisieren. |

### Token-Validierung (`token_rules.json`)

Reguläre Ausdrücke zur Absicherung dynamischer Variablen und Projekt Zomboid-Markup-Tags sind in der Datei `token_rules.json` konfiguriert:

| Schlüssel | Beschreibung |
| --- | --- |
| `max_retries` | Maximale Anzahl an Übersetzungsversuchen mit unterschiedlichen Startwerten, wenn wichtige Token nicht übereinstimmen. |
| `retry_temperatures` | Temperaturschema wird für alle Wiederholungsversuche angewendet (z.B. `[0.2, 0.35, 0.5]`) |
| `issues_log` | Protokolldatei, in der Zeichen, die nach allen Wiederholungsversuchen die Validierung nicht bestanden haben, zusammen mit ihrer Quelle `EN` und den fehlgeschlagenen Versuchen, aufgezeichnet werden. |
| `check_report` | Ausgabedatei für den Bericht zur Überprüfung von Token im Modus 3 |
| `rules` | Eine Sammlung von Regex-Regelobjekten (mit den Attributen `name`, `pattern`, `enabled`, `critical` und `description`) |

Regeln, die mit `"critical": true` gekennzeichnet sind, lösen während der Übersetzung Wiederholungsversuche aus und protokollieren Schlüssel, die für eine erneute Übersetzung bei Updates benötigt werden. Nicht-kritische Regeln (`"critical": false`) werden nur im Bericht der Testlauf-Überprüfung als Warnungen angezeigt.

---

## Verwendung

### Interaktiver Modus

Beginnen Sie zuerst mit dem Starten von `llama-server`, und anschließend führen Sie folgenden Befehl aus:

```bash
python pz_translate.py
```

1. **Auswahl der Benutzerschnittstellen-Sprache:** Wählen Sie aus den verfügbaren Sprachen im Verzeichnis `cli_locales/` (Standard: `en`).
2. **Auswahlmodus:**
   - `1` – Eine bestimmte Mod-Pfad übersetzen.
   - `2` – Alle Mods in `mods_path` scannen, die Tabelle mit Zeichen-/Zeichenanzahl anzeigen und die Mod-Nummern eingeben (z.B. `1,3,5`, `1-4` oder `all`).
   - `3` – Verwaltung gespeicherter Fortschritte (Aktualisierung neuer/geänderter/fehlerhafter Token-Schlüssel, Neubearbeitung von Grund auf, Wiederherstellung aus `pz_translator_mods/`, Löschen von Übersetzungen oder Ausführen eines Testberichts zur Token-Prüfung).
   - `4` – Sprache der Benutzeroberfläche ändern.
   - `0` – Beenden.

### Kommandozeilenargumente

Sie können das interaktive Menü mithilfe von Befehlszeilenargumenten (CLI-Argumente überschreiben die `config.json`-Datei) umgehen.

| Flagge | Beschreibung |
| --- | --- |
| `--config <path>` | Der Weg zu einer benutzerdefinierten `config.json`-Datei |
| `--rules <path>` | Der Weg zu einer benutzerdefinierten `token_rules.json`-Datei |
| `--mode {1,2,3}` | `1` = Einzelne Modus, `2` = Verzeichnis scannen, `3` = gespeicherten Fortschritt verwalten |
| `--path <path>` | Pfad zum Mod-Ordner (Modus 1) oder zum Stammordner für Mods (Modus 2) |
| `--lang <code>` | Zielsprache als PZ-Ordnercode (`RU`, `CN`, `PTBR`) oder ISO-Code (`ru`, `zh`, `pt-BR`) |
| `--source-lang <code>` | Überschreiben des Quell-Sprachordners (Standard: `EN`) |
| `--host <host>` | Überschreiben von `llamacpp_host` |
| `--port <port>` | Überschreiben von `llamacpp_port` |
| `--ui-lang <code>` | Sprachcode der Benutzeroberfläche (z. B. `en`, `ru`) |
| `--force` | Vorhandene Übersetzungen überschreiben |
| `--check` | Führen Sie eine Testprüfung aller gespeicherten Übersetzungen durch und erstellen Sie eine Datei namens `pz_translator_check_report.txt`. |

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

# Run a dry-run token check on all saved translations without calling the LLM
python pz_translate.py --mode 3 --check
```

---

## Wie es funktioniert

1. **Mod-Entdeckung:** Durchsucht rekursiv Verzeichnisse vom Typ `Translate/<SOURCE_LANG>`, die `.json`-Dateien enthalten, und extrahiert Mod-Namen aus den Dateien `mod.info` und den Ordnerstrukturen des Workshop-Verzeichnisses (`mods/<ModName>/<Version>`).
2. **Vergleich und Volumenabschätzung:** Vergleicht die Schlüssel in `EN/*.json` mit vorhandenen Zieldateien (`<TARGET_LANG>/*.json`), gespeicherten SHA-1-Hashes in `pz_translator_state.json` und wichtigen Regeln aus `token_rules.json`. Fehlende Schlüssel, Schlüssel, deren englischer Quelltext geändert wurde, und verfolgte Schlüssel mit fehlerhaften Platzhaltern/Tags werden für die Übersetzung in eine Warteschlange gestellt; bereits vorhandene Übersetzungen von Autoren bleiben unverändert.
3. **Übersetzung und Validierung von LLMs:** Sendet jede vollständige Originalzeichenkette an `http://<host>:<port>/completion` unter Verwendung des standardisierten TranslateGemma-Prompts, und prüft anschließend kritische Token auf Übereinstimmung mit der Originalzeichenkette. Bei einer Diskrepanz werden bis zu `max_retries` verschiedene Seeds verwendet. Wenn alle Versuche fehlschlagen, behält das System den englischen Text, markiert den Modifizierungsstatus als `EN/<LANG>`, und protokolliert die Details in `pz_translator_issues.log`.
4. **Dualer Ausgabemodus:** Jeder `save_every`-Schlüssel (und bei Abschluss oder `Ctrl+C`) schreibt gültiges UTF-8-JSON in:
   - Das Zielverzeichnis für die Mod-Dateien: `...\Translate\<LANG>\<file>.json`
   - Das lokale Spiegelverzeichnis: `pz_translator_mods\<full_path_without_drive_letter>\Translate\<LANG>\<file>.json`

---

## Anmerkungen und Einschränkungen

- **Unterstützte Dateiformat:** Nur die `.json`-Dateien für die Lokalisierung von Project Zomboid **Build 42.15+** werden verarbeitet. Ältere `.txt`-Dateien für Übersetzungen werden ignoriert, da B42.15+ diese nicht mehr lädt.
- **Mehrspieler (`DoLuaChecksum`):** Da die Ordner `Translate` sich innerhalb von `media/lua/shared/` befinden, kann das direkte Hinzufügen von Übersetzungsdateien in die Steam Workshop-Ordner zu Inkonsistenzen bei der Überprüfung der Checksummen auf Mehrspielerservern mit `DoLuaChecksum=true` führen. Für öffentliche Mehrspielerserver sollte entweder eine separate Mod erstellt werden, die die spiegelnden Dateien aus `pz_translator_mods/` enthält, oder im Einzelspieler- / Server-Modus mit `DoLuaChecksum=false` gespielt werden.
