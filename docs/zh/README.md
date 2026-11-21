# 《僵尸生存》模组翻译

一个命令行工具，用于本地化 **Project Zomboid (42.15+)** 模组，该工具使用本地的 `llama.cpp` 服务器 (`llama-server`)，并利用 **TranslateGemma** 技术。

它会扫描 Steam 商店或本地模组文件夹，查找 `Translate/EN/*.json` 类型的文件，估算翻译量（行数和字符数），翻译缺失或更新的字符串，验证变量和 UI 标记，并本地复制所有生成的翻译，以便您可以轻松地创建独立的翻译模组，或在 Steam 更新后恢复文件。

---

## 特点

- **支持 42.15+ 的 JSON 格式：** 兼容 Project Zomboid B42.15+ 中使用的现代 `.json` 翻译格式（在扫描过程中，仅支持 `.txt` 格式的旧模组会被安全跳过）。
- **丰富且美观的终端界面：** 采用 `rich` 库，呈现清晰的彩色表格、状态徽章，以及实时进度条，显示已用时间和剩余时间。
- **多语言命令行界面 (`i18n`):** 默认语言为英语，并在交互式启动时，会提示用户从 `cli_locales/*.json` 文件中选择界面语言。
- **三种工作模式：**
  - **模式 1：** 翻译一个特定的模块（或其 `Translate` / `EN` 文件夹）。
  - **模式 2：** 扫描整个工作目录，检查每个模组的翻译状态和字符数量，然后选择模组，可以通过编号 (`1,3,5`)、范围 (`1-4`) 或 `all` 进行选择。
  - **模式 3：管理已保存的进度** — 检测模块更新，翻译新的/修改的/损坏的字符串，从头开始重新创建，从镜像恢复，清理生成的临时文件，或运行一个“模拟运行”的令牌检查报告。
- **占位符和标记验证 (`token_rules.json`):** 通过可配置的正则表达式规则，提取模组的占位符（如 `{name}`、`%1`）和 Project Zomboid 的 RichText 标签（如 `<LINE>`, `<RGB:...>`, `<IMAGE:...>`, 等），并在翻译后进行精确匹配。如果匹配失败，则尝试使用不同的种子（`max_retries`）。如果所有尝试都失败，则保留原始的英文字符串，将模组状态标记为 `EN/<LANG>`，并将详细信息记录到 `pz_translator_issues.log` 文件中。
- **更新检测与进度跟踪：** 存储源语言英文字符串的 SHA-1 哈希值，保存在 `pz_translator_state.json` 文件中。当 Steam 商店的模组更新时，只有新增、修改或出现问题的键才会进入翻译队列。
- **本地镜像 (`pz_translator_mods/`):** 能够保存所有翻译文件的副本，并保留相对的目录结构，从而方便创建仅包含翻译内容的独立模组。
- **安全可靠，具备容错能力：**
  - 之前已存在的作者翻译（包括未经修改的模组以及未在 `pz_translator_state.json` 文件中跟踪的单个作者翻译）永远不会被 token 规则分析、修改或覆盖。
  - 支持 UTF-8 编码头，手动编辑的 mod JSON 文件中的尾随逗号，并保留 `$schema` 和空字符串。
  - 自动保存进度，周期性地（`save_every`）和在按下 `Ctrl+C` 键时保存。

---

## 要求

- **Python 3.9 及更高版本**
- **llama.cpp** (运行 `llama-server`)，使用配置的宿主机/端口（默认：`http://127.0.0.1:8734`），运行 **TranslateGemma** GGUF 模型。
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
    "token_rules_file": "token_rules.json",
    "save_every": 20
}
```

| 关键 | 描述 |
| --- | --- |
| `llamacpp_host` | 您运行的 `llama-server` 的地址 |
| `llamacpp_port` | 启动您的 `llama-server` 进程 |
| `mods_path` | 默认根目录在模式 2 下进行扫描（例如，Steam Workshop `108600` 文件夹）。 |
| `default_source_lang` | 源文件翻译文件夹名称（默认：`EN`） |
| `default_target_lang` | 默认的目标语言代码（例如：`RU`、`DE`、`CN`、`JP`、`PTBR`） |
| `ui_lang` | 默认的界面语言代码，位于 `cli_locales/` 目录中。 |
| `mirror_dir` | 本地文件夹，用于存储生成的翻译的完整路径副本。 |
| `state_file` | JSON 文件，用于存储翻译历史记录和源字符串的哈希值 |
| `token_rules_file` | 包含正则表达式规则和重试设置的 JSON 文件，用于验证占位符/标签 |
| `save_every` | 将进度保存到磁盘，并每 N 个翻译后的关键词进行镜像。 |

### 令牌验证 (`token_rules.json`)

用于保护动态变量和 Project Zomboid 标记的正则表达式规则，已配置在 `token_rules.json` 文件中：

| 关键 | 描述 |
| --- | --- |
| `max_retries` | 当关键的词语不匹配时，尝试不同种子进行翻译的最大次数 |
| `retry_temperatures` | 温度计划应用于重试尝试（例如：`[0.2, 0.35, 0.5]`）。 |
| `issues_log` | 日志文件，记录所有重试后，未能通过验证的字符串，以及它们的 `EN` 来源和失败的尝试次数。 |
| `check_report` | 用于模式 3 的“模拟测试结果报告”的输出文件 |
| `rules` | 正则表达式规则对象的数组，包含以下属性：`name`（名称）、`pattern`（模式）、`enabled`（启用状态）、`critical`（是否关键）、`description`（描述）。 |

带有 `"critical": true` 标记的规则会在翻译过程中触发重试，并在更新时记录需要重新翻译的键。 带有 `"critical": false` 标记的规则，仅会在测试报告中显示为警告。

---

## 使用方法

### 互动模式

首先启动 `llama-server`，然后运行：

```bash
python pz_translate.py
```

1. **选择界面语言：** 从 `cli_locales/` 目录中的可用语言中选择（默认：`en`）。
2. **选择模式：**
   - `1` — 翻译特定的模组路径。
   - `2` — 扫描 `mods_path` 中的所有模组，查看字符串/字符计数表，并输入模组编号（例如：`1,3,5`、`1-4` 或 `all`）。
   - `3` — 管理已保存的进度（更新新的/已更改/损坏的令牌键，从头开始重新翻译，从 `pz_translator_mods/` 恢复，删除翻译，或运行一个“模拟”的令牌检查报告）。
   - `4` — 更改界面语言。
   - `0` — 退出。

### 命令行参数

您可以通过命令行参数（CLI 参数会覆盖 `config.json` 文件）来绕过交互式菜单。

| 旗帜 | 描述 |
| --- | --- |
| `--config <path>` | 创建自定义 `config.json` 文件的步骤 |
| `--rules <path>` | 创建自定义 `token_rules.json` 文件的步骤 |
| `--mode {1,2,3}` | `1` = 单个模式，`2` = 扫描目录，`3` = 管理已保存的进度 |
| `--path <path>` | 进入模组文件夹（模式 1）或模组根文件夹（模式 2）的路径 |
| `--lang <code>` | 目标语言：以 PZ 文件夹代码（如 `RU`、`CN`、`PTBR`）或 ISO 代码（如 `ru`、`zh`、`pt-BR`）的形式指定。 |
| `--source-lang <code>` | 覆盖源语言文件夹（默认：`EN`） |
| `--host <host>` | 覆盖 `llamacpp_host` |
| `--port <port>` | 覆盖 `llamacpp_port` |
| `--ui-lang <code>` | 界面语言代码 (例如：`en`，`ru`) |
| `--force` | 覆盖已有的翻译 |
| `--check` | 对所有已保存的翻译进行“模拟”的令牌检查，并将结果写入 `pz_translator_check_report.txt` 文件。 |

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

# Run a dry-run token check on all saved translations without calling the LLM
python pz_translate.py --mode 3 --check
```

---

## 工作原理

1. **模包发现：** 递归搜索 `Translate/<SOURCE_LANG>` 目录，查找包含 `.json` 文件的文件夹，并从 `mod.info` 和 Workshop 文件夹结构（例如：`mods/<ModName>/<Version>`）中提取模包名称。
2. **差异和体积估算：** 比较 `EN/*.json` 中的键与现有的目标文件 (`<TARGET_LANG>/*.json`)，以及存储在 `pz_translator_state.json` 中的 SHA-1 哈希值，以及 `token_rules.json` 中的关键规则。 缺少键、英语原文已更改的键，以及包含无效占位符/标签的已跟踪键，将被排队进行翻译；现有的作者翻译将保持不变。
3. **LLM 翻译与验证：** 将完整的原始字符串发送到 `http://<host>:<port>/completion`，使用标准的 TranslateGemma 提示格式。然后，检查关键的词语与原始字符串是否匹配。如果存在不匹配，则尝试使用不同的随机种子，最多尝试 `max_retries` 次。如果所有尝试都失败，则保留英文文本，将修改状态标记为 `EN/<LANG>`，并将详细信息记录到 `pz_translator_issues.log` 文件中。
4. **双重输出：** 每次执行 `save_every` 指令（以及在完成或按下 `Ctrl+C` 键时），都会将有效的 UTF-8 JSON 数据写入：
   - 目标模块文件夹：`...\Translate\<LANG>\<file>.json`
   - 本地镜像文件夹：`pz_translator_mods\<full_path_without_drive_letter>\Translate\<LANG>\<file>.json`

---

## 注意事项及局限性

- **支持的文件格式：** 仅支持 Project Zomboid **42.15+** 版本的 `.json` 格式的本地化文件。 较早版本的 `.txt` 格式的翻译文件将被忽略，因为 42.15+ 版本不再加载它们。
- **多人游戏 (`DoLuaChecksum`):** 由于 `Translate` 文件夹位于 `media/lua/shared/` 内部，直接将翻译文件添加到 Steam Workshop 文件夹中，可能会在 `DoLuaChecksum=true` 类型的多人服务器上导致校验和不匹配。对于公开的多人游戏服务器，要么将 `pz_translator_mods/` 提供的镜像文件打包成一个单独的仅用于翻译的模组，要么在单人模式或 `DoLuaChecksum=false` 类型的服务器上进行游戏。
