"""
Перечисление состояний клиента.
Реализует диаграмму состояний для клиента в ping-pong взаимодействии.
"""

from enum import Enum


class ClientState(Enum):
    """
    Состояния клиента согласно диаграмме состояний.

    Переходы:
    IDLE -> CREATING_REQUEST -> WAITING_RESPONSE -> READING_RESPONSE -> COMPLETED
                                      |                    |
                                      v                    v
                                   ERROR <--------------- ERROR
    """
    IDLE = "idle"
    CREATING_REQUEST = "creating_request"
    WAITING_RESPONSE = "waiting_response"
    READING_RESPONSE = "reading_response"
    ERROR = "error"
    COMPLETED = "completed"
