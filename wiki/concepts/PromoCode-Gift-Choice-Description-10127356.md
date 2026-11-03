---
type: concept
title: "Подарок на выбор в описании промокода — №10127356"
status: testing
updated: 2026-11-03
related:
  - "[[Акции-Architecture]]"
---

# Подарок на выбор в описании промокода

## Задача
№10127356: https://dev.saby.ru/opendoc.html?guid=01a12fc9-b6b3-7932-b8ac-227c889d5b02&client=3
Веха 26.6100, срок 28.11.2026. Ветка `26.6100/bugfix/aatimoshenko/10127356`.

## Где остановились
03.11 оформлен Merge Request: документ СБИС [01a19ffa](https://online.sbis.ru/opendoc.html?guid=01a19ffa-bc84-70ef-a76e-f96c038c9d70&client=3), GitLab MR !153497-!153499.
Коммит `5afbfecb83`. Задача переведена на этап ожидания проверки/сборки (status: testing).

## Что выяснено по коду
Настроен один любой подарок из пяти напитков. Автоописание формировалось как «Подарок <список>...» без указания выбора, поэтому воспринималось как обещание выдать все позиции.
В `promotion/description.py: _get_gift_profit_descr` проверялись `GiftItemType` и `GiftItemCount`, но не `GiftItemSetType`.

## Решения и почему
1. При `profit.Get('GiftItemSetType') == GiftDiscount.ItemSetTypeAny` формируется префикс `подарок на выбор:`.
2. В `PriceFormation.Online/lang/en.json` добавлены 4 строки перевода для английской локали (`a choice of {} as a gift...`).
3. Регрессионные тесты в `tests_priceformationonline/loyaltyprograms/loyaltyprogram/get_description.py` проверяют режим с выбором и неизменность описания подарка без выбора (29 тестов OK).

## Roadmap
- [x] Анализ проблемы и определение root cause.
- [x] Согласование формулировки «Подарок на выбор».
- [x] Регрессионный тест (красный до фикса).
- [x] Реализация фикса в генераторе описания.
- [x] Обновление словаря перевода (en.json).
- [x] Прогон тестов и проверка pylint.
- [x] Коммит `5afbfecb83` и push ветки `26.6100/bugfix/aatimoshenko/10127356`.
- [x] Создание документа Merge Request [01a19ffa](https://online.sbis.ru/opendoc.html?guid=01a19ffa-bc84-70ef-a76e-f96c038c9d70&client=3) (!153497-!153499).

## Ссылки
Ветка: `26.6100/bugfix/aatimoshenko/10127356`
Коммит: `5afbfecb83`
MR СБИС: https://online.sbis.ru/opendoc.html?guid=01a19ffa-bc84-70ef-a76e-f96c038c9d70&client=3
GitLab MRs:
- https://git.sbis.ru/warehouse/price-formation/-/merge_requests/153497
- https://git.sbis.ru/warehouse/price-formation/-/merge_requests/153498
- https://git.sbis.ru/warehouse/price-formation/-/merge_requests/153499
