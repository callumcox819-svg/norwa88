"""Региональные настройки бота (Норвегия / Finn.no)."""

from __future__ import annotations

import os

BOT_DISPLAY_NAME = "Poputka88 Norway"
MARKETPLACE_NAME = "Finn.no"

# Код service в GAG API — переопредели в Variables, когда дашь точное значение
GAG_DEFAULT_SERVICE = (os.getenv("GAG_DEFAULT_SERVICE", "finn_no") or "finn_no").strip()

HTML_DATA_DIR = "HTMLno"

# Домены для ValidEmail при первом входе (приоритет отправки)
DEFAULT_VALIDATION_DOMAINS: tuple[str, ...] = (
    "online.no",
    "gmail.com",
    "hotmail.com",
    "outlook.com",
    "yahoo.com",
    "icloud.com",
    "live.no",
    "me.com",
)


def format_item_price(price: str) -> str:
    """Цена в письмах/HTML: NOK, если валюта не указана."""
    p = (price or "").strip()
    if not p:
        return ""
    upper = p.upper()
    if upper.startswith("NOK") or upper.startswith("KR"):
        return p
    if any(upper.startswith(c) for c in ("CHF", "EUR", "USD", "GBP", "SEK", "DKK")):
        return p
    return f"{p} kr"
