# Hibernate Session & Persistence Context Rules

Version: 1.0

---

# HIB-031

## Название

Persistence Context растет без очистки

Severity

Critical

Confidence

High

Category

Session

---

### Что искать

```java
for (...) {
    entityManager.persist(...)
}
```

или

```java
repository.save(...)
```

тысячи раз

без

```java
entityManager.clear()
```

---

### Почему плохо

Каждая Entity остается в Persistence Context.

Dirty Checking выполняется для всех объектов.

---

### Последствия

- рост Heap
- Full GC
- OutOfMemoryError
- замедление flush()

---

### Исправление

Batch Processing

```java
if (i % 500 == 0) {
    entityManager.flush();
    entityManager.clear();
}
```

---

Expected Improvement

Very High

---

# HIB-032

## Название

flush() внутри цикла

Severity

Critical

---

Что искать

```java
for (...) {
    entityManager.flush();
}
```

---

Почему плохо

Каждый flush запускает Dirty Checking.

Отправляет SQL отдельно.

---

Исправление

Flush один раз на batch.

---

Related

SPR-016

---

# HIB-033

## Название

saveAndFlush() внутри цикла

Severity

Critical

---

Последствия

Каждая запись становится отдельной операцией.

Полностью ломается batching.

---

# HIB-034

## Название

merge() вместо persist()

Severity

Medium

---

Почему

merge()

выполняет дополнительные проверки.

---

Исправление

Использовать persist()

для новых Entity.

---

# HIB-035

## Название

merge() в массовой обработке

Severity

High

---

Почему

merge()

значительно дороже persist().

---

# HIB-036

## Название

save()

для каждой записи отдельно

Severity

High

---

Исправление

Batch Insert.

---

# HIB-037

## Название

Dirty Checking большого Persistence Context

Severity

Critical

---

Что искать

Десятки тысяч Entity

в одной транзакции.

---

Последствия

Flush становится квадратичным.

---

# HIB-038

## Название

Изменение большого количества Entity

без batching

Severity

Critical

---

Исправление

hibernate.jdbc.batch_size

---

# HIB-039

## Название

EntityManager.clear()

никогда не вызывается

Severity

High

---

Почему

Heap растет на протяжении всего Batch Job.

---

# HIB-040

## Название

EntityManager.detach()

не используется

Severity

Medium

---

Когда применять

После обработки крупных объектов.

---

# HIB-041

## Название

findById()

в цикле

Severity

Critical

---

Что искать

```java
for (...) {
    repository.findById(...)
}
```

---

Почему

Типичный Enterprise N+1.

---

# HIB-042

## Название

existsById()

в цикле

Severity

Critical

---

Почему

Тысячи SELECT.

---

Исправление

IN

HashSet

Bulk Query.

---

# HIB-043

## Название

deleteById()

в цикле

Severity

Critical

---

Исправление

Bulk Delete.

---

# HIB-044

## Название

save()

после каждого изменения

Severity

High

---

Почему

Hibernate сам отслеживает изменения.

---

# HIB-045

## Название

Ручной flush()

без необходимости

Severity

Medium

---

# HIB-046

## Название

FlushMode.AUTO

для массовой обработки

Severity

Medium

---

Рекомендация

Проверить возможность использования

FlushMode.COMMIT.

---

# HIB-047

## Название

Persistence Context используется как Cache

Severity

High

---

Почему

Не предназначен для долгоживущего хранения данных.

---

# HIB-048

## Название

Одна транзакция изменяет десятки тысяч Entity

Severity

Critical

---

Исправление

Разделить обработку на чанки.

---

# HIB-049

## Название

Session удерживается слишком долго

Severity

High

---

Почему

Рост памяти

увеличение Dirty Checking

рост количества блокировок.

---

# HIB-050

## Название

Массовая обработка без StatelessSession

Severity

Medium

---

Когда проверить

Импорт миллионов записей.

---

Возможное решение

StatelessSession

если не требуется Dirty Checking.

---

# Проверить дополнительно

- jdbc.batch_size
- order_inserts
- order_updates
- batch_versioned_data
- FlushMode
- clear()
- detach()
- merge()
- persist()
- save()
- saveAll()
- saveAndFlush()
- Dirty Checking
- Persistence Context Size
- Batch Processing

---

# Самые критичные правила

HIB-031

HIB-032

HIB-033

HIB-037

HIB-041

HIB-042

HIB-043

HIB-048

Именно они чаще всего становятся причиной деградации производительности при обработке больших объемов данных.