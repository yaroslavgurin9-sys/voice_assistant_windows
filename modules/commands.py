"""Модуль управления командами."""

import subprocess
import logging
from typing import Callable, Dict, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Command:
    """Класс для репрезентации команды."""
    name: str
    trigger: str  # Фраза-триггер
    action: Callable  # Выполняемое действие
    description: str = ""
    confidence_threshold: float = 0.7


class CommandManager:
    """Менеджер для управления командами."""

    def __init__(self):
        """Инициализация."""
        self.commands: Dict[str, Command] = {}
        self._register_builtin_commands()
        logger.info("Менеджер команд инициализирован")

    def _register_builtin_commands(self) -> None:
        """Регистрация встроенных команд."""
        # Управление системой
        self.register_command(Command(
            name="open_browser",
            trigger="открой браузер",
            action=self._open_browser,
            description="Открыть браузер"
        ))
        
        self.register_command(Command(
            name="open_notepad",
            trigger="открой блокнот",
            action=self._open_notepad,
            description="Открыть блокнот"
        ))
        
        self.register_command(Command(
            name="lock_screen",
            trigger="u043eт экран",
            action=self._lock_screen,
            description="u0417аблокировать экран"
        ))

    def register_command(self, command: Command) -> None:
        """
        Регистрировать новую команду.

        Args:
            command: Объект Команды
        """
        self.commands[command.name] = command
        logger.info(f"Команда '{command.name}' регистрирована")

    def execute_command(self, command_name: str, *args, **kwargs) -> bool:
        """
        Эксекютировать команду.

        Args:
            command_name: Название команды

        Returns:
            True если успешно, False если нет
        """
        if command_name not in self.commands:
            logger.warning(f"Команда '{command_name}' не найдена")
            return False
        
        try:
            command = self.commands[command_name]
            command.action(*args, **kwargs)
            logger.info(f"Команда '{command_name}' выполнена")
            return True
        except Exception as e:
            logger.error(f"Ошибка при выполнении команды '{command_name}': {e}")
            return False

    def get_all_commands(self) -> List[Command]:
        """Получить все доступные команды."""
        return list(self.commands.values())

    # Встроенные действия
    @staticmethod
    def _open_browser(*args, **kwargs) -> None:
        """Открыть браузер."""
        subprocess.Popen("start chrome", shell=True)

    @staticmethod
    def _open_notepad(*args, **kwargs) -> None:
        """Открыть блокнот."""
        subprocess.Popen("notepad.exe")

    @staticmethod
    def _lock_screen(*args, **kwargs) -> None:
        """Заблокировать экран."""
        subprocess.Popen("rundll32.exe user32.dll,LockWorkStation")

    def find_similar_command(self, user_input: str) -> Optional[Command]:
        """
        Поиск похожей команды как встроцзаю или
        расстояние (симплый каср для искрама).
        """
        best_match = None
        best_score = 0
        
        for command in self.commands.values():
            # Постойсянные встроится
            if user_input.lower() in command.trigger.lower():
                score = len(user_input) / len(command.trigger)
                if score > best_score:
                    best_score = score
                    best_match = command
        
        if best_score >= 0.5:
            return best_match
        
        return None
