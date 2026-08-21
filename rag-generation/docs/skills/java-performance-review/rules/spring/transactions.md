# Spring Transaction Performance Rules

Version: 1.0

---

# SPR-001

## Название

Внешний REST вызов внутри @Transactional

Severity

Critical

Confidence

High

---

### Что искать

```java
@Transactional
```

и внутри

```java
RestTemplate

WebClient.block()

FeignClient
```

---

### Почему плохо

Транзакция остается открытой во время сетевого ожидания.

Все ресурсы БД удерживаются значительно дольше.

---

### Последствия

- долгие транзакции
- блокировки
- рост connection pool
- рост lock wait
- снижение Throughput

---

### Исправление

REST выполнять

до открытия

или

после завершения

транзакции.

---

### Related

JAVA-002

HIB-011

PG-018

---

# SPR-002

## Название

Kafka publish внутри транзакции

Severity

Critical

---

Что искать

```java
@Transactional

kafkaTemplate.send(...)
```

---

Почему

Транзакция удерживается во время отправки сообщения.

---

Исправление

Transactional Event

Outbox Pattern

---

Related

KAFKA-012

ARCH-031

---

# SPR-003

## Название

ActiveMQ внутри транзакции

Severity

Critical

---

Исправление

Outbox

или

Transaction Synchronization

---

# SPR-004

## Название

Большая транзакция

Severity

Critical

---

Что искать

Одна транзакция

обрабатывает

тысячи записей.

---

Последствия

- большие rollback
- блокировки
- VACUUM задерживается
- рост WAL

---

Исправление

Chunk Processing

Batch

---

# SPR-005

## Название

@Transactional вокруг Scheduler

Severity

High

---

Почему

Огромная транзакция.

---

Исправление

Обрабатывать данными пакетами.

---

# SPR-006

## Название

@Transactional вокруг Batch Job

Severity

Critical

---

Исправление

Batch Size

100

500

1000

по ситуации.

---

# SPR-007

## Название

REQUIRES_NEW внутри цикла

Severity

Critical

---

Что искать

```
for (...)

@Transactional(REQUIRES_NEW)
```

---

Последствия

Тысячи отдельных транзакций.

---

# SPR-008

## Название

Чрезмерное использование REQUIRES_NEW

Severity

High

---

Почему

Каждая новая транзакция требует отдельного соединения.

---

# SPR-009

## Название

@Transactional на контроллере

Severity

High

---

Почему

HTTP входит в транзакцию.

---

Исправление

Транзакция

должна начинаться

в сервисном слое.

---

# SPR-010

## Название

@Transactional на приватном методе

Severity

Info

---

Почему

Spring Proxy

не работает.

---

# SPR-011

## Название

Самовызов @Transactional

Severity

Medium

---

Что искать

```
this.method()
```

---

Почему

Proxy обходится.

---

# SPR-012

## Название

readOnly отсутствует

Severity

Medium

---

Что искать

Методы чтения

без

```
readOnly=true
```

---

Почему

Hibernate выполняет лишнюю работу.

---

# SPR-013

## Название

readOnly=true

для UPDATE

Severity

High

---

Почему

Ошибка конфигурации.

---

# SPR-014

## Название

Слишком длинная цепочка сервисов

Severity

High

---

Service

↓

Service

↓

Service

↓

Service

↓

Repository

---

Почему

Трудно определить

границы транзакции.

---

# SPR-015

## Название

Вызов нескольких Repository

в одном цикле

Severity

Critical

---

Почему

Частая причина N+1.

---

Related

JAVA-001

HIB-001

---

# SPR-016

## Название

flush()

внутри транзакции

Severity

High

---

Исправление

Использовать batching.

---

# SPR-017

## Название

saveAndFlush()

в цикле

Severity

Critical

---

Последствия

Flush

на каждой записи.

---

# SPR-018

## Название

TransactionTemplate

внутри цикла

Severity

Critical

---

Почему

Тысячи транзакций.

---

# SPR-019

## Название

EntityManager.flush()

в цикле

Severity

Critical

---

# SPR-020

## Название

EntityManager.clear()

не используется

при batch

Severity

High

---

Почему

Persistence Context

неограниченно растет.

---

# SPR-021

## Название

Scheduler без блокировки кластера

Severity

Critical

---

Почему

При нескольких Pod

одна задача выполняется

несколько раз.

---

Исправление

ShedLock

Quartz Cluster

Leader Election

---

Related

ARCH-021

K8S-015

---

# SPR-022

## Название

Async без собственного Executor

Severity

High

---

Почему

Используется

SimpleAsyncTaskExecutor

или

общий Executor.

---

# SPR-023

## Название

Неограниченный TaskExecutor

Severity

Critical

---

Последствия

Рост памяти

создание тысяч потоков

---

# SPR-024

## Название

RestTemplate без Pooling

Severity

High

---

Исправление

HttpClient Pool

---

# SPR-025

## Название

WebClient.block()

Severity

High

---

Почему

Блокирует поток.

---

# SPR-026

## Название

Отсутствует timeout

для REST

Severity

Critical

---

Что искать

RestTemplate

WebClient

Feign

без timeout.

---

# SPR-027

## Название

Retry внутри транзакции

Severity

Critical

---

Почему

Увеличивается время удержания блокировок.

---

# SPR-028

## Название

@Transactional вокруг файловой системы

Severity

High

---

Почему

IO значительно медленнее SQL.

---

# SPR-029

## Название

Массовое логирование внутри транзакции

Severity

Medium

---

# SPR-030

## Название

Большой DTO внутри транзакции

Severity

Medium

---

Почему

Лишняя сериализация

увеличивает время транзакции.

---

# Итоги раздела

Особое внимание уделять

- REST внутри транзакции
- Kafka внутри транзакции
- REQUIRES_NEW
- saveAndFlush()
- flush()
- Batch Processing
- Scheduler
- Async
- Timeout
- Pooling
- readOnly
- EntityManager
- Persistence Context

Это наиболее распространенные причины проблем производительности в Spring-приложениях.