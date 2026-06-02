from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from database import db, now_utc
from utils.stylish_text import s

bot_assets = db["bot_assets"]


def is_owner(user_id: int | None) -> bool:
    return user_id == settings.owner_id


async def set_panel_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    if not is_owner(user.id):
        await message.reply_text(s("Owner access required."))
        return
    source = message.reply_to_message if message.reply_to_message and message.reply_to_message.photo else message
    if not source.photo:
        await message.reply_text(s("Reply to a photo with /setpanelphoto."))
        return
    bot_assets.update_one(
        {"key": "panel_photo"},
        {"$set": {"file_id": source.photo[-1].file_id, "updated_at": now_utc()}},
        upsert=True,
    )
    await message.reply_text(s("Panel photo saved for owner, settings, and event panels."))


async def send_panel_photo_or_text(message, text: str) -> None:
    asset = bot_assets.find_one({"key": "panel_photo"}) or {}
    file_id = asset.get("file_id")
    if file_id:
        await message.reply_photo(photo=file_id, caption=text)
    else:
        await message.reply_text(text)
