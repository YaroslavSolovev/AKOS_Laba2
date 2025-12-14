# Person 3: Клиент (часть 1) - создание и отправка запросов

## Ответственность
Реализация класса клиента: создание и отправка запросов, ожидание ответа

## Файлы для реализации
- `src/client.py` (первая часть: класс + первые методы)

## Задачи

### 1. Создать класс `PingPongClient`

**Наследование:** от `BaseCommunicator`

**Импорты:**
```python
import time
from typing import Optional

from src.base_communicator import BaseCommunicator
from src.states import ClientState
from src.errors import (
    CommunicationError,
    FileAccessError,
    TimeoutError,
    InvalidResponseError
)
```

### 2. Реализовать методы

#### `__init__(self, shared_file: str = "shared_communication.txt", timeout: int = 30)`
- Вызвать `super().__init__(shared_file)`
- Инициализировать:
  - `self.timeout` - таймаут ожидания
  - `self.state = ClientState.IDLE` - начальное состояние

#### `_change_state(self, new_state: ClientState)`
- Просто обновить `self.state = new_state`
- **БЕЗ логирования** переходов состояний

#### `create_request(self, message: str = "ping") -> str`
- Изменить состояние на `CREATING_REQUEST`
- Вернуть сообщение как есть (без форматирования)
- **НЕТ request_id, НЕТ timestamp** - просто возвращаем `message`

#### `send_request(self, request: str)`
- Записать запрос в файл через `self._write_file(request)`
- Логировать: `self._log(f"> {request}")`

#### `wait_for_response(self, sent_request: str) -> bool`
- Изменить состояние на `WAITING_RESPONSE`
- В цикле:
  - Читать файл через `self._read_file()`
  - Проверять что содержимое **отличается** от `sent_request`
  - Если содержимое != запросу - значит это ответ от сервера, вернуть `True`
  - Игнорировать `FileAccessError` (файл может быть заблокирован)
  - Пауза 0.1 секунды между проверками
- Если время вышло - бросить `TimeoutError(f"Нет ответа ({self.timeout}s)")`

## Критерии приемки
- Все методы имеют docstring
- Type hints для параметров
- Простой формат запроса (без ID и timestamp)
- Правильная обработка таймаута
- Клиент не читает свой же запрос (ждет когда содержимое изменится)
- Код следует PEP 8

## Объем работы
~80 строк кода
