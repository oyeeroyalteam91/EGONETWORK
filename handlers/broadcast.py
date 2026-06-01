from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from database import db
from utils.stylish_text import s

group_settings = db["group_settings"]


def is_owner(user_id: int | None) -> bool:
    return user_id == settings.owner_id


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    if not is_owner(user.id):
        await message.reply_text(s("Owner access required."))
        return
    text = " ".join(context.args).strip()
    if not text:
        await message.reply_text("Usage: /broadcast message")
        return

    sent = 0
    failed = 0
    for group in group_settings.find({}):
        chat_id = group.get("chat_id")
        if not chat_id:
            continue
        try:
            await context.bot.send_message(chat_id=chat_id, text=s(text))
            sent += 1
        except Exception:
            failed += 1
    await message.reply_text(s(f"Broadcast done. Sent: {sent}, Failed: {failed}"))
