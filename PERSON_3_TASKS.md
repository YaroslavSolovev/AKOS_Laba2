# 👤 Задачи для Человека 3: Клиент - создание и отправка запросов

## Ваша роль: Первая часть клиента

Вы отвечаете за класс клиента и методы создания, отправки и ожидания ответов.

---

## 📁 Ваш файл:

`src/client.py` (первая половина - класс и первые 3 метода)

---

## ⚠️ Зависимости:

Вы можете начать работу ТОЛЬКО после того, как завершат:
- **Человек 1** (BaseCommunicator)
- **Человек 2** (ClientState, исключения)

---

## ✅ Задача: Создать класс PingPongClient (часть 1)

### Импорты:

```python
"""
ООП-реализация клиента для ping-pong взаимодействия.
Клиент создает запросы, ожидает ответы и обрабатывает ошибки.
"""

import time
from datetime import datetime
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

---

## Что нужно реализовать:

### 1. Класс PingPongClient

```python
class PingPongClient(BaseCommunicator):
    """
    Клиент для ping-pong взаимодействия через файл-дескриптор.

    Состояния:
    1. CREATING_REQUEST - создание запроса
    2. WAITING_RESPONSE - ожидание ответа
    3. READING_RESPONSE - чтение ответа
    4. ERROR - обработка ошибки
    """
```

Класс наследуется от `BaseCommunicator`.

---

### 2. Метод __init__

```python
def __init__(self, shared_file: str = "shared_communication.txt", timeout: int = 30):
    """
    Инициализация клиента.

    Args:
        shared_file: Путь к общему файлу для взаимодействия
        timeout: Таймаут ожидания ответа в секундах
    """
```

**Что делает:**
1. Вызывает `super().__init__(shared_file)`
2. Сохраняет `self.timeout = timeout`
3. Устанавливает начальное состояние: `self.state = ClientState.IDLE`
4. Инициализирует счетчик запросов: `self.request_id = 0`
5. Устанавливает максимум попыток: `self.max_retries = 3`

---

### 3. Метод _change_state

```python
def _change_state(self, new_state: ClientState):
    """
    Изменение состояния клиента с логированием.

    Args:
        new_state: Новое состояние клиента
    """
```

**Что делает:**
1. Логирует переход: `f"State transition: {self.state.value} -> {new_state.value}"`
2. Обновляет состояние: `self.state = new_state`

---

### 4. Метод create_request

```python
def create_request(self) -> str:
    """
    Шаг 1: Создание запроса ping.

    Returns:
        Строка запроса в формате "CLIENT_REQUEST|ping|request_id|timestamp"
    """
```

**Что делает:**
1. Меняет состояние на `ClientState.CREATING_REQUEST`
2. Увеличивает счетчик: `self.request_id += 1`
3. Получает timestamp: `datetime.now().isoformat()`
4. Формирует запрос: `f"CLIENT_REQUEST|ping|{self.request_id}|{timestamp}"`
5. Логирует: `f"Created request: {request}"`
6. Возвращает строку запроса

**Формат запроса:** `CLIENT_REQUEST|ping|1|2025-11-29T13:55:05.160412`

---

### 5. Метод send_request

```python
def send_request(self, request: str):
    """
    Отправка запроса в общий файл.

    Args:
        request: Строка запроса для отправки

    Raises:
        FileAccessError: При ошибке записи в файл
    """
```

**Что делает:**
1. Вызывает `self._write_file(request)` (метод из BaseCommunicator)
2. Логирует: `f"Request sent to file: {self.shared_file}"`

---

### 6. Метод wait_for_response

```python
def wait_for_response(self) -> bool:
    """
    Шаг 2: Ожидание ответа от сервера.

    Returns:
        True если ответ появился, False если таймаут

    Raises:
        TimeoutError: При истечении таймаута
    """
```

**Что делает:**
1. Меняет состояние на `ClientState.WAITING_RESPONSE`
2. Логирует: `f"Waiting for response (timeout: {self.timeout}s)..."`
3. Сохраняет время начала: `start_time = time.time()`
4. В цикле while пока не прошло `self.timeout` секунд:
   - Пытается прочитать файл через `self._read_file()`
   - Если content не None и начинается с "SERVER_RESPONSE":
     - Логирует "Response detected in file"
     - Возвращает `True`
   - Если возникает `FileAccessError` - игнорировать (файл может быть заблокирован)
   - Делает паузу `time.sleep(0.1)` для снижения нагрузки
5. Если таймаут истек - выбрасывает `TimeoutError`

---

## 📋 Полный шаблон кода:

```python
"""
ООП-реализация клиента для ping-pong взаимодействия.
Клиент создает запросы, ожидает ответы и обрабатывает ошибки.
"""

import time
from datetime import datetime
from typing import Optional

from src.base_communicator import BaseCommunicator
from src.states import ClientState
from src.errors import (
    CommunicationError,
    FileAccessError,
    TimeoutError,
    InvalidResponseError
)


class PingPongClient(BaseCommunicator):
    """
    Клиент для ping-pong взаимодействия через файл-дескриптор.

    Состояния:
    1. CREATING_REQUEST - создание запроса
    2. WAITING_RESPONSE - ожидание ответа
    3. READING_RESPONSE - чтение ответа
    4. ERROR - обработка ошибки
    """

    def __init__(self, shared_file: str = "shared_communication.txt", timeout: int = 30):
        # TODO: Реализовать
        pass

    def _change_state(self, new_state: ClientState):
        # TODO: Реализовать
        pass

    def create_request(self) -> str:
        # TODO: Реализовать
        pass

    def send_request(self, request: str):
        # TODO: Реализовать
        pass

    def wait_for_response(self) -> bool:
        # TODO: Реализовать
        pass
```

**Примечание:** Оставшиеся методы (`read_response`, `handle_error`, `cleanup`, `send_ping`) реализует Человек 4.

---

## ✅ Критерии приемки:

- [ ] Класс `PingPongClient` наследуется от `BaseCommunicator`
- [ ] Метод `__init__` инициализирует все необходимые атрибуты
- [ ] Метод `_change_state` логирует переходы состояний
- [ ] Метод `create_request` создает запрос в правильном формате
- [ ] Формат запроса: `CLIENT_REQUEST|ping|{id}|{timestamp}`
- [ ] Метод `send_request` записывает запрос в файл
- [ ] Метод `wait_for_response` корректно ждет ответ с таймаутом
- [ ] При таймауте выбрасывается исключение `TimeoutError`
- [ ] Все методы имеют docstring
- [ ] Код следует PEP 8

---

## 🧪 Как протестировать:

Создайте тестовый файл `test_client_part1.py`:

```python
from src.client import PingPongClient
import os
import time

# Создать клиента
client = PingPongClient("test_shared.txt", timeout=5)

# Тест 1: Создание запроса
request = client.create_request()
print(f"✅ Создан запрос: {request}")
assert request.startswith("CLIENT_REQUEST|ping|1|")

# Тест 2: Отправка запроса
client.send_request(request)
assert os.path.exists("test_shared.txt")
print("✅ Запрос отправлен в файл")

# Тест 3: Имитация ответа от сервера
with open("test_shared.txt", "w") as f:
    f.write("SERVER_RESPONSE|pong|1|2025-11-29T13:55:05.479380")

# Тест 4: Ожидание ответа
found = client.wait_for_response()
assert found == True
print("✅ Ответ найден")

# Очистка
os.remove("test_shared.txt")
print("\n✅ Все тесты пройдены!")
```

---

## 📚 Полезные ссылки:

- [time.time() - получение времени](https://docs.python.org/3/library/time.html#time.time)
- [datetime.isoformat()](https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat)
- [Наследование классов в Python](https://docs.python.org/3/tutorial/classes.html#inheritance)
