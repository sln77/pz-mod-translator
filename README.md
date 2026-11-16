# Project Zomboid Mod Translator

<p align="center">
  <a href="#features">Features</a> ·
  <a href="#requirements">Requirements</a> ·
  <a href="#configuration-configjson">Config</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#how-it-works">How It Works</a>
</p>

<p align="center">
  <b>English</b> ·
  <a href="docs/ru/README.md">Русский</a> ·
  <a href="docs/zh/README.md">简体中文</a> ·
  <a href="docs/zh-TW/README.md">繁體中文</a> ·
  <a href="docs/ja/README.md">日本語</a> ·
  <a href="docs/ko/README.md">한국어</a> ·
  <a href="docs/de/README.md">Deutsch</a> ·
  <a href="docs/fr/README.md">Français</a> ·
  <a href="docs/es/README.md">Español</a> ·
  <a href="docs/it/README.md">Italiano</a> ·
  <a href="docs/pt-BR/README.md">Português</a> ·
  <a href="docs/tr/README.md">Türkçe</a> ·
  <a href="docs/uk/README.md">Українська</a> ·
  <a href="docs/pl/README.md">Polski</a>
</p>

A CLI tool for localizing **Project Zomboid (Build 42.15+)** mods using a local `llama.cpp` server (`llama-server`) powered by **TranslateGemma**.

It scans Steam Workshop or local mod folders for `Translate/EN/*.json` files, estimates translation volume (lines and character count), translates missing or updated strings, and mirrors every generated translation locally so you can easily package standalone translation mods or restore files after Steam updates.

---

## Features

- **Build 42.15+ JSON Support:** Works with the modern `.json` translation format used in Project Zomboid B42.15+ (legacy `.txt`-only mods are safely skipped during scans).
- **Rich Terminal Interface:** Clean colored tables, status badges, and live progress bars with elapsed/remaining time via `rich`.
- **Multilingual CLI (`i18n`):** Defaults to English and prompts to select the interface language from `cli_locales/*.json` on interactive startup.
- **3 Working Modes:**
  - **Mode 1:** Translate a single specified mod (or its `Translate` / `EN` folder).
  - **Mode 2:** Scan your entire Workshop directory, inspect translation status and character volume per mod, and select mods by numbers (`1,3,5`), ranges (`1-4`), or `all`.
  - **Mode 3:** Manage saved progress — detect mod updates, translate only new/changed strings, overwrite from scratch, restore from mirror, or cleanly delete generated files.
- **Update Detection & Progress Tracking:** Stores per-key SHA-1 hashes of source English strings in `pz_translator_state.json`. If a mod updates in Steam Workshop, only newly added or modified English keys are queued for translation.
- **Local Mirror (`pz_translator_mods/`):** Saves a copy of every translated file preserving the relative directory tree (making it easy to build standalone translation-only mods).
- **Safe & Fault-Tolerant:**
  - Pre-existing author translations with `0` pending keys are never touched, overwritten, or tracked.
  - Handles UTF-8 BOM, trailing commas in hand-edited mod JSONs, and preserves `$schema` and empty strings.
  - Auto-saves progress periodically (`save_every`) and on `Ctrl+C`.

---

## Requirements

- **Python 3.9+**
- **llama.cpp** (`llama-server`) running a **TranslateGemma** GGUF model on the configured host/port (default: `http://127.0.0.1:8734`).
- Python dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration (`config.json`)

On first run (or via the included `config.json`), the script uses the following settings:

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

| Key | Description |
| --- | --- |
| `llamacpp_host` | Host address of your running `llama-server` |
| `llamacpp_port` | Port of your running `llama-server` |
| `mods_path` | Default root directory scanned in Mode 2 (e.g., Steam Workshop `108600` folder) |
| `default_source_lang` | Source translation folder name (default: `EN`) |
| `default_target_lang` | Default target language code (e.g., `RU`, `DE`, `CN`, `JP`, `PTBR`) |
| `ui_lang` | Default interface language code from `cli_locales/` |
| `mirror_dir` | Local folder where full-path copies of generated translations are stored |
| `state_file` | JSON file storing translation history and source string hashes |
| `save_every` | Save progress to disk and mirror every N translated keys |

---

## Usage

### Interactive Mode

Start `llama-server` first, then run:

```bash
python pz_translate.py
```

1. **Select Interface Language:** Choose from available languages in `cli_locales/` (default: `en`).
2. **Select Mode:**
   - `1` — Translate a specific mod path.
   - `2` — Scan all mods in `mods_path`, view the table with string/character counts, and enter mod numbers (e.g., `1,3,5`, `1-4`, or `all`).
   - `3` — Manage saved progress (update changed/new keys, re-translate from scratch, restore from `pz_translator_mods/`, or delete translations).
   - `4` — Change interface language.
   - `0` — Exit.

### Command-Line Arguments

You can bypass the interactive menu using CLI flags (CLI arguments override `config.json`):

| Flag | Description |
| --- | --- |
| `--config <path>` | Path to a custom `config.json` file |
| `--mode {1,2,3}` | `1` = single mod, `2` = scan directory, `3` = manage saved progress |
| `--path <path>` | Path to a mod folder (Mode 1) or mods root folder (Mode 2) |
| `--lang <code>` | Target language as a PZ folder code (`RU`, `CN`, `PTBR`) or ISO code (`ru`, `zh`, `pt-BR`) |
| `--source-lang <code>` | Override source language folder (default: `EN`) |
| `--host <host>` | Override `llamacpp_host` |
| `--port <port>` | Override `llamacpp_port` |
| `--ui-lang <code>` | Interface language code (e.g., `en`, `ru`) |
| `--force` | Overwrite already existing translations |

#### Examples

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

## How It Works

1. **Mod Discovery:** Recursively searches for `Translate/<SOURCE_LANG>` directories containing `.json` files and extracts mod names from `mod.info` and Workshop folder structures (`mods/<ModName>/<Version>`).
2. **Diff & Volume Estimation:** Compares keys in `EN/*.json` against existing target files (`<TARGET_LANG>/*.json`) and stored SHA-1 hashes in `pz_translator_state.json`. Only missing keys or keys whose English source text changed since the last translation are queued.
3. **LLM Translation:** Sends each string to `http://<host>:<port>/completion` using TranslateGemma chat turn formatting.
4. **Dual Output:** Every `save_every` keys (and on completion or `Ctrl+C`), writes valid UTF-8 JSON to:
   - The target mod folder: `...\Translate\<LANG>\<file>.json`
   - The local mirror folder: `pz_translator_mods\<full_path_without_drive_letter>\Translate\<LANG>\<file>.json`

---

## Notes & Limitations

- **Supported Format:** Only Project Zomboid **Build 42.15+** `.json` localization files are processed. Old `.txt` translation files are ignored because B42.15+ no longer loads them.
- **Multiplayer (`DoLuaChecksum`):** Because `Translate` folders reside inside `media/lua/shared/`, adding translation files directly inside Steam Workshop folders can trigger checksum mismatches on multiplayer servers with `DoLuaChecksum=true`. For public multiplayer servers, either package the mirrored files from `pz_translator_mods/` as a separate translation-only mod or play in singleplayer / servers with `DoLuaChecksum=false`.
```