"""
Конфигурационный файл для бота.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: Optional[str] = os.getenv("BOT_TOKEN")

QUIZ_QUESTIONS_COUNT: int = 10

ANCIENT_CHARACTERS = [
    "Сократ",
    "Платон",
    "Аристотель",
    "Гомер",
    "Александр Македонский",
    "Перикл",
    "Леонид",
    "Ахиллес",
    "Одиссей",
    "Геракл"
]

