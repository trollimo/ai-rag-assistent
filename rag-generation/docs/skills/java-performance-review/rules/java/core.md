# Java Core Performance Rules

Version: 1.0

---

# JAVA-001

## Название

Repository внутри цикла

---

## Severity

Critical

---

## Confidence

High

---

## Категория

Database

---

## Что искать

```
for (...)

repository.find...

repository.save...

repository.exists...

repository.delete...
```

```
while (...)
```

```
stream().forEach(...)
```

---

## Почему это проблема

Каждая итерация приводит к отдельному SQL-запросу.

При большом количестве элементов возникает классическая проблема N+1.

---

## Последствия

- тысячи SQL
- рост latency
- перегрузка connection pool
- перегрузка PostgreSQL

---

## Как исправить

Использовать

batch

findAllById()

JOIN

IN

bulk update

bulk delete

---

## False Positive

Небольшая коллекция

до 10 элементов.

---

## Related

HIB-001

SQL-001

PG-001

---

## Expected Improvement

Very High

---

# JAVA-002

## Название

REST внутри цикла

---

Severity

Critical

---

Что искать

```
for (...)

restTemplate.exchange()

webClient.get()

feignClient.call()

```

---

Последствия

N HTTP запросов

рост latency

Fan-Out

перегрузка сети

---

Исправление

Batch API

Bulk API

Асинхронная обработка

Кэширование

---

Related

REST-001

ARCH-011

---

# JAVA-003

## Название

Kafka publish внутри цикла

---

Severity

Critical

---

Что искать

```
for (...)

kafkaTemplate.send()

```

---

Почему плохо

Каждое сообщение публикуется отдельно.

---

Исправление

Batch

Aggregation

Compression

---

Related

KAFKA-003

---

# JAVA-004

## Название

Полное чтение таблицы

---

Severity

Critical

---

Что искать

```
repository.findAll()
```

---

Также

```
select *

```

без условий.

---

Почему плохо

При росте таблицы

потребление памяти растет линейно.

---

Исправление

Pagination

Streaming

Cursor

---

Related

SQL-003

PG-014

---

# JAVA-005

## Название

contains() по ArrayList внутри цикла

---

Severity

High

---

Что искать

```
for (...)

list.contains(...)
```

---

Почему плохо

Сложность

O(n²)

---

Исправление

HashSet

---

Related

JAVA-041

---

# JAVA-006

## Название

remove() по ArrayList внутри цикла

---

Severity

High

---

Почему

Каждое удаление

сдвигает массив.

---

Исправление

Iterator.remove()

removeIf()

LinkedList

если оправдано.

---

# JAVA-007

## Название

Вложенные циклы

---

Severity

High

---

Что искать

```
for

for

```

или

```
stream()

stream()

```

---

Исправление

Map

HashMap

Предварительная индексация.

---

# JAVA-008

## Название

Вложенные Stream API

---

Severity

Medium

---

Что искать

```
stream()

flatMap()

stream()

```

---

Почему

Может приводить

к квадратичной сложности.

---

# JAVA-009

## Название

parallelStream() без необходимости

---

Severity

Medium

---

Почему

Использует общий ForkJoinPool.

Может ухудшить производительность.

---

Исправление

Собственный Executor.

---

# JAVA-010

## Название

Thread.sleep()

---

Severity

High

---

Что искать

```
Thread.sleep
```

---

Почему

Блокирует поток.

---

Исправление

Планировщик

Await

Condition

---

# JAVA-011

## Название

Создание ObjectMapper в горячем коде

---

Severity

Medium

---

Что искать

```
new ObjectMapper()
```

---

Исправление

Singleton Bean.

---

# JAVA-012

## Название

Pattern.compile() в цикле

---

Severity

Medium

---

Исправление

Статический Pattern.

---

# JAVA-013

## Название

String concat в цикле

---

Severity

Medium

---

Что искать

```
+=
```

---

Исправление

StringBuilder.

---

# JAVA-014

## Название

BigDecimal в горячем цикле

---

Severity

Medium

---

Почему

Дорогие операции.

---

Исправление

Минимизировать количество вычислений.

---

# JAVA-015

## Название

Reflection в горячем пути

---

Severity

Medium

---

Что искать

```
Class.forName

Method.invoke

Field.get

```

---

Исправление

Кэширование

MethodHandle

Прямой вызов.

---

# JAVA-016

## Название

Autoboxing в цикле

---

Severity

Medium

---

Что искать

Integer

Long

Double

вместо примитивов.

---

# JAVA-017

## Название

Лишние временные коллекции

---

Severity

Medium

---

Что искать

```
collect()

collect()

collect()

```

---

Исправление

Однопроходная обработка.

---

# JAVA-018

## Название

Большие промежуточные списки

---

Severity

High

---

Почему

Рост памяти

GC

---

Исправление

Streaming

Chunking

---

# JAVA-019

## Название

Неограниченный рост HashMap

---

Severity

High

---

Исправление

Очистка

LRU

TTL

---

# JAVA-020

## Название

HashMap без initial capacity

---

Severity

Low

---

Почему

Повторные resize.

---

Исправление

```
new HashMap<>(expectedSize)
```

---

Продолжение

JAVA-021

...

JAVA-040

в следующем обновлении.