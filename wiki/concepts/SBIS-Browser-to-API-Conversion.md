---
type: concept
address: c-000058
title: "SBIS: преобразование браузерного запроса в API-вызов"
created: 2026-05-21
updated: 2026-05-21
tags:
  - saby
  - api
  - sbis-mcp
  - recipe
status: current
related:
  - "[[SBIS-Record-Format]]"
  - "[[SBIS-DocumentMessage-ListForEDO]]"
  - "[[Saby-API-Protocol]]"
  - "[[SBIS-Internal-API-Methods]]"
---

# SBIS: преобразование браузерного запроса в API-вызов

Рецепт: берёшь запрос из DevTools → Network → копируешь как curl/fetch → превращаешь в вызов нашего `SbisClient.call()`.

---

## Откуда брать браузерный запрос

DevTools → Network → фильтр `service/?` → нужный запрос → Copy as fetch (или curl). Имя метода — в заголовке `X-CalledMethod` или в теле `.method`.

---

## Что такое браузерный формат

Браузер всегда отправляет **Protocol 7** ([[SBIS-Record-Format]]): `d` и `s` как **массивы**, плюс `_type` и `f`.

```json
{
  "jsonrpc": "2.0",
  "protocol": 7,
  "method": "DocumentMessage.ListForEDO",
  "params": {
    "Фильтр": {
      "d": [true, "uuid-doc", "uuid-doc", "up", "after"],
      "s": [
        {"t": "Логическое", "n": "appendLikes"},
        {"t": "Строка",     "n": "document"},
        {"t": "Строка",     "n": "fromTheme"},
        {"t": "Строка",     "n": "scroll"},
        {"t": "Строка",     "n": "toRequestOnly"}
      ],
      "_type": "record",
      "f": 0
    },
    "Навигация": {
      "d": ["forward", true, 20, null],
      "s": [
        {"t": "Строка",      "n": "Direction"},
        {"t": "Логическое",  "n": "HasMore"},
        {"t": "Число целое", "n": "Limit"},
        {"t": "Запись",      "n": "Position"}
      ],
      "_type": "record",
      "f": 0
    }
  }
}
```

---

## Алгоритм преобразования

Большинство внутренних методов принимают и **Protocol 1/2** — `d`/`s` как объекты. Это гораздо удобнее для программной генерации.

### 1. Разворачиваем `d` + `s` → dict

Берём `s[i].n` как ключ, `d[i]` как значение:

```python
# Browser (Protocol 7)
"d": [true, "uuid", "uuid", "up", "after"]
"s": [{"n": "appendLikes"}, {"n": "document"}, ...]

# API (Protocol 1/2)
"d": {"appendLikes": true, "document": "uuid", ...}
"s": {"appendLikes": "Логическое", "document": "Строка", ...}
```

Схема `s` тоже становится dict: `{fieldName: typeName}`.

### 2. Убираем `_type` и `f`

В Protocol 1/2 они не нужны.

### 3. Вложенные записи (Position и другие `Запись`-поля)

Если поле имеет тип `"Запись"` и содержит вложенный record — аналогично разворачиваем:

```python
# Browser (Position при пагинации):
"Position": {
  "d": ["2026-04-23 09:10:23.103000+0300"],
  "s": [{"t": "Строка", "n": "themeDatetime"}],
  "_type": "record",
  "f": 1
}

# API (Protocol 1/2 — оставить как есть, метод принимает):
"Position": {
  "d": ["2026-04-23 09:10:23.103000+0300"],
  "s": [{"t": "Строка", "n": "themeDatetime"}],
  "_type": "record",
  "f": 1
}
```

> Вложенные `Запись`-поля с `_type`/`f` передаём **без изменений** — сервер ожидает именно их. Трансформируем только верхний уровень `Фильтр`/`Навигация`.

### 4. Null-позиция — упрощаем

Если `Position: null` (первая страница), можно вместо полной структуры Навигации передать `None`:

```python
# Вместо всей структуры Навигации с Position=null:
"Навигация": None
```

Некоторые методы это принимают. Если нет — вернуть полную структуру с `"Position": null`.

---

## Итоговый результат для `DocumentMessage.ListForEDO`

```python
params = {
    "Фильтр": {
        "s": {
            "appendLikes":   "Логическое",
            "document":      "Строка",
            "fromTheme":     "Строка",
            "scroll":        "Строка",
            "toRequestOnly": "Строка",
        },
        "d": {
            "appendLikes":   True,
            "document":      document_id,
            "fromTheme":     document_id,
            "scroll":        "up",
            "toRequestOnly": "after",
        },
    },
    "Навигация": {
        "s": {
            "Direction": "Строка",
            "HasMore":   "Логическое",
            "Limit":     "Число целое",
            "Position":  "Запись",
        },
        "d": {
            "Direction": "forward",
            "HasMore":   True,
            "Limit":     limit,
            "Position":  nav_position,  # None или {"d":[datetime],"s":[...],"_type":"record","f":1}
        },
    },
    "Сортировка": None,
    "ДопПоля":    [],
}
```

Наш `SbisClient.call()` сам обернёт это в JSON-RPC конверт (без `"protocol":7`).

---

## Шпаргалка трансформации

| Браузер (Protocol 7)                        | API (Protocol 1/2)                      |
|---------------------------------------------|-----------------------------------------|
| `"d": [v1, v2, v3]`                         | `"d": {"field1": v1, "field2": v2}`     |
| `"s": [{"n":"f","t":"Строка"}, ...]`        | `"s": {"f": "Строка", ...}`             |
| `"_type": "record"`, `"f": 0`               | убрать                                  |
| Вложенный `Запись`-field (Position и др.)   | оставить как есть (с `_type`/`f`)       |
| `"Position": null`                          | `"Position": null` или `"Навигация": None` |
| `"protocol": 7` в конверте                  | убрать (наш клиент не ставит)           |

---

## Возможные ошибки

- **"Блок данных должен быть объектом"** — метод ожидает объектный `d`, а получил массив (или наоборот). Проверь какой протокол принимает конкретный метод.
- **"Неизвестная строковая константа типа поля n"** — метод не принимает Protocol 1/2 вообще. Причина: в `s`-объекте значение типа оказалось объектом (`{"n":"Массив","t":"Строка"}`), сервер пытается прочитать его как строку и спотыкается на ключе `"n"`. Решение: откатиться на Protocol 7 (массивы + `_type` + `f`) целиком.
- **Position не работает** — убедись, что вложенный record для Position передан в полном виде (с `_type`, `f`, `s` как массив), а не в упрощённом.
- **Поле не передаётся** — в Protocol 1/2 можно просто не включать необязательные поля в `d` и `s`. В Protocol 7 порядок в `d` строго соответствует порядку в `s`.

## entity.Record как именованный параметр

Если браузер строит параметр через `new entity.Record({rawData: {...}})` и передаёт его как именованный аргумент:

```js
var params = {'docRec': param0};
new source.SbisService(...).call('ПолучитьДанныеОДокументе', params);
```

В JSON-RPC теле rawData уходит **напрямую** под ключом `docRec` — без трансформации `s`/`d`, без `protocol: 7`:

```json
{
  "jsonrpc": "2.0",
  "method": "Документ.ПолучитьДанныеОДокументе",
  "params": {
    "docRec": {
      "_type": "record",
      "d": ["guid-value", "", ...],
      "s": [
        {"n": "docGuid", "t": "Строка"},
        ...
      ]
    }
  },
  "id": 1
}
```

Правило: трансформация Protocol 7 → 1/2 применяется только к `Фильтр`/`Навигация`/`Сортировка`. `entity.Record`-параметры передаются as-is.
