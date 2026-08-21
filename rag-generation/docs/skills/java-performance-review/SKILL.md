# Java Performance Reviewer Skill

Version: 1.0 MVP

---

# Purpose

Данный Skill предназначен для поиска реальных и потенциальных проблем производительности
в Java-репозиториях.

Основная задача — выполнить архитектурный Performance Review и сформировать отчет,
приоритизированный по критичности и ожидаемому эффекту.

Анализ выполняется статически.

Не допускается придумывать проблемы, которых нет.

Каждый вывод должен быть основан на найденном коде, SQL, конфигурации
или явно отмечен как рекомендация для ручной проверки.

---

# Supported Technologies

- Java
- Spring Framework
- Spring Boot
- Hibernate / JPA
- jOOQ
- JDBC
- SQL
- PostgreSQL
- Sybase
- Liquibase
- Kafka
- ActiveMQ
- REST
- OpenAPI
- WebSocket
- Kubernetes
- Helm
- Docker

---

# Analysis Levels

Во время анализа необходимо оценивать несколько уровней системы.

Level 1

Single Class

↓

Level 2

Module

↓

Level 3

Microservice

↓

Level 4

Whole Repository

↓

Level 5

Architecture

↓

Level 6

Scalability

Если видно влияние между компонентами —
необходимо описывать системную проблему,
а не только локальный дефект.

---

# Analysis Modes

Перед запуском анализа агент должен предложить пользователю выбрать режим.

Если пользователь явно указал режим —
не задавать вопросы.

Если режим не указан —
предложить выбор.

Не предлагать более восьми вариантов.

## 1. Full Performance Review

Полный анализ всего репозитория.

Включает все проверки.

Рекомендуемый режим.

---

## 2. Database Review

Проверять только

- SQL
- PostgreSQL
- Liquibase
- Hibernate
- jOOQ

---

## 3. Java Review

Проверять

- Java
- Collections
- Streams
- Concurrency
- Memory
- JVM

---

## 4. Spring Review

Проверять

- Spring
- Transactions
- REST
- Dependency Injection
- Scheduling
- Cache

---

## 5. Messaging Review

Проверять

- Kafka
- ActiveMQ
- Async Processing

---

## 6. Architecture Review

Проверять

- взаимодействие сервисов
- синхронные вызовы
- циклические зависимости
- fan-out
- orchestration
- scalability

---

## 7. Scalability Review

Проверять

- горизонтальное масштабирование

- bottleneck

- shared state

- distributed locks

- hot tables

- hot partitions

- hot rows

- cache scalability

---

## 8. Quick Review

Выполнить только проверки

Critical

High

для быстрого получения результата.

---

# Analysis Order

Всегда соблюдать следующий порядок.

1

Repository

↓

2

Modules

↓

3

Database

↓

4

Messaging

↓

5

REST APIs

↓

6

Architecture

↓

7

Scalability

↓

8

Final Report

---

# Severity

Critical

↓

High

↓

Medium

↓

Low

↓

Info

---

# Confidence

High

Medium

Low

---

# Rules

Каждая найденная проблема должна содержать

- ID
- Title
- Severity
- Confidence
- Technology
- Description
- Evidence
- Recommendation
- Expected Improvement

---

# Manual Checks

Если невозможно сделать вывод статически,
необходимо сформировать рекомендации
для ручной проверки.

Например

- EXPLAIN ANALYZE

- pg_stat_statements

- Kubernetes Resources

- Helm

- JVM Metrics

- GC Logs

- Prometheus

- Grafana

---

# Helm

Если Helm Chart отсутствует,
не считать это ошибкой.

Вместо этого добавить раздел

Manual Helm Review

с перечнем того,
что необходимо проверить вручную.

---

# Reporting

Отчет должен содержать разделы

## Executive Summary

## Critical Issues

## High Priority

## Medium Priority

## Low Priority

## Scalability Risks

## Architecture Risks

## Manual Checks

## Top 10 Improvements

## Estimated Performance Impact

---

# Report Output Format

По умолчанию отчет записывается в файл `report.md` в корне анализируемого репозитория.

Пользователь может выбрать формат

- Markdown (по умолчанию)
- HTML

## Markdown Output

Агент записывает файл `report.md` в корень репозитория.

Файл должен содержать полный отчет в формате Markdown.

Использовать шаблон report-template.md как основу структуры.

## HTML Output

Агент записывает файл `report.html` в корень репозитория.

Использовать шаблон report-template.html как основу.

HTML-отчет должен содержать

- Table of Contents с якорными ссылками
- Executive Summary с метриками
- Сворачиваемые секции для каждого уровня severity
- Таблицы для Repository Overview и Top 10 Fixes
- Цветовые метки severity (Critical, High, Medium, Low, Info)
- Подсветку кода через highlight.js (CDN)
- Адаптивный дизайн

## File Naming

- Markdown: report.md
- HTML: report.html

Если пользователь указал свой путь — использовать его.

---

# Important

Никогда

- не придумывать проблемы

- не делать вывод без доказательств

- не завышать Severity

- не считать рекомендацию ошибкой

---

# Evidence

Любая найденная проблема должна содержать
ссылку

- на Java-класс

или

- SQL

или

- Liquibase

или

- конфигурацию

или

- участок кода

---

# Estimated Improvement

По возможности оценивать

Very High

High

Medium

Low

---

# Output Language

Использовать язык пользователя.

По умолчанию

Русский.
