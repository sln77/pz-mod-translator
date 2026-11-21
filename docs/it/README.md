# Traduttore per i mod di Project Zomboid

Uno strumento a riga di comando per localizzare i mod di **Project Zomboid (versione 42.15+)** utilizzando un server locale `llama.cpp` (`llama-server`) alimentato da **TranslateGemma**.

Scansiona la Steam Workshop o le cartelle dei mod locali alla ricerca di file `Translate/EN/*.json`, stima il volume di traduzione (numero di righe e caratteri), traduce le stringhe mancanti o aggiornate, verifica le variabili e i tag di markup dell'interfaccia utente, e crea una copia locale di ogni traduzione generata, in modo da poter facilmente creare mod di traduzione autonome o ripristinare i file dopo gli aggiornamenti di Steam.

---

## Caratteristiche

- **Supporto per il formato JSON 42.15+:** Funziona con il formato di traduzione `.json` moderno utilizzato in Project Zomboid B42.15+ (i mod esistenti in formato `.txt` vengono automaticamente ignorati durante la scansione).
- **Interfaccia Terminale Ricca:** Tabelle colorate, badge di stato e barre di avanzamento in tempo reale con indicazione del tempo trascorso/rimanente, utilizzando la libreria `rich`.
- **Interfaccia a riga di comando multilingue (`i18n`):** Utilizza l'inglese come lingua predefinita e, all'avvio interattivo, chiede all'utente di selezionare la lingua dell'interfaccia da un file JSON disponibile in `cli_locales/*.json`.
- **3 Modalità operative:**
  - **Modalità 1:** Tradurre un singolo modulo specificato (o la sua cartella `Translate` / `EN`).
  - **Modalità 2:** Scansiona l'intera directory del tuo workshop, verifica lo stato delle traduzioni e il volume di caratteri per ogni mod, e seleziona le mod utilizzando i numeri (`1,3,5`), gli intervalli (`1-4`), o il metodo `all`.
  - **Modalità 3:** Gestire i progressi salvati – rilevare aggiornamenti del modulo, tradurre nuove/modificate/danneggiate stringhe, sovrascrivere da zero, ripristinare da una copia, eliminare in modo pulito i file generati, oppure eseguire un rapporto di controllo delle stringhe "dry-run".
- **Identificatori e validazione del markup (`token_rules.json`):** Estrae gli identificatori del mod (`{name}`, `%1`) e i tag RichText di Project Zomboid (`<LINE>`, `<RGB:...>`, `<IMAGE:...>`, ecc.) utilizzando regole di espressione regolare configurabili e verifica una corrispondenza esatta dopo la traduzione. In caso di discrepanza, riprova con semi diversi (`max_retries`). Se tutti i tentativi falliscono, mantiene la stringa originale in inglese, indica lo stato del mod come `EN/<LANG>`, e registra i dettagli in `pz_translator_issues.log`.
- **Rilevamento delle modifiche e monitoraggio dei progressi:** Memorizza gli hash SHA-1 univoci delle stringhe originali in inglese nel file `pz_translator_state.json`. Se un mod viene aggiornato tramite Steam Workshop, solo le chiavi nuove, modificate o con token non validi vengono aggiunte alla coda per la traduzione.
- **Mirror locale (`pz_translator_mods/`):** Salva una copia di ogni file tradotto, preservando la struttura delle directory relative (rendendo facile la creazione di mod dedicate esclusivamente alla traduzione).
- **Sicuro e resistente a guasti:**
  - Le traduzioni di opere già esistenti (sia modifiche originali, sia traduzioni individuali non tracciate nel file `pz_translator_state.json`) non vengono mai analizzate dalle regole basate su token, modificate o sovrascritte.
  - Gestisce il BOM (Byte Order Mark) di UTF-8, le virgole finali nei file JSON modificati manualmente e preserva il campo `$schema` e le stringhe vuote.
  - Salva automaticamente i progressi periodicamente (`save_every`) e quando si preme `Ctrl+C`.

---

## Requisiti

- **Python 3.9 o versioni successive**
- **llama.cpp** (`llama-server`) che esegue un modello **TranslateGemma** in formato GGUF sull'host/porta configurata (impostazione predefinita: `http://127.0.0.1:8734`).
- Dipendenze Python:

```bash
pip install -r requirements.txt
```

---

## Configurazione (`config.json`)

Al primo avvio (o tramite il file `config.json` incluso), lo script utilizza le seguenti impostazioni:

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

| Punti chiave | Descrizione |
| --- | --- |
| `llamacpp_host` | Indirizzo IP o nome del server su cui è in esecuzione `llama-server`. |
| `llamacpp_port` | Avviare il server `llama-server` |
| `mods_path` | La directory radice predefinita viene scansionata in modalità 2 (ad esempio, la cartella `108600` del Workshop di Steam). |
| `default_source_lang` | Nome della cartella di origine per la traduzione (valore predefinito: `EN`) |
| `default_target_lang` | Codice della lingua di destinazione predefinito (ad esempio, `RU`, `DE`, `CN`, `JP`, `PTBR`) |
| `ui_lang` | Codice della lingua predefinito per l'interfaccia, proveniente dalla cartella `cli_locales/` |
| `mirror_dir` | Cartella locale in cui vengono memorizzate le copie complete delle traduzioni generate. |
| `state_file` | File JSON che memorizza la cronologia delle traduzioni e gli hash delle stringhe originali. |
| `token_rules_file` | File JSON contenente regole di espressione regolare e impostazioni per il tentativo di convalida di segnaposto/tag. |
| `save_every` | Salva i progressi su disco e crea una copia di ogni N traduzioni. |

### Validazione dei token (`token_rules.json`)

Le regole di espressione regolare per proteggere le variabili dinamiche e i tag di markup di Project Zomboid sono configurate nel file `token_rules.json`:

| Punti chiave | Descrizione |
| --- | --- |
| `max_retries` | Numero massimo di tentativi di traduzione con diverse "semi" quando i token critici non corrispondono. |
| `retry_temperatures` | Programma di temperature applicato durante i tentativi di riprova (ad esempio, `[0.2, 0.35, 0.5]`) |
| `issues_log` | File di log in cui vengono registrate le stringhe che non sono state validate dopo tutti i tentativi, insieme alla loro origine (`EN`) e ai tentativi falliti. |
| `check_report` | File di output per il rapporto di controllo dei token durante la simulazione (Modalità 3) |
| `rules` | Un array di oggetti che rappresentano le regole di espressione regolare, con i seguenti attributi: `name` (nome), `pattern` (modello), `enabled` (abilitato), `critical` (critico), `description` (descrizione). |

Le regole contrassegnate con `"critical": true` attivano tentativi di ripetizione durante la traduzione e registrano le chiavi da tradurre nuovamente durante gli aggiornamenti. Le regole non critiche (`"critical": false`) vengono segnalate solo come avvisi nel rapporto di verifica preliminare.

---

## Utilizzo

### Modalità interattiva

Iniziare con `llama-server`, quindi eseguire:

```bash
python pz_translate.py
```

1. **Selezionare la lingua dell'interfaccia:** Scegliere tra le lingue disponibili in `cli_locales/` (impostazione predefinita: `en`).
2. **Modalità selezionata:**
   - `1` – Tradurre un percorso di mod specifico.
   - `2` — Scansiona tutti i mod presenti in `mods_path`, visualizza la tabella con il conteggio delle stringhe/caratteri, e inserisci i numeri dei mod (ad esempio, `1,3,5`, `1-4` o `all`).
   - `3` – Gestire i progressi salvati (aggiornare le chiavi di token nuove/modificate/errate, tradurre nuovamente da zero, ripristinare da `pz_translator_mods/`, eliminare le traduzioni o eseguire un rapporto di controllo delle chiavi).
   - `4` – Modificare la lingua dell'interfaccia.
   - `0` – Esci.

### Argomenti della riga di comando

È possibile aggirare il menu interattivo utilizzando i flag della riga di comando (gli argomenti della riga di comando sovrascrivono il file `config.json`):

| Bandiera | Descrizione |
| --- | --- |
| `--config <path>` | Percorso per creare un file `config.json` personalizzato |
| `--rules <path>` | Percorso per creare un file `token_rules.json` personalizzato. |
| `--mode {1,2,3}` | `1` = modifica singola, `2` = scansiona la directory, `3` = gestisci i progressi salvati |
| `--path <path>` | Percorso alla cartella dei mod (Modalità 1) o alla cartella principale dei mod (Modalità 2) |
| `--lang <code>` | Lingua di destinazione come codice della cartella PZ (`RU`, `CN`, `PTBR`) o codice ISO (`ru`, `zh`, `pt-BR`) |
| `--source-lang <code>` | Sovrascrivi la cartella della lingua di origine (valore predefinito: `EN`) |
| `--host <host>` | Sovrascrivi `llamacpp_host` |
| `--port <port>` | Sovrascrivi `llamacpp_port` |
| `--ui-lang <code>` | Codice della lingua dell'interfaccia (ad esempio, `en`, `ru`) |
| `--force` | Sovrascrivere le traduzioni esistenti |
| `--check` | Eseguire un controllo preliminare dei token su tutte le traduzioni salvate e creare un file chiamato `pz_translator_check_report.txt`. |

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

# Run a dry-run token check on all saved translations without calling the LLM
python pz_translate.py --mode 3 --check
```

---

## Come funziona

1. **Scoperta dei Mod:** Cerca ricorsivamente le directory contenenti `Translate/<SOURCE_LANG>` file e `.json`, estraendo i nomi dei mod dalle strutture delle cartelle `mod.info` e Workshop (`mods/<ModName>/<Version>`).
2. **Stima della differenza e del volume:** Confronta le chiavi in `EN/*.json` con i file di riferimento esistenti (`<TARGET_LANG>/*.json`), gli hash SHA-1 memorizzati in `pz_translator_state.json`, e le regole critiche provenienti da `token_rules.json`. Le chiavi mancanti, le chiavi il cui testo originale in inglese è stato modificato, e le chiavi tracciate con segnaposto/tag danneggiati, vengono messe in coda per la traduzione; le traduzioni preesistenti degli autori rimangono inalterate.
3. **Traduzione e validazione LLM:** Invia ogni stringa originale completa all'indirizzo `http://<host>:<port>/completion` utilizzando il formato standardizzato del prompt "TranslateGemma", quindi verifica i token critici rispetto alla stringa originale. In caso di discrepanza, riprova con semi diversi fino a `max_retries`; se tutti i tentativi falliscono, mantiene il testo in inglese, indica lo stato di modifica come `EN/<LANG>`, e registra i dettagli nel file `pz_translator_issues.log`.
4. **Uscita Dupla:** Ogni chiave `save_every` (e al completamento o con `Ctrl+C`), scrive un JSON valido in formato UTF-8 nei seguenti file:
   - La cartella di destinazione per il modulo: `...\Translate\<LANG>\<file>.json`
   - La cartella del riflesso locale: `pz_translator_mods\<full_path_without_drive_letter>\Translate\<LANG>\<file>.json`

---

## Note e limitazioni

- **Formato supportato:** Sono elaborati solo i file di localizzazione `.json` di Project Zomboid, versione 42.15+. I vecchi file di traduzione `.txt` vengono ignorati, poiché la versione 42.15+ non li carica più.
- **Multiplayer (`DoLuaChecksum`):** Poiché le cartelle `Translate` si trovano all'interno di `media/lua/shared/`, l'aggiunta di file di traduzione direttamente all'interno delle cartelle del Steam Workshop può causare discrepanze nei controlli di integrità sui server multiplayer con `DoLuaChecksum=true`. Per i server multiplayer pubblici, è possibile impacchettare i file replicati da `pz_translator_mods/` come un mod separato dedicato esclusivamente alla traduzione, oppure giocare in modalità singleplayer / su server con `DoLuaChecksum=false`.
