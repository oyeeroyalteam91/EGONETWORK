from __future__ import annotations

from telegram import ChatPermissions, Update
from telegram.ext import ContextTypes

from config import settings
from database import db, now_utc
from utils.stylish_text import s

admin_records = db["admin_records"]


def is_owner(user_id: int | None) -> bool:
    return user_id == settings.owner_id


async def owner_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    if not is_owner(user.id):
        await message.reply_text(s("Owner access required."))
        return
    text = (
        f"{s('Owner Panel')}\n\n"
        "/owner - show owner panel\n"
        "/restrict user_id reason - add global restriction record\n"
        "/allow user_id - remove global restriction record\n"
        "/warns user_id - show warning count\n"
        "/clearwarns user_id - clear warnings\n"
        "/broadcast message - send owner message to saved groups\n"
    )
    await message.reply_text(text)


async def restrict_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    if not is_owner(user.id):
        await message.reply_text(s("Owner access required."))
        return
    if not context.args:
        await message.reply_text("Usage: /restrict user_id reason")
        return
    target_id = int(context.args[0])
    reason = " ".join(context.args[1:]) or "No reason provided"
    admin_records.update_one(
        {"type": "global_restriction", "user_id": target_id},
        {"$set": {"reason": reason, "by": user.id, "updated_at": now_utc()}, "$setOnInsert": {"created_at": now_utc()}},
        upsert=True,
    )
    await message.reply_text(s(f"Global restriction record added for {target_id}."))


async def allow_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    if not is_owner(user.id):
        await message.reply_text(s("Owner access required."))
        return
    if not context.args:
        await message.reply_text("Usage: /allow user_id")
        return
    target_id = int(context.args[0])
    admin_records.delete_one({"type": "global_restriction", "user_id": target_id})
    await message.reply_text(s(f"Global restriction record removed for {target_id}."))


async def soft_mute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not message or not chat or not user:
        return
    if not is_owner(user.id):
        await message.reply_text(s("Owner access required."))
        return
    if not context.args:
        await message.reply_text("Usage: /mute user_id")
        return
    target_id = int(context.args[0])
    await context.bot.restrict_chat_member(
        chat_id=chat.id,
        user_id=target_id,
        permissions=ChatPermissions(can_send_messages=False),
    )
    await message.reply_text(s("Member send access paused."))


async def soft_unmute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not message or not chat or not user:
        return
    if not is_owner(user.id):
        await message.reply_text(s("Owner access required."))
        return
    if not context.args:
        await message.reply_text("Usage: /unmute user_id")
        return
    target_id = int(context.args[0])
    await context.bot.restrict_chat_member(
        chat_id=chat.id,
        user_id=target_id,
        permissions=ChatPermissions(can_send_messages=True, can_send_audios=True, can_send_documents=True, can_send_photos=True, can_send_videos=True, can_send_video_notes=True, can_send_voice_notes=True, can_send_polls=True, can_send_other_messages=True, can_add_web_page_previews=True),
    )
    await message.reply_text(s("Member send access restored."))
