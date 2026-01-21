"""Модуль детектора слова-активатора на Porcupine."""

import struct
import logging
from typing import Callable, Optional
from threading import Thread

try:
    import pvporcupine
    PORCUPINE_AVAILABLE = True
except ImportError:
    PORCUPINE_AVAILABLE = False

import pyaudio
from config.settings import PORCUPINE_CONFIG

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """Детектор слова-активатора с Porcupine."""

    def __init__(self, on_wake: Callable[[], None]):
        """
        Инициализация детектора.

        Args:
            on_wake: Коллбэк, который вызывается при срабатывании
        """
        if not PORCUPINE_AVAILABLE:
            logger.error("Порцупине не установлен. Установите: pip install pvporcupine")
            raise ImportError("pvporcupine is required")
        
        self.on_wake = on_wake
        self.is_listening = False
        self.porcupine = None
        self.stream = None
        self.pa = None
        
        try:
            self._init_porcupine()
            self._init_audio()
            logger.info("Детектор слова-активатора инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации: {e}")
            raise

    def _init_porcupine(self) -> None:
        """Инициализировать Porcupine с Jarvis ключевым словом."""
        access_key = PORCUPINE_CONFIG.get("access_key", "")
        if not access_key:
            logger.warning("Порцупин ассесс ключ не найден. Попробуем бесплатные ключевые слова.")
            # Если нет API ключа, используем встроенные
            self.porcupine = pvporcupine.create(keywords=["jarvis"])
        else:
            self.porcupine = pvporcupine.create(
                access_key=access_key,
                keywords=["jarvis"]
            )
        
        self.frame_length = self.porcupine.frame_length
        self.sample_rate = self.porcupine.sample_rate
        logger.info(f"Порцупин готов (слово: jarvis)")

    def _init_audio(self) -> None:
        """Настройка аудио стрима."""
        self.pa = pyaudio.PyAudio()
        try:
            self.stream = self.pa.open(
                rate=self.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.frame_length,
                input_device_index=None,
            )
            logger.info("Аудио стрим открыт")
        except Exception as e:
            logger.error(f"Ошибка открытия аудио стрима: {e}")
            raise

    def start(self) -> None:
        """Начать ослушивание в отдельном потоке."""
        self.is_listening = True
        thread = Thread(target=self._listen_loop, daemon=True)
        thread.start()
        logger.info("Начало ослушивание wake-word")

    def _listen_loop(self) -> None:
        """Цикл ослушивания."""
        while self.is_listening:
            try:
                pcm = self.stream.read(
                    self.frame_length,
                    exception_on_overflow=False
                )
                pcm = struct.unpack_from("h" * self.frame_length, pcm)
                result = self.porcupine.process(pcm)
                
                if result >= 0:
                    logger.info(f"🎱 JARVIS обнаружен!")
                    self.on_wake()
            except Exception as e:
                logger.error(f"Ошибка в цикле ослушивания: {e}")
                break

    def stop(self) -> None:
        """Остановить ослушивание."""
        self.is_listening = False
        logger.info("Ослушивание остановлено")

    def close(self) -> None:
        """Очистить ресурсы."""
        self.stop()
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.pa:
                self.pa.terminate()
            if self.porcupine:
                self.porcupine.delete()
            logger.info("Ресурсы очищены")
        except Exception as e:
            logger.error(f"Ошибка при очистке: {e}")

    def __del__(self) -> None:
        """Очистка при удалении объекта."""
        try:
            self.close()
        except:
            pass
