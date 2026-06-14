---
type: concept
address: c-000060
title: "SabyBank-Stub-Rewards-Calculation"
created: 2026-05-20
updated: 2026-05-20
tags:
  - price-formation
  - referral-program
  - sabybank
  - sql
  - bug-fix
status: current
related:
  - "[[SetLeadPrice-SABYBANK-Stub-Branch]]"
  - "[[SabyBank-RKO-Referral]]"
  - "[[Loyalty-Database-Schema]]"
  - "[[ReferralDeals-System]]"
---

# SabyBank: калькуляция вознаграждений по корешкам в виджетах и реестрах

## Контекст

Программы рефералки типа `SabyBank` (`ProgramType = 1`) работают по-другому: вознаграждение привязано не к сделке CRM (`Документ`), а к «корешку» — записи `ВидЦеныДокумент` с `ТипСвязи IS NOT NULL`. `SetLeadPrice` уже переключён на корешки ([[SetLeadPrice-SABYBANK-Stub-Branch]]). Задача — привести к единообразию три оставшихся места, где считаются суммы вознаграждений.

## Что изменено

### 1. `get_stats_helpers.py` — виджеты GetStats / GetStatsByPartner

Функция `sql_get_price_stats` строит LEFT JOIN `ВидЦеныДокумент` → суммирует `Бонусы`. В JOIN-условие добавлен один `{% item %}`:

```sql
{% item %}
    COALESCE((program."Атрибуты"->'ReferralProgram'->>'ProgramType')::INT, 0) <> 1
    OR ptd."ТипСвязи" IS NOT NULL
{% enditem %}
```

**Логика:** если программа НЕ SabyBank → запись проходит всегда; если SabyBank → только корешки. Таблица `program` уже есть в JOIN-scope (`JOIN "ВидЦены" program ON ...`) — Python не трогаем.

**Важно:** `<>` вместо `!=` — sbis-шаблонизатор воспринимает `!` как префикс параметра, `!= 1` → ошибка `parameter name expected`.

### 2. `get_lead_period_list.py` — реестр заявок по периодам

**Python:** перед `get_list_by_cursor` читаем тип программы и кладём флаг в filters:

```python
from priceformationonline.referralprogram.referralprogram.core import (
    ProgramType,
    ReferralProgramRepository,
)

referral_program = ReferralProgramRepository.read(filters.Get('ReferralProgramId'))
filters.Put('IsSabyBank', referral_program.program_type == ProgramType.SABYBANK, sbis.FieldType.ftBOOLEAN)
```

`ProgramType.SABYBANK` — это `int`, не Enum; `.value` не нужен (упадёт с `AttributeError`).

**SQL:** `'IsSabyBank'` добавлен в `valid_param_list`. Условие Price-подзапроса:

```sql
AND (
    (
        -- Вознаграждения по корешкам РКО (SabyBank)
        !IsSabyBank::BOOLEAN
        AND ptd."ТипСвязи" IS NOT NULL
        AND ptd."EffectiveDate" BETWEEN res.period[1]::date
        AND (res.period[2]::date + '1 day'::interval - '1 msec'::INTERVAL)
    )
    OR (
        -- Вознаграждения по сделкам и посетителям (стандартные программы)
        NOT !IsSabyBank::BOOLEAN
        AND (
            (
                ptd."Документ" IS NOT NULL
                AND ptd."EffectiveDate" BETWEEN res.period[1]::date
                AND (res.period[2]::date + '1 day'::interval - '1 msec'::INTERVAL)
            )
            OR (
                ptd."Документ" IS NULL
                AND ptd."ДатаВремя" BETWEEN res.period[1]::date
                AND (res.period[2]::date + '1 day'::interval - '1 msec'::INTERVAL)
            )
        )
    )
)
```

### 3. `GetPartnerList` — отложено

Деferred в отдельную задачу — не трогаем.

## Тестовый паттерн — корешок без отдельной модели

Для SabyBank-тестов используется двухшаговый паттерн (без отдельной ORM-модели `ReferralProgramStub`):

```python
# Шаг 1: создать запись (без link_type)
stub = PriceEntitySaleDoc.create(
    price_entity=program.id,
    card=code,
    date_time=datetime.datetime(2025, 5, 1),
    effective_date=datetime.datetime(2025, 6, 15),
    bonuses=400,
)
# Шаг 2: проставить ТипСвязи через второй класс
stub_ret = PriceEntityRetailSaleDoc.get_by_id(stub.id)
stub_ret.link_type = 15  # 10=in progress, 15=success, 20=failed
stub_ret.save()
```

`PriceEntitySaleDoc` — нет поля `link_type`. `PriceEntityRetailSaleDoc` — есть `link_type = SmallIntegerField(column_name='ТипСвязи')`. Оба маппятся на `ВидЦеныДокумент`.

## Нюансы

- Корешок с `ТипСвязи = 10` (in progress): у него `EffectiveDate IS NULL` → условие `BETWEEN` даёт NULL → запись не засчитывается. Корректное поведение.
- Стандартная запись без `ТипСвязи` (для SabyBank-программ) — не засчитывается. Проверено тестом.
- Функция `sql_get_price_stats` используется и для `GetStats` (режим REFERRAL_PROGRAM), и для `GetStatsByPartner` (режим PARTNER) — один фикс покрывает оба.

## Связанные файлы

| Файл | Изменение |
|------|-----------|
| `referralprogram/get_stats_helpers.py` | `{% item %}` в JOIN ON условие |
| `referralprogram/get_lead_period_list.py` | Python: `IsSabyBank` флаг; SQL: ветвление по флагу |
| `tests_new/.../get_lead_period_list.py` | `test_get_periods_sabybank` |
| `tests_new/.../get_stats.py` | `test_sabybank_price_from_stubs` |
