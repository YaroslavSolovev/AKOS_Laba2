"""
Сервер для ping-pong взаимодействия через файл
"""

import os
import sys
import time

SHARED_FILE = "shared_communication.txt"
POLL_INTERVAL = 0.1


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


def clear_file():
    """Очистка файла"""
    try:
        with open(SHARED_FILE, 'w', encoding='utf-8') as f:
            f.write("")
    except IOError:
        pass


def remove_file():
    """Удаление файла"""
    try:
        if os.path.exists(SHARED_FILE):
            os.remove(SHARED_FILE)
    except IOError:
        pass


def process_request(request):
    """Обработка запроса"""
    if request.lower() == "ping":
        return "pong"
    else:
        raise ValueError(f"Неверный запрос: '{request}'")


def handle_single_request():
    """Обработка одного запроса"""
    try:
        # Чтение запроса
        request = read_file()
        if not request:
            return False

        print(f"[SERVER] < {request}")

        # Обработка
        response = process_request(request)

        time.sleep(0.05)

        # Отправка ответа
        write_file(response)
        print(f"[SERVER] > {response}")

        # Даем клиенту время прочитать
        time.sleep(0.2)

        # Очистка файла
        clear_file()

        return True

    except ValueError as e:
        # Неверный запрос
        print(f"[SERVER] Ошибка: {e}")
        error_msg = "ERROR: ожидается 'ping'"
        try:
            write_file(error_msg)
            print(f"[SERVER] > {error_msg}")
            time.sleep(0.2)
            clear_file()
        except:
            pass
        return False

    except Exception as e:
        print(f"[SERVER] Ошибка: {e}")
        return False


def main():
    print("=" * 60)
    print("PING-PONG SERVER")
    print("Ожидание запросов от клиента...")
    print("Нажмите Ctrl+C для остановки")
    print("=" * 60)

    remove_file()
    requests_count = 0

    try:
        while True:
            if handle_single_request():
                requests_count += 1
            else:
                time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\n[SERVER] Остановка сервера...")
    except Exception as e:
        print(f"\nОшибка: {e}")
        sys.exit(1)
    finally:
        remove_file()
        print(f"[SERVER] Обработано запросов: {requests_count}")
        print("=" * 60)
        print("Сервер остановлен")
        print("=" * 60)


if __name__ == "__main__":
    main()
