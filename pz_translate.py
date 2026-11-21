#!/usr/bin/env python3
"""pz_translate.py — Universal Project Zomboid (B42+ JSON) Mod Translator via TranslateGemma."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table

ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG_FILE = ROOT / "config.json"
LOCALES_DIR = ROOT / "cli_locales"

DEFAULT_CONFIG: Dict[str, object] = {
    "llamacpp_host": "127.0.0.1",
    "llamacpp_port": 8734,
    "mods_path": r"Z:\steam\steamapps\workshop\content\108600",
    "default_source_lang": "EN",
    "default_target_lang": "RU",
    "ui_lang": "en",
    "mirror_dir": "pz_translator_mods",
    "state_file": "pz_translator_state.json",
    "token_rules_file": "token_rules.json",
    "save_every": 20,
}

DEFAULT_TOKEN_RULES: Dict[str, object] = {
    "max_retries": 3,
    "retry_temperatures": [0.2, 0.35, 0.5],
    "issues_log": "pz_translator_issues.log",
    "check_report": "pz_translator_check_report.txt",
    "rules": [
        {
            "name": "curly_placeholders",
            "pattern": r"\{[^{}\r\n]{1,64}\}",
            "enabled": True,
            "critical": True,
            "description": "Mod variables like {name}, {page}, {count}",
        },
        {
            "name": "pz_percent_args",
            "pattern": r"%\d+",
            "enabled": True,
            "critical": True,
            "description": "PZ getText positional arguments like %1, %2",
        },
        {
            "name": "pz_richtext_tags",
            "pattern": r"<(?:LINE|BR|br|H[1-6]|TEXT|LEFT|RIGHT|CENTRE|CENTER|SPACE|GREEN|RED|ORANGE|BLUE|YELLOW|WHITE|GRAY|GREY|(?:RGB|INDENT|SETX|SETY|SIZE|IMAGE|IMAGECENTRE|JOYPAD):[^<>\r\n]+)>",
            "enabled": True,
            "critical": True,
            "description": "PZ RichText UI tags",
        },
        {
            "name": "line_breaks",
            "pattern": r"\n|\\n|\t",
            "enabled": True,
            "critical": False,
            "description": "Newlines and tabs (non-critical, shown only in dry-run check)",
        },
    ],
}

# Project Zomboid folder code -> (TranslateGemma ISO code, language name)
PZ_LANGUAGES: Dict[str, Tuple[str, str]] = {
    "EN": ("en", "English"),
    "RU": ("ru", "Russian"),
    "CN": ("zh", "Chinese"),
    "CH": ("zh-TW", "Traditional Chinese"),
    "JP": ("ja", "Japanese"),
    "KO": ("ko", "Korean"),
    "DE": ("de", "German"),
    "FR": ("fr", "French"),
    "ES": ("es", "Spanish"),
    "IT": ("it", "Italian"),
    "PTBR": ("pt-BR", "Portuguese"),
    "PT": ("pt", "Portuguese"),
    "TR": ("tr", "Turkish"),
    "UA": ("uk", "Ukrainian"),
    "PL": ("pl", "Polish"),
    "NL": ("nl", "Dutch"),
    "DA": ("da", "Danish"),
    "HU": ("hu", "Hungarian"),
    "TH": ("th", "Thai"),
    "CS": ("cs", "Czech"),
    "FI": ("fi", "Finnish"),
    "NO": ("no", "Norwegian"),
    "RO": ("ro", "Romanian"),
}

LANG_ALIASES: Dict[str, str] = {
    **{k.lower(): k for k in PZ_LANGUAGES},
    **{iso.lower(): pz for pz, (iso, _) in PZ_LANGUAGES.items()},
    "zh-cn": "CN",
    "zh_tw": "CH",
    "pt_br": "PTBR",
    "ja": "JP",
    "uk": "UA",
}

DEFAULT_EN_UI: Dict[str, str] = {
    "lang_display_name": "English",
    "app_title": "Project Zomboid Mod Translator",
    "label_server": "Server",
    "label_mods_path": "Mods path",
    "label_mirror": "Mirror",
    "label_ui_lang": "UI language",
    "label_token_rules": "Token rules",
    "select_ui_lang_title": "Select Interface Language",
    "prompt_ui_lang": "Interface language [{default}]:",
    "invalid_ui_lang": "Unknown language selection. Try again.",
    "menu_title": "Select Mode",
    "menu_opt_1": "1. Translate a specific mod to a target language",
    "menu_opt_2": "2. Scan all mods (search Translate folders), select from list, and translate",
    "menu_opt_3": "3. Manage saved progress (update / overwrite / restore / delete / check)",
    "menu_opt_4": "4. Change interface language",
    "menu_opt_0": "0. Exit",
    "prompt_mode": "Mode [1/2/3/4/0]:",
    "invalid_mode": "Please enter 1, 2, 3, 4, or 0.",
    "prompt_mod_path": "Enter path to mod folder (or its Translate / EN folder):",
    "prompt_scan_path": "Enter path to scan mods [{default}]:",
    "error_path_not_found": "Error: path not found: {path}",
    "available_langs_hint": "Target languages (PZ or ISO code, e.g.: RU, DE, CN, JP, PTBR):",
    "prompt_target_lang": "Target language [{default}]:",
    "scanning_path": "Scanning {path} ...",
    "no_targets_found": "No Translate/{source_lang} folders with .json files found in: {path}",
    "skipped_legacy_note": "(Skipped legacy B41 .txt-only mods: {count})",
    "found_targets_header": "Found mods with Translate/{source_lang}: {count}",
    "col_num": "#",
    "col_mod": "Mod",
    "col_workshop_id": "Workshop ID",
    "col_files": "Files",
    "col_status": "Status",
    "col_volume": "To Translate",
    "col_lang": "Lang",
    "col_lines": "Lines",
    "col_in_game": "In Game",
    "col_in_mirror": "Mirror",
    "col_updated": "Updated",
    "col_updates": "Updates",
    "col_checked": "Checked",
    "col_critical": "Critical",
    "col_warnings": "Warnings",
    "status_has_lang": "{lang}: {existing}/{total} files",
    "status_has_mixed": "{src}/{lang}: {existing}/{total} ({fb} fallback)",
    "status_no_lang": "no {lang}",
    "vol_read_error": "JSON read error ({count} files)",
    "vol_up_to_date": "up to date (0 chars)",
    "vol_pending_full": "{lines} lines, {chars} chars",
    "vol_pending_partial": "{lines} lines, {chars} chars (of {total_chars})",
    "vol_diff_tag": "({new} new, {chg} chg, {fix} fix)",
    "vol_read_errs_tag": "[read errors: {count}]",
    "total_to_translate": "Total to translate across list: {lines} lines, {chars} chars",
    "prompt_select_mods": "Enter mod numbers separated by commas (e.g. 1,3,5 or 1-4 or all; Enter to cancel):",
    "input_error": "Input error: {error}. Try again.",
    "selected_summary": "Selected mods: {count} | Target language: {lang} ({name})",
    "translating_mod_header": "Mod: {name} ({path}) -> {lang} ({lang_name})",
    "file_read_error": "Failed to read {file}: {error}",
    "file_up_to_date": "{file}: already up to date (skipped)",
    "file_translating": "{file}: translating {lines} lines{detail} ({chars} chars)...",
    "file_detail_diff": " ({new} new, {chg} chg, {fix} fix)",
    "conn_error": "Connection error on {key}: {error}",
    "server_unreachable": "llama-server unreachable (3 consecutive errors). Saving progress and exiting.",
    "key_error": "Error on {key}: {error}",
    "token_fallback_warn": "Placeholder mismatch on {key} after {attempts} attempts -> kept {src_lang} ({src_lang}/{lang}); logged.",
    "file_mixed_note": "{file}: {count} fallback line(s) kept in {src_lang} ({src_lang}/{lang}) -> see {log}",
    "interrupted_saving": "Interrupted by user. Saving current progress...",
    "stopped_saved": "Translation stopped. Progress saved.",
    "saved_to_mod": "Saved to mod:    {path}",
    "saved_to_mirror": "Saved to mirror: {path}",
    "done_single": "Done!",
    "done_all": "Done! All selected mods translated.",
    "state_empty": "Saved progress is empty ({file} has no entries yet).",
    "manage_title": "Saved Translations ({count})",
    "prompt_select_saved": "Select mod numbers (e.g. 1,3 or 1-4 or all; Enter to go back):",
    "manage_actions_title": "Select action for chosen mods:",
    "manage_act_1": "1. Update (translate new, changed, and broken-token strings)",
    "manage_act_2": "2. Overwrite from scratch (re-translate all strings)",
    "manage_act_3": "3. Restore translations from mirror folder back to game",
    "manage_act_4": "4. Delete translations",
    "manage_act_5": "5. Dry-run token check (inspect broken tokens without translating)",
    "prompt_action": "Action [1-5]:",
    "unknown_action": "Unknown action.",
    "delete_scope_title": "Where to delete translations from?",
    "delete_scope_1": "1. Only from game folder (keep mirror & progress history)",
    "delete_scope_2": "2. Only from mirror folder",
    "delete_scope_3": "3. Everywhere (game, mirror, and progress history)",
    "prompt_delete_scope": "Option [1-3]:",
    "cancelled": "Cancelled.",
    "deleted_summary": "{name} [{lang}]: deleted from game: {game_cnt}, from mirror: {mirror_cnt}",
    "delete_file_error": "Failed to delete {path}: {error}",
    "restored_summary": "{name} [{lang}]: restored files: {count}",
    "check_report_title": "Dry-run Token Check ({count} mods)",
    "check_report_saved": "Detailed dry-run report saved to: {path}",
    "check_clean_summary": "All checked keys are clean (0 critical mismatches).",
    "folder_not_found": "Folder not found: {path}",
    "no_source_json": "No source JSON found in {path}",
    "err_invalid_range": "Invalid range: {part}",
    "err_out_of_range": "Number out of range: {num}",
    "err_invalid_value": "Invalid value: {part}",
    "err_none_selected": "No mods selected",
}

console = Console()
_RNG = random.SystemRandom()


class I18n:
    def __init__(self, lang: str = "en") -> None:
        self.lang = lang
        self.messages: Dict[str, str] = dict(DEFAULT_EN_UI)
        self.load(lang)

    def load(self, lang: str) -> None:
        self.lang = lang
        base = dict(DEFAULT_EN_UI)
        en_file = LOCALES_DIR / "en.json"
        if en_file.is_file():
            try:
                base.update(json.loads(en_file.read_text(encoding="utf-8")))
            except Exception:
                pass

        if lang != "en":
            lang_file = LOCALES_DIR / f"{lang}.json"
            if lang_file.is_file():
                try:
                    base.update(json.loads(lang_file.read_text(encoding="utf-8")))
                except Exception:
                    pass
        self.messages = base

    def t(self, _msg_key: str, /, **kwargs: object) -> str:
        template = self.messages.get(_msg_key, DEFAULT_EN_UI.get(_msg_key, _msg_key))
        if kwargs:
            try:
                return template.format(**kwargs)
            except Exception:
                fallback = DEFAULT_EN_UI.get(_msg_key, template)
                try:
                    return fallback.format(**kwargs)
                except Exception:
                    return template
        return template


@dataclass
class ModTranslateTarget:
    display_name: str
    workshop_id: Optional[str]
    version_tag: Optional[str]
    translate_dir: Path
    source_dir: Path
    json_files: List[Path]


@dataclass
class TokenRule:
    name: str
    pattern: re.Pattern[str]
    critical: bool
    description: str = ""


@dataclass
class TokenRulesConfig:
    max_retries: int
    retry_temperatures: List[float]
    issues_log: Path
    check_report: Path
    rules: List[TokenRule]

    @property
    def critical_rules(self) -> List[TokenRule]:
        return [r for r in self.rules if r.critical]


@dataclass
class TokenMismatch:
    rule_name: str
    critical: bool
    expected: Dict[str, int]
    got: Dict[str, int]

    def format_short(self) -> str:
        return f"{self.rule_name}: expected {self.expected}, got {self.got}"


@dataclass
class AppSettings:
    host: str
    port: int
    mods_path: Path
    default_source_lang: str
    default_target_lang: str
    ui_lang: str
    mirror_root: Path
    state_file: Path
    token_rules_file: Path
    save_every: int


def resolve_language(raw_lang: str) -> Tuple[str, str, str]:
    key = raw_lang.strip().lower()
    if key in LANG_ALIASES:
        pz_code = LANG_ALIASES[key]
        iso_code, name = PZ_LANGUAGES[pz_code]
        return pz_code, iso_code, name
    pz_code = raw_lang.strip().upper()
    return pz_code, raw_lang.strip(), raw_lang.strip()


def build_prompt(
    text: str,
    tgt_code: str,
    tgt_name: str,
    src_code: str = "en",
    src_name: str = "English",
    prompt_mode: str = "canonical",
) -> str:
    if prompt_mode == "special":
        instruction = (
            f"You are a professional {src_name} ({src_code}) to {tgt_name} ({tgt_code}) translator for video game and "
            f"software UI localization. Copy numeric placeholders like {{0}}, {{1}} EXACTLY as-is without changing or removing them. "
            f"Produce ONLY the direct {tgt_name} translation, without quotes or explanations.\n\n\n{text}"
        )
    else:
        instruction = (
            f"You are a professional {src_name} ({src_code}) to {tgt_name} ({tgt_code}) translator. "
            f"Your goal is to accurately convey the meaning and nuances of the original {src_name} text "
            f"while adhering to {tgt_name} grammar, vocabulary, and cultural sensitivities. "
            f"Produce only the {tgt_name} translation, without any additional explanations or commentary. "
            f"Please translate the following {src_name} text into {tgt_name}:\n\n\n{text}"
        )
    return f"<start_of_turn>user\n{instruction}<end_of_turn>\n<start_of_turn>model\n"


def call_llama(
    prompt: str,
    port: int,
    host: str = "127.0.0.1",
    temperature: float = 0.2,
    seed: Optional[int] = None,
) -> str:
    payload: Dict[str, object] = {
        "prompt": prompt,
        "temperature": temperature,
        "top_p": 0.95,
        "stop": ["<end_of_turn>", "<start_of_turn>"],
    }
    if seed is not None:
        payload["seed"] = seed

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"http://{host}:{port}/completion",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return str(data.get("content", "")).strip()


def clean_translation_output(raw_output: str, source_text: str) -> str:
    text = raw_output.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ('"', "'"):
        if not (source_text.startswith(text[0]) and source_text.endswith(text[0])):
            text = text[1:-1].strip()
    return text


def load_config(config_path: Path) -> dict:
    cfg = dict(DEFAULT_CONFIG)
    if config_path.is_file():
        try:
            loaded = json.loads(config_path.read_text(encoding="utf-8-sig"))
            if isinstance(loaded, dict):
                cfg.update(loaded)
        except Exception as e:
            console.print(f"[yellow]Warning: failed to read {config_path.name}: {e}[/]")
    else:
        try:
            config_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
        except OSError:
            pass
    return cfg


def abs_path(path: Path) -> Path:
    return Path(os.path.abspath(path))


def resolve_app_path(raw: str) -> Path:
    p = Path(raw)
    return p if p.is_absolute() else ROOT / p


def build_settings(cfg: dict, args: argparse.Namespace) -> AppSettings:
    host = str(args.host or cfg.get("llamacpp_host", "127.0.0.1"))
    port = int(args.port if args.port is not None else cfg.get("llamacpp_port", 8734))
    mods_path = Path(str(cfg.get("mods_path", DEFAULT_CONFIG["mods_path"])))
    default_source_lang = str(args.source_lang or cfg.get("default_source_lang", "EN"))
    default_target_lang = str(cfg.get("default_target_lang", "RU"))
    ui_lang = str(args.ui_lang or cfg.get("ui_lang", "en"))
    mirror_root = abs_path(resolve_app_path(str(cfg.get("mirror_dir", "pz_translator_mods"))))
    state_file = abs_path(resolve_app_path(str(cfg.get("state_file", "pz_translator_state.json"))))
    token_rules_raw = str(getattr(args, "rules", None) or cfg.get("token_rules_file", "token_rules.json"))
    token_rules_file = abs_path(resolve_app_path(token_rules_raw))
    save_every = max(1, int(cfg.get("save_every", 20)))

    return AppSettings(
        host=host,
        port=port,
        mods_path=mods_path,
        default_source_lang=default_source_lang,
        default_target_lang=default_target_lang,
        ui_lang=ui_lang,
        mirror_root=mirror_root,
        state_file=state_file,
        token_rules_file=token_rules_file,
        save_every=save_every,
    )


def load_token_rules(rules_path: Path) -> TokenRulesConfig:
    raw_cfg: dict = dict(DEFAULT_TOKEN_RULES)
    if rules_path.is_file():
        try:
            loaded = json.loads(rules_path.read_text(encoding="utf-8-sig"))
            if isinstance(loaded, dict):
                raw_cfg.update(loaded)
        except Exception as e:
            console.print(f"[yellow]Warning: failed to read {rules_path.name}: {e} (using defaults)[/]")
    else:
        try:
            rules_path.write_text(json.dumps(DEFAULT_TOKEN_RULES, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
        except OSError:
            pass

    compiled: List[TokenRule] = []
    for item in raw_cfg.get("rules", []):
        if not isinstance(item, dict) or not item.get("enabled", True):
            continue
        name = str(item.get("name", "unnamed"))
        pat_str = str(item.get("pattern", ""))
        if not pat_str:
            continue
        try:
            rx = re.compile(pat_str)
        except re.error as e:
            console.print(f"[red]Invalid regex in {rules_path.name} ({name}): {e}[/]")
            continue
        compiled.append(
            TokenRule(
                name=name,
                pattern=rx,
                critical=bool(item.get("critical", True)),
                description=str(item.get("description", "")),
            )
        )

    temps_raw = raw_cfg.get("retry_temperatures", [0.2, 0.35, 0.5])
    temps = [float(x) for x in temps_raw] if isinstance(temps_raw, list) and temps_raw else [0.2, 0.35, 0.5]

    return TokenRulesConfig(
        max_retries=max(1, int(raw_cfg.get("max_retries", 3))),
        retry_temperatures=temps,
        issues_log=abs_path(resolve_app_path(str(raw_cfg.get("issues_log", "pz_translator_issues.log")))),
        check_report=abs_path(resolve_app_path(str(raw_cfg.get("check_report", "pz_translator_check_report.txt")))),
        rules=compiled,
    )


def mask_critical_tokens(text: str, critical_rules: List[TokenRule]) -> Tuple[str, Dict[str, str]]:
    """Mask critical tokens into {0}, {1}, ... without colliding with unmasked literal {N}."""
    if not critical_rules:
        return text, {}
    combined = re.compile("|".join(f"(?:{r.pattern.pattern})" for r in critical_rules))
    if not combined.search(text):
        return text, {}

    remainder = combined.sub("", text)
    used_nums = {int(m) for m in re.findall(r"\{(\d+)\}", remainder)}
    next_idx = 0
    tok_to_mask: Dict[str, str] = {}
    mask_to_tok: Dict[str, str] = {}

    def _repl(match: re.Match[str]) -> str:
        nonlocal next_idx
        tok = match.group(0)
        if tok not in tok_to_mask:
            while next_idx in used_nums:
                next_idx += 1
            mask = f"{{{next_idx}}}"
            tok_to_mask[tok] = mask
            mask_to_tok[mask] = tok
            next_idx += 1
        return tok_to_mask[tok]

    masked = combined.sub(_repl, text)
    return masked, mask_to_tok


def compare_tokens(src_text: str, dst_text: str, rules: List[TokenRule]) -> List[TokenMismatch]:
    mismatches: List[TokenMismatch] = []
    for rule in rules:
        c_src = Counter(rule.pattern.findall(src_text))
        c_dst = Counter(rule.pattern.findall(dst_text))
        if c_src != c_dst:
            mismatches.append(
                TokenMismatch(
                    rule_name=rule.name,
                    critical=rule.critical,
                    expected=dict(c_src),
                    got=dict(c_dst),
                )
            )
    return mismatches


def append_issue_log(
    log_path: Path,
    mod_name: str,
    src_lang: str,
    tgt_lang: str,
    rel_str: str,
    key: str,
    source_text: str,
    failed_attempts: List[Tuple[int, str, int, float, str, List[str]]],
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().isoformat(timespec="seconds")
    lines = [
        f"[{ts}] [{src_lang}/{tgt_lang}] Mod: {mod_name} | File: {rel_str} | Key: {key}",
        f"  {src_lang} (saved): {source_text!r}",
    ]
    for attempt_no, mode_tag, seed, temp, bad_text, reasons in failed_attempts:
        reason_str = "; ".join(reasons) or "empty output"
        lines.append(f"  Attempt {attempt_no} [{mode_tag}] (seed={seed}, temp={temp}): {bad_text!r}")
        lines.append(f"    Mismatch: {reason_str}")
    lines.append("-" * 72)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def translate_with_retries(
    source_text: str,
    src_code: str,
    src_name: str,
    tgt_code: str,
    tgt_name: str,
    settings: AppSettings,
    rules_cfg: TokenRulesConfig,
) -> Tuple[str, bool, List[Tuple[int, str, int, float, str, List[str]]]]:
    """A_mask_first pipeline:
    - No critical tokens -> pure canonical prompt (0 hallucinations).
    - Has critical tokens -> try 1: canonical + {0}, try 2+: special + {0}.
    """
    critical_rules = rules_cfg.critical_rules
    masked_text, mask_to_tok = mask_critical_tokens(source_text, critical_rules)
    temps = rules_cfg.retry_temperatures
    failed_attempts: List[Tuple[int, str, int, float, str, List[str]]] = []

    if mask_to_tok:
        expected_masks = Counter(m for m in re.findall(r"\{\d+\}", masked_text) if m in mask_to_tok)
        mask_replace_rx = re.compile("|".join(re.escape(m) for m in mask_to_tok))

    for idx in range(rules_cfg.max_retries):
        if not mask_to_tok:
            prompt_mode = "canonical"
            mode_tag = "canonical+raw"
            temp = temps[min(idx, len(temps) - 1)]
        elif idx == 0:
            prompt_mode = "canonical"
            mode_tag = "canonical+{0}"
            temp = temps[0]
        else:
            prompt_mode = "special"
            mode_tag = "special+{0}"
            temp = temps[min(idx - 1, len(temps) - 1)]

        seed = _RNG.randint(1, 2_147_483_647)
        prompt = build_prompt(masked_text, tgt_code, tgt_name, src_code, src_name, prompt_mode=prompt_mode)
        raw = call_llama(prompt, settings.port, settings.host, temperature=temp, seed=seed)
        cleaned = clean_translation_output(raw, masked_text)

        if not cleaned:
            failed_attempts.append((idx + 1, mode_tag, seed, temp, raw, ["empty output"]))
            continue

        reasons: List[str] = []
        restored = cleaned

        if mask_to_tok:
            got_masks = Counter(m for m in re.findall(r"\{\d+\}", cleaned) if m in mask_to_tok)
            if got_masks != expected_masks:
                reasons.append(f"mask mismatch: expected {dict(expected_masks)}, got {dict(got_masks)}")
            restored = mask_replace_rx.sub(lambda m: mask_to_tok[m.group(0)], cleaned)

        mismatches = compare_tokens(source_text, restored, critical_rules)
        if mismatches:
            reasons.extend(m.format_short() for m in mismatches)

        if not reasons:
            return restored, True, failed_attempts

        failed_attempts.append((idx + 1, mode_tag, seed, temp, restored, reasons))

    return source_text, False, failed_attempts


def list_available_ui_langs() -> List[Tuple[str, str]]:
    langs: Dict[str, str] = {"en": "English"}
    if LOCALES_DIR.is_dir():
        for file in sorted(LOCALES_DIR.glob("*.json")):
            code = file.stem
            name = code
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
                name = str(data.get("lang_display_name", code))
            except Exception:
                pass
            langs[code] = name
    return [("en", langs["en"])] + [(k, v) for k, v in sorted(langs.items()) if k != "en"]


def select_ui_language_interactive(i18n: I18n, default_lang: str) -> str:
    available = list_available_ui_langs()
    if default_lang not in {code for code, _ in available}:
        default_lang = "en"

    table = Table(title=i18n.t("select_ui_lang_title"), box=box.ROUNDED, show_header=False)
    table.add_column("No", style="cyan", justify="right")
    table.add_column("Code", style="bold green")
    table.add_column("Language", style="white")
    for idx, (code, name) in enumerate(available, 1):
        table.add_row(str(idx), code, name)
    console.print(table)

    code_map = {code.lower(): code for code, _ in available}
    while True:
        raw = console.input(f"[bold cyan]{i18n.t('prompt_ui_lang', default=default_lang)}[/] ").strip()
        if not raw:
            chosen = default_lang
            break
        if raw.isdigit():
            num = int(raw)
            if 1 <= num <= len(available):
                chosen = available[num - 1][0]
                break
        elif raw.lower() in code_map:
            chosen = code_map[raw.lower()]
            break
        console.print(f"[red]{i18n.t('invalid_ui_lang')}[/]")

    i18n.load(chosen)
    return chosen


def hash_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def get_mirror_path(real_path: Path, mirror_root: Path) -> Path:
    p = abs_path(real_path)
    rel = p.relative_to(p.anchor) if p.anchor else p
    return mirror_root / rel


def make_state_id(translate_dir: Path, pz_lang: str) -> str:
    return f"{abs_path(translate_dir)}::{pz_lang.upper()}"


def load_state(state_file: Path) -> dict:
    if not state_file.exists():
        return {"version": 1, "mods": {}}
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("mods"), dict):
            return data
    except Exception:
        pass
    return {"version": 1, "mods": {}}


def save_state(state: dict, state_file: Path) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    tmp_file = state_file.with_suffix(".tmp")
    tmp_file.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp_file, state_file)


def strip_trailing_commas(text: str) -> str:
    """Remove trailing commas before '}' or ']' outside string literals."""
    out: List[str] = []
    in_string = False
    escaped = False
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if in_string:
            out.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
                out.append(ch)
            elif ch == ",":
                j = i + 1
                while j < n and text[j] in " \t\r\n":
                    j += 1
                if j < n and text[j] in "}]":
                    i += 1
                    continue
                out.append(ch)
            else:
                out.append(ch)
        i += 1
    return "".join(out)


def load_json_safe(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8-sig")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = json.loads(strip_trailing_commas(raw))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def read_mod_name(translate_dir: Path) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    parts = translate_dir.parts
    workshop_id = None
    mod_folder_name = None
    version_tag = None

    for idx, part in enumerate(parts):
        if part == "108600" and idx + 1 < len(parts) and parts[idx + 1].isdigit():
            workshop_id = parts[idx + 1]
        if part.lower() == "mods" and idx + 1 < len(parts):
            mod_folder_name = parts[idx + 1]
            if idx + 2 < len(parts) and parts[idx + 2].lower() != "media":
                version_tag = parts[idx + 2]

    mod_info_name = None
    cur = translate_dir.parent
    for _ in range(5):
        mod_info = cur / "mod.info"
        if mod_info.is_file():
            try:
                for line in mod_info.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
                    if line.strip().lower().startswith("name="):
                        mod_info_name = line.split("=", 1)[1].strip()
                        break
            except OSError:
                pass
            if mod_info_name:
                break
        if cur.parent == cur:
            break
        cur = cur.parent

    name = mod_info_name or mod_folder_name or translate_dir.parent.name
    return name, workshop_id, version_tag


def find_translate_targets(root_path: Path, source_lang: str = "EN") -> Tuple[List[ModTranslateTarget], int]:
    targets: List[ModTranslateTarget] = []
    skipped_legacy = 0
    src_upper = source_lang.upper()

    candidate_translates: List[Path] = []
    if root_path.name.upper() == src_upper and root_path.parent.name.lower() == "translate":
        candidate_translates.append(root_path.parent)
    elif root_path.name.lower() == "translate":
        candidate_translates.append(root_path)
    else:
        for dirpath, dirnames, _ in os.walk(root_path):
            if "Translate" in dirnames:
                candidate_translates.append(Path(dirpath) / "Translate")
                dirnames.remove("Translate")
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]

    seen = set()
    for t_dir in sorted(candidate_translates):
        canonical = abs_path(t_dir)
        if canonical in seen:
            continue
        seen.add(canonical)

        src_dir = None
        try:
            for child in t_dir.iterdir():
                if child.is_dir() and child.name.upper() == src_upper:
                    src_dir = child
                    break
        except OSError:
            continue

        if not src_dir:
            continue

        json_files = sorted(p for p in src_dir.rglob("*.json") if p.is_file())
        if not json_files:
            if any(src_dir.rglob("*.txt")):
                skipped_legacy += 1
            continue

        name, workshop_id, version_tag = read_mod_name(t_dir)
        targets.append(
            ModTranslateTarget(
                display_name=name,
                workshop_id=workshop_id,
                version_tag=version_tag,
                translate_dir=abs_path(t_dir),
                source_dir=abs_path(src_dir),
                json_files=[abs_path(p) for p in json_files],
            )
        )

    return targets, skipped_legacy


def format_num(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def collect_todo_keys(
    source_data: dict,
    existing: dict,
    saved_hashes: dict,
    force: bool,
    critical_rules: List[TokenRule],
) -> Tuple[List[str], int, int, int]:
    """Return (keys_to_translate, new_count, changed_count, fix_count).

    Keys present in `existing` that are NOT in `saved_hashes` belong to
    pre-existing author translations and are NEVER analyzed or touched.
    """
    todo: List[str] = []
    new_cnt = 0
    changed_cnt = 0
    fix_cnt = 0

    for k, v in source_data.items():
        if k == "$schema" or not isinstance(v, str) or not v.strip():
            continue
        if force:
            todo.append(k)
            new_cnt += 1
        elif k not in existing:
            todo.append(k)
            new_cnt += 1
        elif k in saved_hashes:
            if saved_hashes[k] != hash_text(v):
                todo.append(k)
                changed_cnt += 1
            elif not isinstance(existing[k], str) or (
                critical_rules and compare_tokens(v, existing[k], critical_rules)
            ):
                todo.append(k)
                fix_cnt += 1

    return todo, new_cnt, changed_cnt, fix_cnt


def count_entry_fallbacks(entry: dict) -> int:
    return sum(len(f.get("fallback_keys", [])) for f in entry.get("files", {}).values())


def estimate_translation_volume(
    target: ModTranslateTarget,
    pz_lang: str,
    state: dict,
    critical_rules: List[TokenRule],
    force: bool = False,
) -> Tuple[int, int, int, int, int, int, int, int]:
    """Return (pending_keys, pending_chars, new_cnt, chg_cnt, fix_cnt, total_keys, total_chars, read_errors)."""
    out_root = target.translate_dir / pz_lang
    state_entry = state.get("mods", {}).get(make_state_id(target.translate_dir, pz_lang), {})
    files_state = state_entry.get("files", {})

    pending_keys = 0
    pending_chars = 0
    new_total = 0
    changed_total = 0
    fix_total = 0
    total_keys = 0
    total_chars = 0
    read_errors = 0

    for src_file in target.json_files:
        rel_str = src_file.relative_to(target.source_dir).as_posix()
        out_file = out_root / rel_str

        try:
            source_data = load_json_safe(src_file)
        except Exception:
            read_errors += 1
            continue

        existing: dict = {}
        if out_file.exists() and not force:
            try:
                existing = load_json_safe(out_file)
            except Exception:
                existing = {}

        saved_hashes = files_state.get(rel_str, {}).get("en_hashes", {})

        for k, v in source_data.items():
            if k == "$schema" or not isinstance(v, str) or not v.strip():
                continue
            total_keys += 1
            total_chars += len(v)

        todo, new_cnt, chg_cnt, fix_cnt = collect_todo_keys(
            source_data, existing, saved_hashes, force, critical_rules
        )
        new_total += new_cnt
        changed_total += chg_cnt
        fix_total += fix_cnt
        pending_keys += len(todo)
        pending_chars += sum(len(source_data[k]) for k in todo)

    return pending_keys, pending_chars, new_total, changed_total, fix_total, total_keys, total_chars, read_errors


def save_json_and_mirror(out_file: Path, data: dict, mirror_root: Path) -> Path:
    text = json.dumps(data, ensure_ascii=False, indent=4) + "\n"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(text, encoding="utf-8")

    mirror_file = get_mirror_path(out_file, mirror_root)
    mirror_file.parent.mkdir(parents=True, exist_ok=True)
    mirror_file.write_text(text, encoding="utf-8")
    return mirror_file


def ensure_state_entry(state: dict, target: ModTranslateTarget, pz_lang: str) -> dict:
    sid = make_state_id(target.translate_dir, pz_lang)
    mods = state.setdefault("mods", {})
    entry = mods.get(sid)
    if not entry:
        entry = {
            "mod_name": target.display_name,
            "workshop_id": target.workshop_id,
            "version_tag": target.version_tag,
            "translate_dir": str(target.translate_dir),
            "source_dir": str(target.source_dir),
            "lang": pz_lang,
            "files": {},
        }
        mods[sid] = entry
    else:
        entry["mod_name"] = target.display_name
        entry["workshop_id"] = target.workshop_id
        entry["version_tag"] = target.version_tag
        entry["translate_dir"] = str(target.translate_dir)
        entry["source_dir"] = str(target.source_dir)
    return entry


def update_file_state(
    entry: dict,
    rel_str: str,
    out_file: Path,
    mirror_file: Path,
    en_hashes: dict,
    translated_count: int,
    fallback_keys: Set[str],
) -> None:
    files = entry.setdefault("files", {})
    now_iso = datetime.now().isoformat(timespec="seconds")
    files[rel_str] = {
        "out_file": str(out_file),
        "mirror_file": str(mirror_file),
        "translated_keys": translated_count,
        "en_hashes": en_hashes,
        "fallback_keys": sorted(fallback_keys),
        "updated_at": now_iso,
    }
    entry["updated_at"] = now_iso


def translate_mod_target(
    target: ModTranslateTarget,
    pz_lang: str,
    tgt_code: str,
    tgt_name: str,
    settings: AppSettings,
    rules_cfg: TokenRulesConfig,
    state: dict,
    i18n: I18n,
    force: bool = False,
) -> None:
    out_root = target.translate_dir / pz_lang
    src_pz_lang, src_code, src_name = resolve_language(settings.default_source_lang)
    header = i18n.t(
        "translating_mod_header",
        name=target.display_name,
        path=target.translate_dir,
        lang=pz_lang,
        lang_name=tgt_name,
    )
    console.print(Panel(f"[bold white]{header}[/]", border_style="cyan", box=box.ROUNDED))

    sid = make_state_id(target.translate_dir, pz_lang)
    existing_entry = state.get("mods", {}).get(sid)
    files_state = existing_entry.get("files", {}) if existing_entry else {}
    consecutive_conn_errors = 0

    for src_file in target.json_files:
        rel_path = src_file.relative_to(target.source_dir)
        rel_str = rel_path.as_posix()
        out_file = out_root / rel_path

        try:
            source_data = load_json_safe(src_file)
        except Exception as e:
            console.print(f"  [red][!] {i18n.t('file_read_error', file=rel_path, error=e)}[/]")
            continue

        existing: dict = {}
        if out_file.exists() and not force:
            try:
                existing = load_json_safe(out_file)
            except Exception:
                existing = {}

        saved_hashes: dict = {} if force else dict(files_state.get(rel_str, {}).get("en_hashes", {}))
        fallback_set: Set[str] = (
            set() if force else set(files_state.get(rel_str, {}).get("fallback_keys", []))
        )
        todo, new_cnt, chg_cnt, fix_cnt = collect_todo_keys(
            source_data, existing, saved_hashes, force, rules_cfg.critical_rules
        )

        if not todo:
            console.print(f"  [green][✓][/] {i18n.t('file_up_to_date', file=rel_path)}")
            continue

        entry = ensure_state_entry(state, target, pz_lang)
        result: dict = {} if force else dict(existing)

        for k, v in source_data.items():
            if k == "$schema" or not isinstance(v, str):
                if k not in result:
                    result[k] = v
            elif not v.strip():
                result[k] = v

        # Remove obsolete keys only if they were previously translated by this tool
        if not force:
            obsolete = [k for k in list(result.keys()) if k not in source_data and k in saved_hashes]
            for k in obsolete:
                del result[k]
                saved_hashes.pop(k, None)
                fallback_set.discard(k)

        todo_chars = sum(len(source_data[k]) for k in todo)
        detail = (
            i18n.t("file_detail_diff", new=new_cnt, chg=chg_cnt, fix=fix_cnt)
            if not force and (chg_cnt > 0 or fix_cnt > 0)
            else ""
        )
        console.print(
            f"  [cyan][~][/] {i18n.t('file_translating', file=rel_path, lines=len(todo), detail=detail, chars=format_num(todo_chars))}"
        )

        file_fallbacks = 0
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                MofNCompleteColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                task_id = progress.add_task(f"[cyan]{rel_path}[/]", total=len(todo))
                for idx, key in enumerate(todo, 1):
                    src_val = source_data[key]
                    try:
                        translated, ok, failed_attempts = translate_with_retries(
                            src_val,
                            src_code,
                            src_name,
                            tgt_code,
                            tgt_name,
                            settings,
                            rules_cfg,
                        )
                        result[key] = translated
                        saved_hashes[key] = hash_text(src_val)
                        consecutive_conn_errors = 0

                        if ok:
                            fallback_set.discard(key)
                        else:
                            fallback_set.add(key)
                            file_fallbacks += 1
                            append_issue_log(
                                rules_cfg.issues_log,
                                target.display_name,
                                src_pz_lang,
                                pz_lang,
                                rel_str,
                                key,
                                src_val,
                                failed_attempts,
                            )
                            progress.console.print(
                                f"    [yellow][!] {i18n.t('token_fallback_warn', key=key, attempts=rules_cfg.max_retries, src_lang=src_pz_lang, lang=pz_lang)}[/]"
                            )
                    except urllib.error.URLError as e:
                        consecutive_conn_errors += 1
                        progress.console.print(f"    [red]{i18n.t('conn_error', key=key, error=e)}[/]")
                        if consecutive_conn_errors >= 3:
                            progress.console.print(f"  [bold red][!] {i18n.t('server_unreachable')}[/]")
                            mirror_file = save_json_and_mirror(out_file, result, settings.mirror_root)
                            update_file_state(
                                entry, rel_str, out_file, mirror_file, saved_hashes, len(result), fallback_set
                            )
                            save_state(state, settings.state_file)
                            raise SystemExit(1)
                    except Exception as e:
                        progress.console.print(f"    [yellow]{i18n.t('key_error', key=key, error=e)}[/]")
                        result[key] = src_val

                    if idx % settings.save_every == 0 or idx == len(todo):
                        mirror_file = save_json_and_mirror(out_file, result, settings.mirror_root)
                        update_file_state(
                            entry, rel_str, out_file, mirror_file, saved_hashes, len(result), fallback_set
                        )
                        save_state(state, settings.state_file)

                    progress.advance(task_id)
        except KeyboardInterrupt:
            console.print(f"\n  [yellow][!] {i18n.t('interrupted_saving')}[/]")
            mirror_file = save_json_and_mirror(out_file, result, settings.mirror_root)
            update_file_state(entry, rel_str, out_file, mirror_file, saved_hashes, len(result), fallback_set)
            save_state(state, settings.state_file)
            raise

        ordered = {k: result[k] for k in source_data if k in result}
        for k, v in result.items():
            if k not in ordered:
                ordered[k] = v

        mirror_file = save_json_and_mirror(out_file, ordered, settings.mirror_root)
        update_file_state(entry, rel_str, out_file, mirror_file, saved_hashes, len(ordered), fallback_set)
        save_state(state, settings.state_file)
        console.print(f"  [green][✓][/] {i18n.t('saved_to_mod', path=out_file)}")
        console.print(f"  [green][✓][/] {i18n.t('saved_to_mirror', path=mirror_file)}")
        if file_fallbacks > 0 or fallback_set:
            console.print(
                f"  [yellow][!][/] {i18n.t('file_mixed_note', file=rel_path, count=len(fallback_set), src_lang=src_pz_lang, lang=pz_lang, log=rules_cfg.issues_log.name)}"
            )


def run_dry_check(
    state: dict,
    sids: List[str],
    settings: AppSettings,
    rules_cfg: TokenRulesConfig,
    i18n: I18n,
) -> None:
    """Inspect only keys tracked in `en_hashes` (our translations) without modifying anything."""
    mods = state.get("mods", {})
    src_lang = settings.default_source_lang.upper()

    table = Table(
        title=i18n.t("check_report_title", count=len(sids)),
        box=box.ROUNDED,
        header_style="bold cyan",
    )
    table.add_column(i18n.t("col_mod"), style="bold white")
    table.add_column(i18n.t("col_lang"), no_wrap=True)
    table.add_column(i18n.t("col_checked"), justify="right", no_wrap=True)
    table.add_column(i18n.t("col_critical"), justify="right", no_wrap=True)
    table.add_column(i18n.t("col_warnings"), justify="right", no_wrap=True)

    report_lines: List[str] = [
        f"Dry-run token check @ {datetime.now().isoformat(timespec='seconds')}",
        f"Rules file: {settings.token_rules_file}",
        "=" * 80,
    ]
    total_crit = 0

    for sid in sids:
        entry = mods.get(sid)
        if not entry:
            continue
        mod_name = entry.get("mod_name", "?")
        lang = entry.get("lang", "?")
        src_dir = Path(entry.get("source_dir", ""))
        files_info = entry.get("files", {})

        checked_keys = 0
        crit_cnt = 0
        warn_cnt = 0
        fb_cnt = count_entry_fallbacks(entry)
        mod_details: List[str] = []

        for rel_str, f_info in files_info.items():
            saved_hashes: dict = f_info.get("en_hashes", {})
            fb_keys = set(f_info.get("fallback_keys", []))
            if not saved_hashes:
                continue
            src_file = src_dir / rel_str
            out_file = Path(f_info["out_file"])
            if not src_file.is_file() or not out_file.is_file():
                continue

            try:
                en_data = load_json_safe(src_file)
                tr_data = load_json_safe(out_file)
            except Exception as e:
                mod_details.append(f"  [READ ERROR] {rel_str}: {e}")
                continue

            for key in saved_hashes:
                src_val = en_data.get(key)
                tr_val = tr_data.get(key)
                if not isinstance(src_val, str) or not src_val.strip():
                    continue
                checked_keys += 1
                if not isinstance(tr_val, str):
                    crit_cnt += 1
                    mod_details.append(f"  [CRITICAL][{rel_str} | {key}] missing/non-string value in {lang}")
                    continue

                if key in fb_keys:
                    mod_details.append(f"  [FALLBACK {src_lang}/{lang}][{rel_str} | {key}] {src_val!r}")

                mismatches = compare_tokens(src_val, tr_val, rules_cfg.rules)
                crit_m = [m for m in mismatches if m.critical]
                warn_m = [m for m in mismatches if not m.critical]

                if crit_m:
                    crit_cnt += 1
                    reasons = "; ".join(m.format_short() for m in crit_m)
                    mod_details.append(
                        f"  [CRITICAL][{rel_str} | {key}] {reasons}\n"
                        f"    {src_lang}: {src_val!r}\n"
                        f"    {lang}: {tr_val!r}"
                    )
                if warn_m:
                    warn_cnt += 1
                    reasons = "; ".join(m.format_short() for m in warn_m)
                    mod_details.append(
                        f"  [WARNING ][{rel_str} | {key}] {reasons}\n"
                        f"    {src_lang}: {src_val!r}\n"
                        f"    {lang}: {tr_val!r}"
                    )

        total_crit += crit_cnt
        lang_badge = f"[yellow]{src_lang}/{lang} ({fb_cnt})[/]" if fb_cnt else f"[bold]{lang}[/]"
        crit_badge = f"[red]{crit_cnt}[/]" if crit_cnt else "[green]0[/]"
        warn_badge = f"[yellow]{warn_cnt}[/]" if warn_cnt else "[dim]0[/]"
        table.add_row(mod_name, lang_badge, format_num(checked_keys), crit_badge, warn_badge)

        tag = f"{src_lang}/{lang}" if fb_cnt else lang
        if mod_details:
            report_lines.append(
                f"\n### {mod_name} [{tag}] (critical={crit_cnt}, warnings={warn_cnt}, fallback_en={fb_cnt})"
            )
            report_lines.extend(mod_details)
        else:
            report_lines.append(f"\n### {mod_name} [{tag}] — OK (checked={checked_keys}, fallback_en={fb_cnt})")

    console.print(table)
    rules_cfg.check_report.parent.mkdir(parents=True, exist_ok=True)
    rules_cfg.check_report.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    if total_crit == 0:
        console.print(f"[green]{i18n.t('check_clean_summary')}[/]")
    console.print(f"[cyan]{i18n.t('check_report_saved', path=rules_cfg.check_report)}[/]")


def remove_empty_parents(start_dir: Path, stop_at: Path) -> None:
    cur = abs_path(start_dir)
    stop = abs_path(stop_at)
    while cur != stop and cur.parent != cur:
        try:
            if cur.exists() and cur.is_dir() and not any(cur.iterdir()):
                cur.rmdir()
                cur = cur.parent
            else:
                break
        except OSError:
            break


def delete_tracked_translations(
    state: dict,
    sids: List[str],
    scope: str,
    settings: AppSettings,
    i18n: I18n,
) -> None:
    mods = state.get("mods", {})
    for sid in sids:
        entry = mods.get(sid)
        if not entry:
            continue
        t_dir = Path(entry["translate_dir"])
        lang = entry["lang"]
        lang_dir = t_dir / lang
        files_dict = entry.get("files", {})

        deleted_game = 0
        deleted_mirror = 0

        for f_info in files_dict.values():
            out_file = Path(f_info["out_file"])
            mirror_file = Path(f_info["mirror_file"])

            if scope in ("game", "both") and out_file.exists():
                try:
                    out_file.unlink()
                    deleted_game += 1
                    remove_empty_parents(out_file.parent, t_dir)
                except OSError as e:
                    console.print(f"  [red][!] {i18n.t('delete_file_error', path=out_file, error=e)}[/]")

            if scope in ("mirror", "both") and mirror_file.exists():
                try:
                    mirror_file.unlink()
                    deleted_mirror += 1
                    remove_empty_parents(mirror_file.parent, settings.mirror_root)
                except OSError as e:
                    console.print(f"  [red][!] {i18n.t('delete_file_error', path=mirror_file, error=e)}[/]")

        if scope in ("game", "both") and lang_dir.exists():
            remove_empty_parents(lang_dir, t_dir)

        if scope == "both":
            mods.pop(sid, None)

        console.print(
            f"  [green][✓][/] {i18n.t('deleted_summary', name=entry.get('mod_name'), lang=lang, game_cnt=deleted_game, mirror_cnt=deleted_mirror)}"
        )

    save_state(state, settings.state_file)


def restore_from_mirror(state: dict, sids: List[str], i18n: I18n) -> None:
    mods = state.get("mods", {})
    for sid in sids:
        entry = mods.get(sid)
        if not entry:
            continue
        restored = 0
        for f_info in entry.get("files", {}).values():
            out_file = Path(f_info["out_file"])
            mirror_file = Path(f_info["mirror_file"])
            if mirror_file.is_file():
                out_file.parent.mkdir(parents=True, exist_ok=True)
                out_file.write_text(mirror_file.read_text(encoding="utf-8"), encoding="utf-8")
                restored += 1
        console.print(
            f"  [green][✓][/] {i18n.t('restored_summary', name=entry.get('mod_name'), lang=entry.get('lang'), count=restored)}"
        )


def parse_selection(raw: str, max_idx: int, i18n: I18n) -> List[int]:
    raw = raw.strip().lower()
    if raw in ("all", "*"):
        return list(range(1, max_idx + 1))

    selected: List[int] = []
    seen = set()
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            bounds = part.split("-", 1)
            if len(bounds) == 2 and bounds[0].strip().isdigit() and bounds[1].strip().isdigit():
                a, b = int(bounds[0].strip()), int(bounds[1].strip())
                if a <= b:
                    for num in range(a, b + 1):
                        if 1 <= num <= max_idx and num not in seen:
                            selected.append(num)
                            seen.add(num)
                    continue
            raise ValueError(i18n.t("err_invalid_range", part=part))
        elif part.isdigit():
            num = int(part)
            if 1 <= num <= max_idx:
                if num not in seen:
                    selected.append(num)
                    seen.add(num)
            else:
                raise ValueError(i18n.t("err_out_of_range", num=num))
        else:
            raise ValueError(i18n.t("err_invalid_value", part=part))

    if not selected:
        raise ValueError(i18n.t("err_none_selected"))
    return selected


def prompt_language(i18n: I18n, default_lang: str) -> Tuple[str, str, str]:
    console.print(f"\n[dim]{i18n.t('available_langs_hint')}[/]")
    preview = ", ".join(f"{pz} ({name})" for pz, (_, name) in list(PZ_LANGUAGES.items())[1:11])
    console.print(f"  [dim]{preview}, ...[/]")
    raw = console.input(f"[bold cyan]{i18n.t('prompt_target_lang', default=default_lang)}[/] ").strip() or default_lang
    return resolve_language(raw)


def render_banner(settings: AppSettings, i18n: I18n) -> None:
    info = (
        f"[bold cyan]{i18n.t('app_title')}[/]\n"
        f"[dim]{i18n.t('label_server')}:[/] http://{settings.host}:{settings.port}   "
        f"[dim]{i18n.t('label_ui_lang')}:[/] [green]{i18n.lang}[/]\n"
        f"[dim]{i18n.t('label_mods_path')}:[/] {settings.mods_path}\n"
        f"[dim]{i18n.t('label_mirror')}:[/] {settings.mirror_root}\n"
        f"[dim]{i18n.t('label_token_rules')}:[/] {settings.token_rules_file}"
    )
    console.print(Panel(info, border_style="blue", box=box.ROUNDED))


def run_mode_1(
    mod_path_arg: Optional[str],
    lang_arg: Optional[str],
    settings: AppSettings,
    rules_cfg: TokenRulesConfig,
    i18n: I18n,
    force: bool,
) -> int:
    if mod_path_arg:
        mod_path = Path(mod_path_arg.strip('"').strip("'"))
    else:
        raw_path = console.input(f"[bold cyan]{i18n.t('prompt_mod_path')}[/] ").strip().strip('"').strip("'")
        mod_path = Path(raw_path)

    if not mod_path.exists():
        console.print(f"[red]{i18n.t('error_path_not_found', path=mod_path)}[/]")
        return 1

    pz_lang, tgt_code, tgt_name = (
        resolve_language(lang_arg) if lang_arg else prompt_language(i18n, settings.default_target_lang)
    )
    targets, skipped_legacy = find_translate_targets(mod_path, settings.default_source_lang)

    if not targets:
        console.print(f"[yellow]{i18n.t('no_targets_found', source_lang=settings.default_source_lang, path=mod_path)}[/]")
        if skipped_legacy:
            console.print(f"[dim]{i18n.t('skipped_legacy_note', count=skipped_legacy)}[/]")
        return 1

    state = load_state(settings.state_file)
    console.print(f"\n[bold]{i18n.t('selected_summary', count=len(targets), lang=pz_lang, name=tgt_name)}[/]")
    try:
        for t in targets:
            translate_mod_target(t, pz_lang, tgt_code, tgt_name, settings, rules_cfg, state, i18n, force)
    except KeyboardInterrupt:
        console.print(f"\n[yellow]{i18n.t('stopped_saved')}[/]")
        return 130

    console.print(f"\n[bold green]{i18n.t('done_single')}[/]")
    return 0


def run_mode_2(
    workshop_arg: Optional[str],
    lang_arg: Optional[str],
    settings: AppSettings,
    rules_cfg: TokenRulesConfig,
    i18n: I18n,
    force: bool,
) -> int:
    if workshop_arg:
        scan_root = Path(workshop_arg.strip('"').strip("'"))
    else:
        default_str = str(settings.mods_path)
        raw = (
            console.input(f"[bold cyan]{i18n.t('prompt_scan_path', default=default_str)}[/] ")
            .strip()
            .strip('"')
            .strip("'")
        )
        scan_root = Path(raw) if raw else settings.mods_path

    if not scan_root.exists():
        console.print(f"[red]{i18n.t('error_path_not_found', path=scan_root)}[/]")
        return 1

    pz_lang, tgt_code, tgt_name = (
        resolve_language(lang_arg) if lang_arg else prompt_language(i18n, settings.default_target_lang)
    )

    console.print(f"\n[cyan]{i18n.t('scanning_path', path=scan_root)}[/]")
    targets, skipped_legacy = find_translate_targets(scan_root, settings.default_source_lang)

    if not targets:
        console.print(f"[yellow]{i18n.t('no_targets_found', source_lang=settings.default_source_lang, path=scan_root)}[/]")
        if skipped_legacy:
            console.print(f"[dim]{i18n.t('skipped_legacy_note', count=skipped_legacy)}[/]")
        return 1

    state = load_state(settings.state_file)
    src_lang = settings.default_source_lang.upper()

    table = Table(
        title=i18n.t("found_targets_header", source_lang=settings.default_source_lang, count=len(targets)),
        box=box.ROUNDED,
        header_style="bold cyan",
    )
    table.add_column(i18n.t("col_num"), justify="right", style="cyan", no_wrap=True)
    table.add_column(i18n.t("col_mod"), style="bold white")
    table.add_column(i18n.t("col_workshop_id"), style="dim cyan", no_wrap=True)
    table.add_column(i18n.t("col_files"), justify="right", no_wrap=True)
    table.add_column(i18n.t("col_status"), no_wrap=True)
    table.add_column(i18n.t("col_volume"))

    total_pending_keys = 0
    total_pending_chars = 0

    for idx, t in enumerate(targets, 1):
        mod_label = t.display_name
        if t.version_tag:
            mod_label += f" [magenta][{t.version_tag}][/]"

        wid_label = t.workshop_id or "—"
        files_label = f"{len(t.json_files)} JSON"

        sid = make_state_id(t.translate_dir, pz_lang)
        state_entry = state.get("mods", {}).get(sid)
        fb_cnt = count_entry_fallbacks(state_entry) if state_entry else 0

        out_dir = t.translate_dir / pz_lang
        if out_dir.exists():
            existing_count = len(list(out_dir.rglob("*.json")))
            if fb_cnt > 0:
                status_label = f"[yellow]{i18n.t('status_has_mixed', src=src_lang, lang=pz_lang, existing=existing_count, total=len(t.json_files), fb=fb_cnt)}[/]"
            else:
                status_color = "green" if existing_count >= len(t.json_files) else "blue"
                status_label = f"[{status_color}]{i18n.t('status_has_lang', lang=pz_lang, existing=existing_count, total=len(t.json_files))}[/]"
        else:
            status_label = f"[yellow]{i18n.t('status_no_lang', lang=pz_lang)}[/]"

        p_keys, p_chars, new_cnt, chg_cnt, fix_cnt, _, t_chars, errs = estimate_translation_volume(
            t, pz_lang, state, rules_cfg.critical_rules, force=force
        )
        total_pending_keys += p_keys
        total_pending_chars += p_chars

        if errs and p_chars == 0:
            vol_label = f"[red]{i18n.t('vol_read_error', count=errs)}[/]"
        elif p_chars == 0:
            vol_label = f"[green]{i18n.t('vol_up_to_date')}[/]"
        else:
            if p_chars == t_chars:
                vol_label = f"[yellow]{i18n.t('vol_pending_full', lines=format_num(p_keys), chars=format_num(p_chars))}[/]"
            else:
                vol_label = f"[yellow]{i18n.t('vol_pending_partial', lines=format_num(p_keys), chars=format_num(p_chars), total_chars=format_num(t_chars))}[/]"
            if not force and (chg_cnt > 0 or fix_cnt > 0):
                vol_label += f" [cyan]{i18n.t('vol_diff_tag', new=new_cnt, chg=chg_cnt, fix=fix_cnt)}[/]"

        if errs and p_chars > 0:
            vol_label += f" [red]{i18n.t('vol_read_errs_tag', count=errs)}[/]"

        table.add_row(str(idx), mod_label, wid_label, files_label, status_label, vol_label)

    console.print(table)
    if skipped_legacy:
        console.print(f"[dim]{i18n.t('skipped_legacy_note', count=skipped_legacy)}[/]")
    console.print(
        f"[bold yellow]{i18n.t('total_to_translate', lines=format_num(total_pending_keys), chars=format_num(total_pending_chars))}[/]"
    )

    while True:
        raw_sel = console.input(f"\n[bold cyan]{i18n.t('prompt_select_mods')}[/] ").strip()
        if not raw_sel:
            console.print(f"[dim]{i18n.t('cancelled')}[/]")
            return 0
        try:
            indices = parse_selection(raw_sel, len(targets), i18n)
            break
        except ValueError as e:
            console.print(f"[red]{i18n.t('input_error', error=e)}[/]")

    chosen = [targets[i - 1] for i in indices]
    console.print(f"\n[bold]{i18n.t('selected_summary', count=len(chosen), lang=pz_lang, name=tgt_name)}[/]")

    try:
        for t in chosen:
            translate_mod_target(t, pz_lang, tgt_code, tgt_name, settings, rules_cfg, state, i18n, force)
    except KeyboardInterrupt:
        console.print(f"\n[yellow]{i18n.t('stopped_saved')}[/]")
        return 130

    console.print(f"\n[bold green]{i18n.t('done_all')}[/]")
    return 0


def run_mode_3(
    settings: AppSettings,
    rules_cfg: TokenRulesConfig,
    i18n: I18n,
    check_only: bool = False,
) -> int:
    state = load_state(settings.state_file)
    mods = state.get("mods", {})
    if not mods:
        console.print(f"\n[yellow]{i18n.t('state_empty', file=settings.state_file.name)}[/]")
        return 0

    entries = list(mods.items())
    if check_only:
        run_dry_check(state, [sid for sid, _ in entries], settings, rules_cfg, i18n)
        return 0

    src_lang = settings.default_source_lang.upper()
    table = Table(
        title=i18n.t("manage_title", count=len(entries)),
        box=box.ROUNDED,
        header_style="bold cyan",
    )
    table.add_column(i18n.t("col_num"), justify="right", style="cyan", no_wrap=True)
    table.add_column(i18n.t("col_mod"), style="bold white")
    table.add_column(i18n.t("col_workshop_id"), style="dim cyan", no_wrap=True)
    table.add_column(i18n.t("col_lang"), no_wrap=True)
    table.add_column(i18n.t("col_lines"), justify="right", no_wrap=True)
    table.add_column(i18n.t("col_in_game"), justify="center", no_wrap=True)
    table.add_column(i18n.t("col_in_mirror"), justify="center", no_wrap=True)
    table.add_column(i18n.t("col_updated"), style="dim", no_wrap=True)
    table.add_column(i18n.t("col_updates"))

    for idx, (_, entry) in enumerate(entries, 1):
        name = entry.get("mod_name", "?")
        if entry.get("version_tag"):
            name += f" [magenta][{entry['version_tag']}][/]"
        wid = entry.get("workshop_id") or "—"
        lang = entry.get("lang", "?")
        updated = entry.get("updated_at", "—")
        files_info = entry.get("files", {})
        keys_cnt = sum(f.get("translated_keys", 0) for f in files_info.values())
        fb_cnt = count_entry_fallbacks(entry)
        lang_badge = f"[yellow]{src_lang}/{lang} ({fb_cnt})[/]" if fb_cnt else f"[bold]{lang}[/]"

        total_files = len(files_info)
        game_exists = sum(1 for f in files_info.values() if Path(f["out_file"]).is_file())
        mirror_exists = sum(1 for f in files_info.values() if Path(f["mirror_file"]).is_file())

        g_color = "green" if game_exists == total_files else ("yellow" if game_exists > 0 else "red")
        m_color = "green" if mirror_exists == total_files else ("yellow" if mirror_exists > 0 else "red")

        update_note = "[dim]—[/]"
        t_dir = Path(entry["translate_dir"])
        if t_dir.exists():
            found, _ = find_translate_targets(t_dir, settings.default_source_lang)
            if found:
                p_keys, p_chars, new_cnt, chg_cnt, fix_cnt, *_ = estimate_translation_volume(
                    found[0], lang, state, rules_cfg.critical_rules, force=False
                )
                if p_keys > 0:
                    update_note = (
                        f"[yellow]{i18n.t('vol_pending_full', lines=format_num(p_keys), chars=format_num(p_chars))} "
                        f"{i18n.t('vol_diff_tag', new=new_cnt, chg=chg_cnt, fix=fix_cnt)}[/]"
                    )

        table.add_row(
            str(idx),
            name,
            wid,
            lang_badge,
            format_num(keys_cnt),
            f"[{g_color}]{game_exists}/{total_files}[/]",
            f"[{m_color}]{mirror_exists}/{total_files}[/]",
            updated,
            update_note,
        )

    console.print(table)

    while True:
        raw_sel = console.input(f"\n[bold cyan]{i18n.t('prompt_select_saved')}[/] ").strip()
        if not raw_sel:
            return 0
        try:
            indices = parse_selection(raw_sel, len(entries), i18n)
            break
        except ValueError as e:
            console.print(f"[red]{i18n.t('input_error', error=e)}[/]")

    selected_sids = [entries[i - 1][0] for i in indices]

    console.print(
        Panel(
            f"{i18n.t('manage_act_1')}\n"
            f"{i18n.t('manage_act_2')}\n"
            f"{i18n.t('manage_act_3')}\n"
            f"{i18n.t('manage_act_4')}\n"
            f"{i18n.t('manage_act_5')}",
            title=i18n.t("manage_actions_title"),
            border_style="cyan",
            box=box.ROUNDED,
        )
    )
    action = console.input(f"[bold cyan]{i18n.t('prompt_action')}[/] ").strip()

    if action in ("1", "2"):
        force_flag = action == "2"
        try:
            for sid in selected_sids:
                entry = mods[sid]
                t_dir = Path(entry["translate_dir"])
                lang = entry["lang"]
                if not t_dir.exists():
                    console.print(f"  [red][!] {i18n.t('folder_not_found', path=t_dir)}[/]")
                    continue
                found, _ = find_translate_targets(t_dir, settings.default_source_lang)
                if not found:
                    console.print(f"  [red][!] {i18n.t('no_source_json', path=t_dir)}[/]")
                    continue
                pz_lang, tgt_code, tgt_name = resolve_language(lang)
                translate_mod_target(
                    found[0], pz_lang, tgt_code, tgt_name, settings, rules_cfg, state, i18n, force=force_flag
                )
        except KeyboardInterrupt:
            console.print(f"\n[yellow]{i18n.t('stopped_saved')}[/]")
            return 130
    elif action == "3":
        restore_from_mirror(state, selected_sids, i18n)
    elif action == "4":
        console.print(
            Panel(
                f"{i18n.t('delete_scope_1')}\n"
                f"{i18n.t('delete_scope_2')}\n"
                f"{i18n.t('delete_scope_3')}",
                title=i18n.t("delete_scope_title"),
                border_style="red",
                box=box.ROUNDED,
            )
        )
        del_choice = console.input(f"[bold red]{i18n.t('prompt_delete_scope')}[/] ").strip()
        scope_map = {"1": "game", "2": "mirror", "3": "both"}
        if del_choice in scope_map:
            delete_tracked_translations(state, selected_sids, scope_map[del_choice], settings, i18n)
        else:
            console.print(f"[dim]{i18n.t('cancelled')}[/]")
    elif action == "5":
        run_dry_check(state, selected_sids, settings, rules_cfg, i18n)
    else:
        console.print(f"[yellow]{i18n.t('unknown_action')}[/]")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Project Zomboid Mod Translator (JSON) via TranslateGemma")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_FILE), help="Path to config.json")
    parser.add_argument("--rules", default=None, help="Path to token_rules.json")
    parser.add_argument("--mode", type=int, choices=[1, 2, 3], help="1 = single mod, 2 = scan all mods, 3 = manage")
    parser.add_argument("--path", default=None, help="Path to mod (mode 1) or mods root folder (mode 2)")
    parser.add_argument("--lang", default=None, help="Target game language (e.g. RU, DE, CN, JP)")
    parser.add_argument("--source-lang", default=None, help="Source language folder (default from config)")
    parser.add_argument("--host", default=None, help="llama-server host")
    parser.add_argument("--port", type=int, default=None, help="llama-server port")
    parser.add_argument("--ui-lang", default=None, help="Interface language code (e.g. en, ru)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing translations")
    parser.add_argument("--check", action="store_true", help="Dry-run token check in mode 3")
    args = parser.parse_args()

    cfg = load_config(Path(args.config))
    settings = build_settings(cfg, args)
    rules_cfg = load_token_rules(settings.token_rules_file)
    i18n = I18n(settings.ui_lang)

    if args.mode is not None or args.check:
        render_banner(settings, i18n)
        if args.check or args.mode == 3:
            return run_mode_3(settings, rules_cfg, i18n, check_only=args.check)
        if args.mode == 1:
            return run_mode_1(args.path, args.lang, settings, rules_cfg, i18n, args.force)
        if args.mode == 2:
            return run_mode_2(args.path, args.lang, settings, rules_cfg, i18n, args.force)

    # Interactive mode: step 1 is selecting interface language
    if not args.ui_lang:
        select_ui_language_interactive(i18n, settings.ui_lang)

    while True:
        render_banner(settings, i18n)
        console.print(
            Panel(
                f"{i18n.t('menu_opt_1')}\n"
                f"{i18n.t('menu_opt_2')}\n"
                f"{i18n.t('menu_opt_3')}\n"
                f"{i18n.t('menu_opt_4')}\n"
                f"{i18n.t('menu_opt_0')}",
                title=i18n.t("menu_title"),
                border_style="cyan",
                box=box.ROUNDED,
            )
        )
        choice = console.input(f"[bold cyan]{i18n.t('prompt_mode')}[/] ").strip()
        if choice == "0":
            return 0
        if choice == "4":
            select_ui_language_interactive(i18n, i18n.lang)
            continue
        if choice == "1":
            return run_mode_1(args.path, args.lang, settings, rules_cfg, i18n, args.force)
        if choice == "2":
            return run_mode_2(args.path, args.lang, settings, rules_cfg, i18n, args.force)
        if choice == "3":
            return run_mode_3(settings, rules_cfg, i18n)
        console.print(f"[red]{i18n.t('invalid_mode')}[/]")


if __name__ == "__main__":
    sys.exit(main())