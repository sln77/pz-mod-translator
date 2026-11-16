# Project Zomboid 模组翻译

<p align="center">
  <a href="#features">功能</a> ·
  <a href="#requirements">需求</a> ·
  <a href="#configuration-configjson">配置</a> ·
  <a href="#usage">使用方法</a> ·
  <a href="#how-it-works">工作原理</a>
</p>

<p align="center">
  <b>英语</b> ·
  <a href="docs/ru/README.md">俄语</a> ·
  <a href="docs/zh/README.md">简体中文</a> ·
  <a href="docs/zh-TW/README.md">繁體中文</a> ·
  <a href="docs/ja/README.md">日语</a> ·
  <a href="docs/ko/README.md">韩语</a> ·
  <a href="docs/de/README.md">德语</a> ·
  <a href="docs/fr/README.md">法语</a> ·
  <a href="docs/es/README.md">西班牙语</a> ·
  <a href="docs/it/README.md">意大利语</a> ·
  <a href="docs/pt-BR/README.md">葡萄牙语</a> ·
  <a href="docs/tr/README.md"> Türkçe </a> ·
  <a href="docs/uk/README.md">乌克兰语</a> ·
  <a href="docs/pl/README.md">波兰语</a>
</p>

一个用于本地化 **Project Zomboid (Build 42.15+)** 模组，使用本地 `llama.cpp` 服务器 (`llama-server`)，并由 **TranslateGemma** 驱动的命令行工具。

它会扫描 Steam Workshop 或本地模组文件夹，查找 `Translate/EN/*.json` 文件，估算翻译量（行数和字符数），翻译缺失或更新的字符串，并将所有生成的翻译本地镜像，以便您可以轻松地打包独立的翻译模组，或在 Steam 更新后恢复文件。

---

## 功能

- **支持 42.15+ JSON 格式：** 与 Project Zomboid B42.15+ 中使用的现代 `.json` 翻译格式兼容（旧的 `.txt` 格式的模组在扫描时会被安全跳过）。
- **丰富的终端界面：** 清晰的彩色表格、状态徽章，以及带有已用/剩余时间的实时进度条，都使用 `rich` 实现。
- **多语言命令行界面 (`i18n`):** 默认使用英语，并在交互式启动时，从 `cli_locales/*.json` 中提示用户选择界面语言。
- **3 运行模式：**
  - **模式 1：** 翻译一个指定的模（或其 `Translate` / `EN` 文件夹）。
  - **模式 2：** 扫描整个工作目录，检查每个模组的翻译状态和字符数量，并选择模组（例如：`1,3,5`、范围：`1-4` 或 `全部`）。
  - **模式 3：管理已保存的进度 — 检测模块更新，仅翻译新的/已更改的字符串，从头开始重置，从镜像恢复，或干净地删除生成的。**
- **更新检测与进度跟踪：** 将源语言英语字符串的每个键的 SHA-1 哈希值存储在 `pz_translator_state.json` 文件中。如果 Steam 工作站中的模组更新，只有新添加或修改的英语键才会排队进行翻译。
- **本地镜像 (`pz_translator_mods/`):** 存储所有翻译文件的副本，同时保留相对目录结构（这使得创建仅包含翻译的独立模组变得容易）。
- **安全且具有容错性：**
  - 现有的作者翻译，如果其 `pending` 键值为 `0`，则不会被修改、覆盖或跟踪。
  - 处理 UTF-8 BOM、手动编辑的 mod JSON 中的尾随逗号，并保留 `$schema` 和空字符串。
  - 自动保存进度，周期性地 (`save_every`)，以及在按下 `Ctrl+C` 键时。

---

## 要求

- **Python 3.9+**
- **llama.cpp** (`llama-server`) 运行一个 **TranslateGemma** GGUF 模型，在配置的 host/port 上 (默认：`http://127.0.0.1:8734`)。
- Python 依赖：

```bash
pip install -r requirements.txt
```

---

## 配置 (`config.json`)

首次运行（或通过包含的 `config.json` 文件），脚本将使用以下设置：

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

| 关键 | 描述 |
| --- | --- |
| `llamacpp_host` | 运行的 `llama-server` 的主机地址 |
| `llamacpp_port` | 启动 `llama-server` 的端口 |
| `mods_path` | 默认根目录，在模式 2 下进行扫描（例如，Steam Workshop `108600` 文件夹） |
| `default_source_lang` | 源翻译文件夹名称 (默认: `EN`) |
| `default_target_lang` | 默认目标语言代码 (例如：`RU`, `DE`, `CN`, `JP`, `PTBR`) |
| `ui_lang` | 默认的界面语言代码，来自 `cli_locales/` |
| `mirror_dir` | 本地文件夹，用于存储生成的翻译的完整路径副本 |
| `state_file` | JSON 文件，用于存储翻译历史记录和源字符串的哈希值 |
| `save_every` | 将进度保存到磁盘，并每 N 个翻译后的键进行镜像。 |

---

## 使用方法

### 交互模式

首先启动 `llama-server`，然后运行：

```bash
python pz_translate.py
```

1. **选择界面语言：** 从 `cli_locales/` 目录中的可用语言中选择（默认：`en`）。
2. **选择模式：**
   - `1` — 翻译特定的模组路径。
   - `2` — 扫描 `mods_path` 目录下的所有模组，查看包含字符串/字符数量的表格，并输入模组编号（例如：`1,3,5`、`1-4` 或 `all`）。
   - `3` — 管理已保存的进度 (更新已更改/新建的键，从头开始重新翻译，从 `pz_translator_mods/` 恢复，或删除翻译)。
   - `4` — 更改界面语言。
   - `0` — 退出。

### 命令行参数

您可以使用命令行标志（命令行参数覆盖 `config.json`）来绕过交互式菜单。

| 标志 | 描述 |
| --- | --- |
| `--config <路径>` | 指向自定义 `config.json` 文件的路径 |
| `--mode {1, 2, 3}` | `1` = 单个模块，`2` = 扫描目录，`3` = 管理已保存的进度 |
| `--path <path>` | 指向模组文件夹的路径 (模式 1) 或模组根文件夹的路径 (模式 2) |
| `--lang <code>` | 目标语言作为 PZ 文件夹代码（例如：`RU`、`CN`、`PTBR`）或 ISO 代码（例如：`ru`、`zh`、`pt-BR`） |
| `--source-lang <code>` | 覆盖源语言文件夹 (默认: `EN`) |
| `--host <host>` | 覆盖 `llamacpp_host` |
| `--port <端口>` | 覆盖 `llamacpp_port` |
| `--ui-lang <code>` | 界面语言代码（例如：`en`、`ru`） |
| `--force` | 覆盖已有的翻译 |

#### 示例

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

## 工作原理

1. **模发现：** 递归搜索包含 `.json` 文件的 `Translate/<SOURCE_LANG>` 目录，并从 `mod.info` 和 Workshop 文件夹结构（`mods/<ModName>/<Version>`）中提取模名。
2. **差异和体积估算：** 将 `EN/*.json` 中的键与现有的目标文件 (`<TARGET_LANG>/*.json`) 以及 `pz_translator_state.json` 中存储的 SHA-1 哈希进行比较。 仅对缺失的键或自上次翻译以来，其英语源文本发生变化的键进行排队。
3. **LLM 翻译：** 使用 `TranslateGemma` 聊天轮格式，将每个字符串发送到 `http://<host>:<port>/completion`。
4. **双输出：** 每次 `save_every` 键触发（以及在完成或按下 `Ctrl+C` 时），都会将有效的 UTF-8 JSON 写入：
   - 目标模块文件夹: `...\Translate\<LANG>\<file>.json`
   - 本地镜像文件夹：`pz_translator_mods\<完整路径，不含驱动器盘符>\Translate\<LANG>\<file>.json`

---

## 注意事项及局限性

- **支持的格式：** 仅处理 Project Zomboid **42.15+** 的 `.json` 语言文件。 旧的 `.txt` 翻译文件将被忽略，因为 B42.15+ 不再加载它们。
- **多人游戏 (`DoLuaChecksum`):** 因为 `Translate` 文件夹位于 `media/lua/shared/` 目录下，直接将翻译文件添加到 Steam Workshop 文件夹中，可能会在启用了 `DoLuaChecksum=true` 的多人服务器上触发校验和不匹配。 对于公共多人服务器，要么将 `pz_translator_mods/` 目录中的镜像文件打包成一个单独的仅用于翻译的模组，要么在单人模式/服务器上使用 `DoLuaChecksum=false`。
```
