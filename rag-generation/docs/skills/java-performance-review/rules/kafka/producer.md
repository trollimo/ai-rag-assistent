# Kafka Producer Performance Rules

Version: 1.0

---

# KAFKA-001

## Название

Producer без batching

Severity

Critical

Confidence

High

Category

Producer

---

### Что искать

Producer отправляет сообщения по одному.

```
send(record)
```

в горячем цикле.

---

### Почему плохо

Практически каждое сообщение становится отдельным сетевым запросом.

---

### Исправление

Настроить

- batch.size
- linger.ms

---

Expected Improvement

Very High

---

# KAFKA-002

## Название

linger.ms = 0

Severity

High

---

Почему

Producer почти не формирует batch.

---

Рекомендация

Проверить возможность использования

```
linger.ms=5..20
```

---

# KAFKA-003

## Название

batch.size слишком маленький

Severity

Medium

---

Почему

Пакеты получаются маленькими.

Растет количество сетевых запросов.

---

# KAFKA-004

## Название

compression.type отсутствует

Severity

High

---

Что искать

Нет настройки

```
compression.type
```

---

Исправление

Рассмотреть

```
lz4

snappy

zstd
```

---

# KAFKA-005

## Название

gzip используется для сообщений высокой частоты

Severity

Medium

---

Почему

Высокая нагрузка CPU.

---

# KAFKA-006

## Название

acks=all без необходимости

Severity

Medium

---

Почему

Максимальная надежность,

но увеличивается latency.

---

Проверить требования бизнеса.

---

# KAFKA-007

## Название

acks=0

Severity

High

---

Почему

Высокий риск потери сообщений.

---

# KAFKA-008

## Название

Idempotence отключен

Severity

High

---

Что искать

Нет

```
enable.idempotence=true
```

---

Почему

Повторные отправки могут создавать дубликаты.

---

# KAFKA-009

## Название

max.in.flight.requests слишком большой

Severity

Medium

---

Почему

Возможна потеря порядка сообщений.

---

# KAFKA-010

## Название

Producer создается часто

Severity

Critical

---

Что искать

```
new KafkaProducer()
```

в методах

или циклах.

---

Почему

Создание Producer дорого.

---

Исправление

Singleton.

---

# KAFKA-011

## Название

flush()

после каждого send()

Severity

Critical

---

Почему

Полностью отключает batching.

---

# KAFKA-012

## Название

send().get()

Severity

Critical

---

Что искать

```
producer.send(...).get()
```

---

Почему

Асинхронная отправка превращается в синхронную.

---

# KAFKA-013

## Название

Большие сообщения

Severity

High

---

Что проверить

Размер сообщений

сотни КБ

или мегабайты.

---

# KAFKA-014

## Название

JSON сериализация большого объекта

Severity

Medium

---

Почему

Высокая CPU-нагрузка.

---

# KAFKA-015

## Название

Повторная сериализация одинаковых объектов

Severity

Low

---

# KAFKA-016

## Название

Producer используется внутри транзакции БД

Severity

Critical

---

Почему

Длинные транзакции.

Высокая задержка commit.

---

Исправление

Outbox Pattern.

---

Related

PG-033

---

# KAFKA-017

## Название

Retry Storm

Severity

Critical

---

Что искать

Большое число retries

без backoff.

---

Почему

При деградации брокера

нагрузка возрастает лавинообразно.

---

# KAFKA-018

## Название

delivery.timeout.ms слишком большой

Severity

Medium

---

Почему

Ошибки обнаруживаются слишком поздно.

---

# KAFKA-019

## Название

Producer публикует синхронно несколько топиков

Severity

Medium

---

Почему

Растет время ответа.

---

# KAFKA-020

## Название

Producer может ограничивать масштабирование сервиса

Severity

Critical

---

Если обнаружены одновременно

- send().get()
- flush()
- нет batching
- producer внутри транзакции
- большие сообщения

следует отметить

**высокий риск деградации производительности и горизонтального масштабирования.**

---

# Проверить дополнительно

- batch.size
- linger.ms
- compression.type
- enable.idempotence
- acks
- retries
- retry.backoff.ms
- delivery.timeout.ms
- request.timeout.ms
- max.in.flight.requests
- message.max.bytes
- producer reuse

---

# Наиболее критичные правила

KAFKA-001

KAFKA-010

KAFKA-011

KAFKA-012

KAFKA-016

KAFKA-017

KAFKA-020