---
address: c-000122
created: 2026-06-14
updated: 2026-06-14
type: concept
title: "Wasaby Full-Text Search (sbis_fts)"
tags:
  - wasaby
  - backend
  - search
  - elasticsearch
  - python
  - middleware
status: current
related:
  - "[[Wasaby-BL-Objects]]"
  - "[[Wasaby-BL-Calls]]"
sources:
  - ".raw/wasaby.Backend/Middleware/Поиск/Полнотекстовый поиск/Полнотекстовый поиск.pdf"
  - ".raw/wasaby.Backend/Middleware/Поиск/Полнотекстовый поиск/Python API полнотекстового поиска.pdf"
---

# Wasaby Full-Text Search (sbis_fts)

Полнотекстовый поиск платформы Wasaby построен на **Elasticsearch**, но взаимодействие только через SDK-модуль — прямого доступа к ES нет. Это позволяет менять поисковый движок без изменения кода.

**Возможности**: морфологический поиск, префиксный, устранение опечаток, поиск в переключённой раскладке, фильтрация и агрегация по иерархии.

## Подключение

SDK-модули: подключить модули полнотекстового поиска к проекту.

Структура поискового объекта описывается в файле `.ftsx` (метаданные приложения).

## Python API (модуль sbis_fts)

```python
import sbis
import sbis_fts

obj = sbis_fts.Object('test_index')  # имя объекта из .ftsx
```

### CRUD-методы

| Метод | Описание | Возвращает |
|-------|----------|------------|
| `Upsert(data: sbis.Record)` | Запись/обновление (partial update) | `UpsertResult(id)` |
| `MultiUpsert(data: sbis.RecordSet)` | Массовый upsert | `MultiUpsertResult(items: [{id, error}])` |
| `Read(id: str)` | Чтение по ID | `ReadResult(id, data: sbis.Record)` |
| `MultiRead(ids: List[str])` | Массовое чтение | `MultiReadResult(items: [{id, data, error}])` |
| `Delete(id: str)` | Удаление | `DeleteResult(id)` |
| `MultiDelete(ids: List[str])` | Массовое удаление | `MultiDeleteResult(items: [{id, error}])` |
| `MultiDeleteByList(selectName, params)` | Удаление по поисковому запросу | `MultiDeleteResult` |

### Запись объектов

```python
# Одиночная запись
data = sbis.Record()
data.AddString('id', 'c548b46d-2ea0-414b-a8d8-dd2fa228c89b')
data.AddString('text_search_field', 'Тест')
obj.Upsert(data)

# Массовая запись
f = sbis.RecordFormat()
f.AddString("id")
f.AddString("text_search_field")
data = sbis.RecordSet(f)
r1 = sbis.Record(f)
r1["id"].From("1dac4a56-...")
r1["text_search_field"].From("multi upsert str 1")
data.AddRow(r1)
obj.MultiUpsert(data)
```

### Поиск (List)

```python
list_params = sbis_fts.Object.ListParams()
list_params.searchString = 'тест'           # строка поиска (необяз.)
list_params.filter = sbis.Record()           # поля фильтрации (необяз.)
list_params.filter.AddUuid('uuid_filter_field', '8cbb1d2e-...')
list_params.exactMatch = False               # точное совпадение (необяз.)
# list_params.navigation = sbis.Navigation() # навигация (необяз.)

list_result = obj.List('method_name', list_params)
for item in list_result.items:
    print(item.id, item.score, item.data, item.highlight)
```

Результат `List`:
- `items[].id` — идентификатор
- `items[].score` — релевантность
- `items[].data` — sbis.Record с возвращаемыми полями
- `items[].highlight` — sbis.Record с подсветкой найденных фрагментов
- `navigationResult` — данные пагинации
- `dataFormat`, `highlightFormat` — форматы записей

### Поиск по иерархии

```python
list_params = sbis_fts.Object.ListParams()
list_params.searchString = 'папка'
list_params.filter = sbis.Record()
list_params.filter.AddUuid('hierarchy_filter_field', '80904afa-148d-11ed-...')
list_result = obj.List('default', list_params)
# Вернёт дочерние объекты относительно указанного UUID
```

### Агрегация

```python
searchData = sbis.Record()
searchData.AddString('selectName', 'default')
searchData.AddString('searchString', 'сын')

# Только агрегация (4 типа: terms, max, min, avg)
aggregation = sbis.Record()
aggregation.AddString('type', 'max')
aggregation.AddString('field', 'int_filter_field')
agg_result = FullTextSearch.Aggregation('test_index', searchData, aggregation)

# Поиск + агрегация одновременно
aggregation.AddString('type', 'terms')
aggregation.AddString('field', 'text_array_filter_field')
agg_result = FullTextSearch.ListWithAggregation('test_index', searchData, aggregation)
# items[] — найденные объекты с подсветкой
# aggregation.items[] — RecordSet(key, count) с частотами
```

## Типы полей в .ftsx

| Тип поля | Назначение |
|----------|------------|
| `string` | Текстовое поле поиска |
| `string array` | Массив строк для поиска |
| `RPCFILE` | Поиск по файлу |
| `int` | Числовой фильтр |
| `hierarchy` | Иерархический фильтр |

Параметр `boost` в `.ftsx` задаёт приоритет поля при ранжировании (например, `boost=16` для основного поля).

## Связанные страницы

- [[Wasaby-BL-Objects]] — методы БЛ, вызывающие FTS API
- [[Wasaby-ClickHouse]] — аналитические запросы (агрегация без полнотекстового поиска)
