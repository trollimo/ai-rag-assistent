# Java Concurrency Performance Rules

Version: 1.0

---

# JAVA-041

## Название

synchronized на горячем пути

Severity

High

Category

Concurrency

---

Что искать

```java
synchronized (...) {
```

```java
public synchronized void ...
```

---

Почему плохо

Каждый поток ожидает освобождения монитора.

При высокой нагрузке резко падает Throughput.

---

Последствия

- рост latency
- блокировка потоков
- низкая масштабируемость

---

Исправление

Минимизировать критическую секцию.

Использовать lock-free структуры данных или более мелкозернистую синхронизацию.

---

Related

JAVA-043

JAVA-052

---

# JAVA-042

## Название

Глобальная синхронизация

Severity

Critical

---

Что искать

```java
synchronized(SomeClass.class)
```

или

```java
static synchronized
```

---

Почему плохо

Один монитор используется всеми потоками JVM.

---

Последствия

Практически отсутствует горизонтальная масштабируемость.

---

Expected Improvement

Very High

---

# JAVA-043

## Название

Длительная работа внутри synchronized

Severity

Critical

---

Что искать

Внутри synchronized

- SQL
- REST
- Kafka
- File IO
- sleep()

---

Почему плохо

Монитор удерживается во время медленных операций.

---

Исправление

Вынести внешние вызовы за пределы критической секции.

---

Related

JAVA-001

JAVA-002

JAVA-003

---

# JAVA-044

## Название

REST внутри synchronized

Severity

Critical

---

Почему

Сетевой вызов блокирует все ожидающие потоки.

---

# JAVA-045

## Название

Repository внутри synchronized

Severity

Critical

---

Почему

Длительная блокировка монитора во время SQL.

---

# JAVA-046

## Название

sleep() внутри synchronized

Severity

Critical

---

Что искать

```java
Thread.sleep()
```

внутри synchronized.

---

Последствия

Искусственная блокировка всех потоков.

---

# JAVA-047

## Название

Небезопасный double-checked locking

Severity

High

---

Что искать

Double Checked Locking

без volatile.

---

Почему

Нарушение модели памяти Java.

---

Исправление

volatile

или

Initialization-on-demand holder.

---

# JAVA-048

## Название

Небезопасный Singleton

Severity

High

---

Что искать

Lazy Singleton

без синхронизации.

---

# JAVA-049

## Название

ThreadLocal без очистки

Severity

High

---

Что искать

```java
ThreadLocal.set()
```

без

```java
remove()
```

---

Последствия

Memory Leak

особенно в thread pool.

---

# JAVA-050

## Название

Executors.newFixedThreadPool()

с неограниченной очередью

Severity

Critical

---

Почему

LinkedBlockingQueue по умолчанию не ограничена.

При всплеске нагрузки память может закончиться.

---

Исправление

ThreadPoolExecutor

с ограниченной очередью.

---

Related

JAVA-051

---

# JAVA-051

## Название

Неограниченная BlockingQueue

Severity

Critical

---

Последствия

OutOfMemoryError

---

Исправление

Ограниченный размер очереди.

---

# JAVA-052

## Название

Один Executor для всех задач

Severity

High

---

Почему

Долгие задачи блокируют быстрые.

---

Исправление

Разделить Executor по типам нагрузки.

---

# JAVA-053

## Название

CompletableFuture.join()

в цикле

Severity

High

---

Почему

Фактически превращает параллельную обработку в последовательную.

---

Исправление

allOf()

---

# JAVA-054

## Название

CompletableFuture без Executor

Severity

Medium

---

Почему

Используется общий ForkJoinPool.

---

# JAVA-055

## Название

ForkJoinPool.commonPool()

для бизнес-задач

Severity

Medium

---

Почему

Конкурирует со всеми остальными задачами JVM.

---

# JAVA-056

## Название

Busy Waiting

Severity

High

---

Что искать

```java
while(true)
```

или

```java
while(flag)
```

без ожидания.

---

Последствия

100% CPU.

---

# JAVA-057

## Название

Spin Lock

Severity

Medium

---

Почему

При высокой конкуренции потребляет CPU.

---

# JAVA-058

## Название

CountDownLatch не освобождается

Severity

Critical

---

Последствия

Deadlock.

---

# JAVA-059

## Название

Future.get()

без timeout

Severity

High

---

Последствия

Потенциальная бесконечная блокировка.

---

Исправление

get(timeout)

---

# JAVA-060

## Название

ReadWriteLock используется при преобладании записи

Severity

Medium

---

Почему

Накладные расходы превышают выигрыш.

---

# JAVA-061

## Название

AtomicLong под высокой конкуренцией

Severity

Medium

---

Исправление

LongAdder.

---

# JAVA-062

## Название

Shared Mutable State

Severity

High

---

Почему

Рост количества блокировок.

---

# JAVA-063

## Название

Большая критическая секция

Severity

High

---

Исправление

Минимизировать объем синхронизированного кода.

---

# JAVA-064

## Название

Executor без graceful shutdown

Severity

Medium

---

Последствия

Утечки потоков.

---

# JAVA-065

## Название

Создание Thread вручную

Severity

Medium

---

Что искать

```java
new Thread(...)
```

---

Исправление

ExecutorService.

---

# JAVA-066

## Название

CachedThreadPool для неконтролируемой нагрузки

Severity

Critical

---

Почему

Количество потоков практически не ограничено.

---

Последствия

CPU thrashing

OutOfMemoryError

---

# JAVA-067

## Название

ScheduledExecutor выполняет длительные задачи

Severity

High

---

Последствия

Накопление отставания расписания.

---

# JAVA-068

## Название

Синхронная обработка независимых задач

Severity

Medium

---

Исправление

CompletableFuture

или

асинхронный pipeline.

---

# JAVA-069

## Название

Lock удерживается во время IO

Severity

Critical

---

Что искать

Lock

+

REST

SQL

Kafka

Files

---

# JAVA-070

## Название

Отсутствие timeout при ожидании блокировки

Severity

Medium

---

Исправление

tryLock(timeout)

---

# Итоги раздела

Особое внимание уделять:

- synchronized
- ExecutorService
- BlockingQueue
- CompletableFuture
- ForkJoinPool
- ThreadLocal
- Deadlock
- Contention
- IO внутри блокировок
- Неограниченным очередям
- Неконтролируемому росту потоков

Эти проблемы наиболее часто становятся причиной деградации производительности в высоконагруженных Java-сервисах.