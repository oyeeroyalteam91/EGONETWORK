from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from database import db, now_utc
from handlers.economy import add_coins
from utils.stylish_text import s

users = db["users"]
groups = db["group_settings"]
events = db["events"]
event_claims = db["event_claims"]

INDIA_TZ = ZoneInfo("Asia/Kolkata")
BIRTHDAY_COINS = 500
DEFAULT_EVENT_COINS = 250


def is_owner(user_id: int | None) -> bool:
    return user_id == settings.owner_id


def india_now() -> datetime:
    return datetime.now(INDIA_TZ)


def today_ddmm() -> str:
    return india_now().strftime("%d-%m")


def today_id() -> str:
    return india_now().strftime("%Y-%m-%d")


def clean_date(value: str) -> str | None:
    value = value.strip().replace("/", "-").replace(".", "-")
    parts = value.split("-")
    if len(parts) == 3:
        if len(parts[0]) == 4:
            day, month = parts[2], parts[1]
        else:
            day, month = parts[0], parts[1]
    elif len(parts) == 2:
        day, month = parts[0], parts[1]
    else:
        return None
    try:
        d = int(day)
        m = int(month)
        if 1 <= d <= 31 and 1 <= m <= 12:
            return f"{d:02d}-{m:02d}"
    except ValueError:
        return None
    return None


def user_name(row: dict) -> str:
    profile = row.get("profile") or {}
    return profile.get("name") or row.get("name") or row.get("username") or str(row.get("user_id"))


def was_done(key: str, user_id: int, day: str) -> bool:
    return event_claims.find_one({"key": key, "user_id": user_id, "day": day}) is not None


def mark_done(key: str, user_id: int, day: str) -> None:
    event_claims.update_one({"key": key, "user_id": user_id, "day": day}, {"$set": {"at": now_utc(), "timezone": "Asia/Kolkata"}}, upsert=True)


async def send_all_groups(context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    for group in groups.find({}):
        chat_id = group.get("chat_id")
        if not chat_id:
            continue
        try:
            await context.bot.send_message(chat_id=int(chat_id), text=text)
        except Exception:
            pass


async def events_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return
    rows = list(events.find({"enabled": True}).sort("date", 1).limit(20))
    lines = [s("EGO Event Control"), ""]
    lines.append("Calendar: India IST")
    lines.append("Birthday wishes: ON")
    lines.append(f"Birthday reward: {BIRTHDAY_COINS} coins")
    lines.append("Daily check: 12:05 AM IST")
    lines.append("")
    lines.append("Commands:")
    lines.append("/events")
    lines.append("/eventstatus")
    lines.append("/addevent key DD-MM coins name")
    lines.append("")
    lines.append("Saved events:")
    if not rows:
        lines.append("No custom events saved yet.")
    for row in rows:
        lines.append(f"{row.get('date')} | {row.get('name')} | {row.get('coins')} coins")
    await message.reply_text("\n".join(lines))


async def event_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return
    bday_count = users.count_documents({"profile.birthday": {"$exists": True}})
    event_count = events.count_documents({"enabled": True})
    text = (
        f"{s('Event Status')}\n\n"
        f"Calendar: Asia/Kolkata\n"
        f"Today: {today_id()}\n"
        f"Date key: {today_ddmm()}\n"
        f"Daily check: 12:05 AM IST\n"
        f"Birthdays saved: {bday_count}\n"
        f"Custom events: {event_count}\n"
        f"Birthday coins: {BIRTHDAY_COINS}\n"
    )
    await message.reply_text(text)


async def add_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    if not is_owner(user.id):
        await message.reply_text(s("Owner access required."))
        return
    if len(context.args) < 4:
        await message.reply_text("Usage: /addevent key DD-MM coins name")
        return
    key = context.args[0].lower().strip()
    date = clean_date(context.args[1])
    if not date:
        await message.reply_text("Use date format DD-MM")
        return
    coins = int(context.args[2])
    name = " ".join(context.args[3:]).strip()
    events.update_one({"key": key}, {"$set": {"date": date, "coins": coins, "name": name, "enabled": True, "timezone": "Asia/Kolkata", "updated_at": now_utc()}}, upsert=True)
    await message.reply_text(s(f"Event saved: {name}"))


async def daily_event_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    ddmm = today_ddmm()
    day = today_id()

    for row in users.find({"profile.birthday": {"$exists": True}}):
        user_id = int(row.get("user_id"))
        birthday = clean_date(str((row.get("profile") or {}).get("birthday", "")))
        if birthday != ddmm or was_done("birthday", user_id, day):
            continue
        total = add_coins(user_id, BIRTHDAY_COINS, "birthday")
        mark_done("birthday", user_id, day)
        await send_all_groups(context, s(f"Happy Birthday {user_name(row)}! Birthday reward: {BIRTHDAY_COINS} coins. Balance: {total}"))

    for event in events.find({"date": ddmm, "enabled": True}):
        key = str(event.get("key"))
        name = str(event.get("name", "Event"))
        coins = int(event.get("coins", DEFAULT_EVENT_COINS))
        given = 0
        for row in users.find({"user_id": {"$exists": True}}):
            user_id = int(row.get("user_id"))
            claim_key = f"event_{key}"
            if was_done(claim_key, user_id, day):
                continue
            add_coins(user_id, coins, claim_key)
            mark_done(claim_key, user_id, day)
            given += 1
        if given:
            await send_all_groups(context, s(f"{name} event reward distributed: {coins} coins to {given} members."))
