# Ошибка неверного формата запроса

from src.errors.communication_error import CommunicationError


class InvalidRequestError(CommunicationError):
    # Запрос от клиента неправильный
    pass
