# Java Collections Performance Rules

Version: 1.0

---

# JAVA-COL-001

## Название

contains() на List в горячем цикле

Severity

Critical

Confidence

High

Category

Collections

---

### Что искать

```java
for (...) {

    list.contains(...);

}
```

---

### Почему плохо

Поиск в List имеет сложность O(n).

В результате весь алгоритм становится O(n²).

---

### Исправление

Использовать

```
HashSet
```

или

```
HashMap
```

---

Expected Improvement

Very High

---

# JAVA-COL-002

## Название

remove() из ArrayList в цикле

Severity

High

---

Почему

Все элементы после удаляемого
сдвигаются.

---

Исправление

Iterator.remove()

или

LinkedList (если оправдано).

---

# JAVA-COL-003

## Название

indexOf() внутри цикла

Severity

Critical

---

Почему

Каждый вызов выполняет линейный поиск.

---

# JAVA-COL-004

## Название

Вложенные циклы по двум коллекциям

Severity

Critical

---

Что искать

```java
for (...) {

   for (...) {

   }

}
```

---

Почему

Часто заменяется

HashMap

или

HashSet.

---

# JAVA-COL-005

## Название

Поиск объекта перебором

Severity

High

---

Исправление

Предварительно построить Map.

---

# JAVA-COL-006

## Название

HashMap создается в каждой итерации

Severity

Medium

---

Почему

Лишние allocations.

---

# JAVA-COL-007

## Название

Повторное построение одинаковой Map

Severity

Medium

---

Почему

Можно построить один раз.

---

# JAVA-COL-008

## Название

ArrayList без начальной емкости

Severity

Medium

---

Что искать

```java
new ArrayList<>()
```

если заранее известно количество элементов.

---

Исправление

```java
new ArrayList<>(expectedSize)
```

---

# JAVA-COL-009

## Название

HashMap без initialCapacity

Severity

Medium

---

Почему

Многократный resize.

---

# JAVA-COL-010

## Название

HashSet без initialCapacity

Severity

Medium

---

# JAVA-COL-011

## Название

LinkedList используется как List

Severity

Medium

---

Почему

Случайный доступ O(n).

---

# JAVA-COL-012

## Название

Vector используется без необходимости

Severity

Low

---

Почему

Лишняя синхронизация.

---

# JAVA-COL-013

## Название

CopyOnWriteArrayList для частой записи

Severity

High

---

Почему

Каждая запись копирует массив.

---

# JAVA-COL-014

## Название

Collections.synchronizedList()

Severity

Medium

---

Проверить

не станет ли коллекция
узким местом.

---

# JAVA-COL-015

## Название

ConcurrentHashMap не используется

Severity

Medium

---

Что искать

HashMap

используется
из нескольких потоков.

---

# JAVA-COL-016

## Название

containsKey()

с последующим get()

Severity

Low

---

Что искать

```java
if(map.containsKey(k)){

    map.get(k);

}
```

---

Исправление

Использовать

```
get()
```

один раз.

---

# JAVA-COL-017

## Название

computeIfAbsent()

не используется

Severity

Low

---

# JAVA-COL-018

## Название

toArray()

в горячем цикле

Severity

Medium

---

Почему

Создаются новые массивы.

---

# JAVA-COL-019

## Название

Создание временных коллекций

Severity

Medium

---

Что искать

Новые List

Map

Set

в каждой итерации.

---

# JAVA-COL-020

## Название

Коллекция используется только для поиска

Severity

Medium

---

Исправление

HashSet.

---

# JAVA-COL-021

## Название

Сортировка внутри цикла

Severity

Critical

---

Почему

Одинаковая коллекция
сортируется многократно.

---

# JAVA-COL-022

## Название

distinct()

можно заменить Set

Severity

Low

---

# JAVA-COL-023

## Название

merge нескольких коллекций

в цикле

Severity

Medium

---

# JAVA-COL-024

## Название

Большая коллекция удерживается дольше необходимого

Severity

Medium

---

Почему

Рост использования Heap.

---

# JAVA-COL-025

## Название

Коллекции ограничивают масштабирование

Severity

High

---

Если обнаружены

- contains() в цикле
- indexOf()
- вложенные циклы
- повторные сортировки
- временные коллекции
- массовые allocations

следует отметить

**локальные алгоритмы ограничивают производительность сервиса и увеличивают потребление CPU при росте нагрузки.**

---

# Проверить дополнительно

- List
- Set
- Map
- HashMap
- HashSet
- TreeMap
- TreeSet
- ConcurrentHashMap
- ArrayList
- LinkedList
- CopyOnWriteArrayList
- synchronized collections
- contains()
- indexOf()
- remove()
- sort()
- initialCapacity

---

# Наиболее критичные правила

JAVA-COL-001

JAVA-COL-003

JAVA-COL-004

JAVA-COL-021

JAVA-COL-025