"""
Класс ошибки доступа к файлу.
"""

from src.errors.communication_error import CommunicationError


class FileAccessError(CommunicationError):
    """Ошибка доступа к общему файлу."""
    pass
