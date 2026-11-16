# 프로젝트 좀비 모드 번역가

로컬 `llama.cpp` 서버(`llama-server`)를 사용하여 **Project Zomboid (Build 42.15 이상)** 모드를 현지화하는 CLI 도구. **TranslateGemma** 기반.

Steam 워크숍 또는 로컬 모드 폴더에서 `Translate/EN/*.json` 파일을 검색하고, 번역량(줄 수 및 문자 수)을 추정하고, 누락되거나 업데이트된 문자열을 번역하며, 생성된 모든 번역을 로컬에 복사하여, 독립적인 번역 모드를 쉽게 패키징하거나 Steam 업데이트 후 파일을 복원할 수 있도록 합니다.

---

## 특징

- **42.15+ 버전의 JSON 지원:** Project Zomboid B42.15+에서 사용되는 최신 `.json` 번역 형식을 지원합니다 (B42.15+의 기존 `.txt` 파일만 사용하는 모드는 스캔 시 안전하게 건너뜁니다).
- **풍부한 터미널 인터페이스:** `rich`를 사용하여 깔끔한 색상 테이블, 상태 배지, 그리고 경과 시간/남은 시간을 표시하는 실시간 진행 막대를 제공합니다.
- **다국어 CLI (`i18n`):** 기본적으로 영어로 설정되며, 인터랙티브 시작 시 `cli_locales/*.json`에서 인터페이스 언어를 선택하도록 안내합니다.
- **3 작동 모드:**
  - **모드 1:** 특정 모드(또는 해당 `Translate` / `EN` 폴더)를 번역합니다.
  - **모드 2:** 워크숍 전체 디렉토리를 스캔하고, 각 모드별 번역 상태 및 문자 수를 확인하고, 숫자 (`1,3,5`), 범위 (`1-4`), 또는 `모든`을 사용하여 모드를 선택합니다.
  - **모드 3:** 저장된 진행 상황 관리 — 모드 업데이트 감지, 새/변경된 문자열 번역만 수행, 처음부터 다시 시작, 미러에서 복원, 또는 생성된 파일 깔끔하게 삭제.
- **업데이트 감지 및 진행 상황 추적:** 소스 영어 문자열의 각 키에 대한 SHA-1 해시를 `pz_translator_state.json`에 저장합니다. Steam Workshop에서 업데이트가 발생하면, 새로 추가되거나 수정된 영어 키만 번역 대기 목록에 추가됩니다.
- **로컬 미러 (`pz_translator_mods/`):** 번역된 모든 파일의 복사본을 저장하고, 상대적인 디렉토리 구조를 유지하여 (독립적인 번역 모드를 쉽게 만들 수 있도록 함).
- **안전하고, 오류에 강함:**
  - 기존 저자 번역에 대해 `0`개의 처리 중인 키가 있는 경우, 해당 번역은 변경되지 않거나 추적되지 않습니다.
  - UTF-8 BOM, 수동으로 편집한 mod JSON 파일의 꼬리 쉼표, 그리고 `$schema`와 빈 문자열을 처리합니다.
  - 자동으로 주기적으로 진행 상황을 저장합니다 (`save_every`) 및 `Ctrl+C` 키를 누를 때 저장합니다.

---

## 요구 사항

- **파이썬 3.9 이상**
- **llama.cpp** (`llama-server`)가 구성된 호스트/포트에서 **TranslateGemma** GGUF 모델을 실행합니다 (기본값: `http://127.0.0.1:8734`).
- 파이썬 종속성:

```bash
pip install -r requirements.txt
```

---

## 구성 (`config.json`)

처음 실행 시 (또는 포함된 `config.json` 파일을 통해) 스크립트는 다음 설정을 사용합니다:

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

| 핵 | 설명 |
| --- | --- |
| `llamacpp_host` | 현재 실행 중인 `llama-server`의 호스트 주소 |
| `llamacpp_port` | `llama-server` 실행 포트 |
| `mods_path` | 모드 2에서 기본 루트 디렉터리 스캔 (예: Steam 워크숍 `108600` 폴더) |
| `default_source_lang` | 소스 번역 폴더 이름 (기본값: `EN`) |
| `default_target_lang` | 기본 대상 언어 코드 (예: `RU`, `DE`, `CN`, `JP`, `PTBR`) |
| `ui_lang` | `cli_locales/` 디렉토리에서 기본 인터페이스 언어 코드 |
| `mirror_dir` | 생성된 번역의 전체 경로 복사본이 저장되는 로컬 폴더 |
| `state_file` | 번역 기록 및 원본 문자열 해시를 저장하는 JSON 파일 |
| `save_every` | 진행 상황을 디스크에 저장하고, 번역된 키를 N개씩 복제 |

---

## 사용 방법

### 대화형 모드

먼저 `llama-server`를 시작하고, 그 다음 다음 명령을 실행하세요:

```bash
python pz_translate.py
```

1. **인터페이스 언어 선택:** `cli_locales/`에 있는 사용 가능한 언어 중에서 선택하세요 (기본값: `en`).
2. **모드 선택:**
   - `1` — 특정 모드 경로 번역
   - `2` — `mods_path` 내의 모든 모드를 스캔하고, 문자/문자 개수를 보여주는 테이블을 확인하고, 모드 번호를 입력합니다 (예: `1,3,5`, `1-4`, 또는 `모든`).
   - `3` — 저장된 진행 상황 관리 (변경/새로운 키 업데이트, 처음부터 다시 번역, `pz_translator_mods/`에서 복원, 번역 삭제)
   - `4` — 인터페이스 언어 변경
   - `0` — 종료

### 명령줄 인수

CLI 플래그를 사용하여 대화형 메뉴를 우회할 수 있습니다 (CLI 인수는 `config.json`을 덮어씁니다):

| 플래그 | 설명 |
| --- | --- |
| `--config <경로>` | 사용자 정의 `config.json` 파일의 경로 |
| `--mode {1, 2, 3}` | `1` = 단일 모드, `2` = 디렉토리 스캔, `3` = 저장된 진행 상황 관리 |
| `--path <경로>` | 모드 폴더의 경로 (모드 1) 또는 모드 루트 폴더의 경로 (모드 2) |
| `--lang <code>` | 대상 언어는 PZ 폴더 코드(`RU`, `CN`, `PTBR`) 또는 ISO 코드(`ru`, `zh`, `pt-BR`)로 지정 |
| `--source-lang <code>` | 소스 언어 폴더 재정의 (기본값: `EN`) |
| `--host <호스트>` | `llamacpp_host` 재정의 |
| `--port <포트>` | `llamacpp_port` 재정의 |
| `--ui-lang <code>` | 인터페이스 언어 코드 (예: `en`, `ru`) |
| `--force` | 기존 번역을 덮어쓰기 |

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
```

---

## 작동 방식

1. **모드 검색:** `Translate/<SOURCE_LANG>` 디렉터리 내에 있는 `.json` 파일을 재귀적으로 검색하고, `mod.info` 및 워크숍 폴더 구조(`mods/<ModName>/<Version>`)에서 모드 이름을 추출합니다.
2. **차이 및 볼륨 추정:** `EN/*.json` 파일의 키를 기존 대상 파일(`<TARGET_LANG>/*.json`) 및 `pz_translator_state.json`에 저장된 SHA-1 해시와 비교합니다. 누락된 키 또는 마지막 번역 이후 영어 원본 텍스트가 변경된 키만 큐에 추가됩니다.
3. **LLM 번역:** `TranslateGemma` 채팅 턴 형식으로 각 문자열을 `http://<호스트>:<포트>/completion`으로 전송합니다.
4. **듀얼 출력:** `save_every` 키(및 완료 또는 `Ctrl+C` 시)에 유효한 UTF-8 JSON을 다음 위치에 기록합니다:
   - 대상 모듈 폴더: `...\Translate\<LANG>\<file>.json`
   - 로컬 미러 폴더: `pz_translator_mods\<전체 경로 (드라이브 문자 제외)>\Translate\<언어>\<파일>.json`

---

## 참고사항 및 제한 사항

- **지원 형식:** Project Zomboid **빌드 42.15 이상**의 `.json` 로컬라이제이션 파일만 처리됩니다. 이전 `.txt` 번역 파일은 B42.15+에서 더 이상 로드되지 않으므로 무시됩니다.
- **멀티플레이어 (`DoLuaChecksum`):** `Translate` 폴더가 `media/lua/shared/` 안에 위치하기 때문에, Steam 워크숍 폴더 안에 직접 번역 파일을 추가하면 `DoLuaChecksum=true`인 멀티플레이어 서버에서 체크섬 불일치가 발생할 수 있습니다. 공개 멀티플레이어 서버의 경우, `pz_translator_mods/`에서 복사된 파일을 별도의 번역만 포함하는 모드로 패키징하거나, `DoLuaChecksum=false`로 싱글 플레이 또는 서버에서 플레이하십시오.
```
