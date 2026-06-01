from __future__ import annotations

import logging

from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from config import settings
from handlers.admin_tools import allow_user, owner_panel, restrict_user, soft_mute, soft_unmute
from handlers.broadcast import broadcast
from handlers.chat import chat_reply
from handlers.commands import commands
from handlers.group_settings import group_panel, save_group, set_start_pic, set_welcome_pic, verify_off, verify_on
from handlers.leaderboard import add_manual_points, leaderboard, reward_activity
from handlers.media import get_custom_pic, list_custom_pics, set_custom_pic
from handlers.moderation import moderation_guard
from handlers.profile import my_profile, profile_data_info, profile_message_handler, setup_profile
from handlers.start import privacy_policy, start
from handlers.verification import enforce_verification, verify_callback
from handlers.warnings import clear_warnings, show_warnings

logging.basicConfig(level=logging.INFO)


def build_app() -> Application:
    application = Application.builder().token(settings.bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", commands))
    application.add_handler(CommandHandler("commands", commands))
    application.add_handler(CommandHandler("setup", setup_profile))
    application.add_handler(CommandHandler("profile", my_profile))
    application.add_handler(CommandHandler("leaderboard", leaderboard))
    application.add_handler(CommandHandler("top", leaderboard))
    application.add_handler(CommandHandler("addpoints", add_manual_points))
    application.add_handler(CommandHandler("setpic", set_custom_pic))
    application.add_handler(CommandHandler("getpic", get_custom_pic))
    application.add_handler(CommandHandler("pics", list_custom_pics))

    application.add_handler(CommandHandler("owner", owner_panel))
    application.add_handler(CommandHandler("restrict", restrict_user))
    application.add_handler(CommandHandler("allow", allow_user))
    application.add_handler(CommandHandler("mute", soft_mute))
    application.add_handler(CommandHandler("unmute", soft_unmute))
    application.add_handler(CommandHandler("warns", show_warnings))
    application.add_handler(CommandHandler("clearwarns", clear_warnings))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("group", group_panel))
    application.add_handler(CommandHandler("verifyon", verify_on))
    application.add_handler(CommandHandler("verifyoff", verify_off))
    application.add_handler(CommandHandler("setwelcome", set_welcome_pic))
    application.add_handler(CommandHandler("setstartpic", set_start_pic))

    application.add_handler(CallbackQueryHandler(privacy_policy, pattern="privacy_policy"))
    application.add_handler(CallbackQueryHandler(profile_data_info, pattern="profile_data_info"))
    application.add_handler(CallbackQueryHandler(verify_callback, pattern="verify|verification_info"))

    application.add_handler(MessageHandler(filters.ALL, save_group), group=-1)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, profile_message_handler), group=0)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, moderation_guard), group=1)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, enforce_verification), group=2)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reward_activity), group=3)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_reply), group=4)

    return application


def main() -> None:
    application = build_app()
    application.run_polling()


if __name__ == "__main__":
    main()
