"""
Пакет перечислений состояний для клиента и сервера.
Каждый Enum в отдельном файле.
"""

from src.states.client_state import ClientState
from src.states.server_state import ServerState

__all__ = [
    'ClientState',
    'ServerState',
]
