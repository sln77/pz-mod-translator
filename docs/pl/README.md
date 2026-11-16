# Tłumacz Modów dla Project Zomboid

Narzędzie wiersza poleceń do lokalizacji modów dla **Project Zomboid (wersja 42.15+)** przy użyciu lokalnego serwera `llama.cpp` (`llama-server`), zasilanego przez **TranslateGemma**.

Skanuje Steam Workshop lub lokalne foldery z modami w poszukiwaniu plików `Translate/EN/*.json`, szacuje ilość tłumaczeń (liczba wierszy i znaków), tłumaczy brakujące lub zaktualizowane ciągi znaków oraz tworzy lokalne kopie wszystkich wygenerowanych tłumaczeń, dzięki czemu można łatwo pakować samodzielne mody z tłumaczeniami lub przywracać pliki po aktualizacjach Steam.

---

## Funkcje

- **Obsługa JSON w wersji 42.15+:** Działa z nowoczesnym formatem `.json` tłumaczeń używanym w Project Zomboid B42.15+ (starsze mody w formacie `.txt` są bezpiecznie pomijane podczas skanowania).
- **Bogaty interfejs terminala:** Czyste, kolorowe tabele, znaczniki statusu oraz dynamiczne paski postępu z czasem upływającym/pozostałym, dzięki bibliotece `rich`.
- **Wielojęzyczna linia poleceń (CLI) (`i18n`):** Domyślnie ustawiona na język angielski, a podczas interaktywnego uruchamiania, użytkownik jest proszony o wybranie języka interfejsu z plików `cli_locales/*.json`.
- **3 Tryby pracy:**
  - **Tryb 1:** Przetłumaczenie pojedynczego, określonego modułu (lub jego folderu `Translate` / `EN`).
  - **Tryb 2:** Przeskanuj cały katalog Twojego workshopu, sprawdź status tłumaczenia i ilość znaków na mod, a następnie wybierz mody za pomocą numerów (`1,3,5`), zakresów (`1-4`) lub słowa kluczowego `all`.
  - **Tryb 3:** Zarządzanie zapisanym postępem — wykrywanie aktualizacji modów, tłumaczenie tylko nowych/zmodyfikowanych ciągów, ponowne tworzenie od początku, przywracanie z kopii, lub czyste usuwanie wygenerowanych plików.
- **Wykrywanie zmian i śledzenie postępów:** Przechowuje hasze SHA-1 dla poszczególnych kluczy w języku angielskim w pliku `pz_translator_state.json`. Jeśli mod jest aktualizowany w Steam Workshop, tylko nowe lub zmodyfikowane klucze w języku angielskim są kolejkowane do tłumaczenia.
- **Lokalna kopia (`pz_translator_mods/`):** Zapisuje kopię każdego przetłumaczonego pliku, zachowując strukturę katalogów (co ułatwia tworzenie samodzielnych modów zawierających tylko tłumaczenia).
- **Bezpieczne i odporne na awarie:**
  - Istniejące tłumaczenia autorów z `0` oczekującymi kluczami nigdy nie są modyfikowane, nadpisywane ani śledzone.
  - Obsługuje nagłówek UTF-8, przecinki na końcu plików JSON modyfikowanych ręcznie, oraz zachowuje `$schema` i puste ciągi znaków.
  - Automatycznie zapisuje postęp okresowo (`save_every`) i przy naciśnięciu `Ctrl+C`.

---

## Wymagania

- **Python 3.9+**
- **llama.cpp** (`llama-server`) uruchamiający model **TranslateGemma** w formacie GGUF na skonfigurowanym host/porcie (domyślnie: `http://127.0.0.1:8734`).
- Zależności Pythona:

```bash
pip install -r requirements.txt
```

---

## Konfiguracja (`config.json`)

Przy pierwszym uruchomieniu (lub za pomocą wbudowanego pliku `config.json`), skrypt używa następujących ustawień:

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

| Klucz | Opis |
| ---
--- | ---
--- |
| `llamacpp_host` | Adres hosta Twojego działającego `llama-server` |
| `llamacpp_port` | Port, na którym działa `llama-server`. |
| `ścieżka_do_modów` | Domyślny katalog główny przeskanowany w trybie 2 (np. folder `108600` w Steam Workshop) |
| `default_source_lang` | Nazwa folderu z tłumaczeniami (domyślnie: `EN`) |
| `default_target_lang` | Domyślny kod języka docelowego (np. `RU`, `DE`, `CN`, `JP`, `PTBR`) |
| `ui_lang` | Domyślny kod języka interfejsu z katalogu `cli_locales/` |
| `mirror_dir` | Lokalny folder, w którym przechowywane są pełne ścieżki do skopiowanych tłumaczeń. |
| `state_file` | Plik JSON przechowujący historię tłumaczeń i hasze ciągów źródłowych |
| `save_every` | Zapisuj postęp na dysk i twórz kopie zapasowe dla każdego N przetłumaczonych kluczy. |

---

## Użycie

### Tryb interaktywny

Najpierw uruchom `llama-server`, a następnie wykonaj:

```bash
python pz_translate.py
```

1. **Wybierz język interfejsu:** Wybierz spośród dostępnych języków w `cli_locales/` (domyślnie: `en`).
2. **Wybierz tryb:**
   - `1` — Tłumaczenie konkretnej ścieżki modyfikacji.
   - `2` — Przeskanuj wszystkie mody w ścieżce `mods_path`, wyświetl tabelę z liczbami znaków/liter, a następnie wprowadź numery modów (np. `1,3,5`, `1-4` lub `wszystkie`).
   - `3` — Zarządzaj zapisanym postępem (aktualizuj zmienione/nowe klucze, przetłumaczyć od nowa, przywrócić z `pz_translator_mods/`, lub usuwać tłumaczenia).
   - `4` — Zmień język interfejsu.
   - `0` — Wyjście.

### Argumenty wiersza poleceń

Można ominąć interaktywne menu, używając flag CLI (argumenty CLI nadpisują `config.json`):

| Flaga | Opis |
| ---
--- | ---
--- |
| `--config <ścieżka>` | Ścieżka do pliku `config.json` o niestandardowej konfiguracji |
| `--mode {1, 2, 3}` | `1` = pojedynczy mod, `2` = skanowanie katalogu, `3` = zarządzanie zapisanym postępem |
| `--path <ścieżka>` | Ścieżka do folderu z modami (Tryb 1) lub głównego folderu z modami (Tryb 2) |
| `--lang <code>` | Język docelowy jako kod folderu PZ (`RU`, `CN`, `PTBR`) lub kod ISO (`ru`, `zh`, `pt-BR`) |
| `--source-lang <code>` | Przeciążanie źródłowego folderu języka (domyślnie: `EN`) |
| `--host <host>` | Przeciąż `llamacpp_host` |
| `--port <port>` | Przeciąż `llamacpp_port` |
| `--ui-lang <code>` | Kod języka interfejsu (np. `en`, `ru`) |
| `--force` | Nadpisywanie istniejących tłumaczeń |

#### Przykłady

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

## Jak to działa

1. **Odkrywanie Modów:** Rekurencyjnie przeszukuje katalogi `Translate/<SOURCE_LANG>`, które zawierają pliki `.json`, i wyodrębnia nazwy modów z plików `mod.info` oraz struktur folderów Workshop (`mods/<ModName>/<Version>`).
2. **Porównywanie i szacowanie objętości:** Porównuje klucze w `EN/*.json` z istniejącymi plikami docelowymi (`<TARGET_LANG>/*.json`) oraz przechowywanymi hashami SHA-1 w pliku `pz_translator_state.json`. Tylko brakujące klucze lub klucze, których tekst źródłowy w języku angielskim uległ zmianie od ostatniego tłumaczenia, są kolejkowane.
3. **Tłumaczenie LLM:** Wysyła każdą ciąg znaków do `http://<host>:<port>/completion` używając formatowania rozmowy w TranslateGemma.
4. **Dwuwyjściowe:** Każde pole `save_every` (oraz po zakończeniu lub przy użyciu `Ctrl+C`), zapisuje poprawny JSON w formacie UTF-8 do:
   - Folder docelowy dla modyfikacji: `...\Translate\<LANG>\<file>.json`
   - Lokalny folder lustrzany: `pz_translator_mods\<pełna_ścieżka_bez_litery_dysku>\Translate\<JĘZYK>\<plik>.json`

---

## Uwagi i ograniczenia

- **Obsługiwany format:** Tylko pliki lokalizacyjne w formacie `.json` z gry Project Zomboid **Build 42.15+** są przetwarzane. Stare pliki lokalizacyjne w formacie `.txt` są ignorowane, ponieważ B42.15+ ich już nie ładuje.
- **Tryb wieloosobowy (`DoLuaChecksum`):** Ponieważ foldery `Translate` znajdują się wewnątrz `media/lua/shared/`, dodawanie plików tłumaczeń bezpośrednio do folderów Steam Workshop może powodować nieprawidłowe sumy kontrolne na serwerach wieloosobowych z `DoLuaChecksum=true`. Dla publicznych serwerów wieloosobowych, można albo zapakować odzwierciedlone pliki z `pz_translator_mods/` jako oddzielny mod zawierający tylko tłumaczenia, albo grać w trybie pojedynczym / na serwerach z `DoLuaChecksum=false`.
```
