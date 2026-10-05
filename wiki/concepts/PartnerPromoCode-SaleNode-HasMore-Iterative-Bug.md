---
type: concept
title: "PartnerPromoCode.GetClientList — кнопка «Ещё...» под продажей: порционный режим отдавал hasMore при исчерпанном блоке"
created: 2026-10-05
updated: 2026-10-05
status: developing
tags:
  - bug
  - promocode
  - partner-promocode
  - iterative
  - cursor
  - navigation
related:
  - "[[LoyaltyPrograms-IterativeListLoading]]"
  - "[[Promocode-Subsystem-Overview]]"
  - "[[BonusChart-IterativeBlock-Bug-Fix]]"
---

# PartnerPromoCode.GetClientList — «Ещё...» под продажей партнёрского промокода

Ошибка на стенде №07248704 ([ссылка](https://online.sbis.ru/opendoc.html?guid=019f9455-6cb4-7227-8248-ef7684f1c66b&client=3)), автор Куимова Н.В., заведена 24.07.2026. Карточка клиента, вкладка «Рекомендации»: при развороте продажи по партнёрскому промокоду (пример ПАРТ280924_1944, клиент Ариец В.) под единственной продажей висит «Ещё...», по нажатию — ошибка списка о дублях `Id`.

## Три круга

| Круг | Что правили | Итог проверки |
|---|---|---|
| 1, `087602fc35` (03.08) | Курсор в `PartnerPromoCode.GetClientList`: «Ещё» отдавал первую страницу заново | 10.08 «сценарий прежний» |
| 2, `ce15654011` (24.08) | `nextPosition` приходит `sbis.Record`, а не dict — `_extract_sale_cursor` его не узнавал | 26.08 «сценарий прежний» |
| 3 (05.10) | Сам признак «есть ещё» | на стенде не проверено |

Первые два круга чинили только то, что происходит **после** нажатия (дубль), а QA возвращала из-за **самой кнопки** (ОР «нет лишних кнопок»). Комментарий Маркова при переназначении («бл при нажатии на кнопку еще возвращает ту же запись») увёл в сторону дубля.

## Корневая причина

По логу браузера от 24.07 (pre-test-online): ответ на разворот — одна продажа, но `n: true` и в метаданных `iterative: true`, `nextPosition = {"DateWTZ": <дата этой продажи>}`. Фронт в узле дерева по `n` рисует «Ещё...».

Признак ставит `PromoCode.GetSaleList` (`PromoCodeSaleListIterative`). В порционном режиме `ListWithCursor` выставляет `nav_result = bool(next_position)`, а `next_position` есть всегда, когда в блоке есть хоть одна запись (контрольная запись). Итерация кончалась только пустым блоком — то есть лишним запросом. Неполный блок (`ScannedCount < _iterative_block_size`) не учитывался, хотя он значит, что до конца таблицы в этом направлении всё прочитано.

У акций это уже было решено своим способом — `SaleDateBound` в `promotion/get_sale_list.py` (контрольная запись подавляется, когда блок дошёл до самой ранней продажи).

## Фикс

`promocode/get_sale_list.py`: `PromoCodeSaleListIterative._prepare_next_position_iterative` — если `ScannedCount < _iterative_block_size` и `RawResultCount <= _limit`, контрольная запись удаляется и `nextPosition = None`. Счётчики запрос уже считал, SQL не менялся. Значения читаются из контрольной записи до `DelRow`, ссылка на запись отпускается (антипаттерн «удаление строки при живой `rec`»).

Тесты в `tests/.../promocode/get_sale_list.py`: `test_no_more_when_block_not_full` (красный до фикса: `[{'DateWTZ': '2025-03-19 00:00:00'}] is not false`), `test_has_more_when_block_full` (блок 1 через `GlobalParams`), `test_has_more_when_page_full` (limit 1). Файл 45 OK / 2 skipped, `partner_promo_code` 33 OK, pylint 10/10.

**Ограничение**: блок считается по промокоду, не по клиенту. Если партнёрским кодом воспользовались больше 10 000 раз (все клиенты вместе), блок полный и «Ещё...» у клиента останется. Вторым шагом можно догружать на сервере в `PartnerPromoCode.GetClientList`.

## Почему не в базовом классе

Все пять порционных реестров — продажи промокодов, бонусов, акций, реферальных бонусов и `DiscountCard.GetListWithStats` — читают блок одинаково (`LIMIT !_iterative_block_size`) и отдают `ScannedCount`/`RawResultCount`, так что правило общее и убрало бы лишний пустой запрос везде. Оставлено локально, потому что ошибка про один реестр. Кроме того, `_prepare_next_position_iterative` продублирован в `ListWithCursor` и `ListWithCompositeCursor`, а `IterativeBlockSizeEmaMixin` нет у реферальных бонусов. Пользователь 05.10 согласился: перенос в базу — отдельная задача (не заведена).

## Ветки

Ошибка в версии **26.6100**. Сначала ветка ошибочно сделана от `rc-26.5100` (по текущей рабочей ветке, без проверки версии в карточке): `26.5100/bugfix/aatimoshenko/07248704_has_more`, `848396691a`, запушена, MR не создавался, судьба не решена. Правильная — `26.6100/bugfix/aatimoshenko/07248704_has_more` от `rc-26.6100`, cherry-pick `a53c615a3d`, тесты те же зелёные, на 05.10 не запушена.

## Инструментальное

Файлы перехода (видео и `.sbislogz` возврата 26.08) видны в `sbis_get_timeline` только как `attach_id` без `href` — `sbis_download_attachment` их не скачивает. Разбор шёл по `.sbislogz` из вложений карточки (24.07). Тот же `.sbislogz` — zip в base64, сырые ответы с `n`/`m` видны только при распаковке: `convert_log_to_json` метаданные навигации не отдаёт.
