# 🎤 Голосовой помощник для Windows 11

**Полнофункциональный голосовой ассистент** с распознаванием речи, синтезом, OCR, переводом и мониторингом системы.

---

## 🌟 ТРЕБОВАНИЕ

### Зависимости

- **Python 3.10+**
- **Windows 11** (x86_64)
- **Git** (для клонирования проекта)

### Внешние зависимости

1. **Tesseract OCR**
   - Скачайте установщик: https://github.com/UB-Mannheim/tesseract/wiki
   - Установите по пути: `C:\Program Files\Tesseract-OCR\`

2. **Модели Vosk**
   - Скачайте русскую модель: https://alphacephei.com/vosk/models
   - Распакуйте в `models/vosk-model-ru-0.42/`

---

## 🚀 Установка

```bash
# Клонирование
git clone https://github.com/yaroslavgurin9-sys/voice_assistant_windows.git
cd voice_assistant_windows

# Виртуальное окружение
python -m venv venv
venv\Scripts\activate

# Зависимости
pip install -r requirements.txt

# Копирование конфига
.env.example -> .env

# Запуск
python main.py
```

---

## 🎤 Основные модули

- **speech_recognition.py** - Vosk ASR для распознавания речи
- **text_to_speech.py** - pyttsx3 синтез речи
- **system_monitor.py** - Мониторинг CPU/GPU/RAM/Temp
- **ocr_translator.py** - OCR + перевод
- **commands.py** - Управление командами

---

## 📚 Полезные ресурсы

- [Vosk Models](https://alphacephei.com/vosk/)
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
- [Argos Translate](https://www.argosopentech.com/)

---

**Создано с ❤️ для Windows 11**
