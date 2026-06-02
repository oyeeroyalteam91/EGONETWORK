from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from handlers.profile import auto_setup_if_needed
from handlers.start import start


async def start_flow(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)
    await auto_setup_if_needed(update, context)
