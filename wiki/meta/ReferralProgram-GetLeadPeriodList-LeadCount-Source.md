---
type: decision
title: "ReferralProgram GetLeadPeriodList — источник LeadCount"
created: 2026-06-16
updated: 2026-06-16
decision_date: 2026-06-16
status: active
tags:
  - referralprogram
  - loyalty
  - bugfix
  - architecture
  - marketing
related:
  - "[[ReferralProgram-Module]]"
  - "[[ReferralProgram-Data-Model]]"
  - "[[ReferralProgram-Stub-Implementation]]"
  - "[[ReferralProgram-ZeroReward-Lead-Filter-Bug]]"
  - "[[SabyBank-RKO-Referral]]"
---

# ReferralProgram GetLeadPeriodList — источник LeadCount

**Task:** https://online.sbis.ru/opendoc.html?guid=7b54d7ee-8c08-4eab-951d-e794d7c0e3bf&client=3 (№04307081)

---

## Проблема

`ReferralProgram.GetLeadPeriodList` возвращает `LeadCount` (количество заявок за период), считая только лиды **с вознаграждением** — из-за фильтра `Бонусы > 0` в подзапросе по `ВидЦеныДокумент`. Лиды без вознаграждения (новые, в работе, отклонённые) не учитываются.

Дополнительная ошибка: дата привязки к периоду — `EffectiveDate` (дата закрытия/начисления), тогда как нужна дата **создания** заявки.

---

## Решение

### Стандартные программы (IsStubMode="0")

`ВидЦеныДокумент` для стандартных программ содержит записи **только** для лидов с вознаграждением — туда попадают данные только после начисления бонуса через `SetLeadPrice` (UPDATE, не INSERT). Значит, невозможно получить из ВЦД все лиды.

**Решение:** `LeadCount` для стандартных программ получается из **сервиса маркетинга** (`get_sales_sources_stats('Лид', source_ids, date_begin, date_end)`). Вызов делается per-period из Python после получения списка периодов из SQL.

```python
# get_lead_period_list.py
def _fill_lead_count_from_marketing(result: sbis.RecordSet, filters: sbis.Record):
    source_ids = _get_source_ids(filters.Get('ReferralProgramId'), filters.Get('PartnerId'))
    for rec in result:
        period_start, period_end = rec.Get('Period')
        stats = get_sales_sources_stats('Лид', source_ids, period_start, period_end)
        lead_count = sum(r.Get('Qty') or 0 for r in stats) if stats else 0
        rec.Set('LeadCount', lead_count or None)
```

В SQL для `IsStubMode="0"` LeadCount возвращается как `NULL` (`AND FALSE` в WHERE → COUNT=0 → NULLIF=NULL), Python затем его заполняет.

### SabyBank / стабы (IsStubMode="1")

`ВидЦеныДокумент` для SabyBank содержит записи для **всех** лидов — каждый лид создаёт корешок через `CreateStub` (задача 06152561: CreateLead автоматически вызывает CreateStub). Источник ВЦД корректен.

**Решение:** считать по `ДатаВремя` (дата создания корешка в ВЦД) вместо `EffectiveDate` (дата закрытия RKO). Фильтр `Бонусы > 0` убран, фильтр `ТипСвязи IS NOT NULL` остаётся (идентификатор корешка).

```sql
AND ptd."ТипСвязи" IS NOT NULL
AND ptd."ДатаВремя" BETWEEN res.period[1]::date
AND (res.period[2]::date + '1 day'::interval - '1 msec'::INTERVAL)
```

---

## Ключевое разграничение

| Режим | Источник LeadCount | Дата привязки |
|---|---|---|
| Стандартная программа | `get_sales_sources_stats` (CRM/маркетинг) | Дата создания заявки в CRM |
| SabyBank (стабы) | `ВидЦеныДокумент` (`ТипСвязи IS NOT NULL`) | `ДатаВремя` корешка |

`Price` во всех случаях остаётся в ВЦД по `EffectiveDate` — это правильно, т.к. вознаграждение относится к дате закрытия.

---

## Получение AdObject IDs

Для вызова `get_sales_sources_stats` нужны `AdObject` — идентификаторы источников в маркетинге:

- **Владелец** (без `PartnerId`): новый SQL `_SQL_GET_ALL_PROGRAM_SOURCE_IDS` — все уникальные AdObject всех реферальных кодов программы
- **Партнёр** (с `PartnerId`): существующий `SQL_GET_REFERRAL_CODE_SOURCE_IDS` — AdObject реферального кода партнёра

---

## Изменённые файлы

**БЛ:**
- `get_lead_period_list.py` — рефакторинг SQL LeadCount + новые функции `_fill_lead_count_from_marketing`, `_get_source_ids`; импорт `get_sales_sources_stats`, `SQL_GET_REFERRAL_CODE_SOURCE_IDS`

**Тесты:**
- Все тесты стандартных программ: мок `get_sales_sources_stats` (путь `priceformationonline.referralprogram.referralprogram.get_lead_period_list.get_sales_sources_stats`)
- `test_get_periods_with_different_creation_and_closing_dates`: LeadCount=1 в январе (дата создания), 0 в феврале (вместо прежнего 0/1 по EffectiveDate)
- `test_get_periods_sabybank`: May LeadCount=1 (ДатаВремя=May 1), June LeadCount=None (вместо 1 по EffectiveDate)

---

## Generalizable insight

> [!key-insight] `ВидЦеныДокумент` — таблица **вознаграждений**, а не лидов. Для стандартных реферальных программ записи в ВЦД создаются только через `SetLeadPrice` (UPDATE). Считать «все лиды» из ВЦД для стандартных программ — структурная ошибка. Правильный источник количества лидов для стандартных программ — сервис маркетинга (`SalesSources.ReadStat` / `get_sales_sources_stats`).

---

## Требования из задачи

- Показывать количество **созданных, не удалённых** заявок (не только с вознаграждением)
- Скрывать колонку вознаграждений если данных нет (`HasPrices` в метаданных — уже было)
- Не отображать нули (`NULLIF(count, 0)` — уже было)
- Добавить в старый реестр тоже
