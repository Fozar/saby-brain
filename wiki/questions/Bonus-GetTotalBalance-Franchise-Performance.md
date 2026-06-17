---
type: synthesis
title: "Bonus.GetTotalBalance — деградация на франшизе (~80k карт)"
created: 2026-06-17
updated: 2026-06-17
tags:
  - loyalty
  - bonuses
  - franchise
  - performance
  - price-formation
  - discount-cards
  - sbis
status: developing
question: "Почему виджет «Бонусы» не строится на больших аккаунтах и метод Bonus.GetTotalBalance считает ~4.5 с?"
answer_quality: solid
related:
  - "[[Bonus-GetTotalBalance]]"
  - "[[Bonus-Programs-Architecture]]"
  - "[[Franchise-Loyalty-Architecture]]"
  - "[[DiscountCard-Service-API]]"
  - "[[DiscountRegistry-Revive-Performance]]"
---

# Bonus.GetTotalBalance — деградация на франшизе (~80k карт)

Задача 05292113 (ошибка на стенде), стенд `pre-test-online`, аккаунт 11479853
(«Красная ЛИСА У.М., ООО»). Виджет «Бонусы» не строится в серверном представлении:
`Bonus.GetTotalBalance/1` считает 4461 мс и не укладывается в бюджет серверного префетча.

## Куда уходит время

Разбивка по серверному логу `LoyaltyWidgets.GetBonusesNew` (ruuid
`019ed3ec-7626-776b-8cc8-1d5010424398`, 17.06.2026 07:52, ver 26.4100-651):

| Этап | ~Время | Что происходит |
|---|---:|---|
| Скан `Карта` (`_SQL_GET_BALANCE_COMPONENTS`) | ~943 мс | собирает список ~80k UUID персональных счетов |
| Подготовка аргумента (~80k UUID) к вызову СДК | ~963 мс | сборка и сериализация массива |
| RPC `Card.GetBonusBalanceByCards` | ~2216 мс | SQL 461 мс + передача 79 943 строк обратно |
| `ToDict` + суммирование 80k значений | ~326 мс | сведение в одно число |

EXPLAIN запроса в СДК (`Card.GetBonusBalanceByCards`):

```
Index Scan using "iCard-Identifier" on "Card"
  (cost=0.42..224006.86 rows=73192 width=48)
  (actual time=35.866..461.247 rows=79943 loops=1)
  Buffers: shared hit=320184
```

Запрос идёт по индексу `iCard-Identifier`, отрабатывает 461 мс, всё в кеше (`shared hit`).
Дорого не получение баланса, а то, что аккаунт франшизный с ~80 000 персональных счетов,
и эти 80k карт гоняются туда-обратно ради одной суммы.

## Корневая причина

`get_total_balance.py` → `_sum_cards_balance()` → `_get_balance_by_cards()` вызывает
`Card.GetBonusBalanceByCards`, который возвращает баланс **по каждой карте**
(`SELECT Identifier, BonusBalance ... WHERE Identifier = ANY($1)`), а вызывающий код сразу
сворачивает результат в `sum(...)`. На франшизе с десятками тысяч счетов всё растёт линейно
по числу карт на каждом шаге: скан `Карта` → массив аргументов → строки ответа → суммирование.

Рядом уже есть `Card.GetBonusBalanceByCardTypeList` — он считает `SUM(BonusBalance) ... GROUP BY`
на стороне СДК и возвращает агрегат, а не строки. Для персональных счетов (без типа карты)
такого агрегата нет — отсюда поимённый путь. См. устройство метода в [[Bonus-GetTotalBalance]].

## Решение (на согласование, без правок)

Перенести агрегацию в СДК, чтобы не передавать 80k UUID и не получать 80k строк.

- **1a — быстрый шаг.** Добавить в `discount-cards` скалярный метод
  `Card.GetBonusBalanceSumByCards(card_uuids) -> Decimal`
  (`SELECT SUM("BonusBalance") FROM "Card" WHERE "Identifier" = ANY($1)`). Убирает возврат
  80k строк и `ToDict`/`sum`; список UUID в аргументе пока остаётся.
- **1b — целевой вариант.** Считать франшизный баланс по бизнес-группе целиком на стороне СДК
  (в `Card`/`CardType` есть `FranchiseUUIDList`), напр.
  `Card.GetFranchiseBonusBalance(agent_group_id) -> Decimal`. Тогда уходит и скан `Карта`,
  и массив-аргумент, и массив-ответ — остаётся один скалярный запрос (~0.5 с по EXPLAIN).
- **Скан `Карта`** (~943 мс) — вторичный источник. Индекс под `(Атрибуты->>'IsBonus')::boolean`
  или делегирование локальной части в СДК его уберёт, но ~3.2 с в СДК-ветке это не трогает,
  поэтому имеет смысл только вместе с 1a/1b.

Перед правкой проверить существующий `Card.GetBonusBalanceByClient(client_id)`: он делает
`SUM(BonusBalance) ... WHERE ClientID=$1`. Концепт [[Bonus-GetTotalBalance]] помечает его как
«ненадёжный» — нужно выверить scope (владелец vs партнёр, франшизные vs локальные карты) и
семантику `BonusBalance` (полный) против `AvailableBonusBalance` (доступный, читается из `Карта`).

Методы 1a/1b — зона СДК `discount-cards`, согласовать с Кузаковым Ю.
