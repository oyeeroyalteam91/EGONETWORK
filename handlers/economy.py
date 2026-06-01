from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from database import db, now_utc
from utils.stylish_text import s

wallets = db["wallets"]
transactions = db["transactions"]

DEFAULT_DAILY_AMOUNT = 100


def get_balance(user_id: int) -> int:
    wallet = wallets.find_one({"user_id": user_id}) or {}
    return int(wallet.get("coins", 0))


def add_coins(user_id: int, amount: int, reason: str) -> int:
    result = wallets.find_one_and_update(
        {"user_id": user_id},
        {"$inc": {"coins": amount}, "$set": {"updated_at": now_utc()}, "$setOnInsert": {"created_at": now_utc()}},
        upsert=True,
        return_document=True,
    )
    transactions.insert_one({"user_id": user_id, "amount": amount, "reason": reason, "created_at": now_utc()})
    return int(result.get("coins", amount)) if result else amount


def spend_coins(user_id: int, amount: int, reason: str) -> tuple[bool, int]:
    current = get_balance(user_id)
    if current < amount:
        return False, current
    new_total = add_coins(user_id, -amount, reason)
    return True, new_total


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    await message.reply_text(s(f"Your balance: {get_balance(user.id)} coins"))


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    total = add_coins(user.id, DEFAULT_DAILY_AMOUNT, "daily_reward")
    await message.reply_text(s(f"Daily reward claimed: {DEFAULT_DAILY_AMOUNT} coins. Balance: {total}"))
