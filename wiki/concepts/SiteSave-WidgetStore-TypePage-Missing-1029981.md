---
type: concept
title: "Site.Save в магазине виджетов: нет Type_page.Get/3 (№1029981)"
created: 2026-10-29
updated: 2026-10-29
status: developing
tags: [price-formation, test-stand, bugfix, not-ours]
related:
  - "[[ReferralDeals-System]]"
---

# Site.Save в магазине виджетов: нет Type_page.Get/3

## Задача
Ошибка на стенде №1029981 (doc_id 633344387), веха 26.5120, автор Земцова А.В., срок 29.10.
https://dev.saby.ru/opendoc.html?guid=01a185ec-5d86-7356-ac47-0e525e034205&client=3
Приёмочные автотесты: владелец РС (test-partners, «Saby Net АТ Реферальная сеть»), магазин виджетов, удалить виджет, сохранить -> «Что-то пошло не так».

## Где остановились
Анализ готов, причина вне price-formation. Решение: передать задачу владельцу `Dashboard.Save` / `metadata-repository`.

## Что выяснено по коду
- В логе (`test-partners`, сборка online-inside 26.5120-87, Platforma 26.5100-148) `Site.Save` -> 404, код -32601.
- Цепочка в ошибке: `Dashboard.Save/2@online` -> метод `Type_page.Get` версии 3 не найден в сервисе `metadata-repository`.
- В нашем репозитории `Dashboard.Save` и `Type_page` не встречаются. `Site.Save` мы зовём только в `dcquestionary/discountcardquestionary/core_site_constructor.py` (анкета ДК), это другой путь.
- `Type_page.Get` вызывается из `sbis/service-engine`, `SiteCustomization/SiteCustomizationMetatypes/getters/type_get.py` (ветка rc-26.5111, 26.5120 в поиске нет).

## Решения и почему
Фазы 2-5 не выполняем: чинить нечего в нашем коде. Правдоподобная причина: несовпадение версий сервисов на стенде (метод версии 3 ещё не выкачен в `metadata-repository`). Это гипотеза, не проверена.

## Открытые вопросы
Кому передать: владелец конструктора сайтов / дашбордов (SiteCustomization).
