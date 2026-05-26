"""Aqua / GOO Network: профиль (profileID) и личный User API key."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from keyboards.main_menu import main_keyboard
from region import AQUA_DEFAULT_SERVICE, AQUA_GENERATE_DOMAIN
from services.aqua_keys import (
    AQUA_PROFILE_ADDRESS_KEY,
    AQUA_PROFILE_ID_KEY,
    AQUA_PROFILE_NAME_KEY,
    AQUA_PROFILE_PSEUDONYM_KEY,
    AQUA_PROFILE_TITLE_KEY,
    AQUA_USER_API_KEY,
    global_team_aqua_api_key,
)
from services.aqua_user import format_aqua_profile_message, load_aqua_profile
from services.user_settings import get_setting, set_setting
from utils.callback_edit import cq_edit_text
from utils.secrets import clean_secret
from utils.text_html import e

router = Router(name="aqua_settings")

AQUA_API_DOCS = (
    "📖 <b>GOO Network API</b>\n\n"
    "<b>Генерация ссылки (с парсером)</b>\n"
    "<code>POST https://api.goo.network/api/generate/single/parse</code>\n"
    "• <code>service</code> — <code>finn_no</code>\n"
    "• <code>url</code> — ссылка на объявление\n"
    "• <code>profileID</code> — ID из Aqua (🟢 токен в шапке профиля)\n"
    "• <code>domain</code> — <code>OLD</code>\n\n"
    "<b>Без парсера</b>\n"
    "<code>POST .../api/generate/single/no-parse</code>\n"
    "• <code>name</code>, <code>price</code>, <code>image</code>\n\n"
    "Заголовки: <code>Authorization: Apikey &lt;User&gt;</code>, "
    "<code>X-Team-Key</code> — задаётся на сервере (Railway).\n\n"
    "🇳🇴 <b>Aqua</b> · Норвегия"
)


class AquaKeysState(StatesGroup):
    user_key = State()


class AquaProfileState(StatesGroup):
    profile_id = State()
    pseudonym = State()
    title = State()
    name = State()
    address = State()


def _back_settings() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="settings_open")]
        ]
    )


def _profile_kb(*, has_user_key: bool) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🆔 profileID (Aqua)", callback_data="aqua_set:profile_id"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔑 User API key", callback_data="aqua_set:user_key"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Название / ФИО / адрес", callback_data="aqua_profile_edit"
                )
            ],
            [InlineKeyboardButton(text="📖 API", callback_data="aqua_api_docs")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="settings_open")],
            [InlineKeyboardButton(text="🍀 Скрыть", callback_data="ref_hide")],
        ]
    )


async def _render_profile(target: Message | CallbackQuery, *, edit: bool = False) -> None:
    uid = int(target.from_user.id)
    un = (target.from_user.username or "").strip()
    p = await load_aqua_profile(uid, username=un, telegram_id=uid)
    team_ok = bool(global_team_aqua_api_key() or p.team_key_set)
    team_line = (
        "🟢 Team key на сервере"
        if team_ok
        else "🔴 Team key: задайте <code>AQUA_TEAM_API_KEY</code> в Railway"
    )
    text = (
        format_aqua_profile_message(p)
        + f"\n\n{team_line}\n"
        f"🌐 Домен: <code>{e(AQUA_GENERATE_DOMAIN)}</code> · "
        f"📦 <code>{e(AQUA_DEFAULT_SERVICE)}</code>"
    )
    kb = _profile_kb(has_user_key=p.user_key_set)
    if isinstance(target, CallbackQuery):
        await cq_edit_text(target, text, reply_markup=kb)
    elif edit and target.bot:
        await target.bot.edit_message_text(
            text,
            chat_id=target.chat.id,
            message_id=target.message_id,
            reply_markup=kb,
            parse_mode="HTML",
        )
    else:
        await target.answer(text, reply_markup=kb, parse_mode="HTML")


@router.message(F.text.in_({"📋 Профиль", "Профиль"}))
async def cmd_profile_legacy(message: Message, state: FSMContext) -> None:
    """Старая reply-кнопка — открыть профиль из настроек."""
    await state.clear()
    await _render_profile(message)


@router.callback_query(F.data.in_({"aqua_show:profile", "gag_show:profile"}))
async def aqua_show_profile(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await _render_profile(callback)
    await callback.answer()


@router.callback_query(F.data.in_({"aqua_show:keys", "gag_show:key", "aqua_show:key"}))
async def aqua_show_keys_compat(callback: CallbackQuery, state: FSMContext) -> None:
    """Старые кнопки «Ключи Aqua» → экран профиля."""
    await aqua_show_profile(callback, state)


@router.callback_query(F.data == "aqua_api_docs")
async def aqua_api_docs(callback: CallbackQuery) -> None:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="aqua_show:profile")]
        ]
    )
    await cq_edit_text(callback, AQUA_API_DOCS, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "aqua_set:user_key")
async def aqua_set_user_key(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AquaKeysState.user_key)
    cur = (await get_setting(callback.from_user.id, AQUA_USER_API_KEY) or "").strip()
    hint = f"{cur[:8]}…" if len(cur) > 8 else (cur or "—")
    await cq_edit_text(
        callback,
        "✍️ <b>User API key</b> (личный, для генерации ссылок)\n\n"
        f"Сейчас: <code>{e(hint)}</code>\n\n"
        "Authorization: <code>Apikey …</code> из Aqua.\n"
        "Отмена: <code>-</code>",
        reply_markup=_back_settings(),
    )
    await callback.answer()


@router.message(AquaKeysState.user_key)
async def aqua_save_user_key(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    if raw == "-":
        await state.clear()
        await message.answer("Отменено.", reply_markup=main_keyboard())
        return
    val = clean_secret(raw)
    if not val:
        await message.answer("Пустой ключ.")
        return
    await set_setting(message.from_user.id, AQUA_USER_API_KEY, val)
    await state.clear()
    await message.answer("✅ User API key сохранён.", reply_markup=main_keyboard())


@router.callback_query(F.data == "aqua_set:profile_id")
async def aqua_set_profile_id_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AquaProfileState.profile_id)
    cur = (await get_setting(callback.from_user.id, AQUA_PROFILE_ID_KEY) or "").strip()
    await cq_edit_text(
        callback,
        "🆔 <b>profileID</b> из Aqua\n\n"
        f"Сейчас: <code>{e(cur or '—')}</code>\n\n"
        "Вставь зелёный токен из профиля Aqua (как в Finn-боте).\n"
        "Отмена: <code>-</code>",
        reply_markup=_back_settings(),
    )
    await callback.answer()


@router.message(AquaProfileState.profile_id)
async def aqua_save_profile_id(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    if raw == "-":
        await state.clear()
        await message.answer("Отменено.", reply_markup=main_keyboard())
        return
    pid = clean_secret(raw)
    if not pid:
        await message.answer("Пустой profileID.")
        return
    await set_setting(message.from_user.id, AQUA_PROFILE_ID_KEY, pid)
    await set_setting(message.from_user.id, "aqua_service", AQUA_DEFAULT_SERVICE)
    await state.clear()
    await message.answer("✅ profileID сохранён.", reply_markup=main_keyboard())


@router.callback_query(F.data == "aqua_profile_edit")
async def aqua_profile_edit(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AquaProfileState.pseudonym)
    p = await load_aqua_profile(
        callback.from_user.id,
        username=callback.from_user.username or "",
        telegram_id=callback.from_user.id,
    )
    await state.update_data(
        profile_pseudonym=p.pseudonym,
        profile_title=p.title,
        profile_name=p.name,
    )
    await cq_edit_text(
        callback,
        "✏️ <b>Доп. поля профиля</b> (для писем и no-parse)\n\n"
        "Шаг 1/4 — <b>Псевдоним</b>\n"
        f"Сейчас: <code>{e(p.pseudonym or '—')}</code>\n"
        "Пропустить: <code>-</code>",
        reply_markup=_back_settings(),
    )
    await callback.answer()


@router.message(AquaProfileState.pseudonym)
async def aqua_profile_pseudonym(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    data = await state.get_data()
    if raw != "-":
        await state.update_data(profile_pseudonym=raw)
    await state.set_state(AquaProfileState.title)
    await message.answer(
        "Шаг 2/4 — <b>Название</b>\n"
        f"Сейчас: <code>{e(data.get('profile_title') or '—')}</code>",
        parse_mode="HTML",
    )


@router.message(AquaProfileState.title)
async def aqua_profile_title(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    if raw != "-":
        await state.update_data(profile_title=raw)
    await state.set_state(AquaProfileState.name)
    await message.answer("Шаг 3/4 — <b>ФИО</b> покупателя", parse_mode="HTML")


@router.message(AquaProfileState.name)
async def aqua_profile_name(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    if raw != "-":
        await state.update_data(profile_name=raw)
    await state.set_state(AquaProfileState.address)
    await message.answer("Шаг 4/4 — <b>Адрес</b>", parse_mode="HTML")


@router.message(AquaProfileState.address)
async def aqua_profile_address(message: Message, state: FSMContext) -> None:
    uid = message.from_user.id
    raw = (message.text or "").strip()
    data = await state.get_data()
    if raw != "-":
        await state.update_data(profile_address=raw)
    data = await state.get_data()
    if data.get("profile_pseudonym") is not None:
        await set_setting(uid, AQUA_PROFILE_PSEUDONYM_KEY, str(data.get("profile_pseudonym") or ""))
    if data.get("profile_title"):
        await set_setting(uid, AQUA_PROFILE_TITLE_KEY, str(data["profile_title"]))
    if data.get("profile_name"):
        await set_setting(uid, AQUA_PROFILE_NAME_KEY, str(data["profile_name"]))
    if data.get("profile_address"):
        await set_setting(uid, AQUA_PROFILE_ADDRESS_KEY, str(data["profile_address"]))
    await set_setting(uid, "aqua_service", AQUA_DEFAULT_SERVICE)
    await state.clear()
    await message.answer("✅ Поля профиля сохранены.", reply_markup=main_keyboard())
