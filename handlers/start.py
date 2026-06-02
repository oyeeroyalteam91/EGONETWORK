from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config import settings
from database import db

bot_assets = db["bot_assets"]


def main_menu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("Add AZAI To Group", url=f"https://t.me/{settings.bot_name}?startgroup=true")],
        [InlineKeyboardButton("Help", callback_data="start_help"), InlineKeyboardButton("Commands", callback_data="start_commands")],
        [InlineKeyboardButton("Profile Setup", callback_data="start_profile"), InlineKeyboardButton("Shop", callback_data="start_shop")],
        [InlineKeyboardButton("Quiz", callback_data="start_quiz"), InlineKeyboardButton("Events", callback_data="start_events")],
        [InlineKeyboardButton("Updates", url=settings.updates_channel), InlineKeyboardButton("Support", url=settings.support_link)],
        [InlineKeyboardButton("Owner", url=settings.my_master), InlineKeyboardButton("Privacy Policy", callback_data="privacy_policy")],
    ]
    return InlineKeyboardMarkup(buttons)


def start_caption() -> str:
    return (
        f"AZAI | {settings.network_name}\n"
        f"EST. {settings.est_year}\n\n"
        "Hey, welcome to AZAI.\n"
        "An advanced EGO NETWORK manager built for clean groups, smooth automation, games, rewards, shop, quiz, and smart chat.\n\n"
        "Power moves quietly.\n"
        "Use the buttons below to control everything.\n\n"
        "Profile setup required: /setup"
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


async def start_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.message:
        return
    await query.answer()
    await query.message.reply_text(
        "AZAI Help\n\n"
        "Use /setup to complete your profile.\n"
        "Use /verify inside groups to unlock chat access.\n"
        "Use /shop to view items.\n"
        "Use /animequiz or /gkquiz to play.\n"
        "Owner controls are available through /owner."
    )


async def start_commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.message:
        return
    await query.answer()
    await query.message.reply_text(
        "AZAI Commands\n\n"
        "User: /start /setup /profile /verify /shop /inventory /balance /daily /leaderboard\n"
        "Games: /animequiz /gkquiz /dice /dart /basketball /football /bowling /slot\n"
        "Owner: /owner /group /verifyon /verifyoff /additem /setshopmedia /setstartmedia /setpanelphoto /autoquiz /events"
    )


async def start_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.message:
        return
    await query.answer()
    await query.message.reply_text("Profile setup: tap /setup")


async def start_shop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.message:
        return
    await query.answer()
    await query.message.reply_text("Shop: tap /shop")


async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.message:
        return
    await query.answer()
    await query.message.reply_text("Quiz: tap /animequiz or /gkquiz")


async def start_events(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.message:
        return
    await query.answer()
    await query.message.reply_text("Events: tap /events")
