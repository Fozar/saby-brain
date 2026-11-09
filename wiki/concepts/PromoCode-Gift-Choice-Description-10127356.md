---
type: concept
title: "Подарок на выбор в описании промокода — №10127356"
status: testing
updated: 2026-11-09
related:
  - "[[Акции-Architecture]]"
  - "[[Loyalty-November-2026-WorkPlan]]"
  - "[[zvonok-matyushev-timoshenko-plan-2026-11-09]]"
---

# Подарок на выбор в описании промокода

## Задача
№10127356: https://dev.saby.ru/opendoc.html?guid=01a12fc9-b6b3-7932-b8ac-227c889d5b02&client=3
Веха 26.6100, срок 28.11.2026. Ветка `26.6100/bugfix/aatimoshenko/10127356`.

## Где остановились
03.11 оформлен Merge Request: документ СБИС [01a19ffa](https://online.sbis.ru/opendoc.html?guid=01a19ffa-bc84-70ef-a76e-f96c038c9d70&client=3), GitLab MR !153497-!153499.
Замечание reviewbot по комментарию в `_get_gift_profit_descr` исправлено в том же коммите (`b057825256`), тред в GitLab закрыт (status: testing).

## Что выяснено по коду
Настроен один любой подарок из пяти напитков. Автоописание формировалось как «Подарок <список>...» без указания выбора, поэтому воспринималось как обещание выдать все позиции.
В `promotion/description.py: _get_gift_profit_descr` проверялись `GiftItemType` и `GiftItemCount`, но не `GiftItemSetType`.

## Решения и почему
1. При `profit.Get('GiftItemSetType') == GiftDiscount.ItemSetTypeAny` формируется префикс `подарок на выбор:`.
2. В `PriceFormation.Online/lang/en.json` добавлены 4 строки перевода для английской локали (`a choice of {} as a gift...`).
3. Блок «Возможные вариации» в `_get_gift_profit_descr` дополнен 4 новыми вариантами.
4. Регрессионные тесты в `tests_priceformationonline/loyaltyprograms/loyaltyprogram/get_description.py` проверяют режим с выбором и неизменность описания подарка без выбора (29 тестов OK).

## Roadmap
- [x] Анализ проблемы и определение root cause.
- [x] Согласование формулировки «Подарок на выбор».
- [x] Регрессионный тест (красный до фикса).
- [x] Реализация фикса в генераторе описания.
- [x] Обновление словаря перевода (en.json).
- [x] Прогон тестов и проверка pylint.
- [x] Создание документа Merge Request [01a19ffa](https://online.sbis.ru/opendoc.html?guid=01a19ffa-bc84-70ef-a76e-f96c038c9d70&client=3) (!153497-!153499).
- [x] Замечание reviewbot по комментарию учтено (`b057825256`), тред закрыт.

## Ссылки
Ветка: `26.6100/bugfix/aatimoshenko/10127356`
Коммит: `b057825256`
MR СБИС: https://online.sbis.ru/opendoc.html?guid=01a19ffa-bc84-70ef-a76e-f96c038c9d70&client=3
GitLab MRs:
- https://git.sbis.ru/warehouse/price-formation/-/merge_requests/153497
- https://git.sbis.ru/warehouse/price-formation/-/merge_requests/153498
- https://git.sbis.ru/warehouse/price-formation/-/merge_requests/153499

## Уточнение по ноябрьскому плану и встрече 09.11

Включена в ноябрьский план (пункт `631644112`), критерий «Ошибка закрыта». Срок пункта 30.11.2026, срок карточки задачи 28.11.2026; это разные сроки, прежний срок карточки не заменяем.

На встрече около 08:20 Тимошенко сказал, что после проблем на фронте сделал rebase и снова отправил исправление на ревью. Соответствие этой реплики задаче вероятно по порядку обсуждения, но номер не произнесён; конкретные MR и коммит из этой реплики не выводим. Ранее записанные MR и результат тестов сохранены без изменений.

### Открытые вопросы

- Проверить результат повторного ревью и готовность фронтенда; текущий статус MR при ingest не запрашивался.

Источники: [[Loyalty-November-2026-WorkPlan]], [[zvonok-matyushev-timoshenko-plan-2026-11-09]].
