---
type: synthesis
title: "Bonus.GetClientListWithStats — франшизные персональные счета с BonusBalance=0 в СДК"
created: 2026-08-06
updated: 2026-08-06
tags:
  - loyalty
  - bonuses
  - franchise
  - discount-cards
  - sql
  - price-formation
  - sbis
status: developing
question: "Почему после расторжения франшизного договора в реестре Бонусы\\Клиенты не показывается баланс части физлиц, хотя в карточке клиента баланс верный?"
answer_quality: solid
related:
  - "[[Bonus-GetTotalBalance]]"
  - "[[GetClientListWithStatsTotals-Franchise-WelcomeBonus-Double-Bug]]"
  - "[[GetClientListWithStats-PA-NavCondition-Duplicate-Bug]]"
  - "[[Franchise-Loyalty-System]]"
  - "[[Loyalty-Franchise-Mechanics]]"
  - "[[Bonus-GetTotalBalance-Local-Card-Scan-Memory]]"
---

# Bonus.GetClientListWithStats — франшизные персональные счета с BonusBalance=0 в СДК

Задача **№08041679** (ошибка на стенде `test-online`, репортёр Дорогунцова Н.А., 2026-08-04).
Франшиза: владелец «Календула123», франчайзи «Приоритет1». После расторжения франшизного
договора и синхронизации в реестре Бонусы\Клиенты у части физлиц (с идентификаторами,
без выданной карты) не отображается баланс — ни построчно, ни в итогах. В карточке
конкретного физлица баланс при этом верный. Автор задачи предположила «легальное кэширование
реестра» — гипотеза не подтвердилась.

## Первая гипотеза (опровергнута логами)

Похожий паттерн уже разбирался в [[Bonus-GetTotalBalance-Local-Card-Scan-Memory]] и
[[GetClientListWithStatsTotals-Franchise-WelcomeBonus-Double-Bug]]: `has_franchise`
(`bool(FranchiseBusinessGroup.get_list())`) переключает, идёт ли код в СДК за франшизным
балансом. Гипотеза: после расторжения `has_franchise` становится `False` на стороне
владельца → СДК-ветка перестаёт вызываться.

**Не подтвердилось.** `cloud_get_logs` (стенд `test-online`, ruuid `019fcb51-2a8d-...` и
`019fcb4a-43ad-...`) показал: папка бизнес-группы владельца **не удаляется** при расторжении
с одним франчайзи (`_handle_terminated` в `handle_agent_group.py` перенаправляет обработку
целиком в схему франчайзи и завершается — очистка папки `ВидЦены`/`ВидКарты` происходит
только там, не у владельца). `has_franchise=True` сохраняется, `Card.GetBonusBalanceByCardType`
и `Card.GetPersonalCardBonusBalanceSum` реально вызываются.

## Вторая гипотеза (тоже опровергнута)

`Bonus.GetClientListWithStats` (построчный БЛ-метод, не totals) собирает
`ClientCardUUIDList` из двух CTE — `personal_accounts` (`Эмиссия IS NULL`) и `cards_only`
(реальные карты) — и шлёт **все** UUID одним списком в `Card.GetBonusBalanceByCards`.
Гипотеза: СДК-метод ищет только по реально выпущенным картам (таблица `"Card"` с
`OnlineCardTypeID`/`Number`), персональные счета там не хранятся → UUID не находится.

**Не подтвердилось.** Прямой запрос по актуальной ветке `rc-26.5100` в
`discount-cards` (после `git checkout rc-26.5100`, локальный чекаут ранее стоял на
устаревшей `26.3218`) показал: `Card.GetBonusBalanceByCards` ищет по `"Identifier"` в
таблице `"Card"` **без фильтра** по `OnlineCardTypeID`/`Number` — персональные счета там
тоже есть, просто с `OnlineCardTypeID IS NULL AND "Number" IS NULL`. Лог реального запроса
(`Card.GetBonusBalanceByCards/1`, discount-cards, `discount-cards-db.test.nix.tensor.ru`)
подтвердил: 6 UUID отправлено → **`tuples: 6`**, все найдены.

## Корневая причина — данные в СДК, не наш код

Прямой запрос к правильной БД СДК (`discount-cards-db.test.nix.tensor.ru:6432/discount-cards`,
схема `public`) по тем же 6 UUID:

| UUID | ClientID (СДК) | Тип | BonusBalance |
|---|---|---|---:|
| `139c52b5-3317-4420-bb72-2ba217122a3a` | 115179124 | персональный счёт | **0** |
| `3cb31f03-c236-4136-b991-cf018d2728f4` | 115179124 | персональный счёт | **0** |
| `7ad58f17-b6e7-4c80-8958-8365e06814cc` | 115179124 | персональный счёт | **0** |
| `ee633029-db05-4323-a265-270e09192315` | 115179124 | персональный счёт | **0** |
| `1c06df44-6c28-40ff-9e1c-7da692ec7dab` | 115179124 | персональный счёт | 253 |
| `266b6aa9-7961-439d-82fe-ec35ebb758ab` (Номер `EAAA100000000`) | 115179124 | карта, тип 2 | 100 |

Реестр показывал 353 (= 253 + 100) для одного клиента и 100 для другого — ровно два
ненулевых значения. Три недостающих клиента («Бонбон Бонус», «Физик Два», «Физик Раз»)
— это три персональных счёта с `BonusBalance = 0`.

> [!key-insight] Код price-formation работает корректно на всех проверенных участках
> SQL строит `ClientCardUUIDList` верно, `has_franchise=True` подтверждён, UUID уходят
> в `Card.GetBonusBalanceByCards`, СДК находит все 6 записей, маппинг
> `{CardUUID: Bonus} → баланс строки` в `_get_card_balance` отрабатывает верно (подтверждено
> и юнит-тестом `test_franchise_balance`, и логами — ненулевые 253/100 дошли до UI). Метод
> запросил и получил именно то, что реально лежит в СДК: `BonusBalance=0`.

Значит проблема — в том, что СДК не посчитал/не засинхронизировал реальный накопленный
бонус (по тексту задачи: приветственные через SabyGet, вручную через ПМО, по событию на
день рождения) в свою колонку `"Card"."BonusBalance"` для этих персональных счетов. Это
зона discount-cards, не price-formation.

## Методическая находка: подбор правильного шарда/алиаса СДК

Датасорсы PyCharm с именем `discount-cards@*` (`test-services-db3`, `fix-services-db9`,
`pre-test-services-db6`, `dev-services-db5`) — **не тот же хост**, что реально использует
`test-online` в проде логов (`discount-cards-db.test.nix.tensor.ru`, виден в `[sql][start]`
строке `cloud_get_logs`). Запрос по тем же UUID к «похожему» датасорсу вернул 0 строк —
не ошибка, а просто другой шард/окружение. Нужно сверять host из `[sql][start][host:port/db]`
в логе с реальным датасорсом, а не полагаться на похожее имя.

Также: чтобы читать актуальный код SDK-соседа (`discount-cards`), обязательно
`git checkout` на ветку, соответствующую версии приложения из лога (`v:26.4100-92` →
`rc-26.5100`), иначе рискуешь смотреть код многовековой давности (реальный локальный чекаут
стоял на `26.3218/bugfix/...`, отстававшей на ~2000 версий) — совпадает с правилом из
CLAUDE.md «перед чтением SDK сверить ветки».

## Статус

Анализ передан автору задачи как «не наш баг» — рекомендация перевести на discount-cards
(Кузаков Ю.) с конкретной трассировкой (какие UUID, какой ClientID, что `BonusBalance=0`
после синхронизации франшизы). Фикс в price-formation не требуется и не предлагался.
