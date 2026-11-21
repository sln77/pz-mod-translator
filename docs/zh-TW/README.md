# 《Zomboid》模翻譯

一個用於將 **Project Zomboid (版本 42.15+)** 的模組，透過本地的 `llama.cpp` 伺服器 (`llama-server`)，並利用 **TranslateGemma** 進行本地化，的命令行工具。

它會掃描 Steam 商店或本地模組資料夾，尋找 `Translate/EN/*.json` 檔案，估算翻譯數量（字數和行數），翻譯缺失或更新的字串，驗證變數和使用者介面標記，並將所有生成的翻譯本地複製，以便您可以輕鬆地製作獨立的翻譯模組，或在 Steam 更新後恢復檔案。

---

## 特色

- **支援 42.15+ 的 JSON 格式：** 能夠與 Project Zomboid 42.15+ 使用的現代 `.json` 翻譯格式相容 (舊版的 `.txt` 格式模組在掃描時會被安全跳過)。
- **豐富的終端介面：** 採用 `rich` 函式，呈現整潔的彩色表格、狀態標籤，以及顯示已過/剩餘時間的實時進度條。
- **多語言 CLI (`i18n`):** 預設語言為英文，在互動式啟動時，會提示使用者從 `cli_locales/*.json` 選擇介面語言。
- **3 種工作模式：**
  - **模式 1：** 翻譯一個特定的模組（或其 `Translate` / `EN` 資料夾）。
  - **模式 2：** 掃描整個工作目錄，檢查每個模組的翻譯狀態和字數，並根據數字 (`1,3,5`)、範圍 (`1-4`) 或 `all` 選擇模組。
  - **模式 3：管理已儲存的進度** — 偵測模組更新、翻譯新的/變更/失效的字串、從頭開始重新建立、從鏡像中恢復、乾淨地刪除產生的檔案，或執行「乾淨執行」的字串檢查報告。
- **占位符與標記驗證 (`token_rules.json`):** 透過可配置的正規表示法規則，提取模組的占位符 (`{name}`, `%1`) 以及 Project Zomboid 的 RichText 標記 (`<LINE>`, `<RGB:...>`, `<IMAGE:...>` 等)，並在翻譯後進行完全匹配驗證。若出現不符，則嘗試使用不同的種子 (`max_retries`)。如果所有嘗試都失敗，則保留原始的英文字串，將模組狀態標記為 `EN/<LANG>`，並將詳細資訊記錄到 `pz_translator_issues.log`。
- **偵測更新與進度追蹤：** 將原始英文字串的 SHA-1 哈希值儲存在 `pz_translator_state.json` 檔案中。當 Steam 工作室的模組更新時，僅會將新增、修改或失效的鍵值排入翻譯佇列。
- **本地鏡 (`pz_translator_mods/`):** 儲存所有翻譯檔案的副本，並保留相對目錄結構（這使得建立僅包含翻譯的獨立模組變得容易）。
- **安全且具容錯性：**
  - 先前已翻譯的作者作品（無論是原始版本或未在 `pz_translator_state.json` 檔案中追蹤的個別作者翻譯），永遠不會被 token 規則分析、修改或取代。
  - 支援 UTF-8 標頭、手動編輯的 mod JSON 檔案中的尾隨逗號，並保留 `$schema` 標頭和空字串。
  - 自動儲存進度，定期 (`save_every`)，以及按下 `Ctrl+C` 鍵。

---

## 需求

- **Python 3.9 或更高版本**
- **llama.cpp** (執行 `llama-server`) 運行一個 **TranslateGemma** 的 GGUF 模型，在設定的主機/埠上 (預設：`http://127.0.0.1:8734`)。
- Python 依賴：

```bash
pip install -r requirements.txt
```

---

## 設定檔 (`config.json`)

首次執行（或透過內建的 `config.json` 檔案），腳本將使用以下設定：

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

| 關鍵 | 說明 |
| --- | --- |
| `llamacpp_host` | 您的 `llama-server` 伺服器的位址 |
| `llamacpp_port` | 將您的 `llama-server` 部署到某個位置 |
| `mods_path` | 預設根目錄在模式 2 下進行掃描（例如，Steam 工作室 `108600` 檔案夾）。 |
| `default_source_lang` | 原始翻譯資料夾名稱 (預設：`EN`) |
| `default_target_lang` | 預設目標語言代碼 (例如：`RU`、`DE`、`CN`、`JP`、`PTBR`) |
| `ui_lang` | 預設介面語言代碼，來自 `cli_locales/` 目錄 |
| `mirror_dir` | 當地的資料夾，用於儲存生成的翻譯的完整路徑副本。 |
| `state_file` | JSON 檔案，用於儲存翻譯歷史記錄和原始字串的雜湊值 |
| `token_rules_file` | 包含正規表示法規則和重試設定的 JSON 檔案，用以驗證佔位符/標籤 |
| `save_every` | 將進度儲存至硬碟，並將每 N 個翻譯的關鍵詞複製一份。 |

### 驗證 Token (`token_rules.json`)

用於保護動態變數和 Project Zomboid 標記的正規表示法規則，已設定在 `token_rules.json` 檔案中：

| 關鍵 | 說明 |
| --- | --- |
| `max_retries` | 當關鍵詞不符時，嘗試翻譯的最大次數 |
| `retry_temperatures` | 適用於重試嘗試的溫度計畫（例如：`[0.2, 0.35, 0.5]`） |
| `issues_log` | 記錄檔，其中包含所有重試後，無法通過驗證的字串，以及它們的 `EN` 來源和失敗的嘗試。 |
| `check_report` | 模式 3 的「乾式測試」token 檢查報告的輸出檔案 |
| `rules` | 正規表示式規則物件的陣列（包含 `name`、`pattern`、`enabled`、`critical`、`description` 屬性） |

標記為 `"critical": true` 的規則，在翻譯過程中會觸發重新嘗試，並追蹤需要重新翻譯的關鍵字。對於非關鍵規則 (`"critical": false`)，僅會在預覽檢查報告中顯示為警告。

---

## 使用方式

### 互動模式

首先啟動 `llama-server`，然後執行：

```bash
python pz_translate.py
```

1. **選擇介面語言：** 請從 `cli_locales/` 裡的可用語言中選擇（預設：`en`）。
2. **選擇模式：**
   - `1` — 翻譯特定模組路徑。
   - `2` — 掃描 `mods_path` 中的所有模組，檢視包含字串/字元計數的表格，並輸入模組編號（例如：`1,3,5`、`1-4` 或 `all`）。
   - `3` — 管理已儲存的進度 (更新新的/變更的/失效的關鍵字，重新翻譯，從頭開始，從 `pz_translator_mods/` 恢復，刪除翻譯，或執行「乾淨執行」的關鍵字檢查報告)。
   - `4` — 更改介面語言
   - `0` — 退出。

### 命令行參數

您可以使用命令行參數（CLI 參數會覆蓋 `config.json`）來繞過互動式選單。

| 旗幟 | 說明 |
| --- | --- |
| `--config <path>` | 建立自訂的 `config.json` 檔案 |
| `--rules <path>` | 建立自訂的 `token_rules.json` 檔案的步驟 |
| `--mode {1,2,3}` | `1` = 單一模式，`2` = 掃描目錄，`3` = 管理已儲存的進度 |
| `--path <path>` | 前往模組資料夾 (模式 1) 或模組根資料夾 (模式 2) 的路徑 |
| `--lang <code>` | 目標語言為 PZ 檔案碼（例如：`RU`、`CN`、`PTBR`）或 ISO 碼（例如：`ru`、`zh`、`pt-BR`） |
| `--source-lang <code>` | 覆蓋原始語言資料夾 (預設：`EN`) |
| `--host <host>` | 覆蓋 `llamacpp_host` |
| `--port <port>` | 覆蓋 `llamacpp_port` |
| `--ui-lang <code>` | 介面語言代碼 (例如：`en`、`ru`) |
| `--force` | 覆蓋現有的翻譯 |
| `--check` | 執行所有已儲存翻譯的乾式驗證，並將結果寫入 `pz_translator_check_report.txt`。 |

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

# Run a dry-run token check on all saved translations without calling the LLM
python pz_translate.py --mode 3 --check
```

---

## 它是如何運作的

1. **模組搜尋：** 遞迴搜尋包含 `.json` 檔案的 `Translate/<SOURCE_LANG>` 類別的資料夾，並從 `mod.info` 和工作區資料夾結構 (`mods/<ModName>/<Version>`) 中提取模組名稱。
2. **差異與數量估算：** 比較 `EN/*.json` 中的鍵值與現有目標檔案 (`<TARGET_LANG>/*.json`)，以及儲存在 `pz_translator_state.json` 中的 SHA-1 哈希值，以及來自 `token_rules.json` 的關鍵規則。 缺少鍵值、英文來源文字已變更的鍵值，以及包含失效的佔位符/標籤的追蹤鍵值，都會排入翻譯佇列；現有的作者翻譯則保持不變。
3. **LLM 翻譯與驗證：** 將完整的原始字串送至 `http://<host>:<port>/completion`，並使用標準的「TranslateGemma」提示格式進行翻譯，然後檢查關鍵字與原始字串是否一致。若不一致，則嘗試使用不同的種子，最多 `max_retries` 次；若所有嘗試都失敗，則保留原始英文版本，將修改狀態標記為 `EN/<LANG>`，並將詳細資訊記錄至 `pz_translator_issues.log`。
4. **雙重輸出：** 每次執行 `save_every` 指令（以及在完成或按下 `Ctrl+C` 鍵時），都會將有效的 UTF-8 格式的 JSON 寫入：
   - 目標模組資料夾：`...\Translate\<LANG>\<file>.json`
   - 本地鏡像資料夾：`pz_translator_mods\<full_path_without_drive_letter>\Translate\<LANG>\<file>.json`

---

## 注意事項與限制

- **支援格式：** 僅支援 Project Zomboid **42.15+** 的 `.json` 格式的本地化檔案。舊的 `.txt` 格式的翻譯檔案將被忽略，因為 42.15+ 無法讀取它們。
- **多人模式 (`DoLuaChecksum`):** 因為 `Translate` 檔案位於 `media/lua/shared/` 內，直接將翻譯檔案加入 Steam Workshop 檔案夾，可能會在 `DoLuaChecksum=true` 上的多人伺服器上產生檢查碼不符的情況。對於公開的多人伺服器，您可以將 `pz_translator_mods/` 提供的複製檔案作為一個獨立的翻譯模組，或是單人模式/伺服器中使用 `DoLuaChecksum=false`。
