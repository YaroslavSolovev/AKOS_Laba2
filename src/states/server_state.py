"""
Перечисление состояний сервера.
Реализует диаграмму состояний для сервера в ping-pong взаимодействии.
"""

from enum import Enum


class ServerState(Enum):
    """
    Состояния сервера согласно диаграмме состояний.

    Переходы:
    IDLE -> WAITING_REQUEST -> PROCESSING_REQUEST -> SENDING_RESPONSE -> COMPLETED
                |                      |
                v                      v
              IDLE                  ERROR
    """
    IDLE = "idle"
    WAITING_REQUEST = "waiting_request"
    PROCESSING_REQUEST = "processing_request"
    SENDING_RESPONSE = "sending_response"
    ERROR = "error"
    COMPLETED = "completed"
