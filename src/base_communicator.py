# Базовый класс для клиента и сервера
# Общие методы для работы с файлом

import os
from datetime import datetime
from typing import Optional
from abc import ABC, abstractmethod

from src.errors import FileAccessError


class BaseCommunicator(ABC):
    # Родительский класс для клиента и сервера

    def __init__(self, shared_file: str):
        self.shared_file = shared_file
        self._role = self.__class__.__name__.replace("PingPong", "").upper()

    def _log(self, message: str):
        # Выводим сообщение с временем
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] [{self._role}] {message}")

    @abstractmethod
    def _change_state(self, new_state):
        # Этот метод должен быть реализован в дочерних классах
        pass

    def _read_file(self) -> Optional[str]:
        # Читаем из файла
        try:
            if not os.path.exists(self.shared_file):
                return None

            with open(self.shared_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                return content if content else None

        except IOError as e:
            raise FileAccessError(f"Failed to read from file: {e}")

    def _write_file(self, content: str):
        # Записываем в файл
        try:
            with open(self.shared_file, 'w', encoding='utf-8') as f:
                f.write(content + "\n")
                f.flush()
                os.fsync(f.fileno())  # Сразу сохраняем на диск

        except IOError as e:
            raise FileAccessError(f"Failed to write to file: {e}")

    def _clear_file(self):
        # Очищаем файл
        try:
            with open(self.shared_file, 'w', encoding='utf-8') as f:
                f.write("")
            self._log("Cleared shared file")

        except IOError as e:
            raise FileAccessError(f"Failed to clear file: {e}")

    def _remove_file(self):
        # Удаляем файл
        try:
            if os.path.exists(self.shared_file):
                os.remove(self.shared_file)
                self._log(f"Removed file: {self.shared_file}")

        except IOError as e:
            self._log(f"Warning: Failed to remove file: {e}")

    def _file_exists(self) -> bool:
        # Проверяем есть ли файл
        return os.path.exists(self.shared_file)
