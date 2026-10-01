---
type: concept
title: "Карточка акции, вкладка «Отображение на карте»: превью сайта и штампики на конструкторе Дизайна ДК"
created: 2026-09-25
updated: 2026-09-25
status: developing
tags:
  - discount-card
  - discount-card-design
  - site-constructor
  - promotion
  - stamps
related:
  - "[[DiscountCard-Design-Constructor-Project]]"
  - "[[DiscountCard-Design-Constructor-Architecture]]"
  - "[[DiscountCardTemplate-Create-Design-Dialog]]"
  - "[[DiscountCardType-Create-Design-Constructor]]"
---

# Карточка акции, вкладка «Отображение на карте»: превью сайта и штампики на конструкторе Дизайна ДК

Задача №06242899 (`019ef86c-9ebd-7349-b3db-76b9ed4a19be`), автор и ответственный Михель, срок 10.10, этап 9 проекта [[DiscountCard-Design-Constructor-Project]]. Требования к БЛ Лебедева дописала в тело задачи 24.09. Всё под фичей `dc_design_new`.

Требования в задаче короткие:
- `DiscountCardDesign.GetList` должен отдавать скриншот сайта в `PreviewUrl` и поле `SiteId`;
- `Promotion.Update` с `StampedDiscountCards` должен «инициализировать данные штампиков»;
- `DiscountCardType.CreateWithStamps` должен сделать так, чтобы `DataContext.Read` возвращал `Stamps` («и ShowStamps??»).

## Что на самом деле значит «инициализировать штампики»

Ответ нашёлся во фронте (`client/`), а не в ТЗ.

- **Значения по умолчанию бэку заполнять не нужно.** Виджет `LoyaltyPublic/DiscountCard/Design/_constructor/Stamps.tsx` сам подставляет цвета `#28bd44` / `#8991a9` / `#db4200` и иконки «кубок»/«подарок». Раскладку по умолчанию («маленькие снизу справа») даёт `useLayoutValue` в `_constructor/Helpers.ts`. Пустой `Stamps` рисуется нормально.
- **Видимость штампиков фронт берёт из `LoyaltyCardDesign.ShowStamps`.** Баннер показывает их только при `true` (`_constructor/Banner.tsx:24`), действие «Скрыть» ставит `false`, чипса «Штампики» — `true` (`LoyaltyOnline/DiscountCard/_designConstructor/Chips.tsx:166`).
- **Но `ShowStamps` нет ни в ПО, ни в СДК.** В `DiscountCard.aorx` у `LoyaltyCardDesign` такого свойства нет. `LoyaltyCardDesign.Write` в СДК сохраняет только поля из `DEFAULT_VIEW_DETAILS` (`dcservice/appobjectimpl/loyaltycarddesign/helpers.py`), где его тоже нет. Проверено на `origin/rc-26.5100` СДК, включая правку Кузакова от 17.09 (`2d03aa4d7`). Значит, «Скрыть штампики» сейчас после сохранения не держится.

Тимошенко спросил об этом Лебедеву 24.09. Её ответ в 17:25: «Давай пока тогда без ShowStamps, только Stamps». Отсюда решение: «штампики включены» = `Stamps` заполнен. Фронту для этого нужно поменять условие показа на «`Stamps` заполнен», а «Скрыть» — на очистку `Stamps`. Подтверждения, что фронт это берёт, на 25.09 нет.

## Реализация

Ветка `26.5100/feature/aatimoshenko/06242899` от `origin/rc-26.5100`, не закоммичено на 25.09.

- **`GetList`: `SiteId` и скриншот берём из готового метода СДК.** `CardType.GetSiteList(CardTypeUUIDs)` (Кузаков, `2efb16446`, 28.07; в `rc-26.5100` СДК есть) отдаёт `SiteId` и `SiteSnapshot` по активному шаблону со всех аккаунтов. Его же под фичей зовёт `GetListSimple` (`priceformationcommon/.../get_list_simple.py`). Правка СДК не понадобилась, UUID типа карты — из `ВидКарты."Идентификатор"`. Если у дизайна есть `SiteId`, в `PreviewUrl` кладём `SiteSnapshot`, даже пустой: превью брендбука для такого дизайна уже неактуально. `SiteId` добавлен в контракт в `DiscountCard.orx`.
- **`init_design_stamps(card_type_id, require_site=True)`** в `discountcard/discountcarddesign/card_design.py`. Функция делает `CardTemplate.Read` (активный шаблон: `@Template`, `SiteId`), затем `LoyaltyCardDesign.Read`. Если в `Stamps` пусто, пишет туда три цвета по умолчанию и вызывает `LoyaltyCardDesign.Write`. Это то же чтение и запись целиком, что делает фронт, поэтому остальной дизайн не теряется. Сразу писать через `CardTypeTemplate.Update` нельзя: он заменяет `ViewDetails` целиком, а `CardTemplate.Read` `ViewDetails` не отдаёт. `Layout` не пишем — у aorx и фронта разная нумерация (см. ниже).
- **`Promotion.Update`**, ветка вкладки (`_update_card_view`): штампики включаются **только у добавленных** карт (новый список минус старый) и в самом конце, после всех записей в БД. Если включать у всех, каждое пересохранение вкладки возвращало бы штампики, скрытые в конструкторе. Ошибка СДК по одной карте только пишется в лог: связи уже сохранены, а штампики можно включить чипсой.
- **`CreateWithStamps`**: после `DiscountCardType.Create` вызывается `init_design_stamps(..., require_site=False)`. Сайта на этот момент ещё нет, но шаблон уже заполнен в формате конструктора обработчиком `after_create`.

Проверки: тесты `card_design` 12 OK, `GetList` 7 OK, `discountcardtype/create` 13 OK, pylint 10/10, radon A/B. Тесты вкладки в `Promotion.Update` написаны, но **не запускались** (см. «Инструментальное»).

## Открытые вопросы

- **Нумерация `Layout` разная.** В aorx `0` — «Большие штампики, по центру», во фронтовом `Constructor/Interfaces.ts` `0` — «Маленькие, снизу справа», а «Большие по центру» — `9`. Для этой задачи не важно, но при сборке картинки баннера по данным из БД раскладка перепутается.
- **Картинку баннера со штампиками для Apple Wallet / Google Pay на новых дизайнах пока никто не делает.** `GetBannerInfo` из ТЗ не реализован ни в одном репозитории. В `LoyaltyCardDesign.Write` висит TODO «Обновление образов, штампиков». Признак `with_stamps` в СДК вычисляется только из `ThemeData` брендбука (`dccore/cardtemplate/entity.py:235`). По чтению кода выходит, что для дизайнов на конструкторе обновление картинки баннера со штампиками не запустится; на стенде не проверено.
- **Механизм скриншотов может смениться.** 17.09 Лебедева предлагала свой скриншотер на бэке, решили подождать доработку платформы, а если её не будет — в ноябре делать своё. Для этой задачи это не важно: правка будет внутри `GetSiteList`.

## Источники

- ТЗ проекта «Техническое задание.sabydoc», раздел «Карточка Акции, вкладка Отображение на карте»: скриншоты через `Site.GetList` с `IncludeSites`, отдельный метод `GetBannerInfo` для страницы скриншота баннера.
- Переписка по задаче №06242622 (`GetListSimple`, 27.07–21.09).
- Диалог по задаче с Лебедевой 23–24.09.
- Код `price-formation` (`rc-26.5100`) и `discount-cards` (`origin/rc-26.5100`).

## Инструментальное

- Тесты `tests/tests_priceformationonline/loyaltyprograms/promotion/update.py` в собранном проекте `online` **не импортируются вообще**: нет модуля `cloud_statistics`. Проверено через `git stash` — от правок не зависит. Класс `DisplayOnACardTab` объявлен только под `is_online_with_discount_core()`, а этот проект не собран.
- Файлы тестов, которые импортируют `tests_priceformationonline...` без префикса `tests.`, для `-m unittest` требуют `tests/` в `PYTHONPATH` (`.../price-formation/tests;.../price-formation`). Иначе unittest показывает только невнятное `has no attribute`.
- Изменение контракта в orx (новое возвращаемое поле) подхватилось тестами без пересборки тестового проекта.
