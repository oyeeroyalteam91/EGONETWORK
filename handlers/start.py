from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config import settings
from database import db
from utils.stylish_text import s, plain

bot_assets = db["bot_assets"]


def user_info_text(update: Update) -> str:
    user = update.effective_user
    if not user:
        return "Name: Unknown\nUser ID: Unknown\nUsername: Not set"
    username = f"@{user.username}" if user.username else "Not set"
    return f"Name: {user.full_name}\nUser ID: {user.id}\nUsername: {username}"


def panel_keyboard(page: int = 1) -> InlineKeyboardMarkup:
    if page == 1:
        rows = [
            [InlineKeyboardButton(s("Setup"), callback_data="azai_setup"), InlineKeyboardButton(s("Help"), callback_data="azai_help")],
            [InlineKeyboardButton(s("Shop"), callback_data="azai_shop"), InlineKeyboardButton(s("Quiz"), callback_data="azai_quiz")],
            [InlineKeyboardButton(s("Events"), callback_data="azai_events"), InlineKeyboardButton(s("Profile"), callback_data="azai_profile")],
            [InlineKeyboardButton(s("Donate"), callback_data="azai_donate"), InlineKeyboardButton(s("Next"), callback_data="azai_page_2")],
            [InlineKeyboardButton(s("Updates"), url=settings.updates_channel), InlineKeyboardButton(s("Support"), url=settings.support_link)],
        ]
    else:
        rows = [
            [InlineKeyboardButton(s("Owner"), callback_data="azai_owner"), InlineKeyboardButton(s("Group"), callback_data="azai_group")],
            [InlineKeyboardButton(s("Verify"), callback_data="azai_verify"), InlineKeyboardButton(s("Games"), callback_data="azai_games")],
            [InlineKeyboardButton(s("Stickers"), callback_data="azai_stickers"), InlineKeyboardButton(s("AI Chat"), callback_data="azai_ai")],
            [InlineKeyboardButton(s("Back"), callback_data="azai_page_1"), InlineKeyboardButton(s("Home"), callback_data="azai_page_1")],
            [InlineKeyboardButton(s("Owner Link"), url=settings.my_master)],
        ]
    return InlineKeyboardMarkup(rows)


def start_text(update: Update, page: int = 1) -> str:
    head = f"{s('AZAI')} | {s(settings.network_name)}\n{s('EST.')} {settings.est_year}"
    base = f"{head}\n\n{s('Power moves quietly.')}\n\n{plain(user_info_text(update))}\n\n"
    if page == 1:
        return base + plain(
            "Features:\n"
            "- Verification and group safety\n"
            "- AI chat and smart replies\n"
            "- Economy, rewards, and leaderboard\n"
            "- Anime/GK quiz and games\n"
            "- Shop, vault, events, birthday rewards\n\n"
            "Choose a panel below."
        )
    return base + plain(
        "Control Panels:\n"
        "- Owner tools\n"
        "- Group settings\n"
        "- Verification controls\n"
        "- Games and stickers\n"
        "- AI chat system\n\n"
        "Use Back or Home anytime."
    )


async def send_panel(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1) -> None:
    query = update.callback_query
    text = start_text(update, page)
    markup = panel_keyboard(page)
    if query and query.message:
        await query.answer("Updating...")
        try:
            await query.message.edit_caption(caption=text, reply_markup=markup)
            return
        except Exception:
            try:
                await query.message.edit_text(text=text, reply_markup=markup)
                return
            except Exception:
                await query.message.reply_text(text, reply_markup=markup)
                return
    message = update.effective_message
    if not message:
        return
    asset = bot_assets.find_one({"key": "start_media"}) or {}
    file_id = asset.get("file_id")
    media_type = asset.get("media_type")
    if file_id and media_type == "video":
        await message.reply_video(video=file_id, caption=text, reply_markup=markup)
    elif file_id and media_type == "animation":
        await message.reply_animation(animation=file_id, caption=text, reply_markup=markup)
    elif file_id and media_type == "photo":
        await message.reply_photo(photo=file_id, caption=text, reply_markup=markup)
    else:
        await message.reply_text(text, reply_markup=markup)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_panel(update, context, 1)


async def azai_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data or not query.message:
        return
    data = query.data
    if data == "azai_page_1":
        await send_panel(update, context, 1)
        return
    if data == "azai_page_2":
        await send_panel(update, context, 2)
        return
    await query.answer("Opening...")
    replies = {
        "azai_setup": "Setup: /setup",
        "azai_help": "Help: /help or /commands",
        "azai_shop": "Shop: /shop\nAdd item: /additem key price name\nSet media: /setshopmedia key",
        "azai_quiz": "Quiz: /animequiz /gkquiz\nKeys: /animepickeys\nSet pic: /setanimepic key\nAuto: /autoquiz",
        "azai_events": "Events: /events /eventstatus\nAdd event: /addevent key DD-MM coins name",
        "azai_profile": "Profile: /profile\nSetup: /setup",
        "azai_donate": "Donate panel is not connected yet. Owner can add donation link later.",
        "azai_owner": "Owner panel: /owner",
        "azai_group": "Group panel: /group",
        "azai_verify": "Verification: /verify /verifyon /verifyoff",
        "azai_games": "Games: /dice /dart /basketball /football /bowling /slot",
        "azai_stickers": "Stickers: /addsticker /removesticker /stickers",
        "azai_ai": "AI Chat: mention AZAI or say hi, help, shop, quiz, problem.",
    }
    await query.message.reply_text(replies.get(data, "Panel not found."))


async def privacy_policy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.message:
        return
    await query.answer("Opening privacy...")
    await query.message.reply_text(
        "Privacy Policy\n\n"
        "AZAI stores basic data for verification, safety, economy, games, quizzes, profile setup, birthday rewards, festival rewards, and community management. Never share passwords, OTPs, payment details, bot tokens, or database links."
    )
