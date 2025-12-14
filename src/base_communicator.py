"""
Базовый класс для клиента и сервера.
Содержит общую функциональность для работы с файловым дескриптором.
"""

import os
from typing import Optional
from abc import ABC, abstractmethod

from src.errors import FileAccessError


class BaseCommunicator(ABC):
    """
    Абстрактный базовый класс для клиента и сервера.
    Инкапсулирует общую логику работы с файлом и логированием.
    """

    def __init__(self, shared_file: str):
        """
        Инициализация базового коммуникатора.

        Args:
            shared_file: Путь к общему файлу для взаимодействия
        """
        self.shared_file = shared_file
        self._role = self.__class__.__name__.replace("PingPong", "").upper()

    def _log(self, message: str):
        """
        Логирование с ролью.

        Args:
            message: Сообщение для логирования
        """
        print(f"[{self._role}] {message}")

    @abstractmethod
    def _change_state(self, new_state):
        """
        Абстрактный метод для изменения состояния.
        Должен быть реализован в дочерних классах.

        Args:
            new_state: Новое состояние
        """
        pass

    def _read_file(self) -> Optional[str]:
        """
        Чтение содержимого из общего файла.

        Returns:
            Содержимое файла или None если файл не существует/пуст

        Raises:
            FileAccessError: При ошибке чтения файла
        """
        try:
            if not os.path.exists(self.shared_file):
                return None

            with open(self.shared_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                return content if content else None

        except IOError as e:
            raise FileAccessError(f"Failed to read from file: {e}")

    def _write_file(self, content: str):
        """
        Запись содержимого в общий файл с принудительной синхронизацией.

        Args:
            content: Содержимое для записи

        Raises:
            FileAccessError: При ошибке записи в файл
        """
        try:
            with open(self.shared_file, 'w', encoding='utf-8') as f:
                f.write(content + "\n")
                f.flush()
                os.fsync(f.fileno())  # Принудительная запись на диск

        except IOError as e:
            raise FileAccessError(f"Failed to write to file: {e}")

    def _clear_file(self):
        """
        Очистка содержимого общего файла.

        Raises:
            FileAccessError: При ошибке очистки файла
        """
        try:
            with open(self.shared_file, 'w', encoding='utf-8') as f:
                f.write("")
        except IOError as e:
            raise FileAccessError(f"Failed to clear file: {e}")

    def _remove_file(self):
        """
        Удаление общего файла.
        """
        try:
            if os.path.exists(self.shared_file):
                os.remove(self.shared_file)
        except IOError:
            pass  # Игнорируем ошибки удаления

    def _file_exists(self) -> bool:
        """
        Проверка существования общего файла.

        Returns:
            True если файл существует, False иначе
        """
        return os.path.exists(self.shared_file)
