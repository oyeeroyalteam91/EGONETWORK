from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _int_env(name: str, default: int | None = None) -> int:
    value = os.getenv(name, "").strip()
    if not value:
        if default is None:
            raise RuntimeError(f"Missing required environment variable: {name}")
        return default
    return int(value)


@dataclass(frozen=True)
class Settings:
    bot_token: str
    owner_id: int
    aliza_id: int
    bot_name: str
    network_name: str
    est_year: str
    base_location: str
    updates_channel: str
    support_link: str
    my_master: str
    mongo_uri: str
    mongo_db_name: str
    ai_provider: str
    ai_api_key: str
    webapp_url: str


settings = Settings(
    bot_token=_required("BOT_TOKEN"),
    owner_id=_int_env("OWNER_ID"),
    aliza_id=_int_env("ALIZA_ID"),
    bot_name=os.getenv("BOT_NAME", "AZAI"),
    network_name=os.getenv("NETWORK_NAME", "EGO NETWORK"),
    est_year=os.getenv("EST_YEAR", "2026"),
    base_location=os.getenv("BASE_LOCATION", "Patna, Bihar"),
    updates_channel=os.getenv("UPDATES_CHANNEL", "https://t.me/EGOxUPDATES"),
    support_link=os.getenv("SUPPORT_LINK", "https://t.me/EGOxSUPPORT"),
    my_master=os.getenv("MY_MASTER", "https://t.me/EGOISTICxPRIME"),
    mongo_uri=_required("MONGO_URI"),
    mongo_db_name=os.getenv("MONGO_DB_NAME", "azai_db"),
    ai_provider=os.getenv("AI_PROVIDER", "none"),
    ai_api_key=os.getenv("AI_API_KEY", ""),
    webapp_url=os.getenv("WEBAPP_URL", ""),
)
