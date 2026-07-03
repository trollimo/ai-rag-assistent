# Java правила кодирования

## Именование
Классы — PascalCase. Методы и переменные — camelCase.
Константы (`static final`) — UPPER_SNAKE_CASE. Пакеты — нижний регистр, без подчёркиваний.

## Форматирование
- отступы: 4 пробела;
- фигурные скобки — на той же строке (K&R style);
- макс. длина строки: 120 символов.

## Тестирование
- JUnit 5, тесты лежат в `tests/component/` и `tests/integration/`;
- для mock — Mockito;
- параметризованные тесты — `@ParameterizedTest`.

## Сборка и зависимости
- Maven или Gradle;
- `pom.xml` / `build.gradle` лежит в корне проекта;
- версии зависимостей вынесены в `properties` / `libs.versions.toml`.

## Структура проекта (Maven)
```
project/
├── src/
│   ├── main/java/  (group/artifact/module/)
│   │   ├── service/
│   │   ├── model/
│   │   ├── repository/
│   │   └── Application.java
│   └── test/java/
│       ├── unit/
│       └── integration/
├── pom.xml
└── README.md
```

## Инструменты
- Линтер: checkstyle;
- Форматтер: spotless (Google Java Format);
- Статический анализ: SpotBugs.
