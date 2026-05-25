"""Домены для валидации (приоритет из настроек, дефолт — Норвегия)."""

from __future__ import annotations

import json
import re

from region import DEFAULT_VALIDATION_DOMAINS
from services.user_settings import get_setting, set_setting

DOMAIN_PRIORITY_KEY = "domain_priority"
_NORWAY_DEFAULTS_SEEDED_KEY = "norway_domains_seeded"


async def get_validation_domains(user_id: int) -> list[str]:
    raw = await get_setting(user_id, DOMAIN_PRIORITY_KEY)
    try:
        items = json.loads(raw) if raw else []
    except json.JSONDecodeError:
        items = []
    if not isinstance(items, list):
        items = []
    out: list[str] = []
    seen: set[str] = set()
    for x in items:
        d = re.sub(r"^https?://", "", str(x).strip().lower())
        d = d.split("/")[0].strip()
        if d and d not in seen:
            seen.add(d)
            out.append(d)
    return out


async def ensure_norway_default_domains(user_id: int) -> None:
    """Один раз подставить норвежский приоритет доменов, если список пуст."""
    if await get_setting(user_id, _NORWAY_DEFAULTS_SEEDED_KEY):
        return
    if await get_validation_domains(user_id):
        await set_setting(user_id, _NORWAY_DEFAULTS_SEEDED_KEY, "1")
        return
    await set_setting(
        user_id,
        DOMAIN_PRIORITY_KEY,
        json.dumps(list(DEFAULT_VALIDATION_DOMAINS)),
    )
    await set_setting(user_id, _NORWAY_DEFAULTS_SEEDED_KEY, "1")
