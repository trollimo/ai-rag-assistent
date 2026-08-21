# Rule Taxonomy

Version: 1.0

---

# Назначение

Все правила должны иметь постоянный уникальный идентификатор.

Идентификатор никогда не изменяется.

Допускается только добавление новых правил.

Запрещается повторное использование Rule ID.

---

# Формат Rule ID

<PREFIX>-<NUMBER>

Примеры

JAVA-001

SPR-017

HIB-042

PG-011

SQL-083

KAFKA-021

---

# Структура Rule

Каждое правило должно содержать

Rule ID

Название

Категория

Технологии

Severity

Confidence

Описание

Почему проблема

Что искать

Как проверить

Как исправить

Когда допустимо

Ложные срабатывания

Связанные правила

Expected Improvement

---

# Prefixes

## JAVA

Язык Java

Диапазон

JAVA-001 ... JAVA-999

Разделы

Collections

Streams

Memory

GC

Concurrency

Synchronization

Algorithms

IO

NIO

Reflection

JIT

Virtual Threads

Exceptions

Strings

Boxing

Objects

Executors

CompletableFuture

Parallel Streams

---

## SPR

Spring Framework

SPR-001 ... SPR-999

Разделы

Core

MVC

Transactions

Cache

Async

Scheduling

Security

Events

Configuration

Bean Lifecycle

Profiles

RestTemplate

WebClient

---

## BOOT

Spring Boot

BOOT-001 ... BOOT-999

Разделы

Autoconfiguration

Configuration

Properties

Actuator

Startup

Logging

Metrics

---

## HIB

Hibernate / JPA

HIB-001 ... HIB-999

Разделы

Fetching

Session

Persistence Context

Dirty Checking

Batch

Entity

Cascade

Locking

Cache

Collections

Inheritance

Query

Pagination

Flush

Merge

Persist

---

## JOOQ

jOOQ

JOOQ-001 ... JOOQ-999

Разделы

DSL

Fetch

Mapping

Batch

Transactions

SQL Generation

Streaming

---

## JDBC

JDBC

JDBC-001 ... JDBC-999

Разделы

PreparedStatement

Statement

Batch

ResultSet

Fetch Size

Transactions

LOB

---

## SQL

Общие SQL правила

SQL-001 ... SQL-999

Разделы

Join

Where

Exists

In

Union

Distinct

Order By

Group By

Pagination

Aggregation

Functions

Subquery

CTE

Window Functions

---

## PG

PostgreSQL

PG-001 ... PG-999

Разделы

Indexes

Execution Plan

Seq Scan

Bitmap Scan

Hash Join

Nested Loop

Statistics

Vacuum

Analyze

Partitioning

Locking

MVCC

Autovacuum

Materialized Views

---

## SYB

Sybase

SYB-001 ... SYB-999

---

## LB

Liquibase

LB-001 ... LB-999

Разделы

Changesets

Indexes

Rollback

DDL

Sequences

Constraints

---

## KAFKA

Kafka

KAFKA-001 ... KAFKA-999

Разделы

Producer

Consumer

Partitions

Lag

Transactions

Compression

Serialization

Batching

Idempotence

Rebalance

---

## AMQ

ActiveMQ

AMQ-001 ... AMQ-999

Разделы

Producer

Consumer

Queue

Topic

Redelivery

DLQ

Prefetch

---

## REST

REST API

REST-001 ... REST-999

Разделы

HTTP

Payload

Pagination

Compression

Timeout

Retry

Circuit Breaker

Fan-Out

---

## OAPI

OpenAPI

OAPI-001 ... OAPI-999

---

## WS

WebSocket

WS-001 ... WS-999

---

## REDIS

REDIS-001 ... REDIS-999

Разделы

Cache

TTL

Hot Keys

Serialization

Pub/Sub

Distributed Lock

---

## JVM

JVM-001 ... JVM-999

Разделы

Heap

GC

JIT

Metaspace

TLAB

Escape Analysis

Safepoints

---

## DOCKER

DOCKER-001 ... DOCKER-999

---

## K8S

Kubernetes

K8S-001 ... K8S-999

Разделы

Deployment

Resources

Requests

Limits

Autoscaling

Affinity

Topology

PDB

Probes

StatefulSet

ConfigMap

Secrets

---

## HELM

HELM-001 ... HELM-999

---

## ARCH

Архитектура

ARCH-001 ... ARCH-999

Разделы

Microservices

Fan-Out

Fan-In

Shared Database

Gateway

Scheduler

Integration

Bounded Context

Scalability

Availability

Resilience

---

## SCALE

Масштабируемость

SCALE-001 ... SCALE-999

Разделы

Horizontal

Vertical

Stateful

Stateless

Partitioning

Sharding

Caching

Replication

---

# Cross Rules

Одно правило может ссылаться на другое.

Пример

HIB-014

↓

SQL-021

↓

PG-008

↓

ARCH-011

Это позволяет показать цепочку причин.

---

# Rule Levels

## Level A

Локальная проблема.

Например

Repository внутри цикла.

---

## Level B

Проблема компонента.

Например

Микросервис читает всю таблицу.

---

## Level C

Архитектурная проблема.

Например

Gateway вызывает 12 сервисов последовательно.

---

# Теги

Каждое правило должно иметь теги.

Пример

Tags

performance

database

hibernate

n+1

---

# Affected Resources

Каждое правило должно указывать влияние.

CPU

Memory

GC

Database

Disk

Network

Locks

Latency

Throughput

Horizontal Scaling

Vertical Scaling

Availability

---

# Search Patterns

Каждое правило должно содержать

Поисковые конструкции

Например

findAll()

saveAndFlush()

Thread.sleep()

SELECT *

OFFSET

@ManyToMany

@Transactional

Repository

for (

stream()

parallelStream()

---

# False Positives

Каждое правило обязано содержать раздел

False Positives

где перечислены случаи,

когда предупреждение допустимо игнорировать.

---

# Rule Lifecycle

Draft

↓

Reviewed

↓

Stable

↓

Deprecated

↓

Removed

Rule ID при этом никогда не переиспользуется.