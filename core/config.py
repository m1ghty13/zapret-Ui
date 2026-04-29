"""Загрузка/сохранение config.json."""
import json
import logging
import os
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

# Конфиг лежит рядом с .exe или в корне проекта
_CONFIG_PATH = Path(__file__).parent.parent / "config.json"

_DEFAULTS: dict[str, Any] = {
    "current_strategy": "ALT",
    "enabled_groups": ["Discord", "YouTube"],
    "autostart": False,
    "minimize_to_tray": True,
    "auto_test_on_first_run": True,
    "is_first_run": True,
    "secure_dns_hint": True,
    "winws_path": "bin/winws.exe",
    "hostlist_path": "lists/hostlist.txt",
    "tested_strategies": {},   # { "ALT": {"score": 3, "total": 5, "status": "works"} }
    "test_domains": ["discord.com", "youtube.com", "instagram.com"],
}

_data: dict[str, Any] = {}


def load() -> None:
    global _data
    _data = dict(_DEFAULTS)
    if _CONFIG_PATH.exists():
        try:
            with open(_CONFIG_PATH, encoding="utf-8") as f:
                saved = json.load(f)
            _data.update(saved)
            log.debug("Конфиг загружен: %s", _CONFIG_PATH)
        except Exception as e:
            log.warning("Не удалось прочитать конфиг: %s", e)
    else:
        save()


def save() -> None:
    try:
        with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log.error("Не удалось сохранить конфиг: %s", e)


def get(key: str, default: Any = None) -> Any:
    return _data.get(key, default)


def set(key: str, value: Any) -> None:  # noqa: A001
    _data[key] = value
    save()


def get_all() -> dict[str, Any]:
    return dict(_data)
