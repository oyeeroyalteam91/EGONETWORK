from __future__ import annotations

import logging
from datetime import time
from zoneinfo import ZoneInfo
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters
from config import settings
from handlers.admin_tools import allow_user, owner_panel, restrict_user, soft_mute, soft_unmute
from handlers.assets import set_start_media, show_start_media
from handlers.broadcast import broadcast
from handlers.chat import chat_reply
from handlers.commands import commands
from handlers.economy import balance, daily
from handlers.events import add_event, daily_event_job, event_status, events_panel
from handlers.games import basketball, bowling, dart, dice, football, slot
from handlers.group_settings import group_panel, save_group, set_start_pic, set_welcome_pic, verify_off, verify_on
from handlers.leaderboard import add_manual_points, leaderboard, reward_activity, set_leader_pic
from handlers.media import get_custom_pic, list_custom_pics, set_custom_pic
from handlers.moderation import moderation_guard
from handlers.profile import my_profile, profile_data_info, profile_message_handler, setup_profile
from handlers.quiz import anime_pic_keys, anime_quiz, auto_quiz_job, disable_auto_quiz, enable_auto_quiz, gk_quiz, quiz_answer_callback, set_anime_quiz_pic
from handlers.quiz_toggle import autoquiz_toggle
from handlers.shop import add_shop_item, buy_callback, my_items, set_shop_media, shop
from handlers.start import privacy_policy, start
from handlers.verification import enforce_verification, verify_callback, verify_command
from handlers.warnings import clear_warnings, show_warnings
from handlers.welcome import welcome_new_members

logging.basicConfig(level=logging.INFO)
INDIA_TZ = ZoneInfo("Asia/Kolkata")

USER_COMMANDS = {
    "start": start, "verify": verify_command, "help": commands, "commands": commands,
    "setup": setup_profile, "profile": my_profile, "balance": balance, "daily": daily,
    "leaderboard": leaderboard, "top": leaderboard, "setleaderpic": set_leader_pic,
    "setpic": set_custom_pic, "getpic": get_custom_pic, "pics": list_custom_pics,
    "animequiz": anime_quiz, "gkquiz": gk_quiz, "animepickeys": anime_pic_keys,
    "dice": dice, "dart": dart, "basketball": basketball, "football": football,
    "bowling": bowling, "slot": slot, "shop": shop, "inventory": my_items, "items": my_items,
    "events": events_panel, "eventstatus": event_status,
}

OWNER_COMMANDS = {
    "owner": owner_panel, "restrict": restrict_user, "allow": allow_user,
    "mute": soft_mute, "unmute": soft_unmute, "warns": show_warnings,
    "clearwarns": clear_warnings, "broadcast": broadcast, "group": group_panel,
    "verifyon": verify_on, "verifyoff": verify_off, "setwelcome": set_welcome_pic,
    "setstartpic": set_start_pic, "setstartmedia": set_start_media, "startmedia": show_start_media,
    "setshopmedia": set_shop_media, "additem": add_shop_item, "addpoints": add_manual_points,
    "setanimepic": set_anime_quiz_pic, "autoquiz": autoquiz_toggle,
    "autoquizon": enable_auto_quiz, "autoquizoff": disable_auto_quiz, "addevent": add_event,
}


def build_app() -> Application:
    app = Application.builder().token(settings.bot_token).build()
    for command, handler in {**USER_COMMANDS, **OWNER_COMMANDS}.items():
        app.add_handler(CommandHandler(command, handler))
    app.add_handler(CallbackQueryHandler(privacy_policy, pattern="privacy_policy"))
    app.add_handler(CallbackQueryHandler(profile_data_info, pattern="profile_data_info"))
    app.add_handler(CallbackQueryHandler(verify_callback, pattern="verify|verification_info"))
    app.add_handler(CallbackQueryHandler(quiz_answer_callback, pattern="^quiz:"))
    app.add_handler(CallbackQueryHandler(buy_callback, pattern="^buy:"))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_members), group=-2)
    app.add_handler(MessageHandler(filters.ALL, save_group), group=-1)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, profile_message_handler), group=0)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, moderation_guard), group=1)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, enforce_verification), group=2)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reward_activity), group=3)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_reply), group=4)
    if app.job_queue:
        app.job_queue.run_repeating(auto_quiz_job, interval=1800, first=60)
        app.job_queue.run_daily(daily_event_job, time=time(hour=0, minute=5, tzinfo=INDIA_TZ), name="india_daily_events")
    return app


def main() -> None:
    build_app().run_polling()


if __name__ == "__main__":
    main()
