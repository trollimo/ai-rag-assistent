# Liquibase & Database Schema Performance Rules

Version: 1.0

---

# LB-001

## Название

Таблица без Primary Key

Severity

Critical

Confidence

High

Category

Schema

---

### Что искать

```xml
<createTable>
```

или

```sql
CREATE TABLE
```

без

PRIMARY KEY

---

### Почему плохо

- ухудшается производительность JOIN
- невозможно эффективно ссылаться по FK
- появляются дубликаты

---

### Исправление

Создать Primary Key.

---

# LB-002

## Название

Foreign Key без индекса

Severity

Critical

---

### Что искать

```
addForeignKeyConstraint
```

или

```
FOREIGN KEY
```

без последующего

```
CREATE INDEX
```

---

### Почему плохо

JOIN

DELETE

UPDATE

родительской таблицы

становятся значительно медленнее.

---

### Исправление

Каждый FK проверить на наличие индекса.

---

Related

PG-003

---

# LB-003

## Название

Отсутствует индекс по часто используемому WHERE

Severity

Critical

---

Что искать

Колонки

по которым приложение

регулярно выполняет

WHERE

JOIN

ORDER BY

---

# LB-004

## Название

Неверный порядок полей

в составном индексе

Severity

High

---

Пример

```
INDEX(status, created_at)
```

при запросах

```
WHERE created_at=...
```

---

# LB-005

## Название

Дублирующиеся индексы

Severity

Medium

---

Почему

Каждый дополнительный индекс

замедляет

INSERT

UPDATE

DELETE.

---

# LB-006

## Название

Слишком широкий индекс

Severity

Medium

---

Что искать

Индекс

по большому количеству колонок.

---

# LB-007

## Название

UUID как Primary Key

Severity

Medium

---

Почему

Случайные значения

увеличивают Fragmentation B-Tree.

---

Рекомендация

Если допустимо —

рассмотреть BIGINT

или UUID v7.

---

# LB-008

## Название

VARCHAR(4000)

для коротких значений

Severity

Low

---

Почему

Проверить,

не завышен ли размер.

---

# LB-009

## Название

TEXT

для полей,

используемых в JOIN

Severity

Medium

---

Почему

Широкие строки

ухудшают производительность.

---

# LB-010

## Название

JSON вместо JSONB

(PostgreSQL)

Severity

Medium

---

Почему

JSONB

лучше индексируется.

---

# LB-011

## Название

JSONB

без GIN Index

Severity

High

---

Что искать

JSONB

используется

в WHERE.

---

# LB-012

## Название

BOOLEAN индексируется

Severity

Low

---

Почему

Часто имеет низкую селективность.

---

# LB-013

## Название

TIMESTAMP без индекса

Severity

Medium

---

Особенно

если используется

для сортировки

или диапазонов.

---

# LB-014

## Название

CREATE INDEX

без CONCURRENTLY

Severity

High

---

Когда проверять

Большие production таблицы.

---

Почему

Создание индекса

может блокировать запись.

---

# LB-015

## Название

ALTER TABLE

для большой таблицы

Severity

High

---

Рекомендация

Проверить,

не приведет ли миграция

к длительной блокировке.

---

# LB-016

## Название

NOT NULL

добавляется

без этапной миграции

Severity

High

---

Почему

На больших таблицах

может быть дорогостоящей операцией.

---

# LB-017

## Название

Добавление столбца

с DEFAULT

на большую таблицу

Severity

Medium

---

Рекомендация

Проверить версию PostgreSQL

и стратегию миграции.

---

# LB-018

## Название

Нет Partial Index

Severity

Medium

---

Что искать

status='ACTIVE'

deleted=false

tenant_id

используются постоянно.

---

# LB-019

## Название

Нет Covering Index

Severity

Medium

---

Исправление

Использовать INCLUDE.

---

# LB-020

## Название

Нет Partitioning

для быстрорастущих таблиц

Severity

High

---

Особенно

events

audit

history

logs

messages

telemetry

---

# LB-021

## Название

Архивные данные

не отделены

Severity

Medium

---

Почему

Рабочие запросы

сканируют историю.

---

# LB-022

## Название

Нет Retention Strategy

Severity

Medium

---

Что проверить

Логи

История

События

очищаются ли автоматически.

---

# LB-023

## Название

Слишком много индексов

Severity

Medium

---

Почему

Каждый индекс

замедляет запись.

---

# LB-024

## Название

Нет комментариев

к сложной миграции

Severity

Info

---

Упростит сопровождение.

---

# LB-025

## Название

Rollback отсутствует

Severity

Low

---

Что искать

Liquibase

без rollback.

---

# LB-026

## Название

Одна миграция

изменяет слишком много объектов

Severity

Medium

---

Почему

Сложнее откатывать

и анализировать проблемы.

---

# LB-027

## Название

Большая миграция

не разделена

на этапы

Severity

Medium

---

# LB-028

## Название

Миграция может препятствовать масштабированию

Severity

High

---

Если обнаружены

- блокирующие ALTER TABLE
- CREATE INDEX без CONCURRENTLY
- массовые UPDATE
- массовые DELETE

следует отметить

риск долгого запуска новых Pod.

---

# LB-029

## Название

Не найдены Helm Chart

Severity

Info

---

Если Helm отсутствует,

рекомендовать проверить вручную:

- запускаются ли Liquibase миграции каждым Pod;
- используется ли отдельный Job для миграций;
- есть ли защита от одновременного запуска миграций;
- корректно ли настроены readiness/liveness probes во время выполнения миграций;
- не блокирует ли длительная миграция rollout Deployment.

---

# LB-030

## Название

Schema требует ручной проверки

Severity

Info

---

Рекомендуется дополнительно проверить:

- EXPLAIN ANALYZE
- pg_stat_user_indexes
- pg_stat_statements
- autovacuum
- bloat
- fillfactor
- размер таблиц
- размер индексов
- hot tables
- slow queries

---

# При анализе Liquibase проверить

- PK
- FK
- Index
- Composite Index
- Partial Index
- Covering Index
- GIN
- BRIN
- JSONB
- UUID
- Partitioning
- Retention
- Rollback
- Concurrent Index
- ALTER TABLE
- Migration Size
- Migration Order

---

# Наиболее критичные правила

LB-002

LB-003

LB-014

LB-015

LB-020

LB-028

Эти проблемы наиболее часто приводят к деградации производительности БД и проблемам при развертывании микросервисов в production.