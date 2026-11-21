# Tradutor de Mod para Project Zomboid

Uma ferramenta de linha de comando para traduzir os mods de **Project Zomboid (versão 42.15+)** utilizando um servidor `llama.cpp` local (`llama-server`), alimentado pela **TranslateGemma**.

Ele escaneia a Steam Workshop ou as pastas de mods locais em busca de arquivos `Translate/EN/*.json`, estima o volume de tradução (número de linhas e caracteres), traduz strings ausentes ou atualizadas, valida variáveis e tags de marcação da interface, e cria uma cópia local de todas as traduções geradas, para que você possa facilmente criar mods de tradução independentes ou restaurar os arquivos após as atualizações da Steam.

---

## Recursos

- **Suporte a JSON na versão 42.15+:** Funciona com o formato de tradução `.json` moderno utilizado no Project Zomboid 42.15+ (os mods antigos que utilizam apenas arquivos `.txt` são ignorados durante a verificação).
- **Interface de Terminal Rica:** Tabelas coloridas e limpas, indicadores de status e barras de progresso em tempo real, exibindo o tempo decorrido e o tempo restante, utilizando a biblioteca `rich`.
- **Interface de Linha de Comando Multilíngue (`i18n`):** Por padrão, utiliza o inglês e solicita ao usuário que selecione o idioma da interface a partir dos arquivos `cli_locales/*.json` durante o início interativo.
- **3 Modos de operação:**
  - **Modo 1:** Traduzir um único mod especificado (ou a pasta `Translate` / `EN` dele).
  - **Modo 2:** Digitalize todo o diretório do seu workshop, verifique o status das traduções e o volume de caracteres por mod, e selecione os mods usando números (`1,3,5`), intervalos (`1-4`), ou `all`.
  - **Modo 3:** Gerenciar o progresso salvo – detectar atualizações de mods, traduzir novas/modificadas/corrompidas strings, sobrescrever do zero, restaurar a partir de uma cópia, excluir de forma limpa os arquivos gerados, ou executar um relatório de verificação de tokens de teste.
- **Substituições e Validação de Marcadores (`token_rules.json`):** Extrai os substituições do mod (`{name}`, `%1`) e as tags RichText do Project Zomboid (`<LINE>`, `<RGB:...>`, `<IMAGE:...>`, etc.) através de regras de expressões regulares configuráveis e verifica se há uma correspondência exata após a tradução. Em caso de incompatibilidade, tenta novamente com diferentes "sementes" (`max_retries`). Se todos os tentos falharem, mantém a string original em inglês, marca o status do mod como `EN/<LANG>`, e registra os detalhes em `pz_translator_issues.log`.
- **Detecção de Atualizações e Rastreamento de Progresso:** Armazena os hashes SHA-1 por chave das strings originais em inglês no arquivo `pz_translator_state.json`. Se uma atualização for publicada na Steam Workshop, apenas as chaves de novas adições, modificações ou chaves com erros são colocadas em fila para tradução.
- **Espelho Local (`pz_translator_mods/`):** Salva uma cópia de todos os arquivos traduzidos, preservando a estrutura de diretórios relativa (o que facilita a criação de modificações independentes, focadas apenas na tradução).
- **Seguro e resistente a falhas:**
  - Traduções de autores já existentes (tanto modificações originais quanto chaves de tradução individuais não rastreadas em `pz_translator_state.json`) nunca são analisadas pelas regras de token, modificadas ou substituídas.
  - Suporta o cabeçalho UTF-8, vírgulas extras em arquivos JSON de mods editados manualmente, e preserva o `$schema` e strings vazias.
  - Salva o progresso automaticamente em intervalos regulares (`save_every`) e ao pressionar `Ctrl+C`.

---

## Requisitos

- **Python 3.9 ou superior**
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
    "token_rules_file": "token_rules.json",
    "save_every": 20
}
```

| Chave | Descrição |
| --- | --- |
| `llamacpp_host` | Endereço do servidor onde o `llama-server` está sendo executado. |
| `llamacpp_port` | Porta para o seu servidor `llama-server` em execução. |
| `mods_path` | Diretório raiz padrão escaneado no Modo 2 (por exemplo, a pasta `108600` do Steam Workshop). |
| `default_source_lang` | Nome da pasta de origem para a tradução (padrão: `EN`) |
| `default_target_lang` | Código padrão da língua de destino (por exemplo, `RU`, `DE`, `CN`, `JP`, `PTBR`) |
| `ui_lang` | Código da linguagem padrão da interface, proveniente de `cli_locales/` |
| `mirror_dir` | Pasta local onde são armazenadas cópias completas das traduções geradas. |
| `state_file` | Arquivo JSON que armazena o histórico de traduções e os hashes das strings originais. |
| `token_rules_file` | Arquivo JSON com regras de expressões regulares e configurações de repetição para validação de placeholders/tags. |
| `save_every` | Salvar o progresso no disco e criar cópias de segurança de cada N chaves traduzidas. |

### Validação de Tokens (`token_rules.json`)

As regras de Regex para proteger variáveis dinâmicas e as tags de marcação do Project Zomboid são configuradas no arquivo `token_rules.json`:

| Chave | Descrição |
| --- | --- |
| `max_retries` | Número máximo de tentativas de tradução com diferentes "sementes" quando os tokens críticos não correspondem. |
| `retry_temperatures` | Cronograma de temperatura aplicado em todas as tentativas de repetição (por exemplo, `[0.2, 0.35, 0.5]`) |
| `issues_log` | Arquivo de log onde as strings que falharam na validação após todas as tentativas são registradas, juntamente com sua origem em inglês (`EN`) e os resultados das tentativas malsucedidas. |
| `check_report` | Arquivo de saída para o relatório de inspeção de tokens no modo 3 |
| `rules` | Array de objetos de regras de expressão regular (`name`, `pattern`, `enabled`, `critical`, `description`) |

As regras marcadas com `"critical": true` acionam tentativas de tradução durante o processo e registram chaves para re-tradução durante as atualizações. As regras não críticas (`"critical": false`) são apenas reportadas como avisos no relatório de verificação prévia.

---

## Utilização

### Modo Interativo

Comece executando o `llama-server` primeiro, e depois execute:

```bash
python pz_translate.py
```

1. **Selecione o idioma da interface:** Escolha entre os idiomas disponíveis em `cli_locales/` (padrão: `en`).
2. **Modo de Seleção:**
   - `1` — Traduzir um caminho de mod específico.
   - `2` – Analise todos os mods em `mods_path`, visualize a tabela com o número de strings/caracteres, e insira os números dos mods (por exemplo, `1,3,5`, `1-4` ou `all`).
   - `3` — Gerenciar o progresso salvo (atualizar chaves de tokens novas/modificadas/corrompidas, traduzir novamente do zero, restaurar a partir de `pz_translator_mods/`, excluir traduções ou executar um relatório de verificação de tokens).
   - `4` – Alterar o idioma da interface.
   - `0` — Sair.

### Argumentos da Linha de Comando

É possível contornar o menu interativo utilizando as opções da linha de comando (os argumentos da linha de comando substituem o arquivo `config.json`):

| Bandeira | Descrição |
| --- | --- |
| `--config <path>` | Caminho para um arquivo `config.json` personalizado |
| `--rules <path>` | Caminho para um arquivo `token_rules.json` personalizado |
| `--mode {1,2,3}` | `1` = modo único, `2` = escanear diretório, `3` = gerenciar o progresso salvo |
| `--path <path>` | Caminho para a pasta de mods (Modo 1) ou para a pasta raiz de mods (Modo 2) |
| `--lang <code>` | Língua-alvo como código de pasta PZ (`RU`, `CN`, `PTBR`) ou código ISO (`ru`, `zh`, `pt-BR`) |
| `--source-lang <code>` | Substituir a pasta de origem da língua (padrão: `EN`) |
| `--host <host>` | Substituir `llamacpp_host` |
| `--port <port>` | Substituir `llamacpp_port` |
| `--ui-lang <code>` | Código da linguagem da interface (por exemplo, `en`, `ru`) |
| `--force` | Substituir as traduções existentes |
| `--check` | Execute uma verificação de tokens em todas as traduções salvas e crie o arquivo `pz_translator_check_report.txt`. |

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

# Run a dry-run token check on all saved translations without calling the LLM
python pz_translate.py --mode 3 --check
```

---

## Como funciona

1. **Descoberta de Mods:** Procura recursivamente por `Translate/<SOURCE_LANG>` diretórios que contenham `.json` arquivos e extrai os nomes dos mods das estruturas de pastas `mod.info` e Workshop (`mods/<ModName>/<Version>`).
2. **Comparação e Estimativa de Volume:** Compara as chaves em `EN/*.json` com os arquivos de referência existentes (`<TARGET_LANG>/*.json`), os hashes SHA-1 armazenados em `pz_translator_state.json`, e as regras críticas de `token_rules.json`. Chaves ausentes, chaves cujos textos originais em inglês foram alterados, e chaves rastreadas com marcadores/tags quebrados são colocadas em fila para tradução; as traduções pré-existentes do autor permanecem inalteradas.
3. **Tradução e Validação de LLM:** Envia cada string original completa para `http://<host>:<port>/completion` utilizando o formato de prompt "TranslateGemma" padrão, e, em seguida, verifica os tokens críticos em relação à string original. Em caso de incompatibilidade, tenta novamente com diferentes "seeds" até `max_retries`; se todos os tentos falharem, mantém o texto em inglês, marca o status de modificação como `EN/<LANG>`, e registra os detalhes em `pz_translator_issues.log`.
4. **Saída Dupla:** Cada chave `save_every` (e ao final ou com `Ctrl+C`), grava JSON válido em UTF-8 nos seguintes locais:
   - A pasta de destino: `...\Translate\<LANG>\<file>.json`
   - A pasta do espelho local: `pz_translator_mods\<full_path_without_drive_letter>\Translate\<LANG>\<file>.json`

---

## Observações e Limitações

- **Formato Suportado:** Apenas os arquivos de localização `.json` do Project Zomboid **versão 42.15+** são processados. Os arquivos de tradução antigos no formato `.txt` são ignorados, pois a versão 42.15+ não os carrega mais.
- **Multijogador (`DoLuaChecksum`):** Como as pastas `Translate` estão localizadas dentro de `media/lua/shared/`, adicionar arquivos de tradução diretamente nas pastas do Steam Workshop pode causar incompatibilidades nos checksum em servidores multijogador com `DoLuaChecksum=true`. Para servidores multijogador públicos, é possível empacotar os arquivos espelhados de `pz_translator_mods/` como um mod separado, dedicado apenas à tradução, ou jogar no modo singleplayer / servidores com `DoLuaChecksum=false`.
