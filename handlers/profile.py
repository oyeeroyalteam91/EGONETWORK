from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config import settings
from database import upsert_user, get_user

PROFILE_STEPS = ["name", "gender", "birthday", "religion", "festival"]

PROMPTS = {
    "name": "EGO NETWORK | Profile Setup\nPlease send your display name.",
    "gender": "Please send your gender.",
    "birthday": "Please send your birthdate. Example: 21-07 or 21-07-2007.",
    "religion": "Please send your religion.",
    "festival": "Please send your favorite festival. Example: Diwali, Eid, Holi, Christmas, Chhath.",
}


def profile_info_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Why we ask this", callback_data="profile_data_info")],
    ])


def next_step(step: str) -> str | None:
    if step not in PROFILE_STEPS:
        return None
    index = PROFILE_STEPS.index(step)
    if index + 1 >= len(PROFILE_STEPS):
        return None
    return PROFILE_STEPS[index + 1]


def missing_step(profile: dict) -> str | None:
    for step in PROFILE_STEPS:
        if not profile.get(step):
            return step
    return None


async def setup_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    context.user_data["profile_step"] = "name"
    await message.reply_text(PROMPTS["name"], reply_markup=profile_info_keyboard())


async def auto_setup_if_needed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    data = get_user(user.id) or {}
    profile = data.get("profile", {}) or {}
    step = missing_step(profile)
    if step:
        context.user_data["profile_step"] = step
        await message.reply_text(PROMPTS[step], reply_markup=profile_info_keyboard())


async def profile_data_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.message:
        return
    await query.answer()
    await query.message.reply_text(
        "EGO NETWORK | Data Use\n\n"
        "We collect only basic profile details for verification, birthday wishes, festival rewards, and community features.\n"
        "Never share passwords, OTPs, payment details, private documents, bot tokens, or database links."
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
    profile = current.get("profile", {}) or {}
    profile[step] = text

    upsert_user(user.id, {
        "name": user.full_name,
        "username": user.username,
        "profile": profile,
    })

    upcoming = next_step(step)
    if upcoming:
        context.user_data["profile_step"] = upcoming
        await message.reply_text(PROMPTS[upcoming], reply_markup=profile_info_keyboard())
        return

    context.user_data.pop("profile_step", None)
    await message.reply_text(
        f"Profile setup completed.\n{settings.network_name} | EST. {settings.est_year}\nYour saved details can now be used for wishes, rewards, and community features."
    )


async def my_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return

    data = get_user(user.id) or {}
    profile = data.get("profile", {}) or {}
    text = (
        f"Your Profile\n{settings.network_name} | EST. {settings.est_year}\n\n"
        f"Name: {profile.get('name', user.full_name)}\n"
        f"Gender: {profile.get('gender', 'Not set')}\n"
        f"Birthday: {profile.get('birthday', 'Not set')}\n"
        f"Religion: {profile.get('religion', 'Not set')}\n"
        f"Favorite Festival: {profile.get('festival', 'Not set')}"
    )
    await message.reply_text(text)
