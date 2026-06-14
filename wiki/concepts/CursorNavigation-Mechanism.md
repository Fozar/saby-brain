---
type: concept
title: "Cursor Navigation Mechanism"
tags: [price-formation, common, python, navigation, cursor, pagination, sql]
status: evergreen
related:
  - "[[PriceFormation-Backend-Architecture]]"
  - "[[PriceFormationOnline-Core]]"
  - "[[PriceFormationOnline-Helpers]]"
  - "[[Report-Prefetch-Service]]"
created: 2026-04-14
updated: 2026-04-14
---

# Cursor Navigation Mechanism

Модуль `priceformationcommon/core/cursor_navigation.py` — универсальный механизм курсорной пагинации для SQL-запросов в price-formation. Работает с платформенным `sbis.Navigation` и генерирует SQL-выражения для `WHERE`, `ORDER BY`, `LIMIT`.

---

## Ключевые типы

### `NavField` (namedtuple)

Описывает одно поле навигации:

```python
NavField('PED."ДатаВремя"', 'NavKey', 'TIMESTAMPTZ')
NavField('PED."@ВидЦеныДокумент"', 'RowId', 'INT')
```

- `nav_expression` — левая часть WHERE и ORDER BY (SQL-выражение)
- `key_name` — имя поля для извлечения позиции из результата
- `key_type` — SQL тип для каста (`::TIMESTAMPTZ`, `::INT` и т.д.)

### `NavigationParams` (namedtuple)

```python
NavigationParams(direction, limit, position, position_included)
```

- `direction` — `ndFORWARD` / `ndBACKWARD` / `ndBOTHWAYS`
- `limit` — кол-во записей в порции
- `position` — `dict` с текущей позицией курсора или `None` (первая порция)
- `position_included` — включать ли запись на позиции в результат

### `NextPositionMetadataType`

`Optional[List[Dict[str, Any]]]` — список всегда из одного элемента (требование платформенного компонента списков).

---

## Основные функции

### `get_list_by_cursor` — точка входа

```python
get_list_by_cursor(
    sql_method, _filter, navigation,
    nav_fields,         # List[NavField] или str (устаревший вариант)
    reverse=False,      # True → вперёд=DESC, назад=ASC
    with_next_position=True
) -> sbis.RecordSet | None
```

Логика:
1. `get_navigation_params` → `NavigationParams`
2. Запрос `ndFORWARD` → `_get_list_with_cursor_metadata(..., order='ASC')`
3. Запрос `ndBACKWARD` → `_get_list_with_cursor_metadata(..., order='DESC')`, затем `_reverse(result)`
4. `ndBOTHWAYS` → оба запроса, объединение: `result_bwd.Extend(result_fwd)`, `NavigationResult(has_bwd, has_fwd)`, `SetMetadataHashTable('nextPosition', {'forward':..., 'backward':...})`
5. Для одного направления: `result.nav_result = sbis.NavigationResult(has_more)` + `AddJson('nextPosition', next_position)`

**Требования к SQL-запросу** (шаблонизатор):

```sql
{% ifdef nav_condition %}
WHERE !nav_condition
{% endif %}

{% ifdef order_expression %}
ORDER BY !order_expression
{% endif %}

{% ifdef limit %}
LIMIT !limit
{% endif %}
```

### `get_nav_expressions` — генерация SQL-выражений

```python
get_nav_expressions(
    nav_fields, position=None, order=None,
    limit=None, position_included=False,
    with_cursor_metadata=False
) -> Tuple
```

Возвращает кортеж:
- Вариант (1) `List[NavField]`: `(nav_condition, order_expression, limit)`
- Вариант (2) `str`: `(nav_key, nav_operator, order, limit)`

Операторы сравнения:
- `position_included=True`: `<=` (DESC) / `>=` (ASC)
- `position_included=False`: `<` (DESC) / `>` (ASC)

При `position=None` → `nav_condition = 'TRUE'`.

Для нескольких полей навигации строится tuple-сравнение:
```sql
(expr1, expr2) < (val1::TYPE1, val2::TYPE2)
```
Если какое-то поле в `position` равно `None` — цепочка обрывается на нём.

`with_cursor_metadata=True` добавляет `+1` к лимиту для определения наличия следующей страницы.

### `get_navigation_params` — нормализация параметров

Приводит `sbis.Navigation` к `NavigationParams`. Поддерживает три формата `position`:
1. `None` — первая порция
2. Запись с полем `cursor` (список на фронте _со_ следующей позицией в метаданных)
3. Запись с прямыми полями навигации (список на фронте _без_ метаданных)

Фильтрует `position` по полям из `nav_fields` (если передан) — чтобы лишние поля не вызывали ошибок в `get_list_by_cursor`.

При `ntNULL` или `navigation=None` → defaults: `direction=ndFORWARD`, `limit=10000`, `position=None`.

`position_included = (direction == ndBOTHWAYS)` — при двустороннем запросе текущая позиция включается.

### `add_cursor_params` — подстановка в шаблон

```python
add_cursor_params(params, nav_condition, order_expression, limit)
```

Добавляет в словарь `params` ключи `nav_condition`, `order_expression`, `limit` как `sbis.TemplateExecutor(sbis.Template(...))`.

### `_get_list_with_cursor_metadata` — внутренний исполнитель

1. Вызывает `get_nav_expressions(..., with_cursor_metadata=True)` → лимит `+1`
2. Вызывает `sql_method`
3. Если `result.Size() == limit` → есть следующая страница:
   - Удаляет последнюю запись `DelRow(result.Size() - 1)`
   - Извлекает `next_nav_position` из предпоследней (`extract(result[-1], nav_key_name_list)`)
   - Сериализует: int и None — как есть, остальное → `str(v)`

### Вспомогательные функции

| Функция | Назначение |
|---|---|
| `get_empty_list_by_cursor(navigation, record_set)` | Пустой результат с корректными `nav_result` метаданными |
| `get_next_position_metadata(next_position, nav_field_list)` | Новая версия сериализации позиции (TODO: заменить inline в `_get_list_with_cursor_metadata`) |
| `navigation_from_record(value)` | Создать `sbis.Navigation` из `sbis.Record` (Direction/Limit/Position) |
| `valid_cursor_navigation(value)` | Валидатор: `ntNULL` или `ntPOSITION` + не `ndBOTHWAYS` без позиции |
| `valid_navigation_record(value)` | Валидатор для записи с параметрами навигации |

---

## Два варианта nav_fields

| Вариант | Тип | Когда использовать |
|---|---|---|
| (1) современный | `List[NavField]` | Всегда для новых методов; поддерживает многополевую навигацию |
| (2) устаревший | `str` | Обратная совместимость; одно поле, другой интерфейс `sql_method` |

В варианте (2) `sql_method` принимает `(filter, nav_key, nav_operator, order, limit)`.
В варианте (1) `sql_method` принимает `(filter, nav_condition, order_expression, limit)`.

---

## Паттерн использования

```python
from priceformationcommon.core.cursor_navigation import (
    NavField, get_list_by_cursor, add_cursor_params, get_navigation_params
)

NAV_FIELDS = [
    NavField('PED."ДатаВремя"', 'NavKey', 'TIMESTAMPTZ'),
    NavField('PED."@ВидЦеныДокумент"', 'RowId', 'INT'),
]

def _sql_get_events(_filter, nav_condition, order_expression, limit):
    params = {'filter': _filter}
    add_cursor_params(params, nav_condition, order_expression, limit)
    return sbis.SqlQuery('...', params)

def get_events(_filter, navigation):
    return get_list_by_cursor(_sql_get_events, _filter, navigation, NAV_FIELDS)
```

---

## Сериализация позиции

`next_nav_position` хранится как `List[Dict[str, str | int | None]]`.
Правило: `int` и `None` — без изменений, всё остальное → `str(v)`.
Это покрывает `Decimal`, `datetime`, `UUID` и др.

TODO (в коде): унифицировать через `get_next_position_metadata` + добавить методы для десериализации с учётом типов полей.

---

## Связанные концепции

- [[PriceFormation-Backend-Architecture]] — где лежит этот модуль в общей структуре
- [[Report-Prefetch-Service]] — альтернативный механизм пагинации (мультинавигация, иерархия)
