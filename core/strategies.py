"""Парсинг и загрузка JSON-стратегий из папки strategies/."""
import json
import logging
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

STRATEGIES_DIR = Path(__file__).parent.parent / "strategies"

# Порядок и группировка стратегий
STRATEGY_GROUPS: dict[str, list[str]] = {
    "ALT": ["ALT", "ALT2", "ALT3", "ALT4", "ALT5", "ALT6",
            "ALT7", "ALT8", "ALT9", "ALT10", "ALT11"],
    "FAKE TLS AUTO": ["FAKE TLS AUTO", "FAKE TLS AUTO ALT",
                      "FAKE TLS AUTO ALT2", "FAKE TLS AUTO ALT3"],
    "SIMPLE FAKE": ["SIMPLE FAKE", "SIMPLE FAKE ALT", "SIMPLE FAKE ALT2"],
    "General": ["general"],
}

ALL_STRATEGIES: list[str] = [s for group in STRATEGY_GROUPS.values() for s in group]


def _strategy_file(name: str) -> Path:
    safe = name.replace(" ", "_").replace("/", "_")
    return STRATEGIES_DIR / f"{safe}.json"


def load_strategy(name: str) -> dict[str, Any]:
    """Загружает JSON стратегии по имени. Возвращает {"name": ..., "args": [...]}."""
    path = _strategy_file(name)
    if not path.exists():
        log.warning("Файл стратегии не найден: %s", path)
        return {"name": name, "args": []}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log.error("Ошибка чтения стратегии %s: %s", name, e)
        return {"name": name, "args": []}


def get_args(name: str) -> list[str]:
    """Возвращает список аргументов winws.exe для стратегии."""
    return load_strategy(name).get("args", [])


def get_group(name: str) -> str:
    """Возвращает группу, к которой принадлежит стратегия."""
    for group, members in STRATEGY_GROUPS.items():
        if name in members:
            return group
    return "General"


def list_strategies() -> list[str]:
    """Возвращает список всех доступных стратегий."""
    return ALL_STRATEGIES
