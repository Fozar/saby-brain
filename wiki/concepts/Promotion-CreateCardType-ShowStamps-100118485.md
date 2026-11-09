---
type: concept
title: "Акция: при создании типа карт из карточки акции не включается показ штампиков"
created: 2026-11-03
updated: 2026-11-03
status: testing
tags:
  - discount-card
  - discount-card-design
  - stamps
  - promotion
  - bug
related:
  - "[[Promotion-CardView-Constructor-Stamps]]"
  - "[[DiscountCard-Design-Constructor-Project]]"
  - "[[DiscountCardType-Create-Design-Constructor]]"
---

# Акция: при создании типа карт из карточки акции не включается показ штампиков

Ошибка на стенде №100118485 ([ссылка](https://online.sbis.ru/opendoc.html?guid=01a0f6d9-865b-7e48-aef8-3541de29c29d&client=3)), автор Лебедева Н.А., создана 01.10.26, 02.11.26 переназначена на Тимошенко. Веха 26.6100, срок 28.11.26. Всё под фичей `dc_design_new`.

## Симптом

В карточке акции на вкладке «Отображение на карте» создаём новый тип карт (диалог «Новая дисконтная карта»). Превью карты показывает логотип, баннер и штрихкод, но штампиков нет, а в панели справа «Можно добавить» предлагается «Штампики» — то есть показ штампиков выключен.

## Что выяснено по коду

- `DiscountCardType.CreateWithStamps` (`priceformationonline/discountcard/discountcardtype/create.py:25`) — переопределение `DiscountCardType.Create`: после создания типа карты зовёт `init_design_stamps(result.Get('@ВидКарты'), require_site=False)`.
- `init_design_stamps` (`priceformationonline/discountcard/discountcarddesign/card_design.py:197`) читает ПО ДизайнКарты через `LoyaltyCardDesign.Read`, заполняет `Stamps` цветами по умолчанию (`DEFAULT_STAMPS`) и пишет обратно через `LoyaltyCardDesign.Write`.
- Видимость штампиков на превью определяется не заполненностью `Stamps`, а флагом ПО ДизайнКарты `ShowStamps`: `client/LoyaltyOnline/DiscountCard/_designConstructor/Chips.tsx` (чипса «Штампики» ставит `true`, «Скрыть» — `false`), `client/LoyaltyOnline/Promotion/Form/_cardDesign/ViewReact/CardTypeDetails.tsx:123`.
- `init_design_stamps` этот флаг не трогал. В `LoyaltyCardDesign.Read` (`discount-cards`, `dcservice/appobjectimpl/loyaltycarddesign/read.py`) `ShowStamps` приходит из `ViewDetails`, а в `Write` (`write.py`) для отсутствующего поля берётся `DEFAULT_VIEW_DETAILS['ShowStamps'] = None`. То есть у нового дизайна флаг пустой и показ выключен.

Это продолжение истории из [[Promotion-CardView-Constructor-Stamps]]: 24.09 Лебедева сказала «пока без ShowStamps, только Stamps». Позже фронт перевели на `ShowStamps`, а заполнение штампиков на бэке осталось прежним — отсюда расхождение.

## Причина

В зоне price-formation: `init_design_stamps` заполняет `Stamps`, но не включает `ShowStamps` в прикладном объекте ДизайнКарты.

Тот же дефект был у второго вызова — `_init_stamps_for_added_cards` в `priceformationonline/loyaltyprograms/promotion/update.py:292` (карты, которые акция только начала штамповать): штампики заполняются, показ не включается.

## Решение

Фронт (Лебедева): `client/LoyaltyPublic/DiscountCard/Design/_constructor/Stamps.tsx` — демонстрационная раскладка теперь только при `showDemoStamps && !showStamps`. MR !153466–!153468, ветка `26.6100/bugfix/100118485_show_stamps`, влита в `rc-26.6100` 03.11 (документ MR №110211328).

Бэкенд (Тимошенко):

- `priceformationonline/discountcard/discountcarddesign/card_design.py` — `init_design_stamps` вместе со `Stamps` ставит `ShowStamps = true` через `Put(..., sbis.FieldType.ftBOOLEAN)` (у нового дизайна поля в записи ещё нет, `Set` упадёт). Ранний выход — только если штампики уже настроены **и** показ уже включён.
- Правка сделана внутри `init_design_stamps`, а не в `create_with_stamps`: иначе у второго вызова (`promotion/update.py`) остался бы тот же баг.

Поведение меняется и для карт, которые акция только начала штамповать: если штампики были настроены и скрыты, показ включится, сами настройки (цвета, иконки, раскладка) не трогаются.

## Проверки

- `tests/.../discountcard/discountcarddesign/card_design.py` — 17 тестов OK (было 16). Новый `test_hidden_stamps_enabled`, в трёх существующих проверяется `ShowStamps`; `test_configured_stamps` теперь про «настроены и показ включён».
- Красный до фикса: 4 падения ровно на симптоме (`ShowStamps` = None, `Write` не вызван), после фикса зелено.
- `discountcard/discountcardtype/create.py` (54 теста, включая `CreateWithStamps`) — OK, `loyaltyprograms/promotion/update.py` (78 тестов) — OK.
- pylint по проектной конфигурации: 10.00/10.

## Ссылки

- Задача: https://online.sbis.ru/opendoc.html?guid=01a0f6d9-865b-7e48-aef8-3541de29c29d&client=3
- Ветка: `26.6100/bugfix/aatimoshenko/100118485`, коммит `1ba9c264cd`, worktree `D:/dev/pf-26.61`
- MR: документ [01a1a0fd](https://online.sbis.ru/opendoc.html?guid=01a1a0fd-6cd4-740b-bd0c-7e2d3ac9bc68&client=3), GitLab !153523–!153526 (rc-26.6100, rc-26.6200, rc-26.6206, rc-27.1100)
- Фронт Лебедевой: MR №110211328, !153466–!153468 (влито)

## Инструментальное

- Тесты линейки 26.6100 гоняются только на стенде `D:/dev/pf-26.61` (build `D:/dev/test_build/pf-26.61`, SDK 266000). Сборка основной папки сделана на SDK 265100 и не грузится: `ImportError: DLL load failed while importing wrap`.
- `py_tests_runner.py` ищет тесты по имени файла; путь с подкаталогом (`discountcard/discountcardtype/create.py`) даёт 0 тестов.
