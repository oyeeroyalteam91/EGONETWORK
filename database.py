from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo import MongoClient, ASCENDING

from config import settings

client = MongoClient(settings.mongo_uri)
db = client[settings.mongo_db_name]

users = db["users"]
groups = db["groups"]
warnings = db["warnings"]
gbans = db["gbans"]

users.create_index([("user_id", ASCENDING)], unique=True)
groups.create_index([("chat_id", ASCENDING)], unique=True)
warnings.create_index([("chat_id", ASCENDING), ("user_id", ASCENDING)], unique=True)
gbans.create_index([("user_id", ASCENDING)], unique=True)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def upsert_user(user_id: int, data: dict[str, Any]) -> None:
    users.update_one(
        {"user_id": user_id},
        {"$set": {**data, "updated_at": now_utc()}, "$setOnInsert": {"created_at": now_utc()}},
        upsert=True,
    )


def get_user(user_id: int) -> dict[str, Any] | None:
    return users.find_one({"user_id": user_id})


def is_verified(user_id: int, chat_id: int | None = None) -> bool:
    user = get_user(user_id)
    if not user:
        return False
    if chat_id is None:
        return bool(user.get("verified"))
    verified_groups = user.get("verified_groups", [])
    return bool(user.get("verified")) and chat_id in verified_groups


def mark_verified(user_id: int, chat_id: int | None = None) -> None:
    update: dict[str, Any] = {"verified": True, "verified_at": now_utc(), "updated_at": now_utc()}
    operation: dict[str, Any] = {"$set": update, "$setOnInsert": {"created_at": now_utc()}}
    if chat_id is not None:
        operation["$addToSet"] = {"verified_groups": chat_id}
    users.update_one({"user_id": user_id}, operation, upsert=True)


def is_gbanned(user_id: int) -> bool:
    return gbans.find_one({"user_id": user_id}) is not None


def add_gban(user_id: int, reason: str, by_user_id: int) -> None:
    gbans.update_one(
        {"user_id": user_id},
        {"$set": {"reason": reason, "by_user_id": by_user_id, "created_at": now_utc()}},
        upsert=True,
    )


def remove_gban(user_id: int) -> None:
    gbans.delete_one({"user_id": user_id})


def add_warning(chat_id: int, user_id: int, reason: str) -> int:
    result = warnings.find_one_and_update(
        {"chat_id": chat_id, "user_id": user_id},
        {
            "$inc": {"count": 1},
            "$push": {"reasons": {"reason": reason, "at": now_utc()}},
            "$setOnInsert": {"created_at": now_utc()},
            "$set": {"updated_at": now_utc()},
        },
        upsert=True,
        return_document=True,
    )
    return int(result.get("count", 1)) if result else 1
