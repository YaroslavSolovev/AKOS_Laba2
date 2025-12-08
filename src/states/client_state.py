# Состояния клиента для ping-pong

from enum import Enum


class ClientState(Enum):
    # Возможные состояния работы клиента
    IDLE = "idle"  # ничего не делаем
    CREATING_REQUEST = "creating_request"  # создаем запрос
    WAITING_RESPONSE = "waiting_response"  # ждем ответа
    READING_RESPONSE = "reading_response"  # читаем ответ
    ERROR = "error"  # если ошибка
    COMPLETED = "completed"  # все готово
