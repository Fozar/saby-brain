---
type: concept
address: c-000053
title: "JSONB Array Containment Optimization"
created: 2026-05-19
updated: 2026-05-19
tags:
  - postgresql
  - performance
  - jsonb
  - sql-optimization
  - price-formation
status: current
related:
  - "[[Wasaby-DB-Access-Patterns]]"
  - "[[PriceFormation-Backend-Architecture]]"
  - "[[Loyalty-Public-API]]"
---

# JSONB Array Containment Optimization

## Проблема: коррелированный подзапрос с `jsonb_array_elements_text`

Паттерн EXISTS + unnest создаёт SubPlan, который выполняется **один раз на каждую строку** основного запроса. При 711 строках и ~3 элементах в массиве — это 2000+ итераций функции:

```sql
-- АНТИПАТТЕРН: SubPlan выполняется N раз
EXISTS (
    SELECT 1
    FROM jsonb_array_elements_text(
        COALESCE(
            NULLIF(card_type."Атрибуты" #> '{Card,SalePointIdList}', 'null'::jsonb),
            '[]'::jsonb
        )
    ) AS sp_id(txt)
    WHERE sp_id.txt::integer = !sales_point_id::integer
)
```

EXPLAIN для такого запроса:
```
SubPlan 1
  ->  Function Scan on jsonb_array_elements_text sp_id  (loops=711)
        Filter: ((txt)::integer = 243504)
        Rows Removed by Filter: 2061
        actual time=0.549..0.549 rows=0 per loop
```

Суммарно: 711 × 0.549ms ≈ 390ms только на SubPlan, плюс 2061 лишних сравнений.

---

## Решение: оператор `@>` (containment)

Оператор `@>` вычисляется **inline** на каждую строку без создания SubPlan:

```sql
-- ПРАВИЛЬНО: inline containment, никакого SubPlan
NULLIF(card_type."Атрибуты" #> '{Card,SalePointIdList}', 'null'::jsonb) IS NULL
OR (card_type."Атрибуты" #> '{Card,SalePointIdList}') @> to_jsonb(!sales_point_id::integer)
```

Логика полностью сохраняется:
- `NULLIF(..., 'null'::jsonb) IS NULL` → если список точек не задан (SQL NULL или jsonb null) — карта применима везде (возвращаем `true`)
- `@> to_jsonb(...)` → проверка вхождения ID в массив без разворачивания

---

## Применение в `has_applicable_benefits_by_sales_point`

Реальный случай из `LoyaltyProgram.HasApplicableBenefitsBySalesPoint`:

```sql
-- БЫЛО (два SubPlan, 711 loops каждый):
SELECT
    bool_or(
        (
            NULLIF(card_type."Атрибуты" #> '{Card,SalePointIdList}', 'null'::jsonb) IS NULL
            OR EXISTS (
                SELECT 1 FROM jsonb_array_elements_text(COALESCE(...)) AS sp_id(txt)
                WHERE sp_id.txt::integer = !sales_point_id::integer
            )
        )
    ) FILTER (...) AS has_discount_cards
    ...

-- СТАЛО (никаких SubPlan):
SELECT
    bool_or(
        NULLIF(card_type."Атрибуты" #> '{Card,SalePointIdList}', 'null'::jsonb) IS NULL
        OR (card_type."Атрибуты" #> '{Card,SalePointIdList}') @> to_jsonb(!sales_point_id::integer)
    ) FILTER (WHERE card_type."Тип" = ANY(!discount_card_types::integer[])) AS has_discount_cards
,   bool_or(
        NULLIF(card_type."Атрибуты" #> '{PromoCode,SalePointIdList}', 'null'::jsonb) IS NULL
        OR (card_type."Атрибуты" #> '{PromoCode,SalePointIdList}') @> to_jsonb(!sales_point_id::integer)
    ) FILTER (WHERE card_type."Тип" = ANY(!promo_code_types::integer[])) AS has_promo_codes
FROM "ВидКарты" card_type
WHERE ...
```

Результат: время запроса снизилось с ~435ms до ~1ms (Seq Scan по 739 строкам без SubPlan).

---

## Тип данных в JSON: integer vs text

Ключевой вопрос: как хранятся ID в JSON-массиве?

| Формат в JSON | Правильный `@>` |
|---|---|
| `[123, 456]` (числа) | `@> to_jsonb(!id::integer)` |
| `["123", "456"]` (строки) | `@> to_jsonb(!id::text)` |

`jsonb_array_elements_text` маскирует разницу (возвращает `text` для обоих форматов). При переходе на `@>` нужно знать фактический тип.

Для `SalePointIdList` в `ВидКарты."Атрибуты"` — хранятся как JSON-числа → используем `::integer`.

---

## Когда применять

Этот рефактор применим всегда, когда:
1. JSON-массив содержит идентификаторы (int или text)
2. Нужно проверить вхождение одного значения в массив
3. Запрос выполняется в контексте агрегации или большого набора строк

Не применять, если нужна сложная фильтрация элементов массива (несколько условий — тогда `jsonb_array_elements` с WHERE остаётся уместным).

---

## Сопутствующий косметический рефактор

Из той же сессии — два мелких улучшения:

```python
# Объединение импортов из одного модуля
# БЫЛО:
from priceformationcommon.discountcard.emission.const import ItemType
from priceformationcommon.discountcard.emission.const import ItemArchetype
# СТАЛО:
from priceformationcommon.discountcard.emission.const import ItemArchetype, ItemType

# Упрощение None-проверок для булевых полей из SQL
# БЫЛО:
has_discount_cards = applicable_benefits.Get('has_discount_cards')
if has_discount_cards is None:
    has_discount_cards = False
# СТАЛО:
has_discount_cards = applicable_benefits.Get('has_discount_cards') or False
# Безопасно: bool_or() возвращает только True, False или NULL — не другие falsy-значения
```
