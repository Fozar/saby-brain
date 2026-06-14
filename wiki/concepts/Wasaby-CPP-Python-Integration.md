---
type: concept
title: "Wasaby C++/Python Integration Pitfalls"
updated: 2026-04-10
tags:
  - wasaby
  - python
  - cpp
  - record
  - recordset
  - crash
  - anti-patterns
status: current
related:
  - "[[Wasaby-Python-Patterns]]"
  - "[[Wasaby-RecordSet-Join]]"
  - "[[Wasaby-Data-Types]]"
created: 2026-04-10
---

# Wasaby C++/Python Integration Pitfalls

Record и RecordSet — C++-объекты, доступные из Python. Неправильная работа со ссылками на них **не вызывает Python-исключений** — процесс падает с крэшем (SIGSEGV). Три задокументированных анти-паттерна.

> [!danger] Крэш, не исключение
> Все три паттерна ниже приводят к **падению процесса** (crash), а не к `Exception`. Стандартный `try/except` не поможет.

---

## Анти-паттерн 1: Захват ссылки на удалённый Record

Сохранение Python-ссылки на запись RecordSet, после чего строка удаляется из RecordSet.

```python
# ❌ КРЭШ — rec становится dangling pointer после DelRow
rs = RecordSet(...)
rec = rs[0]          # захватили ссылку на Record внутри RecordSet
rs.DelRow(0)         # C++ удалил объект
print(rec['Field'])  # CRASH: обращение к освобождённой памяти
```

**Правило:** никогда не хранить ссылку на `rs[i]` после любой операции удаления строки из RecordSet.

---

## Анти-паттерн 2: Захват ссылки с последующим изменением формата

Сохранение Python-ссылки на Record, после чего изменяется формат (схема) RecordSet.

```python
# ❌ КРЭШ — rec становится невалидным после изменения формата
rs = RecordSet(...)
rec = rs[0]                  # захватили ссылку
rs.AddColInt32("NewColumn")  # C++ перестроил внутреннюю структуру
print(rec['ExistingField'])  # CRASH: структура памяти изменилась
```

**Правило:** все изменения формата RecordSet должны происходить **до** захвата ссылок на его записи.

---

## Анти-паттерн 3: Захват ссылки в замыкание (callback)

Передача Python-ссылки на Record/RecordSet в callback, который вызывается позже (например, `InvokeOnTransactionCommit`). К моменту вызова callback объект может быть уже удалён.

```python
# ❌ КРЭШ — rec может быть невалиден к моменту вызова callback
rec = rs[0]

def on_commit():
    do_something(rec['Field'])  # rec уже может не существовать!

InvokeOnTransactionCommit(on_commit)
```

```python
# ✅ Правильно — передаём КОПИЮ
rec = rs[0]
rec_copy = Record(rec)  # создаём независимую копию

def on_commit():
    do_something(rec_copy['Field'])  # безопасно: копия живёт независимо

InvokeOnTransactionCommit(on_commit)
```

**Правило:** при передаче данных из Record/RecordSet в любой отложенный callback — создавать копию через `Record(rec)`.

---

## Сводная таблица

| Анти-паттерн | Триггер крэша | Исправление |
|---|---|---|
| Ссылка на удалённую строку | `rs.DelRow(i)` после `rec = rs[i]` | Не хранить `rs[i]` через удаление |
| Ссылка при изменении формата | `rs.AddColXxx(...)` после `rec = rs[i]` | Менять формат до захвата ссылок |
| Ссылка в замыкании | callback вызывается после уничтожения Record | `Record(rec)` — передавать копию |

---

## Общий принцип

> Python-переменная, ссылающаяся на `Record` из `RecordSet`, — это **не владеющая** ссылка. Lifetime объекта управляется C++, а не Python GC.

Безопасные сценарии:
- Использовать `rec` только **внутри** синхронного блока, не сохраняя в переменные с более широкой областью видимости
- Если нужно сохранить данные — читать значения в Python-словарь / создавать `Record(rec)` копию

## Связанные темы

- [[Wasaby-Python-Patterns]] — работа с транзакциями, исключениями, файлами
- [[Wasaby-RecordSet-Join]] — in-memory join операции над RecordSet
- [[Wasaby-Data-Types]] — типы полей Record/RecordSet
