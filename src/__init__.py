"""
ООП-реализация межпроцессного взаимодействия через файл-дескриптор.
Паттерн ping-pong между клиентом и сервером.
"""

__version__ = "1.0.0"
__author__ = "Python laba2"

from src.client import PingPongClient
from src.server import PingPongServer
from src.states import ClientState, ServerState
from src.errors import (
    CommunicationError,
    FileAccessError,
    TimeoutError,
    InvalidRequestError,
    InvalidResponseError
)

__all__ = [
    'PingPongClient',
    'PingPongServer',
    'ClientState',
    'ServerState',
    'CommunicationError',
    'FileAccessError',
    'TimeoutError',
    'InvalidRequestError',
    'InvalidResponseError',
]
