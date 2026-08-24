# 🚂 Performance Review Report Template

Version: 1.0

---

# 📄 Формат отчета

Отчет по умолчанию записывается в файл report.md в корне репозитория.

Также доступен HTML-формат (report.html) с:

- таблицами
- цветовыми метками severity
- сворачиваемыми секциями
- подсветкой кода (highlight.js)
- адаптивным дизайном

Для HTML-формата использовать шаблон report-template.html.

---

# 📋 Общие требования

Отчет должен быть структурирован.

Проблемы сортируются по:

1. Severity
2. Confidence
3. Expected Improvement

Никогда не выводить проблемы в случайном порядке.

---

# 📊 Executive Summary

Кратко описать систему.

Указать

- используемые технологии
- найденные компоненты
- общий уровень риска
- основные bottleneck
- главные ограничения масштабируемости

Пример

`
Проанализировано:

7 микросервисов

Java 21

Spring Boot

Hibernate

PostgreSQL

Kafka

Liquibase

Kubernetes

Обнаружено

Critical: 4

High: 18

Medium: 31

Low: 27

Performance Grade

D

Performance Risk

84

Основной риск связан с чрезмерной нагрузкой на БД, несколькими N+1, отсутствием batching и длинными синхронными REST-цепочками.
`

---

# 📁 Repository Overview

Указать

## Компоненты

Список сервисов

## Общие библиотеки

## Database

## Messaging

## API

## Kubernetes

## Helm

---

# 🛠 Technology Stack

Определить

Java

Spring

Hibernate

jOOQ

Liquibase

Kafka

PostgreSQL

Redis

Docker

Kubernetes

Helm

OpenAPI

REST

WebSocket

---

# 🏗 Architecture Overview

Попытаться определить

тип архитектуры

например

Монолит

Микросервисы

Event Driven

REST

CQRS

Scheduler

Batch

Streaming

---

# 🎯 Performance Score

Вывести

Performance Grade

Performance Risk

Architecture Risk

Database Risk

Scalability Risk

---

# 🚨 Critical Issues

Для каждой проблемы использовать формат

---

Rule

JAVA-001

Severity

Critical

Confidence

High

Technology

Java

Component

billing-service

Location

src/main/...

Problem

...

Impact

CPU

Memory

Database

Latency

Scalability

Explanation

...

Recommendation

...

Expected Improvement

Very High

Related Rules

JAVA-017

SQL-022

HIB-014

---

# ⚠️ High Issues

Использовать тот же формат.

---

# 🔶 Medium Issues

Использовать тот же формат.

---

# 🔹 Low Issues

Использовать тот же формат.

---

# 🏛 Architecture Findings

Перечислить

единые точки отказа

Fan-Out

Fan-In

Shared Database

Stateful

Scheduler

Shared Cache

Gateway

Distributed Lock

Single Consumer

Sticky Session

Длинные цепочки

REST

Kafka

Database

---

# 📈 Scalability Findings

Проверить

горизонтальное масштабирование

вертикальное масштабирование

горячие сервисы

горячие таблицы

горячие индексы

очереди

partitioning

batching

---

# ☕ Java Findings

Сгруппировать проблемы

Collections

Streams

Concurrency

Memory

GC

Reflection

Exceptions

Algorithms

---

# 🌱 Spring Findings

Transactions

Cache

Async

Scheduling

MVC

Security

Configuration

---

# 🗄 Hibernate Findings

N+1

Fetching

Batch

Session

Flush

Entity Graph

Dirty Checking

Locking

Cache

---

# 📝 SQL Findings

Indexes

Join

Pagination

Aggregation

Functions

Subquery

Window Functions

---

# 🐘 PostgreSQL Findings

Execution Plans

Indexes

Seq Scan

Bitmap Scan

Nested Loop

Hash Join

Partitioning

Vacuum

Statistics

---

# 📨 Messaging Findings

Kafka

Producer

Consumer

Lag

Partition

Compression

Transactions

ActiveMQ

---

# ☸ Kubernetes Findings

Requests

Limits

HPA

Affinity

AntiAffinity

Topology Spread

PDB

Readiness

Liveness

Startup Probe

---

# ⚓ Helm Findings

Если Helm найден

проанализировать chart.

Если отсутствует

написать

Helm Chart не найден.

Рекомендуется проверить вручную:

- requests
- limits
- replicas
- HPA
- affinity
- antiAffinity
- topologySpreadConstraints
- startupProbe
- readinessProbe
- livenessProbe
- PDB
- JVM Heap
- CPU Limits
- Memory Limits

---

# 🔄 Liquibase Findings

Если найден

проверить

индексы

nullable

constraints

partitioning

rollback

типы данных

Если отсутствует

вывести рекомендации по ручной проверке.

---

# 🏚 Technical Debt

Перечислить

неэффективные конструкции

дублирование

устаревшие API

временные решения

---

# 🔧 Top 10 Fixes

Отсортировать по ожидаемому эффекту.

Для каждого исправления

Rule

Описание

Ожидаемый эффект

Сложность

Priority

---

# 👀 Manual Review Required

Вывести список того,

что невозможно определить автоматически.

Например

EXPLAIN ANALYZE

реальные размеры таблиц

нагрузка

Heap Dump

Thread Dump

GC Logs

JFR

Prometheus

Grafana

---

# ✅ Positive Findings

Указать

что реализовано хорошо.

Например

используется batching

используются prepared statements

используется keyset pagination

есть HPA

есть индексы

используется connection pool

используется compression

---

# 🏁 Final Conclusion

Краткий вывод.

Обязательно ответить

Можно ли выпускать систему в production
с точки зрения производительности?

Варианты

Да

Да, после исправления High

Только после исправления Critical

Недостаточно данных

---

# Правила формирования отчета

Никогда

не писать

"все хорошо"

или

"проблем нет"

Если критичных проблем нет,

необходимо перечислить

потенциальные риски,

которые следует проверить вручную.

---

Отчет должен быть понятен

Senior Developer

Software Architect

Performance Engineer

Tech Lead

и использовать профессиональную терминологию.