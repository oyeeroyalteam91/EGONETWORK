from __future__ import annotations

from telegram import ChatPermissions, Update
from telegram.ext import ContextTypes

from config import settings
from database import db, now_utc
from handlers.panel_photo import send_panel_photo_or_text
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
        f"{s('Owner Panel')}\n"
        f"{settings.network_name} | {settings.est_year}\n\n"
        "Core:\n"
        "/owner - show panel\n"
        "/group - group settings\n"
        "/events - event control\n"
        "/broadcast message - send update\n\n"
        "Verification & Events:\n"
        "/verifyon - enable verification\n"
        "/verifyoff - disable verification\n"
        "/autoquiz - toggle 30 minute quiz\n"
        "/addevent key DD-MM coins name\n\n"
        "Media:\n"
        "/setpanelphoto - set panel photo\n"
        "/setwelcome - set welcome photo\n"
        "/setstartmedia - set start media\n"
        "/setanimepic key - set anime quiz photo\n"
        "/setshopmedia key - set shop media\n\n"
        "Economy & Safety:\n"
        "/additem key price name\n"
        "/addpoints user_id amount\n"
        "/restrict user_id reason\n"
        "/allow user_id\n"
        "/mute user_id\n"
        "/unmute user_id\n"
        "/warns user_id\n"
        "/clearwarns user_id"
    )
    await send_panel_photo_or_text(message, text)


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
    await context.bot.restrict_chat_member(chat_id=chat.id, user_id=target_id, permissions=ChatPermissions(can_send_messages=False))
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
    await context.bot.restrict_chat_member(chat_id=chat.id, user_id=target_id, permissions=ChatPermissions(can_send_messages=True, can_send_audios=True, can_send_documents=True, can_send_photos=True, can_send_videos=True, can_send_video_notes=True, can_send_voice_notes=True, can_send_polls=True, can_send_other_messages=True, can_add_web_page_previews=True))
    await message.reply_text(s("Member send access restored."))
