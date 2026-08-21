# PostgreSQL Index & Execution Plan Rules

Version: 1.0

---

# PG-001

## Название

Seq Scan большой таблицы

Severity

Critical

Confidence

High

Category

Execution Plan

---

### Что искать

EXPLAIN

EXPLAIN ANALYZE

```
Seq Scan
```

---

### Почему плохо

PostgreSQL читает всю таблицу.

При росте данных время выполнения растет линейно.

---

### Последствия

- высокий IO
- высокий CPU
- рост latency
- перегрузка PostgreSQL

---

### Исправление

Создать подходящий индекс

или изменить запрос.

---

### Expected Improvement

Very High

---

# PG-002

## Название

Seq Scan горячей таблицы

Severity

Critical

---

Что искать

Seq Scan

для

orders

payments

events

messages

audit

или другой таблицы,

которая активно используется.

---

# PG-003

## Название

Missing Index

Severity

Critical

---

Что искать

WHERE

по колонке

без подходящего индекса.

---

Исправление

Создать индекс.

---

# PG-004

## Название

Неверный порядок колонок

в составном индексе

Severity

High

---

Что искать

```
INDEX(a,b,c)
```

а запрос

```
WHERE b=...
```

---

Почему

Индекс используется частично

или вообще не используется.

---

# PG-005

## Название

Слишком широкий индекс

Severity

Medium

---

Почему

Большой индекс

хуже помещается

в shared_buffers.

---

# PG-006

## Название

Избыточный индекс

Severity

Medium

---

Что искать

Несколько индексов,

покрывающих одинаковые поля.

---

Почему

Замедляются INSERT/UPDATE/DELETE.

---

# PG-007

## Название

Отсутствует Covering Index

Severity

High

---

Почему

Вместо

Index Only Scan

используется

Index Scan + Heap Fetch.

---

Исправление

Использовать INCLUDE.

---

# PG-008

## Название

Index Only Scan невозможен

Severity

Medium

---

Почему

Запрашиваются поля,

которых нет в индексе.

---

# PG-009

## Название

Bitmap Heap Scan

для горячего запроса

Severity

Medium

---

Почему

Часто означает,

что индекс недостаточно селективен.

---

# PG-010

## Название

Nested Loop

на больших таблицах

Severity

Critical

---

Что искать

```
Nested Loop
```

и большое число строк.

---

Почему

Стоимость растет квадратично.

---

Исправление

Проверить индексы

и статистику.

---

# PG-011

## Название

Hash Join

не помещается в память

Severity

High

---

Почему

Появляются Batch Hash Join

и запись на диск.

---

# PG-012

## Название

Sort Spill

Severity

High

---

Что искать

```
Sort Method: external merge
```

---

Почему

Сортировка выполняется на диске.

---

# PG-013

## Название

Materialize

для большого набора данных

Severity

Medium

---

Почему

Дополнительная память.

---

# PG-014

## Название

Rows Removed by Filter

Severity

High

---

Почему

Читается значительно больше строк,

чем реально используется.

---

# PG-015

## Название

Высокий Heap Fetch

Severity

Medium

---

Почему

Недостаточно покрывающий индекс.

---

# PG-016

## Название

Низкая селективность индекса

Severity

Medium

---

Что искать

Индекс

по boolean

или колонке

с малым количеством уникальных значений.

---

# PG-017

## Название

Функция делает индекс бесполезным

Severity

Critical

---

Что искать

```
LOWER()

DATE()

CAST()

COALESCE()
```

в WHERE.

---

# PG-018

## Название

Отсутствует Partial Index

Severity

Medium

---

Что искать

```
status='ACTIVE'
```

в большинстве запросов.

---

Исправление

Partial Index.

---

# PG-019

## Название

GIN индекс отсутствует

для поиска

Severity

High

---

Что искать

LIKE

ILIKE

JSONB

ARRAY

Full Text Search.

---

# PG-020

## Название

BRIN не используется

для очень больших таблиц

Severity

Medium

---

Когда проверить

Логи

История

Телеметрия

Events.

---

# PG-021

## Название

EXPLAIN ANALYZE отсутствует

Severity

Info

---

Рекомендация

Для наиболее тяжелых запросов

получить

EXPLAIN ANALYZE

перед окончательными выводами.

---

# PG-022

## Название

Autovacuum не успевает

Severity

High

---

Признаки

Большое количество Dead Tuples

или постоянно растущие таблицы.

---

# PG-023

## Название

Index Bloat

Severity

Medium

---

Почему

Размер индекса

значительно превышает необходимый.

---

# PG-024

## Название

Table Bloat

Severity

High

---

Последствия

Рост времени Seq Scan

и Index Scan.

---

# PG-025

## Название

Fillfactor по умолчанию

для активно обновляемой таблицы

Severity

Medium

---

Почему

Увеличивается Page Split.

---

# PG-026

## Название

Слишком много индексов

Severity

Medium

---

Почему

Каждый INSERT

UPDATE

DELETE

обновляет все индексы.

---

# PG-027

## Название

Индекс не используется

Severity

Low

---

Рекомендация

Проверить возможность удаления

неиспользуемого индекса.

---

# PG-028

## Название

Shared Buffers неэффективно используются

Severity

Info

---

Требуется ручная проверка

метрик PostgreSQL.

---

# PG-029

## Название

Плохая статистика планировщика

Severity

High

---

Признаки

Сильное расхождение

между Estimated Rows

и Actual Rows.

---

Исправление

ANALYZE

или настройка autovacuum.

---

# PG-030

## Название

Нет ручной проверки Execution Plan

Severity

Info

---

Если репозиторий содержит сложные SQL,

рекомендовать проверить вручную:

- EXPLAIN
- EXPLAIN ANALYZE
- BUFFERS
- WAL
- Timing
- Rows
- Loops
- Planning Time
- Execution Time

---

# При анализе PostgreSQL всегда проверять

- Seq Scan
- Index Scan
- Index Only Scan
- Bitmap Scan
- Nested Loop
- Hash Join
- Merge Join
- Sort
- Materialize
- Buffers
- Heap Fetches
- Rows Removed by Filter
- Partial Index
- Covering Index
- Composite Index
- GIN
- GiST
- BRIN
- Fillfactor
- Bloat
- Autovacuum
- ANALYZE
- EXPLAIN ANALYZE

---

# Наиболее критичные правила

PG-001

PG-002

PG-003

PG-010

PG-017

PG-019

PG-022

PG-024

PG-029

Эти проблемы чаще всего приводят к деградации PostgreSQL под высокой нагрузкой и должны иметь высокий приоритет при анализе.