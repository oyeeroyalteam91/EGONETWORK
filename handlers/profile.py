from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from database import upsert_user, get_user
from utils.stylish_text import s

PROFILE_STEPS = ["name", "birthday", "religion"]


def profile_info_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Why we ask this", callback_data="profile_data_info")],
    ])


async def setup_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    context.user_data["profile_step"] = "name"
    await message.reply_text(s("Profile setup started. Send your display name."))


async def profile_data_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.message:
        return
    await query.answer()
    await query.message.reply_text(
        "We ask basic profile details only to personalize replies, improve verification, and keep community records clean. "
        "Do not share passwords, OTPs, payment details, or private documents."
    )


async def profile_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user or not message.text:
        return

    step = context.user_data.get("profile_step")
    if not step:
        return

    text = message.text.strip()
    current = get_user(user.id) or {}
    profile = current.get("profile", {})
    profile[step] = text

    upsert_user(user.id, {
        "name": user.full_name,
        "username": user.username,
        "profile": profile,
    })

    if step == "name":
        context.user_data["profile_step"] = "birthday"
        await message.reply_text(s("Now send your birthday."), reply_markup=profile_info_keyboard())
    elif step == "birthday":
        context.user_data["profile_step"] = "religion"
        await message.reply_text(s("Now send your religion."), reply_markup=profile_info_keyboard())
    else:
        context.user_data.pop("profile_step", None)
        await message.reply_text(s("Profile setup completed."))


async def my_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return

    data = get_user(user.id) or {}
    profile = data.get("profile", {})
    text = (
        f"{s('Your Profile')}\n\n"
        f"Name: {profile.get('name', user.full_name)}\n"
        f"Birthday: {profile.get('birthday', 'Not set')}\n"
        f"Religion: {profile.get('religion', 'Not set')}"
    )
    await message.reply_text(text)
