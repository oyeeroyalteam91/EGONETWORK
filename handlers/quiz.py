from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Literal

import httpx
from bson import ObjectId
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from config import settings
from database import db, now_utc
from handlers.economy import add_coins
from utils.stylish_text import s

QuizType = Literal["anime", "gk"]

active_quizzes = db["active_quizzes"]
quiz_answers = db["quiz_answers"]
auto_quiz_chats = db["auto_quiz_chats"]
anime_quiz_pics = db["anime_quiz_pics"]

QUIZ_REWARD = 50


@dataclass(frozen=True)
class QuizQuestion:
    question: str
    options: list[str]
    answer_index: int
    key: str = ""


ANIME_QUESTIONS: list[QuizQuestion] = [
    QuizQuestion("Guess this anime character from the picture.", ["Naruto Uzumaki", "Monkey D. Luffy", "Ichigo Kurosaki", "Goku"], 0, "naruto"),
    QuizQuestion("Guess this anime character from the picture.", ["Tanjiro Kamado", "Monkey D. Luffy", "Levi Ackerman", "Saitama"], 1, "luffy"),
    QuizQuestion("Guess this anime character from the picture.", ["Eren Yeager", "Gojo Satoru", "Goku", "Light Yagami"], 2, "goku"),
    QuizQuestion("Guess this anime character from the picture.", ["Light Yagami", "Naruto Uzumaki", "Vegeta", "Asta"], 0, "light"),
    QuizQuestion("Guess this anime character from the picture.", ["Saitama", "Itachi Uchiha", "Roronoa Zoro", "Deku"], 0, "saitama"),
]

GK_QUESTIONS: list[QuizQuestion] = [
    QuizQuestion("What is the capital of India?", ["Mumbai", "New Delhi", "Kolkata", "Patna"], 1),
    QuizQuestion("Which planet is known as the Red Planet?", ["Mars", "Venus", "Jupiter", "Mercury"], 0),
    QuizQuestion("How many days are in a leap year?", ["365", "366", "364", "360"], 1),
    QuizQuestion("Who wrote the Indian National Anthem?", ["Mahatma Gandhi", "Rabindranath Tagore", "B. R. Ambedkar", "Subhas Chandra Bose"], 1),
    QuizQuestion("Which gas do plants absorb mostly for photosynthesis?", ["Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen"], 1),
]


def is_owner(user_id: int | None) -> bool:
    return user_id == settings.owner_id


def pick_question(quiz_type: QuizType) -> QuizQuestion:
    return random.choice(ANIME_QUESTIONS if quiz_type == "anime" else GK_QUESTIONS)


def quiz_keyboard(quiz_id: str, options: list[str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(option, callback_data=f"quiz:{quiz_id}:{index}")] for index, option in enumerate(options)])


def get_anime_pic_file_id(question_key: str) -> str | None:
    row = anime_quiz_pics.find_one({"key": question_key}) or {}
    return row.get("file_id") or row.get("image_url")


async def fetch_anime_image(question: QuizQuestion) -> str | None:
    saved = get_anime_pic_file_id(question.key)
    if saved:
        return saved
    character_name = question.options[question.answer_index]
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get("https://api.jikan.moe/v4/characters", params={"q": character_name, "limit": 1})
            data = response.json()
            image_url = data.get("data", [{}])[0].get("images", {}).get("jpg", {}).get("image_url")
            if image_url:
                anime_quiz_pics.update_one({"key": question.key}, {"$set": {"image_url": image_url, "updated_at": now_utc(), "auto": True}}, upsert=True)
                return image_url
    except Exception:
        return None
    return None


async def pick_anime_question_with_image() -> tuple[QuizQuestion | None, str | None]:
    questions = ANIME_QUESTIONS[:]
    random.shuffle(questions)
    for question in questions:
        image = await fetch_anime_image(question)
        if image:
            return question, image
    return None, None


async def send_quiz(context: ContextTypes.DEFAULT_TYPE, chat_id: int, quiz_type: QuizType) -> None:
    image_url = None
    if quiz_type == "anime":
        question, image_url = await pick_anime_question_with_image()
        if not question:
            quiz_type = "gk"
            question = pick_question("gk")
    else:
        question = pick_question("gk")
    inserted = active_quizzes.insert_one({"chat_id": chat_id, "type": quiz_type, "question": question.question, "options": question.options, "answer_index": question.answer_index, "question_key": question.key, "created_at": now_utc(), "open": True})
    quiz_id = str(inserted.inserted_id)
    title = "Anime Pic Quiz" if quiz_type == "anime" else "GK Quiz"
    text = f"{s(title)}\n\n{s(question.question)}\n\n{s('Choose carefully. Only one chance is allowed.')}\n{s(f'Reward: {QUIZ_REWARD} coins')}"
    if quiz_type == "anime" and image_url:
        await context.bot.send_photo(chat_id=chat_id, photo=image_url, caption=text, reply_markup=quiz_keyboard(quiz_id, question.options))
    else:
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=quiz_keyboard(quiz_id, question.options))


async def anime_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat:
        await send_quiz(context, chat.id, "anime")


async def gk_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat:
        await send_quiz(context, chat.id, "gk")


async def quiz_answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = update.effective_user
    if not query or not user or not query.data or not query.message:
        return
    await query.answer()
    parts = query.data.split(":")
    if len(parts) != 3:
        return
    quiz_id, selected_raw = parts[1], parts[2]
    selected = int(selected_raw)
    quiz = active_quizzes.find_one({"_id": ObjectId(quiz_id)})
    if not quiz or not quiz.get("open", True):
        await query.message.reply_text(s("This quiz is closed."))
        return
    existing = quiz_answers.find_one({"quiz_id": quiz_id, "user_id": user.id})
    if existing:
        await query.message.reply_text(s("You already used your one chance."))
        return
    correct = selected == int(quiz["answer_index"])
    quiz_answers.insert_one({"quiz_id": quiz_id, "user_id": user.id, "selected": selected, "correct": correct, "created_at": now_utc()})
    if correct:
        total = add_coins(user.id, QUIZ_REWARD, f"{quiz.get('type', 'quiz')}_quiz_win")
        await query.message.reply_text(s(f"Correct answer. You earned {QUIZ_REWARD} coins. Balance: {total}"))
    else:
        correct_option = quiz["options"][int(quiz["answer_index"])]
        await query.message.reply_text(s(f"Wrong answer. Correct answer: {correct_option}"))


async def set_anime_quiz_pic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return
    if not is_owner(user.id):
        await message.reply_text(s("Owner access required."))
        return
    if not context.args:
        keys = ", ".join(q.key for q in ANIME_QUESTIONS)
        await message.reply_text(f"Usage: /setanimepic key\nKeys: {keys}")
        return
    key = context.args[0].lower().strip()
    valid_keys = {q.key for q in ANIME_QUESTIONS}
    if key not in valid_keys:
        await message.reply_text(s("Invalid anime key."))
        return
    source = message.reply_to_message if message.reply_to_message and message.reply_to_message.photo else message
    if not source.photo:
        await message.reply_text(s("Reply to an anime character photo with /setanimepic key."))
        return
    anime_quiz_pics.update_one({"key": key}, {"$set": {"file_id": source.photo[-1].file_id, "updated_at": now_utc(), "auto": False}}, upsert=True)
    await message.reply_text(s(f"Anime quiz picture saved for {key}."))


async def anime_pic_keys(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return
    lines = [s("Anime Pic Quiz Keys")]
    for question in ANIME_QUESTIONS:
        saved = "set" if get_anime_pic_file_id(question.key) else "auto-ready"
        lines.append(f"{question.key}: {question.options[question.answer_index]} - {saved}")
    await message.reply_text("\n".join(lines))


async def enable_auto_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message
    if chat and message:
        auto_quiz_chats.update_one({"chat_id": chat.id}, {"$set": {"enabled": True, "updated_at": now_utc()}}, upsert=True)
        await message.reply_text(s("Auto quiz enabled. Anime Pic Quiz and GK Quiz will run every 30 minutes."))


async def disable_auto_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message
    if chat and message:
        auto_quiz_chats.update_one({"chat_id": chat.id}, {"$set": {"enabled": False, "updated_at": now_utc()}}, upsert=True)
        await message.reply_text(s("Auto quiz disabled."))


async def auto_quiz_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    for item in auto_quiz_chats.find({"enabled": True}):
        quiz_type: QuizType = random.choice(["anime", "gk"])
        try:
            await send_quiz(context, int(item["chat_id"]), quiz_type)
        except Exception:
            continue
