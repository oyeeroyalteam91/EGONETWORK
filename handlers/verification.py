from __future__ import annotations

from datetime import timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config import settings
from database import db, is_gbanned, is_verified, mark_verified, now_utc, upsert_user

group_settings = db["group_settings"]
admin_records = db["admin_records"]
verification_prompts = db["verification_prompts"]

PROMPT_COOLDOWN_SECONDS = 45


def verification_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Verify Access", callback_data=f"verify:{chat_id}")],
        [InlineKeyboardButton("Why this data?", callback_data="verification_info")],
    ])


def verification_enabled(chat_id: int) -> bool:
    data = group_settings.find_one({"chat_id": chat_id}) or {}
    return bool(data.get("verification_enabled", True))


def globally_restricted(user_id: int) -> bool:
    return admin_records.find_one({"type": "global_restriction", "user_id": user_id}) is not None


async def is_group_admin(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int) -> bool:
    if user_id == settings.owner_id:
        return True
    try:
        member = await context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return member.status in {"administrator", "creator"}
    except Exception:
        return False


def should_send_prompt(chat_id: int, user_id: int) -> bool:
    row = verification_prompts.find_one({"chat_id": chat_id, "user_id": user_id}) or {}
    last_at = row.get("last_at")
    current = now_utc()
    if last_at and current - last_at < timedelta(seconds=PROMPT_COOLDOWN_SECONDS):
        return False
    verification_prompts.update_one({"chat_id": chat_id, "user_id": user_id}, {"$set": {"last_at": current}}, upsert=True)
    return True


async def enforce_verification(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if not message or not user or not chat:
        return
    if chat.type not in {"group", "supergroup"}:
        return
    if user.is_bot:
        return
    if not verification_enabled(chat.id):
        return
    if await is_group_admin(context, chat.id, user.id):
        return
    if is_gbanned(user.id) or globally_restricted(user.id):
        try:
            await message.delete()
        except Exception:
            pass
        return
    if is_verified(user.id, chat.id):
        return
    try:
        await message.delete()
    except Exception:
        pass
    if not should_send_prompt(chat.id, user.id):
        return
    text = (
        "Access Locked\n\n"
        "Please verify yourself before chatting in this group.\n"
        "This applies to every non-admin member.\n\n"
        "If the button does not work, send /verify in this group."
    )
    try:
        await context.bot.send_message(chat_id=chat.id, text=text, reply_markup=verification_keyboard(chat.id))
    except Exception:
        pass


async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if not message or not user or not chat:
        return
    if chat.type not in {"group", "supergroup"}:
        await message.reply_text("Use /verify inside the group where access is locked.")
        return
    if is_verified(user.id, chat.id):
        await message.reply_text("You are already verified in this group.")
        return
    upsert_user(user.id, {"name": user.full_name, "username": user.username, "verified": True})
    mark_verified(user.id, chat.id)
    await message.reply_text("Verification complete. You can chat now.")


async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = update.effective_user
    if not query or not user or not query.data:
        return
    await query.answer()
    target_message = query.message
    if query.data == "verification_info":
        text = (
            "Why this data is collected:\n\n"
            "AZAI uses basic Telegram profile data only for verification, safety, anti-spam, warning count, and group protection. "
            "It does not need your password, private chats, OTP, or payment details."
        )
        if target_message:
            await target_message.reply_text(text)
        return
    if not query.data.startswith("verify:"):
        return
    chat_id = int(query.data.split(":", 1)[1])
    if is_verified(user.id, chat_id):
        if target_message:
            await target_message.reply_text("You are already verified in this group.")
        return
    upsert_user(user.id, {"name": user.full_name, "username": user.username, "verified": True})
    mark_verified(user.id, chat_id)
    if target_message:
        await target_message.reply_text("Verification complete. You can chat now.")
