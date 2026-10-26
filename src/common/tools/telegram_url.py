from __future__ import annotations

from urllib.parse import urlparse

_TELEGRAM_WEB_HOSTS = frozenset(
    {
        "t.me",
        "telegram.me",
        "www.t.me",
        "www.telegram.me",
    }
)


def is_valid_telegram_url(url: str) -> bool:
    raw = url.strip()
    if not raw:
        return False
    parsed = urlparse(raw)
    scheme = parsed.scheme.lower()
    if scheme in ("http", "https"):
        host = parsed.hostname
        if host is None:
            return False
        return host.lower() in _TELEGRAM_WEB_HOSTS
    if scheme == "tg":
        return True
    return False
