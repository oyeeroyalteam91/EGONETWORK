from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from database import db, now_utc
from utils.stylish_text import s

custom_pics = db["custom_pics"]


async def set_custom_pic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return

    target = message.reply_to_message
    photo_source = target if target and target.photo else message
    if not photo_source.photo:
        await message.reply_text(s("Send /setpic with a photo or reply to a photo with /setpic."))
        return

    title = " ".join(context.args).strip() if context.args else "default"
    file_id = photo_source.photo[-1].file_id
    custom_pics.update_one(
        {"owner_id": user.id, "title": title},
        {"$set": {"file_id": file_id, "updated_at": now_utc()}, "$setOnInsert": {"created_at": now_utc()}},
        upsert=True,
    )
    await message.reply_text(s(f"Custom pic saved as {title}."))


async def get_custom_pic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return

    title = " ".join(context.args).strip() if context.args else "default"
    item = custom_pics.find_one({"owner_id": user.id, "title": title})
    if not item:
        await message.reply_text(s("No custom pic found with this name."))
        return
    await message.reply_photo(photo=item["file_id"], caption=s(f"Custom pic: {title}"))


async def list_custom_pics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return

    items = list(custom_pics.find({"owner_id": user.id}).limit(20))
    if not items:
        await message.reply_text(s("No custom pics saved yet."))
        return
    names = "\n".join(f"- {item.get('title', 'default')}" for item in items)
    await message.reply_text(f"{s('Saved Custom Pics')}\n{names}")
