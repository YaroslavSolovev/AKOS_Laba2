# Запуск сервера

import sys
from src.server import PingPongServer


def main():
    print("=" * 60)
    print("PING-PONG SERVER")
    print("=" * 60)

    # Создаем сервер
    server = PingPongServer(
        shared_file="shared_communication.txt",
        poll_interval=0.1
    )

    try:
        # Запускаем (макс 10 запросов или Ctrl+C чтобы остановить)
        server.start(max_requests=10)

    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Server shutdown complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
