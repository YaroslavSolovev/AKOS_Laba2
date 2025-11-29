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
