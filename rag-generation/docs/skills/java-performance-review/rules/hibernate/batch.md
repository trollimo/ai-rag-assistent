# Hibernate Batch Processing Rules

Version: 1.0

---

# HIB-051

## Название

hibernate.jdbc.batch_size не настроен

Severity

Critical

Confidence

High

Category

Batching

---

### Что искать

Отсутствует

```properties
hibernate.jdbc.batch_size
```

или значение

```
0
```

---

### Почему плохо

Каждый INSERT

UPDATE

DELETE

отправляется отдельно.

---

### Исправление

Рекомендуемое значение

```
20

50

100
```

Подбирать экспериментально.

---

Expected Improvement

Very High

---

# HIB-052

## Название

batch_size слишком маленький

Severity

Medium

---

Что искать

```
hibernate.jdbc.batch_size=2
```

или

5

---

Почему

Практически отсутствует выигрыш.

---

# HIB-053

## Название

batch_size слишком большой

Severity

Medium

---

Почему

Большие batch

увеличивают память

и время rollback.

---

# HIB-054

## Название

saveAndFlush()

ломает batching

Severity

Critical

---

Почему

Каждый flush

отправляет SQL немедленно.

---

Related

SPR-017

HIB-032

---

# HIB-055

## Название

flush()

внутри batch

Severity

Critical

---

Исправление

Flush только после N записей.

---

# HIB-056

## Название

order_inserts отключен

Severity

High

---

Что искать

Отсутствует

```
hibernate.order_inserts=true
```

---

Почему

Hibernate хуже группирует INSERT.

---

# HIB-057

## Название

order_updates отключен

Severity

High

---

Почему

Обновления не объединяются.

---

# HIB-058

## Название

batch_versioned_data отключен

Severity

Medium

---

Почему

Versioned Entity

не участвуют в batching.

---

# HIB-059

## Название

IDENTITY отключает batching

Severity

Critical

---

Что искать

```java
@GeneratedValue(strategy = IDENTITY)
```

---

Почему

После каждого INSERT

нужно получать ID.

Batching невозможен.

---

Исправление

SEQUENCE

с allocationSize.

---

# HIB-060

## Название

SEQUENCE без allocationSize

Severity

Medium

---

Что искать

```java
allocationSize=1
```

---

Почему

Частые обращения

к sequence.

---

Рекомендация

```
allocationSize=50
```

или больше.

---

# HIB-061

## Название

TABLE Generator

Severity

High

---

Почему

Самый медленный способ генерации ID.

---

# HIB-062

## Название

Batch Insert отсутствует

Severity

High

---

Что искать

```
save()

save()

save()
```

тысячи раз.

---

Исправление

saveAll()

Batch.

---

# HIB-063

## Название

Batch Update отсутствует

Severity

High

---

Исправление

Bulk Update.

---

# HIB-064

## Название

Batch Delete отсутствует

Severity

Critical

---

Что искать

```
delete()

delete()

delete()
```

---

Исправление

DELETE WHERE ...

---

# HIB-065

## Название

Persist большого объема

без clear()

Severity

Critical

---

Последствия

Рост Heap.

---

# HIB-066

## Название

saveAll()

без batching Hibernate

Severity

Medium

---

Почему

saveAll()

сам по себе

не гарантирует batching.

---

# HIB-067

## Название

Batch содержит разные Entity

Severity

Medium

---

Почему

Batch дробится.

---

# HIB-068

## Название

INSERT перемешаны с UPDATE

Severity

Medium

---

Почему

Batch не формируется.

---

# HIB-069

## Название

UPDATE перемешаны с DELETE

Severity

Medium

---

# HIB-070

## Название

Большой batch без commit

Severity

High

---

Почему

Rollback становится дорогим.

---

# HIB-071

## Название

save()

вложенных Entity

через Cascade.ALL

Severity

High

---

Почему

Непредсказуемое количество SQL.

---

# HIB-072

## Название

Batch Job без chunking

Severity

Critical

---

Что искать

Одна транзакция

на миллионы записей.

---

# HIB-073

## Название

Batch чтение без fetchSize

Severity

High

---

Почему

Драйвер загружает весь ResultSet.

---

# HIB-074

## Название

Streaming отсутствует

Severity

Medium

---

Исправление

ScrollableResults

Stream()

Cursor.

---

# HIB-075

## Название

save()

в цикле

без saveAll()

Severity

Medium

---

# HIB-076

## Название

StatelessSession не используется

для массового импорта

Severity

Medium

---

Когда применять

Импорт

миллионов записей.

---

# HIB-077

## Название

Массовое обновление через Entity

вместо Bulk Update

Severity

Critical

---

Исправление

JPQL UPDATE

или

Native SQL.

---

# HIB-078

## Название

Массовое удаление через Entity

Severity

Critical

---

Исправление

Bulk DELETE.

---

# HIB-079

## Название

Отсутствует контроль размера batch

Severity

Medium

---

Почему

Размер должен определяться

экспериментально

по метрикам.

---

# HIB-080

## Название

Нет мониторинга batching

Severity

Low

---

Рекомендация

Включить

Hibernate Statistics

или p6spy

для проверки,

что batching действительно работает.

---

# Проверить дополнительно

- jdbc.batch_size
- order_inserts
- order_updates
- batch_versioned_data
- allocationSize
- IDENTITY
- SEQUENCE
- TABLE Generator
- saveAll()
- Bulk Update
- Bulk Delete
- StatelessSession
- fetchSize
- Streaming
- Chunk Processing

---

# Наиболее критичные правила

HIB-051

HIB-054

HIB-055

HIB-059

HIB-064

HIB-065

HIB-072

HIB-077

HIB-078

Эти ошибки чаще всего приводят к тому, что массовые операции работают в десятки раз медленнее ожидаемого.