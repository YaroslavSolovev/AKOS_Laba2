"""
ООП-реализация клиента для ping-pong взаимодействия.
Клиент создает запросы, ожидает ответы и обрабатывает ошибки.
"""

import time
from typing import Optional

from src.base_communicator import BaseCommunicator
from src.states import ClientState
from src.errors import (
    CommunicationError,
    FileAccessError,
    TimeoutError,
    InvalidResponseError
)


class PingPongClient(BaseCommunicator):
    """
    Клиент для ping-pong взаимодействия через файл-дескриптор.

    Состояния:
    1. CREATING_REQUEST - создание запроса
    2. WAITING_RESPONSE - ожидание ответа
    3. READING_RESPONSE - чтение ответа
    4. ERROR - обработка ошибки
    """

    def __init__(self, shared_file: str = "shared_communication.txt", timeout: int = 30):
        """
        Инициализация клиента.

        Args:
            shared_file: Путь к общему файлу для взаимодействия
            timeout: Таймаут ожидания ответа в секундах
        """
        super().__init__(shared_file)
        self.timeout = timeout
        self.state = ClientState.IDLE

    def _change_state(self, new_state: ClientState):
        """
        Изменение состояния клиента.

        Args:
            new_state: Новое состояние клиента
        """
        self.state = new_state

    def create_request(self, message: str = "ping") -> str:
        """
        Создание запроса.

        Args:
            message: Сообщение для отправки (по умолчанию "ping")

        Returns:
            Строка запроса
        """
        self._change_state(ClientState.CREATING_REQUEST)
        return message

    def send_request(self, request: str):
        """
        Отправка запроса в общий файл.

        Args:
            request: Строка запроса для отправки

        Raises:
            FileAccessError: При ошибке записи в файл
        """
        self._write_file(request)
        self._log(f"> {request}")

    def wait_for_response(self, sent_request: str) -> bool:
        """
        Ожидание ответа от сервера.

        Args:
            sent_request: Запрос который был отправлен (чтобы не читать его же)

        Returns:
            True если ответ появился, False если таймаут

        Raises:
            TimeoutError: При истечении таймаута
        """
        self._change_state(ClientState.WAITING_RESPONSE)

        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                content = self._read_file()
                # Ждем пока содержимое изменится (не равно нашему запросу)
                if content and content.strip() and content.strip() != sent_request.strip():
                    return True
            except FileAccessError:
                pass  # Файл может быть заблокирован сервером

            time.sleep(0.1)

        raise TimeoutError(f"Нет ответа ({self.timeout}s)")

    def read_response(self) -> str:
        """
        Чтение ответа от сервера.

        Returns:
            Содержимое ответа от сервера

        Raises:
            FileAccessError: При ошибке чтения файла
            InvalidResponseError: При неверном формате ответа
        """
        self._change_state(ClientState.READING_RESPONSE)

        response = self._read_file()
        if not response:
            raise InvalidResponseError("Пустой ответ")

        # Если это ошибка от сервера - выбрасываем исключение
        if response.startswith("ERROR:"):
            error_msg = response.replace("ERROR:", "").strip()
            raise InvalidResponseError(f"Сервер: {error_msg}")

        self._log(f"< {response}")
        return response

    def handle_error(self, error: Exception):
        """
        Обработка ошибки.

        Args:
            error: Исключение, которое произошло
        """
        self._change_state(ClientState.ERROR)
        self._log(f"Ошибка: {error}")

    def cleanup(self):
        """Очистка общего файла после завершения."""
        self._remove_file()

    def send_message(self, message: str) -> Optional[str]:
        """
        Отправка сообщения и получение ответа.

        Args:
            message: Сообщение для отправки

        Returns:
            Ответ от сервера или None при ошибке
        """
        try:
            # Создание и отправка запроса
            request = self.create_request(message)
            self.send_request(request)

            # Ожидание и чтение ответа (передаем запрос чтобы не читать его же)
            self.wait_for_response(request)
            response = self.read_response()

            self._change_state(ClientState.COMPLETED)
            return response

        except (CommunicationError, Exception) as e:
            self.handle_error(e)
            return None
