---
type: concept
title: "Wasaby RecordSet Performance"
updated: 2026-04-10
tags:
  - wasaby
  - python
  - performance
  - recordset
  - record
status: current
related:
  - "[[Wasaby-Python-Patterns]]"
  - "[[Wasaby-CPP-Python-Integration]]"
  - "[[Wasaby-RecordSet-Join]]"
  - "[[Wasaby-DB-Access-Patterns]]"
created: 2026-04-10
---

# Wasaby RecordSet Performance

Паттерны оптимизации при работе с `Record`/`RecordSet` из Python. Платформа Wasaby — C++-based; каждое пересечение границы Python↔C++ несёт накладные расходы.

> [!key-insight] Суть проблемы
> Даже простой доступ к полю (`rec.typeDoc`) проходит путь: построить C++-строку из Python-строки → обратиться к полю → уничтожить временную C++-строку → преобразовать значение в Python-тип. Каждый такой переход — цена.

---

## 1. Создание RecordSet/Record из Python-данных

Вместо поштучного заполнения через `AddRow` + `Set` — передавайте данные сразу при создании.

```python
# Позиционно (list[list])
rs = sbis.CreateRecordSet(frmt, [
    [1, 'foo', True],
    [2, 'bar', False],
])

# По имени (list[dict])
rs = sbis.CreateRecordSet(frmt, [
    {'Id': 1, 'Name': 'foo', 'Active': True},
    {'Id': 2, 'Name': 'bar', 'Active': False},
])

# Аналогично для одиночной записи
rec = sbis.Record(frmt, [1, 'foo', True])          # позиционно
rec = sbis.Record(frmt, {'Id': 1, 'Name': 'foo'})  # по имени
```

---

## 2. Dataclasses вместо RecordSet для вычислений

Если RecordSet нужен только как источник данных для Python-кода — конвертируйте его в нативные dataclass-объекты. Избегаете повторных пересечений моста при каждом обращении к полю.

```python
from dataclasses import dataclass

@dataclass
class PriceItem:
    id: int
    price: float
    discount: float

# Один раз пересекаем мост — получаем список нативных объектов
items: list[PriceItem] = rs.ToListOf(PriceItem, ['Id', 'Price', 'Discount'])

# Дальше работаем с чистым Python — никаких bridge-переходов
total = sum(item.price * (1 - item.discount) for item in items)
```

---

## 3. SqlQueryOf — обход RecordSet для calculation-кода

Когда RecordSet на выходе не нужен (промежуточные вычисления, агрегация), используйте `SqlQueryOf` — результат сразу приходит как `list[OurDataClass]`.

```python
@dataclass
class BonusRow:
    card_id: int
    amount: float

rows: list[BonusRow] = sbis.SqlQueryOf(
    BonusRow,
    # стандартные аргументы SqlQuery — запрос, фильтр, и т.д.
    'SELECT "ИдКарты", "Сумма" FROM "Бонусы" WHERE ...',
)
```

Подходит для любой ситуации, где нужны данные из БД без дальнейшей работы с RecordSet-API.

---

## 4. Оптимизация списочного метода через формат результата

Передавайте ожидаемый формат результата в метод БД-запроса. Неиспользуемые колонки получат `NULL` и не будут вычисляться. Это быстрее, чем получить полный RecordSet и вызвать `Migrate()`.

```python
# Медленно: полный RecordSet → Migrate к нужному формату
full_rs = get_full_recordset()
result = full_rs.Migrate(target_format)

# Быстро: сразу указываем нужный формат — лишние колонки = NULL
result = get_recordset_with_format(target_format)
```

---

## 5. Объединение из нескольких источников

Для join-операций над RecordSet в памяти используйте класс `Query` — одним вызовом вместо ручного цикла. Подробнее: [[Wasaby-RecordSet-Join]].

---

## 6. Правильное добавление строк в RecordSet

> [!danger] Анти-паттерн: `AddRow(rec)` копирует запись
> Создание отдельной записи и передача её в `AddRow` приводит к лишнему копированию.

```python
# ❌ Неэффективно — копирование записи
rec = sbis.Record(format)
rec['Id'] = 1
rec['Name'] = 'foo'
rs.AddRow(rec)  # копирует rec в rs

# ✅ Правильно — rec это ссылка на новую строку внутри rs
rec = rs.AddRow()   # без аргументов — добавляет пустую строку и возвращает ссылку
rec.Set('Id', 1)
rec.Set('Name', 'foo')
```

---

## 7. Массовое заполнение полей: Fill вместо поштучного присваивания

Каждое присваивание через `rec["Foo"].From(10)` создаёт и уничтожает временный объект `IField`. При заполнении нескольких полей — используйте `Fill`.

```python
# ❌ Медленно — создаёт/уничтожает IField для каждого поля
rec["Foo"].From(10)
rec["Bar"].From(True)
rec["Baz"].From('hello world')

# ✅ Быстро — одно пересечение моста
rec.Fill({"Foo": 10, "Bar": True, "Baz": 'hello world'})
```

---

## 8. Проверка существования поля: вне цикла

Проверка `rec.TestField("Foo")` в каждой итерации цикла — дорого. Проверяйте один раз по формату.

```python
# ❌ Медленно — TestField в каждой итерации
for row in rs:
    if row.TestField("Foo"):
        process(row["Foo"])

# ✅ Быстро — проверяем один раз, до цикла
has_foo = "Foo" in helper_rs.Format()
for row in rs:
    if has_foo:
        process(row["Foo"])
```

---

## 9. Анти-паттерн: проверка перед установкой того же значения

Не читайте текущее значение поля только для того, чтобы убедиться, что оно уже равно устанавливаемому. Лишнее чтение дороже, чем просто написать новое значение.

```python
# ❌ Бессмысленно — чтение + запись вместо просто записи
if rec['Status'] != new_status:
    rec['Status'] = new_status

# ✅ Просто устанавливайте значение
rec['Status'] = new_status
```

---

## Сводка паттернов

| Ситуация | Анти-паттерн | Паттерн |
|---|---|---|
| Создание RecordSet из данных | `AddRow()` + `Set()` в цикле | `CreateRecordSet(frmt, data)` |
| Вычисления над данными | прямой доступ к полям RecordSet | `ToListOf(DataClass, fields)` |
| Запрос → вычисления | SqlQuery → RecordSet | `SqlQueryOf(DataClass, ...)` |
| Добавление строки | `AddRow(rec)` с готовой записью | `rec = rs.AddRow()` |
| Заполнение полей | `rec["F"].From(v)` per field | `rec.Fill({...})` |
| Проверка поля в цикле | `TestField(...)` каждую итерацию | `"F" in rs.Format()` один раз |
| Ненужный формат | полный RS → `Migrate()` | передать format в запрос |

---

## 10. Сравнительный бенчмарк итерации (1000 прогонов, 1000 записей)

Источник: статья Боровикова К. о скорости перебора RecordSet.

| Тест | Описание | Скорость |
|---|---|---|
| test0 | `rs[index]['field']` + `TestField` + `int(rec['id'])` | медленно |
| test1 | `for rec in rs` + `TestField` + `rec['field']` | медленно |
| test2 | `for rec in rs` + `rec['field']` (без TestField) | медленно |
| test3 | `for rec in rs: [rec.id, rec.name]` | быстро |
| test4 | `[[rec.id, rec.name] for rec in rs]` | быстрее |
| test5 | `list(map(attrgetter('id','name'), rs))` | ещё быстрее |
| test7 | `rs.Get(i, 'id')` через range | ~2× vs test4 |
| test8 | `f = rs.Get; [f(i,'id')…] for i in range(…)` | чуть быстрее test7 |
| test9 | `rs.ToList(('id', 'name'))` | ~3× vs test4 |
| test10/11 | `rs.ToList()` / `rs.as_list()` | сопоставимо с test9 |
| test6 | `SqlQueryRow` + `array_agg` → `zip` (без Python-обёрток) | максимально быстро |

> [!key-insight] Вывод
> Основная стоимость — создание Python-обёрток над C++ `Record` и `IField`. Порядок предпочтения:
> `rs.ToList(fields)` > `attrgetter` > `rec.field` атрибут > `rec['field']` оператор > `TestField`

### Методы ToList / Get

```python
# rs.Get — доступ к значению без создания Record-обёртки
rs.Get(i, 'name')         # одно значение строки i
f = rs.Get                # кэшируем ссылку на метод для скорости
[f(i, 'id') for i in range(rs.Size())]

# rs.ToList — bulk-конвертация в list
rs.ToList('id')                    # list[id1, id2, ...]
rs.ToList(('id', 'name'))          # list[list[id,name], ...]
rs.ToList()                        # все поля; если 1 поле — list[val]

# Пример: передать первичные ключи в другой метод
Activity.ListActivity(person_list.ToList('Лицо'))

# Пример: распаковка в цикле
for person, last_activity in activity_rs.ToList(('person', 'last')):
    ...

# Пример: звёздочка для массива хвоста
for person, *sums in sums_rs.ToList():
    ...
```

---

## 11. ToDict и GroupBy

### RecordSet.ToDict(key_field, value_fields)

Конвертирует RecordSet в `dict`: ключ — значение `key_field`, значение — остальные поля.

```python
rs = SqlQuery('', employees, month)
sums = rs.ToDict('Сотрудник', ('Начисления', 'Удержания'))
employee_sums = sums[employee]   # или sums.get(employee)
```

- Если `value_fields` — 1 поле: значение = скалярное значение поля
- Если несколько: значение = list значений полей
- Если не передать: все поля, кроме ключевого (с версии 150)

### RecordSet.GroupBy(key_field, value_fields, ordered=False)

Как `ToDict`, но значение — **список** строк с одинаковым ключом. Аналог `itertools.groupby`, но без требования сортировки.

```python
# Все сотрудники по подразделениям
dep_employees = rs.GroupBy('СтруктураПредприятия', 'Сотрудник')

# Настройки с датами (для bisect)
values = rs.GroupBy('Настройка', ('ДатаНачала', 'ДатаКонца', 'Значение'))
```

- `ordered=True` — работает быстрее, когда данные уже отсортированы по ключу
- По умолчанию `ordered=False` — работает с неотсортированными данными

---

## Сводка паттернов

| Ситуация | Анти-паттерн | Паттерн |
|---|---|---|
| Создание RecordSet из данных | `AddRow()` + `Set()` в цикле | `CreateRecordSet(frmt, data)` |
| Вычисления над данными | прямой доступ к полям RecordSet | `ToListOf(DataClass, fields)` |
| Запрос → вычисления | SqlQuery → RecordSet | `SqlQueryOf(DataClass, ...)` |
| Добавление строки | `AddRow(rec)` с готовой записью | `rec = rs.AddRow()` |
| Заполнение полей | `rec["F"].From(v)` per field | `rec.Fill({...})` |
| Проверка поля в цикле | `TestField(...)` каждую итерацию | `"F" in rs.Format()` один раз |
| Ненужный формат | полный RS → `Migrate()` | передать format в запрос |
| Bulk-итерация | `for rec in rs: [rec['f']…]` | `rs.ToList(fields)` |
| Извлечение по ключу | ручной цикл поиска | `rs.ToDict(key, fields)` |
| Группировка данных | `itertools.groupby` | `rs.GroupBy(key, fields)` |

---

## Связанные темы

- [[Wasaby-CPP-Python-Integration]] — крэши (не исключения) при неправильной работе со ссылками
- [[Wasaby-Python-Patterns]] — общие паттерны Python в Wasaby: транзакции, исключения, файлы
- [[Wasaby-RecordSet-Join]] — объединение RecordSet через класс Query
- [[Wasaby-DB-Access-Patterns]] — IStatement, SqlQuery, async, bulk ops
- [[Wasaby-App-Optimization]] — обзор уровней оптимизации
- [[PriceFormation-Common-Helpers]] — record.py и dict_utils.py: create_record, Fill/AddRow паттерны в helpers
