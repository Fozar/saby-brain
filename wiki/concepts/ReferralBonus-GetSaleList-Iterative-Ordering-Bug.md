---
type: synthesis
address: c-000056
title: "ReferralBonus GetSaleList Iterative Ordering Bug"
created: 2026-05-19
updated: 2026-05-26
tags:
  - bugfix
  - loyalty
  - referral
  - iterative-loading
  - postgresql
  - cursor-navigation
  - add-graphic-data
  - asc-ordering
status: fixed
related:
  - "[[LoyaltyPrograms-IterativeListLoading]]"
  - "[[CursorNavigation-Mechanism]]"
  - "[[Referral-Bonus-Program]]"
  - "[[Loyalty-Database-Schema]]"
  - "[[PostgreSQL-CTE-Cursor-Pushdown]]"
---

# ReferralBonus.GetSaleList — Баг порядка записей в итеративном реестре

**Файл**: `priceformationonline/loyaltyprograms/referralbonus/get_sale_list.py`  
**Класс**: `ReferralBonusSaleListWithCursorIterative`  
**Флаг**: `Feature.LOYALTY_IT_NAV`

## Симптомы

- Август 2025 отображается выше апреля 2025 при переключении на апрель
- Графические записи (GraphicData) появляются между записями одного месяца
- Заголовок показывает август при открытии апреля

## Root Cause 1: GROUP BY (Sale, EffectiveDate)

Оригинальный `SalesWithRefCustomers` CTE:
```sql
SELECT U."Sale" AS "SaleId",
       SUM(U."Бонусы") AS "Bonuses",
       U."EffectiveDate" AS "DateWTZ",   -- НЕ агрегирован
       MAX(U."TotalPrice") AS "TotalPrice"
FROM "UnfilteredRecords" AS U
...
GROUP BY U."Sale", U."EffectiveDate"     -- EffectiveDate в ключе
```

Одна продажа может иметь несколько строк ВЦД с **разными** `EffectiveDate` (начисление + ретроактивная корректировка). `GROUP BY (Sale, EffectiveDate)` создаёт несколько строк с одинаковым `SaleId` → `Id='R{SaleId}'` дублируется в Controls → артефакты рендеринга.

## Root Cause 2: Нестабильная сортировка

```sql
ORDER BY "DateWTZ" {% ifequal _order "DESC" %} DESC {% endif %}
-- SaleId отсутствует как вторичный ключ
```

При совпадении `DateWTZ` у нескольких продаж PostgreSQL возвращает их в случайном порядке → на разных запросах разный порядок → графические записи попадают в неправильные позиции.

## Fix

```sql
-- SalesWithRefCustomers CTE:
SELECT U."Sale" AS "SaleId",
       SUM(U."Бонусы") AS "Bonuses",
       MAX(U."EffectiveDate") AS "DateWTZ",  -- агрегация MAX
       MAX(U."TotalPrice") AS "TotalPrice"
...
GROUP BY U."Sale"                             -- только Sale

-- ResultPage ORDER BY:
ORDER BY "DateWTZ" {% ifequal _order "DESC" %} DESC {% endif %},
         "SaleId" {% ifequal _order "DESC" %} DESC {% endif %}

-- Финальный UNION ORDER BY:
ORDER BY "_IsControlRecord",
         "DateWTZ" {% ifequal _order "DESC" %} DESC {% endif %},
         "SaleId" {% ifequal _order "DESC" %} DESC {% endif %}
```

## Почему не ListWithCompositeCursor

Фронтенд `client/LoyaltyOnline/Referral/Sales/Config.ts` использует `field: 'DateWTZ'` (плоский курсор) — без переключения на `field: 'cursor'` при `loyalty_it_nav`. Это означает:

- `ListWithCursor._get_position_from_record` → `['2025-04-08 10:00:00']` (плоский список) — **правильно**
- `ListWithCompositeCursor` → `[{'DateWTZ': '...'}]` → фронт обернёт в `{DateWTZ: {'DateWTZ': '...'}}` — **сломает курсор**

Для сравнения: `Bonus.GetSaleList` (`BonusSaleListIterative`) использует `ListWithCompositeCursor` + фронт переключается на `field: 'cursor'` при `loyalty_it_nav=ON`. Referral фронт такого переключения не имеет.

## Паттерн из BonusSaleListIterative

Исправление идентично паттерну из `BonusSaleListIterative`:
```sql
-- BonusRetailSales (эталон):
MAX("UnfilteredRecords"."EffectiveDate") AS "DateWTZ"
GROUP BY "SaleId", "DocumentId"   -- DocumentId=NULL для розницы → GROUP BY SaleId
ORDER BY "DateWTZ" ..., "SaleId" ..., "DocumentId" ...
```

У Referral нет складских продаж → `GROUP BY Sale` без `DocumentId`.

## Принятое ограничение

Одинаковый для Bonus и Referral: при `ResultPage LIMIT` срезающем посередине группы одного `DateWTZ` следующий вызов (`EffectiveDate > cursor`) пропустит хвост группы. Возникает только если `> page_size` реферальных продаж приходится на один блок. В тесте: 17 652 ВЦД → 30 продаж (ratio ~192).

## Как заполняются ВЦД для Referral

При покупке участника реферальной программы `Accrual` создаёт строки ВЦД для каждого уровня реферальной иерархии (уровень 1/2/3). Все строки создаются в одной транзакции → одинаковый `EffectiveDate` в типичном случае. Разные `EffectiveDate` = ретроактивная корректировка (редко).

## Тест

`tests_priceformationonline/loyaltyprograms/referralbonus/get_sale_list.py::test_4`:
```python
# Одна продажа + два ВЦД с разными EffectiveDate
PriceEntityRetailSaleDoc.create(sale=sale, card=card, referral_customer=buyer,
    bonuses=50, total_price=1000, activated=True, effective_date=now - timedelta(days=2))
PriceEntityRetailSaleDoc.create(sale=sale, card=card, referral_customer=buyer,
    bonuses=-20, total_price=1000, activated=True, effective_date=now - timedelta(days=1))

result = sbis.ReferralBonus.GetSaleList([], sbis.Record({'WithoutResults': True}), None, None)
sale_rows = [r for r in result if r.SaleId == sale.id]
assertEqual(len(sale_rows), 1)  # без дублей
```

**Нюанс**: флаг `WithoutResults` (с S) — именно так проверяет `BonusSaleListWithCursor.get_result`. `WithoutResult` (без S) игнорируется → вызывается `Sale.BuildList` → в тестовой среде продажа не находится → запись удаляется.

`Card.create(person=referrer)` + `referral_customer=buyer` достаточно: `referrer` попадает в `RefCustomers` через второй UNION (`Карта.Лицо` в строке с `ReferralCustomer IS NOT NULL`).

## Git-история

Ни одного коммита с попыткой составного курсора для Referral. `ListWithCompositeCursor` существует для Bonus (`BonusSaleListIterative`, `6893757737`) и PromoCode (`ae3ede9ba5`), но не для Referral. Ближайший коммит по файлу: `dc8f7c09be` — замена `TIMESTAMPTZ` → `TIMESTAMP` в курсорном сравнении.

---

## Баг 04297958 — Хаотичный порядок при прокрутке вверх (backward scroll)

**Задача**: [04297958 на стенде](https://online.sbis.ru/opendoc.html?guid=04297958&client=3); возвращался дважды → переоткрыт под 04307024 (работа на `rc-26.3100`)  
**Статус**: **ИСПРАВЛЕНО** (2026-05-27, Opus 4.7).

> [!warning] Две предыдущие попытки были неверны
> 1. Ветка `04297958_2` закоммитила только устранение дублей строк (Root Cause 1/2) — порядок не трогала.
> 2. Правка `add_graphic_data` (инверсия вставки для backward, «фронт сам разворачивает») — **ложная гипотеза**. Свежий лог `pre-test-online-27-05-2026` показал: при `Direction: backward` БЛ отдаёт recordset в **ASC**, фронт его **не разворачивает**. Эта правка откачена.
>
> Истинная причина и фикс — ниже.

### Симптом

При ручной прокрутке вверх из апреля 2025 в реестре «Реферальная система/Покупки» появляется хаотичный порядок:
```
26 августа → график → 11 августа → Июль '25 → 11 августа снова → 30 июля
```
Две разные продажи с `Aug11` разделены заголовком «Июль '25».

### Ожидаемый визуальный порядок (сверху вниз)

```
[Итоги месяца] [График месяца] [покупки, новая→старая] [Итоги след.месяца] [График след.месяца] [покупки] ...
```
Одинаков и при прокрутке вниз (forward), и при прокрутке вверх (backward).

### Root Cause (истинная)

В кодовой базе есть **канонический контракт** курсорной навигации
(`PriceFormation.Common/priceformationcommon/core/cursor_navigation.py:152-156`): для backward запрос идёт в
**ASC** (нужно, чтобы взять записи «над курсором» и корректно вычислить границу), а затем результат
**разворачивается** хелпером `_reverse()` в DESC для отображения.

Итеративный путь loyalty (`ListWithCursor` / `ListWithCompositeCursor` в `loyaltyprogram/helpers.py`,
метод `_get_result_in_one_direction_iterative`) этого разворота **не делал** — финальный `ORDER BY` в SQL
использует `{_order}` (ASC для backward), и recordset уходил на фронт как есть. Не-итеративный referral-запрос
обходил это, форсируя `ORDER BY DateWTZ DESC` снаружи (`referralbonus/get_sale_list.py:114`), а итеративный — нет.

`add_graphic_data` тут **ни при чём** — она корректно работает с DESC-данными. Просто данные приходили в ASC.

**Почему нельзя просто поменять SQL `ORDER BY` на DESC:** `_prepare_next_position_iterative`
(`helpers.py`, ~стр. 331/346-347) берёт **последнюю строку** результата как границу курсора. При backward это
должна быть новейшая запись = последняя в ASC. Форсирование DESC в SQL сломало бы пагинацию. Поэтому выборка
остаётся ASC, а разворот — в Python **после** вычисления позиции.

### Принятое решение

1. **Откат** правки `add_graphic_data` к оригиналу (DESC-only, без ветки `is_backward` и хелперов).
2. **Разворот результата для backward в итеративном пути.** Файл `loyaltyprogram/helpers.py`:
   - модульный хелпер `_reverse_record_set(record_set)` (аналог канонического `_reverse`);
   - в обоих `_get_result_in_one_direction_iterative` (`ListWithCursor` и `ListWithCompositeCursor`) **после**
     вычисления `next_position`/`prev_position`, перед `return`:
     ```python
     if direction == self.BACKWARD and result:
         result = _reverse_record_set(result)
     ```
   В этой точке у `result` ещё нет nav-метаданных (навешиваются позже в `_get_result`), контрольная запись уже
   удалена — разворот безопасен, курсор не ломается.

Покрывает все итеративные курсорные реестры (Referral/Bonus/PromoCode/Promotion GetSaleList, ReferralBonus.GetActionList).

### Почему курсор не ломается

`_reverse` идёт строго ПОСЛЕ извлечения позиций: `next_position` берётся из ASC (последняя строка = новейшая =
правильная граница backward), `prev_position` из `result[0]`, и лишь затем разворачиваются отображаемые строки.
Это в точности приём канонического `cursor_navigation._navigate`.

### Тесты (зелёные)

1. `tests/.../referralbonus/get_sale_list.py::GetSaleList::test_6_backward_returns_descending_order` —
   интеграционный: две продажи в разных месяцах, backward-навигация с курсором старше обеих, проверка
   `DateWTZ` по убыванию (DESC). `WithoutResults=True` минует `add_graphic_data`/`business-calendar`, но разворот
   в итеративном пути применяется. `closed=effective_date`, чтобы обе ветки флага (iterative/non-iterative) были стабильны.
2. `tests/.../loyaltyprogram/get_graphic_data.py::AddGraphicData` — юнит на оригинальную DESC-расстановку
   (`test_forward_desc_order_unchanged`, `test_backward_desc_data_same_as_forward`), моки
   `get_graphic_data_by_periods` + `get_holidays_data`.

**Регресс**: `loyaltyprograms` (referralbonus/loyaltyprogram/bonus/promocode/promotion get_sale_list + action_list) — зелёные.

### Почему итеративный блок не ломает середину месяца

`LastId`/`FirstId` вычисляются независимым внутренним `GetSaleList(WithoutResults=True)` — полный скан месяца,
без блочных ограничений. Chart/totals вставляются только когда anchor-record реально попал на страницу. ✓

---

*Backward-фикс (разворот recordset в итеративном пути) реализован и проверен: Opus 4.7, 2026-05-27.*
