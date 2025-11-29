"""
Класс ошибки таймаута при ожидании ответа.
"""

from src.errors.communication_error import CommunicationError


class TimeoutError(CommunicationError):
    """Ошибка таймаута при ожидании ответа."""
    pass
