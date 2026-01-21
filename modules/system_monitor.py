"""Модуль мониторинга системы (температура, нагрузка, FPS)."""

import psutil
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from config.settings import SYSTEM_MONITOR_CONFIG

logger = logging.getLogger(__name__)


@dataclass
class SystemStats:
    """Класс для стокранения системных статистик."""
    cpu_percent: float
    cpu_freq: float
    cpu_temp: Optional[float] = None
    gpu_percent: Optional[float] = None
    gpu_temp: Optional[float] = None
    gpu_memory: Optional[float] = None
    ram_percent: float = 0
    disk_percent: float = 0


class SystemMonitor:
    """Монитор системных показателей."""

    def __init__(self):
        """Инициализация монитора."""
        logger.info("Монитор системы инициализирован")
        self._init_gpu_monitoring()

    def _init_gpu_monitoring(self) -> None:
        """Попытка инициализировать GPUtil для NVIDIA."""
        try:
            import gputil
            self.gputil = gputil
            logger.info("Поддержка GPU (NVIDIA) инициализирована")
        except ImportError:
            self.gputil = None
            logger.warning("Оптиональные библиотеки GPU не установлены")

    def get_cpu_stats(self) -> Dict[str, float]:
        """Получить статистику ПП."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_freq = psutil.cpu_freq().current if psutil.cpu_freq() else 0
            
            return {
                "cpu_percent": cpu_percent,
                "cpu_freq": cpu_freq,
            }
        except Exception as e:
            logger.error(f"Ошибка получения CPU статистики: {e}")
            return {"cpu_percent": 0, "cpu_freq": 0}

    def get_ram_stats(self) -> Dict[str, float]:
        """Получить статистику ОЗУ."""
        try:
            memory = psutil.virtual_memory()
            return {
                "ram_percent": memory.percent,
                "ram_used": memory.used / (1024**3),  # ГБ
                "ram_total": memory.total / (1024**3),  # ГБ
            }
        except Exception as e:
            logger.error(f"Ошибка получения RAM статистики: {e}")
            return {"ram_percent": 0, "ram_used": 0, "ram_total": 0}

    def get_disk_stats(self) -> Dict[str, float]:
        """Получить статистику диска C:."""
        try:
            disk = psutil.disk_usage("C:\\")
            return {
                "disk_percent": disk.percent,
                "disk_used": disk.used / (1024**3),  # ГБ
                "disk_total": disk.total / (1024**3),  # ГБ
            }
        except Exception as e:
            logger.error(f"Ошибка получения диск статистики: {e}")
            return {"disk_percent": 0, "disk_used": 0, "disk_total": 0}

    def get_gpu_stats(self) -> Dict[str, Optional[float]]:
        """Получить статистику GPU (NVIDIA)."""
        if not self.gputil:
            return {"gpu_percent": None, "gpu_temp": None, "gpu_memory": None}
        
        try:
            gpus = self.gputil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Первый GPU
                return {
                    "gpu_percent": gpu.load * 100,
                    "gpu_temp": gpu.temperature,
                    "gpu_memory": gpu.memoryUsed / gpu.memoryTotal * 100,
                }
        except Exception as e:
            logger.warning(f"Ошибка получения GPU статистики: {e}")
        
        return {"gpu_percent": None, "gpu_temp": None, "gpu_memory": None}

    def get_cpu_temp(self) -> Optional[float]:
        """Получить температуру ПП."""
        try:
            temps = psutil.sensors_temperatures()
            if "coretemp" in temps:
                return temps["coretemp"][0].current
            elif temps:
                # Получить первый доступный сенсор
                first_sensor = list(temps.values())[0]
                return first_sensor[0].current
        except Exception as e:
            logger.debug(f"Не удалось получить температуру: {e}")
        return None

    def get_all_stats(self) -> SystemStats:
        """Получить все системные статистики."""
        cpu_stats = self.get_cpu_stats()
        ram_stats = self.get_ram_stats()
        gpu_stats = self.get_gpu_stats()
        
        return SystemStats(
            cpu_percent=cpu_stats["cpu_percent"],
            cpu_freq=cpu_stats["cpu_freq"],
            cpu_temp=self.get_cpu_temp(),
            gpu_percent=gpu_stats["gpu_percent"],
            gpu_temp=gpu_stats["gpu_temp"],
            gpu_memory=gpu_stats["gpu_memory"],
            ram_percent=ram_stats["ram_percent"],
            disk_percent=0,  # Пока не используется
        )

    def format_stats(self, stats: SystemStats) -> str:
        """Оторматировать статистику в строку."""
        result = [
            f"ПП: {stats.cpu_percent:.1f}% ({stats.cpu_freq:.0f} МГц)",
            f"ОЗУ: {stats.ram_percent:.1f}%",
        ]
        
        if stats.cpu_temp:
            result.append(f"Темп. ПП: {stats.cpu_temp:.1f}°C")
        
        if stats.gpu_percent is not None:
            result.append(f"GPU: {stats.gpu_percent:.1f}% ({stats.gpu_memory:.1f}% памяти)")
            if stats.gpu_temp:
                result.append(f"Темп. GPU: {stats.gpu_temp:.1f}°C")
        
        return " | ".join(result)
