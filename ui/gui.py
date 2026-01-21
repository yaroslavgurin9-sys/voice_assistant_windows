"""Минималистичное окно голосового помощника (PyQt6)."""

import sys
import logging
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

logger = logging.getLogger(__name__)


class AssistantWindow(QMainWindow):
    """Минималистичное плавающее окно ассистента."""

    def __init__(self, assistant):
        super().__init__()
        self.assistant = assistant
        self.setWindowTitle("Jarvis")
        self.setWindowFlag(Qt.WindowType.Tool)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.resize(420, 180)
        self.move(50, 50)
        
        self._init_ui()
        self._init_timer()

    def _init_ui(self):
        central = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Тайтл
        title = QLabel("Jarvis")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")
        layout.addWidget(title)
        
        # Последняя реплика
        self.last_text_label = QLabel("Скажи: 'Jarvis'...")
        self.last_text_label.setFont(QFont("Segoe UI", 11))
        self.last_text_label.setStyleSheet("color: #d0d0d0;")
        self.last_text_label.setWordWrap(True)
        layout.addWidget(self.last_text_label)
        
        # Статус системы
        self.system_label = QLabel("CPU/GPU: --")
        self.system_label.setFont(QFont("Segoe UI", 9))
        self.system_label.setStyleSheet("color: #aaaaaa;")
        layout.addWidget(self.system_label)
        
        # Кнопки
        btn_row = QWidget()
        btn_layout = QVBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(4)
        
        self.btn_toggle = QPushButton("▶ Запустить")
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.clicked.connect(self._on_toggle)
        self.btn_toggle.setStyleSheet(self._button_style())
        btn_layout.addWidget(self.btn_toggle)
        
        self.btn_close = QPushButton("✕ Закрыть окно")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(self.close)
        self.btn_close.setStyleSheet(self._button_style(outline=True))
        btn_layout.addWidget(self.btn_close)
        
        btn_row.setLayout(btn_layout)
        layout.addWidget(btn_row)
        
        central.setLayout(layout)
        central.setStyleSheet("""
            background-color: rgba(20, 20, 25, 220);
            border-radius: 14px;
        """)
        self.setCentralWidget(central)

    def _init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_stats)
        self.timer.start(2000)

    def _update_stats(self):
        if not self.assistant:
            return
        stats = self.assistant.system_monitor.get_all_stats()
        self.system_label.setText(self.assistant.system_monitor.format_stats(stats))

    def _on_toggle(self):
        if not self.assistant.is_running:
            self.assistant.start_background()
            self.btn_toggle.setText("⏸ Остановить")
            self.last_text_label.setText("Скажи: 'Jarvis' и команду")
        else:
            self.assistant.stop()
            self.btn_toggle.setText("▶ Запустить")
            self.last_text_label.setText("Ассистент остановлен")

    def show_message(self, text: str):
        """Показать последнюю реплику/команду в окне."""
        self.last_text_label.setText(text)


def run_gui(assistant):
    """Запуск минималистичного окна ассистента."""
    app = QApplication.instance() or QApplication(sys.argv)
    window = AssistantWindow(assistant)
    assistant.gui_window = window
    window.show()
    return app.exec()
