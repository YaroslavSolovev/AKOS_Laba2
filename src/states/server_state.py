# Состояния сервера для ping-pong

from enum import Enum


class ServerState(Enum):
    # Возможные состояния работы сервера
    IDLE = "idle"  # ничего не делаем
    WAITING_REQUEST = "waiting_request"  # ждем запрос
    PROCESSING_REQUEST = "processing_request"  # обрабатываем запрос
    SENDING_RESPONSE = "sending_response"  # отправляем ответ
    ERROR = "error"  # если ошибка
    COMPLETED = "completed"  # все готово
