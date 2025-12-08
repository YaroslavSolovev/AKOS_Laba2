# Все ошибки в одном месте

from src.errors.communication_error import CommunicationError
from src.errors.file_access_error import FileAccessError
from src.errors.timeout_error import TimeoutError
from src.errors.invalid_request_error import InvalidRequestError
from src.errors.invalid_response_error import InvalidResponseError

__all__ = [
    'CommunicationError',
    'FileAccessError',
    'TimeoutError',
    'InvalidRequestError',
    'InvalidResponseError',
]
