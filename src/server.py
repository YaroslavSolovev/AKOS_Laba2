"""
ООП-реализация сервера для ping-pong взаимодействия.
Сервер ожидает запросы, обрабатывает их и отправляет ответы.
"""

import time
from typing import Optional

from src.base_communicator import BaseCommunicator
from src.states import ServerState


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

    def _change_state(self, new_state: ServerState):
        """
        Изменение состояния сервера.

        Args:
            new_state: Новое состояние сервера
        """
        self.state = new_state

    def wait_for_request(self) -> Optional[str]:
        """
        Ожидание запроса от клиента.

        Returns:
            Содержимое запроса или None если файл не существует/пуст
        """
        self._change_state(ServerState.WAITING_REQUEST)
        content = self._read_file()

        if content and content.strip():
            return content.strip()

        return None

    def process_request(self, request: str) -> str:
        """
        Обработка запроса.

        Args:
            request: Строка запроса от клиента

        Returns:
            Ответ на запрос

        Raises:
            ValueError: Если запрос не "ping"
        """
        self._change_state(ServerState.PROCESSING_REQUEST)

        # Принимаем только "ping"
        if request.lower() == "ping":
            return "pong"
        else:
            raise ValueError(f"Неверный запрос: '{request}' (ожидается 'ping')")


    def send_response(self, response: str):
        """
        Отправка ответа клиенту.

        Args:
            response: Строка ответа для отправки
        """
        self._change_state(ServerState.SENDING_RESPONSE)
        self._write_file(response)
        self._log(f"> {response}")
        self.requests_processed += 1

    def handle_error(self, error: Exception):
        """
        Обработка ошибки.

        Args:
            error: Исключение, которое произошло
        """
        self._change_state(ServerState.ERROR)
        self._log(f"Ошибка: {error}")

    def process_single_request(self) -> bool:
        """
        Обработка одного запроса (полный цикл).

        Returns:
            True если запрос был обработан, False если запросов нет
        """
        try:
            # Ожидание запроса
            request = self.wait_for_request()
            if request is None:
                return False

            # Логируем что получили
            self._log(f"< {request}")

            # Обработка запроса (может выбросить исключение)
            response = self.process_request(request)

            # Небольшая задержка
            time.sleep(0.05)

            # Отправка ответа
            self.send_response(response)

            # Даем клиенту время прочитать ответ
            time.sleep(0.2)

            # Очищаем файл после отправки ответа
            # чтобы не прочитать свой же ответ в следующей итерации
            try:
                self._clear_file()
            except:
                pass

            self._change_state(ServerState.COMPLETED)
            return True

        except ValueError as e:
            # Неверный запрос - отправляем сообщение об ошибке клиенту
            self.handle_error(e)

            # Отправляем ошибку клиенту
            error_message = "ERROR: ожидается 'ping'"
            try:
                self._write_file(error_message)
                self._log(f"> {error_message}")
                # Даем клиенту время прочитать ошибку
                time.sleep(0.2)
                # Очищаем файл
                self._clear_file()
            except:
                pass

            return False
        except Exception as e:
            self.handle_error(e)
            return False

    def start(self, max_requests: Optional[int] = None):
        """
        Запуск сервера в режиме ожидания запросов.

        Args:
            max_requests: Максимальное количество запросов для обработки (None = бесконечно)
        """
        self._log("Сервер запущен")

        self.running = True
        self.requests_processed = 0
        self._remove_file()

        try:
            while self.running:
                processed = self.process_single_request()

                # Проверка лимита запросов
                if max_requests and self.requests_processed >= max_requests:
                    self._log(f"Достигнут лимит запросов: {max_requests}")
                    break

                if not processed:
                    self._change_state(ServerState.WAITING_REQUEST)
                    time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            self._log("\nОстановка сервера...")
        finally:
            self.stop()

    def stop(self):
        """Остановка сервера и очистка ресурсов."""
        self.running = False
        self._remove_file()
        self._log(f"Обработано запросов: {self.requests_processed}")
