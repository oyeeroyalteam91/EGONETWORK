from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from handlers.stickers import maybe_reply_with_sticker
from utils.stylish_text import s


def should_reply(text: str) -> bool:
    lowered = text.lower()
    return any(word in lowered for word in ["azai", "@", "hello", "hlo", "hi", "hey"])


async def chat_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user or not message.text:
        return

    if message.chat.type in {"group", "supergroup"} and not should_reply(message.text):
        return

    if await maybe_reply_with_sticker(update, context):
        return

    text = message.text.lower()

    if user.id == settings.owner_id:
        await message.reply_text(s("Mr. Ego, Sir, AZAI active hai. Batao kya handle karna hai?"))
        return

    if user.id == settings.aliza_id:
        await message.reply_text(s("Ji Bhabhi Ji, AZAI yahin hai. Aap bolo, full respect mode on hai."))
        return

    if "bhabhi" in text or "aliza" in text:
        await message.reply_text(s("Bhabhi Ji ke liye respect always top level par hai."))
        return

    if "tension" in text or "problem" in text or "sad" in text:
        await message.reply_text(s("Relax bhai. Scene tough ho sakta hai, tu weak nahi. Ek-ek step me solve karte hain."))
        return

    if "kaha se" in text or "where are" in text or "from" in text:
        await message.reply_text(s("System base Patna, Bihar se linked hai. Vibe EGO NETWORK wali hai."))
        return

    await message.reply_text(s("Haan bhai, AZAI active hai. Chill mode on, kaam bolo."))
