---
type: synthesis
address: c-000068
title: "BonusChart-IterativeBlock-Bug-Fix"
created: 2026-05-20
updated: 2026-05-20
tags:
  - price-formation
  - loyalty
  - iterative-nav
  - bug-fix
  - chart-data
status: developing
related:
  - "[[ReferralBonus-GetSaleList-Iterative-Ordering-Bug]]"
  - "[[Bonus-GetSaleTotals-Timeout-Fix]]"
  - "[[CursorNavigation-Mechanism]]"
  - "[[Price-Formation-Test-Runner]]"
---

# Кривые данные на графике продаж — итеративный блок ВЦД

## Симптом

При включённой фиче `loyalty_it_nav` графики в реестрах **Бонусы\Покупки** и **Реферальная система\Покупки** показывают данные только в конце месяца. Начало и середина месяца пустые. Воспроизводится на аккаунтах с большим объёмом данных (инсайд, лояльность/лояльность123).

## Root Cause

Данные для графика запрашиваются из `get_graphic_data.py` через вызов:

```python
filters = sbis.Record({'PeriodStart': ..., 'PeriodEnd': ..., 'WithoutResults': True})
data = get_list_method(None, filters, None, navigation)
```

При `loyalty_it_nav=True` вызов маршрутизируется в итеративные классы (`BonusSaleListIterative`, `ReferralBonusSaleListWithCursorIterative`). Их SQL строит `UnfilteredRecords` CTE с `LIMIT !_iterative_block_size` (10 000 по умолчанию) и `ORDER BY EffectiveDate DESC`. На крупных аккаунтах 10K строк охватывают только хвост месяца — вся агрегация графика работает с неполными данными.

## Ключевые файлы

| Файл | Что происходит |
|------|---------------|
| `get_graphic_data.py` | Вызывает `Bonus/ReferralBonus.GetSaleList(WithoutResults=True)` для сбора данных графика |
| `loyaltyprograms/bonus/get_sale_list.py` | `BonusSaleListIterative` — `UnfilteredRecords LIMIT 10K` |
| `loyaltyprograms/referralbonus/get_sale_list.py` | `ReferralBonusSaleListWithCursorIterative` — то же |

## Fix

В обоих итеративных классах добавлены два метода:

```python
def get_result(self, filters, navigation):
    self._without_results = bool(filters.Get('WithoutResults'))
    if self._without_results:
        self._iterative_block_size = 2_000_000_000  # снимает LIMIT в UnfilteredRecords
    return super().get_result(filters, navigation)

def _prepare_next_position_iterative(self, result, direction, navigation_data):
    if not self._without_results:
        self._tune_iterative_block_size_from_result(result, navigation_data)  # EMA только для реестра
    return super()._prepare_next_position_iterative(result, direction, navigation_data)
```

**Почему 2B, а не NULL**: `_iterative_block_size` инициализируется в `__init__` и используется в шаблоне как `LIMIT !_iterative_block_size`. Передача очень большого числа даёт `LIMIT 2000000000` — эффективно «без лимита».

**Почему пропускаем EMA**: `_tune_iterative_block_size_from_result` сохраняет новый размер блока в `GlobalParams`. При `WithoutResults=True` `ScannedCount` будет равен полному размеру периода (потенциально огромному) — это сломало бы EMA для нормального реестра.

**Почему не трогаем не-итеративный класс**: после выпиливания фичи `loyalty_it_nav` не-итеративные классы будут удалены. Фикс изолирован в итеративных классах.

## Тесты

В каждый тестовый файл добавлен тест-регрессия:
- `bonus/get_sale_list.py::GetSaleList::test_7_without_results_scans_full_period_despite_small_block`
- `referralbonus/get_sale_list.py::GetSaleList::test_5_without_results_scans_full_period_despite_small_block`

Механика теста: мокируем `GlobalParams.get()` → `'1'` (block_size=1), создаём две продажи с `effective_date` разницей в 20 дней, вызываем `WithoutResults=True`, проверяем что обе продажи в результате. Без фикса ранняя продажа терялась.

## Связанный контекст

- Фича `loyalty_it_nav` → `BonusItNav` — новое поведение, старый код будет удалён после выпиливания флага.
- Аналогичная фича существует для `ReferralBonus`, `PromoCode`, `DiscountCard` — у остальных данная проблема может присутствовать тоже.
- Кэширование данных графика по аккаунту делало баг видимым для всех пользователей аккаунта, не только тех, у кого включена фича.
