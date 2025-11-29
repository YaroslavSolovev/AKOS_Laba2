"""
ООП-реализация клиента для ping-pong взаимодействия.
Клиент создает запросы, ожидает ответы и обрабатывает ошибки.
"""

import time
from datetime import datetime
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
        self.request_id = 0
        self.max_retries = 3

    def _change_state(self, new_state: ClientState):
        """
        Изменение состояния клиента с логированием.

        Args:
            new_state: Новое состояние клиента
        """
        self._log(f"State transition: {self.state.value} -> {new_state.value}")
        self.state = new_state

    def create_request(self) -> str:
        """
        Шаг 1: Создание запроса ping.

        Returns:
            Строка запроса в формате "CLIENT_REQUEST|ping|request_id|timestamp"
        """
        self._change_state(ClientState.CREATING_REQUEST)
        self.request_id += 1
        timestamp = datetime.now().isoformat()
        request = f"CLIENT_REQUEST|ping|{self.request_id}|{timestamp}"
        self._log(f"Created request: {request}")
        return request

    def send_request(self, request: str):
        """
        Отправка запроса в общий файл.

        Args:
            request: Строка запроса для отправки

        Raises:
            FileAccessError: При ошибке записи в файл
        """
        self._write_file(request)
        self._log(f"Request sent to file: {self.shared_file}")

    def wait_for_response(self) -> bool:
        """
        Шаг 2: Ожидание ответа от сервера.

        Returns:
            True если ответ появился, False если таймаут

        Raises:
            TimeoutError: При истечении таймаута
        """
        self._change_state(ClientState.WAITING_RESPONSE)
        self._log(f"Waiting for response (timeout: {self.timeout}s)...")

        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                content = self._read_file()
                if content and content.startswith("SERVER_RESPONSE"):
                    self._log("Response detected in file")
                    return True
            except FileAccessError:
                pass  # Файл может быть заблокирован сервером

            time.sleep(0.1)  # Короткая пауза для снижения нагрузки на CPU

        raise TimeoutError(f"No response received within {self.timeout} seconds")

    def read_response(self) -> str:
        """
        Шаг 3: Чтение ответа от сервера.

        Returns:
            Содержимое ответа от сервера

        Raises:
            FileAccessError: При ошибке чтения файла
            InvalidResponseError: При неверном формате ответа
        """
        self._change_state(ClientState.READING_RESPONSE)

        response = self._read_file()
        if not response:
            raise InvalidResponseError("Empty response from server")

        self._log(f"Read response: {response}")

        # Валидация формата ответа
        if not response.startswith("SERVER_RESPONSE"):
            raise InvalidResponseError(f"Invalid response format: {response}")

        parts = response.split("|")
        if len(parts) < 4 or parts[1] != "pong":
            raise InvalidResponseError(f"Expected 'pong' response, got: {response}")

        return response

    def handle_error(self, error: Exception, retry_count: int = 0) -> bool:
        """
        Шаг 4: Обработка ошибки.

        Args:
            error: Исключение, которое произошло
            retry_count: Текущий счетчик попыток

        Returns:
            True если нужно повторить попытку, False если нет
        """
        self._change_state(ClientState.ERROR)
        self._log(f"ERROR: {type(error).__name__}: {error}")

        if retry_count < self.max_retries:
            self._log(f"Retry {retry_count + 1}/{self.max_retries}")
            time.sleep(1)  # Пауза перед повторной попыткой
            return True
        else:
            self._log("Max retries reached. Giving up.")
            return False

    def cleanup(self):
        """Очистка общего файла после завершения."""
        self._remove_file()

    def send_ping(self) -> Optional[str]:
        """
        Основной метод для отправки ping и получения pong.
        Реализует полный цикл согласно диаграмме состояний.

        Returns:
            Ответ от сервера или None при ошибке
        """
        retry_count = 0

        while retry_count <= self.max_retries:
            try:
                # 1. Создание запроса
                request = self.create_request()

                # Отправка запроса
                self.send_request(request)

                # 2. Ожидание ответа
                self.wait_for_response()

                # 3. Чтение ответа
                response = self.read_response()

                # Успех
                self._change_state(ClientState.COMPLETED)
                self._log("Ping-pong cycle completed successfully")
                return response

            except (CommunicationError, Exception) as e:
                # 4. Обработка ошибки
                should_retry = self.handle_error(e, retry_count)
                if not should_retry:
                    return None
                retry_count += 1

        return None
