# 프로젝트 좀비 모드 번역가

**프로젝트 짐보이드 (빌드 42.15 이상) 모드**를 로컬 `llama.cpp` 서버 (`llama-server`)와 **TranslateGemma**를 사용하여 현지화하는 데 사용할 수 있는 명령줄 도구.

Steam 워크숍 또는 로컬 모드 폴더에서 `Translate/EN/*.json` 파일을 검색하여 번역량 (줄 수 및 문자 수)을 추정하고, 누락되거나 업데이트된 문자열을 번역하며, 변수 및 UI 마크업 태그를 검증하고, 생성된 모든 번역을 로컬에 복사하여 독립적인 번역 모드를 쉽게 패키징하거나 Steam 업데이트 후 파일을 복원할 수 있도록 합니다.

---

## 특징

- **42.15+ JSON 지원:** Project Zomboid B42.15+에서 사용되는 최신 `.json` 번역 형식을 지원합니다 (기존 `.txt` 파일만 사용하는 모드는 스캔 시 안전하게 건너뜁니다).
- **풍부한 터미널 인터페이스:** 깔끔한 색상 테이블, 상태 표시, 그리고 `rich` 라이브러리를 사용하여 경과 시간/남은 시간을 표시하는 실시간 진행 표시줄.
- **다국어 CLI (`i18n`):** 기본적으로 영어로 설정되어 있으며, 인터랙티브 시작 시 `cli_locales/*.json` 파일에서 인터페이스 언어를 선택하도록 안내합니다.
- **3가지 작동 모드:**
  - **모드 1:** 특정 모드(또는 해당 모드의 `Translate` / `EN` 폴더)를 번역합니다.
  - **모드 2:** 워크숍 전체 디렉토리를 스캔하여 각 모드의 번역 상태와 문자 수를 확인하고, 숫자 (`1,3,5`), 범위 (`1-4`), 또는 `all`를 사용하여 모드를 선택합니다.
  - **모드 3: 저장된 진행 상황 관리 – 모드 업데이트 감지, 새로운/변경/손상된 토큰 문자열 번역, 처음부터 다시 시작, 미러에서 복원, 생성된 파일 깔끔하게 삭제, 또는 토큰 검사 보고서를 실행.**
- **플래스홀더 및 마크업 검증 (`token_rules.json`):** 구성 가능한 정규 표현 규칙을 사용하여 모드 플래스홀더 (`{name}`, `%1`) 및 프로젝트 좀바이 RichText 태그 (`<LINE>`, `<RGB:...>`, `<IMAGE:...>`, 등)를 추출하고, 번역 후 정확한 일치 여부를 확인합니다. 일치하지 않으면 다른 시드 (`max_retries`)를 사용하여 다시 시도합니다. 모든 시도가 실패하면 원래 영어 문자열을 유지하고, 모드 상태를 `EN/<LANG>`으로 표시하며, 상세 정보를 `pz_translator_issues.log`에 기록합니다.
- **업데이트 감지 및 진행 상황 추적:** `pz_translator_state.json` 파일에 소스 영어 문자열의 각 키에 대한 SHA-1 해시를 저장합니다. Steam 워크숍에서 업데이트가 발생하면, 새로 추가되거나 수정되거나 오류가 있는 키만 번역 대기 목록에 추가됩니다.
- **로컬 미러 (`pz_translator_mods/`):** 번역된 모든 파일의 복사본을 저장하고, 상대적인 디렉토리 구조를 유지하여 독립적인 번역 모드를 쉽게 만들 수 있도록 합니다.
- **안전하고, 오류에 강함:**
  - 기존에 작성된 번역 (수정되지 않은 모드와 `pz_translator_state.json`에 기록되지 않은 개별 저자 번역 키)은 토큰 규칙에 의해 분석되거나 수정되거나 덮어쓰여지지 않습니다.
  - UTF-8 BOM, 수동으로 편집한 모드 JSON 파일의 꼬리 따옴표, 그리고 `$schema`와 빈 문자열을 유지합니다.
  - 자동으로 주기적으로 진행 상황을 저장 (`save_every`)하고, `Ctrl+C` 키를 누를 때도 저장합니다.

---

## 요구 사항

- **파이썬 3.9 이상**
- **llama.cpp** (`llama-server`)가 설정된 호스트/포트에서 **TranslateGemma** GGUF 모델을 실행합니다 (기본값: `http://127.0.0.1:8734`).
- 파이썬 의존성:

```bash
pip install -r requirements.txt
```

---

## 구성 (`config.json`)

처음 실행하거나, 포함된 `config.json` 파일을 통해 실행할 경우, 스크립트는 다음과 같은 설정을 사용합니다:

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

| 핵심 | 설명 |
| --- | --- |
| `llamacpp_host` | `llama-server`을 실행하는 호스트 주소 |
| `llamacpp_port` | `llama-server` 실행 포트 |
| `mods_path` | 기본 루트 디렉터리가 모드 2 (예: 스팀 워크숍 `108600` 폴더)에서 스캔됨 |
| `default_source_lang` | 소스 번역 폴더 이름 (기본값: `EN`) |
| `default_target_lang` | 기본 대상 언어 코드 (예: `RU`, `DE`, `CN`, `JP`, `PTBR`) |
| `ui_lang` | `cli_locales/` 디렉토리에서 기본 인터페이스 언어 코드 |
| `mirror_dir` | 생성된 번역의 전체 경로를 저장하는 로컬 폴더 |
| `state_file` | 번역 기록 및 원본 문자 해시를 저장하는 JSON 파일 |
| `token_rules_file` | 정규 표현 규칙 및 대체 변수/태그 검증을 위한 재시도 설정이 포함된 JSON 파일 |
| `save_every` | 진행 내용을 저장하고, 번역된 키를 N개씩 복제하여 저장 |

### 토큰 유효성 검사 (`token_rules.json`)

동적 변수와 프로젝트 줌보이드 마크업 태그를 보호하기 위한 정규 표현 규칙은 `token_rules.json` 파일에 설정되어 있습니다.

| 핵심 | 설명 |
| --- | --- |
| `max_retries` | 중요한 토큰이 일치하지 않을 때, 다양한 시드를 사용하여 번역 시도 횟수의 최대 |
| `retry_temperatures` | 재시도 시도에 걸맞은 온도 스케줄 적용 (예: `[0.2, 0.35, 0.5]`) |
| `issues_log` | 유효성 검사를 통과하지 못한 문자열이 모든 재시도 후 기록된 로그 파일. 여기에는 `EN` 소스 및 실패한 시도에 대한 정보가 포함됩니다. |
| `check_report` | 모드 3에서 수행된 토큰 검사 보고서의 출력 파일 |
| `rules` | 정규 표현 규칙 객체의 배열 (`name`, `pattern`, `enabled`, `critical`, `description`) |

`"critical": true`로 표시된 규칙은 번역 과정에서 재시도, 업데이트 시 재번역을 위한 큐 분리된 키를 추적합니다. 중요하지 않은 규칙(`"critical": false`)은 실행 시뮬레이션 보고서에서 경고로만 표시됩니다.

---

## 사용 방법

### 상호작용 모드

먼저 `llama-server`를 시작하고, 그 다음 다음 명령을 실행하세요:

```bash
python pz_translate.py
```

1. **인터페이스 언어 선택:** `cli_locales/`에 있는 사용 가능한 언어 중에서 선택하세요 (기본값: `en`).
2. **선택 모드:**
   - `1` — 특정 모드 경로 번역
   - `2` — `mods_path` 내 모든 모드를 스캔하고, 문자/문자 수 정보를 보여주는 표를 확인한 다음, 모드 번호 (예: `1,3,5`, `1-4`, 또는 `all`)를 입력합니다.
   - `3` — 저장된 진행 상황 관리 (새/변경/손상된 토큰 키 업데이트, 처음부터 다시 번역, `pz_translator_mods/`에서 복원, 번역 삭제, 또는 토큰 검사 보고서 실행)
   - `4` — 인터페이스 언어 변경
   - `0` — 종료

### 명령줄 인자

CLI 플래그를 사용하여 인터랙티브 메뉴를 우회할 수 있습니다 (CLI 플래그는 `config.json` 설정을 덮어씁니다).

| 깃발 | 설명 |
| --- | --- |
| `--config <path>` | 사용자 정의 `config.json` 파일 생성 방법 |
| `--rules <path>` | 사용자 정의 `token_rules.json` 파일 생성 방법 |
| `--mode {1,2,3}` | `1` = 단일 모드, `2` = 디렉토리 검색, `3` = 저장된 진행 상황 관리 |
| `--path <path>` | 모드 폴더 (모드 1) 또는 모드 루트 폴더 (모드 2)로 이동하는 경로 |
| `--lang <code>` | 대상 언어를 PZ 폴더 코드(`RU`, `CN`, `PTBR`) 또는 ISO 코드(`ru`, `zh`, `pt-BR`)로 지정 |
| `--source-lang <code>` | 기본 언어 폴더를 덮어쓰기 (기본값: `EN`) |
| `--host <host>` | `llamacpp_host` 설정을 재정의 |
| `--port <port>` | `llamacpp_port` 설정을 재정의 |
| `--ui-lang <code>` | 인터페이스 언어 코드 (예: `en`, `ru`) |
| `--force` | 기존 번역을 덮어쓰기 |
| `--check` | 저장된 모든 번역에 대해 건너뛰기 방식으로 토큰 검사를 수행하고, `pz_translator_check_report.txt` 파일을 생성합니다. |

#### 예시

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

## 작동 원리

1. **모드 검색:** `Translate/<SOURCE_LANG>` 디렉터리 내에 있는 `.json` 파일을 재귀적으로 검색하고, `mod.info` 파일과 워크숍 폴더 구조(`mods/<ModName>/<Version>`)에서 모드 이름을 추출합니다.
2. **차이 및 볼륨 추정:** `EN/*.json` 파일의 키를 기존 대상 파일(`<TARGET_LANG>/*.json`), `pz_translator_state.json`에 저장된 SHA-1 해시, 그리고 `token_rules.json` 파일의 중요한 규칙과 비교합니다. 누락된 키, 영어 원본 텍스트가 변경된 키, 그리고 깨진 플레이스홀더/태그가 있는 추적된 키는 번역 대기 목록에 추가됩니다. 기존 저자 번역은 변경되지 않습니다.
3. **LLM 번역 및 검증:** 원본 텍스트 전체를 `http://<host>:<port>/completion`에 canonical TranslateGemma 프롬프트 형식을 사용하여 전송하고, 그 후 핵심 토큰을 원본 텍스트와 비교합니다. 불일치가 발생하면 `max_retries`까지 다른 시드를 사용하여 다시 시도합니다. 모든 시도가 실패하면, 영어 텍스트를 유지하고 수정 상태를 `EN/<LANG>`로 표시하며, 세부 정보를 `pz_translator_issues.log`에 기록합니다.
4. **듀얼 출력:** `save_every` 키(및 완료 또는 `Ctrl+C` 시)에, 유효한 UTF-8 JSON 형식으로 다음 위치에 저장합니다:
   - 대상 모드 폴더: `...\Translate\<LANG>\<file>.json`
   - 로컬 미러 폴더: `pz_translator_mods\<full_path_without_drive_letter>\Translate\<LANG>\<file>.json`

---

## 참고사항 및 제한 사항

- **지원 형식:** Project Zomboid **버전 42.15 이상**의 `.json` 형식의 현지화 파일만 처리됩니다. 이전 `.txt` 형식의 번역 파일은 더 이상 로드되지 않으므로 무시됩니다.
- **멀티플레이어 (`DoLuaChecksum`):** `Translate` 폴더가 `media/lua/shared/` 안에 위치하기 때문에, Steam 워크숍 폴더 안에 직접 번역 파일을 추가하면 `DoLuaChecksum=true`인 멀티플레이어 서버에서 체크섬 불일치가 발생할 수 있습니다. 공개 멀티플레이어 서버의 경우, `pz_translator_mods/`에서 복사한 파일을 별도의 번역 전용 모드로 패키징하거나, `DoLuaChecksum=false`로 싱글 플레이 또는 서버에서 플레이하는 것이 좋습니다.
