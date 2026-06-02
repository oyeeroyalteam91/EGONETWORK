from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config import settings
from database import db, now_utc
from handlers.economy import get_balance, spend_coins

shop_items = db["shop_items"]
inventory = db["inventory"]


def is_owner(user_id: int | None) -> bool:
    return user_id == settings.owner_id


def shop_keyboard(items: list[dict]) -> InlineKeyboardMarkup:
    buttons = []
    for item in items:
        buttons.append([InlineKeyboardButton(f"Buy {item['name']} — {item['price']} coins", callback_data=f"buy:{item['key']}")])
    return InlineKeyboardMarkup(buttons)


async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    items = list(shop_items.find({}).sort("price", 1).limit(20))
    if not items:
        await message.reply_text(
            "EGO Shop\n"
            f"{settings.network_name} | EST. {settings.est_year}\n\n"
            "No items added yet.\n"
            "Owner can add items with:\n"
            "/additem key price name\n\n"
            f"Balance: {get_balance(user.id)} coins"
        )
        return
    lines = ["EGO Shop", f"{settings.network_name} | EST. {settings.est_year}", ""]
    for item in items:
        media_status = "Media: Set" if item.get("media_file_id") else "Media: Not set"
        lines.append(f"{item['name']} — {item['price']} coins")
        lines.append(item.get("description", "Premium EGO item."))
        lines.append(media_status)
        lines.append("")
    lines.append(f"Balance: {get_balance(user.id)} coins")
    await message.reply_text("\n".join(lines), reply_markup=shop_keyboard(items))


async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = update.effective_user
    if not query or not user or not query.data or not query.message:
        return
    await query.answer()
    key = query.data.split(":", 1)[1]
    item = shop_items.find_one({"key": key})
    if not item:
        await query.message.reply_text("Item not found.")
        return
    ok, balance = spend_coins(user.id, int(item["price"]), f"buy_{key}")
    if not ok:
        await query.message.reply_text(f"Not enough coins. Balance: {balance}")
        return
    inventory.insert_one({"user_id": user.id, "item_key": key, "price": item["price"], "created_at": now_utc()})
    caption = f"Purchase complete: {item['name']}\nBalance: {balance} coins\nSaved to your vault."
    media_file_id = item.get("media_file_id")
    media_type = item.get("media_type", "photo")
    if media_file_id and media_type == "animation":
        await query.message.reply_animation(animation=media_file_id, caption=caption)
    elif media_file_id:
        await query.message.reply_photo(photo=media_file_id, caption=caption)
    else:
        await query.message.reply_text(caption)


async def send_item_media(message, item: dict, caption: str) -> None:
    media_file_id = item.get("media_file_id")
    media_type = item.get("media_type", "photo")
    if media_file_id and media_type == "animation":
        await message.reply_animation(animation=media_file_id, caption=caption)
    elif media_file_id:
        await message.reply_photo(photo=media_file_id, caption=caption)
    else:
        await message.reply_text(caption)


async def my_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    rows = list(inventory.find({"user_id": user.id}).sort("created_at", -1).limit(20))
    if not rows:
        await message.reply_text("Your EGO Vault is empty.")
        return
    await message.reply_text(f"Your EGO Vault: {len(rows)} item(s)")
    for row in rows:
        item = shop_items.find_one({"key": row.get("item_key")}) or {}
        name = item.get("name", row.get("item_key", "Unknown Item"))
        price = row.get("price", item.get("price", 0))
        caption = f"Vault Item: {name}\nPurchased for: {price} coins"
        await send_item_media(message, item, caption)


async def add_shop_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    if not is_owner(user.id):
        await message.reply_text("Owner access required.")
        return
    if len(context.args) < 3:
        await message.reply_text("Usage: /additem key price name")
        return
    key = context.args[0].lower().strip()
    price = int(context.args[1])
    name = " ".join(context.args[2:]).strip()
    shop_items.update_one(
        {"key": key},
        {"$set": {"name": name, "price": price, "description": "Premium EGO item.", "updated_at": now_utc()}, "$setOnInsert": {"created_at": now_utc(), "media_file_id": "", "media_type": "photo"}},
        upsert=True,
    )
    await message.reply_text(f"Shop item saved: {name}")


async def remove_shop_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    if not is_owner(user.id):
        await message.reply_text("Owner access required.")
        return
    if not context.args:
        await message.reply_text("Usage: /removeitem key")
        return
    key = context.args[0].lower().strip()
    shop_items.delete_one({"key": key})
    await message.reply_text(f"Shop item removed: {key}")


async def set_shop_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    if not is_owner(user.id):
        await message.reply_text("Owner access required.")
        return
    if len(context.args) < 1:
        await message.reply_text("Usage: /setshopmedia item_key")
        return
    key = context.args[0].lower().strip()
    source = message.reply_to_message
    if not source:
        await message.reply_text("Reply to a photo or GIF with /setshopmedia item_key.")
        return
    media_type = None
    file_id = None
    if source.animation:
        media_type = "animation"
        file_id = source.animation.file_id
    elif source.photo:
        media_type = "photo"
        file_id = source.photo[-1].file_id
    if not file_id:
        await message.reply_text("Only photo or GIF animation is supported for shop media.")
        return
    shop_items.update_one({"key": key}, {"$set": {"media_type": media_type, "media_file_id": file_id, "updated_at": now_utc()}}, upsert=True)
    await message.reply_text(f"Shop media saved for {key}.")
