"""
Главная точка выполнения голосового помощника для Windows 11.
"""

import logging
import sys
import signal
import time
from pathlib import Path
from typing import Optional
from config.settings import LOGGING_CONFIG, DATA_DIR, LOGS_DIR
from modules.text_to_speech import TextToSpeech
from modules.speech_recognition import SpeechRecognizer
from modules.system_monitor import SystemMonitor
from modules.ocr_translator import OCRTranslator
from modules.commands import CommandManager

# Конфигурация логирования
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG["level"]),
    format=LOGGING_CONFIG["format"],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG["log_file"]),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


class VoiceAssistant:
    """Основной класс голосового помощника."""

    def __init__(self):
        """Инициализация помощника."""
        logger.info("=" * 60)
        logger.info("Голосовой помощник Windows 11 стартует...")
        logger.info("=" * 60)

        try:
            # Инициализация модулей
            logger.info("Модули инициализируются...")
            self.tts = TextToSpeech()
            self.recognizer = SpeechRecognizer(on_result=self._on_speech_recognized)
            self.system_monitor = SystemMonitor()
            self.ocr_translator = OCRTranslator()
            self.command_manager = CommandManager()
            
            self.is_running = False
            self.last_command = None
            logger.info("Модули успешно инициализированы")
        except Exception as e:
            logger.error(f"Ошибка инициализации: {e}")
            raise

    def start(self) -> None:
        """Начать работу помощника."""
        self.is_running = True
        logger.info("Помощник активирован")
        
        # Привет
        self.tts.speak("Помощник активирован. Готов выполнять команды.")
        
        # Начать послушивание в отдельном потоке
        self.recognizer.start_listening_thread()
        
        # Главный цикл
        try:
            while self.is_running:
                # Показывать системные статистики
                stats = self.system_monitor.get_all_stats()
                logger.info(self.system_monitor.format_stats(stats))
                time.sleep(5)  # Обновление каждые 5 секунд
        except KeyboardInterrupt:
            logger.info("\nПринят сигнал прерывания")
            self.stop()
        except Exception as e:
            logger.error(f"Ошибка в главном цикле: {e}")
            self.stop()

    def stop(self) -> None:
        """Остановить работу помощника."""
        self.is_running = False
        self.recognizer.stop_listening()
        self.tts.speak("Помощник деактивирован. Досвидания.")
        logger.info("\nПомощник деактивирован")
        logger.info("=" * 60)

    def _on_speech_recognized(self, text: str) -> None:
        """
        Коллбэк для обработки распознанного текста.

        Args:
            text: Отрисованный текст
        """
        if not text.strip():
            return
        
        logger.info(f"Читатель текст: {text}")
        self.process_command(text)

    def process_command(self, user_input: str) -> None:
        """
        Обработать команду.

        Args:
            user_input: Открытый текст
        """
        # Проспечить под текст
        logger.info(f"Обработка команды: {user_input}")
        
        # Найти похожую команду
        command = self.command_manager.find_similar_command(user_input)
        
        if command:
            self.tts.speak(f"Команда: {command.description}")
            self.command_manager.execute_command(command.name)
        else:
            # Показать системные статистики, если запрошены
            if "статистика" in user_input.lower():
                stats = self.system_monitor.get_all_stats()
                message = self.system_monitor.format_stats(stats)
                self.tts.speak(message)
                logger.info(f"Статистика: {message}")
            else:
                self.tts.speak("Не найдена похожая команда.")
                logger.warning(f"Команда не распознана: {user_input}")

    def display_available_commands(self) -> None:
        """Показать доступные команды."""
        logger.info("\nДоступные команды:")
        for cmd in self.command_manager.get_all_commands():
            logger.info(f"  - {cmd.trigger}: {cmd.description}")


def main() -> None:
    """Основная функция."""
    try:
        assistant = VoiceAssistant()
        assistant.display_available_commands()
        assistant.start()
    except Exception as e:
        logger.critical(f"Критикческая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
