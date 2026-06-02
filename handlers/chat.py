from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from handlers.ai_chat import azai_reply
from handlers.stickers import maybe_reply_with_sticker


def should_reply(text: str) -> bool:
    lowered = text.lower()
    triggers = ["azai", "hello", "hlo", "hi", "hey"]
    return any(word in lowered for word in triggers)


def has_special(text: str) -> bool:
    lowered = text.lower()
    words = ["bhabhi", "aliza", "tension", "problem", "sad", "kaha se", "where are", "from", "shop", "quiz", "verify", "help", "madad", "kaisa", "kaise"]
    return any(word in lowered for word in words)


async def chat_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user or not message.text:
        return
    if context.user_data.get("profile_step"):
        return
    text = message.text.strip()
    if message.chat.type in {"group", "supergroup"} and not should_reply(text):
        return
    if message.chat.type == "private" and not should_reply(text) and not has_special(text):
        return
    if await maybe_reply_with_sticker(update, context):
        return
    reply = await azai_reply(user.id, text)
    await message.reply_text(reply)
