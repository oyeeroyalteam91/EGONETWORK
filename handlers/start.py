from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config import settings
from utils.stylish_text import s


def main_menu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(s("Updates"), url=settings.updates_channel)],
        [InlineKeyboardButton(s("Support"), url=settings.support_link)],
        [InlineKeyboardButton(s("Privacy Policy"), callback_data="privacy_policy")],
    ]
    return InlineKeyboardMarkup(buttons)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return

    text = (
        f"{s('Welcome To')} {settings.bot_name}\n"
        f"{s(settings.network_name)} | {settings.est_year}\n\n"
        f"{s('Royal community control is ready.')}\n"
        f"{s('Verify, protect, manage, and keep the group clean without noise.')}"
    )
    await message.reply_text(text, reply_markup=main_menu())


async def privacy_policy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.message:
        return
    await query.answer()
    text = (
        "Privacy Policy\n\n"
        "AZAI stores only basic data needed for verification, safety, moderation, and community management. "
        "This can include Telegram user ID, display name, username, verification status, warning count, and group ID. "
        "Private tokens, database links, and owner secrets must never be shown to users."
    )
    await query.message.reply_text(text)
