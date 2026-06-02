from __future__ import annotations

from config import settings


def owner_name(user_id: int | None) -> str:
    if user_id == settings.owner_id:
        return "Mr. Ego, Sir"
    if user_id == settings.aliza_id:
        return "Bhabhi Ji"
    return "bhai"


def azai_reply(user_id: int | None, text: str) -> str:
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

    if "kya kar" in t or "help" in t or "madad" in t:
        return "Batao kya chahiye. Group control, shop, quiz, events, verification, sab handle kar sakta hoon."

    if "tension" in t or "sad" in t or "problem" in t:
        return "Relax bhai. Scene tough ho sakta hai, tu weak nahi. Pehle calm ho, phir step by step solve karte hain."

    if "bhabhi" in t or "aliza" in t:
        return "Bhabhi Ji ke liye respect always top level par hai."

    if "shop" in t:
        return "Shop ke liye /shop use karo. Owner item add karega /additem se, aur media /setshopmedia se."

    if "quiz" in t:
        return "Quiz ke liye /animequiz, /gkquiz, aur auto ke liye /autoquiz use karo. Anime pic set karne ke liye /setanimepic key."

    if "verify" in t or "verification" in t:
        return "Verification ke liye group me /verify use karo. Ek baar verified ho jao to dobara verify nahi karna padega."

    return f"{name}, samjha. Thoda clear bol do, main scene pakad ke reply karta hoon."
