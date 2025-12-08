# Запуск клиента

import time
import sys
from src.client import PingPongClient


def main():
    print("=" * 60)
    print("PING-PONG CLIENT")
    print("=" * 60)

    client = PingPongClient(shared_file="shared_communication.txt", timeout=30)

    try:
        # Отправляем несколько ping-запросов
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
