# プロジェクト・ゾンバイ・モッド翻訳者

<p align="center">
  <a href="#features">機能</a> ·
  <a href="#requirements">要件</a> ·
  <a href="#configuration-configjson">設定</a> ·
  <a href="#usage">使用方法</a> ·
  <a href="#how-it-works">仕組み</a>
</p>

<p align="center">
  **英語** ·
  <a href="docs/ru/README.md">ロシア語</a> ·
  <a href="docs/zh/README.md">简体中文</a> ·
  <a href="docs/zh-TW/README.md">繁體中文</a> ·
  <a href="docs/ja/README.md">日本語</a> ·
  <a href="docs/ko/README.md">한국어</a> ·
  <a href="docs/de/README.md">ドイツ語</a> ·
  <a href="docs/fr/README.md">フランス語</a> ·
  <a href="docs/es/README.md">スペイン語</a> ·
  <a href="docs/it/README.md">イタリア語</a> ·
  <a href="docs/pt-BR/README.md">ポルトガル語</a> ·
  <a href="docs/tr/README.md">トルコ語</a> ·
  <a href="docs/uk/README.md">Украинский</a> ·
  <a href="docs/pl/README.md">ポーランド語</a>
</p>

ローカルの `llama.cpp` サーバー (`llama-server`) を使用し、**TranslateGemma** を活用して、ローカルの **Project Zomboid (Build 42.15+)** のモッドをローカライズするための CLI ツール。

Steam Workshop またはローカルのモッドフォルダをスキャンし、`Translate/EN/*.json` ファイルを検索します。翻訳のボリューム（行数と文字数）を推定し、欠落しているまたは更新された文字列を翻訳し、生成されたすべての翻訳をローカルにミラーリングすることで、スタンドアロンの翻訳モッドを簡単にパッケージ化したり、Steamのアップデート後にファイルを復元したりできます。

---

## 機能

- **Build 42.15+ JSON サポート:** Project Zomboid B42.15+ で使用されている最新の `.json` 形式の翻訳に対応。 (旧 `.txt` 形式のみのモッドは、スキャン時に安全にスキップされます。)
- **豊富なターミナルインターフェース:** きれいな色付きのテーブル、ステータスバッジ、および経過時間/残りの時間を表示するライブプログレスバーを、`rich`ライブラリを使用。
- **多言語CLI (`i18n`):** デフォルトは英語で、インタラクティブな起動時に `cli_locales/*.json` からインターフェースの言語を選択するようにプロンプトを表示します。
- **3 動作モード:**
  - **モード 1:** 特定のモジュール（またはその `Translate` / `EN` フォルダ）を翻訳する。
  - **モード 2:** ワークショップ全体をスキャンし、各モッドの翻訳ステータスと文字数を確認し、番号 (`1,3,5`)、範囲 (`1-4`)、または `すべて` でモッドを選択します。
  - **モード 3:** 保存された進行状況の管理 — モードのアップデートを検出、新しい/変更された文字列のみを翻訳、ゼロから再作成、ミラーからの復元、または生成されたファイルをクリーンに削除。
- **更新の検出と進捗の追跡:** `pz_translator_state.json` に、ソースの英語文字列の各キーの SHA-1 ハッシュを保存します。 Steam Workshop でのモッドの更新時には、新たに追加または変更された英語のキーのみが翻訳キューに追加されます。
- **ローカルミラー (`pz_translator_mods/`):** 翻訳されたすべてのファイルのコピーを保存し、相対的なディレクトリ構造を保持します（これにより、スタンドアロンの翻訳専用のモッドを簡単に作成できます）。
- **安全で、故障に強い:**
  - 既存の著者の翻訳で、未処理のキーが「0」の場合、決して変更、上書き、または追跡されません。
  - UTF-8 BOM、手動で編集された mod JSON 内の末尾のカンマ、および `$schema` と空の文字列を処理します。
  - 定期的に自動保存 (`save_every`) および `Ctrl+C` で保存します。

---

## 要件

- **Python 3.9 以降**
- **llama.cpp** (`llama-server`) が、設定されたホスト/ポートで **TranslateGemma** GGUF モデルを実行します (デフォルト: `http://127.0.0.1:8734`)。
- Python の依存関係:

```bash
pip install -r requirements.txt
```

---

## 設定 (`config.json`)

初回実行時（または、同梱されている `config.json` を使用した場合）、スクリプトは以下の設定を使用します：

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

| 主要 | 説明 |
| --- | --- |
| `llamacpp_host` | 実行中の `llama-server` のホストアドレス |
| `llamacpp_port` | `llama-server` の実行ポート |
| `mods_path` | デフォルトのルートディレクトリがモード 2 (例: Steam Workshop の `108600` フォルダ) でスキャンされます。 |
| `default_source_lang` | ソース翻訳フォルダの名前 (デフォルト: `EN`) |
| `default_target_lang` | デフォルトのターゲット言語コード (例: `RU`, `DE`, `CN`, `JP`, `PTBR`) |
| `ui_lang` | デフォルトのインターフェース言語コードは、`cli_locales/` から取得 |
| `mirror_dir` | ローカルフォルダ: 生成された翻訳のフルパスのコピーが保存されている場所 |
| `state_file` | JSONファイルで、翻訳履歴とソース文字列のハッシュを保存 |
| `save_every` | 進捗をディスクに保存し、N個の翻訳されたキーをミラーリングする |

---

## 使用方法

### インタラクティブモード

まず `llama-server` を起動し、その後、以下のコマンドを実行してください:

```bash
python pz_translate.py
```

1. **インターフェース言語の選択:** `cli_locales/` に存在する言語から選択してください (デフォルト: `en`)。
2. **選択モード:**
   - `1` — 特定のモッドのパスを翻訳する。
   - `2` — `mods_path` 内のすべてのモッドをスキャンし、文字列/文字のカウントを含むテーブルを表示し、モッド番号を入力します（例：`1,3,5`、`1-4`、または `all`）。
   - `3` — 保存された進捗の管理（変更/新規キーの更新、ゼロから再翻訳、`pz_translator_mods/` から復元、または翻訳の削除）
   - `4` — インターフェースの言語を変更する。
   - `0` — 終了

### コマンドライン引数

インタラクティブなメニューを、CLIフラグ（CLI引数が `config.json` を上書き）を使用して回避できます。

| 旗 | 説明 |
| --- | --- |
| `--config <パス>` | カスタム `config.json` ファイルへのパス |
| `--mode {1, 2, 3}` | `1` = 単一のモジュール、`2` = ディレクトリのスキャン、`3` = 保存された進捗の管理 |
| `--path <path>` | モッドフォルダへのパス (モード 1) または、モッドのルートフォルダへのパス (モード 2) |
| `--lang <code>` | ターゲット言語を PZ フォルダコード (`RU`, `CN`, `PTBR`) または ISO コード (`ru`, `zh`, `pt-BR`) として指定 |
| `--source-lang <code>` | ソース言語のフォルダを上書き (デフォルト: `EN`) |
| `--host <ホスト>` | `llamacpp_host` の上書き |
| `--port <ポート番号>` | `llamacpp_port` の上書き |
| `--ui-lang <code>` | インターフェース言語コード (例: `en`, `ru`) |
| `--force` | 既存の翻訳を上書きする |

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
```

---

## 仕組み

1. **モッドの発見:** `Translate/<SOURCE_LANG>` ディレクトリ内の `.json` ファイルを再帰的に検索し、`mod.info` とワークショップフォルダ構造（`mods/<ModName>/<Version>`）からモッド名を抽出します。
2. **差分とボリュームの推定:** `EN/*.json` 内のキーを、既存のターゲットファイル (`<TARGET_LANG>/*.json`) と `pz_translator_state.json` に保存されている SHA-1 ハッシュと比較します。 欠けているキーまたは、最後に翻訳されてから英語のソーステキストが変更されたキーのみがキューに入れられます。
3. **LLMによる翻訳:** `TranslateGemma` のチャットターン形式を使用して、各文字列を `http://<host>:<port>/completion` に送信します。
4. **デュアル出力:** `save_every` キー (および完了時または `Ctrl+C` 時) では、有効な UTF-8 JSON を以下に書き込みます:
   - ターゲットのモッドフォルダ: `...\Translate\<LANG>\<file>.json`
   - ローカルミラーフォルダ: `pz_translator_mods\<ドライブ文字なしの完全パス>\Translate\<LANG>\<ファイル>.json`

---

## 注釈と制限

- **対応形式:** Project Zomboid **Build 42.15+** の `.json` 形式のローカライズファイルのみが処理されます。古い `.txt` 形式の翻訳ファイルは、B42.15+ で読み込まれていないため、無視されます。
- **マルチプレイヤー（`DoLuaChecksum`）:** `Translate` フォルダが `media/lua/shared/` 内に存在するため、Steam Workshop のフォルダに直接翻訳ファイルを追加すると、`DoLuaChecksum=true` のマルチプレイヤーサーバーではチェックサムの不一致が発生する可能性があります。 公開のマルチプレイヤーサーバーの場合、`pz_translator_mods/` からのミラーされたファイルを個別の翻訳専用のモジュールとしてパッケージ化するか、`DoLuaChecksum=false` でシングルプレイヤー/サーバーでプレイしてください。
```
