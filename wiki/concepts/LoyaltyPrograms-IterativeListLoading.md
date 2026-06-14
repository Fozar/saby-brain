---
type: concept
title: "LoyaltyPrograms — Iterative List Loading"
updated: 2026-05-19
tags:
  - loyaltyprograms
  - cursor
  - iterative
  - navigation
  - python
status: current
related:
  - "[[Wasaby-BL-List-Advanced]]"
  - "[[Wasaby-BL-List-Methods]]"
  - "[[Loyalty-React-Migration-Project]]"
  - "[[PriceFormation-Backend-Architecture]]"
  - "[[Wasaby-RecordSet-Performance]]"
  - "[[BonusChart-IterativeBlock-Bug-Fix]]"
created: 2026-04-14
---

# LoyaltyPrograms — Iterative List Loading

Механизм курсорной навигации и адаптивной порционной загрузки для реестров покупок в `priceformationonline`.
Реализован в четырёх классах, образующих иерархию.

Общий паттерн порционной загрузки (Wasaby-уровень): [[Wasaby-BL-List-Advanced#Порционная загрузка данных]].

> [!warning] Иерархия классов на rc-26.4100 (обновление)
> После выпила фичи `loyalty_it_nav` (см. [[Feature-Flag-Removal-LOYALTY-IT-NAV]]) не-итеративные базы
> **удалены** — остались только итеративные классы. Актуальная картина:
> - `BonusSaleListIterative(IterativeBlockSizeEmaMixin, ListWithCompositeCursor, SaleListWithCursor)` — `BonusSaleListWithCursor` больше нет.
> - `ReferralBonusSaleListWithCursorIterative(BonusSaleListIterative)` — наследуется от бонусного итеративного, а не от `BonusSaleListWithCursor`.
> - `PromoCodeSaleListIterative(IterativeBlockSizeEmaMixin, ListWithCompositeCursor, SaleListWithCursor)` — `PromoCodeSaleListWithCursor` удалён.
> - `DiscountCardListWithCursorIterative(IterativeBlockSizeEmaMixin, ListWithCompositeCursor)`, `PromotionSaleListWithCursor(IterativeBlockSizeEmaMixin, SaleListWithCursor)`.
> - **`Bonus.GetClientListWithStats` отказался от итеративности** — перешёл на курсорную навигацию через `get_list_by_cursor` (`priceformationcommon.core.cursor_navigation`), без EMA-блока.
>
> Разбор иерархии ниже описывает структуру до 4100 (двухуровневые `*WithCursor` → `*Iterative`); концептуально остаётся верным, имена базовых классов — нет. См. [[Loyalty-IterativeLoading-TD-CommonSolutions]].

Исходные файлы:
- `www/service/Модули/PriceFormation.Online/priceformationonline/loyaltyprograms/loyaltyprogram/helpers.py`
- `www/service/Модули/PriceFormation.Online/priceformationonline/loyaltyprograms/loyaltyprogram/get_sale_list.py`

---

## Иерархия классов

```
ListWithCursor                   (helpers.py:47)   — базовый курсор, плоский nextPosition
└── ListWithCompositeCursor      (helpers.py:386)  — составной курсор, nextPosition как [{key:val}]

SaleListWithCursor               (get_sale_list.py:22) — реестр покупок, обогащение данными
└── BonusSaleListWithCursor      (bonus/get_sale_list.py)
    └── BonusSaleListIterative   — MRO: IterativeBlockSizeEmaMixin, ListWithCompositeCursor, BonusSaleListWithCursor
└── PromotionSaleListWithCursor  (promotion/get_sale_list.py)
    └── PromotionSaleListIterative
└── PromoCodeSaleListWithCursor  (promocode/get_sale_list.py)
    └── PromoCodeSaleListIterative

IterativeBlockSizeEmaMixin       (helpers.py:963) — mixin: адаптивный размер блока через EMA
```

> [!note] MRO-паттерн для итеративных реестров
> `class BonusSaleListIterative(IterativeBlockSizeEmaMixin, ListWithCompositeCursor, BonusSaleListWithCursor)`
> Python MRO обеспечивает, что `ListWithCompositeCursor._get_result_in_one_direction_iterative` перекрывает
> родительский `ListWithCursor`, а `IterativeBlockSizeEmaMixin` добавляет подстройку размера блока поверх.

---

## ListWithCursor

**Файл:** `helpers.py:47`
**Автор:** Постнов С.А.

Базовый класс для реестров с курсорной навигацией. Берёт SQL-шаблон (`_query`), подставляет параметры
навигации, выполняет запрос, возвращает RecordSet с `nextPosition`/`prevPosition` в метаданных.

### Атрибуты экземпляра

| Атрибут | Тип | Дефолт | Назначение |
|---------|-----|--------|-----------|
| `_query` | `str \| None` | `None` | SQL-шаблон. В стандартном режиме содержит Python-форматирование `{_operator}`, `{_order}`, `{_limit}`; в итеративном — только `!Param` (sbis.Template). Задаётся в дочернем классе. |
| `_default_cursor` | `dict` | `{}` | Словарь `{поле: значение}` — начальная позиция курсора, если `navigation.Position()` не передана или невалидна. Ключи определяют, какие поля читаются из записи для `nextPosition`. |
| `_extra_params` | `dict[str, Any]` | `{}` | Дополнительные параметры для подстановки в шаблон (поверх фильтров и курсора). |
| `_default_filters` | `dict` | `{}` | Значения фильтров по умолчанию, когда клиент не передаёт их явно. |
| `_reverse` | `bool` | `False` | Инвертирует смысл FORWARD/BACKWARD. При `True` FORWARD читает в убывающем порядке (от новых к старым). |
| `_direction` | `NavigationDirection \| None` | `None` | Текущее направление навигации, устанавливается в `_get_result`. |
| `_iterative` | `bool` | `False` | Включить порционный режим. |
| `_iterative_block_size` | `int` | `10_000` | Размер блока в порционном режиме. |

### Константы направлений

```python
FORWARD  = sbis.NavigationDirection.ndFORWARD
BACKWARD = sbis.NavigationDirection.ndBACKWARD
BOTHWAYS = sbis.NavigationDirection.ndBOTHWAYS
```

---

### get_result(filters, navigation) → RecordSet

Публичный метод. Точка входа, которую переопределяют дочерние классы при необходимости.
По умолчанию делегирует в `_get_result`.

```python
def get_result(self, filters: RecordType, navigation: sbis.Navigation) -> RecordSetType
```

---

### _get_result(filters, navigation) → RecordSet

Основная логика. Определяет направление из навигации (или создаёт дефолтную), затем ветвится:

**BOTHWAYS:**
1. Запрашивает данные в направлении FORWARD → `data`, `forward_next_position`, `prev_position`
2. Если данных нет → повторяет в BACKWARD → `data`, `backward_next_position`, `prev_position`
3. Если данные есть → повторяет в BACKWARD с `only_next_position=True` (только позиция, без данных) → `backward_next_position`
4. `nav_result = NavigationResult(bool(backward_next), bool(forward_next))`
5. `nextPosition` записывается в метаданные как `{'after': [...], 'before': [...]}`
6. `prevPosition` записывается в метаданные как JSON

**FORWARD / BACKWARD:**
1. Запрашивает данные в нужном направлении → `data`, `next_position`, `prev_position`
2. `nav_result = NavigationResult(bool(next_position))`
3. `nextPosition` и `prevPosition` записываются в метаданные как JSON

**Общее:**
- Если `_iterative=True` → добавляет в метаданные `iterative: True`
- При неизвестном направлении — `sbis.Error('Переданы неверные параметры навигации')`

---

### _get_result_in_one_direction(filters, navigation, direction, only_next_position=False)

Выполняет один направленный запрос. Возвращает `(data, next_position, prev_position)`.

**Стандартный режим (`_iterative=False`):**

1. `_prepare_navigation(navigation, direction)` → `(operator, order, limit, cursor_dict)`
2. Объединяет фильтры: `update_dict(default_filters, filters.as_dict())`
3. Формирует шаблон: `Template(query.format(_operator=operator, _order=order, _limit=limit+1))`
4. `params = {**filters, **cursor, **extra_params}`
5. `result = sbis.QueryByTemplate(template, params)`
6. Если `len(result) == limit+1`:
   - `next_position_index = len-1` при FORWARD, `0` при BACKWARD
   - `next_position = _get_position_from_record(result[next_position_index])`
   - `result.DelRow(next_position_index)` — удаляет сигнальную запись
7. Иначе `next_position = None`
8. `prev_position` берётся из последней (FORWARD) или первой (BACKWARD) записи результата

**Итеративный режим (`_iterative=True`):**
Делегирует в `_get_result_in_one_direction_iterative`.

---

### _get_result_in_one_direction_iterative(filters, navigation, direction, only_next_position)

Декорирован `@logging(with_profiling=True, full=True)`.

**Быстрый путь `only_next_position=True`:**
- Если позиция невалидна → `(None, None, None)`
- Иначе: берёт первый ключ из `_default_cursor`, возвращает `[str(navigation_data[cursor_name])]`

**Основной путь:**
1. `_prepare_navigation` → dict навигации
2. `params = {**filters, **navigation_data, **extra_params}`
3. `result = sbis.QueryByTemplate(Template(self._query), params)` — шаблон без `{...}`
4. `next_position = _prepare_next_position_iterative(result, direction, navigation_data)`
5. `prev_position` — из последней (FORWARD) или первой (BACKWARD) записи

---

### _prepare_navigation(navigation, direction) → tuple | dict

Вычисляет параметры для подстановки в SQL.

**Формула operator/order:**

| `_reverse` | `direction` | `operator` (станд.) | `operator` (итерат.) | `order` |
|-----------|------------|---------------------|----------------------|---------|
| `False` | FORWARD | `>=` | `>` | `ASC` |
| `False` | BACKWARD | `<=` | `<` | `DESC` |
| `True` | FORWARD | `<=` | `<` | `DESC` |
| `True` | BACKWARD | `>=` | `>` | `ASC` |

> Итеративный режим убирает `=` из оператора: следующий вызов начинается строго после последней записи.

**Возвращает:**
- Стандартный режим: `(operator: str, order: str, limit: int, cursor: dict)`
- Итеративный режим: `{'_operator': ..., '_order': ..., '_limit': ..., '_iterative_block_size': ..., **cursor}`

Курсор берётся из `navigation.Position().as_dict()` (если позиция валидна) или из `_default_cursor`.

---

### _prepare_next_position_iterative(result, direction, navigation_data) → list | None

Обрабатывает контрольную запись в итеративном режиме.

Правила:
- Последняя запись обязана содержать `_IsControlRecord = TRUE` — иначе `sbis.Error`
- Если `len(result) == 1` (только контрольная): `nextPosition` из контрольной записи, запись удаляется
- Если `len(result) > 1`: контрольная запись удаляется, `nextPosition` из предпоследней (последней данных)

> [!important] Ключевое отличие от стандартного режима
> В стандартном режиме `nextPosition` = запись, **не вошедшая** в результат (лишняя `limit+1`).
> В итеративном — **последняя вошедшая** запись. Следующий вызов строго после неё (`>` без `=`).

---

### _get_position_from_record(record) → list[str | int] | None

Извлекает значения ключей курсора из записи. Возвращает плоский список:
```python
# _default_cursor = {'DateWTZ': ..., 'SaleId': ...}
# → ['2026-05-19T23:59:59', 42]
```
- `int` остаётся как `int`
- Всё остальное приводится к `str`
- Если любое значение `None` → возвращает `None` (позиции нет)

---

### _is_valid_position(navigation) → bool

Позиция **не валидна**, если:
- `navigation` не передана / `IsNull()`
- Тип навигации `ntPAGE` (страничная, не курсорная)
- `navigation.Position()` пуст
- Первый ключ `_default_cursor` отсутствует или `None` в позиции

---

## ListWithCompositeCursor

**Файл:** `helpers.py:386`

Расширяет `ListWithCursor` для поддержки **составного курсора** (несколько ключей).
Создан как отдельный класс, чтобы изолировать изменения и не ломать существующие реестры на `ListWithCursor`.

### Ключевые отличия от ListWithCursor

| Аспект | ListWithCursor | ListWithCompositeCursor |
|--------|---------------|------------------------|
| Формат `nextPosition` | `['val1', 'val2']` (плоский список) | `[{'key1': 'val1', 'key2': 'val2'}]` (список из одного dict) |
| Чтение позиции | `navigation.Position().as_dict()` | `_extract_position_dict()` (поддерживает вложенность) |
| `_is_valid_position` | Проверяет только первый ключ | Проверяет **все** ключи курсора |
| `only_next_position` | `[str(navigation_data[first_key])]` | `[{k: v for k in cursor_keys}]` |

---

### _extract_position_dict(navigation) → dict | None

Поддерживает два формата `navigation.Position()`:

**Прямой формат** (поля курсора на верхнем уровне):
```python
Position = Record({'DateWTZ': ..., 'SaleId': ...})
```

**Вложенный формат** (курсор завёрнут в `cursor`):
```python
Position = Record({'cursor': [{'DateWTZ': ..., 'SaleId': ...}]})
# cursor может быть: list[dict], list[Record], dict, Record
```

Алгоритм:
```python
cursor_container = position.Get('cursor')
if cursor_container is not None:
    elem = cursor_container[0] if isinstance(cursor_container, list) else cursor_container
    raw_dict = elem if isinstance(elem, dict) else elem.as_dict()
else:
    raw_dict = position.as_dict()
# Возвращает только ключи из _default_cursor
```

Возвращает `None`, если позиция недоступна или пуста.

---

### _is_valid_position (переопределение)

Позиция валидна, если:
- `navigation` не `None` и не `IsNull()`
- Тип не `ntPAGE`
- `_extract_position_dict()` вернул не `None`
- **Все** ключи `_default_cursor` присутствуют и не `None`

---

### _get_position_from_record (переопределение)

Возвращает **список из одного словаря** вместо плоского списка:
```python
# → [{'DateWTZ': '2026-05-19T23:59:59', 'SaleId': 42}]
```
Такой формат совместим с фронтендовым компонентом курсорной навигации, принимающим структурированные позиции.

---

### _prepare_next_position_iterative (переопределение)

Логика идентична базовой (контрольная запись, 1 запись vs >1 записей), но возвращает позицию
в формате `[{...}]` через переопределённый `_get_position_from_record`.

---

## SaleListWithCursor

**Файл:** `get_sale_list.py:22`
**Автор:** Постнов С.А.

Специализация `ListWithCursor` для реестра покупок. Переопределяет поведение навигации
и добавляет механизм обогащения данных из систем Розница и СУ.

### Атрибуты (дополнительные к ListWithCursor)

| Атрибут | Дефолт | Назначение |
|---------|--------|-----------|
| `_reverse` | `True` | Новые записи первыми (от большей даты к меньшей) |
| `_default_cursor` | `{'DateWTZ': last_second_of_current_month()}` | Начало с конца текущего месяца |
| `_is_bonus` | `False` | Реестр бонусный (влияет на формат `TotalDiscount` и набор полей) |
| `_graphic_type` | `None` | Тип графика для итогов |
| `_custom_fields` | `None` | Дополнительные поля формата, специфичные для реестра |
| `_sale_data_fields` | *(список)* | Поля, запрашиваемые из `Sale.BuildList` |
| `_document_data_fields` | *(список)* | Поля, запрашиваемые из `WarehouseDoc.SalesList` |

### Вспомогательные статические методы

**`get_last_date_of_current_month() → date`**
Возвращает дату последнего дня текущего месяца через `get_month_len`.

**`get_last_second_of_current_month() → datetime`**
Возвращает последнюю секунду текущего месяца (`00:00:00` следующего дня минус 1 секунда).
Используется как курсор по умолчанию — первый вызов без позиции начинается с конца текущего месяца.

---

### _add_sale_data(data, search_string)

Обогащает RecordSet из SQL данными о продажах. SQL возвращает только `SaleId`/`DocumentId` и числовые поля.

**Алгоритм:**
1. Собирает `sale_ids` (Розница) и `document_ids` (СУ) из `data`
2. Параллельные вызовы через `FutureInvoke`:
   ```python
   future_retail  = sbis.BLObject('Sale').FutureInvoke('BuildList', fields, filters_retail, ...)
   future_wh      = sbis.BLObject('WarehouseDoc').FutureInvoke('SalesList', ...)
   ```
3. Вызывает `_initial_change_data_source_format(data)` — мигрирует формат RecordSet
4. Для каждой строки `sale`:
   - Если `SaleId` в `retail_sale_data` → заполняет из Розницы, `Id = 'R{SaleId}'`
   - Если `DocumentId` в `warehouse_sale_data` → заполняет из СУ, `Id = 'W{DocumentId}'`
   - Иначе → `data.DelRow(sale)` (строка не прошла текстовый поиск)
5. Вычисляет `Date = DateWTZ.date()`
6. `TotalDiscount = Bonus` (бонусный) или `Discount` (обычный)
7. Если `Return=True` → `TotalPrice = -TotalPrice`
8. Удаляет конфиденциальные поля из `CustomerInfo` и `SellerInfo`

**Конфиденциальные поля:**

| Из `CustomerInfo` | Из `SellerInfo` |
|-------------------|-----------------|
| Фамилия, Имя, Отчество | Фамилия, Имя, Отчество |
| Пол, Gender | Пол, Gender |
| ContactData | ContactData, ДатаРождения, СНИЛС |

---

### _format_result(data)

Упрощённый вариант обогащения — без запросов в Розницу/СУ. Используется, когда SQL уже содержит
все нужные поля (например, реестр без поиска).

1. `_initial_change_data_source_format(data)` — мигрирует формат
2. Для каждой строки: `Date = DateWTZ.date()`, `TotalDiscount`, `Id = 'R...' | 'W...'`

---

### _initial_change_data_source_format(data)

Приводит RecordSet к единому формату через `data.Migrate(result_format)`.

**Базовые поля (все реестры):**

| Поле | Тип |
|------|-----|
| `Id` | `ftSTRING` |
| `SaleId` | `ftINT32` |
| `DocumentId` | `ftINT64` |
| `Date` | `ftDATE` |
| `Type` | `ftINT16` |
| `Seller`, `Customer` | `ftINT32` |
| `TotalPrice`, `TotalDiscount` | `ftMONEY` |
| `SaleName` | `ftSTRING` |
| `PositionCount` | `ftINT32` |
| `SellerInfo`, `CustomerInfo` | `ftRECORD` |
| `Totals` | `ftRECORD` |
| `GraphicData` | `ftRECORDSET` |
| `HolidaysData` | `ftARRAY_BOOLEAN` |
| `AdditionalInfo` | `ftSTRING` |
| `Return` | `ftBOOLEAN` |
| `DateWTZ`, `ClosedWTZ` | `ftDATETIME` (foWITHOUT_TIMEZONE) |

**Поля только для бонусных реестров (`_is_bonus=True`):**
- `Bonuses: ftMONEY`
- `GroupName: ftSTRING`
- `IsEmpty: ftBOOLEAN`

**Поля только для небонусных реестров:**
- `Discount: ftMONEY`

Если `_custom_fields` задан — добавляются в конец.

> [!note] `foWITHOUT_TIMEZONE` для `DateWTZ`/`ClosedWTZ`
> Инициализируется через `result_format.AddDateTime('DateWTZ', sbis.FormatOptions.foWITHOUT_TIMEZONE)`,
> чтобы часовой пояс клиента не учитывался при построении реестра.

---

### _get_sale_data(sale_ids, document_ids, search_string) → (retail_dict, wh_dict)

Запрашивает данные о продажах параллельно через `FutureInvoke`.

**Для Розницы (`Sale.BuildList`):**
- `Sales: ARRAY_INT32` — список ID
- `Search: STRING` — строка поиска
- `NameLength: INT32 = 500`
- `ShowPersonInfoExt: BOOLEAN = True`
- `ShowPositionCount: BOOLEAN = True`

**Для СУ (`WarehouseDoc.SalesList`):**
- `СписокИдО: ARRAY_INT64` — список ID документов
- `ФильтрПоМаске: STRING` — строка поиска
- `iterative_list: BOOLEAN = True`
- `new_navigation: BOOLEAN = True`
- `position_on_today: BOOLEAN = True`
- `rp_doc: BOOLEAN = True`

Возвращает два dict:
- Розница: `{SaleId → [field_values]}`
- СУ: `{DocumentId → [field_values]}`

---

## IterativeBlockSizeEmaMixin

**Файл:** `helpers.py:963`

Mixin для автоматической подстройки `_iterative_block_size` на основе статистики текущей итерации.
Предназначен для наследников `SaleListWithCursor` (через MRO).

### Идея

При разреженных данных (много записей надо просмотреть, чтобы найти нужные) фиксированный блок
из 10 000 строк может возвращать 0 результатов. EMA сглаживает коэффициент разреженности
и увеличивает блок пропорционально. При плотных данных — блок уменьшается.

### Константы класса

| Константа | Значение | Назначение |
|-----------|---------|-----------|
| `_EMA_ALPHA` | `0.3` | Коэффициент сглаживания EMA |
| `_MIN_BLOCK` | `1 000` | Минимальный размер блока |
| `_MAX_BLOCK` | `20 000` | Максимальный размер блока |
| `_DEFAULT_BLOCK` | `10 000` | Дефолт при первом запуске |
| `_CONTROL_FLAG_FIELD` | `'_IsControlRecord'` | Поле-признак контрольной записи |
| `_SCANNED_FIELD` | `'ScannedCount'` | Поле: кол-во просмотренных записей в блоке |
| `_RAW_FIELD` | `'RawResultCount'` | Поле: кол-во записей, прошедших фильтрацию |

**Обязательные атрибуты наследника:**
```python
_BLOCK_SIZE_PARAM: str   # Имя GlobalParams-параметра для размера блока
_RATIO_EMA_PARAM: str    # Имя GlobalParams-параметра для EMA коэффициента
```

---

### _find_control_record(result) → Record | None

Ищет контрольную запись с конца RecordSet (итерация от последнего индекса).
Возвращает первую найденную запись с `_IsControlRecord = True`, или `None`.

---

### _tune_iterative_block_size_from_result(result, navigation_data)

Главный метод mixin-а. Вызывается в `_prepare_next_position_iterative` наследника после получения результата.

**Алгоритм:**
1. Если `result` пуст → выход
2. `_find_control_record(result)` — найти контрольную запись
3. Если не найдена → `sbis.Error('Неправильно настроена итеративная загрузка в реестре')`
4. `scanned = control.Get('ScannedCount')`, `raw = control.Get('RawResultCount')`, `limit = navigation_data['_limit']`
5. Делегирует в `tune_iterative_block_size_by_counts(...)` с параметрами класса
6. Результат записывается в `self._iterative_block_size`
7. При исключении — `sbis.WarningMsg(...)`, без краша

---

### tune_iterative_block_size_by_counts (standalone функция)

**Файл:** `helpers.py:880`

```python
def tune_iterative_block_size_by_counts(
    scanned: int,
    result_cnt: int,
    limit: int,
    *,
    block_size_param: str,
    ratio_ema_param: str,
    current_block: int,
    default_block: int,
    min_block: int,
    max_block: int,
    ema_alpha: float = 0.3,
    k: float = 2.5,
    change_threshold: float = 0.15,
) -> int
```

**Полный алгоритм:**
1. Входная валидация: `scanned > 0`, `result_cnt >= 0`, `limit > 0` — иначе возврат `current_block`
2. `ratio = scanned / max(result_cnt, 1)` — сколько записей нужно просмотреть на 1 результат
3. Читает `ratio_ema` из `GlobalParams(ratio_ema_param)`, при ошибке использует `ratio`
4. `ratio_ema = (1 - ema_alpha) * ratio_ema + ema_alpha * ratio` — экспоненциальное сглаживание
5. `target = int(limit * ratio_ema * k)` — целевой размер блока
6. `local_min_block = max(min_block, limit * 2)` — нижняя граница не меньше двух страниц
7. Зажимает `target` в `[local_min_block, max_block]`
8. Читает `current` из `GlobalParams(block_size_param)`, при ошибке использует `default_block`
9. Если `abs(target - current) / current < change_threshold (0.15)` → возврат без изменений
10. Сохраняет новый `ratio_ema` и `target` в `GlobalParams`, логирует через `sbis.LogMsg`
11. Возвращает `target`

**Параметры `k` и `change_threshold`:**
- `k=2.5` — запас блока сверх рассчитанного минимума
- `change_threshold=0.15` — гистерезис 15%, защита от дёрганья при незначительных изменениях

---

## Требования к SQL-запросу в итеративном режиме

### Стандартный режим (_iterative=False)

SQL получает Python-форматирование через `.format(...)`:
```sql
SELECT ... FROM "ВидЦеныДокумент"
WHERE "DateWTZ" {_operator} !DateWTZ::TIMESTAMP
ORDER BY "DateWTZ" {_order}
LIMIT {_limit}
```
Параметры `{_operator}`, `{_order}`, `{_limit}` — Python `str.format`.
Фильтры и курсор — через `!Param` (sbis.Template).

### Итеративный режим (_iterative=True)

SQL только через `!Param`:
```sql
WITH "UnfilteredRecords" AS (
    SELECT "SaleId", "DateWTZ" FROM "ВидЦеныДокумент"
    WHERE "DateWTZ" !_operator !DateWTZ::TIMESTAMP
    ORDER BY "DateWTZ" !_order
    LIMIT !_iterative_block_size
)
SELECT *, FALSE AS "_IsControlRecord", 0 AS "ScannedCount", 0 AS "RawResultCount"
FROM "UnfilteredRecords"
WHERE <основные условия фильтрации>
LIMIT !_limit

UNION ALL

-- Контрольная запись: ключ следующего блока + статистика
SELECT
    "SaleId", "DateWTZ",
    TRUE AS "_IsControlRecord",
    (SELECT COUNT(*) FROM "UnfilteredRecords") AS "ScannedCount",
    (SELECT COUNT(*) FROM "UnfilteredRecords" WHERE <условия>) AS "RawResultCount"
FROM "UnfilteredRecords"
ORDER BY "DateWTZ" !_order
LIMIT 1
```

**Обязательные поля контрольной записи:**
- `_IsControlRecord = TRUE`
- Ключи курсора (`DateWTZ` и др.) для `nextPosition`

**Дополнительно (для `IterativeBlockSizeEmaMixin`):**
- `ScannedCount` — размер блока (`COUNT(*)` до фильтрации)
- `RawResultCount` — количество записей после фильтрации

---

## Пример: добавить новый итеративный реестр

```python
# bonus/get_sale_list.py
from priceformationcommon.helpers.params import GlobalParams
from priceformationonline.loyaltyprograms.loyaltyprogram.helpers import (
    ListWithCompositeCursor, IterativeBlockSizeEmaMixin,
)
from priceformationonline.loyaltyprograms.loyaltyprogram.get_sale_list import SaleListWithCursor


class BonusSaleListWithCursor(SaleListWithCursor):
    def __init__(self):
        super().__init__()
        self._is_bonus = True
        self._default_filters = {'ProgramId': None, 'ClientId': None}
        self._query = """
            WITH "UnfilteredRecords" AS (
                SELECT "SaleId", "DateWTZ", "Bonus"
                FROM "ВидЦеныДокумент"
                WHERE "DateWTZ" {_operator} !DateWTZ::TIMESTAMP
                  AND "ProgramId" = !ProgramId
                ORDER BY "DateWTZ" {_order}
                LIMIT {_limit}
            )
            SELECT *, FALSE AS "_IsControlRecord" FROM "UnfilteredRecords"
            WHERE "ClientId" = !ClientId
            LIMIT {_limit}
        """

    def get_result(self, filters, navigation):
        data = self._get_result(filters, navigation)
        self._add_sale_data(data, filters.Get('Search'))
        return data


# Итеративный вариант через MRO
class BonusSaleListIterative(IterativeBlockSizeEmaMixin, ListWithCompositeCursor, BonusSaleListWithCursor):
    _BLOCK_SIZE_PARAM = 'Bonus.GetSaleList.IterativeBlockSize'
    _RATIO_EMA_PARAM  = 'Bonus.GetSaleList.IterativeRatioEMA'

    def __init__(self):
        super().__init__()
        self._iterative = True
        self._iterative_block_size = int(
            GlobalParams(self._BLOCK_SIZE_PARAM).get() or self._DEFAULT_BLOCK
        )
        # SQL переписывается под итеративный режим (только !Param, контрольная запись, ScannedCount/RawResultCount)
        self._query = "..."

    def _prepare_next_position_iterative(self, result, direction, navigation_data):
        self._tune_iterative_block_size_from_result(result, navigation_data)
        return super()._prepare_next_position_iterative(result, direction, navigation_data)
```

> [!warning] SQL в итеративном режиме — другой шаблон
> `_query` в `BonusSaleListIterative` **обязательно переопределять**: стандартный шаблон из
> `BonusSaleListWithCursor` содержит Python `{_operator}` и не совместим с итеративным режимом.
