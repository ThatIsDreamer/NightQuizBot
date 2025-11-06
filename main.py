"""
Телеграм-бот квиз об античной Греции.
Использует Aiogram для работы с Telegram Bot API.
"""

import asyncio
import logging
import random
from typing import Dict

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import BOT_TOKEN, QUIZ_QUESTIONS_COUNT
from questions import QuestionManager, Question

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен! Установите переменную окружения BOT_TOKEN.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

question_manager = QuestionManager()


class QuizStates(StatesGroup):
    quiz_in_progress = State()


user_data: Dict[int, Dict] = {}


def get_user_data(user_id: int) -> Dict:
    """Получить или создать данные пользователя."""
    if user_id not in user_data:
        user_data[user_id] = {
            'current_question_index': 0,
            'questions': [],
            'score': 0,
            'answers': []
        }
    return user_data[user_id]


def create_quiz_keyboard(question: Question) -> InlineKeyboardMarkup:
    """Создать клавиатуру с вариантами ответов для вопроса."""
    builder = InlineKeyboardBuilder()
    for idx, option in enumerate(question.options):
        builder.add(InlineKeyboardButton(
            text=option,
            callback_data=f"answer_{question.id}_{idx}"
        ))
    builder.adjust(1)
    return builder.as_markup()


def create_main_keyboard() -> ReplyKeyboardMarkup:
    """Создать главную клавиатуру."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏛️ Начать квиз")],
            [KeyboardButton(text="📊 Моя статистика")],
        ],
        resize_keyboard=True
    )
    return keyboard


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start."""
    welcome_text = (
        "🏛️ Добро пожаловать в квиз об античной Греции! 🏛️\n\n"
        "Я помогу вам проверить свои знания о Древней Греции, её мифологии, "
        "истории и великих личностях.\n\n"
        "Выберите действие:\n"
        "• 🏛️ Начать квиз - ответьте на вопросы об античной Греции\n"
        "• 📊 Моя статистика - посмотрите свои результаты\n\n"
        "Используйте /help для получения справки."
    )
    await message.answer(welcome_text, reply_markup=create_main_keyboard())


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help."""
    help_text = (
        "📖 Справка по боту:\n\n"
        "🏛️ Начать квиз - запускает квиз из 10 вопросов об античной Греции. "
        "На каждый вопрос есть 4 варианта ответа.\n\n"
        "📊 Моя статистика - показывает ваши результаты в последнем квизе.\n\n"
        "Команды:\n"
        "/start - начать работу с ботом\n"
        "/help - показать эту справку\n"
        "/quiz - начать квиз\n"
        "/cancel - отменить текущее действие"
    )
    await message.answer(help_text)


@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message, state: FSMContext):
    """Обработчик команды /quiz."""
    await start_quiz(message, state)


@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    """Обработчик команды /cancel."""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активных действий для отмены.")
        return
    
    await state.clear()
    user_id = message.from_user.id
    if user_id in user_data:
        user_data[user_id] = {
            'current_question_index': 0,
            'questions': [],
            'score': 0,
            'answers': []
        }
    await message.answer("Действие отменено.", reply_markup=create_main_keyboard())


@dp.message(lambda message: message.text == "🏛️ Начать квиз")
async def start_quiz_button(message: types.Message, state: FSMContext):
    """Обработчик кнопки 'Начать квиз'."""
    await start_quiz(message, state)


async def start_quiz(message: types.Message, state: FSMContext):
    """Начать новый квиз."""
    user_id = message.from_user.id
    user_info = get_user_data(user_id)
    
    all_questions = question_manager.get_all_questions()
    selected_questions = random.sample(all_questions, min(QUIZ_QUESTIONS_COUNT, len(all_questions)))
    
    user_info['current_question_index'] = 0
    user_info['questions'] = selected_questions
    user_info['score'] = 0
    user_info['answers'] = []
    
    await state.set_state(QuizStates.quiz_in_progress)
    
    await send_question(message, user_info)


async def send_question(message: types.Message, user_info: Dict):
    """Отправить вопрос пользователю."""
    question_index = user_info['current_question_index']
    questions = user_info['questions']
    
    if question_index >= len(questions):
        await finish_quiz(message, user_info)
        return
    
    question = questions[question_index]
    question_text = (
        f"❓ Вопрос {question_index + 1} из {len(questions)}\n\n"
        f"{question.text}"
    )
    
    keyboard = create_quiz_keyboard(question)
    await message.answer(question_text, reply_markup=keyboard)


@dp.callback_query(lambda c: c.data.startswith("answer_"), StateFilter(QuizStates.quiz_in_progress))
async def process_answer(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик ответа на вопрос."""
    user_id = callback.from_user.id
    user_info = get_user_data(user_id)
    
    _, question_id, answer_index = callback.data.split("_")
    question_id = int(question_id)
    answer_index = int(answer_index)
    
    question_index = user_info['current_question_index']
    question = user_info['questions'][question_index]
    
    is_correct = answer_index == question.correct_answer
    selected_option = question.options[answer_index]
    correct_option = question.options[question.correct_answer]
    
    user_info['answers'].append({
        'question_id': question.id,
        'selected': answer_index,
        'correct': question.correct_answer,
        'is_correct': is_correct
    })
    
    if is_correct:
        user_info['score'] += 1
        result_text = f"✅ Правильно! Вы выбрали: {selected_option}"
    else:
        result_text = (
            f"❌ Неправильно. Вы выбрали: {selected_option}\n"
            f"✅ Правильный ответ: {correct_option}"
        )
    
    if question.explanation:
        result_text += f"\n\n💡 {question.explanation}"
    
    await callback.message.edit_text(result_text)
    await callback.answer()
    
    user_info['current_question_index'] += 1
    
    await asyncio.sleep(1.5)
    
    if user_info['current_question_index'] < len(user_info['questions']):
        question_text = (
            f"❓ Вопрос {user_info['current_question_index'] + 1} из {len(user_info['questions'])}\n\n"
            f"{user_info['questions'][user_info['current_question_index']].text}"
        )
        keyboard = create_quiz_keyboard(user_info['questions'][user_info['current_question_index']])
        await callback.message.answer(question_text, reply_markup=keyboard)
    else:
        await finish_quiz(callback.message, user_info)


async def finish_quiz(message: types.Message, user_info: Dict):
    """Завершить квиз и показать результаты."""
    total_questions = len(user_info['questions'])
    score = user_info['score']
    percentage = (score / total_questions) * 100
    
    if percentage >= 90:
        grade = "🏆 Отлично! Вы настоящий знаток античной Греции!"
    elif percentage >= 70:
        grade = "⭐ Хорошо! Вы хорошо знаете историю Древней Греции!"
    elif percentage >= 50:
        grade = "👍 Неплохо! Есть что улучшить."
    else:
        grade = "📚 Есть над чем поработать. Изучайте историю дальше!"
    
    result_text = (
        f"🏛️ Квиз завершен!\n\n"
        f"📊 Ваши результаты:\n"
        f"Правильных ответов: {score} из {total_questions}\n"
        f"Процент правильных: {percentage:.1f}%\n\n"
        f"{grade}\n\n"
        f"Хотите попробовать еще раз? Используйте /quiz или кнопку '🏛️ Начать квиз'"
    )
    
    await message.answer(result_text, reply_markup=create_main_keyboard())
    
    user_info['current_question_index'] = 0


@dp.message(lambda message: message.text == "📊 Моя статистика")
async def show_statistics(message: types.Message):
    """Показать статистику пользователя."""
    user_id = message.from_user.id
    user_info = get_user_data(user_id)
    
    if not user_info['answers']:
        await message.answer(
            "📊 У вас пока нет результатов.\n"
            "Пройдите квиз, чтобы увидеть свою статистику!",
            reply_markup=create_main_keyboard()
        )
        return
    
    total_questions = len(user_info['answers'])
    correct_answers = sum(1 for ans in user_info['answers'] if ans['is_correct'])
    percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    stats_text = (
        f"📊 Ваша статистика:\n\n"
        f"Последний квиз:\n"
        f"• Всего вопросов: {total_questions}\n"
        f"• Правильных ответов: {correct_answers}\n"
        f"• Процент правильных: {percentage:.1f}%\n\n"
        f"Пройдите новый квиз, чтобы обновить статистику!"
    )
    
    await message.answer(stats_text, reply_markup=create_main_keyboard())


@dp.message()
async def handle_other_messages(message: types.Message):
    """Обработчик всех остальных сообщений."""
    await message.answer(
        "Используйте кнопки меню или команды:\n"
        "/start - начать работу\n"
        "/help - справка\n"
        "/quiz - начать квиз",
        reply_markup=create_main_keyboard()
    )


async def main():
    """Главная функция для запуска бота."""
    logger.info("Запуск бота...")
    
    if question_manager.get_question_count() < QUIZ_QUESTIONS_COUNT:
        logger.warning(
            f"В системе только {question_manager.get_question_count()} вопросов, "
            f"а требуется минимум {QUIZ_QUESTIONS_COUNT}"
        )
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем.")
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {e}", exc_info=True)

