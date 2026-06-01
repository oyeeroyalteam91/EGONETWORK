from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from utils.stylish_text import s


def should_reply(text: str) -> bool:
    lowered = text.lower()
    triggers = ["azai", "@", "hello", "hlo", "hi"]
    return any(trigger in lowered for trigger in triggers)


async def chat_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user or not message.text:
        return

    if message.chat.type in {"group", "supergroup"} and not should_reply(message.text):
        return

    if user.id == settings.aliza_id:
        await message.reply_text(s("Ji Bhabhi Ji, boliye."))
        return

    text = message.text.lower()
    if "kaha se" in text or "where are" in text or "from" in text:
        await message.reply_text(s("Mera system base reference Patna, Bihar se linked hai."))
        return

    await message.reply_text(s("Haan, boliye. AZAI active hai."))
