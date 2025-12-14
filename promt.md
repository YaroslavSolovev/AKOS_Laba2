# Inter-Process Communication via File Descriptor

Based on the requirements described, here's an OOP implementation in Python for client-server messaging using a shared file:

## Server Application

```python
import os
import time
from abc import ABC, abstractmethod

class Server(ABC):
    def __init__(self, filename):
        self.filename = filename
        self.running = True
    
    def wait_request(self):
        """Ожидает запрос от клиента"""
        while self.running:
            try:
                if os.path.exists(self.filename):
                    with open(self.filename, 'r') as f:
                        message = f.read().strip()
                    if message == "ping":
                        return message
            except Exception as e:
                self.handle_error(e)
            time.sleep(0.1)
    
    def process_request(self, message):
        """Обработка запроса"""
        return "pong"
    
    def send_response(self, response):
        """Отправка ответа клиенту"""
        try:
            with open(self.filename, 'w') as f:
                f.write(response)
        except Exception as e:
            self.handle_error(e)
    
    def handle_error(self, error):
        """Обработка ошибки"""
        print(f"Server error: {error}")
    
    def run(self):
        """Основной цикл сервера"""
        while self.running:
            request = self.wait_request()
            response = self.process_request(request)
            self.send_response(response)
```

## Client Application

```python
import os
import time

class Client:
    def __init__(self, filename):
        self.filename = filename
    
    def create_request(self):
        """Создает запрос"""
        return "ping"
    
    def send_request(self, request):
        """Отправляет запрос серверу"""
        try:
            with open(self.filename, 'w') as f:
                f.write(request)
        except Exception as e:
            self.handle_error(e)
    
    def wait_response(self, timeout=5):
        """Ожидает ответ от сервера"""
        start = time.time()
        while time.time() - start < timeout:
            time.sleep(0.1)
        return True
    
    def read_response(self):
        """Читает ответ от сервера"""
        try:
            with open(self.filename, 'r') as f:
                return f.read().strip()
        except Exception as e:
            self.handle_error(e)
            return None
    
    def handle_error(self, error):
        """Обработка ошибки"""
        print(f"Client error: {error}")
    
    def run(self):
        """Основной цикл клиента"""
        request = self.create_request()
        self.send_request(request)
        self.wait_response()
        response = self.read_response()
        print(f"Response: {response}")
```

Эта реализация следует описанной архитектуре с отдельными методами для каждого этапа взаимодействия.
