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
        "/start\n/help\n/commands\n/setup\n/profile\n/balance\n/daily\n"
        "/leaderboard\n/top\n/animequiz\n/gkquiz\n"
        "/dice\n/dart\n/basketball\n/football\n/bowling\n/slot\n"
        "/shop\n/inventory\n/items\n/setpic name\n/getpic name\n/pics\n\n"
        "Anime Pic Setup:\n"
        "/animepickeys - show anime keys\n"
        "/setanimepic key - reply to photo and save it for that character\n"
        "Example:\n"
        "Reply to Naruto photo with /setanimepic naruto\n"
        "If no custom photo is saved, AZAI will try auto image access for anime quiz.\n\n"
        "Owner/Admin:\n"
        "/owner\n/group\n/verifyon\n/verifyoff\n/setwelcome\n/setstartpic\n/setstartmedia\n/startmedia\n"
        "/setshopmedia item_key\n/autoquizon\n/autoquizoff\n"
        "/restrict user_id reason\n/allow user_id\n/mute user_id\n/unmute user_id\n"
        "/warns user_id\n/clearwarns user_id\n/broadcast message\n/addpoints user_id amount\n"
    )
    await message.reply_text(text)
