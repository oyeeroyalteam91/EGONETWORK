from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config import settings
from database import db

bot_assets = db["bot_assets"]


def main_menu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("Updates", url=settings.updates_channel)],
        [InlineKeyboardButton("Support", url=settings.support_link)],
        [InlineKeyboardButton("Privacy Policy", callback_data="privacy_policy")],
    ]
    return InlineKeyboardMarkup(buttons)


def start_caption() -> str:
    return (
        f"AZAI | {settings.network_name}\n"
        f"EST. {settings.est_year}\n\n"
        "Power moves quietly.\n"
        "Verify, protect, manage, play, earn, and keep the group clean without noise.\n\n"
        "Profile setup required:\n"
        "Tap /setup to complete your profile."
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return

    text = start_caption()
    asset = bot_assets.find_one({"key": "start_media"}) or {}
    file_id = asset.get("file_id")
    media_type = asset.get("media_type")

    if file_id and media_type == "video":
        await message.reply_video(video=file_id, caption=text, reply_markup=main_menu())
    elif file_id and media_type == "animation":
        await message.reply_animation(animation=file_id, caption=text, reply_markup=main_menu())
    elif file_id and media_type == "photo":
        await message.reply_photo(photo=file_id, caption=text, reply_markup=main_menu())
    else:
        await message.reply_text(text, reply_markup=main_menu())


async def privacy_policy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.message:
        return
    await query.answer()
    text = (
        "Privacy Policy\n\n"
        "AZAI stores only basic data needed for verification, safety, moderation, economy, games, quizzes, profile setup, birthday rewards, festival rewards, and community management. "
        "Never share passwords, OTPs, payment details, private documents, bot tokens, or database links."
    )
    await query.message.reply_text(text)
