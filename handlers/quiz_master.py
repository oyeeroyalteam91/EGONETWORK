from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from database import db, now_utc
from utils.stylish_text import s

bot_settings = db["bot_settings"]


def is_owner(user_id: int | None) -> bool:
    return user_id == settings.owner_id


def quiz_master_state() -> bool:
    row = bot_settings.find_one({"key": "quiz_master"}) or {}
    return bool(row.get("active", False))


async def quiz_master(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    if not is_owner(user.id):
        await message.reply_text(s("Owner access required."))
        return

    action = context.args[0].lower().strip() if context.args else "status"
    if action in {"on", "start"}:
        bot_settings.update_one({"key": "quiz_master"}, {"$set": {"active": True, "updated_at": now_utc()}}, upsert=True)
        await message.reply_text(s("Quiz master is ON."))
        return
    if action in {"off", "stop"}:
        bot_settings.update_one({"key": "quiz_master"}, {"$set": {"active": False, "updated_at": now_utc()}}, upsert=True)
        await message.reply_text(s("Quiz master is OFF."))
        return

    state = "ON" if quiz_master_state() else "OFF"
    await message.reply_text(s(f"Quiz master: {state}"))
