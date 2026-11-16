# Traduttore Mod per Project Zomboid

<p align="center">
  <a href="#features">Caratteristiche</a> ·
  <a href="#requirements">Requisiti</a> ·
  <a href="#configuration-configjson">Configurazione</a> ·
  <a href="#usage">Utilizzo</a> ·
  <a href="#come-funziona">Come funziona</a>
</p>

<p align="center">
  <b>Inglese</b> ·
  <a href="docs/ru/README.md">Russo</a> ·
  <a href="docs/zh/README.md">简体中文</a> ·
  <a href="docs/zh-TW/README.md">繁體中文</a> ·
  <a href="docs/ja/README.md">日本語</a> ·
  <a href="docs/ko/README.md">한국어</a> ·
  <a href="docs/de/README.md">Deutsch</a> ·
  <a href="docs/fr/README.md">Francese</a> ·
  <a href="docs/es/README.md">Español</a> ·
  <a href="docs/it/README.md">Italiano</a> ·
  <a href="docs/pt-BR/README.md">Português</a> ·
  <a href="docs/tr/README.md">Türkçe</a> ·
  <a href="docs/uk/README.md">Українська</a> ·
  <a href="docs/pl/README.md">Polacco</a>
</p>

Uno strumento a riga di comando per localizzare i mod di **Project Zomboid (Build 42.15+)** utilizzando un server `llama.cpp` locale (`llama-server`) alimentato da **TranslateGemma**.

Scansiona il Workshop di Steam o le cartelle dei mod locali alla ricerca di file `Translate/EN/*.json`, stima il volume di traduzione (numero di righe e caratteri), traduce le stringhe mancanti o aggiornate e crea una copia locale di ogni traduzione generata, in modo da poter facilmente creare mod di traduzione autonome o ripristinare i file dopo gli aggiornamenti di Steam.

---

## Funzionalità

- **Supporto JSON per la versione 42.15+:** Funziona con il formato di traduzione `.json` moderno utilizzato in Project Zomboid 42.15+ (i mod legacy basati solo su `.txt` vengono ignorati in modo sicuro durante la scansione).
- **Interfaccia Terminale Intuitiva:** Tabelle colorate pulite, badge di stato e barre di avanzamento in tempo reale con tempo trascorso/rimanente, grazie a `rich`.
- **CLI multilingue (`i18n`):** Imposta l'inglese come lingua predefinita e chiede all'utente di selezionare la lingua dell'interfaccia da `cli_locales/*.json` all'avvio interattivo.
- **3 Modalità operative:**
  - **Modalità 1:** Tradurre un singolo modulo specificato (o la sua cartella `Translate` / `EN`).
  - **Modalità 2:** Scansiona l'intera directory del tuo Workshop, controlla lo stato delle traduzioni e il volume dei caratteri per ogni mod, e seleziona le mod tramite numeri (`1,3,5`), intervalli (`1-4`) o `tutte`.
  - **Modalità 3:** Gestire i progressi salvati — rilevare gli aggiornamenti del modulo, tradurre solo le nuove/modificate stringhe, sovrascrivere da zero, ripristinare da un mirror, oppure eliminare in modo pulito i file generati.
- **Rilevamento delle modifiche e monitoraggio dei progressi:** Memorizza gli hash SHA-1 univoci per ogni chiave delle stringhe originali in inglese nel file `pz_translator_state.json`. Se una modifica viene apportata tramite il Steam Workshop, solo le nuove chiavi inglesi o quelle modificate vengono aggiunte alla coda per la traduzione.
- **Mirror locale (`pz_translator_mods/`):** Salva una copia di ogni file tradotto, preservando la struttura delle directory relative (rendendo facile la creazione di mod standalone dedicate esclusivamente alla traduzione).
- **Sicuro e resistente ai guasti:**
  - Le traduzioni esistenti dell'autore con `0` chiavi in attesa non vengono modificate, sovrascritte o monitorate.
  - Gestisce il BOM UTF-8, le virgole finali nei file JSON modificati manualmente e preserva `$schema` e le stringhe vuote.
  - Salva automaticamente i progressi periodicamente (`save_every`) e con `Ctrl+C`.

---

## Requisiti

- **Python 3.9+**
- **llama.cpp** (`llama-server`) che esegue un modello **TranslateGemma** GGUF sull'host/porta configurata (predefinito: `http://127.0.0.1:8734`).
- Dipendenze Python:

```bash
pip install -r requirements.txt
```

---

## Configurazione (`config.json`)

All'avvio (o tramite il file `config.json` incluso), lo script utilizza le seguenti impostazioni:

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

| Chiave | Descrizione |
| --- | --- |
| `llamacpp_host` | Indirizzo dell'host del tuo `llama-server` in esecuzione |
| `llamacpp_port` | Porta del tuo server `llama-server` in esecuzione |
| `mods_path` | Directory principale predefinita scansionata in Modalità 2 (ad esempio, la cartella `108600` del Workshop di Steam) |
| `default_source_lang` | Nome della cartella di origine per la traduzione (valore predefinito: `EN`) |
| `default_target_lang` | Codice della lingua di destinazione predefinito (ad esempio, `RU`, `DE`, `CN`, `JP`, `PTBR`) |
| `ui_lang` | Codice della lingua predefinito dell'interfaccia da `cli_locales/` |
| `mirror_dir` | Cartella locale in cui sono memorizzate le copie complete dei file di traduzione generati. |
| `state_file` | File JSON che memorizza la cronologia delle traduzioni e gli hash delle stringhe originali |
| `save_every` | Salva i progressi su disco e crea una copia di ogni N chiavi tradotte. |

---

## Utilizzo

### Modalità interattiva

Avvia prima `llama-server`, quindi esegui:

```bash
python pz_translate.py
```

1. **Selezionare la lingua dell'interfaccia:** Scegliere tra le lingue disponibili in `cli_locales/` (predefinito: `en`).
2. **Seleziona modalità:**
   - `1` — Traduci un percorso di mod specifico.
   - `2` — Scansionare tutti i mod in `mods_path`, visualizzare la tabella con il conteggio di stringhe/caratteri, e inserire i numeri dei mod (ad esempio, `1,3,5`, `1-4`, o `tutti`).
   - `3` — Gestire i progressi salvati (aggiornare le chiavi modificate/nuove, tradurre nuovamente da zero, ripristinare da `pz_translator_mods/`, oppure eliminare le traduzioni).
   - `4` — Cambiare la lingua dell'interfaccia.
   - `0` — Esci.

### Argomenti della riga di comando

È possibile bypassare il menu interattivo utilizzando i flag della riga di comando (gli argomenti della riga di comando sovrascrivono `config.json`):

| Bandiera | Descrizione |
| --- | --- |
| `--config <percorso>` | Percorso a un file `config.json` personalizzato |
| `--mode {1, 2, 3}` | `1` = modulo singolo, `2` = scansiona la directory, `3` = gestisci i progressi salvati |
| `--path <path>` | Percorso alla cartella dei mod (Modalità 1) o alla cartella principale dei mod (Modalità 2) |
| `--lang <code>` | Lingua di destinazione come codice della cartella PZ (`RU`, `CN`, `PTBR`) o codice ISO (`ru`, `zh`, `pt-BR`) |
| `--source-lang <code>` | Sovrascrivi la cartella della lingua di origine (predefinito: `EN`) |
| `--host <host>` | Sovrascrivi `llamacpp_host` |
| `--port <porta>` | Sovrascrivi `llamacpp_port` |
| `--ui-lang <code>` | Codice della lingua dell'interfaccia (ad esempio, `en`, `ru`) |
| `--force` | Sovrascrivi le traduzioni esistenti |

#### Esempi

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

## Come funziona

1. **Scoperta Mod:** Cerca ricorsivamente le directory `Translate/<SOURCE_LANG>` contenenti file `.json` e estrae i nomi dei mod dai file `mod.info` e dalle strutture delle cartelle del Workshop (`mods/<ModName>/<Version>`).
2. **Stima delle differenze e del volume:** Confronta le chiavi in `EN/*.json` con i file di destinazione esistenti (`<TARGET_LANG>/*.json`) e gli hash SHA-1 memorizzati in `pz_translator_state.json`. Vengono aggiunte solo le chiavi mancanti o le chiavi il cui testo originale in inglese è stato modificato rispetto all'ultima traduzione.
3. **Traduzione LLM:** Invia ogni stringa a `http://<host>:<port>/completion` utilizzando il formato di conversazione di TranslateGemma.
4. **Uscita Dupla:** Ogni chiave `save_every` (e al completamento o con `Ctrl+C`), scrive un JSON UTF-8 valido in:
   - La cartella di destinazione per il modulo: `...\Translate\<LANG>\<file>.json`
   - La cartella del mirror locale: `pz_translator_mods\<percorso_completo_senza_lettera_di_unità>\Translate\<LINGUA>\<file>.json`

---

## Note e limitazioni

- **Formato supportato:** Vengono elaborati solo i file di localizzazione `.json` di Project Zomboid **Build 42.15+**. I vecchi file di traduzione `.txt` vengono ignorati perché B42.15+ non li carica più.
- **Multiplayer (`DoLuaChecksum`):** Poiché le cartelle `Translate` si trovano all'interno di `media/lua/shared/`, l'aggiunta diretta dei file di traduzione all'interno delle cartelle del Steam Workshop può causare incongruenze nei checksum sui server multiplayer con `DoLuaChecksum=true`. Per i server multiplayer pubblici, è possibile impacchettare i file duplicati da `pz_translator_mods/` come un mod separato dedicato esclusivamente alla traduzione, oppure giocare in modalità singleplayer / su server con `DoLuaChecksum=false`.
```
