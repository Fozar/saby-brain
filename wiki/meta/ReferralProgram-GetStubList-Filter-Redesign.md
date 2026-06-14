---
type: decision
title: "ReferralProgram.GetStubList — редизайн фильтров"
created: 2026-05-28
updated: 2026-05-28
decision_date: 2026-05-28
status: active
tags:
  - referralprogram
  - price-formation
  - api-design
related:
  - "[[SabyBank-RKO-Referral]]"
  - "[[ReferralStub-TargetAction-Pattern]]"
---

# ReferralProgram.GetStubList — редизайн фильтров

## Решение

Контракт метода `ReferralProgram.GetStubList` изменён:

| Было | Стало |
|------|-------|
| `CreatedAtPeriod (DATE[])` | удалён |
| `StatusDatePeriod (DATE[])` | удалён |
| _(отсутствовал)_ | `Date (DATE[])` — единый период |
| _(отсутствовал)_ | `PartnerId (INT)` — фильтр по партнёру |

## Логика Date-фильтра

`Date [from, to]` — условный фильтр: колонка выбирается по наличию `Status`:

- `Status` **не указан** → фильтрация по `ptd."ДатаВремя"` (дата создания заявки)
- `Status` **указан** → фильтрация по `ptd."EffectiveDate"` (дата статуса)

Раскрытие происходит в `_prepare_filters` до передачи в SQL:

```python
has_status = filters.Get('Status') is not None
if has_status:
    filters.Put('StatusDateFrom', ...)
    filters.Put('StatusDateTo', ...)
else:
    filters.Put('CreatedAtFrom', ...)
    filters.Put('CreatedAtTo', ...)
```

## Фильтр PartnerId

Фильтрует по `k."Лицо"` (через JOIN `Карта → Лицо`). Независим от остальных фильтров.

## Затронутые файлы

- `priceformationonline/referralprogram/referralprogram/get_stub_list.py`
- `ReferralProgram.orx` — параметры `std_parameter`
- `tests/tests_priceformationonline/referralprogram/referralprogram/get_stub_list.py`

## Тесты

12 тестов, все зелёные. Переименованы:
- `test_created_at_period_filter` → `test_date_filter_by_created_at_when_no_status`
- `test_status_date_period_filter` → `test_date_filter_by_status_date_when_status_given`
- добавлен `test_partner_id_filter`
