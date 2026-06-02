from __future__ import annotations

import os
import httpx

from config import settings

API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.getenv("GQRI_MODEL", "llama-3.1-8b-instant")

PROMPT = "AZAI for EGO NETWORK. Talk in natural Hinglish. Owner is Mr. Ego or Sir. Aliza is Bhabhi Ji or Mam. Be chill, confident, witty, respectful, protective, and concise."


def api_key() -> str:
    return os.getenv("GQRI_API_KEY", "").strip() or os.getenv("GROQ_API_KEY", "").strip()


def owner_name(user_id: int | None) -> str:
    if user_id == settings.owner_id:
        return "Mr. Ego, Sir"
    if user_id == settings.aliza_id:
        return "Bhabhi Ji"
    return "bhai"


def fallback_reply(user_id: int | None, text: str) -> str:
    t = text.lower().strip()
    name = owner_name(user_id)
    if user_id == settings.owner_id and any(x in t for x in ["hi", "hlo", "hello", "hey", "azai"]):
        return f"{name}, AZAI active hai. Scene bolo, handle karte hain."
    if user_id == settings.aliza_id:
        return "Ji Bhabhi Ji, full respect mode on hai. Aap bolo."
    if any(x in t for x in ["hi", "hlo", "hello", "hey"]):
        return "Haan bhai, AZAI active hai. Kya scene hai?"
    if "kaisa" in t or "kaise" in t:
        return "Chill mode on hai bhai. System stable hai, bas kaam batao."
    if "tension" in t or "sad" in t or "problem" in t:
        return "Relax bhai. Scene tough ho sakta hai, tu weak nahi. Pehle calm ho, phir step by step solve karte hain."
    if "bhabhi" in t or "aliza" in t:
        return "Bhabhi Ji ke liye respect always top level par hai."
    return f"{name}, samjha. Thoda clear bol do, main scene pakad ke reply karta hoon."


async def azai_reply(user_id: int | None, text: str) -> str:
    key = api_key()
    if not key:
        return fallback_reply(user_id, text)
    role = "Owner Mr. Ego" if user_id == settings.owner_id else "Bhabhi Ji" if user_id == settings.aliza_id else "Member"
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            res = await client.post(
                API_URL,
                headers={"Authorization": f"Bearer {key}"},
                json={"model": MODEL, "messages": [{"role": "system", "content": PROMPT}, {"role": "user", "content": f"{role}: {text}"}], "temperature": 0.8, "max_tokens": 180},
            )
        data = res.json()
        reply = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return reply or fallback_reply(user_id, text)
    except Exception:
        return fallback_reply(user_id, text)
