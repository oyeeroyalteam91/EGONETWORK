from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Literal

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from database import db, now_utc
from handlers.economy import add_coins
from utils.stylish_text import s

QuizType = Literal["anime", "gk"]

active_quizzes = db["active_quizzes"]
quiz_answers = db["quiz_answers"]

auto_quiz_chats = db["auto_quiz_chats"]

QUIZ_REWARD = 50


@dataclass(frozen=True)
class QuizQuestion:
    question: str
    options: list[str]
    answer_index: int


ANIME_QUESTIONS: list[QuizQuestion] = [
    QuizQuestion("Which anime character wants to become Hokage?", ["Naruto Uzumaki", "Luffy", "Ichigo", "Goku"], 0),
    QuizQuestion("Who is known as the Pirate King goal chaser?", ["Tanjiro", "Monkey D. Luffy", "Levi", "Saitama"], 1),
    QuizQuestion("Which character is from Dragon Ball?", ["Eren Yeager", "Gojo Satoru", "Goku", "Light Yagami"], 2),
    QuizQuestion("Who uses Death Note?", ["Light Yagami", "Naruto", "Vegeta", "Asta"], 0),
    QuizQuestion("Who is famous for One Punch?", ["Saitama", "Itachi", "Zoro", "Deku"], 0),
]

GK_QUESTIONS: list[QuizQuestion] = [
    QuizQuestion("What is the capital of India?", ["Mumbai", "New Delhi", "Kolkata", "Patna"], 1),
    QuizQuestion("Which planet is known as the Red Planet?", ["Mars", "Venus", "Jupiter", "Mercury"], 0),
    QuizQuestion("How many days are in a leap year?", ["365", "366", "364", "360"], 1),
    QuizQuestion("Who wrote the Indian National Anthem?", ["Mahatma Gandhi", "Rabindranath Tagore", "B. R. Ambedkar", "Subhas Chandra Bose"], 1),
    QuizQuestion("Which gas do plants absorb mostly for photosynthesis?", ["Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen"], 1),
]


def pick_question(quiz_type: QuizType) -> QuizQuestion:
    return random.choice(ANIME_QUESTIONS if quiz_type == "anime" else GK_QUESTIONS)


def quiz_keyboard(quiz_id: str, options: list[str]) -> InlineKeyboardMarkup:
    buttons = []
    for index, option in enumerate(options):
        buttons.append([InlineKeyboardButton(option, callback_data=f"quiz:{quiz_id}:{index}")])
    return InlineKeyboardMarkup(buttons)


async def send_quiz(context: ContextTypes.DEFAULT_TYPE, chat_id: int, quiz_type: QuizType) -> None:
    question = pick_question(quiz_type)
    inserted = active_quizzes.insert_one({
        "chat_id": chat_id,
        "type": quiz_type,
        "question": question.question,
        "options": question.options,
        "answer_index": question.answer_index,
        "created_at": now_utc(),
        "open": True,
    })
    quiz_id = str(inserted.inserted_id)
    title = "Anime Quiz" if quiz_type == "anime" else "GK Quiz"
    text = (
        f"{s(title)}\n\n"
        f"{s(question.question)}\n\n"
        f"{s('Choose carefully. Only one chance is allowed.')}\n"
        f"{s(f'Reward: {QUIZ_REWARD} coins')}"
    )
    await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=quiz_keyboard(quiz_id, question.options))


async def anime_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if not chat:
        return
    await send_quiz(context, chat.id, "anime")


async def gk_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if not chat:
        return
    await send_quiz(context, chat.id, "gk")


async def quiz_answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = update.effective_user
    if not query or not user or not query.data:
        return
    await query.answer()
    parts = query.data.split(":")
    if len(parts) != 3:
        return
    quiz_id, selected_raw = parts[1], parts[2]
    selected = int(selected_raw)
    quiz = active_quizzes.find_one({"_id": __import__("bson").ObjectId(quiz_id)})
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
        await query.message.reply_text(s(f"Correct answer. You won {QUIZ_REWARD} coins. Balance: {total}"))
    else:
        correct_option = quiz["options"][int(quiz["answer_index"])]
        await query.message.reply_text(s(f"Wrong answer. Correct answer: {correct_option}"))


async def enable_auto_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return
    auto_quiz_chats.update_one({"chat_id": chat.id}, {"$set": {"enabled": True, "updated_at": now_utc()}}, upsert=True)
    await message.reply_text(s("Auto quiz enabled. Anime and GK quizzes will run every 30 minutes."))


async def disable_auto_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    message = update.effective_message
    if not chat or not message:
        return
    auto_quiz_chats.update_one({"chat_id": chat.id}, {"$set": {"enabled": False, "updated_at": now_utc()}}, upsert=True)
    await message.reply_text(s("Auto quiz disabled."))


async def auto_quiz_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    for item in auto_quiz_chats.find({"enabled": True}):
        quiz_type: QuizType = random.choice(["anime", "gk"])
        try:
            await send_quiz(context, int(item["chat_id"]), quiz_type)
        except Exception:
            continue
