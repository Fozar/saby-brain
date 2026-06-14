---
address: c-000106
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby SQL Dev Standard"
tags:
  - wasaby
  - standards
  - sql
  - database
  - backend
status: current
related:
  - "[[Wasaby-Dev-Standards]]"
  - "[[Wasaby-SQL-DBA]]"
sources:
  - ".raw/wasaby.Backend/Стандарты разработки/Стандарт разработки SQL.sabydoc"
---

# Wasaby SQL Dev Standard

Корпоративный стандарт написания SQL в СБИС 3.

## Именование объектов БД

- Язык: **английский** (не транслит), PascalCase, без пробелов
- Допустимые символы: буквы, цифры, подчёркивание
- Имена оборачиваются в двойные кавычки `""`
- Комментарии к таблицам и полям — **по-русски**, ёмко
- Имена таблиц и полей — в **единственном числе**: `Party`, `Document`, `Name`, `Sum`
- Создание объектов с именами на русском языке **запрещено**

### Соглашения по именованию

| Тип поля / объекта | Формат | Пример |
|---|---|---|
| Первичный ключ (identity) | `@<Таблица>` | `@Credit`, `@Document` |
| Связь расширения объекта | `<Таблица>_` | `Document_`, `Party_` |
| Иерархия — родитель (id) | `Parent` | `Parent` |
| Иерархия — узел/лист | `Parent@` | `Parent@` |
| PRIMARY KEY constraint | `p<Таблица>` | `pParty` |
| FOREIGN KEY constraint | `r<Таблица>-<Поле>` | `rSpare-WarehouseInfo` |
| Индекс | `i<Таблица>-<Индекс>` | `iAnalytic-Theme` |

По вопросам именования — обращаться к Голованову К.А.

## Оформление кода

- Отступ: **3 пробела** на каждом уровне
- Ограничения уровня столбца (PRIMARY / REFERENCES / UNIQUE / CHECK) — на уровень ниже
- Каждое поле на отдельной строке; типы полей выровнены по левому краю
- Ключевые слова (`SELECT`, `FROM`, `WHERE`, `JOIN`) — в **верхнем регистре**, один уровень отступа
- Запятая ставится **после** имени поля, не перед
- Алиасы — **без AS**: `SELECT "fld" fldX FROM ...`
- Метод объединения таблиц (`INNER JOIN`, `LEFT JOIN`) — на отдельной строке, на уровне `SELECT/FROM`
- Логический оператор (`AND`/`OR`) — в **конце** строки
- Условие в WHERE — каждое на отдельной строке, на уровень ниже WHERE

## Паттерны

### Получение данных
```sql
SELECT
   "Field0",
   "Field1",
FROM
   (SELECT "T0"."Fld" "fldX"
    FROM   "Table0" "T0"
    INNER JOIN "T1" USING("Fld") "T"
    WHERE  ...
    GROUP BY ...
    ORDER BY ...
    HAVING ...) "T"
```

### Создание таблицы
```sql
CREATE TABLE "Table" (
   "Field0" type0
      PRIMARY KEY,
   "Field1" type1,
   UNIQUE("Field0", "Field1"),
   FOREIGN KEY("Field0") REFERENCES "Table2"("Fld0") ON UPDATE CASCADE ON DELETE CASCADE DEFERRABLE
)
```

### Изменение таблицы
```sql
ALTER TABLE "Table"
   ADD COLUMN "Field0" type0,
   ADD CONSTRAINT "ref" FOREIGN KEY("Field0") REFERENCES "Table2"("Fld0") ON UPDATE CASCADE DEFERRABLE
```

### Создание индекса
```sql
CREATE INDEX "Idx" ON "Table"("Field0", "Field1")
WHERE "Field0" <> '' AND "Field1" <> ''
```
