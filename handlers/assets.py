from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from database import db, now_utc
from utils.stylish_text import s

bot_assets = db["bot_assets"]


def is_owner(user_id: int | None) -> bool:
    return user_id == settings.owner_id


async def set_start_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    if not is_owner(user.id):
        await message.reply_text(s("Owner access required."))
        return
    source = message.reply_to_message if message.reply_to_message else message
    media_type = None
    file_id = None
    if source.video:
        media_type = "video"
        file_id = source.video.file_id
    elif source.animation:
        media_type = "animation"
        file_id = source.animation.file_id
    elif source.photo:
        media_type = "photo"
        file_id = source.photo[-1].file_id
    if not file_id:
        await message.reply_text(s("Reply to a photo, video, or GIF with /setstartmedia."))
        return
    bot_assets.update_one(
        {"key": "start_media"},
        {"$set": {"file_id": file_id, "media_type": media_type, "updated_at": now_utc()}},
        upsert=True,
    )
    await message.reply_text(s("Start media saved. It will attach with the start message caption."))


async def show_start_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return
    asset = bot_assets.find_one({"key": "start_media"}) or {}
    if not asset.get("file_id"):
        await message.reply_text(s("No start media saved yet."))
        return
    await message.reply_text(s(f"Start media type: {asset.get('media_type', 'unknown')}"))
