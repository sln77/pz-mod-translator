# Traducteur de mods pour Project Zomboid

Un outil en ligne de commande pour la localisation des mods de **Project Zomboid (version 42.15+)** en utilisant un serveur `llama.cpp` local (`llama-server`) alimenté par **TranslateGemma**.

Il scanne le Steam Workshop ou les dossiers de mods locaux à la recherche de fichiers `Translate/EN/*.json`, estime le volume de traduction (nombre de lignes et de caractères), traduit les chaînes manquantes ou mises à jour, et crée une copie locale de chaque traduction générée, ce qui vous permet de facilement créer des mods de traduction autonomes ou de restaurer les fichiers après les mises à jour de Steam.

---

## Fonctionnalités

- **Support JSON pour la version 42.15+ :** Fonctionne avec le format de traduction moderne `.json` utilisé dans Project Zomboid 42.15+ (les mods existants uniquement au format `.txt` sont ignorés en toute sécurité lors des analyses).
- **Interface de terminal riche :** Tables colorées propres, badges d'état et barres de progression en direct avec le temps écoulé/restant, grâce à la bibliothèque `rich`.
- **Interface en plusieurs langues (CLI) (`i18n`):** Par défaut, utilise l'anglais et propose de sélectionner la langue de l'interface à partir de `cli_locales/*.json` au démarrage interactif.
- **3 Modes de fonctionnement:**
  - **Mode 1 :** Traduire un seul mod spécifié (ou son dossier `Translate` / `EN`).
  - **Mode 2 :** Scannez l'intégralité de votre répertoire de Workshop, vérifiez l'état de traduction et le volume de caractères par mod, et sélectionnez les mods par numéro (`1,3,5`), par plage (`1-4`), ou par `tout`.
  - **Mode 3 :** Gérer les progrès sauvegardés — détecter les mises à jour du mod, traduire uniquement les chaînes de caractères nouvelles/modifiées, remplacer complètement, restaurer à partir d'un miroir, ou supprimer proprement les fichiers générés.
- **Détection des mises à jour et suivi de l'avancement :** Stocke les hachages SHA-1 par clé des chaînes anglaises sources dans `pz_translator_state.json`. Si une mise à jour est installée via le Steam Workshop, seules les nouvelles clés anglaises ou modifiées sont ajoutées à la file d'attente pour la traduction.
- **Mirror local (`pz_translator_mods/`):** Conserve une copie de chaque fichier traduit, en préservant l'arborescence des répertoires relative (ce qui facilite la création de mods de traduction autonomes).
- **Sécurisé et résistant aux pannes:**
  - Les traductions existantes de l'auteur avec `0` clés en attente ne sont jamais modifiées, écrasées ou suivies.
  - Gère le BOM UTF-8, les virgules de fin dans les fichiers JSON modifiés manuellement, et préserve `$schema` et les chaînes vides.
  - Enregistre automatiquement les progrès périodiquement (`save_every`) et lors de la combinaison de touches `Ctrl+C`.

---

## Exigences

- **Python 3.9+**
- **llama.cpp** (`llama-server`) exécutant un modèle **TranslateGemma** GGUF sur l'hôte/port configuré (par défaut : `http://127.0.0.1:8734`).
- Dépendances Python:

```bash
pip install -r requirements.txt
```

---

## Configuration (`config.json`)

Lors de la première exécution (ou via le fichier `config.json` fourni), le script utilise les paramètres suivants :

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

| Clé | Description |
| ---
Ce document décrit... | ---
Ce document décrit... |
| `llamacpp_host` | Adresse IP de votre serveur `llama-server` en cours d'exécution |
| `llamacpp_port` | Port de votre serveur `llama-server` en cours d'exécution |
| `mods_path` | Répertoire racine par défaut analysé en mode 2 (par exemple, le dossier `108600` de Steam Workshop) |
| `default_source_lang` | Nom du dossier de traduction source (par défaut : `EN`) |
| `default_target_lang` | Code de langue cible par défaut (par exemple, `RU`, `DE`, `CN`, `JP`, `PTBR`) |
| `ui_lang` | Code de langue par défaut de l'interface, provenant du répertoire `cli_locales/` |
| `mirror_dir` | Dossier local où sont stockées les copies complètes des traductions générées, avec le chemin complet. |
| `state_file` | Fichier JSON stockant l'historique des traductions et les hachages des chaînes source |
| `save_every` | Sauvegarder la progression sur le disque et créer une copie de sauvegarde de chaque N clés traduites. |

---

## Utilisation

### Mode interactif

Lancez `llama-server` en premier, puis exécutez :

```bash
python pz_translate.py
```

1. **Sélectionner la langue de l'interface :** Choisissez parmi les langues disponibles dans `cli_locales/` (par défaut : `en`).
2. **Mode de sélection :**
   - `1` — Traduire un chemin de mod spécifique.
   - `2` — Scanner tous les mods dans le dossier `mods_path`, afficher le tableau avec le nombre de chaînes/caractères, et saisir les numéros de mod (par exemple, `1,3,5`, `1-4`, ou `tous`).
   - `3` — Gérer les progrès sauvegardés (mettre à jour les clés modifiées/nouvelles, recommencer la traduction, restaurer à partir de `pz_translator_mods/`, ou supprimer les traductions).
   - `4` — Changer la langue de l'interface.
   - `0` — Quitter.

### Arguments de ligne de commande

Vous pouvez contourner le menu interactif en utilisant les options de ligne de commande (les arguments de la ligne de commande remplacent `config.json`):

| Drapeau | Description |
| ---
Ce document décrit... | ---
Ce document décrit... |
| `--config <chemin>` | Chemin vers un fichier `config.json` personnalisé |
| `--mode {1, 2, 3}` | `1` = modification unique, `2` = scanner de répertoire, `3` = gestion des progrès sauvegardés |
| `--path <chemin>` | Chemin vers un dossier de mod (Mode 1) ou vers le dossier racine des mods (Mode 2) |
| `--lang <code>` | Langue cible sous forme de code de dossier PZ (`RU`, `CN`, `PTBR`) ou de code ISO (`ru`, `zh`, `pt-BR`) |
| `--source-lang <code>` | Définir le dossier de la langue source (par défaut : `EN`) |
| `--host <hôte>` | Dépasser `llamacpp_host` |
| `--port <port>` | Dépasser `llamacpp_port` |
| `--ui-lang <code>` | Code de langue de l'interface (par exemple, `en`, `ru`) |
| `--force` | Écraser les traductions existantes |

#### Exemples

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

## Comment ça marche

1. **Découverte des mods :** Recherche récursive des répertoires `Translate/<SOURCE_LANG>` contenant des fichiers `.json` et extraction des noms de mods à partir des fichiers `mod.info` et des structures de dossiers du Workshop (`mods/<ModName>/<Version>`).
2. **Comparaison et estimation du volume :** Compare les clés dans `EN/*.json` avec les fichiers cibles existants (`<LANGUE_CIBLE>/*.json`) et les hachages SHA-1 stockés dans `pz_translator_state.json`. Seules les clés manquantes ou les clés dont le texte source anglais a été modifié depuis la dernière traduction sont ajoutées à la file d'attente.
3. **Traduction LLM :** Envoie chaque chaîne à `http://<hôte>:<port>/completion` en utilisant le formatage de la conversation TranslateGemma.
4. **Sortie Double :** Chaque clé `save_every` (et lors de la fin ou avec `Ctrl+C`), écrit un JSON UTF-8 valide vers :
   - Le dossier de destination pour le module : `...\Translate\<LANG>\<file>.json`
   - Le dossier de miroir local : `pz_translator_mods\<chemin_complet_sans_lettre_de_disque>\Translate\<LANG>\<fichier>.json`

---

## Notes et limitations

- **Format pris en charge :** Seuls les fichiers de localisation `.json` de Project Zomboid **version 42.15+** sont traités. Les anciens fichiers de traduction `.txt` sont ignorés car la version B42.15+ ne les charge plus.
- **Multijoueur (`DoLuaChecksum`):** Puisque les dossiers `Translate` se trouvent à l'intérieur de `media/lua/shared/`, l'ajout direct de fichiers de traduction dans les dossiers du Steam Workshop peut entraîner des incohérences de checksum sur les serveurs multijoueurs avec `DoLuaChecksum=true`. Pour les serveurs multijoueurs publics, soit regrouper les fichiers miroirs de `pz_translator_mods/` sous forme d'un mod de traduction séparé, soit jouer en mode solo / sur des serveurs avec `DoLuaChecksum=false`.
```
