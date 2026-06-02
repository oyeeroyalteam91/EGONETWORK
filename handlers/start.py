from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
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


def user_info_text(update: Update) -> str:
    user = update.effective_user
    if not user:
        return s("Name: Unknown\nUser ID: Unknown\nUsername: Not set")
    username = f"@{user.username}" if user.username else "Not set"
    return s(f"Name: {user.full_name}\nUser ID: {user.id}\nUsername: {username}")


def bot_link(username: str | None) -> str:
    name = username or settings.bot_name
    return f"https://t.me/{name}?startgroup=true"


def panel_keyboard(page: int = 1, bot_username: str | None = None) -> InlineKeyboardMarkup:
    if page == 1:
        rows = [
            [InlineKeyboardButton(s("Integrate In Your Chat"), url=bot_link(bot_username))],
            [InlineKeyboardButton(s("Access Setup"), callback_data="azai_run_setup"), InlineKeyboardButton(s("Command Hall"), callback_data="azai_run_help")],
            [InlineKeyboardButton(s("Royal Shop"), callback_data="azai_run_shop"), InlineKeyboardButton(s("Quiz Arena"), callback_data="azai_page_quiz")],
            [InlineKeyboardButton(s("Event Core"), callback_data="azai_run_events"), InlineKeyboardButton(s("User Vault"), callback_data="azai_run_vault")],
            [InlineKeyboardButton(s("Donate"), callback_data="azai_donate"), InlineKeyboardButton(s("Next"), callback_data="azai_page_2")],
            [InlineKeyboardButton(s("Updates"), url=settings.updates_channel), InlineKeyboardButton(s("Support"), url=settings.support_link)],
        ]
    elif page == 2:
        rows = [
            [InlineKeyboardButton(s("Owner Panel"), callback_data="azai_run_owner"), InlineKeyboardButton(s("Group Panel"), callback_data="azai_run_group")],
            [InlineKeyboardButton(s("Verify Core"), callback_data="azai_run_verify"), InlineKeyboardButton(s("Economy Core"), callback_data="azai_page_economy")],
            [InlineKeyboardButton(s("Game Zone"), callback_data="azai_page_games"), InlineKeyboardButton(s("AI Chat"), callback_data="azai_ai")],
            [InlineKeyboardButton(s("Back"), callback_data="azai_page_1"), InlineKeyboardButton(s("Home"), callback_data="azai_page_1")],
            [InlineKeyboardButton(s("Owner Link"), url=settings.my_master)],
        ]
    elif page == 3:
        rows = [
            [InlineKeyboardButton(s("Anime Quiz"), callback_data="azai_run_anime"), InlineKeyboardButton(s("GK Quiz"), callback_data="azai_run_gk")],
            [InlineKeyboardButton(s("Anime Keys"), callback_data="azai_run_animekeys"), InlineKeyboardButton(s("Auto Quiz"), callback_data="azai_autoquiz_info")],
            [InlineKeyboardButton(s("Back"), callback_data="azai_page_1"), InlineKeyboardButton(s("Home"), callback_data="azai_page_1")],
        ]
    elif page == 4:
        rows = [
            [InlineKeyboardButton(s("Balance"), callback_data="azai_run_balance"), InlineKeyboardButton(s("Daily Reward"), callback_data="azai_run_daily")],
            [InlineKeyboardButton(s("Leaderboard"), callback_data="azai_leader_info"), InlineKeyboardButton(s("Vault"), callback_data="azai_run_vault")],
            [InlineKeyboardButton(s("Back"), callback_data="azai_page_2"), InlineKeyboardButton(s("Home"), callback_data="azai_page_1")],
        ]
    else:
        rows = [
            [InlineKeyboardButton(s("Dice"), callback_data="azai_run_dice"), InlineKeyboardButton(s("Dart"), callback_data="azai_run_dart")],
            [InlineKeyboardButton(s("Basketball"), callback_data="azai_run_basketball"), InlineKeyboardButton(s("Football"), callback_data="azai_run_football")],
            [InlineKeyboardButton(s("Bowling"), callback_data="azai_run_bowling"), InlineKeyboardButton(s("Slot"), callback_data="azai_run_slot")],
            [InlineKeyboardButton(s("Back"), callback_data="azai_page_2"), InlineKeyboardButton(s("Home"), callback_data="azai_page_1")],
        ]
    return InlineKeyboardMarkup(rows)


def start_text(update: Update, page: int = 1) -> str:
    head = f"{s('AZAI')} | {s(settings.network_name)}\n{s('EST.')} {settings.est_year}"
    base = f"{head}\n\n{s('Power moves quietly.')}\n\n{user_info_text(update)}\n\n"
    if page == 1:
        return base + s("Advanced group system with verification, AI chat, rewards, leaderboard, anime quiz, games, shop, vault, events, and clean automation. Choose a panel below.")
    if page == 2:
        return base + s("Control panels for owner tools, group settings, verification, economy, games, and AI chat.")
    if page == 3:
        return base + s("Quiz arena. Anime quiz uses saved pics first. If missing, AZAI tries auto image access before sending.")
    if page == 4:
        return base + s("Economy core. Check balance, daily rewards, leaderboard, and vault items.")
    return base + s("Game zone. Telegram games can be launched directly from buttons.")


async def send_panel(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 1) -> None:
    query = update.callback_query
    text = start_text(update, page)
    markup = panel_keyboard(page, context.bot.username)
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
        await send_panel(update, context, 1); return
    if data == "azai_page_2":
        await send_panel(update, context, 2); return
    if data == "azai_page_quiz":
        await send_panel(update, context, 3); return
    if data == "azai_page_economy":
        await send_panel(update, context, 4); return
    if data == "azai_page_games":
        await send_panel(update, context, 5); return

    await query.answer("Running...")
    run_map = {
        "azai_run_setup": setup_profile,
        "azai_run_help": commands,
        "azai_run_shop": shop,
        "azai_run_vault": my_items,
        "azai_run_anime": anime_quiz,
        "azai_run_gk": gk_quiz,
        "azai_run_animekeys": anime_pic_keys,
        "azai_run_events": events_panel,
        "azai_run_profile": my_profile,
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
    if data in run_map:
        await run_map[data](update, context)
        return
    replies = {
        "azai_donate": s("Donate panel is not connected yet. Owner can add donation link later."),
        "azai_ai": s("AI Chat is active. Say AZAI, hello, help, shop, quiz, or problem."),
        "azai_autoquiz_info": f"{s('Auto Quiz')}\n/autoquiz\n/autoquizon\n/autoquizoff",
        "azai_leader_info": f"{s('Leaderboard')}\n/leaderboard\n/top",
    }
    await query.message.reply_text(replies.get(data, s("Panel not found.")))


async def privacy_policy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.message:
        return
    await query.answer("Opening privacy...")
    await query.message.reply_text(s("Privacy Policy") + "\n\n" + s("AZAI stores basic data for verification, safety, economy, games, quizzes, profile setup, birthday rewards, festival rewards, and community management. Never share passwords, OTPs, payment details, bot tokens, or database links."))
