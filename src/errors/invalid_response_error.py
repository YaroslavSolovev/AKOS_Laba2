"""
Класс ошибки неверного формата ответа от сервера.
"""

from src.errors.communication_error import CommunicationError


class InvalidResponseError(CommunicationError):
    """Ошибка неверного формата ответа от сервера."""
    pass
