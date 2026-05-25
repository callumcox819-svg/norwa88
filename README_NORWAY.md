# Poputka88 Norway

Отдельный Telegram-бот на базе [poputka88](https://github.com/callumcox819-svg/poputka88) для **Норвегии** (маркетплейс **Finn.no**).

Исходник скопирован из `telegram-mailer-bot` (poputka88). Швейцарские сервисы (tutti/post/ricardo) заменены на **Finn.no**; HTML-шаблоны лежат в `data/HTMLno/finn_no/`.

## Что нужно от тебя

1. **BOT_TOKEN** — новый бот в [@BotFather](https://t.me/BotFather).
2. **ADMIN_IDS** — твой Telegram ID.
3. **VALIDEMAIL_API_KEY** (и при необходимости `_2` … `_5`).
4. **Команды BotFather** — когда будут готовы, вставь в `BOTFATHER_COMMANDS.txt` и выполни:
   ```powershell
   cd C:\Users\user\Desktop\poputka88-norway
   .venv\Scripts\python scripts\set_commands.py
   ```
5. **GAG API** — если код сервиса в API не `finn_no`, задай на Railway / в `.env`:
   ```
   GAG_DEFAULT_SERVICE=твой_код_из_gag
   ```

## Быстрый старт (локально)

```powershell
cd C:\Users\user\Desktop\poputka88-norway
copy config.example.py config_local.py
# отредактируй config_local.py: BOT_TOKEN, ADMIN_IDS, ключи

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python bot.py
```

## Домены валидации (по умолчанию)

При первом `/start` подставляется приоритет:

`online.no`, `gmail.com`, `hotmail.com`, `outlook.com`, `yahoo.com`, `icloud.com`, `live.no`, `me.com`

Изменить: **⚙️ Настройки → 📊 Приоритет отправки**.

## Railway (как poputka88)

**Пошагово:** `RAILWAY_NORWA88.txt`

1. **PostgreSQL** в проекте + `DATABASE_URL` = Reference на оба сервиса.
2. **norwa88** — `python bot.py`, `IMAP_DEDICATED_WORKER=1`.
3. **imap-worker** — `python imap_worker.py`, `ENABLE_INCOMING_MAIL=1`, тот же Postgres и `BOT_TOKEN`.

Без Postgres данные живут только в SQLite внутри контейнера и **сбрасываются при деплое**.

## Отличия от poputka88 (CH)

| | poputka88 | poputka88-norway |
|---|-----------|------------------|
| Сервис GAG | tutti / post / ricardo | **finn_no** |
| HTML | `data/HTMLch/` | `data/HTMLno/finn_no/` |
| Цена в письмах | CHF | **kr / NOK** |
| IMAP метки | .ch | **finn.no** |
