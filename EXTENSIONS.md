# 🥒 Расширение функционала

## 1. Интеграция с OpenAI ChatGPT

### Установка

```bash
pip install openai
```

### Реализация

**`modules/gpt_integration.py`:**

```python
import openai
import logging
from config.settings import API_KEYS

logger = logging.getLogger(__name__)

class GPTIntegration:
    def __init__(self):
        openai.api_key = API_KEYS["openai"]
        if not openai.api_key:
            logger.warning("ОпенАИ API ключ не установлен")
    
    def ask_gpt(self, question: str) -> str:
        """Послать вопрос чат ГПТ."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": question}],
                max_tokens=200,
                temperature=0.7
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Ошибка ПОБ: {e}")
            return ""
```

### Добавление в main.py

```python
from modules.gpt_integration import GPTIntegration

# В __init__ VoiceAssistant
self.gpt = GPTIntegration()

# В process_command
if "скажи" in user_input.lower():
    question = user_input.replace("скажи", "").strip()
    answer = self.gpt.ask_gpt(question)
    self.tts.speak(answer)
```

---

## 2. Динамическое обучение команд

### Описание

Мониторинг действий пользователя и сохранение команд в БД.

### Реализация

**`modules/learning.py`:**

```python
import subprocess
import json
import logging
from typing import Dict, List
from datetime import datetime
from pathlib import Path
from config.settings import DATA_DIR

logger = logging.getLogger(__name__)

class CommandLearning:
    def __init__(self):
        self.learned_commands_file = DATA_DIR / "learned_commands.json"
        self.load_learned_commands()
    
    def load_learned_commands(self):
        """Загрузить изученные команды."""
        if self.learned_commands_file.exists():
            with open(self.learned_commands_file, 'r', encoding='utf-8') as f:
                self.learned = json.load(f)
        else:
            self.learned = {}
    
    def save_learned_commands(self):
        """Сохранить изученные команды."""
        with open(self.learned_commands_file, 'w', encoding='utf-8') as f:
            json.dump(self.learned, f, ensure_ascii=False, indent=2)
    
    def monitor_processes(self, duration: int = 10) -> List[Dict]:
        """Мониторить новые процессы в течение N секунд."""
        import time
        import psutil
        
        initial_pids = set(p.pid for p in psutil.process_iter())
        logger.info(f"Мониторинг новых процессов в течение {duration}c...")
        
        time.sleep(duration)
        
        new_processes = []
        current_pids = set(p.pid for p in psutil.process_iter())
        
        for pid in current_pids - initial_pids:
            try:
                proc = psutil.Process(pid)
                new_processes.append({
                    "name": proc.name(),
                    "exe": proc.exe(),
                    "cmdline": " ".join(proc.cmdline())
                })
            except:
                pass
        
        return new_processes
    
    def teach_command(self, phrase: str, action_type: str, action_data: Dict):
        """Научить помощнику новые команды."""
        self.learned[phrase] = {
            "action_type": action_type,  # app, url, command
            "action_data": action_data,
            "created_at": datetime.now().isoformat()
        }
        self.save_learned_commands()
        logger.info(f"Команда '{phrase}' изучена")
```

---

## 3. GUI интерфейс на PyQt6

### Основные компоненты

**`ui/gui.py`:**

```python
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)

class AssistantGUI(QMainWindow):
    def __init__(self, assistant):
        super().__init__()
        self.assistant = assistant
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("🎤 Голосовой помощник")
        self.setGeometry(100, 100, 600, 400)
        
        # Основныод виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Название
        title = QLabel("Голосовой ассистент")
        title.setFont(QFont("Arial", 18))
        layout.addWidget(title)
        
        # статус
        self.status_label = QLabel("Данные на лоди...")
        layout.addWidget(self.status_label)
        
        # Кнопка старт
        start_btn = QPushButton("Запустить")
        start_btn.clicked.connect(self.start_assistant)
        layout.addWidget(start_btn)
        
        # Кнопка стоп
        stop_btn = QPushButton("Остановить")
        stop_btn.clicked.connect(self.stop_assistant)
        layout.addWidget(stop_btn)
        
        central_widget.setLayout(layout)
        
        # Обновление осиатаниѕ
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)  # Обновлять каждую секунду
    
    def start_assistant(self):
        self.assistant.start()
        self.status_label.setText("Помощник активн")
    
    def stop_assistant(self):
        self.assistant.stop()
        self.status_label.setText("Помощник деактивн")
    
    def update_status(self):
        stats = self.assistant.system_monitor.get_all_stats()
        status_text = self.assistant.system_monitor.format_stats(stats)
        self.status_label.setText(status_text)
```

---

## 4. История команд в БД

**`database/models.py`:**

```python
from peewee import *
from config.settings import DATABASE_CONFIG
from datetime import datetime

db = SqliteDatabase(DATABASE_CONFIG["path"])

class Command(Model):
    phrase = CharField()
    action = CharField()
    created_at = DateTimeField(default=datetime.now)
    times_used = IntegerField(default=0)
    
    class Meta:
        database = db
        table_name = 'commands'

class SystemLog(Model):
    event = CharField()
    timestamp = DateTimeField(default=datetime.now)
    details = TextField()
    
    class Meta:
        database = db
        table_name = 'system_logs'

# На старте
if __name__ == "__main__":
    db.create_tables([Command, SystemLog])
```

---

## 5. Отключение в коваринц дополнительных рисбриси

### Как добавить свою рисбрина

1. Напишите новый модуль `modules/your_feature.py`
2. Импортируйте в `main.py`
3. Обновите в `process_command`

### Пример: Управление быстрым фурчком

```python
import keyboard
import logging

logger = logging.getLogger(__name__)

class HotkeysManager:
    def __init__(self, assistant):
        self.assistant = assistant
        keyboard.add_hotkey('alt+ctrl+v', self.toggle_assistant)
    
    def toggle_assistant(self):
        if self.assistant.is_running:
            self.assistant.stop()
        else:
            self.assistant.start()
        logger.info("Напоминание тогда")
```

---

## Рекомендуемые дополнения

- 🥞 **Voice Modulation** - днакфоний голос
- 🤖 **AI Context** - сохранение контекста разговора
- 📮 **Alexa/Google Assistant Integration** - синтеграция других ассистентов
- 🔕 **Custom Wake Words** - свои активирующие фразы
- 📚 **Knowledge Base** - локальная база данных для выррчки
