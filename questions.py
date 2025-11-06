"""
Модульная система вопросов для квиза об античной Греции.
Легко добавлять новые вопросы, просто создавая объекты Question.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Question:
    """Класс для представления вопроса квиза."""
    id: int
    text: str
    options: List[str]
    correct_answer: int
    explanation: Optional[str] = None


class QuestionManager:
    """Менеджер для управления вопросами квиза."""
    
    def __init__(self):
        self.questions: List[Question] = []
        self._load_questions()
    
    def _load_questions(self):
        """Загружает все вопросы в систему."""
        self.questions = [
            Question(
                id=1,
                text="Кто был главным богом в древнегреческой мифологии?",
                options=["Посейдон", "Зевс", "Аид", "Аполлон"],
                correct_answer=1,
                explanation="Зевс был верховным богом Олимпа, богом неба, грома и молний."
            ),
            Question(
                id=2,
                text="Какой город был столицей Древней Греции?",
                options=["Спарта", "Афины", "Фивы", "Коринф"],
                correct_answer=1,
                explanation="Афины были не только столицей, но и центром культуры и демократии."
            ),
            Question(
                id=3,
                text="Кто написал 'Илиаду' и 'Одиссею'?",
                options=["Софокл", "Гомер", "Эсхил", "Еврипид"],
                correct_answer=1,
                explanation="Гомер - легендарный древнегреческий поэт, автор эпических поэм."
            ),
            Question(
                id=4,
                text="Как назывался храм, посвященный богине Афине в Афинах?",
                options=["Парфенон", "Эрехтейон", "Храм Зевса", "Храм Посейдона"],
                correct_answer=0,
                explanation="Парфенон - знаменитый храм на Акрополе, посвященный Афине Парфенос."
            ),
            Question(
                id=5,
                text="Кто был учителем Александра Македонского?",
                options=["Сократ", "Платон", "Аристотель", "Пифагор"],
                correct_answer=2,
                explanation="Аристотель был наставником молодого Александра Македонского."
            ),
            Question(
                id=6,
                text="Как назывался совет старейшин в Спарте?",
                options=["Ареопаг", "Буле", "Герусия", "Экклесия"],
                correct_answer=2,
                explanation="Герусия - совет из 28 старейшин в Спарте, обладавший значительной властью."
            ),
            Question(
                id=7,
                text="Кто победил Медузу Горгону?",
                options=["Геракл", "Персей", "Тесей", "Одиссей"],
                correct_answer=1,
                explanation="Персей отрубил голову Медузе, используя отражение в щите."
            ),
            Question(
                id=8,
                text="Как называлась битва, в которой греки победили персов в 490 году до н.э.?",
                options=["Битва при Фермопилах", "Битва при Марафоне", "Битва при Саламине", "Битва при Платеях"],
                correct_answer=1,
                explanation="Битва при Марафоне - знаменитая победа афинян над персами."
            ),
            Question(
                id=9,
                text="Какой философ был приговорен к смерти через принятие яда цикуты?",
                options=["Платон", "Сократ", "Аристотель", "Диоген"],
                correct_answer=1,
                explanation="Сократ был приговорен к смерти за 'развращение молодежи' и 'непочитание богов'."
            ),
            Question(
                id=10,
                text="Как назывался главный театр в Афинах?",
                options=["Театр Диониса", "Одеон Герода Аттика", "Театр Эпидавра", "Театр в Дельфах"],
                correct_answer=0,
                explanation="Театр Диониса - древнейший театр в Афинах, где проходили драматические представления."
            ),
            Question(
                id=11,
                text="Кто был богом моря в древнегреческой мифологии?",
                options=["Тритон", "Посейдон", "Океан", "Нерей"],
                correct_answer=1,
                explanation="Посейдон - брат Зевса и Аида, владыка морей и океанов."
            ),
            Question(
                id=12,
                text="Как называлась форма правления, изобретенная в Афинах?",
                options=["Тирания", "Олигархия", "Демократия", "Монархия"],
                correct_answer=2,
                explanation="Демократия (власть народа) была создана в Афинах в VI веке до н.э."
            ),
        ]
    
    def get_question(self, question_id: int) -> Optional[Question]:
        """Получить вопрос по ID."""
        for q in self.questions:
            if q.id == question_id:
                return q
        return None
    
    def get_all_questions(self) -> List[Question]:
        """Получить все вопросы."""
        return self.questions
    
    def get_question_count(self) -> int:
        """Получить количество вопросов."""
        return len(self.questions)
    
    def add_question(self, question: Question):
        """Добавить новый вопрос в систему."""
        self.questions.append(question)
    
    def get_random_questions(self, count: int) -> List[Question]:
        """Получить случайный набор вопросов."""
        import random
        if count > len(self.questions):
            count = len(self.questions)
        return random.sample(self.questions, count)

