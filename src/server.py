"""
ООП-реализация сервера для ping-pong взаимодействия.
Сервер ожидает запросы, обрабатывает их и отправляет ответы.
"""

import time
from datetime import datetime
from typing import Optional

from src.base_communicator import BaseCommunicator
from src.states import ServerState
from src.errors import (
    CommunicationError,
    FileAccessError,
    InvalidRequestError
)


class PingPongServer(BaseCommunicator):
    """
    Сервер для ping-pong взаимодействия через файл-дескриптор.

    Состояния:
    1. WAITING_REQUEST - ожидание запроса
    1.1. PROCESSING_REQUEST - обработка запроса
    1.2. ERROR - обработка ошибки
    2. SENDING_RESPONSE - отправка ответа
    """

    def __init__(self, shared_file: str = "shared_communication.txt", poll_interval: float = 0.1):
        """
        Инициализация сервера.

        Args:
            shared_file: Путь к общему файлу для взаимодействия
            poll_interval: Интервал опроса файла в секундах
        """
        super().__init__(shared_file)
        self.poll_interval = poll_interval
        self.state = ServerState.IDLE
        self.running = False
        self.requests_processed = 0
        self.last_request_id = None

    def _change_state(self, new_state: ServerState):
        """
        Изменение состояния сервера с логированием.

        Args:
            new_state: Новое состояние сервера
        """
        self._log(f"State transition: {self.state.value} -> {new_state.value}")
        self.state = new_state

    def wait_for_request(self) -> Optional[str]:
        """
        Шаг 1: Ожидание запроса от клиента.

        Returns:
            Содержимое запроса или None если файл не существует/пуст

        Raises:
            FileAccessError: При ошибке чтения файла
        """
        self._change_state(ServerState.WAITING_REQUEST)

        content = self._read_file()
        if not content:
            return None

        # Проверка что это запрос от клиента
        if content.startswith("CLIENT_REQUEST"):
            self._log(f"Request detected: {content}")
            return content

        return None

    def process_request(self, request: str) -> dict:
        """
        Шаг 1.1: Обработка запроса.

        Args:
            request: Строка запроса от клиента

        Returns:
            Словарь с разобранными данными запроса

        Raises:
            InvalidRequestError: При неверном формате запроса
        """
        self._change_state(ServerState.PROCESSING_REQUEST)
        self._log(f"Processing request: {request}")

        try:
            # Формат: CLIENT_REQUEST|ping|request_id|timestamp
            parts = request.split("|")

            if len(parts) < 4:
                raise InvalidRequestError(f"Invalid request format: expected 4 parts, got {len(parts)}")

            if parts[0] != "CLIENT_REQUEST":
                raise InvalidRequestError(f"Invalid request header: {parts[0]}")

            if parts[1] != "ping":
                raise InvalidRequestError(f"Expected 'ping' message, got: {parts[1]}")

            request_data = {
                'type': parts[0],
                'message': parts[1],
                'request_id': parts[2],
                'timestamp': parts[3]
            }

            # Проверка на дублирование запроса
            if self.last_request_id == request_data['request_id']:
                self._log(f"Duplicate request detected: {request_data['request_id']}")
                request_data['duplicate'] = True
            else:
                request_data['duplicate'] = False
                self.last_request_id = request_data['request_id']

            self._log(f"Request parsed: ID={request_data['request_id']}, Time={request_data['timestamp']}")
            return request_data

        except (IndexError, ValueError) as e:
            raise InvalidRequestError(f"Failed to parse request: {e}")

    def create_response(self, request_data: dict) -> str:
        """
        Создание ответа pong на запрос ping.

        Args:
            request_data: Разобранные данные запроса

        Returns:
            Строка ответа в формате "SERVER_RESPONSE|pong|request_id|timestamp"
        """
        response_timestamp = datetime.now().isoformat()
        response = f"SERVER_RESPONSE|pong|{request_data['request_id']}|{response_timestamp}"
        self._log(f"Created response: {response}")
        return response

    def send_response(self, response: str):
        """
        Шаг 2: Отправка ответа клиенту.

        Args:
            response: Строка ответа для отправки

        Raises:
            FileAccessError: При ошибке записи в файл
        """
        self._change_state(ServerState.SENDING_RESPONSE)
        self._write_file(response)
        self._log(f"Response sent to file: {self.shared_file}")
        self.requests_processed += 1

    def handle_error(self, error: Exception):
        """
        Шаг 1.2: Обработка ошибки.

        Args:
            error: Исключение, которое произошло
        """
        self._change_state(ServerState.ERROR)
        self._log(f"ERROR: {type(error).__name__}: {error}")

        # Попытка очистить файл при ошибке
        try:
            self._clear_file()
        except FileAccessError:
            self._log("Warning: Failed to clear file after error")

    def process_single_request(self) -> bool:
        """
        Обработка одного запроса (полный цикл).

        Returns:
            True если запрос был обработан, False если запросов нет
        """
        try:
            # 1. Ожидание запроса
            request = self.wait_for_request()

            if request is None:
                return False

            # 1.1. Обработка запроса
            request_data = self.process_request(request)

            # Пропуск дубликатов
            if request_data.get('duplicate', False):
                self._log("Skipping duplicate request")
                return False

            # Создание ответа
            response = self.create_response(request_data)

            # Небольшая задержка для имитации обработки
            time.sleep(0.05)

            # 2. Отправка ответа
            self.send_response(response)

            # Успех
            self._change_state(ServerState.COMPLETED)
            self._log("Request-response cycle completed successfully")
            return True

        except CommunicationError as e:
            # 1.2. Обработка ошибки
            self.handle_error(e)
            return False
        except Exception as e:
            self.handle_error(CommunicationError(f"Unexpected error: {e}"))
            return False

    def start(self, max_requests: Optional[int] = None):
        """
        Запуск сервера в режиме ожидания запросов.

        Args:
            max_requests: Максимальное количество запросов для обработки (None = бесконечно)
        """
        self._log("Starting server...")
        self._log(f"Shared file: {self.shared_file}")
        self._log(f"Poll interval: {self.poll_interval}s")

        if max_requests:
            self._log(f"Will process maximum {max_requests} requests")

        self.running = True
        self.requests_processed = 0

        # Очистка файла при запуске
        self._remove_file()

        try:
            while self.running:
                # Обработка запроса если он есть
                processed = self.process_single_request()

                # Проверка лимита запросов
                if max_requests and self.requests_processed >= max_requests:
                    self._log(f"Reached maximum requests limit: {max_requests}")
                    break

                # Если запрос не был обработан, переход в режим ожидания
                if not processed:
                    self._change_state(ServerState.WAITING_REQUEST)
                    time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            self._log("Server interrupted by user")
        finally:
            self.stop()

    def stop(self):
        """Остановка сервера и очистка ресурсов."""
        self._log("Stopping server...")
        self.running = False
        self._remove_file()
        self._log(f"Total requests processed: {self.requests_processed}")
        self._log("Server stopped")
