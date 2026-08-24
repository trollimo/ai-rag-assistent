# Kafka Consumer Performance Rules

Version: 1.0

---

# KAFKA-021

## Название

Consumer обрабатывает сообщения последовательно

Severity

Critical

Confidence

High

Category

Consumer

---

### Что искать

```
for (ConsumerRecord record : records)
```

или

```
records.forEach(...)
```

где обработка длительная.

---

### Почему плохо

Максимальная производительность ограничивается одним потоком.

---

### Исправление

Рассмотреть параллельную обработку
или увеличение количества Consumer.

---

Expected Improvement

Very High

---

# KAFKA-022

## Название

Consumer выполняет HTTP вызов

Severity

Critical

---

Почему

Во время ожидания ответа Consumer не читает Kafka.

---

Последствия

- Consumer Lag
- Rebalance
- Рост задержек

---

# KAFKA-023

## Название

Consumer выполняет SQL в цикле

Severity

Critical

---

Что искать

```
for(record){

repository.find...

}
```

---

Почему

Типичный N+1.

---

Related

JAVA-001

HIB-001

SQL-024

---

# KAFKA-024

## Название

Consumer вызывает внешний сервис

Severity

High

---

Почему

Kafka превращается
в синхронную интеграцию.

---

# KAFKA-025

## Название

max.poll.records слишком большой

Severity

Medium

---

Почему

Один poll()

может обрабатываться слишком долго.

---

# KAFKA-026

## Название

max.poll.records слишком маленький

Severity

Low

---

Почему

Лишние обращения к брокеру.

---

# KAFKA-027

## Название

commitSync()

Severity

Medium

---

Почему

Блокирует поток Consumer.

---

Проверить

можно ли использовать

commitAsync().

---

# KAFKA-028

## Название

commit после каждого сообщения

Severity

Critical

---

Почему

Большое количество сетевых операций.

---

# KAFKA-029

## Название

Auto Commit используется без анализа

Severity

Medium

---

Что проверить

```
enable.auto.commit=true
```

---

# KAFKA-030

## Название

Большая транзакция внутри Consumer

Severity

Critical

---

Почему

Рост Consumer Lag.

---

# KAFKA-031

## Название

Долгая обработка сообщения

Severity

High

---

Признаки

Сложные вычисления

или большие SQL.

---

# KAFKA-032

## Название

Consumer хранит состояние

Severity

High

---

Почему

Усложняется горизонтальное масштабирование.

---

# KAFKA-033

## Название

Consumer использует synchronized

Severity

Medium

---

Почему

Появляется лишняя конкуренция потоков.

---

# KAFKA-034

## Название

Большой JSON десериализуется полностью

Severity

Medium

---

Почему

Высокая CPU-нагрузка.

---

# KAFKA-035

## Название

Повторная десериализация

Severity

Low

---

# KAFKA-036

## Название

Нет Dead Letter Queue

Severity

Medium

---

Почему

Ошибочные сообщения
могут бесконечно повторяться.

---

# KAFKA-037

## Название

Retry внутри Consumer

Severity

High

---

Почему

Поток Consumer блокируется.

---

Исправление

Retry Topic

или DLQ.

---

# KAFKA-038

## Название

Consumer создает большое количество объектов

Severity

Medium

---

Почему

Рост GC.

---

# KAFKA-039

## Название

Нет мониторинга Consumer Lag

Severity

High

---

Рекомендация

Проверить

- Consumer Lag
- Processing Time
- Poll Duration

---

# KAFKA-040

## Название

Consumer ограничивает масштабирование сервиса

Severity

Critical

---

Если обнаружены одновременно

- HTTP
- SQL
- synchronized
- commit после каждого сообщения
- долгие транзакции

следует отметить

**Consumer является bottleneck и препятствует горизонтальному масштабированию.**

---

# Проверить дополнительно

- max.poll.records
- max.poll.interval.ms
- session.timeout.ms
- heartbeat.interval.ms
- enable.auto.commit
- commitSync
- commitAsync
- DLQ
- Retry Topic
- Consumer Lag
- Processing Time
- Rebalance

---

# Наиболее критичные правила

KAFKA-021

KAFKA-022

KAFKA-023

KAFKA-028

KAFKA-030

KAFKA-037

KAFKA-040