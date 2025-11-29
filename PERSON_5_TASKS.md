# 👤 Задачи для Человека 5: Сервер + состояния + приложение

## Ваша роль: Полная реализация серверной части

Вы отвечаете за создание состояний сервера, полный класс сервера и приложение.

---

## 📁 Ваши файлы:

1. `src/states/server_state.py`
2. `src/server.py`
3. `server_app.py`

---

## ⚠️ Зависимости:

Вы можете начать работу ТОЛЬКО после того, как завершат:
- **Человек 1** (BaseCommunicator)
- **Человек 2** (исключения)

---

## ✅ Задача 1: Создать перечисление ServerState

**Файл:** `src/states/server_state.py`

### Состояния сервера согласно ТЗ:

1. `IDLE` - начальное состояние
2. `WAITING_REQUEST` - ожидание запроса от клиента
3. `PROCESSING_REQUEST` - обработка запроса (шаг 1.1)
4. `SENDING_RESPONSE` - отправка ответа (шаг 2)
5. `ERROR` - обработка ошибки (шаг 1.2)
6. `COMPLETED` - успешное завершение цикла

**Диаграмма переходов:**
```
IDLE → WAITING_REQUEST → PROCESSING_REQUEST → SENDING_RESPONSE → COMPLETED
         ↑                      |
         |                      v
        IDLE                  ERROR
```

### Код:

```python
"""
Перечисление состояний сервера.
Реализует диаграмму состояний для сервера в ping-pong взаимодействии.
"""

from enum import Enum


class ServerState(Enum):
    """
    Состояния сервера согласно диаграмме состояний.

    Переходы:
    IDLE -> WAITING_REQUEST -> PROCESSING_REQUEST -> SENDING_RESPONSE -> COMPLETED
                |                      |
                v                      v
              IDLE                  ERROR
    """
    IDLE = "idle"
    WAITING_REQUEST = "waiting_request"
    PROCESSING_REQUEST = "processing_request"
    SENDING_RESPONSE = "sending_response"
    ERROR = "error"
    COMPLETED = "completed"
```

### Обновите src/states/__init__.py:

Человек 2 уже создал базовый файл. Вам нужно ДОПОЛНИТЬ его:

```python
"""
Модуль с перечислениями состояний для клиента и сервера.
"""

from src.states.client_state import ClientState
from src.states.server_state import ServerState

__all__ = [
    'ClientState',
    'ServerState',
]
```

---

## ✅ Задача 2: Создать класс PingPongServer

**Файл:** `src/server.py`

### Импорты:

```python
"""
ООП-реализация сервера для ping-pong взаимодействия.
Сервер ожидает запросы, обрабатывает их и отправляет ответы.
"""

import time
from datetime import datetime
from typing import Optional

from src.base_communicator import BaseCommunicator
from src.states import ServerState
from src.errors import (
    CommunicationError,
    FileAccessError,
    InvalidRequestError
)
```

---

### Методы для реализации:

### 1. __init__

```python
def __init__(self, shared_file: str = "shared_communication.txt", poll_interval: float = 0.1):
    """
    Инициализация сервера.

    Args:
        shared_file: Путь к общему файлу для взаимодействия
        poll_interval: Интервал опроса файла в секундах
    """
```

**Что делает:**
1. Вызывает `super().__init__(shared_file)`
2. Сохраняет `self.poll_interval = poll_interval`
3. Устанавливает начальное состояние: `self.state = ServerState.IDLE`
4. Флаг работы: `self.running = False`
5. Счетчик запросов: `self.requests_processed = 0`
6. ID последнего запроса: `self.last_request_id = None`

---

### 2. _change_state

```python
def _change_state(self, new_state: ServerState):
    """
    Изменение состояния сервера с логированием.

    Args:
        new_state: Новое состояние сервера
    """
```

**Что делает:**
1. Логирует: `f"State transition: {self.state.value} -> {new_state.value}"`
2. Обновляет: `self.state = new_state`

---

### 3. wait_for_request

```python
def wait_for_request(self) -> Optional[str]:
    """
    Шаг 1: Ожидание запроса от клиента.

    Returns:
        Содержимое запроса или None если файл не существует/пуст

    Raises:
        FileAccessError: При ошибке чтения файла
    """
```

**Что делает:**
1. Меняет состояние на `ServerState.WAITING_REQUEST`
2. Читает файл: `content = self._read_file()`
3. Если пусто - возвращает `None`
4. Если содержимое начинается с "CLIENT_REQUEST":
   - Логирует: `f"Request detected: {content}"`
   - Возвращает `content`
5. Иначе возвращает `None`

---

### 4. process_request

```python
def process_request(self, request: str) -> dict:
    """
    Шаг 1.1: Обработка запроса.

    Args:
        request: Строка запроса от клиента

    Returns:
        Словарь с разобранными данными запроса

    Raises:
        InvalidRequestError: При неверном формате запроса
    """
```

**Что делает:**
1. Меняет состояние на `ServerState.PROCESSING_REQUEST`
2. Логирует: `f"Processing request: {request}"`
3. В блоке try:
   - Разбивает запрос: `parts = request.split("|")`
   - Проверяет что частей >= 4, parts[0] == "CLIENT_REQUEST", parts[1] == "ping"
   - Создает словарь:
     ```python
     request_data = {
         'type': parts[0],
         'message': parts[1],
         'request_id': parts[2],
         'timestamp': parts[3]
     }
     ```
   - Проверяет на дубликат:
     ```python
     if self.last_request_id == request_data['request_id']:
         self._log(f"Duplicate request detected: {request_data['request_id']}")
         request_data['duplicate'] = True
     else:
         request_data['duplicate'] = False
         self.last_request_id = request_data['request_id']
     ```
   - Логирует: `f"Request parsed: ID={request_data['request_id']}, Time={request_data['timestamp']}"`
   - Возвращает `request_data`
4. В блоке except (IndexError, ValueError) выбрасывает `InvalidRequestError`

---

### 5. create_response

```python
def create_response(self, request_data: dict) -> str:
    """
    Создание ответа pong на запрос ping.

    Args:
        request_data: Разобранные данные запроса

    Returns:
        Строка ответа в формате "SERVER_RESPONSE|pong|request_id|timestamp"
    """
```

**Что делает:**
1. Получает timestamp: `response_timestamp = datetime.now().isoformat()`
2. Формирует ответ: `f"SERVER_RESPONSE|pong|{request_data['request_id']}|{response_timestamp}"`
3. Логирует: `f"Created response: {response}"`
4. Возвращает строку ответа

---

### 6. send_response

```python
def send_response(self, response: str):
    """
    Шаг 2: Отправка ответа клиенту.

    Args:
        response: Строка ответа для отправки

    Raises:
        FileAccessError: При ошибке записи в файл
    """
```

**Что делает:**
1. Меняет состояние на `ServerState.SENDING_RESPONSE`
2. Записывает в файл: `self._write_file(response)`
3. Логирует: `f"Response sent to file: {self.shared_file}"`
4. Увеличивает счетчик: `self.requests_processed += 1`

---

### 7. handle_error

```python
def handle_error(self, error: Exception):
    """
    Шаг 1.2: Обработка ошибки.

    Args:
        error: Исключение, которое произошло
    """
```

**Что делает:**
1. Меняет состояние на `ServerState.ERROR`
2. Логирует: `f"ERROR: {type(error).__name__}: {error}"`
3. Пытается очистить файл:
   ```python
   try:
       self._clear_file()
   except FileAccessError:
       self._log("Warning: Failed to clear file after error")
   ```

---

### 8. process_single_request

```python
def process_single_request(self) -> bool:
    """
    Обработка одного запроса (полный цикл).

    Returns:
        True если запрос был обработан, False если запросов нет
    """
```

**Что делает:**
1. В блоке try:
   - Ждет запрос: `request = self.wait_for_request()`
   - Если `None` - возвращает `False`
   - Обрабатывает: `request_data = self.process_request(request)`
   - Если дубликат (`request_data.get('duplicate', False)`):
     - Логирует "Skipping duplicate request"
     - Возвращает `False`
   - Создает ответ: `response = self.create_response(request_data)`
   - Делает паузу: `time.sleep(0.05)` (имитация обработки)
   - Отправляет: `self.send_response(response)`
   - Меняет состояние на `ServerState.COMPLETED`
   - Логирует: "Request-response cycle completed successfully"
   - Возвращает `True`
2. В блоке except `CommunicationError`:
   - Вызывает `self.handle_error(e)`
   - Возвращает `False`
3. В блоке except `Exception`:
   - Вызывает `self.handle_error(CommunicationError(f"Unexpected error: {e}"))`
   - Возвращает `False`

---

### 9. start

```python
def start(self, max_requests: Optional[int] = None):
    """
    Запуск сервера в режиме ожидания запросов.

    Args:
        max_requests: Максимальное количество запросов для обработки (None = бесконечно)
    """
```

**Что делает:**
1. Логирует старт:
   ```python
   self._log("Starting server...")
   self._log(f"Shared file: {self.shared_file}")
   self._log(f"Poll interval: {self.poll_interval}s")
   if max_requests:
       self._log(f"Will process maximum {max_requests} requests")
   ```
2. Инициализирует: `self.running = True`, `self.requests_processed = 0`
3. Удаляет файл: `self._remove_file()`
4. В блоке try:
   - В цикле while `self.running`:
     - Обрабатывает запрос: `processed = self.process_single_request()`
     - Проверяет лимит:
       ```python
       if max_requests and self.requests_processed >= max_requests:
           self._log(f"Reached maximum requests limit: {max_requests}")
           break
       ```
     - Если не обработан:
       ```python
       if not processed:
           self._change_state(ServerState.WAITING_REQUEST)
           time.sleep(self.poll_interval)
       ```
5. В блоке except `KeyboardInterrupt`:
   - Логирует: "Server interrupted by user"
6. В блоке finally:
   - Вызывает `self.stop()`

---

### 10. stop

```python
def stop(self):
    """Остановка сервера и очистка ресурсов."""
```

**Что делает:**
1. Логирует: "Stopping server..."
2. Устанавливает: `self.running = False`
3. Удаляет файл: `self._remove_file()`
4. Логирует статистику: `f"Total requests processed: {self.requests_processed}"`
5. Логирует: "Server stopped"

---

## ✅ Задача 3: Создать server_app.py

```python
"""
Точка входа для серверного приложения.
Демонстрирует использование PingPongServer для обработки ping-запросов.
"""

import sys

from src.server import PingPongServer


def main():
    """Главная функция для запуска сервера."""
    print("=" * 60)
    print("PING-PONG SERVER")
    print("=" * 60)

    server = PingPongServer(
        shared_file="shared_communication.txt",
        poll_interval=0.1
    )

    try:
        # Запуск сервера (обработка 10 запросов или Ctrl+C для остановки)
        server.start(max_requests=10)

    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Server shutdown complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
```

---

## ✅ Критерии приемки:

- [ ] `ServerState` создан с 6 состояниями
- [ ] Класс `PingPongServer` наследуется от `BaseCommunicator`
- [ ] Все 10 методов реализованы
- [ ] Метод `process_request` корректно парсит запрос
- [ ] Метод `process_request` проверяет формат запроса
- [ ] Метод `process_single_request` реализует полный цикл
- [ ] Метод `start` работает в бесконечном цикле
- [ ] Поддержка `max_requests` для ограничения числа запросов
- [ ] Обработка `KeyboardInterrupt` (Ctrl+C)
- [ ] `server_app.py` запускается и обрабатывает запросы
- [ ] Все методы имеют docstring

---

## 🧪 Как протестировать:

### Тест 1: Запуск сервера

```bash
python server_app.py
```

Ожидаемый результат:
```
============================================================
PING-PONG SERVER
============================================================
[HH:MM:SS.mmm] [SERVER] Starting server...
[HH:MM:SS.mmm] [SERVER] Shared file: shared_communication.txt
[HH:MM:SS.mmm] [SERVER] Poll interval: 0.1s
[HH:MM:SS.mmm] [SERVER] Will process maximum 10 requests
[HH:MM:SS.mmm] [SERVER] Removed file: shared_communication.txt
[HH:MM:SS.mmm] [SERVER] State transition: idle -> waiting_request
[HH:MM:SS.mmm] [SERVER] State transition: waiting_request -> waiting_request
...
(сервер ждет запросы)
```

### Тест 2: Полный цикл с клиентом

**Терминал 1:**
```bash
python server_app.py
```

**Терминал 2:**
```bash
python client_app.py
```

Ожидаемый результат (терминал сервера):
```
[HH:MM:SS.mmm] [SERVER] Request detected: CLIENT_REQUEST|ping|1|...
[HH:MM:SS.mmm] [SERVER] State transition: waiting_request -> processing_request
[HH:MM:SS.mmm] [SERVER] Processing request: CLIENT_REQUEST|ping|1|...
[HH:MM:SS.mmm] [SERVER] Request parsed: ID=1, Time=...
[HH:MM:SS.mmm] [SERVER] Created response: SERVER_RESPONSE|pong|1|...
[HH:MM:SS.mmm] [SERVER] State transition: processing_request -> sending_response
[HH:MM:SS.mmm] [SERVER] Response sent to file: shared_communication.txt
[HH:MM:SS.mmm] [SERVER] State transition: sending_response -> completed
[HH:MM:SS.mmm] [SERVER] Request-response cycle completed successfully
...
[HH:MM:SS.mmm] [SERVER] Stopping server...
[HH:MM:SS.mmm] [SERVER] Total requests processed: 5
[HH:MM:SS.mmm] [SERVER] Server stopped
```

---

## 📚 Полезные ссылки:

- [Бесконечные циклы в Python](https://docs.python.org/3/reference/compound_stmts.html#while)
- [KeyboardInterrupt](https://docs.python.org/3/library/exceptions.html#KeyboardInterrupt)
- [dict.get() с значением по умолчанию](https://docs.python.org/3/library/stdtypes.html#dict.get)
