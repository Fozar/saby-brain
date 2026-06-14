---
type: concept
title: "Wasaby Python Patterns"
updated: 2026-04-10
tags:
  - wasaby
  - python
  - patterns
  - exceptions
status: current
related:
  - "[[Python-Code-Standards-SBIS]]"
  - "[[Wasaby-BL-Methods]]"
  - "[[Wasaby-BL-Advanced]]"
  - "[[Wasaby-CPP-Python-Integration]]"
  - "[[Wasaby-RecordSet-Performance]]"
created: 2026-04-10
---

# Wasaby Python Patterns

Паттерны Python для разработки на платформе Wasaby/SBIS. Дополняет [[Python-Code-Standards-SBIS]].

## Exceptions (Исключения)

### sbis.Error

Пользовательская ошибка. Первый аргумент — технические детали, второй — сообщение для пользователя.

```python
try:
    classifiers = Классификаторы.СписокПоПолномуКоду(
        None, Record({'ПолныйКодКлассификатора': 'ОКЕИ'}), None, None
    )
except Exception as e:
    raise sbis.Error(e.details, 'Сервис классификаторов временно недоступен.') from e
```

### sbis.Warning

Предупреждение (не прерывает выполнение на уровне платформы, но должно быть обработано).

```python
orphan_rows = check_orphan_rows(doc_id)
if orphan_rows:
    raise sbis.Warning(
        user_msg=sbis.rk('Ошибка проведения. {0}'.format(orphan_rows)),
        details='Ошибка проведения. {0}'.format(orphan_rows)
    )
```

## Critical Resources (Критически важные ресурсы)

> [!key-insight] Правило
> При работе с критически важными ресурсами (файлами, транзакциями) — **всегда использовать `with`**. Python имеет неочевидные утечки без него.

### Транзакции

```python
# ❌ Устарело — транзакция может не закрыться при исключении
tr = CreateTransaction(TransactionLevel.READ_COMMITTED, TransactionMode.WRITE)
SqlQuery('INSERT INTO "SomeTable1" DEFAULT VALUES')
SqlQuery('INSERT INTO "SomeTable2" DEFAULT VALUES')
return True

# ✅ Правильно — ресурс освобождается в любом случае
with CreateTransaction(TransactionLevel.READ_COMMITTED, TransactionMode.WRITE):
    SqlQuery('INSERT INTO "SomeTable1" DEFAULT VALUES')
    SqlQuery('INSERT INTO "SomeTable2" DEFAULT VALUES')
    return True
```

`CreateTransaction` без `with` — устарело. В логи записывается ошибка.

### Уровни транзакций (TransactionLevel)
- `READ_COMMITTED` — стандартный; не видит незафиксированные изменения
- `REPEATABLE_READ` — повторяемое чтение
- `SERIALIZABLE` — полная изоляция

### Режимы транзакций (TransactionMode)
- `WRITE` — операции записи
- `READ` — только чтение

## File Operations (Работа с файлами Python)

При работе с файлами также использовать `with`:

```python
# ✅ Правильно
with open('path/to/file', 'r') as f:
    content = f.read()

# ✅ Запись в файл
with open('path/to/file', 'w') as f:
    f.write(data)
```

## Record/RecordSet Performance

> [!key-insight] Мост Python↔C++ стоит дорого
> Каждое обращение к полю Record/RecordSet пересекает C++-границу. Ключевые паттерны: `rs.AddRow()` без аргументов, `rec.Fill({...})`, `ToListOf(DataClass)`, `SqlQueryOf`. Подробнее: [[Wasaby-RecordSet-Performance]].

Главные практики:
- `rec = rs.AddRow()` (без аргументов) — не копирует запись, в отличие от `rs.AddRow(rec)`
- `rec.Fill({"Foo": 10, "Bar": True})` — массовое заполнение без создания IField на каждое поле
- `rs.ToListOf(DataClass, fields)` — конвертировать RecordSet в dataclasses для вычислительного кода
- `SqlQueryOf(DataClass, ...)` — обойти RecordSet полностью, когда нужен только список объектов
- Проверку `"Field" in rs.Format()` делать **до** цикла, не внутри

## C++/Python Integration Pitfalls

> [!danger] Крэши, не исключения
> Record и RecordSet — C++-объекты. Неправильная работа со ссылками приводит к **падению процесса** (SIGSEGV), а не к Python-исключению. Подробнее: [[Wasaby-CPP-Python-Integration]].

Три анти-паттерна, вызывающих крэш:

1. **Ссылка на удалённую строку** — сохранить `rec = rs[0]`, затем `rs.DelRow(0)`, затем обратиться к `rec`.
2. **Ссылка при изменении формата** — сохранить `rec = rs[0]`, затем `rs.AddColInt32(...)`, затем обратиться к `rec`.
3. **Ссылка в замыкании** — передать `rec` в `InvokeOnTransactionCommit` без копирования. Исправление: `Record(rec)`.

## Связанные темы

- [[Python-Code-Standards-SBIS]] — стандарты кода (120 chars, CamelCase, без wildcard imports)
- [[Python-Localization-rk]] — rk() для локализации строк
- [[Wasaby-BL-Advanced#Custom-Method]] — конфиденциальные данные в методах
- [[Wasaby-CPP-Python-Integration]] — полный разбор C++/Python анти-паттернов с примерами кода
- [[Wasaby-RecordSet-Performance]] — оптимизация Record/RecordSet: Fill, AddRow, ToListOf, SqlQueryOf
- [[PriceFormation-Common-Helpers]] — assert_param/logging/wrappers/lock helpers в priceformationcommon
- [[DCCommon-Helpers]] — barcode, encryption, bonus balance calculation в DCCommon
