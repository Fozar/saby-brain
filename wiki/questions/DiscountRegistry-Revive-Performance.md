---
type: synthesis
title: "DiscountRegistry-Revive-Performance"
created: 2026-06-16
updated: 2026-06-16
tags:
  - price-formation
  - performance
  - loyalty
  - iterative-navigation
  - retail-offline
status: developing
related:
  - "[[Bonus-GetSaleList-Duplicate-W-Records-Iterative-Block-Bug]]"
  - "[[ReferralBonus-GetSaleList-Iterative-Ordering-Bug]]"
  - "[[Feature-Flag-Removal-LOYALTY-IT-NAV]]"
  - "[[Акции-Architecture]]"
question: "Как оптимизировать оживление реестра «Скидки» в Retail offline с 2567 мс до <2300 мс?"
answer_quality: solid
---

# Оживление реестра «Скидки» (Retail offline) — где живёт время

Задача №12221993 (`b02e5df7-fd9c-48b3-a2f1-e4fc41f3cd5f`, «Ошибка на стенде»): сценарий «аккордеон → реестр Скидки → Касса → повторно Скидки» не укладывается в бюджет оживления. ОР ≤2300 мс, ФР 2567 мс (замер 11.06.26). Динамический размер итеративного блока (EMA, коммит `c6f4afe94a`) уже дал 2790→2567, но цели не достиг.

## Главный вывод: BL — это ~15% времени оживления

Анализ оффлайн-логов (`26_2200_скидки.7z`, invoke/events) показывает:

- В Retail offline `Promotion.GetSaleList` **проксируется в облако** (`[rpc call] url:https://retail.saby.ru/service/`), а не выполняется локально. Каждый rpc ~35–130 мс (`[exec_period] 80`).
- На одно открытие реестра клиент делает **~3 итеративных round-trip**.
- `Promotion.GetSaleTotals` ~16–21 мс (кэш итогов уже внедрён), `Promotion.GetList` ~70 мс.
- Итого BL даёт **~300–400 мс из 2567 мс**. Остальное — клиентский рендер и итеративная отрисовка реестра.

Это согласуется с комментарием Ютман Э. (22.04): итеративная загрузка реестра медленная при разреженных продажах с акциями (продажи с акциями редки среди движений `ВидЦеныДокумент`), и «ничего быстро мы с этим сделать не можем».

## Корневая BL-неэффективность (dataset-sensitive)

В `promotion/get_sale_list.py`, CTE `UnfilteredRecords`:
- Первая страница идёт с курсором `9999-01-01` ⇒ предикат пропускает всё.
- **Нет индекса по `EffectiveDate`** для общих строк продаж в `ВидЦеныДокумент`. Существуют только частичные: `PromoCodeEffectiveDate` (PromoCode IS NOT NULL), `CardOnSaleEffectiveDate` (Карта IS NOT NULL), `BonusesEffectiveDate` (ведущий столбец ВидЦены). Общий реестр скидок ни один не покрывает.
- `UnfilteredRecords` **намеренно не** фильтрует `ТипСвязи IS NULL` / `Sale|Документ NOT NULL` заранее.

⇒ блок почти наверняка выбирается через **Seq Scan + Top-N sort по всей таблице**. На крупном перф-стенде это может быть реальным боттлнеком, поэтому списывать всё на фронт нельзя без проверки.

## Архитектурная развилка: push-down/индекс ПРОТИВ EMA

Push-down фильтров `ТипСвязи IS NULL AND (Sale|Документ NOT NULL)` в `UnfilteredRecords` **конфликтует с уже внедрённым EMA**. EMA опирается на сигнал разреженности `ScannedCount` (сырьё до фильтра) / `RawResultCount` (после фильтра); если отфильтровать заранее, коэффициент схлопывается в ~1 и EMA теряет смысл. То есть:

- **Вариант A (индексный путь):** партиал-индекс `(EffectiveDate DESC)` по релевантным строкам + push-down фильтров + убрать EMA. Первая страница → index range-scan ровно page-size строк. Наибольший выигрыш, но нужен **аппрув DBA** на индекс горячей `ВидЦеныДокумент` и откат EMA-механики.
- **Вариант B:** оставить EMA, добавить **полный** (не партиал) индекс по `EffectiveDate` — толще, DBA согласует менее охотно, меньше выигрыш.
- **Вариант C (выбран):** не трогать схему и EMA-архитектуру; только запросные чистки + тюнинг границ EMA; остаток передать фронту.

## Реализовано (Вариант C)

- `get_sale_list.py`: `UNION → UNION ALL` ×2 — в `CombinedResult` (розница: SaleId IS NOT NULL/DocumentId IS NULL; склад: наоборот — непересекаемы) и во внешнем объединении с контрольной записью (`_IsControlRecord` TRUE vs FALSE). Output-neutral, убирает лишние dedup-сортировки.
- Тюнинг EMA для разреженного реестра: `_MAX_BLOCK 20k→30k`, добавлен `_K=3.0` (плечо запаса `target = limit * ratio_ema * _K`). В `IterativeBlockSizeEmaMixin` (`loyaltyprogram/helpers.py`) `k` проброшен как `self._K` с дефолтом 2.5, поэтому поведение `Bonus`/`PromoCode`/`ReferralBonus` GetSaleList не меняется. Значения требуют калибровки по замерам на стенде.
- Тесты `tests/.../promotion/get_sale_list.py` — 30 OK, 2 skip.

**Замечание (латентный баг, не правился):** в `get_sale_totals.py` объединения `SalesData`/`CombinedData`/агрегатов используют `UNION` (дедуп). При совпадении агрегатных строк Warehouse и Retail это даёт недоучёт итогов — `UNION ALL` был бы и быстрее, и корректнее, но требует тестов до/после.

## Дальше
Перезамерить сценарий на перф-стенде (перфалайз task 207239) и `EXPLAIN (ANALYZE, BUFFERS)`. Если оживление всё ещё >2300 мс — передать фронту с разбивкой времени (BL ~15%, остальное рендер/итеративная отрисовка).
