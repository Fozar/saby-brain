---
type: synthesis
address: c-000278
title: "DiscountCardType.Create/Init — конструктор дизайна ДК в диалоге создания типа карты"
created: 2026-08-13
updated: 2026-08-25
status: developing
tags:
  - loyalty
  - discount-cards
  - site-builder
  - price-formation
  - wasaby
question: "Что нужно доработать в БЛ price-formation, чтобы диалог создания типа карты открывал новый конструктор Дизайна ДК?"
answer_quality: solid
related:
  - "[[DiscountCard-Design-Constructor-Architecture]]"
  - "[[DiscountCard-Design-Constructor-Project]]"
  - "[[DiscountCard-Design-Constructor-WorkPlan]]"
  - "[[DiscountCard-Service-API]]"
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[Лебедева-Наталья]]"
  - "[[Ютман-Элина]]"
  - "[[Михель-Витольд]]"
  - "[[Омельяненко-Егор-Анатольевич]]"
  - "[[discount-card-design-constructor-attachments-2026-08-06]]"
---

# DiscountCardType.Create/Init — конструктор дизайна ДК в диалоге создания типа карты

Задача №06242691 (`019ef85e-68a4-791c-9274-146c1ac2e866`), веха 26.5100 online/inside до 10.10.26, часть проекта [[DiscountCard-Design-Constructor-Project|«Перевод дизайна дисконтных карт на конструктор»]]. Пункт плана `604450129` в «План работ (Разработка): август 2026, Система лояльности, Федько Юрий», план 3 ч, срок 31.08.

Блокер от 12.08 снят: 25.08 [[Омельяненко-Егор-Анатольевич|Егор]] снял с задач Михайленко Елену и передал их Тимошенко, решение велено обсуждать с [[Ютман-Элина|Ютман]] и Кузаковым. Требуется **общий код на три пересекающиеся задачи**, а не три отдельные реализации — прямая формулировка Михайленко 25.08: «Нужен общий код который позволит решить эти три задачи».

> [!warning] Раздел «Реализация» ниже описывает ветку от 13.08 и частично устарел
> ТР переписывалась дважды после того, как эта реализация была зашелвлена. Что именно разошлось — см. §Устаревшие части зашелвленной реализации.

## Три задачи и их владельцы

| Задача | Этап проекта | Владелец этапа |
|---|---|---|
| `019ef85e` диалог создания **типа карты** — наша | Этап 4 | [[Лебедева-Наталья\|Лебедева]] |
| `019ef85f` диалог создания **дизайна** | Этап 5 | Кузаков Юрий |
| `019ef861` **пустое представление** реестра | Этап 6 | [[Омельяненко-Егор-Анатольевич\|Омельяненко]] |

Все три висят на вехе 26.5100 и на «Пунктах проверки» одного проекта. В плановой смете проекта (03.04.2026) Тимошенко в составе нет — задачи докинуты сверх сметы, отдельного пункта плана под переданную задачу Михайленко на 25.08 не заведено.

## Эволюция ТР

Три редакции, каждая режет объём БЛ.

| Пункт | 11.08 | 13.08 | 25.08 |
|---|---|---|---|
| Создать сайт дизайна | делаем | зачёркнуто: «фрейм не меняем, на фронте шаблон» | пункт удалён совсем |
| Привязать ПО к сайту | делаем | зачёркнуто: «ид шаблона уже есть в `CardTemplate`» | удалён |
| Запись в `CardTemplate` + `ViewDetails` | делаем | делаем | делаем, источники раскрыты |
| Блоки обратной стороны | пишет БЛ в сайт | пишет БЛ в сайт | **пишет UI**, БЛ только отдаёт данные |
| Реф. ссылка на обратной стороне | делаем | «не нужно» + пример | из ТР **удалена** |
| В загрузчик конструктора | `SiteId` + `CardTemplateId` | `SiteId` + `CardTemplateId` | только `CardTemplateId` |

Источники `ViewDetails` раскрыты 25.08: баннер и логотип — с **опубликованной** ТП, «по аналогии с промостраницей Промокода, метод уже есть»; название — с той же ТП; цвета — «пока не делаем»; блоки — «Кэшбэк» → `[Кэшбэк]` и «Ваши бонусы» → `[Баланс бонусов]`.

`DiscountCardType.Init` **сменил смысл**: было «вычитываем контент сайта по `SiteId`, заполняем фрейм обратной стороны», стало «возвращает данные по ТП для заполнения обратной стороны» → `address: string`, `phone: string`. Заполнение выполняет фронт перед сохранением сайта.

Ответы Ютман 25.08 дословно: «сайт на Create создавать не будем, только поле добавить в формат метода надо. Сайт создастся через механизмы конструктора, вам на Update надо будет только идентификатор из SiteId сохранить в БД»; «данные для этих полей нам откуда-то получить надо, поэтому метод по-прежнему нужен». Пункт исходной постановки «в `Update` удалить созданный сайт / чистить сайты у черновиков» отпал вместе с созданием сайта.

> [!note] Свежая версия ТР не приходит по ссылке из вложения задачи
> `disk.sbis.ru/disk/api/v1/<id>_<version>` отдаёт зафиксированный снимок. Актуальную редакцию возвращает тот же адрес **без второго uuid**: `disk.sbis.ru/disk/api/v1/68a8b956-51fa-4cf5-ab8c-9a092720ddca`. Различие обнаружилось на правке Ютман 25.08 — по «версионному» href приходил документ двухдневной давности.

## Состояние СДК на `rc-26.5100`

Проверено по `origin/rc-26.5100` (`6becc4ee7`) репозитория `discount-cards`.

- `SiteId` **уже в контракте** `CardTypeTemplate.Update` (`www/DCService/dcservice/online/cardtypetemplate/update.py:69`). Закрытый MR Кузакова №06296014 (`019f12c1-4273-7417-9a4b-8c8eff694ef8`, 08.08) завёл колонку и поддержал чтение/сохранение. В `price-formation` `save.py` целиком прокидывает запись в `CardTypeTemplate.Update` — то есть сохранение поля работает само, доработок под `Update` не требуется.
- `ViewDetails` — JSONB-колонка `CardTemplate` с описанной структурой (`www/DCCore/Core.dicx:556`): `Logo`/`LogoID`, `Strip`/`StripID` (баннер), `Description`, `OrganizationName`, `BackgroundColor`/`TextColor`/`LabelColor`, `TypeBarCode`, `ShowDescription`, `BannerType`, `CustomBlockList`, `Widgets{aw, gp}`. Под неё есть датакласс `ViewDetails` с `KEY_MAPPING`/`from_db`/`from_brandbook`/`to_db` и готовый `DEFAULT_VIEW_DETAILS` (`www/DCCore/dccore/cardtemplate/entity.py:127` и `:245`).
- Пишется **мержем**, а не перезаписью: `www/DCCore/dccore/cardtemplate/save.py` → `"ViewDetails" = COALESCE("ViewDetails", '{}') || !ViewDetails`.

### Засада: `ThemeData` перезатирает `ViewDetails`

`www/DCService/dcservice/online/cardtypetemplate/update.py:88`:

```python
theme_data = input_record.Get('ThemeData')
if theme_data:
    view_details = _format_view_details(theme_data)
    new_record.Set('ViewDetails', view_details)
```

При непустом `ThemeData` поле **безусловно пересобирается из брендбука**. А `CardTypeTemplate.Create` — это только обработчик `before_create` с валидацией `ClientID`/`CardTypeID`, создание декларативное, `ViewDetails` он не трогает вовсе. Следствие: инициализировать надо отдельным вызовом после `Create`, и при новом конструкторе `ThemeData` из `price-formation` слать нельзя, иначе инициализация затрётся. Вопрос вынесен Кузакову 25.08, ответа пока нет.

## Данные точки продаж

Готовый путь для «опубликованной ТП», на который ссылается ТР, — промокодный `priceformationonline/loyaltyprograms/promocode/get_sale_point_data.py`: `Establishment.OffersList` в `showcase-service` с фильтром по опубликованным, с фолбэком на `get_sale_point_design` (настройки самой ТП). Возвращает `(id, коммерческое название, лого, баннер)`.

Для сценария «пользователь сменил ТП в диалоге → обновить баннер и лого» **новый метод не нужен**: `LoyaltyProgram.GetSalePointDesign(SalePointId, Options) → {Logo, Banner}` уже объявлен с `access_mode="0"` (`PriceFormation.Online/LoyaltyPrograms.orx:4951`), внутри — `ShowcasePublic.GetImages` по СПП точки. Ютман 25.08 просила «сделать метод доступным с фронта» — он уже доступен. Разница путей осмысленная: в `Create` ТП ещё не выбрана, поэтому нужна первая **опубликованная**; при смене ТП точка известна, проверка публикации не нужна.

Адрес и телефоны берутся не оттуда, а из `OurCompanyReader.Get` (`АдресФактический` с фолбэком на `АдресЮридический`) и `OCContact.List` с `Types: ['phone']`.

### Расхождение в текстах блоков

Существующий механизм (`discountcarddesign/get_draft_list.py:52`) задаёт блоки как `{'label': 'Кешбэк', 'value': '[BonusDescr]'}` и `{'label': 'Ваши бонусы', 'value': '[BonusBalance]'}`. ТР от 25.08 требует «Кэшбэк» → `[Кэшбэк]` и «Ваши бонусы» → `[Баланс бонусов]`. Разные подстановки и разное написание «Кешбэк/Кэшбэк» — уточнять у Ютман перед реализацией `ViewDetails`.

## Реализация

### Часть по ТП (25.08, ветка `26.4213/bugfix/aatimoshenko/07248704`)

- `priceformationonline/helpers/sale_point.py` → `get_sale_point_contacts(sale_point_id) -> (адрес, телефоны)`.
- `priceformationonline/dcservice/servicediscountcard/discountcardtemplate/core/sale_point.py` → `get_design_sale_point()` (`{Id, Name, Logo, Banner}` с опубликованной ТП) и `get_back_side_data()` (`{Address, Phone}` — тело будущего `Init`).

pylint 10.00/10, тестов пока нет. Код написан **не в ветке задачи**, а в текущей рабочей — при оформлении надо переносить. `get_sale_point_contacts` дублирует ~10 строк приватного `_get_sale_point_phones` из устаревшего `get_draft_list.py:316` (там уже стоит `sbis.ErrorMsg('Вызывается устаревшая функция')`).

### Ветка от 13.08 (`26.5100/feature/aatimoshenko/06242691`, зашелвлено)

Всё под фичей `dc_design_new` (`Feature.DC_DESIGN_NEW`). `init_template_design(card_type_id, template_id, card_title)` читала аспект через `ThemeManager.Read`, прогоняла через `provide_dc_theme_data` и отдавала в `CardTypeTemplate.Update`, полагаясь на конвертацию темы в `ViewDetails` силами СДК. `Init` сохраняла `SiteId` и дописывала во фрейм обратной стороны виджеты `:Address`, `:Phone`, `:Referral` (`discountcardtype/design_site.py`), идемпотентно, с глушением ошибок через `Try`. Механика правки сайта была вынесена из анкеты (`dcquestionary/.../core_site_constructor.py`) в общий `priceformationonline/core/site_constructor.py` с параметром `constructor_id`. Текст реферального блока собирался процентом = max по `Level1/2/3BonusPercent` из `ReferralBonus.ReadLite()`. Тесты: 9 новых `design_site` + по 2 кейса в `create`/`init`, зелёные, pylint 10.00/10.

### Устаревшие части зашелвленной реализации

- `design_site.py` — дописывание блоков обратной стороны на бэке. По ТР от 25.08 это делает UI, БЛ только отдаёт `address`/`phone`. Вероятно, не нужен целиком; вынос `site_constructor.py` теряет обоснование вместе с ним.
- Реферальный блок и `get_referral_bonus_info` — реф. ссылка удалена из ТР.
- Инициализация `ViewDetails` дефолтами аспекта брендбука — ТР от 25.08 требует баннер, логотип и название **с опубликованной ТП**, а не дефолты. Прежнее допущение («дефолты аспекта устраивают») снято.
- Сохранение `SiteId` из `Init` — по ответу Ютман это делает `Update`, и оно уже работает через СДК.

Что остаётся годным: расклад по `ПослеСоздать`/`calculated_fields` (см. ниже), вывод про хранение `SiteId`, находки по тестам.

## Переиспользуемые находки

### Вычисляемое поле нельзя вернуть из обработчика `ПослеСоздать`

В `DiscountCardType.Create` (`insert_on_create="true"`) обработчик `ПослеСоздать` получает **узкую запись только с полями БД** — `record.Set('DiscountIdList', …)` падает с «Ошибка! Нет поля "DiscountIdList" в формате записи». Идентификатор, вычисленный в `after_create`, в результат `Create` не попадает; видны только изменения, доехавшие до БД.

Вычисляемые поля результата `Create` заполняет `after`-обработчик того **списочного метода, чьё имя передано первым аргументом** (`sbis.DiscountCardType.Create('DiscountCardType.GetList', …)`). Чтобы поле дошло до клиента, в `.orx` мало объявить `<calculating calc_on_sever="true">` — нужен ещё `<return full_path="РП.<Имя>">` в спецификации списочного метода, иначе `record.TestField(name)` внутри `after` вернёт `None` и поле молча выбросится. Правка `.orx` подхватывается тестовым стендом без пересборки.

### `SiteId` живёт в СДК, а не в атрибутах типа карты

Дублировать `SiteId` в `ВидКарты.Атрибуты` (по аналогии с `Card/QuestionarySiteId`) — ошибка: задвоение состояния плюс поломка на типах карт с несколькими дизайнами (`DiscountCardType.GetTemplateList`, реестр `DesignList`).

### Ловушка тестов: `MagicMock` долетает до `record.Fill`

Тесты, мокающие `sbis.EndPoint` целиком без настройки `CardTemplate.Read`, после добавления полей падают с «No registered converter was able to produce a C++ rvalue of type __int64 from this Python object of type MagicMock». Лечится явным `mk_end_point.return_value.CardTemplate.Read.return_value = None`. Побочно: класс-декоратор `@patch(target, new=Mock(...))` перебивает метод-декоратор `@patch(target)` на том же таргете.

## Открытые вопросы

- **Как класть `ViewDetails`, не попав под перезапись из `ThemeData`** — вопрос Кузакову от 25.08. Без ответа вторая половина хелпера не пишется.
- **Тексты блоков** — `[Кэшбэк]`/`[Баланс бонусов]` из ТР против `[BonusDescr]`/`[BonusBalance]` из существующего механизма.
- **Сроки ПО `LoyaltyCardDesign`** — задача Кузакова `0905e5c8-ce61-489e-a905-23d73b76fe21` (срок был 08.08, статус «В обработке»). Самому хелперу методы ПО не нужны (данные ПО сохраняет конструктор), но без ПО конструктор не прочитает преустановленные данные по `CardTemplateId`.
- **Границы хелпера** — заводит ли метод `DiscountCardType.Init` в `.orx` автор хелпера или владельцы сценариев.
- **Пункт плана под переданную задачу** `019ef85f` — 3 ч на две задачи не бьётся.
- Расхождение имён: ТР называет методы `DiscountCardType.Create/Update/Init`, Лебедева 11.08 писала про `DiscountCardTemplate.Create/Update`, Кузаков дорабатывал `DiscountCardTemplate`.
