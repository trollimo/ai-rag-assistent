# PostgreSQL Locking, MVCC & Transaction Rules

Version: 1.0

---

# PG-031

## Название

Долгая транзакция

Severity

Critical

Confidence

High

Category

Locking

---

### Что искать

- @Transactional вокруг большого объема кода
- REST внутри транзакции
- Kafka внутри транзакции
- Scheduler в одной транзакции
- Batch Job без commit

---

### Почему плохо

PostgreSQL использует MVCC.

Пока транзакция открыта:

- версии строк не удаляются
- растет количество dead tuples
- VACUUM не может очистить таблицу
- увеличивается WAL

---

### Последствия

- рост latency
- Table Bloat
- Index Bloat
- Autovacuum Lag
- увеличение размера базы

---

### Исправление

Максимально сокращать время жизни транзакции.

---

Related

SPR-001

HIB-049

---

# PG-032

## Название

REST внутри транзакции

Severity

Critical

---

Почему

Блокировки удерживаются во время сетевого ожидания.

---

# PG-033

## Название

Kafka publish внутри транзакции

Severity

Critical

---

Исправление

Outbox Pattern.

---

# PG-034

## Название

Batch Job одной транзакцией

Severity

Critical

---

Почему

Огромный rollback.

Большое количество блокировок.

---

Исправление

Chunk Processing.

---

# PG-035

## Название

Массовый UPDATE

Severity

Critical

---

Что искать

UPDATE

без ограничения объема.

---

Последствия

Длительные Row Lock.

---

# PG-036

## Название

Массовый DELETE

Severity

Critical

---

Почему

Большое количество Dead Tuples.

---

Исправление

Удалять пакетами.

---

# PG-037

## Название

Serializable Isolation без необходимости

Severity

High

---

Почему

Максимальное количество конфликтов.

---

Исправление

READ COMMITTED

или

REPEATABLE READ,

если достаточно.

---

# PG-038

## Название

SELECT FOR UPDATE

без необходимости

Severity

High

---

Почему

Увеличивает конкуренцию между транзакциями.

---

# PG-039

## Название

SELECT FOR UPDATE

по большой выборке

Severity

Critical

---

Последствия

Тысячи Row Lock.

---

# PG-040

## Название

SELECT FOR UPDATE

без индекса

Severity

Critical

---

Почему

Сначала выполняется Seq Scan,

затем блокируются строки.

---

# PG-041

## Название

Idle in Transaction

Severity

Critical

---

Что проверить

Если приложение открывает транзакцию,

но долго не выполняет SQL.

---

Последствия

MVCC деградирует.

---

# PG-042

## Название

Высокая конкуренция UPDATE

по одной строке

Severity

High

---

Пример

Счетчики

Баланс

Последний номер

Sequence Table.

---

Исправление

Шардирование

или

LongAdder-подобные техники.

---

# PG-043

## Название

Hot Row

Severity

High

---

Почему

Множество потоков обновляют одну запись.

---

# PG-044

## Название

Hot Table

Severity

Medium

---

Почему

Все операции идут по одной таблице.

---

# PG-045

## Название

Большое количество Dead Tuples

Severity

High

---

Признаки

Частые UPDATE

DELETE.

---

# PG-046

## Название

Autovacuum не успевает

Severity

Critical

---

Последствия

Рост размера таблиц

и времени запросов.

---

# PG-047

## Название

VACUUM блокируется длинными транзакциями

Severity

Critical

---

# PG-048

## Название

UPDATE неизменившихся данных

Severity

Medium

---

Почему

Создается новая версия строки,

хотя значения не изменились.

---

Исправление

Обновлять только изменившиеся поля.

---

# PG-049

## Название

Частый UPDATE больших JSONB

Severity

High

---

Почему

Перезаписывается практически весь объект.

---

# PG-050

## Название

Массовый UPSERT

Severity

High

---

Что искать

```
INSERT ...

ON CONFLICT
```

для миллионов строк.

---

Рекомендация

Проверить влияние на индексы и WAL.

---

# PG-051

## Название

Отсутствует lock timeout

Severity

High

---

Почему

Транзакции могут ждать бесконечно.

---

Исправление

Настроить

lock_timeout.

---

# PG-052

## Название

Отсутствует statement timeout

Severity

High

---

Почему

Один тяжелый запрос может надолго занять соединение.

---

# PG-053

## Название

Нет deadlock timeout

Severity

Medium

---

Рекомендация

Проверить настройки PostgreSQL.

---

# PG-054

## Название

Высокая конкуренция INSERT

Severity

Medium

---

Особенно

при последовательном ключе

и одном индексе.

---

# PG-055

## Название

Нет мониторинга блокировок

Severity

Info

---

Рекомендуется проверять

- pg_locks
- pg_stat_activity
- wait_event
- blocking PIDs

---

# PG-056

## Название

Отсутствует анализ WAL

Severity

Info

---

При высокой нагрузке проверить

- объем WAL
- checkpoints
- replication lag

---

# PG-057

## Название

Большие транзакции увеличивают WAL

Severity

High

---

Почему

Чем больше транзакция,

тем дороже commit и replication.

---

# PG-058

## Название

Частые COMMIT

Severity

Medium

---

Почему

Слишком маленькие batch

увеличивают накладные расходы.

---

# PG-059

## Название

Нет анализа wait events

Severity

Info

---

Рекомендуется проверить

- Lock
- IO
- BufferPin
- ClientRead
- ClientWrite

---

# PG-060

## Название

Возможна деградация масштабируемости

Severity

Critical

---

Если обнаружены одновременно

- долгие транзакции
- массовые UPDATE
- Hot Rows
- SELECT FOR UPDATE
- REST внутри @Transactional

следует сделать вывод:

**существует высокий риск деградации при горизонтальном масштабировании и росте конкурентной нагрузки.**

---

# При анализе PostgreSQL дополнительно проверить

- MVCC
- Row Locks
- Table Locks
- Deadlocks
- Long Transactions
- Idle in Transaction
- Autovacuum
- VACUUM
- WAL
- Hot Rows
- Hot Tables
- pg_locks
- pg_stat_activity
- wait_event
- statement_timeout
- lock_timeout
- SELECT FOR UPDATE

---

# Наиболее критичные правила

PG-031

PG-034

PG-035

PG-036

PG-039

PG-041

PG-046

PG-047

PG-060

Эти проблемы практически всегда становятся причиной деградации производительности и плохой масштабируемости PostgreSQL под высокой конкурентной нагрузкой.