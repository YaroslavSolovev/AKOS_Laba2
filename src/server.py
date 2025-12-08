# Сервер для обработки ping-pong запросов через файл

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
    # Класс сервера - ждет запросы, обрабатывает и отвечает

    def __init__(self, shared_file: str = "shared_communication.txt", poll_interval: float = 0.1):
        # Инициализация сервера
        super().__init__(shared_file)
        self.poll_interval = poll_interval  # как часто проверяем файл
        self.state = ServerState.IDLE  # начальное состояние
        self.running = False  # флаг работы
        self.requests_processed = 0  # счетчик запросов
        self.last_request_id = None  # для проверки дубликатов

    def _change_state(self, new_state: ServerState):
        # Меняем состояние и логируем
        self._log(f"State transition: {self.state.value} -> {new_state.value}")
        self.state = new_state

    def wait_for_request(self) -> Optional[str]:
        # Ждем запрос от клиента
        self._change_state(ServerState.WAITING_REQUEST)

        content = self._read_file()
        if not content:
            return None

        # Проверяем что это именно запрос от клиента
        if content.startswith("CLIENT_REQUEST"):
            self._log(f"Request detected: {content}")
            return content

        return None

    def process_request(self, request: str) -> dict:
        # Обрабатываем запрос - разбираем и проверяем формат
        self._change_state(ServerState.PROCESSING_REQUEST)
        self._log(f"Processing request: {request}")

        try:
            # Разбиваем строку по разделителю |
            # Ожидаемый формат: CLIENT_REQUEST|ping|request_id|timestamp
            parts = request.split("|")

            # Проверяем что все части на месте
            if len(parts) < 4:
                raise InvalidRequestError(f"Invalid request format: expected 4 parts, got {len(parts)}")

            if parts[0] != "CLIENT_REQUEST":
                raise InvalidRequestError(f"Invalid request header: {parts[0]}")

            if parts[1] != "ping":
                raise InvalidRequestError(f"Expected 'ping' message, got: {parts[1]}")

            # Собираем данные в словарь
            request_data = {
                'type': parts[0],
                'message': parts[1],
                'request_id': parts[2],
                'timestamp': parts[3]
            }

            # Проверяем на дубликаты
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
        # Создаем ответ pong на ping
        response_timestamp = datetime.now().isoformat()
        response = f"SERVER_RESPONSE|pong|{request_data['request_id']}|{response_timestamp}"
        self._log(f"Created response: {response}")
        return response

    def send_response(self, response: str):
        # Отправляем ответ клиенту (записываем в файл)
        self._change_state(ServerState.SENDING_RESPONSE)
        self._write_file(response)
        self._log(f"Response sent to file: {self.shared_file}")
        self.requests_processed += 1

    def handle_error(self, error: Exception):
        # Обрабатываем ошибки
        self._change_state(ServerState.ERROR)
        self._log(f"ERROR: {type(error).__name__}: {error}")

        # Пытаемся очистить файл после ошибки
        try:
            self._clear_file()
        except FileAccessError:
            self._log("Warning: Failed to clear file after error")

    def process_single_request(self) -> bool:
        # Обрабатываем один запрос от начала до конца
        try:
            # Ждем запрос
            request = self.wait_for_request()

            if request is None:
                return False

            # Парсим запрос
            request_data = self.process_request(request)

            # Если дубликат - пропускаем
            if request_data.get('duplicate', False):
                self._log("Skipping duplicate request")
                return False

            # Создаем ответ
            response = self.create_response(request_data)

            # Небольшая задержка (типа думаем)
            time.sleep(0.05)

            # Отправляем ответ
            self.send_response(response)

            # Готово!
            self._change_state(ServerState.COMPLETED)
            self._log("Request-response cycle completed successfully")
            return True

        except CommunicationError as e:
            self.handle_error(e)
            return False
        except Exception as e:
            self.handle_error(CommunicationError(f"Unexpected error: {e}"))
            return False

    def start(self, max_requests: Optional[int] = None):
        # Запускаем сервер
        self._log("Starting server...")
        self._log(f"Shared file: {self.shared_file}")
        self._log(f"Poll interval: {self.poll_interval}s")

        if max_requests:
            self._log(f"Will process maximum {max_requests} requests")

        self.running = True
        self.requests_processed = 0

        # Удаляем старый файл если есть
        self._remove_file()

        try:
            while self.running:
                # Пытаемся обработать запрос
                processed = self.process_single_request()

                # Если достигли лимита - выходим
                if max_requests and self.requests_processed >= max_requests:
                    self._log(f"Reached maximum requests limit: {max_requests}")
                    break

                # Если запроса не было - ждем
                if not processed:
                    self._change_state(ServerState.WAITING_REQUEST)
                    time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            self._log("Server interrupted by user")
        finally:
            self.stop()

    def stop(self):
        # Останавливаем сервер и чистим за собой
        self._log("Stopping server...")
        self.running = False
        self._remove_file()
        self._log(f"Total requests processed: {self.requests_processed}")
        self._log("Server stopped")
