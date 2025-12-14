# Person 5: Сервер + состояния сервера + точка входа

## Ответственность
Полная реализация сервера с управлением состояниями

## Файлы для реализации
- `src/states/server_state.py`
- `src/server.py`
- `server_app.py`

## Задачи

### 1. Создать перечисление `ServerState`

**Файл:** `src/states/server_state.py`

```python
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

### 2. Создать класс `PingPongServer`

**Наследование:** от `BaseCommunicator`

**Импорты:**
```python
import time
from typing import Optional

from src.base_communicator import BaseCommunicator
from src.states import ServerState
```

#### `__init__(self, shared_file: str = "shared_communication.txt", poll_interval: float = 0.1)`
- Вызвать `super().__init__(shared_file)`
- Инициализировать:
  - `self.poll_interval` - интервал опроса
  - `self.state = ServerState.IDLE`
  - `self.running = False`
  - `self.requests_processed = 0`

#### `_change_state(self, new_state: ServerState)`
- Просто обновить `self.state = new_state`
- **БЕЗ логирования** переходов

#### `wait_for_request(self) -> Optional[str]`
- Изменить состояние на `WAITING_REQUEST`
- Прочитать файл
- Если есть содержимое - вернуть его
- Иначе вернуть `None`

#### `process_request(self, request: str) -> str`
- Изменить состояние на `PROCESSING_REQUEST`
- **ВАЖНО:** Принимать ТОЛЬКО "ping"!
- Если `request.lower() == "ping"` → вернуть `"pong"`
- Иначе → `raise ValueError(f"Неверный запрос: '{request}' (ожидается 'ping')")`

#### `send_response(self, response: str)`
- Изменить состояние на `SENDING_RESPONSE`
- Записать ответ: `self._write_file(response)`
- Логировать: `self._log(f"> {response}")`
- Увеличить счетчик: `self.requests_processed += 1`

#### `handle_error(self, error: Exception)`
- Изменить состояние на `ERROR`
- Логировать: `self._log(f"Ошибка: {error}")`

#### `process_single_request(self) -> bool`
Полный цикл обработки одного запроса:
```python
def process_single_request(self) -> bool:
    try:
        request = self.wait_for_request()
        if request is None:
            return False

        # Логируем что получили
        self._log(f"< {request}")

        # Обработка запроса (может выбросить ValueError)
        response = self.process_request(request)

        time.sleep(0.05)

        # Отправка ответа
        self.send_response(response)

        # Даем клиенту время прочитать
        time.sleep(0.2)

        # Очищаем файл чтобы не прочитать свой же ответ
        try:
            self._clear_file()
        except:
            pass

        self._change_state(ServerState.COMPLETED)
        return True

    except ValueError as e:
        # Неверный запрос - отправляем ошибку клиенту
        self.handle_error(e)

        # Отправляем сообщение об ошибке
        error_message = "ERROR: ожидается 'ping'"
        try:
            self._write_file(error_message)
            self._log(f"> {error_message}")
            time.sleep(0.2)
            self._clear_file()
        except:
            pass

        return False
    except Exception as e:
        self.handle_error(e)
        return False
```

#### `start(self, max_requests: Optional[int] = None)`
Главный цикл сервера:
```python
def start(self, max_requests: Optional[int] = None):
    self._log("Сервер запущен")
    self.running = True
    self.requests_processed = 0
    self._remove_file()

    try:
        while self.running:
            processed = self.process_single_request()

            if max_requests and self.requests_processed >= max_requests:
                self._log(f"Достигнут лимит запросов: {max_requests}")
                break

            if not processed:
                self._change_state(ServerState.WAITING_REQUEST)
                time.sleep(self.poll_interval)

    except KeyboardInterrupt:
        self._log("\nОстановка сервера...")
    finally:
        self.stop()
```

#### `stop(self)`
```python
def stop(self):
    self.running = False
    self._remove_file()
    self._log(f"Обработано запросов: {self.requests_processed}")
```

### 3. Создать точку входа `server_app.py`

```python
"""
Серверное приложение для ping-pong взаимодействия.
Обрабатывает запросы от клиента.
"""

import sys
from src.server import PingPongServer


def main():
    """Главная функция для запуска сервера."""
    print("=" * 60)
    print("PING-PONG SERVER")
    print("Ожидание запросов от клиента...")
    print("Нажмите Ctrl+C для остановки")
    print("=" * 60)

    server = PingPongServer(
        shared_file="shared_communication.txt",
        poll_interval=0.1
    )

    try:
        # Запуск сервера (без лимита запросов)
        server.start()

    except Exception as e:
        print(f"\nОшибка: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Сервер остановлен")
    print("=" * 60)


if __name__ == "__main__":
    main()
```

## Критерии приемки
- Принимает ТОЛЬКО "ping"
- На другие запросы отправляет "ERROR: ожидается 'ping'"
- Корректная обработка запросов
- Graceful shutdown (Ctrl+C)
- Очистка файла между запросами
- Понятное логирование
- Код следует PEP 8

## Объем работы
~170 строк кода

## Использование
```
[SERVER] Сервер запущен
[SERVER] < ping
[SERVER] > pong
[SERVER] < hello
[SERVER] Ошибка: Неверный запрос: 'hello' (ожидается 'ping')
[SERVER] > ERROR: ожидается 'ping'
```
