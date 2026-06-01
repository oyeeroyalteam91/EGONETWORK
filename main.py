from __future__ import annotations

import logging

from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from config import settings
from handlers.chat import chat_reply
from handlers.moderation import moderation_guard
from handlers.start import privacy_policy, start
from handlers.verification import enforce_verification, verify_callback

logging.basicConfig(level=logging.INFO)


def build_app() -> Application:
    application = Application.builder().token(settings.bot_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(privacy_policy, pattern="privacy_policy"))
    application.add_handler(CallbackQueryHandler(verify_callback, pattern="verify|verification_info"))
    application.add_handler(MessageHandler(filters.TEXT, moderation_guard), group=1)
    application.add_handler(MessageHandler(filters.TEXT, enforce_verification), group=2)
    application.add_handler(MessageHandler(filters.TEXT, chat_reply), group=3)
    return application


def main() -> None:
    application = build_app()
    application.run_polling()


if __name__ == "__main__":
    main()
