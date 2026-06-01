from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from database import db
from utils.stylish_text import s

group_settings = db["group_settings"]


def welcome_caption(name: str) -> str:
    return (
        f"{s('Welcome To')} {settings.network_name}\n\n"
        f"{s('Member')}: {name}\n"
        f"{s('Respect the rules, verify access, and enjoy the community.')}\n\n"
        f"{settings.network_name} | {settings.est_year}"
    )


async def welcome_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    chat = update.effective_chat
    if not message or not chat or not message.new_chat_members:
        return

    data = group_settings.find_one({"chat_id": chat.id}) or {}
    welcome_pic = data.get("welcome_pic")

    for member in message.new_chat_members:
        if member.is_bot:
            continue
        text = welcome_caption(member.full_name)
        if welcome_pic:
            await message.reply_photo(photo=welcome_pic, caption=text)
        else:
            await message.reply_text(text)
