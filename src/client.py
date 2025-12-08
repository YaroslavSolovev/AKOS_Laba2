# Клиент для отправки ping-запросов

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
    # Класс клиента - отправляет запросы и ждет ответы

    def __init__(self, shared_file: str = "shared_communication.txt", timeout: int = 30):
        # Инициализация клиента
        super().__init__(shared_file)
        self.timeout = timeout  # таймаут ожидания ответа
        self.state = ClientState.IDLE  # начальное состояние
        self.request_id = 0  # счетчик запросов
        self.max_retries = 3  # макс попыток при ошибке

    def _change_state(self, new_state: ClientState):
        # Меняем состояние и логируем
        self._log(f"State transition: {self.state.value} -> {new_state.value}")
        self.state = new_state

    def create_request(self) -> str:
        # Создаем ping-запрос
        self._change_state(ClientState.CREATING_REQUEST)
        self.request_id += 1
        timestamp = datetime.now().isoformat()
        request = f"CLIENT_REQUEST|ping|{self.request_id}|{timestamp}"
        self._log(f"Created request: {request}")
        return request

    def send_request(self, request: str):
        # Отправляем запрос (пишем в файл)
        self._write_file(request)
        self._log(f"Request sent to file: {self.shared_file}")

    def wait_for_response(self) -> bool:
        # Ждем ответ от сервера
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
                pass  # файл может быть занят сервером

            time.sleep(0.1)  # небольшая пауза

        raise TimeoutError(f"No response received within {self.timeout} seconds")

    def read_response(self) -> str:
        # Читаем и проверяем ответ от сервера
        self._change_state(ClientState.READING_RESPONSE)

        response = self._read_file()
        if not response:
            raise InvalidResponseError("Empty response from server")

        self._log(f"Read response: {response}")

        # Проверяем формат ответа
        if not response.startswith("SERVER_RESPONSE"):
            raise InvalidResponseError(f"Invalid response format: {response}")

        parts = response.split("|")
        if len(parts) < 4 or parts[1] != "pong":
            raise InvalidResponseError(f"Expected 'pong' response, got: {response}")

        return response

    def handle_error(self, error: Exception, retry_count: int = 0) -> bool:
        # Обрабатываем ошибку и решаем повторять ли попытку
        self._change_state(ClientState.ERROR)
        self._log(f"ERROR: {type(error).__name__}: {error}")

        if retry_count < self.max_retries:
            self._log(f"Retry {retry_count + 1}/{self.max_retries}")
            time.sleep(1)  # пауза перед повтором
            return True
        else:
            self._log("Max retries reached. Giving up.")
            return False

    def cleanup(self):
        # Чистим файл после завершения
        self._remove_file()

    def send_ping(self) -> Optional[str]:
        # Главный метод - полный цикл ping-pong
        retry_count = 0

        while retry_count <= self.max_retries:
            try:
                # Создаем запрос
                request = self.create_request()

                # Отправляем
                self.send_request(request)

                # Ждем ответ
                self.wait_for_response()

                # Читаем ответ
                response = self.read_response()

                # Готово!
                self._change_state(ClientState.COMPLETED)
                self._log("Ping-pong cycle completed successfully")
                return response

            except (CommunicationError, Exception) as e:
                # Если ошибка - пытаемся повторить
                should_retry = self.handle_error(e, retry_count)
                if not should_retry:
                    return None
                retry_count += 1

        return None
