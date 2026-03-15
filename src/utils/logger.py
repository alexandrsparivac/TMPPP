import threading
from typing import Optional
import logging

class LoggerSingleton:
    _instance: Optional["LoggerSingleton"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "LoggerSingleton":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self._logger = logging.getLogger("StudentLifeHelperBot")
        self._log_count = 0

    @classmethod
    def get_instance(cls) -> "LoggerSingleton":
        return cls()

    def info(self, message: str) -> None:
        self._log_count += 1
        self._logger.info(message)

    def error(self, message: str) -> None:
        self._log_count += 1
        self._logger.error(message)

    def warning(self, message: str) -> None:
        self._log_count += 1
        self._logger.warning(message)

    @property
    def log_count(self) -> int:
        return self._log_count
