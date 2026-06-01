from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from database import db, is_gbanned, is_verified, mark_verified, upsert_user
from utils.stylish_text import s

group_settings = db["group_settings"]
admin_records = db["admin_records"]


def verification_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(s("Verify Access"), callback_data=f"verify:{chat_id}")],
        [InlineKeyboardButton(s("Why This Data"), callback_data="verification_info")],
    ])


def verification_enabled(chat_id: int) -> bool:
    data = group_settings.find_one({"chat_id": chat_id}) or {}
    return bool(data.get("verification_enabled", True))


def globally_restricted(user_id: int) -> bool:
    return admin_records.find_one({"type": "global_restriction", "user_id": user_id}) is not None


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
    if is_gbanned(user.id) or globally_restricted(user.id):
        await message.delete()
        return
    if is_verified(user.id, chat.id):
        return

    try:
        await message.delete()
    except Exception:
        pass

    text = (
        f"{s('Access Locked')}\n\n"
        f"{s('Verification is required before chatting in this group.')}\n"
        f"{s('This rule applies to every member, old or new.')}"
    )
    await context.bot.send_message(chat_id=chat.id, text=text, reply_markup=verification_keyboard(chat.id))


async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = update.effective_user
    if not query or not user or not query.data:
        return
    await query.answer()

    if query.data == "verification_info":
        text = (
            "Why this data is collected:\n\n"
            "AZAI uses basic Telegram profile data only for verification, safety, anti-spam, warning count, and group protection. "
            "It does not need your password, private chats, OTP, or payment details."
        )
        await query.message.reply_text(text)
        return

    if not query.data.startswith("verify:"):
        return

    chat_id = int(query.data.split(":", 1)[1])
    upsert_user(user.id, {
        "name": user.full_name,
        "username": user.username,
        "verified": True,
    })
    mark_verified(user.id, chat_id)
    await query.message.reply_text(s("Verification complete. You can chat now."))
