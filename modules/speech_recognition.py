"""Модуль распознавания речи (STT) с Vosk."""

import pyaudio
import json
import logging
import threading
from typing import Callable, Optional
from vosk import Model, KaldiRecognizer
from config.settings import SPEECH_CONFIG, MODELS_DIR

logger = logging.getLogger(__name__)


class SpeechRecognizer:
    """Обертка для Vosk ASR."""

    def __init__(self, on_result: Optional[Callable[[str], None]] = None):
        """
        Инициализация распознавания речи.

        Args:
            on_result: Коллбэк для обработки результата
        """
        try:
            self.model = Model(SPEECH_CONFIG["model_path"])
            self.recognizer = KaldiRecognizer(
                self.model, SPEECH_CONFIG["sample_rate"]
            )
            self.on_result = on_result
            self.is_listening = False
            self.audio = pyaudio.PyAudio()
            logger.info("Модуль распознания речи инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации: {e}")
            raise

    def listen(self) -> None:
        """Начать постоянное послушивание."""
        self.is_listening = True
        logger.info("Начало послушивание")
        
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SPEECH_CONFIG["sample_rate"],
            input=True,
            frames_per_buffer=SPEECH_CONFIG["chunk_size"],
        )
        
        try:
            while self.is_listening:
                data = stream.read(SPEECH_CONFIG["chunk_size"])
                
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    if "result" in result and result["result"]:
                        text = " ".join([item["conf"] for item in result["result"]])
                        if self.on_result:
                            self.on_result(text)
                else:
                    partial = json.loads(self.recognizer.PartialResult())
                    if "partial" in partial:
                        logger.debug(f"Партиальный результат: {partial['partial']}")
        except Exception as e:
            logger.error(f"Ошибка в процессе слушания: {e}")
        finally:
            stream.stop_stream()
            stream.close()

    def start_listening_thread(self) -> threading.Thread:
        """Начать послушивание в отдельном потоке."""
        thread = threading.Thread(target=self.listen, daemon=True)
        thread.start()
        return thread

    def stop_listening(self) -> None:
        """Остановить послушивание."""
        self.is_listening = False
        logger.info("Послушивание остановлено")

    def __del__(self) -> None:
        """Очистка ресурсов."""
        try:
            self.stop_listening()
            self.audio.terminate()
        except:
            pass
