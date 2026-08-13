---
type: synthesis
address: c-000278
title: "DiscountCardType.Create/Init — конструктор дизайна ДК в диалоге создания типа карты"
created: 2026-08-13
updated: 2026-08-13
status: blocked
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

Задача №06242691 (`019ef85e-68a4-791c-9274-146c1ac2e866`), веха 26.5100 online/inside до 10.10.26, часть проекта [[DiscountCard-Design-Constructor-Project|«Перевод дизайна дисконтных карт на конструктор»]]. Реализация написана, прогнана и **зашелвлена не закоммиченной** — см. §Блокер.

## Постановка после обновления ТР (11.08.2026)

ТР переписано [[Лебедева-Наталья|Лебедевой]] и [[Ютман-Элина|Ютман]], два из трёх блоков БЛ вычеркнуты:

| Пункт исходной схемы | Статус |
|---|---|
| Создать запись в `CardTemplate`, инициализировать `ViewDetails` | делаем |
| Создать сайт дизайна | **не нужно** — фрейм не меняем, на фронте используется шаблон конструктора |
| Привязать прикладной объект к сайту | **не нужно** — ид. шаблона уже есть в `CardTemplate` |
| Дописать блоки обратной стороны (адрес/телефон/реф. ссылка) | делаем |

Вместе с созданием сайта отпал и исходный пункт задачи «в методе Update удалить созданный сайт / чистить сайты у черновиков».

Расхождение в самом ТР: текст называет метод `DiscountCardType.Init`, схема процесса рисует `DiscountCardType.Update`. Верен **Init** — это сохранение диалога создания типа карты (`discountcardtype/init.py`); схема унаследована от соседней задачи про диалог создания дизайна.

Идентификатор прикладного объекта **ДизайнКарты** = первичный ключ `CardTemplate.@CardTemplate` (прямая формулировка Лебедевой в переписке). Сам ПО `LoyaltyCardDesign` уже объявлен в `www/service/Модули/PriceFormation.Online/DiscountCard.aorx` (автор — Лебедева) с пустым `<methods/>`; реализует его Кузаков Ю. по задаче `0905e5c8-ce61-489e-a905-23d73b76fe21`.

## Реализация

Ветка `26.5100/feature/aatimoshenko/06242691` от `rc-26.5100`. Всё новое поведение под фичей `dc_design_new` (`Feature.DC_DESIGN_NEW`, уже используется и на фронте — `Design/PrefetchConfig.ts:64`, и в БЛ — `get_template_list.py:56`, `get_list_simple.py:131`).

**Create.** `helpers.on_default_electronic_emission_list_create` уже создаёт шаблон в СДК (`CardTemplate.Save({'CardTypeID': …})`). Добавлена `init_template_design(card_type_id, template_id, card_title)`: читает настройку аспекта (`ThemeManager.Read`), пропускает через `provide_dc_theme_data` (`dccommon/core/brandbook.py` — там дефолт уже содержит `showCashback=True` и `showBonuses=True`, т.е. «блоки кэшбэк и ваши бонусы» из ТР), подставляет название ТП и отдаёт в `CardTypeTemplate.Update` — СДК сам конвертирует тему в `ViewDetails` (`_format_view_details`, `discount-cards www/DCService/dcservice/online/cardtypetemplate/update.py`). Логотип/баннер/цвета остаются дефолтами аспекта, т.е. дизайн по умолчанию совпадает со старым брендбучным (в ТР у них стоят знаки вопроса — допущение не подтверждено аналитиком).

**Init.** При непустом `SiteId` сохраняет его в СДК и дописывает во фрейм обратной стороны виджеты `LoyaltyPublic/DiscountCard/Design/widget:Address`, `:Phone`, `:Referral` (модуль `discountcardtype/design_site.py`). Блоки идемпотентны — уже размещённые не дублируются. Ошибка их заполнения глушится `Try` и не рушит создание типа карты; сохранение `SiteId` — наоборот, пробрасывается.

**Механика правки сайта переиспользована у анкеты**: `SCWidget`/`SCPageWidget`/`get_site_items` (`sbis.Site.GetPages`) / `save_site_items` (`sbis.Site.Save`) вынесены из `dcquestionary/discountcardquestionary/core_site_constructor.py` в общий `priceformationonline/core/site_constructor.py` с параметром `constructor_id`; модуль анкеты остался тонкой обёрткой с `QUESTIONARY_CONSTRUCTOR_ID`.

Текст реферального блока собирается тем же кодом, что и на брендбуке: процент = max по `Level1/2/3BonusPercent` из `ReferralBonus.ReadLite()`, вынесен в `get_referral_bonus_info` (`discountcardtemplate/core/helpers.py`) и переиспользован в `DiscountCardTemplate.Read`. Плейсхолдер `[ReferralLink]` в новом виджете не нужен — ссылку он рисует сам по `salePointId`.

Итог: 9 новых тестов `design_site` + по 2 кейса в `create`/`init`, все зелёные (`create.py` 42 OK, `init.py` 16 OK, пакет `discountcardtype` 177, `dcservice` 55 OK), pylint 10.00/10.

## Ключевые находки

### `SiteId` живёт в СДК, а не в атрибутах типа карты

Колонка `CardTemplate.SiteId` **уже существует** (`discount-cards www/DCCore/Core.dicx:582`), объект `CardTypeTemplate` отдаёт её как `<source_field full_path="CardTemplate.SiteId">` (`www/DCService/Online.orx:1571`) — значит `CardTypeTemplate.Update` пишет её штатно, доработок в СДК не требуется. Коммит `7a6c3a83b3` (Кузаков, 29.06.26, задача №05219646) завёл `SiteId` в спецификациях `DiscountCardTemplate.Read/Save` в price-formation, а `save.py:142` целиком прокидывает запись в `CardTypeTemplate.Update` — то есть на странице «Дизайн» поле, вероятно, уже сохраняется само.

Дублировать `SiteId` в `ВидКарты.Атрибуты` (по аналогии с `Card/QuestionarySiteId`) — **ошибка**: задвоение состояния плюс поломка на типах карт с несколькими дизайнами (`DiscountCardType.GetTemplateList`, реестр `DesignList`).

### Вычисляемое поле нельзя вернуть из обработчика `ПослеСоздать`

Переиспользуемое знание про платформу. В `DiscountCardType.Create` (`insert_on_create="true"`) обработчик `ПослеСоздать` получает **узкую запись только с полями БД** — `record.Set('DiscountIdList', …)` там падает с «Ошибка! Нет поля "DiscountIdList" в формате записи». Поэтому идентификатор, вычисленный в `after_create` (например `template_id` из СДК), в результат `Create` не попадает; в результате видны только изменения, доехавшие до БД (так `Card/DiscountCardThemeId` появляется в `Атрибуты` — его пишет отдельный SQL `set_card_type_attributes`).

Вычисляемые поля результата `Create` заполняет `after`-обработчик того **списочного метода, чьё имя передано первым аргументом** (`sbis.DiscountCardType.Create('DiscountCardType.GetList', …)`) — то есть `get_list.after`, там же живут `IsFranchiseOwnerAccount`, `QuestionarySiteId` и прочие. Поэтому `CardTemplateId`/`SiteId` заполняются в `calculated_fields` из шаблона СДК, который `_get_discount_card_theme_data` и так читает при `is_one_record` (сценарии Read/Create) — на списочной выдаче реестра лишних вызовов не появляется.

Чтобы поле дошло до клиента, в `.orx` его мало объявить как `<calculating calc_on_sever="true">` — нужен ещё `<return full_path="РП.<Имя>">` в спецификации списочного метода. Без второго объявления `record.TestField(name)` внутри `after` возвращает `None`, и поле молча выбрасывается из `calculated_fields`.

Правка `.orx` подхватывается тестовым стендом без пересборки — файл в `test_build/.../modules/PriceFormation.Online/` синхронизирован с репозиторием.

### Ловушка тестов: `MagicMock` долетает до `record.Fill`

Тесты, которые мокают `sbis.EndPoint` целиком, но не настраивают `CardTemplate.Read`, после добавления полей падают с `No registered converter was able to produce a C++ rvalue of type __int64 from this Python object of type MagicMock`. Лечится явным `mk_end_point.return_value.CardTemplate.Read.return_value = None` (потребовалось в `create.py` и `validate.py`).

Побочно: класс-декоратор `@patch(target, new=Mock(...))` перебивает метод-декоратор `@patch(target)` на том же таргете — параметризовать поведение по тестам через такую пару нельзя.

## Блокер

12.08.2026 13:28 Михайленко Елена в общей переписке: **«Не начинайте пока делать свои задачи. Надо обсудить с Егором почему они на трех разных исполнителях хотя на 95% пересекаются»** — про три августовские задачи Михеля: диалог создания типа карты (наша, №06242691), диалог создания дизайна (`019ef85f-f717-7757-b50e-4a057110edb5`), пустое представление реестра типов карт (`019ef861-4ff7-7b16-8a2c-0408eaca28a7`). Реализация убрана в шелф, коммита нет.

Пересечение с соседними задачами по факту невелико и аддитивно: общий `get_list.after` (два новых поля), `DiscountCardTemplate.Read` (вынос хелпера без смены поведения), колонка `CardTemplate.SiteId` (мы пишем из `Init`, Кузаков — из `Save`) и общий модуль работы с сайтами конструктора. `DCService.orx`, `DiscountCardTemplate.Create/Save`, `GetTemplateList`, реестр и фронт не тронуты.

## Открытые вопросы

- Структура страниц сайта дизайна не проверена вживую: обратной стороной считается последняя страница конструктора `DiscountCardDesign`, виджеты кладутся в `FrameControls/rootLayout:RootLayout`. Проверяется только на стенде вместе с фронтом.
- Логотип/баннер/цвета в `ViewDetails` — подтвердить у [[Ютман-Элина|Ютман]], что дефолты аспекта устраивают и тянуть их с точки продаж не нужно.
- Порядок работ зависит от готовности ПО `LoyaltyCardDesign` (Кузаков) — без него преустановленные данные в конструкторе не увидеть.
