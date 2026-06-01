from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from utils.stylish_text import s


async def commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return
    text = (
        f"{s('AZAI Commands')}\n\n"
        "User:\n"
        "/start\n/setup\n/profile\n/leaderboard\n/top\n/setpic name\n/getpic name\n/pics\n\n"
        "Owner/Admin:\n"
        "/owner\n/group\n/verifyon\n/verifyoff\n/setwelcome\n/setstartpic\n/restrict user_id reason\n/allow user_id\n/mute user_id\n/unmute user_id\n/addpoints user_id amount\n"
    )
    await message.reply_text(text)
