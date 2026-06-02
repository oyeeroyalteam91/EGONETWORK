from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from database import db, now_utc
from utils.stylish_text import s

auto_quiz_chats = db["auto_quiz_chats"]


async def autoquiz_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    chat = update.effective_chat
    if not message or not chat:
        return

    current = auto_quiz_chats.find_one({"chat_id": chat.id}) or {}
    enabled = bool(current.get("enabled", False))
    new_state = not enabled

    auto_quiz_chats.update_one(
        {"chat_id": chat.id},
        {"$set": {"enabled": new_state, "updated_at": now_utc()}},
        upsert=True,
    )

    if new_state:
        await message.reply_text(s("Auto quiz enabled. Anime and GK quizzes will run every 30 minutes."))
    else:
        await message.reply_text(s("Auto quiz disabled."))
