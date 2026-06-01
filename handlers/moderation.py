from __future__ import annotations

from datetime import timedelta

from telegram import ChatPermissions, Update
from telegram.ext import ContextTypes

from config import settings
from database import add_warning
from utils.constants import ABUSE_KEYWORDS, DEFAULT_MUTE_MINUTES, DEFAULT_WARNING_LIMIT
from utils.stylish_text import s


def contains_abuse(text: str) -> bool:
    lowered = text.lower()
    return any(word in lowered for word in ABUSE_KEYWORDS)


async def moderation_guard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if not message or not user or not chat or not message.text:
        return
    if chat.type not in {"group", "supergroup"}:
        return
    if user.id == settings.owner_id:
        return
    if not contains_abuse(message.text):
        return

    try:
        await message.delete()
    except Exception:
        pass

    count = add_warning(chat.id, user.id, "abusive_language")
    if count >= DEFAULT_WARNING_LIMIT:
        until_date = message.date + timedelta(minutes=DEFAULT_MUTE_MINUTES)
        try:
            await context.bot.restrict_chat_member(
                chat_id=chat.id,
                user_id=user.id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until_date,
            )
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=chat.id,
            text=s(f"Warning limit reached. User muted for {DEFAULT_MUTE_MINUTES} minutes."),
        )
        return

    await context.bot.send_message(
        chat_id=chat.id,
        text=s(f"Disrespect is not allowed. Warning {count}/{DEFAULT_WARNING_LIMIT}."),
    )
