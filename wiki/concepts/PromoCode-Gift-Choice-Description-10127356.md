---
type: concept
title: "Подарок на выбор в описании промокода — №10127356"
status: developing
updated: 2026-11-03
related:
  - "[[Акции-Architecture]]"
---

# Подарок на выбор в описании промокода

## Задача
№10127356: https://dev.saby.ru/opendoc.html?guid=01a12fc9-b6b3-7932-b8ac-227c889d5b02&client=3
Веха 26.6100, срок 28.11.2026. Ветка `26.6100/bugfix/aatimoshenko/10127356`.

## Где остановились
03.11 реализован фикс в `promotion/description.py` и обновлён английский словарь `en.json`.
Написаны и успешно пройдены регрессионные юнит-тесты в `get_description.py` (29 тестов OK).
Pylint чистый (10.00/10). Ждёт подтверждения пользователя для коммита.

## Что выяснено по коду
Настроен один любой подарок из пяти напитков. Автоописание формировалось как «Подарок <список>...» без указания выбора, поэтому воспринималось как обещание выдать все позиции.
В `promotion/description.py: _get_gift_profit_descr` проверялись `GiftItemType` и `GiftItemCount`, но не `GiftItemSetType`.

## Решения и почему
1. При `profit.Get('GiftItemSetType') == GiftDiscount.ItemSetTypeAny` формируется префикс `подарок на выбор:`.
2. В `PriceFormation.Online/lang/en.json` добавлены 4 строки перевода для английской локали (`a choice of {} as a gift...`).
3. Регрессионные тесты в `tests_priceformationonline/loyaltyprograms/loyaltyprogram/get_description.py` проверяют как режим с выбором, так и неизменность описания без выбора.

## Roadmap
- [x] Анализ проблемы и определение root cause.
- [x] Согласование формулировки «Подарок на выбор».
- [x] Регрессионный тест (красный до фикса).
- [x] Реализация фикса в генераторе описания.
- [x] Обновление словаря перевода (en.json).
- [x] Прогон тестов и проверка pylint.
- [ ] Одобрение коммита пользователем и создание MR.

## Ссылки
Ветка: `26.6100/bugfix/aatimoshenko/10127356`
Файлы:
- `www/service/Модули/PriceFormation.Online/priceformationonline/loyaltyprograms/promotion/description.py`
- `www/service/Модули/PriceFormation.Online/lang/en.json`
- `tests/tests_priceformationonline/loyaltyprograms/loyaltyprogram/get_description.py`
