# Traductor de mods para Project Zomboid

Una herramienta de línea de comandos para la localización de los mods de **Project Zomboid (versión 42.15+)** utilizando un servidor `llama.cpp` local (`llama-server`) impulsado por **TranslateGemma**.

Escanea el Workshop de Steam o las carpetas de mods locales en busca de archivos `Translate/EN/*.json`, estima el volumen de traducción (número de líneas y caracteres), traduce cadenas faltantes o actualizadas, y crea una copia local de cada traducción generada para que puedas empaquetar fácilmente mods de traducción independientes o restaurar archivos después de las actualizaciones de Steam.

---

## Características

- **Soporte JSON para la versión 42.15+:** Funciona con el formato de traducción moderno `.json` utilizado en Project Zomboid B42.15+ (los mods antiguos que solo utilizan `.txt` se omiten de forma segura durante las comprobaciones).
- **Interfaz de terminal rica:** Tablas limpias y coloridas, insignias de estado y barras de progreso en tiempo real con tiempo transcurrido/restante, utilizando la librería `rich`.
- **Interfaz de línea de comandos multilingüe (`i18n`):** Por defecto, utiliza el idioma inglés y solicita al usuario que seleccione el idioma de la interfaz a partir de `cli_locales/*.json` durante el inicio interactivo.
- **3 Modos de funcionamiento:**
  - **Modo 1:** Traducir un único mod especificado (o su carpeta `Translate` / `EN`).
  - **Modo 2:** Escanea todo el directorio de su taller, inspeccione el estado de las traducciones y el volumen de caracteres por mod, y seleccione los mods por números (`1,3,5`), rangos (`1-4`) o `todos`.
  - **Modo 3:** Gestionar el progreso guardado — detectar actualizaciones de mods, traducir solo cadenas nuevas/modificadas, sobrescribir desde cero, restaurar desde un espejo, o eliminar de forma limpia los archivos generados.
- **Detección de actualizaciones y seguimiento del progreso:** Almacena los hashes SHA-1 únicos de las cadenas de texto en inglés originales para cada clave en `pz_translator_state.json`. Si una actualización se instala desde la Steam Workshop, solo las nuevas claves o las claves modificadas en inglés se añaden a la cola para la traducción.
- **Espacio de espejo local (`pz_translator_mods/`):** Guarda una copia de cada archivo traducido, conservando la estructura de directorios relativa (lo que facilita la creación de modificaciones independientes dedicadas únicamente a la traducción).
- **Seguro y resistente a fallos:**
  - Las traducciones existentes del autor con `0` claves pendientes nunca se modifican, se sobrescriben ni se rastrean.
  - Maneja el encabezado UTF-8, comas finales en archivos JSON de mods editados manualmente, y preserva `$schema` y cadenas vacías.
  - Guarda automáticamente el progreso periódicamente (`save_every`) y al presionar `Ctrl+C`.

---

## Requisitos

- **Python 3.9+**
- **llama.cpp** (`llama-server`) ejecutando un modelo **TranslateGemma** GGUF en el host/puerto configurado (predeterminado: `http://127.0.0.1:8734`).
- Dependencias de Python:

```bash
pip install -r requirements.txt
```

---

## Configuración (`config.json`)

Al iniciar (o a través del archivo `config.json` incluido), el script utiliza la siguiente configuración:

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

| Clave | Descripción |
| --- | --- |
| `llamacpp_host` | Dirección del servidor donde se está ejecutando `llama-server` |
| `llamacpp_port` | Puerto de tu servidor `llama-server` en ejecución |
| `mods_path` | Directorio raíz predeterminado escaneado en el Modo 2 (por ejemplo, la carpeta `108600` del Workshop de Steam) |
| `default_source_lang` | Nombre de la carpeta de traducción original (predeterminado: `EN`) |
| `default_target_lang` | Código de idioma predeterminado (por ejemplo, `RU`, `DE`, `CN`, `JP`, `PTBR`) |
| `ui_lang` | Código de idioma de la interfaz predeterminado, proveniente de `cli_locales/` |
| `mirror_dir` | Carpeta local donde se almacenan copias completas de las traducciones generadas. |
| `state_file` | Archivo JSON que almacena el historial de traducciones y los hashes de las cadenas originales. |
| `guardar_cada` | Guardar el progreso en el disco y crear una copia de seguridad de cada N claves traducidas. |

---

## Uso

### Modo interactivo

Comience con `llama-server` primero, y luego ejecute:

```bash
python pz_translate.py
```

1. **Seleccionar idioma de la interfaz:** Elija entre los idiomas disponibles en `cli_locales/` (predeterminado: `en`).
2. **Seleccionar modo:**
   - `1` — Traducir una ruta de mod específica.
   - `2` — Escanear todos los mods en la ruta `mods_path`, mostrar la tabla con el recuento de cadenas/caracteres, e introducir los números de los mods (por ejemplo, `1,3,5`, `1-4`, o `todos`).
   - `3` — Gestionar el progreso guardado (actualizar las claves modificadas/nuevas, volver a traducir desde cero, restaurar desde `pz_translator_mods/`, o eliminar las traducciones).
   - `4` — Cambiar el idioma de la interfaz.
   - `0` — Salir.

### Argumentos de línea de comandos

Puede omitir el menú interactivo utilizando las opciones de la línea de comandos (los argumentos de la línea de comandos anulan `config.json`):

| Banderas | Descripción |
| --- | --- |
| `--config <ruta>` | Ruta a un archivo `config.json` personalizado |
| `--mode {1, 2, 3}` | `1` = modo único, `2` = escanear directorio, `3` = gestionar el progreso guardado |
| `--path <ruta>` | Ruta a la carpeta de mods (Modo 1) o a la carpeta raíz de los mods (Modo 2) |
| `--lang <code>` | Idioma de destino como código de carpeta PZ (`RU`, `CN`, `PTBR`) o código ISO (`ru`, `zh`, `pt-BR`) |
| `--source-lang <code>` | Sobrescribir la carpeta de idioma de origen (predeterminado: `EN`) |
| `--host <host>` | Sobrescribir `llamacpp_host` |
| `--port <puerto>` | Sobrescribir `llamacpp_port` |
| `--ui-lang <code>` | Código de idioma de la interfaz (p. ej., `en`, `ru`) |
| `--force` | Sobrescribir las traducciones existentes |

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
```

---

## Cómo funciona

1. **Descubrimiento de Mods:** Busca recursivamente directorios `Translate/<SOURCE_LANG>` que contengan archivos `.json` y extrae los nombres de los mods de los archivos `mod.info` y las estructuras de carpetas de la Workshop (`mods/<ModName>/<Version>`).
2. **Estimación de diferencias y volumen:** Compara las claves en `EN/*.json` con los archivos objetivo existentes (`<TARGET_LANG>/*.json`) y los hashes SHA-1 almacenados en `pz_translator_state.json`. Solo se añaden a la cola las claves que faltan o las claves cuyo texto fuente en inglés ha cambiado desde la última traducción.
3. **Traducción de LLM:** Envía cada cadena a `http://<host>:<port>/completion` utilizando el formato de "turno de chat" de TranslateGemma.
4. **Salida Dual:** Cada clave `save_every` (y al finalizar o con `Ctrl+C`), escribe JSON UTF-8 válido en:
   - La carpeta de destino para el módulo: `...\Translate\<LANG>\<file>.json`
   - El directorio de espejo local: `pz_translator_mods\<ruta_completa_sin_letra_de_unidad>\Translate\<LANG>\<archivo>.json`

---

## Notas y limitaciones

- **Formato admitido:** Solo se procesan los archivos de localización `.json` de Project Zomboid **versión 42.15+**. Los archivos de traducción antiguos `.txt` se ignoran porque la versión B42.15+ ya no los carga.
- **Multijugador (`DoLuaChecksum`):** Debido a que las carpetas `Translate` se encuentran dentro de `media/lua/shared/`, añadir archivos de traducción directamente dentro de las carpetas del Steam Workshop puede provocar inconsistencias en los checksum en los servidores multijugador con `DoLuaChecksum=true`. Para servidores multijugador públicos, ya sea empaquetar los archivos espejo de `pz_translator_mods/` como un mod separado dedicado únicamente a la traducción, o jugar en modo singleplayer / servidores con `DoLuaChecksum=false`.
```
