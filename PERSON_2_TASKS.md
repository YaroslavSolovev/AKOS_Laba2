# 👤 Задачи для Человека 2: Исключения и состояния клиента

## Ваша роль: Система ошибок и состояний

Вы отвечаете за создание оставшихся исключений и перечисления состояний клиента.

---

## 📁 Ваши файлы:

1. `src/errors/timeout_error.py`
2. `src/errors/invalid_request_error.py`
3. `src/errors/invalid_response_error.py`
4. `src/states/__init__.py`
5. `src/states/client_state.py`

---

## ✅ Задача 1: Создать исключение TimeoutError

**Файл:** `src/errors/timeout_error.py`

```python
"""
Исключение для ошибки таймаута при ожидании ответа.
"""

from src.errors.communication_error import CommunicationError


class TimeoutError(CommunicationError):
    """Исключение для ошибки таймаута при ожидании ответа."""
    pass
```

---

## ✅ Задача 2: Создать исключение InvalidRequestError

**Файл:** `src/errors/invalid_request_error.py`

```python
"""
Исключение для неверного формата запроса.
"""

from src.errors.communication_error import CommunicationError


class InvalidRequestError(CommunicationError):
    """Исключение для неверного формата запроса."""
    pass
```

---

## ✅ Задача 3: Создать исключение InvalidResponseError

**Файл:** `src/errors/invalid_response_error.py`

```python
"""
Исключение для неверного формата ответа.
"""

from src.errors.communication_error import CommunicationError


class InvalidResponseError(CommunicationError):
    """Исключение для неверного формата ответа."""
    pass
```

---

## ✅ Задача 4: Обновить __init__.py для errors

**Файл:** `src/errors/__init__.py`

Человек 1 уже создал базовый файл. Вам нужно ДОПОЛНИТЬ его:

```python
"""
Модуль с исключениями для системы ping-pong.
"""

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

---

## ✅ Задача 5: Создать перечисление ClientState

**Файл:** `src/states/client_state.py`

### Что нужно реализовать:

Создайте перечисление (Enum) с состояниями клиента согласно диаграмме состояний из ТЗ:

**Состояния клиента:**
1. `IDLE` - начальное состояние
2. `CREATING_REQUEST` - создание запроса ping
3. `WAITING_RESPONSE` - ожидание ответа от сервера
4. `READING_RESPONSE` - чтение ответа
5. `ERROR` - обработка ошибки
6. `COMPLETED` - успешное завершение

**Диаграмма переходов:**
```
IDLE → CREATING_REQUEST → WAITING_RESPONSE → READING_RESPONSE → COMPLETED
                                   ↓                  ↓
                                 ERROR ←------------- ERROR
```

### Шаблон кода:

```python
"""
Перечисление состояний клиента.
Реализует диаграмму состояний для клиента в ping-pong взаимодействии.
"""

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

---

## ✅ Задача 6: Создать __init__.py для states

**Файл:** `src/states/__init__.py`

```python
"""
Модуль с перечислениями состояний для клиента и сервера.
"""

from src.states.client_state import ClientState

__all__ = [
    'ClientState',
]
```

**Примечание:** `ServerState` добавит Человек 5

---

## ✅ Критерии приемки:

- [ ] Все 5 файлов созданы
- [ ] Все исключения наследуются от `CommunicationError`
- [ ] В `src/errors/__init__.py` экспортируются все 5 исключений
- [ ] `ClientState` является перечислением (Enum)
- [ ] В `ClientState` есть все 6 состояний
- [ ] Каждое состояние имеет строковое значение (например, "idle")
- [ ] В docstring `ClientState` описана диаграмма переходов
- [ ] Код следует PEP 8

---

## 🧪 Как протестировать:

Создайте тестовый файл `test_errors_states.py`:

```python
from src.errors import (
    CommunicationError,
    FileAccessError,
    TimeoutError,
    InvalidRequestError,
    InvalidResponseError
)
from src.states import ClientState

# Тест 1: Иерархия исключений
try:
    raise TimeoutError("Connection timeout")
except CommunicationError as e:
    print(f"✅ Caught CommunicationError: {e}")

# Тест 2: Состояния клиента
print(f"\nВсе состояния клиента:")
for state in ClientState:
    print(f"  - {state.name}: {state.value}")

# Тест 3: Проверка значений
assert ClientState.IDLE.value == "idle"
assert ClientState.CREATING_REQUEST.value == "creating_request"
assert ClientState.WAITING_RESPONSE.value == "waiting_response"
assert ClientState.READING_RESPONSE.value == "reading_response"
assert ClientState.ERROR.value == "error"
assert ClientState.COMPLETED.value == "completed"

print("\n✅ Все тесты пройдены!")
```

Должно вывести:
```
✅ Caught CommunicationError: Connection timeout

Все состояния клиента:
  - IDLE: idle
  - CREATING_REQUEST: creating_request
  - WAITING_RESPONSE: waiting_response
  - READING_RESPONSE: reading_response
  - ERROR: error
  - COMPLETED: completed

✅ Все тесты пройдены!
```

---

## 📚 Полезные ссылки:

- [Enum - перечисления в Python](https://docs.python.org/3/library/enum.html)
- [Исключения в Python](https://docs.python.org/3/tutorial/errors.html)
- [Пользовательские исключения](https://docs.python.org/3/tutorial/errors.html#user-defined-exceptions)
