# Tłumacz modów dla gry Project Zomboid

Narzędzie wiersza poleceń do lokalizacji modów dla gry **Project Zomboid (wersja 42.15 i nowsze)**, wykorzystujące lokalny serwer `llama.cpp` (`llama-server`) z wykorzystaniem **TranslateGemma**.

Analizuje zawartość Steam Workshop lub lokalnych folderów z modami w poszukiwaniu plików `Translate/EN/*.json`, szacuje ilość tłumaczeń (liczba wierszy i znaków), tłumaczy brakujące lub zaktualizowane ciągi znaków, weryfikuje zmienne i znaczniki interfejsu użytkownika oraz tworzy lokalne kopie wszystkich wygenerowanych tłumaczeń, dzięki czemu można łatwo tworzyć samodzielne mody z tłumaczeniami lub przywracać pliki po aktualizacjach Steam.

---

## Cechy

- **Obsługa formatu JSON w wersji 42.15+:** Kompatybilność z nowoczesnym formatem `.json` używanym w Project Zomboid B42.15+ (starsze mody w formacie `.txt` są bezpiecznie pomijane podczas skanowania).
- **Bogaty interfejs terminala:** Czyste, kolorowe tabele, ikony statusu oraz dynamiczne paski postępu z czasem upływającym i pozostałym, wykorzystujące bibliotekę `rich`.
- **Wielojęzyczna linia poleceń (CLI) (`i18n`):** Domyślnie używa języka angielskiego i podczas interaktywnego uruchomienia pyta o wybranie języka interfejsu, korzystając z plików `cli_locales/*.json`.
- **3 tryby pracy:**
  - **Tryb 1:** Przetłumaczenie pojedynczego, określonego modułu (lub jego folderu `Translate` / `EN`).
  - **Tryb 2:** Przeskanuj cały katalog Twojego projektu, sprawdź status tłumaczenia oraz ilość znaków na mod, a następnie wybierz mody za pomocą numerów (`1,3,5`), zakresów (`1-4`) lub `all`.
  - **Tryb 3:** Zarządzanie zapisanym postępem – wykrywanie aktualizacji modyfikacji, tłumaczenie nowych/zmodyfikowanych/uszkodzonych ciągów znaków, ponowne tworzenie od początku, przywracanie z kopii zapasowej, czyste usuwanie generowanych plików, lub uruchamianie raportu z testowym sprawdzeniem ciągów znaków.
- **Wypełniacze i walidacja znaczników (`token_rules.json`):** Wyodrębnia wypełniacze modów (`{name}`, `%1`) oraz znaczniki RichText z Project Zomboid (`<LINE>`, `<RGB:...>`, `<IMAGE:...>`, itp.) za pomocą konfigurowalnych reguł wyrażeń regularnych i weryfikuje dokładne dopasowanie po tłumaczeniu. W przypadku niepasowania, próbuje ponownie z różnymi wartościami (`max_retries`). Jeśli wszystkie próby zawiodą, zachowuje oryginalny tekst w języku angielskim, oznaczając status modu jako `EN/<LANG>`, oraz zapisuje szczegóły w pliku `pz_translator_issues.log`.
- **Wykrywanie zmian i śledzenie postępów:** Przechowuje hasze SHA-1 dla poszczególnych kluczy w języku angielskim w pliku `pz_translator_state.json`. W przypadku aktualizacji w Steam Workshop, tylko nowe, zmodyfikowane lub uszkodzone klucze są ustawiane do przetłumaczenia.
- **Lokalny Mod (`pz_translator_mods/`):** Zapisuje kopię każdego przetłumaczonego pliku, zachowując strukturę katalogów (co ułatwia tworzenie samodzielnych modów, które zawierają tylko tłumaczenia).
- **Bezpieczne i odporne na awarie:**
  - Istniejące tłumaczenia autorów (zarówno nieprzetworzone mody, jak i pojedyncze tłumaczenia autorów, które nie są śledzone w pliku `pz_translator_state.json`) nigdy nie są analizowane przez reguły tokenowe, modyfikowane ani zastępowane.
  - Obsługuje nagłówek UTF-8, przecinki na końcu plików JSON edytowanych ręcznie, oraz zachowuje `$schema` i puste ciągi znaków.
  - Automatyczne zapisywanie postępów co jakiś czas (`save_every`) oraz po naciśnięciu klawiszy `Ctrl+C`.

---

## Wymagania

- **Python 3.9+**
- **llama.cpp** (`llama-server`) uruchamiający model **TranslateGemma** w formacie GGUF na skonfigurowanym serwerze/porcie (domyślnie: `http://127.0.0.1:8734`).
- Zależności Pythona:

```bash
pip install -r requirements.txt
```

---

## Konfiguracja (`config.json`)

Podczas pierwszego uruchomienia (lub poprzez plik `config.json` dołączony do programu), skrypt wykorzystuje następujące ustawienia:

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

| Kluczowe | Opis |
| --- | --- |
| `llamacpp_host` | Adres IP serwera, na którym działa `llama-server`. |
| `llamacpp_port` | Port, na którym działa serwer `llama-server`. |
| `mods_path` | Domyślny katalog główny skanowany w trybie 2 (np. folder `108600` w Steam Workshop). |
| `default_source_lang` | Nazwa folderu z tłumaczeniami (domyślnie: `EN`) |
| `default_target_lang` | Domyślny kod języka docelowego (np. `RU`, `DE`, `CN`, `JP`, `PTBR`) |
| `ui_lang` | Domyślna kod języka interfejsu z katalogu `cli_locales/` |
| `mirror_dir` | Lokalny folder, w którym przechowywane są pełne ścieżki do skopiowanych tłumaczeń. |
| `state_file` | Plik JSON przechowujący historię tłumaczeń oraz hasze oryginalnych ciągów znaków. |
| `token_rules_file` | Plik JSON zawierający reguły wyrażeń regularnych i ustawienia dotyczące ponownej próby weryfikacji nazw/tagów. |
| `save_every` | Zapisuj postęp na dysk i tworz kopie każdego N-tego przetłumaczonego klucza. |

### Walidacja tokenów (`token_rules.json`)

Reguły wyrażeń regularnych służące do ochrony zmiennych dynamicznych oraz znaczników projektu "Project Zomboid" są skonfigurowane w pliku `token_rules.json`:

| Kluczowe | Opis |
| --- | --- |
| `max_retries` | Maksymalna liczba prób tłumaczenia z wykorzystaniem różnych wartości początkowych, gdy kluczowe słowa nie pasują do siebie. |
| `retry_temperatures` | Harmonogram temperatur stosowany w każdym próbie ponownego uruchomienia (np. `[0.2, 0.35, 0.5]`) |
| `issues_log` | Plik logu, w którym zapisywane są łańcuchy znaków, które nie przeszły walidacji po wszystkich próbach, wraz z ich źródłem w języku angielskim (`EN`) i informacją o nieudanych próbach. |
| `check_report` | Plik wyjściowy dla raportu inspekcji tokenów w trybie 3 |
| `rules` | Tablica obiektów reguł wyrażeń regularnych (`name`, `pattern`, `enabled`, `critical`, `description`) |

Reguły oznaczone jako `"critical": true` powodują ponowne próby tłumaczenia oraz rejestrowanie kluczy, które wymagają ponownego tłumaczenia podczas aktualizacji. Reguły niekrytyczne (`"critical": false`) są jedynie zgłaszane jako ostrzeżenia w raporcie testowym.

---

## Zastosowanie

### Tryb interaktywny

Najpierw uruchom `llama-server`, a następnie wykonaj:

```bash
python pz_translate.py
```

1. **Wybierz język interfejsu:** Wybierz spośród dostępnych języków w katalogu `cli_locales/` (domyślnie: `en`).
2. **Tryb wyboru:**
   - `1` – Przetłumaczenie konkretnej ścieżki modu.
   - `2` – Przeskanuj wszystkie mody w `mods_path`, wyświetl tabelę z liczbą znaków w każdej modyfikacji, a następnie wprowadź numery modów (np. `1,3,5`, `1-4` lub `all`).
   - `3` – Zarządzanie zapisanym postępem (aktualizacja kluczy nowych/zmodyfikowanych/uszkodzonych, ponowne tłumaczenie od początku, przywracanie z folderu `pz_translator_mods/`, usuwanie tłumaczeń, lub uruchamianie raportu sprawdzającego klucze bez faktycznego tłumaczenia).
   - `4` – Zmiana języka interfejsu.
   - `0` – Wyjście.

### Argumenty przekazywane z wiersza poleceń

Można ominąć interaktywne menu, używając flag CLI (argumenty CLI mają priorytet nad plikiem `config.json`):

| Flaga | Opis |
| --- | --- |
| `--config <path>` | Ścieżka do pliku `config.json` o niestandardowej strukturze |
| `--rules <path>` | Droga do tworzenia własnego pliku `token_rules.json` |
| `--mode {1,2,3}` | `1` = pojedynczy mod, `2` = przeszukiwanie katalogu, `3` = zarządzanie zapisanym postępem |
| `--path <path>` | Ścieżka do folderu z modami (tryb 1) lub głównego folderu z modami (tryb 2) |
| `--lang <code>` | Język docelowy, kod folderu w PZ (`RU`, `CN`, `PTBR`) lub kod ISO (`ru`, `zh`, `pt-BR`) |
| `--source-lang <code>` | Przeciążanie domyślnego folderu języka źródłowego (domyślnie: `EN`) |
| `--host <host>` | Nadpisać wartość `llamacpp_host` |
| `--port <port>` | Nadpisać wartość `llamacpp_port` |
| `--ui-lang <code>` | Kod języka interfejsu (np. `en`, `ru`) |
| `--force` | Nadpisywanie istniejących tłumaczeń |
| `--check` | Przeprowadź testowe sprawdzanie tokenów dla wszystkich zapisanych tłumaczeń i zapisz wynik w pliku `pz_translator_check_report.txt`. |

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

# Run a dry-run token check on all saved translations without calling the LLM
python pz_translate.py --mode 3 --check
```

---

## Jak to działa

1. **Wykrywanie modów:** Rekurencyjnie przeszukuje `Translate/<SOURCE_LANG>` katalogów, w których znajdują się `.json` plików, i wyodrębnia nazwy modów z struktur katalogów `mod.info` i Workshop (`mods/<ModName>/<Version>`).
2. **Porównywanie i szacowanie ilości:** Porównuje klucze w plikach `EN/*.json` z istniejącymi plikami docelowymi (`<TARGET_LANG>/*.json`), a także z hashami SHA-1 przechowywanymi w pliku `pz_translator_state.json` oraz kluczowymi zasadami z pliku `token_rules.json`. Klucze, których nie znaleziono, klucze, dla których tekst źródłowy w języku angielskim uległ zmianie, oraz śledzone klucze z uszkodzonymi znacznikami/tagami, są umieszczane w kolejce do tłumaczenia; istniejące tłumaczenia autorów pozostają bez zmian.
3. **Tłumaczenie i weryfikacja LLM:** Wysyła każdą pełną oryginalną sekwencję do `http://<host>:<port>/completion` przy użyciu standardowego formatu zapytania TranslateGemma, a następnie sprawdza kluczowe słowa w odniesieniu do oryginalnej sekwencji. W przypadku niezgodności, próbuje ponownie z różnymi wartościami początkowymi do `max_retries`; jeśli wszystkie próby zawiodą, zachowuje oryginalny tekst w języku angielskim, oznaczając status modyfikacji jako `EN/<LANG>`, i zapisuje szczegóły w `pz_translator_issues.log`.
4. **Dwukierunkowe zapisywanie:** Każdy klucz `save_every` (oraz po zakończeniu działania lub nacisnięciu `Ctrl+C`) zapisuje poprawny JSON w formacie UTF-8 do:
   - Określona ścieżka do folderu z modami: `...\Translate\<LANG>\<file>.json`
   - Lokalny folder lustrzany: `pz_translator_mods\<full_path_without_drive_letter>\Translate\<LANG>\<file>.json`

---

## Uwagi i ograniczenia

- **Obsługiwany format:** Tylko pliki lokalizacyjne w formacie `.json` z gry Project Zomboid **w wersji 42.15+** są przetwarzane. Stare pliki lokalizacyjne w formacie `.txt` są ignorowane, ponieważ wersja 42.15+ ich nie odczytuje.
- **Tryb wieloosobowy (`DoLuaChecksum`):** Ponieważ foldery `Translate` znajdują się wewnątrz `media/lua/shared/`, dodawanie plików tłumaczeniowych bezpośrednio do folderów w Steam Workshop może powodować nieprawidłowe sumy kontrolne na serwerach wieloosobowych z `DoLuaChecksum=true`. W przypadku publicznych serwerów wieloosobowych, można albo zapakować odzwierciedlone pliki z `pz_translator_mods/` jako oddzielny mod tylko do tłumaczeń, albo grać w trybie pojedynczym / na serwerach z `DoLuaChecksum=false`.
