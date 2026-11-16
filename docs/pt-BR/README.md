# Tradutor de Mod para Project Zomboid

<p align="center">
  <a href="#features">Recursos</a> ·
  <a href="#requirements">Requisitos</a> ·
  <a href="#configuration-configjson">Configuração</a> ·
  <a href="#usage">Utilização</a> ·
  <a href="#como-funciona">Como Funciona</a>
</p>

<p align="center">
  <b>Inglês</b> ·
  <a href="docs/ru/README.md">Russo</a> ·
  <a href="docs/zh/README.md">简体中文</a> ·
  <a href="docs/zh-TW/README.md">中文 (Tradicional)</a> ·
  <a href="docs/ja/README.md">日本語</a> ·
  <a href="docs/ko/README.md">한국어</a> ·
  <a href="docs/de/README.md">Alemão</a> ·
  <a href="docs/fr/README.md">Francês</a> ·
  <a href="docs/es/README.md">Espanhol</a> ·
  <a href="docs/it/README.md">Italiano</a> ·
  <a href="docs/pt-BR/README.md">Português</a> ·
  <a href="docs/tr/README.md">Turco</a> ·
  <a href="docs/uk/README.md">Украинский</a> ·
  <a href="docs/pl/README.md">Polski</a>
</p>

Uma ferramenta de linha de comando para localizar os mods de **Project Zomboid (Build 42.15+)** usando um servidor `llama.cpp` local (`llama-server`), alimentado por **TranslateGemma**.

Ele escaneia o Steam Workshop ou as pastas de mods locais em busca de arquivos `Translate/EN/*.json`, estima o volume de tradução (número de linhas e caracteres), traduz strings ausentes ou atualizadas e cria um espelho de todas as traduções geradas localmente, para que você possa facilmente empacotar mods de tradução independentes ou restaurar arquivos após as atualizações do Steam.

---

## Recursos

- **Suporte JSON para a versão 42.15+:** Funciona com o formato de tradução `.json` moderno usado no Project Zomboid B42.15+ (mods antigos que usam apenas `.txt` são ignorados com segurança durante as verificações).
- **Interface de Terminal Rica:** Tabelas coloridas limpas, indicadores de status e barras de progresso em tempo real com tempo decorrido/restante, utilizando a biblioteca `rich`.
- **CLI Multilíngue (`i18n`):** Por padrão, usa o inglês e solicita a seleção do idioma da interface a partir de `cli_locales/*.json` no início interativo.
- **3 Modos de Operação:**
  - **Modo 1:** Traduzir um único mod especificado (ou sua pasta `Translate` / `EN`).
  - **Modo 2:** Digitalize todo o diretório do seu Workshop, verifique o status das traduções e o volume de caracteres por mod, e selecione os mods por números (`1,3,5`), intervalos (`1-4`) ou `todos`.
  - **Modo 3:** Gerenciar o progresso salvo — detectar atualizações de mods, traduzir apenas novas/modificadas strings, sobrescrever do zero, restaurar a partir de um espelho, ou excluir de forma limpa os arquivos gerados.
- **Detecção de Atualizações e Rastreamento de Progresso:** Armazena os hashes SHA-1 por chave das strings em inglês originais no arquivo `pz_translator_state.json`. Se uma atualização for instalada na Steam Workshop, apenas as chaves em inglês recém-adicionadas ou modificadas são colocadas em fila para tradução.
- **Espelho Local (`pz_translator_mods/`):** Salva uma cópia de todos os arquivos traduzidos, preservando a estrutura de diretórios relativa (tornando fácil a criação de mods independentes, dedicados apenas à tradução).
- **Seguro e Tolerante a Falhas:**
  - Traduções de autores existentes com `0` chaves pendentes nunca são modificadas, substituídas ou rastreadas.
  - Lida com o BOM UTF-8, vírgulas no final de arquivos JSON de mods editados manualmente, e preserva o `$schema` e strings vazias.
  - Salva o progresso automaticamente periodicamente (`save_every`) e ao pressionar `Ctrl+C`.

---

## Requisitos

- **Python 3.9+**
- **llama.cpp** (`llama-server`) executando um modelo GGUF **TranslateGemma** no host/porta configurado (padrão: `http://127.0.0.1:8734`).
- Dependências do Python:

```bash
pip install -r requirements.txt
```

---

## Configuração (`config.json`)

Na primeira execução (ou através do arquivo `config.json` incluído), o script utiliza as seguintes configurações:

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

| Chave | Descrição |
| --- | --- |
| `llamacpp_host` | Endereço do host do seu `llama-server` em execução |
| `llamacpp_port` | Porta do seu servidor `llama-server` em execução |
| `mods_path` | Diretório raiz padrão escaneado no Modo 2 (por exemplo, a pasta `108600` do Steam Workshop) |
| `default_source_lang` | Nome da pasta de tradução original (padrão: `EN`) |
| `default_target_lang` | Código padrão da língua de destino (por exemplo, `RU`, `DE`, `CN`, `JP`, `PTBR`) |
| `ui_lang` | Código da linguagem da interface padrão, proveniente de `cli_locales/` |
| `mirror_dir` | Pasta local onde as cópias completas das traduções geradas são armazenadas. |
| `state_file` | Arquivo JSON que armazena o histórico de traduções e os hashes das strings originais. |
| `save_every` | Salvar o progresso no disco e criar cópias de segurança de todas as N chaves traduzidas. |

---

## Uso

### Modo Interativo

Comece com o `llama-server`, e depois execute:

```bash
python pz_translate.py
```

1. **Selecione o Idioma da Interface:** Escolha entre os idiomas disponíveis em `cli_locales/` (padrão: `en`).
2. **Modo de Seleção:**
   - `1` — Traduzir um caminho de mod específico.
   - `2` — Escanear todos os mods em `mods_path`, visualizar a tabela com a contagem de strings/caracteres, e inserir os números dos mods (por exemplo, `1,3,5`, `1-4`, ou `todos`).
   - `3` — Gerenciar o progresso salvo (atualizar chaves alteradas/novas, traduzir novamente do zero, restaurar de `pz_translator_mods/`, ou excluir traduções).
   - `4` — Alterar o idioma da interface.
   - `0` — Sair.

### Argumentos da Linha de Comando

Você pode contornar o menu interativo usando as flags da linha de comando (os argumentos da linha de comando substituem o `config.json`):

| Flag | Descrição |
| --- | --- |
| `--config <caminho>` | Caminho para um arquivo `config.json` personalizado |
| `--mode {1, 2, 3}` | `1` = modo único, `2` = escanear diretório, `3` = gerenciar o progresso salvo |
| `--path <caminho>` | Caminho para uma pasta de mods (Modo 1) ou pasta raiz de mods (Modo 2) |
| `--lang <code>` | Idioma de destino como um código de pasta PZ (`RU`, `CN`, `PTBR`) ou código ISO (`ru`, `zh`, `pt-BR`) |
| `--source-lang <code>` | Substituir a pasta de idioma de origem (padrão: `EN`) |
| `--host <host>` | Sobrescrever `llamacpp_host` |
| `--port <porta>` | Substituir `llamacpp_port` |
| `--ui-lang <code>` | Código da linguagem da interface (por exemplo, `en`, `ru`) |
| `--force` | Sobrescrever traduções já existentes |

#### Exemplos

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

## Como Funciona

1. **Descoberta de Mods:** Procura recursivamente por diretórios `Translate/<SOURCE_LANG>` que contenham arquivos `.json` e extrai os nomes dos mods de `mod.info` e das estruturas de pastas do Workshop (`mods/<ModName>/<Version>`).
2. **Comparação e Estimativa de Volume:** Compara chaves em `EN/*.json` com arquivos de destino existentes (`<TARGET_LANG>/*.json`) e hashes SHA-1 armazenados em `pz_translator_state.json`. Apenas chaves ausentes ou chaves cujo texto em inglês original foi alterado desde a última tradução são colocadas em fila.
3. **Tradução LLM:** Envia cada string para `http://<host>:<port>/completion` usando o formato de "turno de conversa" do TranslateGemma.
4. **Saída Dupla:** Cada chave `save_every` (e ao término ou `Ctrl+C`), escreve JSON UTF-8 válido em:
   - A pasta de destino do módulo: `...\Translate\<LANG>\<file>.json`
   - A pasta de espelho local: `pz_translator_mods\<caminho_completo_sem_letra_de_unidade>\Translate\<LANG>\<arquivo>.json`

---

## Notas & Limitações

- **Formato Suportado:** Apenas os arquivos de localização `.json` do Project Zomboid **Build 42.15+** são processados. Os arquivos de tradução antigos `.txt` são ignorados, pois o B42.15+ não os carrega mais.
- **Multiplayer (`DoLuaChecksum`):** Como as pastas `Translate` residem dentro de `media/lua/shared/`, adicionar arquivos de tradução diretamente dentro das pastas do Steam Workshop pode causar incompatibilidades de checksum nos servidores multiplayer com `DoLuaChecksum=true`. Para servidores multiplayer públicos, ou empacote os arquivos espelhados de `pz_translator_mods/` como um mod separado, dedicado apenas à tradução, ou jogue no modo singleplayer / servidores com `DoLuaChecksum=false`.
```
