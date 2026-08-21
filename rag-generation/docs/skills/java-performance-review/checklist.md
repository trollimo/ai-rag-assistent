# Performance Review Checklist

Version: 1.0

---

# Цель

Данный документ определяет обязательную последовательность анализа репозитория.

Запрещается выполнять анализ выборочно.

Каждый раздел должен быть проверен независимо от того, были ли уже найдены критические проблемы.

---

# Общий алгоритм

```
Repository

↓

Определение технологий

↓

Определение компонентов

↓

Анализ Java

↓

Анализ Spring

↓

Анализ Hibernate

↓

Анализ SQL

↓

Анализ PostgreSQL

↓

Анализ Messaging

↓

Анализ REST

↓

Анализ Kubernetes

↓

Архитектурный анализ

↓

Оценка масштабируемости

↓

Формирование отчета
```

---

# Шаг 1

## Определение технологий

Определить

Java

Spring Boot

Spring Data

Hibernate

JPA

jOOQ

JDBC

Liquibase

Flyway

Kafka

ActiveMQ

RabbitMQ

REST

OpenAPI

GraphQL

WebSocket

Redis

PostgreSQL

Sybase

Oracle

Docker

Kubernetes

Helm

---

# Шаг 2

## Определение компонентов

Определить

количество сервисов

общие библиотеки

starter

gateway

scheduler

batch

worker

API

consumer

producer

database

shared modules

---

# Шаг 3

## Java

Проверить

### Алгоритмы

O(n²)

O(n³)

лишние циклы

вложенные stream

полное чтение коллекций

contains()

remove()

sort()

distinct()

---

### Collections

HashMap

TreeMap

LinkedHashMap

ConcurrentHashMap

ArrayList

LinkedList

CopyOnWrite

BlockingQueue

---

### Memory

boxing

autoboxing

лишние allocations

временные коллекции

StringBuilder

String concat

BigDecimal

Pattern.compile

DateTimeFormatter

ObjectMapper

---

### Concurrency

Executor

ForkJoin

CompletableFuture

parallelStream

synchronized

Lock

Semaphore

CountDownLatch

Atomic

volatile

---

### IO

Files

InputStream

OutputStream

NIO

memory mapping

---

# Шаг 4

## Spring

Проверить

@Transactional

REQUIRES_NEW

Async

Scheduler

Cache

Security

Events

Bean Scope

Profiles

RestTemplate

WebClient

---

# Шаг 5

## Hibernate

Проверить

N+1

Lazy

Eager

Batch

Flush

Merge

Persist

Entity Graph

Join Fetch

Session

Persistence Context

Dirty Checking

Locking

Second Level Cache

---

# Шаг 6

## SQL

Проверить

SELECT *

OFFSET

JOIN

GROUP BY

ORDER BY

DISTINCT

COUNT(*)

UNION

EXISTS

IN

NOT IN

LIKE

ILIKE

CTE

Window Functions

Subquery

---

# Шаг 7

## PostgreSQL

Проверить

Seq Scan

Bitmap Scan

Nested Loop

Hash Join

Merge Join

Execution Plan

Indexes

Covering Index

Partial Index

Partitioning

Vacuum

Analyze

Statistics

Locks

Long Transactions

---

# Шаг 8

## Liquibase

Проверить

индексы

constraints

nullable

rollback

DDL

типы данных

partitioning

changesets

---

Если отсутствует

добавить рекомендацию

ручной проверки.

---

# Шаг 9

## Kafka

Проверить

Producer

Consumer

Partition

Replication

Compression

Batch

Lag

Offset

Transactions

Idempotence

Ordering

---

# Шаг 10

## REST

Проверить

Fan-Out

Payload

Pagination

Compression

Timeout

Retry

Circuit Breaker

HTTP Client

Pooling

---

# Шаг 11

## WebSocket

Проверить

Broadcast

Session

Heartbeat

Serialization

Payload

Memory Leak

---

# Шаг 12

## Kubernetes

Если найден

проверить

Requests

Limits

HPA

PDB

Affinity

AntiAffinity

TopologySpreadConstraints

Readiness

Liveness

Startup Probe

Replica Count

Graceful Shutdown

JVM Heap

CPU

Memory

---

Если отсутствует

вывести список

ручной проверки.

---

# Шаг 13

## Архитектура

Проверить

Fan-Out

Fan-In

Shared Database

Shared Cache

Central Service

Single Point Of Failure

Scheduler

Stateful Service

Sticky Session

Distributed Lock

Batch Processing

Synchronous Chain

Gateway

Event Flow

---

# Шаг 14

## Масштабируемость

Проверить

горизонтальное масштабирование

вертикальное масштабирование

singleton

partitioning

batching

caching

queue

database

---

# Шаг 15

## Формирование списка проблем

Для каждой проблемы определить

Rule ID

Severity

Confidence

Описание

Последствия

Компонент

Файл

Технологию

Рекомендацию

Expected Improvement

---

# Шаг 16

## Приоритизация

Сначала

Critical

потом

High

потом

Medium

потом

Low

---

# Шаг 17

## Подготовка отчета

Обязательно вывести

Executive Summary

Performance Grade

Performance Risk Score

Количество найденных проблем

Critical

High

Medium

Low

Info

---

# Шаг 18

## План исправления

Сформировать

Top-10

наиболее важных исправлений

с ожидаемым эффектом.

---

# Правила анализа

Никогда

не прекращать анализ

после первой найденной проблемы.

---

Всегда

пытаться определить

архитектурную причину,

а не только локальный симптом.

---

При отсутствии достаточных данных

использовать

Confidence = Low

вместо игнорирования проблемы.

---

Всегда анализировать

как отдельный компонент,

так и систему в целом,

если это возможно определить по репозиторию.