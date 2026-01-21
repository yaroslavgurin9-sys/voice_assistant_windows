"""Глобальные параметры приложения."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Пути
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"

# Создание директорий если их нет
for directory in [DATA_DIR, LOGS_DIR, MODELS_DIR]:
    directory.mkdir(exist_ok=True)

# Параметры речи
SPEECH_CONFIG = {
    "sample_rate": 16000,
    "chunk_size": 2048,
    "language": "ru_RU",
    "model_path": str(MODELS_DIR / "vosk-model-ru-0.42"),
}

# Параметры Porcupine (Wake-word)
PORCUPINE_CONFIG = {
    "keyword": "привет помощник",  # Ключевая фраза
    "access_key": os.getenv("PORCUPINE_ACCESS_KEY", ""),  # Получить с picovoice.ai
    "sensitivities": 0.5,
}

# Параметры TTS
TTS_CONFIG = {
    "rate": 150,  # Скорость речи (слова в минуту)
    "volume": 0.9,  # Громкость (0-1)
    "language": "ru",
}

# Параметры OCR
OCR_CONFIG = {
    "tesseract_path": r"C:\Program Files\Tesseract-OCR\tesseract.exe",  # Путь к Tesseract
    "language": "rus",
}

# Параметры перевода
TRANSLATION_CONFIG = {
    "source_lang": "ru",
    "target_lang": "en",
    "use_online": False,  # Использовать онлайн-переводчик (DeepL, Google)
}

# Параметры БД
DATABASE_CONFIG = {
    "path": str(DATA_DIR / "assistant.db"),
    "timeout": 5.0,
}

# Параметры системного мониторинга
SYSTEM_MONITOR_CONFIG = {
    "update_interval": 1.0,  # Интервал обновления (сек)
    "max_temp_warning": 85,  # Предупреждение при температуре (°C)
    "monitor_gpu": True,
}

# API ключи (опционально)
API_KEYS = {
    "openai": os.getenv("OPENAI_API_KEY", ""),
    "google_translate": os.getenv("GOOGLE_TRANSLATE_API_KEY", ""),
    "deepl": os.getenv("DEEPL_API_KEY", ""),
}

# Параметры логирования
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    "log_file": str(LOGS_DIR / "assistant.log"),
}

# Параметры GUI
GUI_CONFIG = {
    "window_width": 1200,
    "window_height": 800,
    "theme": "dark",  # dark, light
    "transparency": 0.95,
}
