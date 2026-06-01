from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from database import is_gbanned, is_verified, mark_verified, upsert_user
from utils.stylish_text import s


def verification_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(s("Verify Access"), callback_data=f"verify:{chat_id}")],
        [InlineKeyboardButton(s("Why This Data"), callback_data="verification_info")],
    ])


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
    if is_gbanned(user.id):
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
