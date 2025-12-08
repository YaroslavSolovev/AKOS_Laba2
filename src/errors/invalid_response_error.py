# Ошибка неверного формата ответа

from src.errors.communication_error import CommunicationError


class InvalidResponseError(CommunicationError):
    # Ответ от сервера неправильный
    pass
