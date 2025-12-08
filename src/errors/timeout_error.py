# Ошибка таймаута

from src.errors.communication_error import CommunicationError


class TimeoutError(CommunicationError):
    # Превышено время ожидания ответа
    pass
