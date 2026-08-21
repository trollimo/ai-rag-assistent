# Kafka Scalability & Cluster Performance Rules

Version: 1.0

---

# KAFKA-041

## Название

Недостаточное количество партиций

Severity

Critical

Confidence

High

Category

Scalability

---

### Что искать

Один Consumer Group

↓

Много экземпляров сервиса

↓

Количество Partition меньше количества Pod.

---

### Почему плохо

Часть Pod простаивает.

Горизонтальное масштабирование невозможно.

---

### Исправление

Увеличить количество Partition.

---

Expected Improvement

Very High

---

# KAFKA-042

## Название

Слишком много Partition

Severity

Medium

---

Почему

Каждая Partition требует ресурсов Broker.

Большое количество Partition увеличивает время Rebalance.

---

# KAFKA-043

## Название

Hot Partition

Severity

Critical

---

### Что искать

Partition Key

имеет низкую кардинальность.

Например

```
country

status

type

tenant=DEFAULT
```

---

### Почему плохо

Практически весь поток сообщений
попадает в одну Partition.

---

### Последствия

- один Consumer перегружен
- остальные простаивают
- рост Consumer Lag

---

### Исправление

Использовать более равномерный ключ.

---

# KAFKA-044

## Название

Случайный Partition Key

Severity

Medium

---

Почему

Нарушается локальность данных.

Может усложнить обработку.

---

# KAFKA-045

## Название

Partition Key не соответствует бизнес-сущности

Severity

Medium

---

Что проверить

Используется ли

```
orderId

userId

accountId

tenantId
```

если важен порядок обработки.

---

# KAFKA-046

## Название

Ordering зависит от нескольких Partition

Severity

High

---

Почему

Kafka гарантирует порядок
только внутри одной Partition.

---

# KAFKA-047

## Название

Количество Consumer больше количества Partition

Severity

High

---

Почему

Часть Consumer никогда
не будет получать сообщения.

---

# KAFKA-048

## Название

Большое количество Consumer Group

Severity

Medium

---

Почему

Broker вынужден обслуживать
каждую группу независимо.

---

# KAFKA-049

## Название

Частые Rebalance

Severity

High

---

Признаки

- короткий session timeout
- долгие обработчики
- частые рестарты

---

Последствия

Временная остановка обработки.

---

# KAFKA-050

## Название

Sticky Assignor не используется

Severity

Low

---

Рекомендация

Проверить возможность использования
Sticky Cooperative Assignor.

---

# KAFKA-051

## Название

Нет мониторинга Rebalance

Severity

Medium

---

Рекомендуется контролировать

- количество Rebalance
- длительность
- причины

---

# KAFKA-052

## Название

Нет мониторинга Partition Skew

Severity

Medium

---

Что проверить

Равномерность распределения сообщений
между Partition.

---

# KAFKA-053

## Название

Consumer Lag постоянно растет

Severity

Critical

---

Возможные причины

- медленный Consumer
- Hot Partition
- SQL
- HTTP
- GC

---

# KAFKA-054

## Название

Producer значительно быстрее Consumer

Severity

High

---

Почему

Lag будет увеличиваться
даже без ошибок.

---

# KAFKA-055

## Название

Нет ограничения скорости обработки

Severity

Medium

---

Рекомендация

Проверить

Backpressure

или Rate Limiting.

---

# KAFKA-056

## Название

Сообщения слишком большие

Severity

High

---

Последствия

- рост Network IO
- рост Latency
- увеличение времени Replication

---

# KAFKA-057

## Название

Нет Compression

Severity

Medium

---

Особенно критично
для больших сообщений.

---

# KAFKA-058

## Название

Broker может стать узким местом

Severity

High

---

Если обнаружены одновременно

- большие сообщения
- отсутствие batching
- большое количество Producer
- много Consumer Group

следует отметить риск
перегрузки Broker.

---

# KAFKA-059

## Название

Архитектура ограничивает горизонтальное масштабирование

Severity

Critical

---

Если обнаружены

- Hot Partition
- Ordering между Partition
- Stateful Consumer
- Shared State
- SQL внутри Consumer
- HTTP внутри Consumer

следует сделать вывод

**Архитектура Kafka ограничивает масштабирование сервиса.**

---

# KAFKA-060

## Название

Необходима ручная проверка Kafka Cluster

Severity

Info

---

Рекомендуется проверить

- Consumer Lag
- Partition Distribution
- ISR
- Under Replicated Partitions
- Offline Partitions
- Broker CPU
- Broker Memory
- Network IO
- Disk IO
- Request Latency
- Produce Latency
- Fetch Latency
- Rebalance Count
- Message Size
- Retention
- Log Compaction

---

# Проверить дополнительно

- Partition Count
- Replication Factor
- Consumer Groups
- Partition Key
- Lag
- ISR
- Rebalance
- Ordering
- Compression
- Throughput
- Broker Load
- Stateful Processing

---

# Наиболее критичные правила

KAFKA-041

KAFKA-043

KAFKA-046

KAFKA-047

KAFKA-053

KAFKA-058

KAFKA-059

Эти проблемы чаще всего приводят к тому, что Kafka-инфраструктура перестает масштабироваться при росте нагрузки, несмотря на увеличение числа экземпляров микросервисов.