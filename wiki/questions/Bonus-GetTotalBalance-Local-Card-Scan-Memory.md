---
type: synthesis
title: "Bonus.GetTotalBalance — локальный скан «Карта» как источник 1 ГБ/итерация"
address: c-000207
created: 2026-07-23
updated: 2026-07-23
tags:
  - loyalty
  - bonuses
  - franchise
  - performance
  - sql
  - price-formation
  - sbis
status: developing
question: "Почему LoyaltyWidgets.GetBonusesNew съедает ~1 ГБ памяти за итерацию на test-inside после июньской оптимизации GetTotalBalance?"
answer_quality: solid
related:
  - "[[Bonus-GetTotalBalance]]"
  - "[[Bonus-GetTotalBalance-Franchise-Performance]]"
  - "[[Bonus-Programs-Architecture]]"
  - "[[Franchise-Loyalty-Architecture]]"
  - "[[DiscountCard-Service-API]]"
  - "[[DiscountRegistry-Revive-Performance]]"
---

# Bonus.GetTotalBalance — локальный скан «Карта» как источник 1 ГБ/итерация

Задача **07208958** (ошибка на стенде, от 2026-07-20), стенд `test-inside.tensor.ru`,
БД `test-master-db1`, приложение `online-83bbmj4`.

`LoyaltyWidgets.GetBonusesNew` потребляет **~1 ГБ памяти за итерацию** (≈1.2 ТБ/сутки по шаблону,
1.3 ТБ памяти / 18 ГБ диска по методу). Постнов С.А. при переводе с предыдущего этапа указал
конкретного виновника: «Тяжелый запрос `Bonus.GetTotalBalance/1`».

## Это отложенный хвост, а не новая проблема

Прямое продолжение [[Bonus-GetTotalBalance-Franchise-Performance]] (задача 05292113, июнь).
Тогда у того же метода было **две** статьи расходов:

| Ветка | Стоимость на тот момент | Судьба |
|---|---|---|
| СДК: поимённый `Card.GetBonusBalanceByCards` (80k UUID туда, 79 943 строки обратно) | ~3.2 с | **починено** коммитом `1be452e6e2` (23.06.2026) |
| Локальный SQL `_SQL_GET_BALANCE_COMPONENTS` — скан `Карта` | ~943 мс | **осознанно отложено** |

Вики того периода прямо фиксировала отложенность: скан `Карта` — «вторичный источник…
имеет смысл только вместе с 1a/1b». Коммит `1be452e6e2` реализовал вариант, близкий к 1a/1b:
заменил `_get_balance_by_cards()` на скалярный `_get_personal_cards_balance_sum()` →
`Card.GetPersonalCardBonusBalanceSum(ClientID)`.

> [!key-insight] Механика регрессии восприятия
> Локальный скан не стал медленнее — он стал **доминирующим**. Пока СДК-ветка стоила 3.2 с,
> скан `Карта` терялся на её фоне. После починки СДК-ветки он остался единственным крупным
> потребителем и всплыл как отдельный баг. Это типовой паттерн: оптимизация верхнего слоя
> делает видимым следующий.

## Куда уходит память

`_SQL_GET_BALANCE_COMPONENTS` (`get_total_balance.py:131`) суммирует
`Атрибуты->'Bonus'->>'AvailableBonusBalance'` по **всем** бонусным картам аккаунта.
На проблемном аккаунте — 25 454 персональных счёта и 433 эмитированные карты.

Сопоставление узлов EXPLAIN из задачи с CTE запроса:

| Узел плана | CTE | Buffers | ≈ Память |
|---|---|---:|---:|
| Index Scan `iЧастноеЛицо-Лицо`, **loops=23 985** | `personal_accounts` → `LEFT JOIN "ЧастноеЛицо"` | 95 885 | **~750 МБ** |
| Index Scan `iКарта-Эмиссия`, RRbF **60K** (rows=433) | `cards_only` → `JOIN "ВидКарты"` | 27 063 | **~210 МБ** |
| Bitmap Index Scan `iКарта-UniquePersonalCard` | `personal_accounts` отбор (25 454 строки) | 148 | незначимо |

Итого ≈ 960 МБ — это и есть заявленный «1 ГБ за итерацию». Доминирует **построчный
nested-loop джойн к `ЧастноеЛицо`** (по 4 буфера на итерацию × 24k итераций).

## Ключевой вывод: дорогие джойны нужны только франшизе

Оба дорогих джойна существуют исключительно ради вычисления колонки `IsFranchise`
(разбор критериев — в [[Bonus-GetTotalBalance]]):

- `personal_accounts`: `P."ИдентификаторФизЛица" IS NOT NULL` — требует `LEFT JOIN "ЧастноеЛицо"`;
- `cards_only`: `FranchiseRole` у эмиссии или родительской папки — требует `LEFT JOIN "ВидКарты" EP`.

А в финальном `SELECT` колонка `IsFranchise` влияет на результат **только при `has_franchise = True`**:

```sql
SUM("AvailableBonusBalance") FILTER (WHERE NOT !has_franchise OR NOT "IsFranchise")
ARRAY_AGG(DISTINCT "CardTypeUUID") FILTER (WHERE !has_franchise AND "IsFranchise" AND ...)
```

При `has_franchise = False`:
- первый FILTER → `NOT False OR ...` → **всегда TRUE**, `IsFranchise` не влияет на сумму;
- второй FILTER → `False AND ...` → **всегда пусто**, `FranchiseCardTypeUUIDList` не заполняется.

> [!key-insight] Для не-франшизного аккаунта оба джойна — чистые накладные расходы
> Их результат вычисляется, оплачивается ~960 МБ буферов и затем полностью игнорируется
> финальным агрегатом.

## Предложенный фикс (не реализован, ждёт подтверждения)

Локальная правка **только в шаблоне** `_SQL_GET_BALANCE_COMPONENTS`, без изменения схемы,
без индексов, без СДК:

- `{% iffalse has_franchise %}` → `FALSE AS "IsFranchise"`, без `LEFT JOIN "ЧастноеЛицо"`
  в `personal_accounts` и без `EP`/`FranchiseRole` в `cards_only`;
- `{% iftrue has_franchise %}` → текущий SQL без изменений.

Преобразование эквивалентное (доказательство — разбор FILTER выше), результат для не-франшизного
аккаунта побитово тот же, память падает примерно вчетверо. Для франшизы — no-op.
Шаблонизатор такие условия по bool-параметру поддерживает (тот же приём — `{% iftrue query_by_month %}`
в соседнем `balance_tab.py`).

> [!warning] Чего фикс не закрывает
> Если проблемный аккаунт **франшизный**, джойны там реально нужны и локально не убираются.
> Лечение — перенос агрегации локальных персональных счетов в СДК (вариант **1b** из
> [[Bonus-GetTotalBalance-Franchise-Performance]]): зона `discount-cards`, согласование с Кузаковым Ю.
> Второй, независимый вектор из той же вики — выражённый индекс под
> `(Атрибуты->>'IsBonus')::boolean`, который убрал бы «Rows Removed by Filter: 60K» в `cards_only`
> (изменение `.dicx` + пересборка, таблица `Карта` — зона `dccommon`).

## Открытый вопрос

> [!open-question] Франшизный ли аккаунт на `test-inside`?
> Это развилка, определяющая, закрывает ли локальный фикс именно этот тикет или только общий случай.
> На момент записи **не выяснено** — вопрос задан, ответ не получен.
> Косвенный признак из EXPLAIN: 25 454 персональных счёта против всего 433 эмитированных карт —
> перекос в сторону персональных счетов, как и на франшизном аккаунте из 05292113 (~80k счетов).
> Сам EXPLAIN тип аккаунта не выдаёт: джойны в текущем коде безусловны и выполняются при любом
> `has_franchise`.

## Ограничение инструментов

Серверные логи этого стенда штатным путём недоступны: `cloud_get_logs` принимает только
`online / test-online / pre-test-online / fix-online / dev-online`, стенда `test-inside` в списке нет.
Сообщений и вложений у задачи 07208958 нет, поэтому EXPLAIN из описания задачи — весь доступный
фактический материал. Ссылка на архив: `explain.sbis.ru/archive/explain/019f7e29-19e1-7000-8003-018ba0e06cc8:2:2026-07-20`.