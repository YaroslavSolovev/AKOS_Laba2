import os
import sys
import time

SHARED_FILE = "shared_communication.txt"
TIMEOUT = 10


def read_file():
    """Чтение из файла"""
    if not os.path.exists(SHARED_FILE):
        return None
    try:
        with open(SHARED_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            return content if content else None
    except IOError:
        return None


def write_file(content):
    """Запись в файл"""
    try:
        with open(SHARED_FILE, 'w', encoding='utf-8') as f:
            f.write(content + "\n")
            f.flush()
            os.fsync(f.fileno())
    except IOError as e:
        raise IOError(f"Ошибка записи: {e}")


def remove_file():
    """Удаление файла"""
    try:
        if os.path.exists(SHARED_FILE):
            os.remove(SHARED_FILE)
    except IOError:
        pass


def send_request(message):
    """Отправка запроса"""
    write_file(message)
    print(f"[CLIENT] > {message}")


def wait_response(sent_message):
    """Ожидание ответа от сервера"""
    start = time.time()
    while time.time() - start < TIMEOUT:
        content = read_file()
        # Проверяем что содержимое изменилось
        if content and content != sent_message:
            return content
        time.sleep(0.1)
    return None


def send_message(message):
    """Отправка сообщения и получение ответа"""
    try:
        # Отправка
        send_request(message)

        # Ожидание ответа
        response = wait_response(message)

        if not response:
            print("[CLIENT] Ошибка: Нет ответа от сервера")
            return None

        # Проверка на ошибку от сервера
        if response.startswith("ERROR:"):
            error_msg = response.replace("ERROR:", "").strip()
            print(f"[CLIENT] Ошибка: Сервер вернул {error_msg}")
            return None

        print(f"[CLIENT] < {response}")
        return response

    except Exception as e:
        print(f"[CLIENT] Ошибка: {e}")
        return None


def main():
    print("=" * 60)
    print("PING-PONG CLIENT")
    print("Введите 'ping' для отправки запроса")
    print("Введите 'exit' или 'quit' для выхода")
    print("=" * 60)

    try:
        while True:
            user_input = input("\n> ").strip()

            # Выход
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Выход...")
                break

            # Пропуск пустых строк
            if not user_input:
                continue

            # Отправка сообщения
            send_message(user_input)

    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
    except Exception as e:
        print(f"\nОшибка: {e}")
        sys.exit(1)
    finally:
        remove_file()


if __name__ == "__main__":
    main()
