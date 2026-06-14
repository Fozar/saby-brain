---
type: concept
title: "Wasaby BL List Advanced Patterns"
updated: 2026-04-14
tags:
  - wasaby
  - business-logic
  - list-methods
  - navigation
  - cursor
  - mass-operations
status: current
related:
  - "[[Wasaby-BL-List-Methods]]"
  - "[[Wasaby-BL-Methods]]"
  - "[[Wasaby-DB-Access-Patterns]]"
  - "[[Wasaby-RecordSet-Performance]]"
  - "[[Loyalty-React-Migration-Project]]"
created: 2026-04-14
---

# Wasaby BL List Advanced Patterns

Расширенные паттерны работы со списочными методами: навигация по курсору, множественная навигация, порционная загрузка, массовые операции, поиск.

Базовый справочник: [[Wasaby-BL-List-Methods]].

---

## Стандартные параметры фильтрации

Предопределённые параметры, которые платформа использует в своих утилитах:

| Параметр | Тип | Семантика |
|----------|-----|-----------|
| `ИдО` | Int64 | Запросить конкретно этот объект (вернуть 1 или 0) |
| `СписокИдО` | String[] | Запросить конкретно эти объекты |
| `Раздел` | Int64/String | Узел иерархии, из которого возвращать данные |

> [!key-insight] Декларативный vs ручной
> Декларативный метод поддерживает `ИдО`, `СписокИдО`, `Раздел` **по умолчанию**.
> Ручной метод требует явной обработки в коде.

---

## Навигация по курсору

Курсорная навигация — выборка относительно фиксированной записи без обработки предыдущих страниц. Снижает нагрузку на БД по сравнению с постраничной.

### Предварительные условия

1. Создать **индекс** в БД по полям, однозначно идентифицирующим запись (через Genie → dicx).
2. Использовать тип метода **Manually implemented list**.

### Что принимает метод БЛ

```python
def MyListMethod(ДопПоля, Фильтр, Сортировка, Навигация):
    # Навигация — экземпляр sbis.Navigation
    my_limit = Навигация.Limit() + 1  # +1 для определения ЕстьЕще
```

### Что возвращает метод БЛ

RecordSet со свойством `nav_result = sbis.NavigationResult(has_more)`.

### Пример: все три направления

```python
def MyListMethod(ДопПоля, Фильтр, Сортировка, Навигация):
    my_limit = Навигация.Limit() + 1

    def get_nav_result(rs):
        if len(rs) > Навигация.Limit():
            rs.DelRow(len(rs) - 1)
            return True
        return False

    # Первый вызов — Position is None
    if Навигация.Position() is None:
        rs = sbis.SqlQuery(
            'SELECT * FROM "MyTable" WHERE "Раздел" IS NULL LIMIT $1 ORDER BY "timestamp" DESC',
            my_limit
        )
        rs.nav_result = sbis.NavigationResult(get_nav_result(rs))
        return rs

    my_cursor = Навигация.Position()['timestamp']
    my_direction = Навигация.Direction()

    if my_direction == sbis.NavigationDirection.ndFORWARD:
        rs = sbis.SqlQuery(
            'SELECT * FROM "MyTable" WHERE "Раздел" IS NULL AND "timestamp" < $1 LIMIT $2 ORDER BY "timestamp" DESC',
            my_cursor, my_limit
        )
        rs.nav_result = sbis.NavigationResult(get_nav_result(rs))
        return rs

    elif my_direction == sbis.NavigationDirection.ndBACKWARD:
        rs = sbis.SqlQuery(
            'SELECT * FROM (SELECT * FROM "MyTable" WHERE "Раздел" IS NULL AND "timestamp" > $1 LIMIT $2 ORDER BY "timestamp" ASC) AS Data ORDER BY "timestamp" DESC',
            my_cursor, my_limit
        )
        rs.nav_result = sbis.NavigationResult(get_nav_result(rs))
        return rs

    elif my_direction == sbis.NavigationDirection.ndBOTHWAYS:
        before_rs = sbis.SqlQuery(...)
        after_rs = sbis.SqlQuery(...)
        before_rs.nav_result = sbis.NavigationResult(get_nav_result(before_rs), get_nav_result(after_rs))
        before_rs.Extend(after_rs)
        return before_rs
```

### Переопределение позиции курсора (nextPosition)

При навигации в обе стороны — через `SetMetadataHashTable`:
```python
rs.SetMetadataHashTable("nextPosition", {"backward": [30, "Петров А.А."], "forward": [130, "Иванов А.А."]})
```

При навигации в одну сторону — через `Metadata().AddJson`:
```python
rs.Metadata().AddJson("nextPosition", [130, "Иванов А.А."])
```

---

## Порционная загрузка данных

Паттерн для итеративного получения больших наборов данных без блокировки клиента.

**Требования:**
1. Курсорная навигация (обязательно).
2. Вернуть **меньше данных**, чем запросил клиент.
3. Вернуть `ЕстьЕще = True`.
4. В метаданных установить `iterative=True` и следующий курсор:

```python
rs = GetReplyData()
rs.SetMetadataBool("iterative", True)
rs.SetMetadataHashTable("nextPosition", {"backward": [30, "Петров А.А."], "forward": [130, "Иванов А.А."]})
```

> [!key-insight] Связь с лояльностью
> Порционная загрузка применяется в 6 BL-методах проекта [[Loyalty-React-Migration-Project]]: Акции, ДК/Клиенты, Бонусы/Клиенты, Бонусы/Покупки, Промокоды, Реферальная/Покупки.

> [!key-insight] Реализация в price-formation
> [[LoyaltyPrograms-IterativeListLoading]] — полный стек: `ListWithCursor` → `ListWithCompositeCursor` + `IterativeBlockSizeEmaMixin` → `SaleListWithCursor`. Контрольная запись (`_IsControlRecord`), EMA адаптация блока, составной курсор как `[{key: val}]`.

---

## Множественная навигация (Multi-Root Navigation)

Используется для загрузки иерархического списка с **уже развёрнутыми узлами** (например, при reload с сохранением состояния дерева).

### Формат запроса

`Навигация` — RecordSet с полями:

| Поле | Описание |
|------|---------|
| `id` | Идентификатор узла (`null` = корень) |
| `nav` | Навигация для данного узла |

### Формат ответа

В метаданных RecordSet должен быть RecordSet `nextPosition` с полями `id` и `nav_result`.

### Пример реализации на Python

```python
MULTI_CURSOR_FRMT = CreateRecordFormat()
MULTI_CURSOR_FRMT.AddString('id')
MULTI_CURSOR_FRMT.AddJson('nav_result')

def Test.MultiRoot(ДопПоля, Фильтр, Сортировка, Навигация):
    rs = RecordSet(CurrentMethodResultFormat())

    if Навигация.Type() == NavigationType.ntMULTI_ROOT:
        multi_cursor = CreateRecordSet(MULTI_CURSOR_FRMT)
        for id, nav in Навигация.RootsDict().items():
            Фильтр.Раздел = id
            tmp_rs = Test.MultiRoot(ДопПоля, Фильтр, Сортировка, nav)
            for rec in tmp_rs:
                rs.AddRow(rec)
            cursor = multi_cursor.AddRow()
            cursor['id'].From(id)
            cursor['nav_result'].From(tmp_rs.Metadata().Get("nextPosition"))
        rs.Metadata().AddRecordSet("nextPosition", MULTI_CURSOR_FRMT, multi_cursor)
    else:
        rs = Test.DeclList(ДопПоля, Фильтр, Сортировка, Навигация)

    return rs
```

---

## Массовая отметка записей (ListIterator)

`ListIterator` (C++: `sbis-bl-core/helpers/list_iterator.hpp`, Python: `from sbis import ListIterator`) — оптимальный обход иерархического и плоского реестра для операций над отмеченными записями.

### Параметр фильтрации `selection`

| Поле | Тип | Описание |
|------|-----|---------|
| `marked` | String[] | Включённые в выборку (`null` = всё) |
| `excluded` | String[] | Исключённые из выборки |
| `type` | String | `all` / `leaf` / `node` |
| `types` | String[] | `leaf`, `node`, `hidden` |
| `recursive` | Boolean | Включать дочерние листья у отмеченных узлов (default: `true`) |

### Ключевые методы итератора

| Метод | Назначение |
|-------|-----------|
| `SetMassReading(True)` | Пакетный запрос через `СписокИдО` (vs единичный через `ИдО`) |
| `SetHierarchy("Раздел")` | Учёт иерархии |
| `SetKeyName("поле")` | Если PK не в первом поле |
| `SetNavigationType(...)` | Переключить на курсорную навигацию |
| `Iterate(callback)` | Запустить обход; callback получает RecordSet порцией |

Фильтр дополняется маркером `__WithIterativenessInMind`.

### Пример BLO.ListWithIterator

```python
# Python
@staticmethod
def ListWithIterator(ДопПоля, Фильтр, Сортировка, Навигация):
    if Фильтр.TestField("selection") is None:
        return BLO.List(ДопПоля, Фильтр, Сортировка, Навигация)

    class Result:
        def __init__(self):
            self.iterator = sbis.ListIterator("BLO.List", Фильтр)
            self.iterator.SetHierarchy("Раздел")
            self.iterator.SetMassReading(True)
            self.result = None

        def callback(self, rs):
            if self.result is None:
                self.result = sbis.RecordSet(rs.Format())
            for rec in rs:
                self.result.AddRow(rec)

        def get(self):
            self.iterator.Iterate(self.callback)
            return self.result

    return Result().get()
```

### Алгоритм работы

1. Итератор вызывает список с `СписокИдО` (из `marked`), удаляет `selection` из фильтра.
2. Callback получает найденные записи, исключает `excluded`.
3. Из оставшихся узлов повторяет вызов с параметром `Раздел` = массив id узлов.
4. Итерации продолжаются, пока не кончатся узлы (скрытые узлы).

---

## Показать отмеченные (ShowMarked)

`blhelpers.ShowMarked` возвращает отмеченные записи **вместе с путями** к ним (для хлебных крошек). Используется при нажатии кнопки "Показать отмеченные" в панели массовых операций.

**Условие вызова:** в фильтре присутствует параметр `SelectionWithPath`.

**Требования к списочному методу:**
- Курсорная навигация.
- Поддержка `СписокИдО`.
- При иерархии — поддержка `Раздел`.

```python
def Test.List(ДопПоля, Фильтр, Сортировка, Навигация):
    if 'SelectionWithPath' in Фильтр:
        import blhelpers
        return blhelpers.ShowMarked(
            'Test.List', Фильтр, Сортировка, Навигация,
            "Раздел",          # parent_property
            '@Идентификатор',  # key_property
            ["@Идентификатор"] # position_fields (для курсора)
        )
    # общий случай...
```

---

## Перенос записей в папку (MoveToFolder)

`blhelpers.MoveToFolder` переносит все записи, подпадающие под условия фильтрации, в указанную папку.

> [!note] Особенность
> Если указана папка — переносится **вся папка целиком**, даже если часть её записей не выбрана. Для иного поведения реализуйте метод перемещения самостоятельно.

```python
import blhelpers
# Документ.Переместить(Фильтр, ИдентификаторПапки):
blhelpers.MoveToFolder("Документ.Список", Фильтр, ИдентификаторПапки, "Раздел", "@Документ")
```

| Параметр | Тип | Описание |
|----------|-----|---------|
| `filter` | Record | Фильтр с вложенной записью `selection` |
| `method` | String | Имя списочного метода |
| `folder_id` | OptInt64 | ID папки-назначения |
| `parent_property` | String | Имя поля иерархии |
| `key_property` | String | Имя поля с ID объекта |

Модуль: **BL Helpers-Py** (SBIS SDK).

---

## Суммирование (Sum.ByMethod)

`Sum.ByMethod` вычисляет суммы полей записей через DWC. Итерации по 30 сек, пока не закончатся данные.

**Архитектура:** каждая итерация (`Sum.ByMethodDWCIterable`) обрабатывает порцию через `ListIterator`, добавляет следующую итерацию в конец очереди DWC.

```python
# Вызов из клиента (запускает длительную операцию)
# Результат приходит через LRS на клиент как Record с полями = отображаемым именам из Fields
```

| Параметр | Тип | Описание |
|----------|-----|---------|
| `MethodName` | String | Имя списочного метода |
| `Filter` | Record | Фильтр с обязательным `selection` |
| `Fields` | HashTable | `{"поле": "Название"}` или массив `{field, title, currencyField, outcome}` |
| `LongOperationToken` | String | Токен длительной операции |

Для суммирования с учётом иерархии передать `__HierarchyName__` в Filter.
Для нестандартного поля ID — `__KeyProperty__` в Filter.

---

## Поиск с учётом неверной раскладки (TranslitListCall)

`TranslitListCall` обрабатывает поисковые запросы, введённые в неверной раскладке. Поддерживаемые: Русская, Английская (США), Казахская, Узбекская, Туркменская.

```python
# Python (BL Helpers-Py)
from blhelpers import TranslitListCall

result = TranslitListCall(
    method="Объект.СписочныйМетод",
    field="СтрокаПоиска",       # поле в Фильтр с поисковой строкой
    ext_fields=ДопПоля,
    filter=Фильтр,
    sort=Сортировка,
    nav=Навигация
)
```

Ответ: RecordSet из двух выборок. В `metaData.switchedStr` — строка, по которой выполнен альтернативный поиск (отсутствует, если данных по другой раскладке нет).

C++ версия: `BL Core` (`TranslitListCall(method, field, params)`).

---

## Хлебные крошки в иерархическом поиске (ListWithParents)

`CoreUtils.ListWithParents` дополняет выборку пропущенными родительскими узлами. Используется для построения пути (хлебных крошек) к найденным записям.

**Порядок записей в ответе:**
1. Дети корня → дети 1-го уровня (сгруппированы по родителям) → 2-й уровень → ...
2. Внутри группы — порядок из оригинальной выборки; дополнительно полученные — в конце.

| Параметр | Описание |
|----------|---------|
| `__ListMethod__` | Имя списочного метода `"Объект.Метод"` |
| `__HierarchyName__` | Поле иерархии (необязательно если есть в Фильтр) |
| `__KeyField__` | Поле PK (если не нулевое поле) |
| `__SearchResultProperty__` | Совпадает с `searchResultProperty` представления |

**Требование к списочному методу:** возможность получить запись через `Прочитать(ИдО)` с теми же полями, что и в выборке.

**Алгоритм:**
1. Вызов списочного метода с аргументами от `ListWithParents`.
2. Для каждого узла-родителя, отсутствующего в выборке — вызов `Прочитать` у объекта иерархии.
3. Запись добавляется в выборку; формат сокращается до формата изначальной выборки.
