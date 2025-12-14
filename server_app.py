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
