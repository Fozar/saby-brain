---
type: synthesis
title: "ReferralProgram Zero Reward Lead Filter Bug"
created: 2026-06-10
updated: 2026-06-10
tags:
  - loyalty
  - referralprogram
  - bugfix
  - rss
status: fixed
related:
  - "[[ReferralProgram-Module]]"
  - "[[ReferralDeals-System]]"
  - "[[Loyalty-Database-Schema]]"
question: "Почему лиды, завершённые положительно с нулевым вознаграждением, не отображаются в РСС при фильтре 'Завершено положительно'?"
answer_quality: solid
---

# ReferralProgram Zero Reward Lead Filter Bug

**Task:** https://online.sbis.ru/opendoc.html?guid=4e532aba-f2a8-4c05-ac16-ff58ece25e23&client=3 (№05265686, стенд)

Решение согласовано Мусохрановым Андреем: убрать условие `Бонусы > 0` из фильтра + записывать ВЦД для всех положительно завершённых лидов включая нулевое вознаграждение.

---

## Bug

В портале реферальной программы (РСС) при фильтрации по статусу **«Завершено положительно»** не отображаются лиды, завершённые положительно **без вознаграждения** (нулевой или незаданный бонус). Оба типа программ затронуты:

- **CURRENCY с price=0** — фиксированное вознаграждение 0 руб.
- **PERCENT до ручной установки** — вознаграждение не задано (NULL) до момента когда менеджер его проставит через `SetLeadPrice`.

---

## Root Cause

Двухсторонний баг: **write-side** и **read-side**.

### Write side — `handle_lead_state_changed.py`

```python
# lines 47–50 (до фикса)
price = _calculate_price_per_lead(referral_program, lead_sum, referral_rec.Get('PricePerLead'))
# Для фиксированного вознаграждения игнорируем неположительные суммы.
# Для процента возвращаем None (вставка остается, но без начисления).
if not (price is None or price > 0):
    return
```

Условие `if not (price is None or price > 0)` срабатывает при `price == 0`: запись в `ВидЦеныДокумент` **не создаётся**, `EffectiveDate` не устанавливается — лид вообще не попадает в базу.

`_calculate_price_per_lead` возвращает:
- `to_money(price_per_lead)` для CURRENCY → `Decimal('0.00')` при price_per_lead=0
- `None` для PERCENT (None корректно проходит проверку, запись создаётся)

### Read side — `get_lead_list.py`

```sql
-- _SQl_GET_COMPLETED_SUCCESS_LEAD_IDS (строка 178, до фикса)
AND ptd."EffectiveDate" BETWEEN !DateBegin::date AND (...)
AND ptd."Бонусы" > 0   -- <-- исключает Бонусы=0 и Бонусы=NULL
```

Этот запрос собирает список `LeadId` для передачи в `SourcesSales.GetRawDocs` при фильтрации по статусу "Завершено положительно". Условие `Бонусы > 0` исключало:
- CURRENCY leads с bonuses=0
- PERCENT leads с bonuses=NULL (до ручной установки)

**Примечание:** `_SQL_GET_PRICE_BY_LEAD` (обогащение данных отображения) тоже содержит `AND ptd."Бонусы" > 0` — это **корректно** и не трогалось: в список обогащения должны попадать только записи с реальным вознаграждением.

---

## Fix

### Write side

```python
# handle_lead_state_changed.py lines 47–50 (после фикса)
price = _calculate_price_per_lead(referral_program, lead_sum, referral_rec.Get('PricePerLead'))
# Для процента возвращаем None (вставка остается, но без начисления).
# Для фиксированного вознаграждения игнорируем только отрицательные суммы.
if price is not None and price < 0:
    return
```

Теперь при price=0 (CURRENCY с нулевым вознаграждением) запись ВЦД создаётся, `EffectiveDate` устанавливается.

### Read side

```sql
-- _SQl_GET_COMPLETED_SUCCESS_LEAD_IDS (после фикса)
AND ptd."EffectiveDate" BETWEEN !DateBegin::date AND (...)
-- убрана строка: AND ptd."Бонусы" > 0
```

`EffectiveDate` — безопасный маркер «завершено положительно»: он устанавливается **только** через `handle_lead_state_changed` (состояние «Выполнение завершено успешно»). Посетительские строки ВЦД (Документ IS NULL) не имеют EffectiveDate — они не попадут в выборку.

---

## Generalizable insight

> [!key-insight] `Бонусы > 0` в запросе идентификации лидов — некорректный фильтр-прокси для статуса «завершено положительно». Правильный маркер завершения — `EffectiveDate IS NOT NULL` (он устанавливается только при положительном закрытии). `Бонусы` — атрибут вознаграждения, не статуса. Смешивание двух семантик (статус vs атрибут) — источник этого класса багов.

---

## Historical data caveat

Лиды, завершённые **до** применения фикса с CURRENCY и price=0, записи в ВЦД **не имеют** — они не появятся даже после деплоя. Это принято как известное ограничение (Мусохранов А.).

---

## Tests

**Обновлён:** `tests_new/online/src/tests_priceformationonline/referralprogram/referralprogram/handle_lead_state_changed.py`
- `test_zero_price_currency`: был `assertEqual(count, 0)` → теперь проверяет что запись создана с `bonuses=0` и `effective_date` установлен.

**Добавлен:** `tests_new/online/src/tests_priceformationonline/referralprogram/referralprogram/get_lead_list.py`
- `test_completed_success_includes_zero_reward_lead`: создаёт ВЦД-записи с `bonuses=0` и `bonuses=None`, проверяет что оба лида попадают в `ObjectIds` при фильтрации по «Завершено положительно».

**QA:** тестовая база (`_sbis_test_db_2026-06-05T02-19-10-114984`) устарела — перед прогоном нужен `test_manager`.

---

## Changed files

- `www/service/Модули/PriceFormation.Online/priceformationonline/referralprogram/referralprogram/handle_lead_state_changed.py` — условие early-return: `price < 0` вместо `not (price is None or price > 0)`.
- `www/service/Модули/PriceFormation.Online/priceformationonline/referralprogram/referralprogram/get_lead_list.py` — убрана строка `AND ptd."Бонусы" > 0` из `_SQl_GET_COMPLETED_SUCCESS_LEAD_IDS`.
- `tests_new/online/src/tests_priceformationonline/referralprogram/referralprogram/handle_lead_state_changed.py` — обновлён `test_zero_price_currency`.
- `tests_new/online/src/tests_priceformationonline/referralprogram/referralprogram/get_lead_list.py` — добавлен `test_completed_success_includes_zero_reward_lead`.

Ветка: `26.4100/bugfix/aatimoshenko/06087022`.
