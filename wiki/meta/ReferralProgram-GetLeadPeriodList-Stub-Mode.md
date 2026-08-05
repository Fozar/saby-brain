---
type: decision
address: c-000254
title: "GetLeadPeriodList — мастер-фильтр заявок на данных корешков под ref_deals_convert"
created: 2026-08-05
updated: 2026-08-05
decision_date: 2026-08-05
status: active
tags:
  - price-formation
  - referral-program
  - feature-flag
  - referral-stub
related:
  - "[[ReferralProgram-GetLeadPeriodList-LeadCount-Source]]"
  - "[[ReferralProgram-RefDealsConvert-Feature]]"
  - "[[ReferralProgram-GetPartnerList-Stub-Stats]]"
  - "[[ReferralStub-Backfill-Service-Method]]"
  - "[[ReferralProgram-GetStubList-Filter-Redesign]]"
  - "[[SabyBank-RKO-Referral]]"
---

# GetLeadPeriodList — мастер-фильтр заявок на данных корешков под ref_deals_convert

Navigation: [[SabyBank-RKO-Referral]] | [[ReferralProgram-RefDealsConvert-Feature]]

**Задача:** https://online.sbis.ru/opendoc.html?guid=019fad04-5b70-7c78-8fe5-085d5dc60814&client=3 (№07294792, этап «Реестр "Заявки" на данных из "корешков"»)

Мастер-фильтр реестра «Заявки» — это `ReferralProgram.GetLeadPeriodList` (`www/service/Модули/LoyaltyReferral/loyaltyreferral/referralprogram/referralprogram/get_lead_period_list.py`): список периодов (месяцы + годовые итоги) с колонками `Price` (вознаграждение) и `LeadCount` (лиды).

---

## Что уже было и что реально требовалось

Постановка звучит как «считать количество заявок по корешкам под фичей», но `LeadCount` **уже** считался по корешкам безусловно — с задачи №07082151 (коммит `4f0b9b8983`, 17.06.2026) подзапрос отбирает `ТипСвязи IS NOT NULL` по `ДатаВремя` без оглядки на тип программы и фичу. Незакрытым оставался **`Price`**: признак `IsStubMode` зависел только от `program_type == SABYBANK`.

> [!key-insight] Почему `Price` ломался у обычных программ под фичей
> Миграция сделок на корешки (`create_stubs_for_existing_leads.py:411`) вставляет корешок **без** `"Документ"` — только `OperationId` + `ТипСвязи` + `Бонусы` + `EffectiveDate`. Ветка `IsStubMode = "0"` ищет либо `Документ IS NOT NULL` (сделка), либо `Документ IS NULL AND OperationId IS NULL` (посетитель) — корешок сделки не подходит **ни под одно** из условий и вознаграждение по нему просто не считается.

Старые записи по сделкам миграция не удаляет, поэтому задвоения при переключении режима нет: в режиме `"0"` считаются старые строки, в режиме `"1"` — корешки.

---

## Решение

`IsStubMode = (program_type == SABYBANK) OR check_feature(Feature.REF_DEALS_CONVERT)` — тот же гейт, что уже применён в [[ReferralProgram-GetPartnerList-Stub-Stats|GetPartnerList]] (`_resolve_stub_counters`) и `get_stats_helpers.use_stub_lead_counters`. Решение принимается один раз на вызов, в `_put_stub_mode_filters()`.

Дополнительно в фильтр кладётся отдельный признак **`IsSabyBank`**: у обычных программ даже в режиме корешков остаются вознаграждения **за посетителей** (`calculate_visitor_price`), которые корешками не оформляются. Без этого при включении фичи они молча исчезли бы из мастер-фильтра. В корешковой ветке SQL для `IsSabyBank = "0"` сохранена OR-ветка `Документ IS NULL AND OperationId IS NULL` по `ДатаВремя`.

`LeadCount` не трогали: без фичи поведение остаётся ровно прежним (осознанное требование постановщика — «без фичи должно остаться ровно то поведение, которое сейчас»).

### Источники по режимам

| Режим | Price | LeadCount |
|---|---|---|
| SabyBank (всегда) | корешки `ТипСвязи IS NOT NULL` по `EffectiveDate` | корешки по `ДатаВремя` |
| Обычная + фича | корешки по `EffectiveDate` **+ посетители** по `ДатаВремя` | корешки по `ДатаВремя` |
| Обычная без фичи | сделки `Документ IS NOT NULL` по `EffectiveDate` + посетители | корешки по `ДатаВремя` |

---

## Фронт уже был готов

`client/LoyaltyOnline/ReferralLeadNew/_dateFilter/View.tsx:79`: `showLeadCount = isSettlementsDeals || refDealsConvertFeatureIsOn` — колонка «Лиды» рисуется только у SabyBank (`ProgramType.SETTLEMENTS_DEALS`) либо под фичей. Мастер-фильтр запрашивает **до 40 периодов за страницу** (`DateFilter/PrefetchConfig.ts`, `limit: 40`).

> [!warning] Маркетинг здесь неприменим
> `SalesSources.ReadStat` (advert-service, `sales_sources/stats/read_stat.py`) агрегирует по `Place`/`AdObject` за **один** интервал и разбивки по месяцам не отдаёт. «Счётчики из маркетинга по каждому периоду» = до 40 межсервисных вызовов на загрузку фильтра — упирается в догму «в цикле по строкам не делать межсервисных вызовов» ([[ReferralProgram-GetLeadPeriodList-LeadCount-Source]]). Поэтому в этом методе, в отличие от `GetStats`/`GetPartnerList`, маркетинговой ветки нет вообще.

---

## Расхождение признаков корешка (зафиксировано тестом)

Методы опознают корешок по разным полям:

- `GetStubList` — `ptd."OperationId" IS NOT NULL` (`get_stub_list.py:143`)
- `GetLeadPeriodList.LeadCount` — `ptd."ТипСвязи" IS NOT NULL`

На боевых данных заполнены оба поля (`CreateStub`, миграция), поэтому цифры сходятся. Коррелирующий тест `test_lead_count_matches_stub_list` это фиксирует: `LeadCount` месяца == `GetStubList(Date=период).Size()`, `Price` месяца == сумме `Price` корешков из `GetStubList(Date=период, Status=[10,15,20])`. Соответствие дат неслучайно: `GetStubList` **без** `Status` фильтрует по дате создания (`ДатаВремя`) — как `LeadCount`, а **со** `Status` — по дате статуса (`EffectiveDate`) — как `Price` ([[ReferralProgram-GetStubList-Filter-Redesign]]).

---

## Порядок выката

Сначала домиграция корешков (`ReferralProgram.CreateStubsForExistingLeads`, см. [[ReferralStub-Backfill-Service-Method]]), затем включение фичи. Если включить фичу раньше — вознаграждения в мастер-фильтре обнулятся, потому что корешков ещё нет.

---

## Статус

Реализовано, 12/12 тестов `get_lead_period_list.py` зелёные (4 новых на режимы + коррелирующий с `GetStubList`), pylint 10.00/10. Не закоммичено, на стенде не проверялось.
