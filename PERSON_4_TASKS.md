# 👤 Задачи для Человека 4: Клиент - обработка ответов + приложение

## Ваша роль: Завершение клиента и точка входа

Вы отвечаете за дополнение класса клиента (чтение ответов, обработка ошибок) и создание приложения.

---

## 📁 Ваши файлы:

1. `src/client.py` (вторая половина - дополнить файл Человека 3)
2. `client_app.py` (новый файл)

---

## ⚠️ Зависимости:

Вы можете начать работу ТОЛЬКО после того, как завершит:
- **Человек 3** (первая часть client.py)

---

## ✅ Задача 1: Дополнить класс PingPongClient

Человек 3 уже создал файл `src/client.py` с первыми методами. Вам нужно ДОПОЛНИТЬ этот файл следующими методами:

### 1. Метод read_response

```python
def read_response(self) -> str:
    """
    Шаг 3: Чтение ответа от сервера.

    Returns:
        Содержимое ответа от сервера

    Raises:
        FileAccessError: При ошибке чтения файла
        InvalidResponseError: При неверном формате ответа
    """
```

**Что делает:**
1. Меняет состояние на `ClientState.READING_RESPONSE`
2. Читает ответ: `response = self._read_file()`
3. Если response пустой - выбрасывает `InvalidResponseError("Empty response from server")`
4. Логирует: `f"Read response: {response}"`
5. Валидирует формат:
   - Проверяет что начинается с "SERVER_RESPONSE"
   - Разбивает по `|`: `parts = response.split("|")`
   - Проверяет что частей >= 4 и parts[1] == "pong"
   - Если формат неверный - выбрасывает `InvalidResponseError`
6. Возвращает строку ответа

**Формат ответа:** `SERVER_RESPONSE|pong|1|2025-11-29T13:55:05.479380`

---

### 2. Метод handle_error

```python
def handle_error(self, error: Exception, retry_count: int = 0) -> bool:
    """
    Шаг 4: Обработка ошибки.

    Args:
        error: Исключение, которое произошло
        retry_count: Текущий счетчик попыток

    Returns:
        True если нужно повторить попытку, False если нет
    """
```

**Что делает:**
1. Меняет состояние на `ClientState.ERROR`
2. Логирует ошибку: `f"ERROR: {type(error).__name__}: {error}"`
3. Если `retry_count < self.max_retries`:
   - Логирует: `f"Retry {retry_count + 1}/{self.max_retries}"`
   - Делает паузу: `time.sleep(1)`
   - Возвращает `True` (нужно повторить)
4. Иначе:
   - Логирует: "Max retries reached. Giving up."
   - Возвращает `False` (не повторять)

---

### 3. Метод cleanup

```python
def cleanup(self):
    """Очистка общего файла после завершения."""
```

**Что делает:**
- Вызывает `self._remove_file()`

---

### 4. Метод send_ping

```python
def send_ping(self) -> Optional[str]:
    """
    Основной метод для отправки ping и получения pong.
    Реализует полный цикл согласно диаграмме состояний.

    Returns:
        Ответ от сервера или None при ошибке
    """
```

**Что делает:**
1. Инициализирует `retry_count = 0`
2. В цикле while `retry_count <= self.max_retries`:
   - В блоке try:
     - Создает запрос: `request = self.create_request()`
     - Отправляет: `self.send_request(request)`
     - Ожидает ответ: `self.wait_for_response()`
     - Читает ответ: `response = self.read_response()`
     - Меняет состояние на `ClientState.COMPLETED`
     - Логирует: "Ping-pong cycle completed successfully"
     - Возвращает `response`
   - В блоке except для `(CommunicationError, Exception)`:
     - Вызывает `should_retry = self.handle_error(e, retry_count)`
     - Если `not should_retry` - возвращает `None`
     - Увеличивает `retry_count += 1`
3. Возвращает `None` если все попытки исчерпаны

---

## ✅ Задача 2: Создать приложение client_app.py

Создайте точку входа для клиента:

```python
"""
Точка входа для клиентского приложения.
Демонстрирует использование PingPongClient для отправки ping-запросов.
"""

import time
import sys

from src.client import PingPongClient


def main():
    """Главная функция для запуска клиента."""
    print("=" * 60)
    print("PING-PONG CLIENT")
    print("=" * 60)

    client = PingPongClient(shared_file="shared_communication.txt", timeout=30)

    try:
        # Отправка нескольких ping-запросов
        num_pings = 5
        successful = 0

        for i in range(num_pings):
            print(f"\n--- Ping #{i+1}/{num_pings} ---")
            response = client.send_ping()

            if response:
                successful += 1
                print(f"SUCCESS: Received response: {response}")
            else:
                print(f"FAILED: No response received")

            if i < num_pings - 1:
                print("Waiting 2 seconds before next ping...")
                time.sleep(2)

        print(f"\n{'=' * 60}")
        print(f"Results: {successful}/{num_pings} successful")
        print(f"{'=' * 60}")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        sys.exit(1)
    finally:
        client.cleanup()


if __name__ == "__main__":
    main()
```

**Что делает приложение:**
1. Создает клиента с таймаутом 30 секунд
2. Отправляет 5 ping-запросов
3. Между запросами ждет 2 секунды
4. Выводит статистику успешных/неуспешных запросов
5. В конце очищает файл

---

## ✅ Критерии приемки:

### Для src/client.py:
- [ ] Метод `read_response` валидирует формат ответа
- [ ] При неверном формате выбрасывается `InvalidResponseError`
- [ ] Метод `handle_error` реализует retry-логику
- [ ] Метод `send_ping` выполняет полный цикл ping-pong
- [ ] При ошибке делается до 3 попыток повтора
- [ ] Все методы имеют docstring

### Для client_app.py:
- [ ] Файл создан в корне проекта
- [ ] Отправляет 5 ping-запросов
- [ ] Между запросами пауза 2 секунды
- [ ] Выводит статистику в конце
- [ ] Обрабатывает Ctrl+C (KeyboardInterrupt)
- [ ] В finally вызывается cleanup

---

## 🧪 Как протестировать:

### Тест 1: Запуск без сервера (должен получить таймаут)

```bash
python client_app.py
```

Ожидаемый результат:
```
============================================================
PING-PONG CLIENT
============================================================

--- Ping #1/5 ---
[HH:MM:SS.mmm] [CLIENT] State transition: idle -> creating_request
[HH:MM:SS.mmm] [CLIENT] Created request: CLIENT_REQUEST|ping|1|...
[HH:MM:SS.mmm] [CLIENT] Request sent to file: shared_communication.txt
[HH:MM:SS.mmm] [CLIENT] State transition: creating_request -> waiting_response
[HH:MM:SS.mmm] [CLIENT] Waiting for response (timeout: 30s)...
[HH:MM:SS.mmm] [CLIENT] State transition: waiting_response -> error
[HH:MM:SS.mmm] [CLIENT] ERROR: TimeoutError: No response received within 30 seconds
[HH:MM:SS.mmm] [CLIENT] Retry 1/3
...
FAILED: No response received

============================================================
Results: 0/5 successful
============================================================
```

### Тест 2: Запуск с сервером

**Терминал 1:**
```bash
python server_app.py
```

**Терминал 2:**
```bash
python client_app.py
```

Ожидаемый результат:
```
============================================================
PING-PONG CLIENT
============================================================

--- Ping #1/5 ---
[HH:MM:SS.mmm] [CLIENT] State transition: idle -> creating_request
[HH:MM:SS.mmm] [CLIENT] Created request: CLIENT_REQUEST|ping|1|...
...
[HH:MM:SS.mmm] [CLIENT] State transition: reading_response -> completed
[HH:MM:SS.mmm] [CLIENT] Ping-pong cycle completed successfully
SUCCESS: Received response: SERVER_RESPONSE|pong|1|...

--- Ping #2/5 ---
...

============================================================
Results: 5/5 successful
============================================================
```

---

## 📚 Полезные ссылки:

- [try/except в Python](https://docs.python.org/3/tutorial/errors.html#handling-exceptions)
- [sys.exit()](https://docs.python.org/3/library/sys.html#sys.exit)
- [finally блок](https://docs.python.org/3/tutorial/errors.html#defining-clean-up-actions)
