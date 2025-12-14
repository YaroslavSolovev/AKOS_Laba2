# Person 4: Клиент (часть 2) + интерактивное приложение

## Ответственность
Завершение класса клиента и создание интерактивной точки входа

## Файлы для реализации
- `src/client.py` (продолжение - оставшиеся методы)
- `client_app.py`

## Задачи

### 1. Завершить класс `PingPongClient`

#### `read_response(self) -> str`
- Изменить состояние на `READING_RESPONSE`
- Прочитать ответ через `self._read_file()`
- Если пусто - бросить `InvalidResponseError("Пустой ответ")`
- **Проверка на ошибку от сервера:**
  - Если ответ начинается с `"ERROR:"` - извлечь сообщение и бросить исключение
  - `raise InvalidResponseError(f"Сервер: {error_msg}")`
- Логировать: `self._log(f"< {response}")`
- Вернуть ответ

#### `handle_error(self, error: Exception)`
- Изменить состояние на `ERROR`
- Логировать: `self._log(f"Ошибка: {error}")`
- **БЕЗ retry логики** - просто выводим ошибку

#### `cleanup(self)`
- Вызвать `self._remove_file()`

#### `send_message(self, message: str) -> Optional[str]`
Главный метод - полный цикл:
```python
def send_message(self, message: str) -> Optional[str]:
    try:
        # Создание и отправка запроса
        request = self.create_request(message)
        self.send_request(request)

        # Ожидание и чтение ответа (передаем запрос чтобы не читать его же)
        self.wait_for_response(request)
        response = self.read_response()

        self._change_state(ClientState.COMPLETED)
        return response

    except (CommunicationError, Exception) as e:
        self.handle_error(e)
        return None
```

### 2. Создать интерактивное приложение `client_app.py`

**Особенности:**
- Пользователь вводит команды в консоли
- Команды выхода: `exit`, `quit`, `q`
- Интерактивный цикл с `input()`

```python
"""
Клиентское приложение для ping-pong взаимодействия.
Интерактивный режим: пользователь вводит сообщения в консоли.
"""

import sys
from src.client import PingPongClient


def main():
    """Главная функция для запуска клиента."""
    print("=" * 60)
    print("PING-PONG CLIENT")
    print("Введите 'ping' для отправки запроса")
    print("Введите 'exit' или 'quit' для выхода")
    print("=" * 60)

    client = PingPongClient(shared_file="shared_communication.txt", timeout=10)

    try:
        while True:
            # Ввод от пользователя
            user_input = input("\n> ").strip()

            # Проверка команды выхода
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Выход...")
                break

            # Если пустая строка - пропускаем
            if not user_input:
                continue

            # Отправка сообщения
            response = client.send_message(user_input)

    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
    except Exception as e:
        print(f"\nОшибка: {e}")
        sys.exit(1)
    finally:
        client.cleanup()


if __name__ == "__main__":
    main()
```

## Критерии приемки
- Обработка ошибок от сервера работает корректно
- Интерактивный режим: пользователь вводит команды
- Команды выхода работают
- Graceful shutdown (cleanup в finally)
- Понятные сообщения об ошибках
- Код следует PEP 8

## Объем работы
~100 строк кода

## Использование
```
> ping
[CLIENT] > ping
[CLIENT] < pong

> hello
[CLIENT] > hello
[CLIENT] Ошибка: Сервер: ожидается 'ping'

> exit
Выход...
```
