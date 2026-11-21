# Traducteur de mods pour Project Zomboid

Un outil en ligne de commande pour localiser les mods de **Project Zomboid (version 42.15 et supérieure)** en utilisant un serveur `llama.cpp` local (`llama-server`), alimenté par **TranslateGemma**.

Il scanne les dossiers du Steam Workshop ou locaux à la recherche de fichiers `Translate/EN/*.json`, estime le volume de traduction (nombre de lignes et de caractères), traduit les chaînes manquantes ou mises à jour, valide les variables et les balises de mise en forme de l'interface utilisateur, et crée une copie locale de chaque traduction générée, ce qui vous permet de créer facilement des mods de traduction autonomes ou de restaurer les fichiers après les mises à jour de Steam.

---

## Caractéristiques

- **Prise en charge du format JSON 42.15+ :** Fonctionne avec le format de traduction moderne `.json` utilisé dans Project Zomboid B42.15+ (les mods existants uniquement au format `.txt` sont ignorés en toute sécurité lors des analyses).
- **Interface de terminal riche :** Tables colorées et propres, badges d'état, et barres de progression en direct avec le temps écoulé/restant, grâce à la bibliothèque `rich`.
- **Interface en plusieurs langues (CLI) (`i18n`):** Par défaut, l'interface est en anglais, et l'utilisateur est invité à choisir la langue de l'interface à partir des fichiers `cli_locales/*.json` lors du démarrage interactif.
- **3 Modes de fonctionnement :**
  - **Mode 1 :** Traduire un seul mod spécifié (ou son dossier `Translate` / `EN`).
  - **Mode 2 :** Scannez l'intégralité du répertoire de votre atelier, vérifiez l'état de traduction et le volume de caractères par mod, et sélectionnez les mods en utilisant les numéros (`1,3,5`), les plages (`1-4`), ou `all`.
  - **Mode 3 :** Gérer les progrès sauvegardés – détecter les mises à jour du mod, traduire les nouvelles chaînes de caractères, remplacer les chaînes existantes, repartir de zéro, restaurer à partir d'une copie, supprimer proprement les fichiers générés, ou exécuter un rapport de vérification des chaînes de caractères sans application.
- **Identification des éléments et validation de la mise en forme (`token_rules.json`):** Extrait les éléments personnalisés du mod (`{name}`, `%1`) et les balises RichText de Project Zomboid (`<LINE>`, `<RGB:...>`, `<IMAGE:...>`, etc.) en utilisant des règles d'expressions régulières configurables, et vérifie une correspondance exacte après la traduction. En cas de non-correspondance, tente à nouveau avec différentes valeurs (`max_retries`). Si toutes les tentatives échouent, conserve la chaîne d'origine en anglais, indique le statut du mod comme `EN/<LANG>`, et enregistre les détails dans le fichier `pz_translator_issues.log`.
- **Détection des mises à jour et suivi de l'avancement :** Le système stocke les hachages SHA-1 uniques pour chaque chaîne en anglais dans le fichier `pz_translator_state.json`. Si une mise à jour est publiée sur le Steam Workshop, seules les clés nouvellement ajoutées, modifiées ou contenant des erreurs sont ajoutées à la file d'attente pour la traduction.
- **Mirror local (`pz_translator_mods/`):** Conserve une copie de chaque fichier traduit, tout en préservant la structure de répertoires relative (ce qui facilite la création de modifications spécifiques à la traduction).
- **Sécurité et résistance aux pannes :**
  - Les traductions existantes (tant les modifications non modifiées que les traductions individuelles qui ne sont pas suivies dans le fichier `pz_translator_state.json`) ne sont jamais analysées par les règles de token, ni modifiées ni écrasées.
  - Gère le BOM UTF-8, les virgules de fin dans les fichiers JSON modifiés manuellement, et préserve les éléments `$schema` et les chaînes vides.
  - Les sauvegardes automatiques sont effectuées périodiquement (`save_every`) et lorsque l'on appuie sur `Ctrl+C`.

---

## Exigences

- **Python 3.9 et versions ultérieures**
- **llama.cpp** (`llama-server`) exécutant un modèle GGUF de **TranslateGemma** sur l'hôte/le port configuré (par défaut : `http://127.0.0.1:8734`).
- Dépendances Python :

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
    "token_rules_file": "token_rules.json",
    "save_every": 20
}
```

| Clé | Description |
| --- | --- |
| `llamacpp_host` | Adresse IP ou nom d'hôte de votre serveur `llama-server` |
| `llamacpp_port` | Démarrez votre serveur `llama-server`. |
| `mods_path` | Répertoire racine par défaut analysé en mode 2 (par exemple, le dossier `108600` de la boutique Steam) |
| `default_source_lang` | Nom du dossier de traduction source (par défaut : `EN`) |
| `default_target_lang` | Code de langue cible par défaut (par exemple, `RU`, `DE`, `CN`, `JP`, `PTBR`) |
| `ui_lang` | Code de langue par défaut de l'interface, provenant du répertoire `cli_locales/` |
| `mirror_dir` | Dossier local où sont stockées les copies complètes des traductions générées. |
| `state_file` | Fichier JSON contenant l'historique des traductions et les hachages des chaînes source. |
| `token_rules_file` | Fichier JSON contenant des règles de régularité et des paramètres de relecture pour la validation des espaces réservés/balises. |
| `save_every` | Enregistrer la progression sur le disque et créer une copie de sauvegarde de chaque N clés traduites. |

### Validation des jetons (`token_rules.json`)

Les règles de regex pour protéger les variables dynamiques et les balises de formatage de Project Zomboid sont configurées dans le fichier `token_rules.json`:

| Clé | Description |
| --- | --- |
| `max_retries` | Nombre maximal d'essais de traduction avec différentes valeurs de départ lorsque les tokens critiques ne correspondent pas. |
| `retry_temperatures` | Calendrier de température appliqué à chaque tentative de relance (par exemple, `[0.2, 0.35, 0.5]`) |
| `issues_log` | Fichier de logs où les chaînes de caractères qui n'ont pas réussi la validation après toutes les tentatives sont enregistrées, avec leur source en anglais (`EN`) et les tentatives infructueuses. |
| `check_report` | Fichier de sortie pour le rapport d'inspection des jetons en mode 3 |
| `rules` | Tableau d'objets de règles d'expression régulière (`name`, `pattern`, `enabled`, `critical`, `description`) |

Les règles marquées avec `"critical": true` déclenchent des tentatives de traduction supplémentaires et enregistrent les clés à ré-traduire lors des mises à jour. Les règles non critiques (`"critical": false`) ne sont signalées que sous forme d'avertissements dans le rapport de vérification préliminaire.

---

## Utilisation

### Mode interactif

Commencez par lancer `llama-server`, puis exécutez :

```bash
python pz_translate.py
```

1. **Sélectionner la langue de l'interface :** Choisissez parmi les langues disponibles dans le répertoire `cli_locales/` (par défaut : `en`).
2. **Mode sélectionné :**
   - `1` — Traduire un chemin de modification spécifique.
   - `2` — Scannez tous les mods dans `mods_path`, affichez le tableau avec le nombre de chaînes et de caractères, et entrez les numéros de mod (par exemple, `1,3,5`, `1-4` ou `all`).
   - `3` — Gérer les progrès sauvegardés (mettre à jour les clés de nouveaux/modifiés/corrompus, recommencer la traduction, restaurer à partir de `pz_translator_mods/`, supprimer les traductions, ou exécuter un rapport de vérification des clés).
   - `4` – Modifier la langue de l'interface.
   - `0` — Quitter.

### Arguments de ligne de commande

Vous pouvez contourner le menu interactif en utilisant des options de ligne de commande (les arguments de la ligne de commande remplacent le fichier `config.json`):

| Drapeau | Description |
| --- | --- |
| `--config <path>` | Chemin vers un fichier `config.json` personnalisé |
| `--rules <path>` | Chemin vers un fichier `token_rules.json` personnalisé |
| `--mode {1,2,3}` | `1` = mode unique, `2` = parcourir le répertoire, `3` = gérer les progrès sauvegardés |
| `--path <path>` | Chemin vers le dossier des modifications (Mode 1) ou vers le dossier racine des modifications (Mode 2) |
| `--lang <code>` | Langue cible sous forme de code de dossier PZ (`RU`, `CN`, `PTBR`) ou de code ISO (`ru`, `zh`, `pt-BR`) |
| `--source-lang <code>` | Définir le dossier de la langue source (par défaut : `EN`) |
| `--host <host>` | Dépasser `llamacpp_host` |
| `--port <port>` | Dépasser `llamacpp_port` |
| `--ui-lang <code>` | Code de langue de l'interface (par exemple, `en`, `ru`) |
| `--force` | Écraser les traductions existantes |
| `--check` | Effectuez une vérification des tokens sur toutes les traductions enregistrées, puis enregistrez les résultats dans un fichier nommé `pz_translator_check_report.txt`. |

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

# Run a dry-run token check on all saved translations without calling the LLM
python pz_translate.py --mode 3 --check
```

---

## Fonctionnement

1. **Découverte des modifications :** Recherche récursivement les `Translate/<SOURCE_LANG>` dossiers contenant `.json` fichiers et extrait les noms de modifications des structures de dossiers `mod.info` et Workshop (`mods/<ModName>/<Version>`).
2. **Estimation des différences et du volume :** Compare les clés dans `EN/*.json` par rapport aux fichiers cibles existants (`<TARGET_LANG>/*.json`), aux hachages SHA-1 stockés dans `pz_translator_state.json`, et aux règles critiques provenant de `token_rules.json`. Les clés manquantes, les clés dont le texte source en anglais a été modifié, et les clés suivies avec des espaces réservés/balises incorrects sont mises en file d'attente pour la traduction ; les traductions existantes de l'auteur sont laissées telles quelles.
3. **Traduction et validation par un modèle de langage :** Envoie chaque chaîne originale complète à `http://<host>:<port>/completion` en utilisant le format de requête "TranslateGemma" standard, puis vérifie les tokens critiques par rapport à la chaîne d'origine. En cas de désaccord, tente à nouveau avec différentes valeurs initiales jusqu'à `max_retries` ; si toutes les tentatives échouent, conserve le texte en anglais, indique le statut de modification comme `EN/<LANG>`, et enregistre les détails dans `pz_translator_issues.log`.
4. **Sortie double :** Chaque `save_every` clés (et à la fin ou `Ctrl+C`), écrit un JSON UTF-8 valide vers :
   - Le dossier de modification cible : `...\Translate\<LANG>\<file>.json`
   - Le dossier de miroir local : `pz_translator_mods\<full_path_without_drive_letter>\Translate\<LANG>\<file>.json`

---

## Notes et limitations

- **Formats pris en charge :** Seuls les fichiers de localisation `.json` de Project Zomboid **version 42.15+** sont traités. Les anciens fichiers de traduction `.txt` sont ignorés car la version 42.15+ ne les charge plus.
- **Multijoueur (`DoLuaChecksum`):** Puisque les dossiers `Translate` se trouvent à l'intérieur de `media/lua/shared/`, l'ajout direct de fichiers de traduction dans les dossiers du Steam Workshop peut entraîner des incohérences de sommes de contrôle sur les serveurs multijoueurs avec `DoLuaChecksum=true`. Pour les serveurs multijoueurs publics, soit regroupez les fichiers miroirs provenant de `pz_translator_mods/` sous forme d'un mod distinct dédié uniquement aux traductions, soit jouer en mode solo / sur des serveurs avec `DoLuaChecksum=false`.
