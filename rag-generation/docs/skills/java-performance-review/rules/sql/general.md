# SQL Performance Rules

Version: 1.0

---

# SQL-001

## Название

SELECT *

Severity

High

Confidence

High

Category

Projection

---

### Что искать

```sql
SELECT *
```

---

### Почему плохо

Читаются все столбцы.

Даже если используются только 2-3 поля.

---

### Последствия

- лишний IO
- рост Network Traffic
- больше памяти
- невозможность Index Only Scan

---

### Исправление

Перечислить только необходимые поля.

---

### Исключения

Допустимо

- COUNT подзапросов нет
- маленькие lookup-таблицы
- ad-hoc SQL администратора

---

### Related

PG-021

HIB-016

---

# SQL-002

## Название

SELECT *

по большой таблице

Severity

Critical

---

Что искать

```
SELECT *
FROM orders
```

без LIMIT

без WHERE

---

Последствия

Полное чтение таблицы.

---

# SQL-003

## Название

Полное чтение таблицы

Severity

Critical

---

Что искать

```
FROM table
```

без

WHERE

LIMIT

FETCH

---

Почему

Table Scan.

---

# SQL-004

## Название

OFFSET Pagination

Severity

Critical

---

Что искать

```sql
OFFSET
```

---

Почему плохо

OFFSET 100000

означает

прочитать

100000 строк

и выбросить их.

---

Исправление

Keyset Pagination

Seek Method

---

Related

PG-041

REST-014

---

# SQL-005

## Название

COUNT(*)

для очень большой таблицы

Severity

High

---

Почему

Полное сканирование.

---

Исправление

При необходимости использовать приблизительный подсчет или агрегаты.

---

# SQL-006

## Название

COUNT(*)

в горячем запросе

Severity

High

---

Что искать

COUNT

выполняется

при каждом HTTP запросе.

---

# SQL-007

## Название

DISTINCT

без необходимости

Severity

Medium

---

Почему

Дополнительная сортировка

или Hash Aggregate.

---

# SQL-008

## Название

ORDER BY

без LIMIT

Severity

Medium

---

Почему

Сортируется весь набор данных.

---

# SQL-009

## Название

ORDER BY

не по индексу

Severity

High

---

Последствия

External Sort

Disk Sort.

---

# SQL-010

## Название

GROUP BY

по большому объему данных

Severity

High

---

Исправление

Предварительная агрегация

Materialized View.

---

# SQL-011

## Название

Коррелированный подзапрос

Severity

Critical

---

Что искать

```sql
SELECT ...

WHERE EXISTS (

SELECT ...

WHERE outer.id = inner.id
)
```

или

подзапрос,

выполняемый

для каждой строки.

---

Почему

Практически SQL-аналог N+1.

---

Исправление

JOIN

CTE

предварительная агрегация.

---

# SQL-012

## Название

IN

с большим количеством значений

Severity

Medium

---

Почему

Очень длинный список

ухудшает план выполнения.

---

Исправление

JOIN

Temporary Table

UNNEST.

---

# SQL-013

## Название

NOT IN

Severity

High

---

Почему

Может работать значительно хуже,

чем NOT EXISTS.

---

# SQL-014

## Название

LIKE '%text'

Severity

Critical

---

Что искать

```sql
LIKE '%abc'
```

---

Почему

Обычный индекс не используется.

---

Исправление

GIN

Trigram

Full Text Search

или изменить шаблон поиска.

---

Related

PG-031

---

# SQL-015

## Название

ILIKE '%text'

Severity

Critical

---

Почему

Та же проблема,

что и LIKE.

---

# SQL-016

## Название

Функция в WHERE

Severity

Critical

---

Что искать

```sql
WHERE LOWER(name)=...
```

```sql
WHERE DATE(created_at)=...
```

```sql
WHERE SUBSTRING(...)
```

---

Почему

Индекс перестает использоваться.

---

Исправление

Вычислять значение заранее

или использовать функциональный индекс.

---

# SQL-017

## Название

CAST в WHERE

Severity

High

---

Почему

Может отключить использование индекса.

---

# SQL-018

## Название

Неявное преобразование типов

Severity

High

---

Что искать

varchar = bigint

timestamp = text

---

Почему

Планировщик вынужден выполнять преобразования.

---

# SQL-019

## Название

UNION вместо UNION ALL

Severity

Medium

---

Почему

UNION удаляет дубликаты.

Это требует сортировки или Hash Aggregate.

---

# SQL-020

## Название

SELECT DISTINCT +

ORDER BY

Severity

High

---

Почему

Две дорогостоящие операции подряд.

---

# SQL-021

## Название

JOIN без условий фильтрации

Severity

High

---

Почему

Читается значительно больше строк,

чем необходимо.

---

# SQL-022

## Название

Избыточное количество JOIN

Severity

Medium

---

Что искать

8+

JOIN

в одном запросе.

---

Почему

План становится сложным,

возрастает вероятность неоптимального порядка соединений.

---

# SQL-023

## Название

LEFT JOIN,

который всегда INNER

Severity

Low

---

Исправление

Использовать INNER JOIN.

---

# SQL-024

## Название

SELECT в цикле приложения

Severity

Critical

---

Что искать

Одинаковый SQL,

выполняемый много раз

для разных параметров.

---

Почему

SQL-аналог N+1.

---

Related

JAVA-001

HIB-001

---

# SQL-025

## Название

Массовый UPDATE

через отдельные запросы

Severity

Critical

---

Исправление

Bulk UPDATE.

---

# SQL-026

## Название

Массовый DELETE

через отдельные запросы

Severity

Critical

---

Исправление

DELETE ... WHERE ...

---

# SQL-027

## Название

Большой IN вместо JOIN

Severity

Medium

---

# SQL-028

## Название

Подзапрос в SELECT

для каждой строки

Severity

Critical

---

Что искать

```sql
SELECT
(
   SELECT ...
)
```

---

Почему

Подзапрос выполняется

для каждой строки результата.

---

# SQL-029

## Название

CTE используется повторно

без необходимости

Severity

Medium

---

Почему

В некоторых СУБД

может материализоваться.

---

# SQL-030

## Название

Отсутствует LIMIT

для пользовательского поиска

Severity

Critical

---

Последствия

Запрос может вернуть

миллионы строк,

что приводит к высокой нагрузке на БД, сеть и приложение.

---

# Проверить дополнительно

- SELECT *
- LIMIT
- OFFSET
- FETCH
- DISTINCT
- GROUP BY
- ORDER BY
- HAVING
- EXISTS
- NOT EXISTS
- IN
- NOT IN
- UNION
- UNION ALL
- CTE
- Window Functions
- Correlated Subqueries
- Functions in WHERE
- CAST
- LIKE
- ILIKE
- JOIN
- Pagination
- Bulk UPDATE
- Bulk DELETE

---

# Наиболее критичные правила

SQL-002

SQL-003

SQL-004

SQL-011

SQL-014

SQL-015

SQL-016

SQL-024

SQL-025

SQL-026

SQL-028

SQL-030

Именно эти антипаттерны чаще всего становятся причиной высокой нагрузки на PostgreSQL и резкого роста времени ответа системы.