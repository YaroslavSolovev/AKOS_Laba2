# Person 1: Базовая инфраструктура и ошибки

## Ответственность
Создание базового класса и системы обработки ошибок

## Файлы для реализации
- `src/base_communicator.py`
- `src/errors/__init__.py`
- `src/errors/communication_error.py`
- `src/errors/file_access_error.py`

## Задачи

### 1. Создать абстрактный базовый класс `BaseCommunicator`

**Методы для реализации:**

#### `__init__(shared_file: str)`
- Сохранить путь к файлу в `self.shared_file`
- Определить роль из имени класса: `self._role = self.__class__.__name__.replace("PingPong", "").upper()`

#### `_log(message: str)`
- Простое логирование: `print(f"[{self._role}] {message}")`
- **БЕЗ временных меток** - только роль и сообщение

#### `_change_state(new_state)`
- Абстрактный метод (помечен `@abstractmethod`)
- Реализация в дочерних классах

#### `_read_file() -> Optional[str]`
- Чтение из файла
- Возвращает содержимое или `None` если файл не существует/пуст
- IOError преобразовывать в `FileAccessError`

#### `_write_file(content: str)`
- Запись в файл с `os.fsync()` для гарантированной синхронизации
- IOError преобразовывать в `FileAccessError`

#### `_clear_file()`
- Очистка содержимого файла (запись пустой строки)
- IOError преобразовывать в `FileAccessError`

#### `_remove_file()`
- Удаление файла
- **НЕ бросает исключение** - ошибки игнорируются

#### `_file_exists() -> bool`
- Проверка существования файла
- Возвращает `True/False`

### 2. Создать исключения

**CommunicationError** (`src/errors/communication_error.py`):
```python
class CommunicationError(Exception):
    """Базовый класс для всех ошибок коммуникации."""
    pass
```

**FileAccessError** (`src/errors/file_access_error.py`):
```python
from src.errors.communication_error import CommunicationError

class FileAccessError(CommunicationError):
    """Ошибка доступа к общему файлу."""
    pass
```

### 3. Создать `__init__.py` в пакете errors
```python
from src.errors.communication_error import CommunicationError
from src.errors.file_access_error import FileAccessError

__all__ = ['CommunicationError', 'FileAccessError']
```

## Критерии приемки
- Все методы имеют docstring
- Код следует PEP 8
- Класс наследуется от ABC
- Абстрактные методы помечены `@abstractmethod`
- Логирование БЕЗ временных меток (только роль + сообщение)
- IOError обрабатываются корректно

## Объем работы
~100 строк кода
