---
type: meta
title: "Hot Cache"
updated: 2026-06-15
tags:
  - meta
  - hot-cache
status: evergreen
related:
  - "[[index]]"
  - "[[log]]"
  - "[[overview]]"
---

# Recent Context

## 2026-06-17 — LoyaltyReferral: выделение рефералки в отдельный модуль (задача 05256826)

Старт выноса реферальной системы из `PriceFormation.Online` в новый BL-модуль `LoyaltyReferral`. План Андрея (4 этапа, добросками; прецедент — KZ Кузакова): 1) модуль+компонент, 2) добавить в online-сборки, 3) зависимости («подумать», риск цикла), 4) перенос кода (сделки→бонусы). Сделано: модуль с `component_uuid` как у PF.Online + зависимость только на `PriceFormation.Online` (mirror KZ); добавлен в тестовые сборки `tests_new/online` и `online_with_discount_core`; echo-метод `LoyaltyReferral.Echo` + тест (зелёный после `test_manager.py -project online --build true`). Ключевое: `Socnet` — локальный класс, не модуль; внешние Python-пакеты `rightcheck`→Rights-Py, `user_service_cloud`→UserServiceCloud-Py, `multitenancy`→Multitenancy-Py (приходят транзитивно). Боевая регистрация — `online/inside` `online32.s3srv:454` (ещё не сделано). Тесты `tests_new` — git-симлинки на `tests/`. ⚠️ `kaizen_zone` модуля отличается от канона; не пайпить билд через `tail` (маскирует exit-код). Подробности: [[LoyaltyReferral-Module-Extraction]].

## 2026-06-16 — ReferralProgram SetStubPrice/SetLeadPrice: рекорд-результат (задача 04307161, saby bank)

Оба метода теперь возвращают `sbis.Record({'AccruedCount', 'NotAccruedCount'})` вместо `int` — для UI-уведомления «скольким начислено / скольким нет», по образцу `DiscountCard.BatchDeleteOrLock`. `accrued = RETURNING.Size()`, `not_accrued = len(marked) − accrued` (не начислено = неуспешный `ТипСвязи` для корешков / не та программа для сделок). Правки: `set_stub_price.py`, `set_lead_price.py` (+хелпер `_build_result`), `ReferralProgram.orx` (`returns SCALAR→RECORD`, два `<return>`), тесты (9/9 OK). UI-уведомление — отдельная задача. Подробности: [[ReferralProgram-SetPrice-Record-Return]].

## 2026-06-16 — Оживление реестра «Скидки» offline (задача 12221993)

Оптимизация оживления реестра «Скидки» Retail offline (2567→<2300 мс). Ключевой вывод: `Promotion.GetSaleList` **проксируется в облако**, BL ≈ 300–400 мс (~15%) из 2567 мс, ~3 итеративных round-trip; остальное — клиентский рендер. Первая страница идёт Seq Scan по `ВидЦеныДокумент` (нет индекса по `EffectiveDate` для общих продаж). Push-down фильтров / партиал-индекс **конфликтует с EMA** (он опирается на нефильтрованный `ScannedCount`). Выбран вариант C: `UNION → UNION ALL` (output-neutral) + тюнинг EMA (`_MAX_BLOCK 20k→30k`, `_K=3.0`), остаток — фронту. Подробности: [[DiscountRegistry-Revive-Performance]].

## 2026-06-16 — ReferralProgram GetLeadPeriodList: LeadCount из маркетинга (задача №04307081)

Баг: `LeadCount` считал только лиды с вознаграждением (`Бонусы > 0` в ВЦД). Ключевой инсайт: `ВидЦеныДокумент` — таблица **вознаграждений**, не лидов; для стандартных программ записи создаются только через `SetLeadPrice` (UPDATE). Решение: стандартные программы → `get_sales_sources_stats('Лид', source_ids, ...)` из CRM/маркетинга per-period в Python; SabyBank/стабы → ВЦД по `ДатаВремя` (дата создания корешка), без `Бонусы > 0`. Подробности: [[ReferralProgram-GetLeadPeriodList-LeadCount-Source]].

## 2026-06-16 — ReferralProgram Data Model (задача 06096778)

Модель данных реферальных программ: `ВидЦены` (программа) → `Раздел` (папка БизнесГруппы) → `AdObject` (источники в маркетинге). `access_data_guid` — единственная жёсткая ссылка на БизнесГруппу в источнике (в `ВидЦены` связь идёт через иерархию Разделов). `utm_rfcid = account_number + @AdObject` — при миграции @AdObject не меняется, ссылка живёт. Оценка задач Тимошенко А.: 0.5–1 день (не 3.5 дня). Подробности: [[ReferralProgram-Data-Model]].

## 2026-06-15 — Bugfix entity_sp deletion (задача 06108231)

Откат коммита `1fb3ffbd1c` (удаление фичи `entity_sp`) на `26.4100/bugfix/06108231_entity_sp_revert`. Принцип: фича удаляется только после 100% раскатки на всех стендах. Подробности: [[entity-sp-deletion-order-2026-06-15]].

## 2026-06-15 — CreateLead auto-creates stub (задача 06152561)

`ReferralProgram.CreateLead` теперь автоматически вызывает `CreateStub` после создания CRM-сделки. Реализовано в `create_lead.py`: `_get_stub_status_from_events` (маппинг TransitionResults → LinkType) + `_create_stub_for_lead` (SQL UUID + вызов CreateStub). Архитектура: GetLead + CreateStub критичные (без try/except), история некритичная. 7/7 тестов зелёные. Подробности: [[ReferralProgram-Stub-Implementation]].

## 2026-06-15 — Ингест PDF-батча: Рефералка в заявках на РКО

8 PDF-файлов из `raw/Рефералка в Заявках в банк на РКО по API/`.

**Новые страницы:**
- [[SabyBank-RKO-TZ]] — полное ТЗ (22 стр. PDF): API, выборки БД, индексы, UI-декомпозиция, источники данных
- [[SabyBank-RKO-WorkPlan]] — план работ 166,5 дня: этапы, сроки, исполнители по каждой задаче

**Обновлено [[SabyBank-RKO-Referral]]:** управление проектом (заказчик Уваров С.В., дедлайн 26.10.26, опыт. эксплуатация 18.09.26, премии 545к), фича `referral_bank`, счётчики активности, выборки БД, план тестирования.

**Ключевые новые факты:**
- Дедлайн полной сдачи заказчику: **26.10.2026**
- Новый индекс БД: `ВидЦеныДокумент (ВидЦены + ДатаВремя + ТипСвязи)` (фильтр по статусу)
- Фича-флаг: `referral_bank` (ответственный Михель В.)
- Source: [[sabybank-rko-referral-pdf-2026-06-15]]

## 2026-06-15 — Линт + калибровка тайлинга

- Создан `scripts/detect-transport.py` (Python-замена для отсутствовавшего .sh)
- Исправлена коллизия `c-000105`: Wasaby-BL-Async-Sync-Cloud-Calls удалён, уникальный контент влит в [[Wasaby-BL-AsyncInvoke]]
- Добавлены перекрёстные ссылки: DWC, LRS, Profiles, Sync-Broker (4 пары)
- 14 orphan-страниц добавлены в index.md; 3 мёртвые ссылки исправлены
- **Слияние**: [[Async-Calls-Bus]] → [[Wasaby-MQ]] (контент поглощён; входящие ссылки переключены; исходный файл ожидает удаления — нужно разрешение)
- Тайлинг откалиброван: 114 пар размечено, истинных дублей 0; пороги 0.90/0.80 → **0.95/0.92**; Error: 114 → 6, Review: 5117 → 35

## 2026-06-14 — wasaby.Backend batch ЗАВЕРШЁН (c-000105..c-000142, 38 страниц)

| Категория | Страницы |
|---|---|
| Стандарты | [[Wasaby-Dev-Standards]], [[Wasaby-SQL-Standard]], [[Wasaby-Python-Standard]], [[Wasaby-Cpp-String-Standard]] |
| Фреймворк | [[Wasaby-Service-Framework]], [[Wasaby-BL-Calls]], [[Wasaby-BL-Objects]], [[Wasaby-Service-Node-Architecture]] |
| Тестирование/Отладка | [[Wasaby-Unit-Testing]], [[Wasaby-Memray]], [[Wasaby-Perforator]], [[Wasaby-Python-Debug]] |
| БД/Хранилища | [[Wasaby-SQL-DBA]], [[Wasaby-ClickHouse]], [[Wasaby-FTS]], [[Wasaby-File-Transfer]] |
| Async/Очереди | [[Wasaby-MQ]], [[Wasaby-Request-Broker]], [[Wasaby-Scheduler]], [[Wasaby-DWC]], [[Wasaby-Long-Running-Operations]], [[Wasaby-Task-Queue]], [[Wasaby-Mass-Mailings]] |
| Middleware | [[Wasaby-Report-Prefetch]], [[Wasaby-HTML-Converter]], [[Wasaby-Informers]], [[Wasaby-Multimedia-Loader]], [[Wasaby-PDF-Transformer]], [[Wasaby-Image-Service]] |
| Инфра/Прочее | [[Wasaby-i18n]], [[Wasaby-Third-Party-Libraries]], [[Wasaby-Parameters-Service]], [[Wasaby-Distributed-Locks]], [[Wasaby-History-Service]], [[Wasaby-Profiles-Service]] |
| Клиентские события | [[Wasaby-STOMP]], [[Wasaby-Sync-Broker]] |
| C++ инфра | [[Wasaby-Conan]] |

**Важные заметки:**
- `PyCharm` для отладки: максимальная версия **2022.3.3**
- `Prefetch.List`: **PrefetchPreSort обязателен** для иерархических отчётов
- `distributed-locks`: `ResourceId` не включает account/user — добавлять самому
- `delayedPrint=true` в HTML-конвертере: JS должен вызывать `window.tensor.waitPrint()` каждые ≤5с

История предыдущих сессий (июнь 2026) — [[log]].

---

## Price Formation Domain

SBIS/Saby loyalty + price formation, ветка `rc-26.3211`.
- Wasaby: 3-level (s3cld/s3srv/s3mod), JSON-RPC, declarative resources
- DB: `ВидЦеныДокумент` (события лояльности), `Карта` (ДК/промокод)
- DWC: `workflow2`. Python: 120 chars, CamelCase ok, no wildcard imports

## Active Threads

- **Loyalty Desktop Broker Migration**: [[Loyalty-Desktop-Broker-Migration]] — feature flag `lty_broker_card_type`, ~60д
- **SabyBank RKO Referral**: [[SabyBank-RKO-Referral]] — релиз 18.08.2026

---

Navigation: [[index]] | [[log]] | [[overview]]
