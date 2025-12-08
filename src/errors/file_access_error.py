# Ошибка доступа к файлу

from src.errors.communication_error import CommunicationError


class FileAccessError(CommunicationError):
    # Проблемы с чтением/записью файла
    pass
