---
type: synthesis
title: "CardEmission FullReSync PK Conflict Fix"
created: 2026-06-10
updated: 2026-06-10
tags:
  - loyalty
  - sync
  - offline
  - discountcard
  - bugfix
status: fixed
related:
  - "[[Sync-Broker]]"
  - "[[Loyalty-Desktop-Broker-Migration]]"
  - "[[BrokerLoyalty-BonusSettings-Race-Fix]]"
question: "Почему не работает принудительная полная синхронизация выпусков карт после того как часть выпусков уже синхронизирована?"
answer_quality: solid
---

# CardEmission FullReSync PK Conflict Fix

**Task:** https://online.sbis.ru/opendoc.html?guid=019ea66a-130a-77e2-b5db-8ac66d300b57&client=3 (№06084819, «Ошибка на стенде», фича `lty_broker_sync`)

Автор файла и диагноза — Михайленко Е.А.; реализация передана Тимошенко А. (просьба Егора).

---

## Bug

Принудительная полная пересинхронизация выпусков карт (`PFSync.CardEmissionReSync`) **падает, если часть выпусков уже была синхронизирована ранее**. Полная пересинхронизация фактически отрабатывала только как fallback — в `except`-ветке `_sync_card_emissions()` при падении регулярной синхронизации.

---

## Root Cause

`PriceFormation.Offline/priceformationoffline/discountcard/pfsync/card_emission_sync.py`, запрос `_sql_upsert_card_emissions` (CTE-upsert в таблицу `ВидКарты`).

Upsert состоит из двух CTE:

- **`Updated`**: `UPDATE ... WHERE "@ВидКарты" = Data."@ВидКарты" AND (<хоть одно поле IS DISTINCT>)`. Существующая запись попадает в `Updated`, **только если хоть что-то изменилось**.
- **`Inserted`**: `INSERT ... WHERE Updated."@ВидКарты" IS NULL` — «вставить всё, чего нет в `Updated`».

При полной пересинхронизации (`ResetSync` → повторная первичная синхронизация) через метод снова проходят **все** выпуски, включая уже существующие и **неизменённые**. Для такой записи:

1. В `Updated` она не попадает (нет ни одного `IS DISTINCT` поля).
2. Значит `Updated."@ВидКарты" IS NULL` → она уходит в `Inserted`.
3. `INSERT` существующего `@ВидКарты` → **нарушение PK / duplicate key** → весь запрос падает.

Первая синхронизация «с нуля» работает (записей ещё нет). Падение начинается именно «после того как какие-то выпуски уже синхронизированы» — что и описано в задаче.

---

## Fix

В CTE `Inserted` добавить отсев уже существующих записей:

```sql
WHERE Updated."@ВидКарты" IS NULL
    AND NOT EXISTS (SELECT NULL FROM "ВидКарты" WHERE "@ВидКарты" = Data."@ВидКарты")
```

Теперь в `Inserted` попадают только действительно новые `@ВидКарты`. Существующая-но-неизменённая запись больше не уходит в `INSERT` (и в `UPDATE` тоже не нужна — она уже актуальна).

**Корректность семантики CTE Postgres:** все sub-statement'ы внутри одного `WITH` видят единый снимок БД до начала запроса. `NOT EXISTS (... ВидКарты ...)` видит таблицу до `UPDATE`, поэтому: обновлённая запись существовала до запроса → `NOT EXISTS = false` → не вставляется (правильно); новая запись → `NOT EXISTS = true` и не в `Updated` → вставляется (правильно).

---

## Generalizable insight

> [!key-insight] Паттерн «UPDATE-only-if-DISTINCT + INSERT-where-not-updated» дырявый при повторном прогоне идентичных данных. Если `UPDATE` отбирает только реально изменившиеся строки, то условие вставки `Updated IS NULL` ложно-положительно ловит **существующие неизменённые** строки → конфликт PK. Условие вставки должно проверять отсутствие строки в целевой таблице (`NOT EXISTS`), а не отсутствие в наборе `Updated`.

Это особенно важно для идемпотентных полных пересинхронизаций (`ResetSync` в [[Sync-Broker]]), где через upsert регулярно проходят неизменённые данные.

---

## Tests

Регрессионный тест: `tests/tests_priceformationoffline/discountcard/pfsync/card_emission_sync.py::test_resync_unchanged_record` — повторный `AddObjects` неизменённой существующей записи. До фикса падает на duplicate key, после — no-op.

Замечание: существующий `test_1` баг не ловил, т.к. в кейсе «Обновляет если добавляемая запись уже есть» значение **меняется** (попадает в `Updated`).

Автотесты офлайна (`tests_priceformationoffline` = проект `desktop`) локально не прогнать — в `test_build` собран только `online` (`Ran 0 tests`). Михайленко также просила ручную проверку через консоль десктопа: `PFSync.CardEmissionReSync`, первый и последующие вызовы.

---

## Changed files

- `www/service/Модули/PriceFormation.Offline/priceformationoffline/discountcard/pfsync/card_emission_sync.py` — условие `NOT EXISTS` в CTE `Inserted`.
- `tests/tests_priceformationoffline/discountcard/pfsync/card_emission_sync.py` — регрессионный тест.

Ветка: `26.4100/bugfix/aatimoshenko/06087022`. Просьба смержить также в `3218` (offline).