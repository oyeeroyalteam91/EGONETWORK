from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from database import db, now_utc
from handlers.panel_photo import send_panel_photo_or_text
from utils.stylish_text import s

group_settings = db["group_settings"]


def is_owner(user_id: int | None) -> bool:
    return user_id == settings.owner_id


async def save_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if not chat or chat.type not in {"group", "supergroup"}:
        return
    group_settings.update_one(
        {"chat_id": chat.id},
        {"$set": {"title": chat.title, "updated_at": now_utc()}, "$setOnInsert": {"created_at": now_utc(), "verification_enabled": True}},
        upsert=True,
    )


async def group_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if not message or not user or not chat:
        return
    if not is_owner(user.id):
        await message.reply_text(s("Owner access required."))
        return
    data = group_settings.find_one({"chat_id": chat.id}) or {}
    text = (
        f"{s('Group Settings')}\n"
        f"{settings.network_name} | {settings.est_year}\n\n"
        f"Verification: {data.get('verification_enabled', True)}\n"
        f"Welcome Pic: {'Set' if data.get('welcome_pic') else 'Not set'}\n"
        f"Start Pic: {'Set' if data.get('start_pic') else 'Not set'}\n\n"
        "/verifyon\n/verifyoff\n/setwelcome\n/setstartpic\n/setpanelphoto"
    )
    await send_panel_photo_or_text(message, text)


async def verify_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if not message or not user or not chat:
        return
    if not is_owner(user.id):
        await message.reply_text(s("Owner access required."))
        return
    group_settings.update_one({"chat_id": chat.id}, {"$set": {"verification_enabled": True, "updated_at": now_utc()}}, upsert=True)
    await message.reply_text(s("Verification enabled."))


async def verify_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if not message or not user or not chat:
        return
    if not is_owner(user.id):
        await message.reply_text(s("Owner access required."))
        return
    group_settings.update_one({"chat_id": chat.id}, {"$set": {"verification_enabled": False, "updated_at": now_utc()}}, upsert=True)
    await message.reply_text(s("Verification disabled."))


async def set_welcome_pic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if not message or not user or not chat:
        return
    if not is_owner(user.id):
        await message.reply_text(s("Owner access required."))
        return
    source = message.reply_to_message if message.reply_to_message and message.reply_to_message.photo else message
    if not source.photo:
        await message.reply_text(s("Reply to a photo with /setwelcome."))
        return
    group_settings.update_one({"chat_id": chat.id}, {"$set": {"welcome_pic": source.photo[-1].file_id, "updated_at": now_utc()}}, upsert=True)
    await message.reply_text(s("Welcome pic saved."))


async def set_start_pic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if not message or not user or not chat:
        return
    if not is_owner(user.id):
        await message.reply_text(s("Owner access required."))
        return
    source = message.reply_to_message if message.reply_to_message and message.reply_to_message.photo else message
    if not source.photo:
        await message.reply_text(s("Reply to a photo with /setstartpic."))
        return
    group_settings.update_one({"chat_id": chat.id}, {"$set": {"start_pic": source.photo[-1].file_id, "updated_at": now_utc()}}, upsert=True)
    await message.reply_text(s("Start pic saved."))
