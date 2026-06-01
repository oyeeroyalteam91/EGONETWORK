from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from database import db, now_utc, upsert_user
from utils.stylish_text import s

points = db["points"]
users = db["users"]


def is_owner(user_id: int | None) -> bool:
    return user_id == settings.owner_id


def display_name(user_id: int) -> str:
    user = users.find_one({"user_id": user_id}) or {}
    if user.get("username"):
        return f"@{user['username']}"
    if user.get("name"):
        return str(user["name"])
    return str(user_id)


def add_points(user_id: int, chat_id: int, amount: int) -> int:
    result = points.find_one_and_update(
        {"user_id": user_id, "chat_id": chat_id},
        {"$inc": {"points": amount}, "$set": {"updated_at": now_utc()}, "$setOnInsert": {"created_at": now_utc()}},
        upsert=True,
        return_document=True,
    )
    return int(result.get("points", amount)) if result else amount


async def reward_activity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if not message or not user or not chat or user.is_bot:
        return
    upsert_user(user.id, {"name": user.full_name, "username": user.username})
    if chat.type not in {"group", "supergroup"}:
        return
    add_points(user.id, chat.id, 1)


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    chat = update.effective_chat
    if not message or not chat:
        return

    rows = list(points.find({"chat_id": chat.id}).sort("points", -1).limit(10))
    if not rows:
        await message.reply_text(s("Leaderboard is empty."))
        return

    lines = [s("EGO Leaderboard"), ""]
    medals = ["🥇", "🥈", "🥉"]
    for index, row in enumerate(rows, start=1):
        prefix = medals[index - 1] if index <= 3 else f"{index}."
        name = display_name(int(row["user_id"]))
        lines.append(f"{prefix} {name} — {row.get('points', 0)} pts")
    await message.reply_text("\n".join(lines))


async def add_manual_points(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not message or not chat or not user:
        return
    if not is_owner(user.id):
        await message.reply_text(s("Owner access required."))
        return
    if not context.args or len(context.args) < 2:
        await message.reply_text("Usage: /addpoints user_id amount")
        return
    target_id = int(context.args[0])
    amount = int(context.args[1])
    total = add_points(target_id, chat.id, amount)
    await message.reply_text(s(f"Points updated. Total: {total}"))
