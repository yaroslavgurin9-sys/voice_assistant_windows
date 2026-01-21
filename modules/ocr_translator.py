"""Модуль OCR и перевода текста."""

import logging
import pytesseract
from PIL import ImageGrab
from typing import Optional
from config.settings import OCR_CONFIG, TRANSLATION_CONFIG

logger = logging.getLogger(__name__)

# Проверить и установить путь к Tesseract
try:
    pytesseract.pytesseract.pytesseract_cmd = OCR_CONFIG["tesseract_path"]
except Exception as e:
    logger.warning(f"Не удалось установить путь Tesseract: {e}")


class OCRTranslator:
    """Модуль для OCR и перевода."""

    def __init__(self):
        """Инициализация."""
        try:
            import argostranslate.package
            import argostranslate.translate
            
            self.argos_available = True
            self.translator_module = argostranslate.translate
            logger.info("Модуль OCR и перевода инициализирован")
        except ImportError:
            self.argos_available = False
            logger.warning("Оптиональные модули перевода не установлены")

    def extract_text_from_screen(self, region: Optional[tuple] = None) -> str:
        """
        Экстракция текста на экране.

        Args:
            region: Координаты (left, top, right, bottom) для обыска региона

        Returns:
            Очищенный текст
        """
        try:
            # Получить скриншот
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()
            
            # Отрисовать текст с OCR
            text = pytesseract.image_to_string(
                screenshot,
                lang=OCR_CONFIG["language"]
            )
            
            logger.debug(f"Одвою текст: {text[:100]}...")
            return text.strip()
        except Exception as e:
            logger.error(f"Ошибка орисования OCR: {e}")
            return ""

    def translate_text(self, text: str, source_lang: Optional[str] = None, target_lang: Optional[str] = None) -> str:
        """
        Перевести текст.

        Args:
            text: Текст для перевода
            source_lang: Исходный язык
            target_lang: Целевой язык

        Returns:
            Переведенный текст
        """
        if not self.argos_available:
            logger.warning("Переводчик Argos не доступен")
            return text
        
        source_lang = source_lang or TRANSLATION_CONFIG["source_lang"]
        target_lang = target_lang or TRANSLATION_CONFIG["target_lang"]
        
        try:
            translated = self.translator_module.translate(text, source_lang, target_lang)
            logger.debug(f"Переведено: {translated}")
            return translated
        except Exception as e:
            logger.error(f"Ошибка перевода: {e}")
            return text

    def extract_and_translate_from_screen(
        self,
        region: Optional[tuple] = None,
        translate: bool = True
    ) -> dict:
        """
        Единая операция: OCR + перевод.

        Returns:
            dict с "исходным текстом" и "переведенным текстом"
        """
        original_text = self.extract_text_from_screen(region)
        translated_text = self.translate_text(original_text) if translate else original_text
        
        return {
            "original": original_text,
            "translated": translated_text,
        }
