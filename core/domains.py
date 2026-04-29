"""Сборка hostlist.txt из включённых групп доменов."""
import logging
from pathlib import Path

log = logging.getLogger(__name__)

LISTS_DIR = Path(__file__).parent.parent / "lists"

# Все доступные группы и их .txt файлы
DOMAIN_GROUPS: dict[str, str] = {
    "Discord":         "discord.txt",
    "YouTube":         "youtube.txt",
    "Faceit":          "faceit.txt",   # faceit.com
    "Instagram/Meta":  "instagram.txt",
    "Twitter/X":       "twitter.txt",
    "Twitch":          "twitch.txt",
    "Steam":           "steam.txt",
    "Epic/Riot":       "epic.txt",
    "Spotify":         "spotify.txt",
    "TikTok":          "tiktok.txt",
    "Telegram":        "telegram.txt",
}


def load_group(group_name: str) -> list[str]:
    """Читает домены группы из .txt файла."""
    filename = DOMAIN_GROUPS.get(group_name)
    if not filename:
        return []
    path = LISTS_DIR / filename
    if not path.exists():
        log.warning("Файл доменов не найден: %s", path)
        return []
    domains = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                domains.append(line)
    return domains


def build_hostlist(enabled_groups: list[str], output_path: str | None = None) -> Path:
    """Собирает hostlist.txt из включённых групп, без дубликатов."""
    seen: set[str] = set()
    all_domains: list[str] = []

    for group in enabled_groups:
        for domain in load_group(group):
            if domain not in seen:
                seen.add(domain)
                all_domains.append(domain)

    if output_path is None:
        output_path = str(LISTS_DIR / "hostlist.txt")

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(all_domains)))

    log.info("hostlist.txt собран: %d доменов → %s", len(all_domains), out)
    return out


def get_all_groups() -> list[str]:
    return list(DOMAIN_GROUPS.keys())
