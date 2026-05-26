"""Aqua / GOO Network API (Норвегия, Finn.no)."""

from __future__ import annotations

import os

from region import AQUA_DEFAULT_SERVICE, AQUA_GENERATE_DOMAIN
from services.user_settings import get_setting

AQUA_USER_API_KEY = "aqua_user_api_key"
AQUA_TEAM_API_KEY = "aqua_team_api_key"
AQUA_PROFILE_ID_KEY = "aqua_profile_id"
AQUA_PROFILE_PSEUDONYM_KEY = "aqua_profile_pseudonym"
AQUA_PROFILE_TITLE_KEY = "aqua_profile_title"
AQUA_PROFILE_NAME_KEY = "aqua_profile_name"
AQUA_PROFILE_ADDRESS_KEY = "aqua_profile_address"
AQUA_SERVICE_KEY = "aqua_service"
GAG_SERVICE_KEY = AQUA_SERVICE_KEY

# Старые ключи GAG (миграция настроек без потери данных)
_LEGACY_GAG_API_KEY = "gag_api_key"
_LEGACY_GAG_TITLE = "gag_profile_title"
_LEGACY_GAG_NAME = "gag_profile_name"
_LEGACY_GAG_ADDR = "gag_profile_address"
_LEGACY_GAG_SERVICE = "gag_service"


def aqua_generate_domain() -> str:
    return (os.getenv("AQUA_GENERATE_DOMAIN", AQUA_GENERATE_DOMAIN) or AQUA_GENERATE_DOMAIN).strip()


def aqua_api_base() -> str:
    """Norway/AQUA: legacy-хост api-old.goo.network (как Finkabot / Finland)."""
    return (
        os.getenv("GOO_API_BASE", "https://api-old.goo.network")
        or "https://api-old.goo.network"
    ).rstrip("/")


def aqua_api_host() -> str:
    from urllib.parse import urlparse

    try:
        return urlparse(aqua_api_base()).netloc or "api-old.goo.network"
    except Exception:
        return "api-old.goo.network"


def normalize_aqua_api_key(value: str | None) -> str:
    """Ключ без пробелов; убрать префикс Apikey, если вставили целиком."""
    from utils.secrets import clean_secret

    v = clean_secret(value)
    if not v:
        return ""
    low = v.lower()
    if low.startswith("apikey"):
        v = v[6:].lstrip(":").strip()
    return v


def normalize_aqua_service(code: str | None) -> str | None:
    s = (code or "").strip().lower()
    if not s:
        return None
    if s in {AQUA_DEFAULT_SERVICE, "finn.no", "finn"}:
        return AQUA_DEFAULT_SERVICE
    return None


def is_valid_aqua_service(code: str | None) -> bool:
    return normalize_aqua_service(code) is not None


def aqua_service_label(code: str | None) -> str:
    return "Finn.no" if normalize_aqua_service(code) == AQUA_DEFAULT_SERVICE else (code or "—")


def aqua_service_for_html_dir(code: str | None) -> str:
    return "finn_no"


async def get_user_aqua_api_key(user_id: int) -> str:
    k = normalize_aqua_api_key(await get_setting(user_id, AQUA_USER_API_KEY))
    if k:
        return k
    return normalize_aqua_api_key(await get_setting(user_id, _LEGACY_GAG_API_KEY))


def global_team_aqua_api_key() -> str:
    """Team key задаётся один раз на Railway (AQUA_TEAM_API_KEY), не у пользователей."""
    v = (os.getenv("AQUA_TEAM_API_KEY") or os.getenv("TEAM_API_KEY") or "").strip()
    if v:
        return normalize_aqua_api_key(v)
    try:
        import config

        return normalize_aqua_api_key(getattr(config, "AQUA_TEAM_API_KEY", "") or "")
    except Exception:
        return ""


async def get_team_aqua_api_key(user_id: int) -> str:
    g = global_team_aqua_api_key()
    if g:
        return g
    return normalize_aqua_api_key(await get_setting(user_id, AQUA_TEAM_API_KEY))


async def get_aqua_profile_id(user_id: int) -> str:
    return (await get_setting(user_id, AQUA_PROFILE_ID_KEY) or "").strip()


async def get_profile_field(user_id: int, new_key: str, legacy_key: str) -> str:
    v = (await get_setting(user_id, new_key) or "").strip()
    if v:
        return v
    return (await get_setting(user_id, legacy_key) or "").strip()
