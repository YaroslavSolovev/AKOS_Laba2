# Person 2: Исключения и состояния клиента

## Ответственность
Создание оставшихся исключений и перечисления состояний клиента

## Файлы для реализации
- `src/errors/timeout_error.py`
- `src/errors/invalid_request_error.py`
- `src/errors/invalid_response_error.py`
- `src/states/__init__.py`
- `src/states/client_state.py`

## Задачи

### 1. Создать исключения

Все исключения наследуются от `CommunicationError`:

**TimeoutError** (`src/errors/timeout_error.py`):
```python
from src.errors.communication_error import CommunicationError

class TimeoutError(CommunicationError):
    """Ошибка таймаута при ожидании ответа."""
    pass
```

**InvalidRequestError** (`src/errors/invalid_request_error.py`):
```python
from src.errors.communication_error import CommunicationError

class InvalidRequestError(CommunicationError):
    """Ошибка неверного формата запроса от клиента."""
    pass
```

**InvalidResponseError** (`src/errors/invalid_response_error.py`):
```python
from src.errors.communication_error import CommunicationError

class InvalidResponseError(CommunicationError):
    """Ошибка неверного формата ответа от сервера."""
    pass
```

### 2. Создать перечисление `ClientState`

**Файл:** `src/states/client_state.py`

```python
from enum import Enum

class ClientState(Enum):
    """
    Состояния клиента согласно диаграмме состояний.

    Переходы:
    IDLE -> CREATING_REQUEST -> WAITING_RESPONSE -> READING_RESPONSE -> COMPLETED
                                      |                    |
                                      v                    v
                                   ERROR <--------------- ERROR
    """
    IDLE = "idle"
    CREATING_REQUEST = "creating_request"
    WAITING_RESPONSE = "waiting_response"
    READING_RESPONSE = "reading_response"
    ERROR = "error"
    COMPLETED = "completed"
```

### 3. Обновить `__init__.py` в пакетах

**src/errors/__init__.py:**
```python
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
```

**src/states/__init__.py:**
```python
from src.states.client_state import ClientState

__all__ = ['ClientState']
```

## Критерии приемки
- Все классы имеют docstring
- Исключения правильно наследуются
- Enum корректно определен
- Диаграмма состояний описана в документации
- Код следует PEP 8

## Объем работы
~80 строк кода
