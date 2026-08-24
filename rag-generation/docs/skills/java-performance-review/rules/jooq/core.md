# jOOQ Performance Rules

Version: 1.0

---

# JOOQ-001

## Название

fetch() вместо fetchLazy()

Severity

High

Confidence

High

Category

Memory

---

### Что искать

```java
dsl.select(...)
   .fetch();
```

для потенциально больших выборок.

---

### Почему плохо

Весь ResultSet загружается в память.

---

### Последствия

- высокий Heap
- Full GC
- OutOfMemoryError

---

### Исправление

```java
fetchLazy()
```

или

```java
fetchStream()
```

---

Expected Improvement

High

---

# JOOQ-002

## Название

fetch()

без LIMIT

Severity

Critical

---

Что искать

Большой SELECT

↓

fetch()

---

Почему

Читается вся таблица.

---

# JOOQ-003

## Название

fetchOne()

без гарантии уникальности

Severity

Medium

---

Почему

jOOQ проверяет,

что запись действительно одна.

---

# JOOQ-004

## Название

fetchAny()

при необходимости детерминированного результата

Severity

Low

---

Проверить корректность бизнес-логики.

---

# JOOQ-005

## Название

DSLContext используется внутри цикла

Severity

Critical

---

Что искать

```java
for (...) {

dsl.select(...)

}
```

---

Почему

SQL-аналог N+1.

---

Related

JAVA-001

SQL-024

---

# JOOQ-006

## Название

insertInto()

в цикле

Severity

Critical

---

Исправление

BatchInsert.

---

# JOOQ-007

## Название

update()

в цикле

Severity

Critical

---

Исправление

Bulk UPDATE.

---

# JOOQ-008

## Название

delete()

в цикле

Severity

Critical

---

Исправление

Bulk DELETE.

---

# JOOQ-009

## Название

Batch API не используется

Severity

Critical

---

Что искать

Тысячи INSERT

по одному.

---

Исправление

```java
dsl.batch(...)
```

---

# JOOQ-010

## Название

batchStore()

не используется

Severity

High

---

# JOOQ-011

## Название

IN

с тысячами значений

Severity

Medium

---

Исправление

Temporary Table

JOIN

UNNEST.

---

# JOOQ-012

## Название

OFFSET Pagination

Severity

Critical

---

Исправление

Seek API.

---

### Что искать

```java
.offset(...)
```

---

Related

SQL-004

---

# JOOQ-013

## Название

Не используется seek()

Severity

High

---

Почему

Seek Pagination

значительно быстрее OFFSET.

---

# JOOQ-014

## Название

SELECT *

Severity

High

---

Что искать

```java
select()
```

без перечисления полей.

---

# JOOQ-015

## Название

selectFrom()

для широкой таблицы

Severity

Medium

---

Почему

Возвращаются все столбцы.

---

# JOOQ-016

## Название

Record используется вместо DTO

Severity

Medium

---

Почему

Передается больше данных,

чем требуется.

---

# JOOQ-017

## Название

mapping()

не используется

Severity

Low

---

Рекомендация

Использовать

типизированное отображение.

---

# JOOQ-018

## Название

fetchInto()

для большого ResultSet

Severity

Medium

---

Почему

Создаются тысячи объектов.

---

# JOOQ-019

## Название

Streaming отсутствует

Severity

High

---

Исправление

```java
fetchStream()
```

---

# JOOQ-020

## Название

Cursor не закрывается

Severity

Critical

---

Последствия

Утечки соединений.

---

# JOOQ-021

## Название

fetchLazy()

без try-with-resources

Severity

Critical

---

Почему

Cursor остается открытым.

---

# JOOQ-022

## Название

Не указан fetchSize

Severity

High

---

Почему

Драйвер может загрузить весь ResultSet.

---

# JOOQ-023

## Название

Сложный SQL строится динамически

Severity

Medium

---

Почему

Труднее анализировать планы выполнения.

---

# JOOQ-024

## Название

Повторное построение одинакового запроса

Severity

Low

---

Почему

Лишние allocations.

---

# JOOQ-025

## Название

JSON сериализация внутри fetch()

Severity

Medium

---

Почему

Лишняя CPU-нагрузка.

---

# JOOQ-026

## Название

Массовый UPSERT

без batching

Severity

High

---

# JOOQ-027

## Название

Не используется Common Table Expression

Severity

Low

---

Рекомендация

Рассмотреть CTE

для сложной логики.

---

# JOOQ-028

## Название

Не используется MULTISET

для сложных графов

Severity

Medium

---

Почему

Часто позволяет избежать N+1.

---

# JOOQ-029

## Название

Вложенные SELECT

вместо JOIN

Severity

High

---

# JOOQ-030

## Название

Нет анализа generated SQL

Severity

Info

---

Рекомендуется проверить

реальный SQL,

который генерирует jOOQ,

и выполнить

EXPLAIN ANALYZE

для наиболее тяжелых запросов.

---

# При анализе jOOQ проверить

- fetch()
- fetchLazy()
- fetchStream()
- Cursor
- fetchSize
- batch()
- batchStore()
- seek()
- offset()
- limit()
- select()
- selectFrom()
- mapping()
- fetchInto()
- MULTISET
- CTE
- generated SQL

---

# Наиболее критичные правила

JOOQ-002

JOOQ-005

JOOQ-006

JOOQ-007

JOOQ-008

JOOQ-009

JOOQ-012

JOOQ-020

JOOQ-021

JOOQ-022

Эти проблемы чаще всего приводят к высокому потреблению памяти, большому количеству SQL-запросов и плохой масштабируемости приложений, использующих jOOQ.