# Traductor de mods para Project Zomboid

Una herramienta de línea de comandos para la localización de los mods de **Project Zomboid (versión 42.15 y superior)** utilizando un servidor `llama.cpp` local (`llama-server`) impulsado por **TranslateGemma**.

Escanea las carpetas del Workshop de Steam o las carpetas de mods locales en busca de archivos `Translate/EN/*.json`, estima el volumen de traducción (número de líneas y caracteres), traduce cadenas faltantes o actualizadas, valida las variables y las etiquetas de marcado de la interfaz de usuario, y crea una copia local de cada traducción generada para que pueda empaquetar fácilmente mods de traducción independientes o restaurar archivos después de las actualizaciones de Steam.

---

## Características

- **Soporte para JSON versión 42.15+:** Funciona con el formato de traducción moderno `.json` utilizado en Project Zomboid B42.15+ (los mods antiguos que solo utilizan el formato `.txt` se omiten de forma segura durante el escaneo).
- **Interfaz de terminal rica:** Tablas limpias y coloridas, insignias de estado y barras de progreso en tiempo real con el tiempo transcurrido/restante, utilizando la librería `rich`.
- **Interfaz de línea de comandos multilingüe (`i18n`):** Por defecto utiliza el idioma inglés y solicita al usuario que seleccione el idioma de la interfaz a partir de los archivos `cli_locales/*.json` durante el inicio interactivo.
- **3 Modos de funcionamiento:**
  - **Modo 1:** Traducir un único modo específico (o su carpeta `Translate` / `EN`).
  - **Modo 2:** Escanee todo el directorio de su taller, revise el estado de las traducciones y el volumen de caracteres por modificación, y seleccione las modificaciones utilizando números (`1,3,5`), rangos (`1-4`) o `all`.
  - **Modo 3:** Gestionar el progreso guardado – detectar actualizaciones de mods, traducir nuevas/modificadas/corruptas cadenas de texto, reescribir desde cero, restaurar desde una copia, eliminar de forma limpia los archivos generados, o ejecutar un informe de verificación de tokens de prueba.
- **Reemplazos y validación de formato (`token_rules.json`):** Extrae los reemplazos específicos de los mods (`{name}`, `%1`) y las etiquetas de formato de Project Zomboid (como `<LINE>`, `<RGB:...>`, `<IMAGE:...>`, etc.) utilizando reglas de expresiones regulares configurables, y verifica una coincidencia exacta después de la traducción. En caso de no coincidencia, intenta nuevamente con diferentes semillas (`max_retries`). Si todos los intentos fallan, mantiene la cadena original en inglés, marca el estado del mod como `EN/<LANG>`, y registra los detalles en `pz_translator_issues.log`.
- **Detección de actualizaciones y seguimiento del progreso:** Almacena los hashes SHA-1 únicos de las cadenas de texto originales en inglés para cada clave en el archivo `pz_translator_state.json`. Si se realiza una actualización en el Steam Workshop, solo las claves nuevas, modificadas o con errores se ponen en cola para la traducción.
- **Mirror local (`pz_translator_mods/`):** Guarda una copia de cada archivo traducido, conservando la estructura de directorios relativa (lo que facilita la creación de modificaciones independientes que solo contienen traducciones).
- **Seguro y resistente a fallos:**
  - Las traducciones de autores existentes (tanto modificaciones sin modificar como claves de traducción individuales que no se rastrean en `pz_translator_state.json`) nunca son analizadas por las reglas de token, modificadas ni reemplazadas.
  - Maneja el encabezado UTF-8, comas al final en archivos JSON modificados manualmente, y preserva el `$schema` y las cadenas vacías.
  - Guarda automáticamente el progreso periódicamente (`save_every`) y al presionar `Ctrl+C`.

---

## Requisitos

- **Python 3.9 o superior**
- **llama.cpp** (`llama-server`) ejecutando un modelo GGUF de **TranslateGemma** en el host/puerto configurado (por defecto: `http://127.0.0.1:8734`).
- Dependencias de Python:

```bash
pip install -r requirements.txt
```

---

## Configuración (`config.json`)

Al iniciar el script (o a través del archivo `config.json` incluido), utiliza la siguiente configuración:

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

| Clave | Descripción |
| --- | --- |
| `llamacpp_host` | Dirección del servidor donde se ejecuta `llama-server`. |
| `llamacpp_port` | Puerto de la aplicación `llama-server` que está ejecutando. |
| `mods_path` | Directorio raíz predeterminado escaneado en el modo 2 (por ejemplo, la carpeta `108600` del Workshop de Steam). |
| `default_source_lang` | Nombre de la carpeta de origen para la traducción (valor predeterminado: `EN`) |
| `default_target_lang` | Código de idioma predeterminado (por ejemplo, `RU`, `DE`, `CN`, `JP`, `PTBR`) |
| `ui_lang` | Código de idioma predeterminado del interfaz, ubicado en `cli_locales/` |
| `mirror_dir` | Carpeta local donde se almacenan copias completas de las traducciones generadas. |
| `state_file` | Archivo JSON que almacena el historial de traducciones y los hashes de las cadenas originales. |
| `token_rules_file` | Archivo JSON con reglas de expresiones regulares y opciones de reintento para la validación de marcadores/etiquetas. |
| `save_every` | Guardar el progreso en el disco y duplicar cada N claves traducidas. |

### Validación de tokens (`token_rules.json`)

Las reglas de expresiones regulares para proteger las variables dinámicas y las etiquetas de marcado de Project Zomboid están configuradas en el archivo `token_rules.json`:

| Clave | Descripción |
| --- | --- |
| `max_retries` | Número máximo de intentos de traducción con diferentes semillas cuando los tokens críticos no coinciden. |
| `retry_temperatures` | Programa de temperatura aplicado en cada intento de reintento (por ejemplo, `[0.2, 0.35, 0.5]`) |
| `issues_log` | Archivo de registro donde se registran las cadenas que no pasaron la validación después de todos los intentos, junto con su origen en inglés (`EN`) y los intentos fallidos. |
| `check_report` | Archivo de salida para el informe de inspección de tokens en modo 3 |
| `rules` | Conjunto de objetos de reglas de expresiones regulares (`name`, `pattern`, `enabled`, `critical`, `description`) |

Las reglas marcadas con `"critical": true` activan reintentos durante la traducción y registran las claves que necesitan ser re-traducidas durante las actualizaciones. Las reglas no críticas (`"critical": false`) solo se informan como advertencias en el informe de prueba.

---

## Uso

### Modo interactivo

Primero, inicie `llama-server`, y luego ejecute:

```bash
python pz_translate.py
```

1. **Seleccionar idioma de la interfaz:** Elija entre los idiomas disponibles en `cli_locales/` (por defecto: `en`).
2. **Modo de selección:**
   - `1` — Traducir una ruta de modificación específica.
   - `2` — Escanea todos los mods en `mods_path`, visualiza la tabla con el recuento de cadenas/caracteres, e introduce los números de los mods (por ejemplo, `1,3,5`, `1-4` o `all`).
   - `3` — Gestionar el progreso guardado (actualizar claves de tokens nuevas/modificadas/defectuosas, volver a traducir desde cero, restaurar desde `pz_translator_mods/`, eliminar traducciones o ejecutar un informe de verificación de tokens de prueba).
   - `4` — Cambiar el idioma de la interfaz.
   - `0` — Salir.

### Argumentos de la línea de comandos

Puede omitir el menú interactivo utilizando las opciones de línea de comandos (los argumentos de la línea de comandos anulan el archivo `config.json`):

| Banderola | Descripción |
| --- | --- |
| `--config <path>` | Ruta para crear un archivo `config.json` personalizado. |
| `--rules <path>` | Ruta para crear un archivo `token_rules.json` personalizado. |
| `--mode {1,2,3}` | `1` = modo individual, `2` = escanear el directorio, `3` = gestionar el progreso guardado |
| `--path <path>` | Ruta a la carpeta de mods (Modo 1) o a la carpeta raíz de los mods (Modo 2) |
| `--lang <code>` | Idioma de destino como código de carpeta PZ (`RU`, `CN`, `PTBR`) o código ISO (`ru`, `zh`, `pt-BR`) |
| `--source-lang <code>` | Sobrescribir la carpeta de idioma de origen (por defecto: `EN`) |
| `--host <host>` | Sobrescribir `llamacpp_host` |
| `--port <port>` | Sobrescribir `llamacpp_port` |
| `--ui-lang <code>` | Código de idioma de la interfaz (por ejemplo, `en`, `ru`) |
| `--force` | Sobrescribir las traducciones existentes |
| `--check` | Realice una verificación de tokens en todas las traducciones guardadas y escriba el archivo `pz_translator_check_report.txt`. |

#### Ejemplos

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

## Cómo funciona

1. **Descubrimiento de mods:** Busca de forma recursiva las `Translate/<SOURCE_LANG>` carpetas que contienen `.json` archivos y extrae los nombres de los mods de las estructuras de carpetas `mod.info` y Workshop (`mods/<ModName>/<Version>`).
2. **Estimación de diferencias y volumen:** Compara las claves en `EN/*.json` con los archivos objetivo existentes (`<TARGET_LANG>/*.json`), los hashes SHA-1 almacenados en `pz_translator_state.json`, y las reglas críticas de `token_rules.json`. Las claves faltantes, las claves cuyo texto original en inglés ha cambiado, y las claves rastreadas con marcadores/etiquetas rotas, se ponen en cola para ser traducidas; las traducciones preexistentes del autor se dejan sin modificar.
3. **Traducción y validación de LLM:** Envía cada cadena original completa a `http://<host>:<port>/completion` utilizando el formato de solicitud "TranslateGemma" estándar, y luego verifica los tokens críticos con la cadena original. En caso de discrepancia, intenta nuevamente con diferentes semillas hasta `max_retries`; si todos los intentos fallan, mantiene el texto en inglés, marca el estado de modificación como `EN/<LANG>`, y registra los detalles en `pz_translator_issues.log`.
4. **Salida Dual:** Cada vez que se utiliza la clave `save_every` (y al finalizar o con `Ctrl+C`), se escribe un JSON válido en UTF-8 en:
   - La carpeta de modificación objetivo: `...\Translate\<LANG>\<file>.json`
   - La carpeta local de espejos: `pz_translator_mods\<full_path_without_drive_letter>\Translate\<LANG>\<file>.json`

---

## Notas y limitaciones

- **Formato admitido:** Solo se procesan los archivos de localización `.json` de Project Zomboid **versión 42.15+**. Los archivos de traducción antiguos en formato `.txt` se ignoran, ya que la versión 42.15+ ya no los carga.
- **Multijugador (`DoLuaChecksum`):** Debido a que las carpetas `Translate` se encuentran dentro de `media/lua/shared/`, añadir archivos de traducción directamente dentro de las carpetas del Steam Workshop puede provocar inconsistencias en los checksum en los servidores multijugador con `DoLuaChecksum=true`. Para servidores multijugador públicos, ya sea empaquetar los archivos duplicados de `pz_translator_mods/` como un mod independiente dedicado únicamente a la traducción, o jugar en modo singleplayer / servidores con `DoLuaChecksum=false`.
