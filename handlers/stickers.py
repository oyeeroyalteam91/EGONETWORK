from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from database import db, now_utc
from utils.stylish_text import s

stickers = db["stickers"]


def is_owner(user_id: int | None) -> bool:
    return user_id == settings.owner_id


async def add_sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    if not is_owner(user.id):
        await message.reply_text(s("Owner access required."))
        return
    if not context.args:
        await message.reply_text("Usage: /addsticker keyword")
        return
    source = message.reply_to_message
    if not source or not source.sticker:
        await message.reply_text(s("Reply to a sticker with /addsticker keyword."))
        return
    keyword = " ".join(context.args).lower().strip()
    stickers.update_one(
        {"keyword": keyword},
        {"$set": {"file_id": source.sticker.file_id, "updated_at": now_utc()}},
        upsert=True,
    )
    await message.reply_text(s(f"Sticker reply saved for: {keyword}"))


async def remove_sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    if not is_owner(user.id):
        await message.reply_text(s("Owner access required."))
        return
    if not context.args:
        await message.reply_text("Usage: /removesticker keyword")
        return
    keyword = " ".join(context.args).lower().strip()
    stickers.delete_one({"keyword": keyword})
    await message.reply_text(s(f"Sticker reply removed for: {keyword}"))


async def list_sticker_replies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return
    rows = list(stickers.find({}).sort("keyword", 1).limit(50))
    if not rows:
        await message.reply_text(s("No sticker replies saved yet."))
        return
    text = "Saved sticker replies:\n" + "\n".join(f"- {row.get('keyword')}" for row in rows)
    await message.reply_text(text)


async def maybe_reply_with_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    message = update.effective_message
    if not message or not message.text:
        return False
    text = message.text.lower()
    row = stickers.find_one({"keyword": {"$in": text.split()}})
    if not row:
        for item in stickers.find({}).limit(100):
            if item.get("keyword") and item["keyword"] in text:
                row = item
                break
    if not row:
        return False
    await message.reply_sticker(sticker=row["file_id"])
    return True
