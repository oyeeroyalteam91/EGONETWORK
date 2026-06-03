from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import ContextTypes

from config import settings
from database import db
from utils.stylish_text import s
from handlers.commands import commands
from handlers.profile import setup_profile, my_profile
from handlers.shop import shop, my_items
from handlers.quiz import anime_quiz, gk_quiz, anime_pic_keys
from handlers.events import events_panel
from handlers.admin_tools import owner_panel
from handlers.group_settings import group_panel
from handlers.verification import verify_command
from handlers.economy import balance, daily
from handlers.games import dice, dart, basketball, football, bowling, slot

bot_assets = db["bot_assets"]


def bot_link(username: str | None) -> str:
    name = username or getattr(settings, "bot_username", "") or settings.bot_name
    name = str(name).replace("@", "").strip()

    if not name:
        name = settings.bot_name

    return f"https://t.me/{name}?startgroup=true"


def get_user_line(update: Update) -> str:
    user = update.effective_user

    if not user:
        return (
            f"{s('Name')}: {s('Unknown')}\n"
            f"{s('User ID')}: {s('Unknown')}\n"
            f"{s('Username')}: {s('Not Set')}"
        )

    username = f"@{user.username}" if user.username else "Not set"

    return (
        f"{s('Name')}: {s(user.full_name)}\n"
        f"{s('User ID')}: {user.id}\n"
        f"{s('Username')}: {username}"
    )


def get_start_quote() -> str:
    row = bot_assets.find_one({"key": "start_quote"}) or {}
    quote = str(row.get("text", "")).strip()

    if quote:
        return quote

    return (
        "Power moves quietly.\n"
        "Built for control, community, rewards, and clean automation."
    )


def start_panel_text(update: Update) -> str:
    quote = get_start_quote()

    return (
        f"{s('Welcome To AZAI')}\n"
        f"{s('EGO Network')} • {s('EST.')} {settings.est_year}\n\n"
        f"{get_user_line(update)}\n\n"
        f"{s(quote)}\n\n"
        f"{s('AZAI is an advanced EGO Network community system.')}\n"
        f"{s('Built for verification, protection, AI chat, rewards, quizzes, shop, vault, events, and clean group control.')}\n\n"
        f"{s('Select an option below.')}"
    )


def mini_app_button() -> InlineKeyboardButton:
    if getattr(settings, "webapp_url", ""):
        return InlineKeyboardButton(
            s("Open Mini App"),
            web_app=WebAppInfo(settings.webapp_url),
        )

    return InlineKeyboardButton(
        s("Open Mini App"),
        callback_data="azai_miniapp_pending",
    )


def start_keyboard(bot_username: str | None = None) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(s("Add To Group"), url=bot_link(bot_username))],
        [
            InlineKeyboardButton(s("Commands"), callback_data="azai_run_commands"),
            InlineKeyboardButton(s("Profile"), callback_data="azai_run_profile"),
        ],
        [
            InlineKeyboardButton(s("Royal Shop"), callback_data="azai_run_shop"),
            InlineKeyboardButton(s("Vault"), callback_data="azai_run_vault"),
        ],
        [
            InlineKeyboardButton(s("Anime Quiz"), callback_data="azai_run_anime"),
            InlineKeyboardButton(s("GK Quiz"), callback_data="azai_run_gk"),
        ],
        [
            InlineKeyboardButton(s("Owner Panel"), callback_data="azai_run_owner"),
            InlineKeyboardButton(s("Group Panel"), callback_data="azai_run_group"),
        ],
        [
            InlineKeyboardButton(s("Donate"), callback_data="azai_donate"),
            InlineKeyboardButton(s("Privacy Policy"), callback_data="privacy_policy"),
        ],
        [
            mini_app_button(),
            InlineKeyboardButton(s("Anime Keys"), callback_data="azai_run_animekeys"),
        ],
        [
            InlineKeyboardButton(s("Updates"), url=settings.updates_channel),
            InlineKeyboardButton(s("Support"), url=settings.support_link),
        ],
        [InlineKeyboardButton(s("My Master"), url=settings.my_master)],
    ]

    return InlineKeyboardMarkup(rows)


async def send_start_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message

    if not message:
        return

    asset = bot_assets.find_one({"key": "start_media"}) or {}
    file_id = asset.get("file_id")
    media_type = asset.get("media_type")

    if not file_id:
        return

    try:
        if media_type == "video":
            await message.reply_video(video=file_id)
        elif media_type == "animation":
            await message.reply_animation(animation=file_id)
        elif media_type == "photo":
            await message.reply_photo(photo=file_id)
    except Exception:
        return


async def send_start_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message

    if not message:
        return

    await message.reply_text(
        start_panel_text(update),
        reply_markup=start_keyboard(context.bot.username),
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_start_media(update, context)
    await send_start_panel(update, context)


async def refresh_home_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    if not query or not query.message:
        return

    await query.answer("Updating...")

    text = start_panel_text(update)
    markup = start_keyboard(context.bot.username)

    try:
        await query.message.edit_text(text=text, reply_markup=markup)
    except Exception:
        try:
            await query.message.edit_caption(caption=text, reply_markup=markup)
        except Exception:
            await query.message.reply_text(text, reply_markup=markup)


async def donate_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    message = update.effective_message

    text = (
        f"{s('Donate Panel')}\n"
        f"{s('AZAI')} × {s('EGO Network')} • {s('EST.')} {settings.est_year}\n\n"
        f"{s('Telegram Stars donation is being prepared.')}\n"
        f"{s('No EC or XP is given for donations.')}\n"
        f"{s('Donations are support-only, not pay-to-win.')}"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(s("Support Channel"), url=settings.support_link)],
            [InlineKeyboardButton(s("Back"), callback_data="azai_home")],
        ]
    )

    if query and query.message:
        await query.answer("Opening...")
        try:
            await query.message.edit_text(text=text, reply_markup=keyboard)
        except Exception:
            await query.message.reply_text(text, reply_markup=keyboard)
        return

    if message:
        await message.reply_text(text, reply_markup=keyboard)


async def miniapp_pending(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    if not query or not query.message:
        return

    await query.answer("Mini App is being prepared.")
    await query.message.reply_text(s("Mini App is being prepared."))


async def azai_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    if not query or not query.data:
        return

    data = query.data

    if data == "azai_home":
        await refresh_home_panel(update, context)
        return

    if data == "azai_miniapp_pending":
        await miniapp_pending(update, context)
        return

    if data == "azai_donate":
        await donate_panel(update, context)
        return

    await query.answer("Opening...")

    run_map = {
        "azai_run_commands": commands,
        "azai_run_setup": setup_profile,
        "azai_run_profile": my_profile,
        "azai_run_shop": shop,
        "azai_run_vault": my_items,
        "azai_run_anime": anime_quiz,
        "azai_run_gk": gk_quiz,
        "azai_run_animekeys": anime_pic_keys,
        "azai_run_events": events_panel,
        "azai_run_owner": owner_panel,
        "azai_run_group": group_panel,
        "azai_run_verify": verify_command,
        "azai_run_balance": balance,
        "azai_run_daily": daily,
        "azai_run_dice": dice,
        "azai_run_dart": dart,
        "azai_run_basketball": basketball,
        "azai_run_football": football,
        "azai_run_bowling": bowling,
        "azai_run_slot": slot,
    }

    handler = run_map.get(data)

    if handler:
        await handler(update, context)
        return

    if query.message:
        await query.message.reply_text(s("Panel action not found."))


async def privacy_policy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    message = update.effective_message

    text = (
        f"{s('Privacy Policy')}\n"
        f"{s('AZAI')} × {s('EGO Network')} • {s('EST.')} {settings.est_year}\n\n"
        f"{s('AZAI stores limited user data required for verification, personalization, rewards, moderation, and community features.')}\n\n"
        f"{s('Data we may store:')}\n"
        f"{s('Telegram User ID')}\n"
        f"{s('Name, Gender, Birthday, Religion Preference')}\n"
        f"{s('Balance, XP, REP, Vault Items')}\n"
        f"{s('Quiz Stats, Warnings, Group Activity')}\n"
        f"{s('Settings and limited memory for better replies')}\n\n"
        f"{s('We do not sell user data.')}\n"
        f"{s('We do not share user data with third parties.')}\n"
        f"{s('We do not reveal source code, bot tokens, API keys, database credentials, security logic, or private owner tools.')}\n\n"
        f"{s('Owner Contact')}: @EGOISTICxPRIME\n\n"
        f"{s('Powered By EGO Network')} • {s('EST.')} {settings.est_year}"
    )

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(s("Back"), callback_data="azai_home")]]
    )

    if query and query.message:
        await query.answer("Opening privacy...")
        try:
            await query.message.edit_text(text=text, reply_markup=keyboard)
        except Exception:
            await query.message.reply_text(text, reply_markup=keyboard)
        return

    if message:
        await message.reply_text(text, reply_markup=keyboard)
