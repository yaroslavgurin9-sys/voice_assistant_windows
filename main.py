"""
Главная точка выполнения голосового помощника для Windows 11.
"""

import logging
import sys
import time
from typing import Optional

from config.settings import LOGGING_CONFIG
from modules.text_to_speech import TextToSpeech
from modules.speech_recognition import SpeechRecognizer
from modules.system_monitor import SystemMonitor
from modules.ocr_translator import OCRTranslator
from modules.commands import CommandManager
from modules.activation import WakeWordDetector

# GUI (минималистичное окно Jarvis)
try:
    from ui.gui import run_gui
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

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
    """Основной класс голосового помощника (Jarvis)."""

    def __init__(self):
        logger.info("=" * 60)
        logger.info("Jarvis для Windows 11 стартует...")
        logger.info("=" * 60)

        self.is_running: bool = False
        self.awaiting_command: bool = False

        # GUI окно (инициализируется позже)
        self.gui_window = None

        # Модули
        logger.info("Инициализация модулей...")
        self.tts = TextToSpeech()
        self.system_monitor = SystemMonitor()
        self.ocr_translator = OCRTranslator()
        self.command_manager = CommandManager()

        # STT и wake-word
        self.recognizer = SpeechRecognizer(on_result=self._on_speech_recognized)
        self.wake_detector: Optional[WakeWordDetector] = WakeWordDetector(
            on_wake=self._on_wake_word
        )

        logger.info("Все модули инициализированы")

    # ------------------------ ПУСК/СТОП ------------------------

    def start_background(self) -> None:
        """Запустить ассистента в фоне (wake-word + ожидание команд)."""
        if self.is_running:
            return
        self.is_running = True
        self.awaiting_command = False

        self.tts.speak("Jarvis на связи. Скажи 'Jarvis' и команду.")
        logger.info("Jarvis активирован")

        # Запуск детектора слова-активатора
        if self.wake_detector:
            self.wake_detector.start()

    def start_console_loop(self) -> None:
        """Простой консольный цикл (без GUI)."""
        self.start_background()
        try:
            while self.is_running:
                stats = self.system_monitor.get_all_stats()
                logger.info(self.system_monitor.format_stats(stats))
                time.sleep(5)
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            logger.error(f"Ошибка в главном цикле: {e}")
            self.stop()

    def stop(self) -> None:
        """Остановить Jarvis."""
        if not self.is_running:
            return
        self.is_running = False
        self.awaiting_command = False

        try:
            self.recognizer.stop_listening()
        except Exception:
            pass

        try:
            if self.wake_detector:
                self.wake_detector.stop()
        except Exception:
            pass

        self.tts.speak("Jarvis отключается. До встречи.")
        logger.info("Jarvis деактивирован")

    # ------------------------ WAVE-WORD ------------------------

    def _on_wake_word(self) -> None:
        """Коллбэк при срабатывании Jarvis ключевого слова."""
        if not self.is_running:
            return
        if self.awaiting_command:
            return

        self.awaiting_command = True
        message = "Слушаю. Говори команду."
        logger.info("Wake-word 'Jarvis' обнаружен")
        logger.info(message)
        self.tts.speak(message)

        if self.gui_window:
            self.gui_window.show_message("Jarvis: слушаю команду...")

        # Запускаем короткий сеанс распознавания
        self.recognizer.start_listening_thread()

    # ------------------------ ОБРАБОТКА РЕЧИ ------------------------

    def _on_speech_recognized(self, text: str) -> None:
        """Коллбэк Vosk с распознанным текстом."""
        text = text.strip()
        if not text:
            self.awaiting_command = False
            self.recognizer.stop_listening()
            return

        logger.info(f"Распознано: {text}")

        if self.gui_window:
            self.gui_window.show_message(f"Вы: {text}")

        # Останавливаем текущий слушающий цикл
        self.recognizer.stop_listening()
        self.awaiting_command = False

        # Обработка команды
        self.process_command(text)

    # ------------------------ ЛОГИКА КОМАНД ------------------------

    def process_command(self, user_input: str) -> None:
        logger.info(f"Обработка команды: {user_input}")

        # Попытка найти зарегистрированную команду
        cmd = self.command_manager.find_similar_command(user_input)
        if cmd:
            self.tts.speak(f"Выполняю: {cmd.description}")
            self.command_manager.execute_command(cmd.name)
            return

        # Специальные команды
        lower = user_input.lower()

        if "статистика" in lower:
            stats = self.system_monitor.get_all_stats()
            message = self.system_monitor.format_stats(stats)
            self.tts.speak(message)
            logger.info(message)
            if self.gui_window:
                self.gui_window.show_message(message)
            return

        if "что на экране" in lower or "прочитай экран" in lower:
            result = self.ocr_translator.extract_and_translate_from_screen()
            if result["original"]:
                self.tts.speak(result["translated"] or result["original"])
                if self.gui_window:
                    self.gui_window.show_message(result["original"])
            else:
                self.tts.speak("Не удалось прочитать текст с экрана.")
            return

        # По умолчанию
        self.tts.speak("Команда не распознана.")
        logger.warning(f"Неизвестная команда: {user_input}")


def main() -> None:
    assistant = VoiceAssistant()

    if GUI_AVAILABLE:
        # Запускаем GUI (минималистичное окно Jarvis)
        from ui.gui import run_gui
        assistant.start_background()
        run_gui(assistant)
    else:
        assistant.start_console_loop()


if __name__ == "__main__":
    main()
