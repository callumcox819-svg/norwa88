"""GAG Team API: ключ, сервис Finn.no (Норвегия)."""

from __future__ import annotations

from config import load_settings
from region import GAG_DEFAULT_SERVICE
from services.user_settings import get_setting

GAG_API_KEY = "gag_api_key"
GAG_PROFILE_TITLE_KEY = "gag_profile_title"
GAG_PROFILE_NAME_KEY = "gag_profile_name"
GAG_PROFILE_ADDRESS_KEY = "gag_profile_address"
GAG_SERVICE_KEY = "gag_service"
GAG_DOMAIN_SLOT_KEY = "gag_domain_slot"

GAG_SERVICE_CHOICES = (GAG_DEFAULT_SERVICE,)

_SERVICE_ALIASES: dict[str, str] = {
    "finn_no": "finn_no",
    "finn.no": "finn_no",
    "finn": "finn_no",
}


def normalize_gag_service(code: str | None) -> str | None:
    s = (code or "").strip().lower()
    if not s:
        return None
    return _SERVICE_ALIASES.get(s)


def is_valid_gag_service(code: str | None) -> bool:
    return normalize_gag_service(code) is not None


def gag_service_for_api(code: str | None) -> str:
    n = normalize_gag_service(code)
    if not n:
        raise ValueError(f"Unknown GAG service: {code!r}")
    return n


def gag_service_for_html_dir(code: str | None) -> str:
    """Имя папки в data/HTMLno/."""
    n = normalize_gag_service(code) or ""
    return n or "finn_no"


def gag_service_matches(cur: str | None, choice: str) -> bool:
    a = normalize_gag_service(cur)
    b = normalize_gag_service(choice)
    return bool(a and b and a == b)


def gag_service_label(code: str | None) -> str:
    n = normalize_gag_service(code) or (code or "").strip()
    return {"finn_no": "Finn.no"}.get(n, n or "—")


def gag_service_from_offer_link(link: str, *, user_fallback: str | None = None) -> str | None:
    l = (link or "").lower()
    if "finn.no" in l or "finnkode" in l:
        return GAG_DEFAULT_SERVICE
    if "facebook.com" in l or "fb.com/marketplace" in l:
        return GAG_DEFAULT_SERVICE
    return normalize_gag_service(user_fallback)


def resolve_gag_service(*, offer_link: str, user_setting: str | None) -> str | None:
    chosen = normalize_gag_service(user_setting)
    if chosen:
        return chosen
    return gag_service_from_offer_link(offer_link)


def parse_gag_domain_slot(raw: str | None) -> int | None:
    s = (raw or "").strip()
    if not s or s.lower() in {"team", "default", "0"}:
        return None
    try:
        v = int(s)
    except ValueError:
        return None
    return v if v in (1, 2, 3, 4) else None


def gag_api_domain_param(slot: int | None) -> int | None:
    if slot in (1, 2, 3, 4):
        return slot + 4
    return None


def gag_generate_endpoint() -> str:
    return load_settings().gag_generate_url


def gag_send_email_endpoint() -> str:
    return load_settings().gag_send_email_url


def gag_default_version() -> str:
    return load_settings().gag_default_version


async def get_user_gag_api_key(user_id: int) -> str:
    return (await get_setting(user_id, GAG_API_KEY) or "").strip()
