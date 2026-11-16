# 《Project Zomboid》模組翻譯

<p align="center">
  <a href="#features">功能</a> ·
  <a href="#requirements">需求</a> ·
  <a href="#configuration-configjson">配置</a> ·
  <a href="#usage">使用方法</a> ·
  <a href="#how-it-works">工作原理</a>
</p>

<p align="center">
  <b>英文</b> ·
  <a href="docs/ru/README.md">俄語</a> ·
  <a href="docs/zh/README.md">簡化中文</a> ·
  <a href="docs/zh-TW/README.md">繁體中文</a> ·
  <a href="docs/ja/README.md">日語</a> ·
  <a href="docs/ko/README.md">韓語</a> ·
  <a href="docs/de/README.md">德語</a> ·
  <a href="docs/fr/README.md">法文</a> ·
  <a href="docs/es/README.md">西班牙語</a> ·
  <a href="docs/it/README.md">意大利語</a> ·
  <a href="docs/pt-BR/README.md">葡萄牙語</a> ·
  <a href="docs/tr/README.md"> Türkçe </a> ·
  <a href="docs/uk/README.md">烏克蘭語</a> ·
  <a href="docs/pl/README.md">波蘭語</a>
</p>

一個用於本地化 **Project Zomboid (Build 42.15+)** 的模組，使用本地的 `llama.cpp` 伺服器 (`llama-server`)，並由 **TranslateGemma** 驅動的 CLI 工具。

它會掃描 Steam 商店或本地模組資料夾，尋找 `Translate/EN/*.json` 檔案，估算翻譯量（行數和字數），翻譯缺失或更新的字串，並將所有生成的翻譯本地複製一份，以便您可以輕鬆地打包獨立的翻譯模組，或在 Steam 更新後還原檔案。

---

## 特色

- **支援 42.15+ 的 JSON 格式：** 與 Project Zomboid B42.15+ 使用的現代 `.json` 翻譯格式相容 (舊的 `.txt` 格式的模組在掃描過程中會被安全跳過)。
- **豐富的終端介面：** 乾淨的彩色表格、狀態徽章，以及帶有已過/剩餘時間的實時進度條，皆由 `rich` 實現。
- **多語言 CLI (`i18n`):** 預設為英文，在互動式啟動時，會提示使用者從 `cli_locales/*.json` 選擇介面語言。
- **3 種工作模式：**
  - **模式 1：** 翻譯一個指定的模組（或其 `Translate` / `EN` 資料夾）。
  - **模式 2：** 掃描整個工作目錄，檢查每個模組的翻譯狀態和字數，並選擇模組（例如：`1,3,5`、範圍：`1-4` 或 `全部`）。
  - **模式 3：管理已儲存的進度 — 偵測模組更新、僅翻譯新的/變更的字串、從頭開始重新建立、從鏡像恢復，或乾淨地刪除產生的檔案。**
- **偵測更新與進度追蹤：** 在 `pz_translator_state.json` 中儲存來源英文字串的每個鍵的 SHA-1 哈希值。如果 Steam Workshop 中的模組更新，只有新增或修改的英文鍵會排入翻譯佇列。
- **本地鏡像 (`pz_translator_mods/`):** 儲存所有翻譯文件的副本，並保留相對目錄結構（這使得創建獨立的僅用於翻譯的模組變得容易）。
- **安全且容錯性高：**
  - 先前已存在的作者翻譯，如果沒有任何待處理的關鍵字 (`0`)，則不會被修改、覆蓋或追蹤。
  - 支援 UTF-8 BOM、手動編輯的 mod JSON 中的尾隨逗號，並保留 `$schema` 和空字串。
  - 自動儲存進度，定期 (`save_every`)，以及在按下 `Ctrl+C` 鍵時。

---

## 需求

- **Python 3.9+**
- **llama.cpp** (`llama-server`) 運行一個 **TranslateGemma** 的 GGUF 模型，在配置的主機/埠上 (預設：`http://127.0.0.1:8734`)。
- Python 依賴：

```bash
pip install -r requirements.txt
```

---

## 配置 (`config.json`)

首次執行 (或透過內建的 `config.json`)，腳本將使用以下設定：

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

| 關鍵 | 說明 |
| --- | --- |
| `llamacpp_host` | 您的正在運行的 `llama-server` 的主機位址 |
| `llamacpp_port` | 連接您的 `llama-server` |
| `mods_path` | 預設根目錄在模式 2 下進行掃描 (例如，Steam Workshop `108600` 資料夾) |
| `default_source_lang` | 原始翻譯資料夾名稱 (預設: `EN`) |
| `default_target_lang` | 預設目標語言代碼 (例如：`RU`、`DE`、`CN`、`JP`、`PTBR`) |
| `ui_lang` | 預設介面語言代碼，來自 `cli_locales/` |
| `mirror_dir` | 本地資料夾，用於儲存生成的翻譯的完整路徑副本 |
| `state_file` | JSON 檔案，用於儲存翻譯歷史記錄和原始字串的雜湊值 |
| `save_every` | 將進度儲存到磁碟，並每 N 個翻譯的關鍵詞建立備份 |

---

## 使用方法

### 互動模式

首先啟動 `llama-server`，然後執行：

```bash
python pz_translate.py
```

1. **選擇介面語言：** 從 `cli_locales/` 裡的可用語言中選擇 (預設：`en`)。
2. **選擇模式：**
   - `1` — 翻譯特定模組路徑。
   - `2` — 掃描 `mods_path` 裡的全部模組，查看包含字串/字元計數的表格，並輸入模組編號（例如：`1,3,5`、`1-4` 或 `全部`）。
   - `3` — 管理已儲存的進度 (更新變更/新增的關鍵字，重新翻譯，從頭開始翻譯，或從 `pz_translator_mods/` 恢復，或刪除翻譯)。
   - `4` — 更改介面語言。
   - `0` — 退出。

### 命令行參數

您可以使用 CLI 參數（CLI 參數會覆蓋 `config.json`）來繞過互動式選單。

| 旗幟 | 說明 |
| --- | --- |
| `--config <路徑>` | 前往自定義的 `config.json` 檔案 |
| `--mode {1, 2, 3}` | `1` = 單個模組，`2` = 掃描目錄，`3` = 管理已儲存的進度 |
| `--path <path>` | 前往模組資料夾的路徑 (模式 1) 或模組根資料夾的路徑 (模式 2) |
| `--lang <code>` | 目標語言為 PZ 檔案碼 (`RU`, `CN`, `PTBR`) 或 ISO 碼 (`ru`, `zh`, `pt-BR`) |
| `--source-lang <code>` | 覆蓋原始語言資料夾 (預設: `EN`) |
| `--host <host>` | 覆蓋 `llamacpp_host` |
| `--port <port>` | 覆蓋 `llamacpp_port` |
| `--ui-lang <code>` | 介面語言代碼 (例如：`en`, `ru`) |
| `--force` | 覆蓋現有翻譯 |

#### 範例

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

## 它是如何運作的

1. **模組發現：** 遞迴搜尋包含 `.json` 檔案的 `Translate/<SOURCE_LANG>` 檔案夾，並從 `mod.info` 和工作區檔案結構 (`mods/<ModName>/<Version>`) 中提取模組名稱。
2. **差異與音量估算：** 比較 `EN/*.json` 中的鍵值與現有目標檔案 (`<TARGET_LANG>/*.json`) 以及儲存於 `pz_translator_state.json` 中的 SHA-1 哈希值。 僅將缺少或自上次翻譯後，英文來源文字已變更的鍵值列入佇列。
3. **LLM 翻譯：** 使用 `TranslateGemma` 聊天回合格式，將每個字串發送到 `http://<host>:<port>/completion`。
4. **雙重輸出：** 每次執行 `save_every` 關鍵字 (以及在完成或按下 `Ctrl+C`)，都會將有效的 UTF-8 JSON 寫入：
   - 目標模組資料夾：`...\Translate\<LANG>\<file>.json`
   - 本地鏡像資料夾：`pz_translator_mods\<完整路徑，不含磁碟符號>\Translate\<語言>\<檔案>.json`

---

## 備註與限制

- **支援格式：** 僅支援 Project Zomboid **42.15+** 的 `.json` 翻譯檔案。舊的 `.txt` 翻譯檔案將被忽略，因為 B42.15+ 不再載入它們。
- **多人遊戲 (`DoLuaChecksum`):** 因為 `Translate` 資料夾位於 `media/lua/shared/` 內，直接將翻譯檔案添加到 Steam Workshop 資料夾中，可能會在 `DoLuaChecksum=true` 的多人遊戲伺服器上觸發檢查碼不符。對於公開的多人遊戲伺服器，您可以將 `pz_translator_mods/` 中的鏡像檔案打包成一個僅包含翻譯的獨立模組，或在單人模式/伺服器上使用 `DoLuaChecksum=false`。
```
