from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from database import warnings
from utils.stylish_text import s


def is_owner(user_id: int | None) -> bool:
    return user_id == settings.owner_id


async def show_warnings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not message or not chat or not user:
        return
    if not is_owner(user.id):
        await message.reply_text(s("Owner access required."))
        return
    if not context.args:
        await message.reply_text("Usage: /warns user_id")
        return
    target_id = int(context.args[0])
    record = warnings.find_one({"chat_id": chat.id, "user_id": target_id}) or {}
    count = record.get("count", 0)
    await message.reply_text(s(f"Warning count for {target_id}: {count}"))


async def clear_warnings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not message or not chat or not user:
        return
    if not is_owner(user.id):
        await message.reply_text(s("Owner access required."))
        return
    if not context.args:
        await message.reply_text("Usage: /clearwarns user_id")
        return
    target_id = int(context.args[0])
    warnings.delete_one({"chat_id": chat.id, "user_id": target_id})
    await message.reply_text(s(f"Warnings cleared for {target_id}."))
