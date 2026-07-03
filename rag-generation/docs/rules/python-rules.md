# Python правила кодирования

## Именование
Классы пишутся в PascalCase. Функции, методы и переменные — в snake_case.
Константы — в UPPER_SNAKE_CASE. Пакеты и модули — короткие lower_snake_case.

## Типизация
Использовать type hints (PEP 484) для всех публичных функций и методов.
Для сложных типов — `from typing import ...` (List, Dict, Optional и т.д.).

## Форматирование
- отступы: 4 пробела;
- макс. длина строки: 100 символов;
- импорты: стандартная библиотека → сторонние → внутренние, разделены пустой строкой.

## Тестирование
- pytest, тесты лежат в `tests/unit/` и `tests/integration/`;
- фикстуры вынесены в `conftest.py`;
- для mock — `unittest.mock` или `pytest-mock`.

## Структура проекта
```
project/
├── src/
│   ├── __init__.py
│   ├── module/
│   │   ├── __init__.py
│   │   ├── service.py
│   │   └── models.py
│   └── main.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── pyproject.toml
└── README.md
```

## Инструменты
- Менеджер зависимостей: uv или poetry;
- Линтер: ruff;
- Форматтер: ruff format;
- type checker: mypy.
