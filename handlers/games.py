from __future__ import annotations

from telegram import Dice, Update
from telegram.ext import ContextTypes

from handlers.economy import add_coins
from utils.stylish_text import s

GAME_REWARDS = {
    "dice": 20,
    "dart": 30,
    "basketball": 35,
    "football": 35,
    "bowling": 35,
}

GAME_EMOJIS = {
    "dice": "🎲",
    "dart": "🎯",
    "basketball": "🏀",
    "football": "⚽",
    "bowling": "🎳",
}


def is_win(game: str, value: int) -> bool:
    if game == "dice":
        return value == 6
    if game == "dart":
        return value == 6
    if game == "basketball":
        return value >= 4
    if game == "football":
        return value >= 4
    if game == "bowling":
        return value >= 5
    return False


async def play_game(update: Update, context: ContextTypes.DEFAULT_TYPE, game: str) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    dice_message = await message.reply_dice(emoji=GAME_EMOJIS[game])
    dice: Dice | None = dice_message.dice
    if not dice:
        return
    if is_win(game, dice.value):
        reward = GAME_REWARDS[game]
        total = add_coins(user.id, reward, f"{game}_win")
        await message.reply_text(s(f"You earned {reward} coins. Balance: {total}"))
    else:
        await message.reply_text(s("Not a win this time. Try again with style."))


async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await play_game(update, context, "dice")


async def dart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await play_game(update, context, "dart")


async def basketball(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await play_game(update, context, "basketball")


async def football(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await play_game(update, context, "football")


async def bowling(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await play_game(update, context, "bowling")


async def slot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return
    await message.reply_dice(emoji="🎰")
    await message.reply_text(s("Fun animation only. No coins, no bets, no cashout."))
