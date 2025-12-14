"""
Класс ошибки неверного формата запроса от клиента.
"""

from src.errors.communication_error import CommunicationError


class InvalidRequestError(CommunicationError):
    """Ошибка неверного формата запроса от клиента."""
    pass
