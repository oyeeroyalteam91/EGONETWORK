from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config import settings
from database import db

bot_assets = db["bot_assets"]


def inline_links() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Updates", url=settings.updates_channel), InlineKeyboardButton("Support", url=settings.support_link)],
        [InlineKeyboardButton("Owner", url=settings.my_master), InlineKeyboardButton("Privacy Policy", callback_data="privacy_policy")],
    ])


def command_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([
        [KeyboardButton("/setup"), KeyboardButton("/help")],
        [KeyboardButton("/shop"), KeyboardButton("/inventory")],
        [KeyboardButton("/animequiz"), KeyboardButton("/gkquiz")],
        [KeyboardButton("/events"), KeyboardButton("/owner")],
    ], resize_keyboard=True)


def start_caption() -> str:
    return (
        f"AZAI | {settings.network_name}\n"
        f"EST. {settings.est_year}\n\n"
        "Hey, welcome to AZAI.\n"
        "Advanced group manager with automation, verification, games, rewards, shop, quiz, events, and smart chat.\n\n"
        "Power moves quietly.\n"
        "Use the command buttons below.\n\n"
        "First step: /setup"
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
        await message.reply_video(video=file_id, caption=text, reply_markup=inline_links())
    elif file_id and media_type == "animation":
        await message.reply_animation(animation=file_id, caption=text, reply_markup=inline_links())
    elif file_id and media_type == "photo":
        await message.reply_photo(photo=file_id, caption=text, reply_markup=inline_links())
    else:
        await message.reply_text(text, reply_markup=inline_links())

    await message.reply_text("Quick command menu", reply_markup=command_keyboard())


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
