"""Модуль обработки естественного языка и распознавания намерения."""

import logging
from typing import Optional, Dict, List, Tuple
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class NLPProcessor:
    """Процессор для распознавания намерений и обработки текста."""

    def __init__(self):
        """Инициализация NLP процессора."""
        self.intent_keywords = {
            "open": ["открой", "запусти", "старт"],
            "close": ["закрой", "выключи"],
            "info": ["найди", "покажи", "скажи"],
            "search": ["поиск", "google", "яндекс"],
            "control": ["статистика", "контроль", "установка"],
        }
        logger.info("НЛП процессор инициализирован")

    def extract_intent(self, text: str) -> Tuple[Optional[str], float]:
        """
        Истрает намерение из текста.

        Returns:
            Кортеж (намерение, уверенность)
        """
        text_lower = text.lower()
        best_intent = None
        best_score = 0

        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    score = 1.0
                    if best_score < score:
                        best_score = score
                        best_intent = intent

        return best_intent, best_score

    def similarity_score(self, text1: str, text2: str) -> float:
        """
        Оценить схождение двух текстов.

        Returns:
            Оценка (0-1)
        """
        matcher = SequenceMatcher(None, text1.lower(), text2.lower())
        return matcher.ratio()

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Попытка истраеть сущности (топики, значения).

        Returns:
            словарь с истраенными сущностями
        """
        entities = {"verbs": [], "nouns": [], "adjectives": []}
        words = text.split()
        
        # Простая таггеризация (без spaCy/NLTK)
        # Можно оставить как есть для будущего расширения
        for word in words:
            entities["nouns"].append(word)
        
        return entities

    def preprocess_text(self, text: str) -> str:
        """
        Предварительная обработка текста.
        """
        # Озаглавливание
        text = text.lower().strip()
        # Оставляем только буквы, цифры, пробелы
        text = "".join(c if c.isalnum() or c.isspace() else " " for c in text)
        # Одного пробела между словами
        text = " ".join(text.split())
        return text
