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

            if response:
                # Ответ получен успешно (уже выведен в логах)
                pass
            else:
                # Не удалось получить ответ
                pass

    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
    except Exception as e:
        print(f"\nОшибка: {e}")
        sys.exit(1)
    finally:
        client.cleanup()


if __name__ == "__main__":
    main()
