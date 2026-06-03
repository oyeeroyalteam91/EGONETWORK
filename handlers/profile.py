from __future__ import annotations

import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config import settings
from database import get_user, upsert_user
from utils.stylish_text import s

PROFILE_STEPS = ["name", "gender", "birthday", "religion", "festival"]

GENDER_MAP = {
    "male": "Male",
    "m": "Male",
    "boy": "Male",
    "ladka": "Male",
    "female": "Female",
    "f": "Female",
    "girl": "Female",
    "ladki": "Female",
    "prefer not to say": "Prefer Not To Say",
    "skip": "Prefer Not To Say",
}

RELIGION_MAP = {
    "hindu": "Hindu",
    "muslim": "Muslim",
    "christian": "Christian",
    "sikh": "Sikh",
    "buddhist": "Buddhist",
    "jain": "Jain",
    "other": "Other",
    "skip": "Skip",
}

VALID_GENDERS = {"Male", "Female", "Prefer Not To Say"}
VALID_RELIGIONS = {
    "Hindu",
    "Muslim",
    "Christian",
    "Sikh",
    "Buddhist",
    "Jain",
    "Other",
    "Skip",
}

PROMPTS = {
    "name": "EGO NETWORK | Profile Setup\nPlease send your display name.",
    "gender": "Choose your gender.\nUse buttons or type: Male, Female, Prefer Not To Say.",
    "birthday": "Send your birthday in DD/MM format.\nExample: 21/07",
    "religion": "Choose your religion.\nUse buttons or type: Hindu, Muslim, Christian, Sikh, Buddhist, Jain, Other, Skip.",
    "festival": "Send your favorite festival.\nExample: Diwali, Eid, Holi, Christmas, Chhath.",
}


def profile_info_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(s("Why We Ask This"), callback_data="profile_data_info")]
        ]
    )


def option_keyboard(step: str) -> InlineKeyboardMarkup:
    if step == "gender":
        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(s("Male"), callback_data="profile_option:gender:Male"),
                    InlineKeyboardButton(s("Female"), callback_data="profile_option:gender:Female"),
                ],
                [
                    InlineKeyboardButton(
                        s("Prefer Not To Say"),
                        callback_data="profile_option:gender:Prefer Not To Say",
                    )
                ],
                [
                    InlineKeyboardButton(
                        s("Why We Ask This"),
                        callback_data="profile_data_info",
                    )
                ],
            ]
        )

    if step == "religion":
        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(s("Hindu"), callback_data="profile_option:religion:Hindu"),
                    InlineKeyboardButton(s("Muslim"), callback_data="profile_option:religion:Muslim"),
                ],
                [
                    InlineKeyboardButton(s("Christian"), callback_data="profile_option:religion:Christian"),
                    InlineKeyboardButton(s("Sikh"), callback_data="profile_option:religion:Sikh"),
                ],
                [
                    InlineKeyboardButton(s("Buddhist"), callback_data="profile_option:religion:Buddhist"),
                    InlineKeyboardButton(s("Jain"), callback_data="profile_option:religion:Jain"),
                ],
                [
                    InlineKeyboardButton(s("Other"), callback_data="profile_option:religion:Other"),
                    InlineKeyboardButton(s("Skip"), callback_data="profile_option:religion:Skip"),
                ],
                [
                    InlineKeyboardButton(
                        s("Why We Ask This"),
                        callback_data="profile_data_info",
                    )
                ],
            ]
        )

    return profile_info_keyboard()


def normalize_birthday(text: str) -> str | None:
    value = text.strip().replace("-", "/")
    match = re.fullmatch(r"(0?[1-9]|[12][0-9]|3[01])/(0?[1-9]|1[0-2])", value)

    if not match:
        return None

    day = int(match.group(1))
    month = int(match.group(2))

    return f"{day:02d}/{month:02d}"


def is_valid_profile_value(step: str, value: str | None) -> bool:
    if not value:
        return False

    if step == "name":
        return len(str(value).strip()) >= 2

    if step == "gender":
        return value in VALID_GENDERS

    if step == "birthday":
        return normalize_birthday(str(value)) is not None

    if step == "religion":
        return value in VALID_RELIGIONS

    if step == "festival":
        return len(str(value).strip()) >= 2

    return True


def missing_step(profile: dict) -> str | None:
    for step in PROFILE_STEPS:
        if not is_valid_profile_value(step, profile.get(step)):
            return step
    return None


def next_step(current_step: str, profile: dict) -> str | None:
    if current_step not in PROFILE_STEPS:
        return None

    start_index = PROFILE_STEPS.index(current_step) + 1

    for step in PROFILE_STEPS[start_index:]:
        if not is_valid_profile_value(step, profile.get(step)):
            return step

    return None


def validate_step(step: str, text: str) -> tuple[bool, str]:
    clean = text.strip()
    lower = clean.lower()

    if step == "name":
        if clean.startswith("/") or len(clean) < 2:
            return False, "Invalid name. Please send a real display name."
        return True, clean[:40]

    if step == "gender":
        value = GENDER_MAP.get(lower)
        if not value:
            return False, "Invalid gender. Please choose Male, Female, or Prefer Not To Say."
        return True, value

    if step == "birthday":
        value = normalize_birthday(clean)
        if not value:
            return False, "Invalid birthday. Send only date and month like 21/07."
        return True, value

    if step == "religion":
        value = RELIGION_MAP.get(lower)
        if not value:
            return False, "Invalid religion. Please choose Hindu, Muslim, Christian, Sikh, Buddhist, Jain, Other, or Skip."
        return True, value

    if step == "festival":
        if clean.startswith("/") or len(clean) < 2:
            return False, "Invalid festival. Please send a valid festival name."
        return True, clean[:40]

    return True, clean


async def setup_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user

    if not message or not user:
        return

    data = get_user(user.id) or {}
    profile = data.get("profile", {}) or {}

    step = missing_step(profile) or "name"
    context.user_data["profile_step"] = step

    await message.reply_text(s(PROMPTS[step]), reply_markup=option_keyboard(step))


async def reset_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user

    if not message or not user:
        return

    upsert_user(
        user.id,
        {
            "name": user.full_name,
            "username": user.username,
            "profile": {},
        },
    )

    context.user_data["profile_step"] = "name"

    await message.reply_text(
        s("Profile reset completed. Please send your display name."),
        reply_markup=profile_info_keyboard(),
    )


async def edit_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await setup_profile(update, context)


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
        await message.reply_text(s(PROMPTS[step]), reply_markup=option_keyboard(step))


async def profile_data_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    if not query or not query.message:
        return

    await query.answer()

    text = (
        "EGO NETWORK | Data Use\n\n"
        "We collect basic profile details only for verification, personalization, birthday wishes, festival rewards, and community features.\n\n"
        "Your data is not sold.\n"
        "Your data is not publicly exposed.\n"
        "Do not share passwords, OTPs, payment details, private documents, bot tokens, or database links."
    )

    await query.message.reply_text(s(text))


async def save_profile_value(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    step: str,
    value: str,
) -> None:
    message = update.effective_message
    user = update.effective_user

    if not message or not user:
        return

    current = get_user(user.id) or {}
    profile = current.get("profile", {}) or {}

    profile[step] = value

    upsert_user(
        user.id,
        {
            "name": user.full_name,
            "username": user.username,
            "profile": profile,
        },
    )

    upcoming = next_step(step, profile)

    if upcoming:
        context.user_data["profile_step"] = upcoming
        await message.reply_text(s(PROMPTS[upcoming]), reply_markup=option_keyboard(upcoming))
        return

    context.user_data.pop("profile_step", None)

    await message.reply_text(
        s(f"Profile setup completed. {settings.network_name} | EST. {settings.est_year}.")
    )


async def profile_option_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    if not query or not query.data:
        return

    await query.answer("Saved")

    try:
        _, step, value = query.data.split(":", 2)
    except ValueError:
        return

    ok, saved_value = validate_step(step, value)

    if not ok:
        if query.message:
            await query.message.reply_text(s(saved_value), reply_markup=option_keyboard(step))
        return

    await save_profile_value(update, context, step, saved_value)


async def profile_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message

    if not message or not message.text:
        return

    step = context.user_data.get("profile_step")

    if not step:
        return

    ok, value = validate_step(step, message.text)

    if not ok:
        await message.reply_text(s(value), reply_markup=option_keyboard(step))
        return

    await save_profile_value(update, context, step, value)


async def my_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user

    if not message or not user:
        return

    data = get_user(user.id) or {}
    profile = data.get("profile", {}) or {}

    text = (
        f"{s('Your Profile')}\n"
        f"{s(f'{settings.network_name} | EST. {settings.est_year}')}\n\n"
        f"{s('Name')}: {profile.get('name', user.full_name)}\n"
        f"{s('Gender')}: {profile.get('gender', 'Not set')}\n"
        f"{s('Birthday')}: {profile.get('birthday', 'Not set')}\n"
        f"{s('Religion')}: {profile.get('religion', 'Not set')}\n"
        f"{s('Favorite Festival')}: {profile.get('festival', 'Not set')}"
    )

    await message.reply_text(text)
