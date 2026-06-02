from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from handlers.stickers import maybe_reply_with_sticker


def should_reply(text: str) -> bool:
    lowered = text.lower()
    return any(word in lowered for word in ["azai", "hello", "hlo", "hi", "hey"])


async def chat_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user or not message.text:
        return

    text = message.text.lower()
    profile_step = context.user_data.get("profile_step")
    if profile_step:
        return

    if message.chat.type in {"group", "supergroup"} and not should_reply(text):
        return

    if message.chat.type == "private" and not should_reply(text):
        special = ["bhabhi", "aliza", "tension", "problem", "sad", "kaha se", "where are", "from"]
        if not any(word in text for word in special):
            return

    if await maybe_reply_with_sticker(update, context):
        return

    if user.id == settings.owner_id and should_reply(text):
        await message.reply_text("Mr. Ego, Sir, AZAI active hai. Batao kya handle karna hai?")
        return

    if user.id == settings.aliza_id and should_reply(text):
        await message.reply_text("Ji Bhabhi Ji, AZAI yahin hai. Aap bolo, full respect mode on hai.")
        return

    if "bhabhi" in text or "aliza" in text:
        await message.reply_text("Bhabhi Ji ke liye respect always top level par hai.")
        return

    if "tension" in text or "problem" in text or "sad" in text:
        await message.reply_text("Relax bhai. Scene tough ho sakta hai, tu weak nahi. Ek-ek step me solve karte hain.")
        return

    if "kaha se" in text or "where are" in text or "from" in text:
        await message.reply_text("System base Patna, Bihar se linked hai. Vibe EGO NETWORK wali hai.")
        return

    if should_reply(text):
        await message.reply_text("Haan bhai, AZAI active hai. Chill mode on, kaam bolo.")
