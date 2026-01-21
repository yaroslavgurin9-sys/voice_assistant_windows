"""Модуль синтеза речи (TTS) с pyttsx3."""

import pyttsx3
import logging
from typing import Optional
from config.settings import TTS_CONFIG

logger = logging.getLogger(__name__)


class TextToSpeech:
    """Обертка для pyttsx3."""

    def __init__(self):
        """Инициализация TTS двига."""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", TTS_CONFIG["rate"])
            self.engine.setProperty("volume", TTS_CONFIG["volume"])
            
            # Установка русского голоса (если доступно)
            self._set_russian_voice()
            logger.info("Модуль TTS инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации TTS: {e}")
            raise

    def _set_russian_voice(self) -> None:
        """Настроика русского голоса."""
        voices = self.engine.getProperty("voices")
        
        # Поиск русского голоса
        for voice in voices:
            if "russian" in voice.name.lower() or "ru" in voice.languages[0].lower():
                self.engine.setProperty("voice", voice.id)
                logger.info(f"Установлен голос: {voice.name}")
                return
        
        # По умолчанию используем первый русского голос или дефолт
        if voices:
            self.engine.setProperty("voice", voices[0].id)
            logger.warning("Не найден русский голос, использую стандартный")

    def speak(self, text: str, wait: bool = True) -> None:
        """
        Проводить синтез речи.

        Args:
            text: Текст для провождения
            wait: Ожидать завершения
        """
        try:
            logger.debug(f"Говорю: {text}")
            self.engine.say(text)
            if wait:
                self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Ошибка по речи: {e}")

    def set_rate(self, rate: int) -> None:
        """Настройка скорости речи."""
        self.engine.setProperty("rate", rate)
        logger.info(f"Скорость иставлена на: {rate}")

    def set_volume(self, volume: float) -> None:
        """Настройка громкости."""
        self.engine.setProperty("volume", max(0, min(1, volume)))
        logger.info(f"Громкость установлена на: {volume}")

    def stop(self) -> None:
        """Остановить воспроизведение."""
        try:
            self.engine.stop()
            logger.info("Речь остановлена")
        except Exception as e:
            logger.error(f"Ошибка при остановке: {e}")

    def __del__(self) -> None:
        """Очистка ресурсов."""
        try:
            self.engine._cleanup()
        except:
            pass
