# Kotlin правила кодирования

## Именование
Классы — PascalCase. Методы и переменные — camelCase.
Константы верхнего уровня — UPPER_SNAKE_CASE (`const val`).
Файлы `.kt` — PascalCase, одноимённо с главным классом внутри.

## Null safety
- использовать `val` по умолчанию, `var` — только когда нужно переприсваивание;
- избегать `!!` — использовать `?:`, `.let { }`, `.takeIf` и safe call `?.`;
- nullable-поля — только если null имеет бизнес-смысл.

## Форматирование
- отступы: 4 пробела;
- макс. длина строки: 120 символов;
- trailing comma — обязательна.

## Тестирование
- kotlin.test + JUnit 5;
- для mock — MockK (не Mockito);
- coroutines test — `runTest` из `kotlinx-coroutines-test`.

## Структура проекта
```
project/
├── src/
│   ├── main/kotlin/
│   │   ├── service/
│   │   ├── model/
│   │   └── Application.kt
│   └── test/kotlin/
│       ├── unit/
│       └── integration/
├── build.gradle.kts
└── README.md
```

## Инструменты
- Сборка: Gradle Kotlin DSL (`build.gradle.kts`);
- Линтер: detekt;
- Форматтер: ktlint / spotless;
- Coroutines + Flow для асинхронщины.
