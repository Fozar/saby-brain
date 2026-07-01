---
type: synthesis
title: "DiscountRegistry-Revive-Performance"
created: 2026-06-16
updated: 2026-07-01
tags:
  - price-formation
  - performance
  - loyalty
  - iterative-navigation
  - retail-offline
  - sql-indexes
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
- `UnfilteredRecords` **намеренно не** фильтрует `ТипСвязи IS NULL` / `Sale|Документ NOT NULL` заранее (это нужно EMA — см. развилку ниже).

> [!warning] Корректировка 2026-07-01: индексы по `EffectiveDate` ЕСТЬ
> Прежний тезис «нет индекса по `EffectiveDate` для общих строк продаж» **неверен** (проверено на стенде `test-osr-db61…/load-ext-3`, схема `_01216129`, 17.2М строк). Индексы объявлены в **`PricingRetailOnline.dicx`** (расширение той же таблицы `ВидЦеныДокумент`), присутствуют в бою (26.3234, 26.4100):
> - `EffectiveDateSale (ВидЦены, EffectiveDate, @ВидЦеныДокумент) WHERE ВидЦены NOT NULL AND EffectiveDate NOT NULL AND Sale NOT NULL`
> - `EffectiveDateDocument (…) WHERE … Документ NOT NULL`
> - `EffectiveDate (EffectiveDate DESC) WHERE EffectiveDate NOT NULL`
>
> Не искать/дублировать индекс в `PriceFormation.Online.dicx` — он в соседнем модуле. Первую страницу основной итерации общий `EffectiveDate`-индекс, вероятно, тоже покрывает — перепроверить EXPLAIN на итоговом тексте запроса.

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

## Убраны «пустые» запросы (2026-07-01)

Вторая итерация той же задачи (совещание). Симптом: `Promotion.GetSaleList` продолжает возвращать `hasMore=true`, хотя продаж с акциями за период уже нет — клиент делает лишние round-trip'ы.

**Корень.** Итерация завершается только когда блок `UnfilteredRecords` не отсканировал **ни одной** строки `ВидЦеныДокумент`. Таблица плотно забита движениями всех типов, продажи с акциями разрежены ⇒ контрольная запись (`ControlRecord = MIN(EffectiveDate) FROM UnfilteredRecords ... WHERE DateWTZ IS NOT NULL`) эмитится на каждом блоке, `hasMore` держится `true` до начала таблицы. Тот же паттерн у bonus/promocode/referralbonus (вне scope).

**Решение — нижняя граница итерации.** CTE `SaleDateBound` в `promotion/get_sale_list.py`: точная `MIN(EffectiveDate)` по акциям реестра. Контрольная запись не эмитится при `ControlRecord.DateWTZ ≤ MinSaleDate` (блок дошёл до последней продажи — ниже данных нет). Т.к. база (`_prepare_next_position_iterative`) падает, если последняя строка не контрольная, оверрайд в `PromotionSaleListWithCursor` трактует **отсутствие** контрольной записи как терминальную страницу → `nextPosition=None` (`hasMore=false`), продажи блока отдаются. Базовый `ListWithCursor` не тронут.

**Как считать границу — критично для перфа** (EXPLAIN на стенде, 297 акций):

| Стратегия | «Все» (297) | узкая акция |
|---|---|---|
| **LATERAL per-id `MIN(EffectiveDate)` (выбрано)** | **8.5 мс** | **0.11 мс** |
| `ВидЦены = ANY(array)` | 1.8 мс | **47 824 мс** ⚠️ |
| «tight» (+`Активирована`/`ТипСвязи`/`Сумма`) | 27 336 мс | **9 095 мс** ⚠️ |
| прокси `MIN(ДатаВремя)` через индекс `ВидЦены` | 58.7 мс | — |

Два жёстких правила (зашиты в комментарии кода):
1. **Только `LATERAL` по каждому id** — даёт Index-Only-Scan по `EffectiveDateSale`/`EffectiveDateDocument`. `= ANY(array)` планировщик уводит в backward-scan общего `EffectiveDate`-индекса (снял 10.8М строк фильтром на узкой акции → 47.8 с).
2. **Без tight-фильтров** показа (`Активирована`/`ТипСвязи`/`Сумма`) — их колонок нет в индексе, скан всех строк акции (9 с). Loose-граница (только `Sale/Документ NOT NULL`) безопасна: неактивированные строки — свежие, не старые, поэтому loose ≈ tight по эффекту.

Тесты: `tests/.../promotion/get_sale_list.py` — `test_no_sales_terminates_despite_noise`, `test_iteration_stops_at_earliest_sale`; класс `GetSaleList` 11/11 OK (проект `online`).

## Дальше
Перезамерить сценарий на перф-стенде (перфалайз task 207239) и `EXPLAIN (ANALYZE, BUFFERS)` на итоговом тексте запроса с `SaleDateBound`. Если оживление всё ещё >2300 мс — передать фронту с разбивкой времени (BL ~15%, остальное рендер/итеративная отрисовка).
