# プロジェクト・ゾンバイ モッド翻訳者

ローカルの `llama.cpp` サーバー (`llama-server`) を使用し、**TranslateGemma** を活用して、**Project Zomboid (Build 42.15+)** のモッドをローカライズするためのコマンドラインツール。

Steam Workshopまたはローカルのモッドフォルダをスキャンし、`Translate/EN/*.json` ファイルを検索します。翻訳のボリューム（行数と文字数）を推定し、欠けているまたは更新された文字列を翻訳し、変数の検証とUIのマークアップタグの検証を行い、生成されたすべての翻訳をローカルに保存することで、スタンドアロンの翻訳モッドを簡単にパッケージ化したり、Steamのアップデート後にファイルを復元したりできます。

---

## 特徴

- **42.15+ での JSON 形式のサポート:** Project Zomboid B42.15+ で使用されている最新の `.json` 形式に対応。 (古い `.txt` 形式のみのモッドは、スキャン時に安全にスキップされます。)
- **洗練されたターミナルインターフェース:** 色付きのテーブル、ステータスバッジ、および経過時間/残りの時間を表示するリアルタイムの進捗バーを、`rich`ライブラリを使用して作成。
- **多言語のコマンドラインインターフェース (`i18n`):** デフォルトでは英語を使用し、インタラクティブな起動時に、`cli_locales/*.json` からインターフェースの言語を選択するように促します。
- **3つの動作モード:**
  - **モード1：** 特定のモード（またはその `Translate` / `EN` フォルダ）を翻訳する。
  - **モード2:** ワークショップ全体をスキャンし、各モッドの翻訳状況と文字数を確認し、番号 (`1,3,5`)、範囲 (`1-4`)、または `all` でモッドを選択します。
  - **モード3：保存された進行状況の管理** – モードのアップデートを検出、新しい/変更された/破損したトークン文字列の翻訳、ゼロから再作成、ミラーからの復元、生成されたファイルのクリーンな削除、またはトークンのチェックレポートを実行する。
- **プレースホルダーとマークアップの検証 (`token_rules.json`):** 設定可能な正規表現ルールを使用して、モッドのプレースホルダー（`{name}`、`%1`）とProject ZomboidのRichTextタグ（`<LINE>`, `<RGB:...>`, `<IMAGE:...>`, など）を抽出し、翻訳後に正確な一致を確認します。不一致の場合、異なるシードで再試行します（`max_retries`）。すべての試行が失敗した場合、元の英語の文字列を保持し、モッドの状態を `EN/<LANG>` とマークし、詳細を `pz_translator_issues.log` に記録します。
- **更新の検出と進捗の追跡:** `pz_translator_state.json` に、ソースの英語文字列の各キーに対する SHA-1 ハッシュを保存します。 Steam Workshop でのアップデートが適用された場合、新たに追加された、変更された、またはトークンが破損したキーのみが翻訳キューに追加されます。
- **ローカルミラー (`pz_translator_mods/`):** 翻訳されたすべてのファイルのコピーを保存し、相対的なディレクトリ構造を保持します（これにより、翻訳専用のスタンドアロンのモジュールを簡単に作成できます）。
- **安全で、故障に強い:**
  - 既存の翻訳（未編集のモッドや、`pz_translator_state.json` に記録されていない個々の著者の翻訳）は、トークンルールによって分析、修正、または上書きされることはありません。
  - UTF-8 BOM、手動で編集された mod JSON 内の末尾のカンマ、および `$schema` と空の文字列を保持します。
  - 自動保存機能を定期的に実行します (`save_every`)、および `Ctrl+C` を押したときに自動保存します。

---

## 要件

- Python 3.9 以降
- **llama.cpp** (`llama-server`) が、設定されたホスト/ポートで **TranslateGemma** GGUF モデルを実行 (デフォルト: `http://127.0.0.1:8734`)。
- Python の依存関係:

```bash
pip install -r requirements.txt
```

---

## 設定 (`config.json`)

初回実行時（または、同梱されている `config.json` ファイルを使用した場合）、スクリプトは以下の設定を使用します。

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

| 重要なポイント | 説明 |
| --- | --- |
| `llamacpp_host` | 現在実行中の `llama-server` のホストアドレス |
| `llamacpp_port` | `llama-server` を実行しているポート |
| `mods_path` | デフォルトのルートディレクトリがモード2でスキャンされる (例: Steam Workshop の `108600` フォルダ)。 |
| `default_source_lang` | 翻訳元のフォルダ名 (デフォルト: `EN`) |
| `default_target_lang` | デフォルトのターゲット言語コード (例: `RU`, `DE`, `CN`, `JP`, `PTBR`) |
| `ui_lang` | `cli_locales/` ディレクトリからのデフォルトのインターフェース言語コード |
| `mirror_dir` | ローカルフォルダ。生成された翻訳の完全パスのコピーが保存される場所。 |
| `state_file` | 翻訳履歴とソース文字列のハッシュ値を保存するJSONファイル |
| `token_rules_file` | プレースホルダー/タグの検証に必要な正規表現ルールと再試行設定を含むJSONファイル |
| `save_every` | 進捗をディスクに保存し、N個の翻訳されたキーを複製する。 |

### トークン検証 (`token_rules.json`)

動的変数とProject Zomboidのマークアップタグを保護するための正規表現ルールは、`token_rules.json`ファイルに設定されています。

| 重要なポイント | 説明 |
| --- | --- |
| `max_retries` | 重要なトークンが一致しない場合に、異なるシードを使用して翻訳を試みる最大回数 |
| `retry_temperatures` | 温度設定を、再試行の各段階で適用 (例: `[0.2, 0.35, 0.5]`) |
| `issues_log` | 検証に失敗した文字列とその `EN` のソース、および失敗した試行回数が記録されたログファイル |
| `check_report` | モード3における、トークン検査レポートの出力ファイル |
| `rules` | 正規表現のルールオブジェクトの配列 (`name`, `pattern`, `enabled`, `critical`, `description`) |

`"critical": true` とマークされたルールは、翻訳中に再試行をトリガーし、更新時に再翻訳が必要なキーを追跡します。重要度の低いルール（`"critical": false`）は、テスト実行レポートでは警告としてのみ報告されます。

---

## 使用方法

### インタラクティブモード

まず `llama-server` を起動し、その後、以下のコマンドを実行してください。

```bash
python pz_translate.py
```

1. **インターフェースの言語を選択:** `cli_locales/` にある利用可能な言語から選択してください (デフォルト: `en`)。
2. **選択モード:**
   - `1` — 特定のモッドパスの翻訳
   - `2` — `mods_path` 内のすべてのモッドをスキャンし、文字列/文字の数を表示し、モッド番号を入力します（例：`1,3,5`、`1-4`、または `all`）。
   - `3` — 保存された進捗の管理（新しい/変更された/破損したトークンキーの更新、ゼロから再翻訳、`pz_translator_mods/` から復元、翻訳の削除、またはトークンチェックレポートの実行）
   - `4` — インターフェースの言語を変更する。
   - `0` — 終了

### コマンドライン引数

インタラクティブなメニューを、CLIフラグ（CLI引数）を使用して回避できます。（CLI引数は `config.json` を上書きします。）

| 旗 | 説明 |
| --- | --- |
| `--config <path>` | カスタム `config.json` ファイルを作成するための手順 |
| `--rules <path>` | カスタム `token_rules.json` ファイルを作成するための手順 |
| `--mode {1,2,3}` | `1` = 単一のモジュール、`2` = ディレクトリのスキャン、`3` = 保存された進行状況の管理 |
| `--path <path>` | モッドフォルダへのパス (モード1) または、モッドのルートフォルダへのパス (モード2) |
| `--lang <code>` | ターゲット言語を、PZフォルダコード（`RU`、`CN`、`PTBR`）またはISOコード（`ru`、`zh`、`pt-BR`）として指定 |
| `--source-lang <code>` | ソース言語のフォルダを上書き (デフォルト: `EN`) |
| `--host <host>` | `llamacpp_host` の設定を上書きする |
| `--port <port>` | `llamacpp_port` の設定を上書きする |
| `--ui-lang <code>` | インターフェースの言語コード (例: `en`, `ru`) |
| `--force` | 既存の翻訳を上書きする |
| `--check` | すべての保存された翻訳に対して、トークンチェックを実行し、結果を `pz_translator_check_report.txt` に書き込む。 |

#### 例

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

## 仕組み

1. **MOD の発見:** `Translate/<SOURCE_LANG>` ディレクトリ内の `.json` ファイルを再帰的に検索し、`mod.info` ファイルとワークショップフォルダ構造（`mods/<ModName>/<Version>`）から MOD の名前を抽出します。
2. **差分とボリュームの推定:** `EN/*.json` 内のキーを、既存のターゲットファイル (`<TARGET_LANG>/*.json`)、`pz_translator_state.json` に保存されている SHA-1 ハッシュ、および `token_rules.json` からの重要なルールと比較します。 欠落しているキー、英語のソーステキストが変更されたキー、および破損したプレースホルダー/タグを持つ追跡されているキーは、翻訳キューに追加されます。 既存の著者による翻訳は、そのまま残ります。
3. **LLMによる翻訳と検証:** 元の文字列全体を、`http://<host>:<port>/completion` に、標準的なTranslateGemmaプロンプト形式で送信し、その後、重要なトークンを元の文字列と比較します。 不一致がある場合、`max_retries` まで異なるシードで再試行します。 すべての試行が失敗した場合、英語のテキストを保持し、修正ステータスを`EN/<LANG>`としてマークし、詳細を`pz_translator_issues.log`に記録します。
4. **二重出力:** 各 `save_every` キー (および完了時、または `Ctrl+C` の場合)、有効な UTF-8 JSON を以下に書き出します:
   - ターゲットのモッドフォルダ: `...\Translate\<LANG>\<file>.json`
   - ローカルのミラーフォルダ: `pz_translator_mods\<full_path_without_drive_letter>\Translate\<LANG>\<file>.json`

---

## 注記と制限

- **対応形式:** Project Zomboid **バージョン 42.15+** の `.json` 形式のローカライズファイルのみが処理されます。古い `.txt` 形式の翻訳ファイルは、バージョン 42.15+ では読み込まれないため、無視されます。
- **マルチプレイヤー（`DoLuaChecksum`）：** `Translate` フォルダが `media/lua/shared/` 内に存在するため、Steam Workshop のフォルダに直接翻訳ファイルを追加すると、`DoLuaChecksum=true` のマルチプレイヤーサーバーではチェックサムの不一致が発生する可能性があります。 公開のマルチプレイヤーサーバーの場合、`pz_translator_mods/` からのミラーされたファイルを個別の翻訳専用のモッドとしてパッケージ化するか、`DoLuaChecksum=false` でシングルプレイヤー/サーバーでプレイしてください。
