---
address: c-000121
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby ClickHouse Integration (Dbi Clickhouse)"
tags:
  - wasaby
  - backend
  - clickhouse
  - database
  - olap
  - python
  - cpp
status: current
related:
  - "[[Wasaby-SQL-DBA]]"
  - "[[Wasaby-BL-Objects]]"
sources:
  - ".raw/wasaby.Backend/Middleware/Работа с СУБД ClickHouse в проектах СБИС/Работа с СУБД ClickHouse в проектах СБИС.pdf"
---

# Wasaby ClickHouse Integration

ClickHouse — столбцовая СУБД для OLAP-задач. Используется для анализа больших объёмов данных (счётчики, статистика, история).

## ClickHouse НЕ умеет

- Транзакции
- UPDATE / DELETE в стандартном понимании
- OLTP-запросы ("выдай всех пользователей-мужчин" — нет; "сколько пользователей-мужчин" — да)
- Хранить большие объёмы данных в одной ячейке

**Модуль СБИС пока не поддерживает**: multitenancy, сложные типы данных.

## Подключение

SDK-модули: **Dbi Clickhouse** (C++) и **Dbi Clickhouse Py** (Python).

**В облаке**: создать кластер ClickHouse с именем `Статистика облака.ClickHouse.TCP.Адрес`.

**Локальный стенд** (`service/sbis-rpc-service.ini`):
```ini
[clusters.Статистика облака.ClickHouse.TCP]
Адрес=[{"master":"clickhouse-ch1:9000 login=Viewer password=Viewer1234"},
        {"master":"clickhouse-ch2:9000 login=Viewer password=Viewer1234"}]
```

## API (namespace: `sbisdbiclickhouse`)

### Чтение

```python
import sbisdbiclickhouse

db = sbisdbiclickhouse.GetConnectedDatabase()
# Работать как с обычной БД через SqlQuery() или IStatement
```

```cpp
auto db = dbi::clickhouse::GetConnectedDataDB();
// SqlQuery(*db, L"SELECT ...")
```

> [!warning] Экранирование
> ClickHouse использует другое экранирование, чем PostgreSQL. Нельзя использовать `SqlIdentifier`/`SqlLiteral`. Использовать **`EscapeIdentifier`** и **`EscapeLiteral`** из классов `IDatabase` и `IStatement`.

### Запись — TableCopier (рекомендуется)

```python
db = sbisdbiclickhouse.GetConnectedDatabase()
format = sbisdbiclickhouse.TableFormat(db, "default.test_table")
tc = db.CreateTableCopier(format)
rec = Record(format)
for i in range(0, 10):
    rec['field1'] = value1
    rec['field2'] = value2
    rec['field3'] = value3
    tc.AddRecord(rec)
tc.Flush()
```

```cpp
auto db = dbi::clickhouse::GetConnectedDataDB();
auto copier = db->CreateTableCopier(CreateRecFormat(L"test_table"));
*copier << value1 << value2 << value3;
copier->Flush();
```

> [!warning] INSERT через SqlQuery — запрещён
> `SqlQuery(db, "INSERT INTO table VALUES($1,$2,$3)", v1, v2, v3)` — нельзя! ClickHouse плохо обрабатывает частые одиночные вставки.
> Можно: `SqlQuery(db, "INSERT INTO default.copy SELECT * FROM default.orig")`

### Удаление и изменение схемы

```python
db = sbisdbiclickhouse.GetConnectedDatabase()
SqlQuery(db, "ALTER TABLE default.test_table ON CLUSTER test_cluster DELETE WHERE field1=1")
```

```cpp
auto db = dbi::clickhouse::GetConnectedDataDB();
SqlQuery(*db, L"ALTER TABLE default.test_table ON CLUSTER test_cluster DELETE WHERE field1=1"_sv)
```

`ON CLUSTER` обязателен для корректной репликации при ALTER TABLE.

## Связанные страницы

- [[Wasaby-SQL-DBA]] — PostgreSQL и инструменты анализа запросов
- [[Wasaby-BL-Objects]] — методы БЛ, из которых вызывается ClickHouse API
