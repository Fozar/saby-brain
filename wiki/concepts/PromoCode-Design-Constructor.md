---
type: concept
title: "Карточка промокода, вкладка Дизайн: конструктор Дизайна ДК вместо брендбука"
created: 2026-10-07
updated: 2026-10-27
status: developing
tags:
  - promocode
  - discount-card-design
  - site-constructor
  - tech-design
related:
  - "[[DiscountCard-Design-Constructor-Project]]"
  - "[[DiscountCard-Design-Constructor-Architecture]]"
  - "[[DiscountCardTemplate-Create-Design-Dialog]]"
  - "[[DiscountCardType-Create-Design-Constructor]]"
  - "[[Promotion-CardView-Constructor-Stamps]]"
  - "[[Promocode-Subsystem-Overview]]"
---

# Карточка промокода, вкладка Дизайн: конструктор Дизайна ДК вместо брендбука

Задача в разработку №09234630 ([ссылка](https://online.sbis.ru/opendoc.html?guid=01a0cd66-19fe-711a-a425-6fb43e1a9c21&client=3)), автор Михель, этап 10 проекта [[DiscountCard-Design-Constructor-Project]] (исполнитель этапа Лебедева). Веха 26.6100, срок 28.11.2026, базовая ветка `rc-26.6100`. Всё под фичей `dc_design_new`.

## Состояние постановки на 07.10

- В ТЗ проекта (раздел "Карточка Промокода, вкладка Дизайн") БЛ расписан через `Promotion.Create/Update/Read` и создание сайта на бэке. Это устарело: у промокода свой объект `PromoCode.*`, а сайт на бэке не создаем ни в одном сценарии проекта (решение по ДК от 25.08).
- 05.10 Матюшев спросил, почему `Promotion`, где брать API сайтов, что с `DesignError`, блокировать ли создание промокода при недоступности сервиса, что со старым дизайном. Ютман в тот же день переписала блок БЛ в задаче (зачеркнула `Promotion.*`, добавила `PromocodeTemplate.Save` и `PromoCode.Create`) и написала, что это "пока не окончательный вариант", собирает совещание с Матюшевым и Омельяненко на 06.10. Итогов совещания в задаче нет.
- Алябушев: "бэк брать на 0,5 и в критерии только техрешение". Это про его команду (Матюшев), не про нас. У нас пункт плана Федько на октябрь, критерий "В 26.6100 согласно требованиям", исполнители Лебедева, Омельяненко, Тимошенко; по словам Тимошенко, на него 2 дня. То есть от нас нужен код, а не только ТР.
- Фронт вкладки ещё на брендбуке: `client/LoyaltyOnline/PromoCode/Form/_design/View.tsx` берёт `DesignData` и рисует `BrandbookEditor`.

Текущая редакция БЛ от Ютман:
- `PromocodeTemplate.Save` под фичей: для нового дизайна инициализировать `ViewDetails` тем же хелпером, что у типа ДК (баннер, логотип, название), и сохранять `SiteId`.
- `PromoCode.Create` под фичей: в запись добавить `SiteId` (на создании null) и `TemplateId` (результат `PromocodeTemplate.Save`).
- "Promotion.Update" (по смыслу `PromoCode.Update`): передавать `SiteId` в `PromocodeTemplate.Save`.

## Редакция постановки на 26.10

После совещания по ТР Лебедева обновила текст задачи (сообщение 26.10 10:40).

- Фронт: на вкладке Дизайн встраивают упрощённый конструктор `SitesEditor/editorConnected:Editor`, данные грузятся при переходе на вкладку (загрузка без pagex).
- `PromocodeTemplate.Save`: под `dc_design_new` для нового дизайна заполнить `ViewDetails` (баннер, логотип, название) тем же хелпером, что у типа ДК. Подробности велено уточнять у Тимошенко.
- `PromoCode.Create` и `PromoCode.Read`: поле `SiteId` (UUID|null) в записи. `PromoCode.Update`: сохранять `SiteId`.
- `TemplateId` из постановки убран. `SiteId` описан на верхнем уровне записи промокода, а не внутри `DesignData`, как у ДК.
- Вопросы в тексте задачи: можно ли не создавать блоки обратной стороны; как внедряем; почему нет переключения QR/штрихкод; почему нет чипсов (кешбэк и т.п.), хотя в редактировании блоков они есть.
- Не сказано: старые промокоды без `SiteId`, франшиза, эл. образы, удаление сайта.

### Договорённости совещания (заметки Тимошенко, 26.10)

- **`PromoCode.Create`**: создание дизайна на брендбуке остаётся. Фича не развилка, а дополнительные действия поверх: брендбук инициализируется всегда, чтобы при резком выключении фичи ничего не сломалось. `SiteId` просто добавляем в формат. `TemplateId` не нужен.
- **`PromoCode.Read`**: добавить `SiteId`.
- **`SiteId` кладём в `DesignData`** (как у ДК).
- **Начальный дизайн**: только название, логотип и баннер.
- **Старые промокоды без `SiteId`**: будет конвертация (отдельный этап).

Сверка с текстом задачи: совпадает по `TemplateId`, начальным блокам и `SiteId` в Create/Read/Update. Расходится или не записано в задаче: в задаче `SiteId` «в рекорд», без `DesignData`; нет условия, что брендбук создаётся и под фичей; нет конвертации старых промокодов.

**Следствие для ТР выше:** пункты «под фичей не читать брендбук» в `create_design` и «выбросить `ThemeData`» в `PromocodeTemplate.Save` противоречат договорённости. Под фичей брендбук пишем как раньше и дополнительно заполняем `ViewDetails` и `SiteId`. Остаётся проверить, что СДК не перезапишет `ViewDetails` из брендбука при сохранении с `ThemeData` (у ДК именно поэтому `ThemeData` обнуляли).

## Как дизайн промокода устроен сейчас

Код `origin/rc-26.6100`, `www/service/Модули/PriceFormation.Online/priceformationonline/`.

- **Хранение.** Шаблон промокода живёт в той же таблице СДК `CardTemplate`, что и шаблон ДК: `CardTypeID` = ид типа промокода в онлайне (`ВидКарты`). Оформление лежит в брендбуке (аспект `9503bacf-...`, ключ `{ClientID}_{PromocodeTypeID}_{@Template}`). `ViewDetails` для промокода СДК не заполняет.
- **`PromoCode.Create`** (`loyaltyprograms/promocode/create.py:154`) -> `PromoCodeData.create_design` (`promocode/core/core.py:531`): `PromocodeTemplate.Save({PromocodeTypeID})` создаёт шаблон в СДК, затем читается `ThemeData` из брендбука и дополняется логотипом, баннером и названием ТП. На фронт уходит `DesignData {@Template, PromocodeTypeID, ThemeData}`. Ошибка проглатывается в `WarningMsg`, промокод создаётся без дизайна.
- **`PromoCode.Read`** (`promocode/read.py:197-215`) -> `get_sale_point_design` -> `PromocodeTemplate.Read` (+ `ThemeData`). Недоступность сервиса -> `Errors.DesignError`. Участник франшизы получает только превью.
- **`PromoCode.Update`** -> `PromoCodeData.save_data` (`core.py:394-411`) -> `PromocodeTemplate.Save(DesignData)`; ошибка тоже только в лог.
- **`PromocodeTemplate.Save`** онлайна (`discountcard/promocodetemplate/save.py`): прокси в СДК, затем `ThemeManager.Update` и обновление эл. образов, только если есть `ThemeData`.
- **СДК `PromocodeTemplate.Save`** (`dcservice/online/promocodetemplate/save.py` -> `cardtemplate/save.py: save_template_in_bb`) умеет только создать шаблон или обновить `Info`. `ViewDetails` и `SiteId` он **не пишет**.
- **СДК `PromocodeTemplate.Read`** (`ReadPromocodeBBImpl`) читает шаблон тем же SQL, что `CardTemplate.Read` (в нём уже есть `SiteId`), но в `RESULT_FORMAT` `SiteId` **нет**. В контракте `Online.orx` тоже нет.
- **Удаление** (`promocode/safe_delete_core.py:95-102`): `PromocodeTemplate.Delete` по типам промокодов. Сайт в конструкторе никто не удаляет, ни у промокодов, ни у ДК (на бэке вызовов `Site.*` нет вообще).
- **Копирования** у промокода нет (`PromoCode.Copy` не существует).

## Как это сделано у ДК (образец)

- Сайт создаёт конструктор на фронте при первом сохранении, бэк хранит только `CardTemplate.SiteId` (`record.set('SiteId', result.siteId)` в `_createDialog/View.tsx:130`).
- Начальные значения: `init_design_template(template_id, card_type_id)` в `discountcard/discountcarddesign/card_design.py` пишет `build_view_details()` через СДК `CardTypeTemplate.Update` и намеренно не шлёт `ThemeData`.
- `SiteId` сохраняется тем же `CardTypeTemplate.Update` (`save_design_site_id_in_sdc`, `discountcardtype/helpers.py:324`) или вместе с записью в `DiscountCardTemplate.Save`, где под фичей `ThemeData` обнуляется, чтобы СДК не пересобрал `ViewDetails` из брендбука.
- Страница Дизайн ДК на фронте: если у записи есть `SiteId`, открывается конструктор с ПО `LoyaltyCardDesign` по `@Template`; если нет, а есть `ThemeData`, старый редактор брендбука (`RegistryNew/Design/PrefetchConfig.ts`).

**Важно:** СДК `CardTypeTemplate.Update` не завязан на дисконтные карты: это декларативное обновление строки `CardTemplate` с проверкой, что `CardTypeID` совпадает с шаблоном. Для шаблона промокода он работает так же, если не передавать `IsActive`. ПО `LoyaltyCardDesign.Read/Write` тоже работает с любой строкой `CardTemplate` по `@CardTemplate`. Значит хранение промокода на конструкторе в СДК уже есть, нужен только онлайн-код и чтение `SiteId`.

## Техническое решение (предлагаемое)

Всё под `dc_design_new`. Без фичи поведение не меняется.

1. **`PromocodeTemplate.Save` (онлайн)** — зона Тимошенко.
   - Выбросить `ThemeData` из записи (как в `DiscountCardTemplate.Save`).
   - Если `@Template` не передан (новый дизайн): после создания шаблона в СДК записать начальные `ViewDetails` через `init_design_template`. Для промокода без блоков `Кэшбэк`/`Ваши бонусы`: у промокода нет баланса и кешбэка. Нужен параметр у `build_view_details` / `init_design_template` (например, `with_blocks=False`) или свой набор блоков (вопрос к Лебедевой/Ютман).
   - Если в записи есть `SiteId`: сохранить его через `CardTypeTemplate.Update` (`@Template`, `CardTypeID`, `ClientID`, `SiteId`), как `save_design_site_id_in_sdc`. Можно объединить с записью `ViewDetails` в один вызов.
   - Обновление эл. образов (`_update_pc_passes`) сейчас идёт только при `ThemeData`. Под фичей его не будет, как и у ДК (TODO в `LoyaltyCardDesign.Write`).
   - Контракт `DiscountCard.orx`: поле `SiteId` (UUID) в параметре `Template`.
2. **`PromocodeTemplate.Read` (онлайн + СДК)**: вернуть `SiteId`.
   - Вариант А (рекомендую): в СДК добавить `SiteId` в `ReadPromocodeBBImpl.RESULT_FORMAT` и в контракты `PromocodeTemplate.Read` / `ReadByIdentifier`. Одна строка кода, SQL уже отдаёт поле.
   - Вариант Б: без правки СДК читать `SiteId` в онлайне через СДК `CardTemplate.Read(PromocodeTypeID)`. Это лишний вызов в СДК на каждом открытии промокода, у франшизы надо отдельно разбираться с UUID.
   - Под фичей при наличии `SiteId` можно не читать брендбук (`ThemeManager.Read`). Это оптимизация, не обязательно.
   - Если шаблона нет, сейчас возвращается заготовка брендбука (`get_minimal_draft`) без `@Template`. Конструктору нужен `@Template`, поэтому под фичей лучше создавать шаблон (как в `create_design`). Вопрос к фронту.
3. **`PromoCode.Create / Read / Update`** — тоже делаем мы (09.10: задача в плане на Тимошенко). В orx ответственный Алябушев, Матюшев задавал вопросы по постановке, поэтому ревью, видимо, через них.
   - `Create`: `create_design` под фичей не читает брендбук, кладёт в `DesignData` `@Template` и `SiteId = None`. Инициализация `ViewDetails` происходит внутри `PromocodeTemplate.Save` (п. 1).
   - `Read`: `DesignData.SiteId` из `PromocodeTemplate.Read`.
   - `Update`: ничего не менять в коде, `DesignData` уже уходит в `PromocodeTemplate.Save` целиком. Но в контракте `DesignData` (`LoyaltyPrograms.orx`: Create ~7564, Read ~9362, Update ~9894) добавить `SiteId`, а у `ThemeData` снять `is_required="1"`.
   - Ошибки: оставить как есть. Создание промокода не блокировать, недоступность СДК на чтении отдавать в `Errors.DesignError`. Отдельное поле не нужно: сайт создаёт фронт, бэк в сервис сайтов не ходит.

## Что нужно фронту (Лебедева)

- `PromoCode.Create/Read`: `DesignData.@Template` (это и есть `TemplateId` из постановки, ид ПО `LoyaltyCardDesign`) и `DesignData.SiteId` (UUID|null).
- Конструктор при первом сохранении создаёт сайт и кладёт его ид в `DesignData.SiteId`. Дизайн пишет сам через `LoyaltyCardDesign.Write`. `PromoCode.Update` -> `PromocodeTemplate.Save` сохраняет `SiteId`.
- `ThemeData` под фичей не слать (бэк всё равно выбросит).
- Чипсы и подстановки для промокода: какие инфоблоки разрешены (раньше `CLIENT`, `END_DATE`, `CUSTOM`), бонусных подстановок быть не должно.

## Открытые вопросы

- **Ютман / Матюшев / Омельяненко**: итог совещания 06.10. Где поля: `SiteId`/`TemplateId` на верхнем уровне записи промокода (как в постановке) или внутри `DesignData` (как у ДК и как удобнее, потому что `DesignData` целиком уходит в `PromocodeTemplate.Save`)? (Кто делает: всё на Тимошенко, снято 09.10.)
- **Лебедева / Ютман**: начальные блоки дизайна промокода. Только название, логотип и баннер или ещё "Срок действия" / "Клиент"?
- **Ютман**: старые промокоды без `SiteId`. Остаются на брендбуке до этапа конвертации? У старых шаблонов `ViewDetails` пустой, а СДК `LoyaltyCardDesign.Read` делает `**view_details` без проверки на `None`. Если фронт откроет конструктор для старого промокода, чтение ПО упадёт. Нужно либо не открывать конструктор без `SiteId`, либо `or {}` в СДК.
- **Франшиза**: участник видит дизайн владельца (`ReadByIdentifier`), а `LoyaltyCardDesign.Read` отказывает в чтении чужого шаблона. Плееру на стороне участника нужны данные ПО. Тот же вопрос, видимо, открыт и для ДК.
- **Эл. образы**: генерация образов СДК читает `ViewDetails` в старом формате (`dccore/cardtemplate/entity.py: from_db`), формат конструктора она не понимает. Это общая дыра проекта (этап "конвертация данных сайта для мобильных устройств"), но для промокода её стоит явно назвать QA.
- **Удаление**: сайт в конструкторе при удалении промокода остаётся. У ДК так же. Нужна ли чистка?

## Новое на 27.10: сайт создаёт бэк

- **Лебедева, 26.10 14:43:** «Нужно всё-таки создавать и записывать сайт в SiteId в Update для новой записи». Шаблон сайта пока `94345145-2493-428e-bf2b-dee75f09e962` (тот же, что у ДК, на фронте `DesignConstructor/Constants.ts: AW`), потом сделают отдельный. Кузаков 26.10: разные шаблоны сайта для ДК и промокода - так и нужно.
- **Как другие сервисы создают сайт на бэке:** копией шаблона, `sbis.Frames.Copy(Record({'Ids': [ид шаблона], 'Version': ...}))`, в ответе словарь «ид шаблона -> ид нового сайта» (crm/wificonnect `wifi_sites/sites.py: create_site`, sabyget `sgc_sites/base.py`, composite-sales через `EndPoint('online')`). У нас вызовов `Frames.*` пока нет.
- **«Новая запись» в Update:** у промокода после `Create` черновик, в `update.py` уже есть проверка `old_promo_code_record.Get('Draft')` (история). Её можно взять признаком первого сохранения.
- **Риск с `ThemeData` снят:** СДК `PromocodeTemplate.Save` (`save_template_in_bb`) пишет только `Info`, `ViewDetails` не трогает; обработчик изменения брендбука `CardType.HandleChangeThemeData` тоже `ViewDetails` не сохраняет. Значит брендбук под фичей можно писать как раньше, начальные `ViewDetails` он не затрёт.
- **`SiteId` в чтении:** СДК `ReadPromocodeBBImpl.RESULT_FORMAT` поля не отдаёт (SQL его уже читает) - нужна правка в discount-cards либо отдельное чтение `CardTemplate.Read` из онлайна.
- Хелперы ДК для переиспользования: `card_design.build_view_details` (возвращает и блоки Кэшбэк/Ваши бонусы - промокоду не нужны), `init_design_template`, `discountcardtype/helpers.save_design_site_id_in_sdc` (через `CardTypeTemplate.Update`).

## Решения 27.10 (Тимошенко)

- Ид шаблона сайта - константа на бэке `PROMOCODE_SITE_TEMPLATE_ID` (пока шаблон ДК), сменим, когда Лебедева сделает отдельный.
- `SiteId` при чтении - вариант А: правка СДК `PromocodeTemplate.Read`/`ReadByIdentifier`.
- Сайт создаём только при первом сохранении (старая запись `Draft`). Если `Frames.Copy` упал - `WarningMsg`, `SiteId` пустой, фронт открывает брендбук; повторно не создаём. Брендбук поддерживаем, пока фичу не откроют всем.
- Начальный дизайн: только название, логотип, баннер (`build_view_details(with_blocks=False)`).
- price-formation работает в сервисе online, `Frames` вызываем напрямую, без `EndPoint('online')`.

## Реализация (27.10, не закоммичено)

- **price-formation**, `D:/dev/pf-26.61`, ветка `26.6100/feature/aatimoshenko/09234630` (перемотана на `rc-26.6100` 27.10): параметр `with_blocks` у `build_view_details`/`init_design_template`; онлайн `PromocodeTemplate.Save` под фичей заполняет `ViewDetails` нового шаблона и пишет `SiteId` через `CardTypeTemplate.Update`; `PromoCodeData.save_data` -> `_create_design_site` (копия шаблона при первом сохранении); `create_design` отдаёт `DesignData.SiteId = None`; контракты: `SiteId` в `DesignData` Create/Read/Update, в параметре `PromocodeTemplate.Save` и в ответе онлайн `PromocodeTemplate.Read`.
- **discount-cards**, `D:/dev/wt09234630-sdk`, та же ветка: `SiteId` в `ReadPromocodeBBImpl.RESULT_FORMAT` и в `Online.orx` (Read, ReadByIdentifier), 2 теста.
- Тесты: price-formation 26 новых и затронутых + регрессия промокодов, шаблонов и типов ДК - OK; СДК `test-core-and-service` 1355 OK. pylint 10/10.
- В тестовом проекте нет `sbis.Frames` - в тестах подменяем объект целиком (`patch('sbis.Frames', create=True)`).
- Тесты `promocode/update.py` и `discountcardtype/create.py` при запуске по папке не грузятся (импорт `tests_priceformationonline.*`), к задаче не относится; гонять с `tests/` в `PYTHONPATH`.

## Пожелание 27.10: выбор QR/штрихкод на дизайне

- **Лебедева, 27.10 12:40** (после двух звонков с Тимошенко и Ютман): поддержать выбор QR/штрихкод на дизайне. Выбран штрихкод: если номер промокода в штрихкод не кодируется, формируем QR, иначе штрихкод. Выбран QR: всегда QR. Предыстория: переключатель убрали по ошибке; Михель против того, чтобы оставлять тип без проверки, потому что не каждый промокод можно закодировать штрихкодом (например, кириллица).
- **Где выбор уже хранится:** ПО `LoyaltyCardDesign.BarcodeType` (enum: 0 штрихкод, 1 QR, по умолчанию 0), пишется в `ViewDetails` шаблона. Наш начальный дизайн (`build_view_details`) тип не заполняет.
- **Что сейчас показывает покупателю тип кода:** СДК SabyGet `promocode/get.py`, `get_list.py` берут тип из `CardType.Info.CodeType` (тип генерации номеров выпуска, по умолчанию `qrcode`), а не из дизайна. В онлайне тип генерации живёт в `NumberFormat.CodeType`/`BarcodeType` (`qr`/`ean8`/`ean13`); ссылка на картинку `get_qr_link_by_code` всегда QR.
- Открыто, кто и где применяет правило: превью в редакторе (фронт), карточка промокода у покупателя (SabyGet, СДК), эл. образы. И какой штрихкод (Code128?) и проверка «кодируется ли номер».
- **Как сейчас у покупателя (проверено по коду СДК):** SabyGet `promocode/get.py`, `get_list.py`, `read.py` берут тип из `CardType.Info.CodeType` (`qrcode`/`ean8`/`ean13`, по умолчанию `qrcode`); на МУ картинку собирает СДК (`Barcode.GenerateToRpc`, поле `CodeImage`), в вебе фронт получает `TypeBarCode`. GPay для промокода по умолчанию QR, для карт Code128 (`pass_/gpay/core/card/get_pass_data.py`). Code128 у промокодов не используется.
- **Кириллица:** может быть в любом промокоде (ручной ввод у индивидуальных и партнёрских, русские буквы в генерации у активности, префикс). Заранее по типу промокода не определить, проверять только конкретный номер при показе.
- **Ответы Лебедевой 27.10 13:21** (диалог с Тимошенко): штрихкод на дизайне = Code128, как у ДК; для EAN-эмиссий тоже решает выбор на дизайне (штрихкод или QR); по умолчанию в новом дизайне штрихкод; показ у покупателя (SabyGet, эл. образы) - «у Юры смежная задача, если он не делает - оценить, влезет - делаем здесь, нет - отдельной задачей».
- `BarcodeType` в `ViewDetails` хранится плоским ключом (0 штрихкод, 1 QR); если ключа нет, ПО читает `None`, не 0. Значит «по умолчанию штрихкод» надо явно писать в начальный дизайн.
- Задачу Кузакова по показу промокода у покупателя в проекте не нашли (этап «11 Карты в сабигет» - только ДК; эл. образы - этап «Конвертация дизайна для AppleWallet и GPay», Омельяненко).


## Состояние

07.10: собран контекст, ТР выше. Заготовку кода не делал: постановка БЛ "не окончательная" (Ютман 05.10).
09.10: уточнено, что вся БЛ задачи на нас (`PromocodeTemplate.*`, `PromoCode.*`, СДК), пункт плана "В 26.6100 согласно требованиям", 2 дня. Слова Алябушева про "только ТР" относились к его команде. Ветка по плану `26.6100/feature/aatimoshenko/09234630` от `origin/rc-26.6100`. Объём правки в нашей зоне небольшой: `PromocodeTemplate.Save` (+ контракт), параметр блоков у `build_view_details`, `SiteId` в СДК `PromocodeTemplate.Read`.
26.10: прошло совещание по ТР, Лебедева обновила постановку (раздел «Редакция постановки на 26.10»). `SiteId` на верхнем уровне записи, `TemplateId` убран. Заметки совещания сверены: `SiteId` в `DesignData`, брендбук создаётся и под фичей. Дальше попросить Лебедеву дописать это в задачу и проверить, не затрёт ли СДК `ViewDetails` при сохранении с `ThemeData`, затем код.
27.10: начали работу. Лебедева попросила создавать сайт на бэке в `PromoCode.Update` для новой записи (раздел «Новое на 27.10»). Риск с затиранием `ViewDetails` брендбуком проверен - его нет. Перед ТР заданы вопросы Тимошенко: шаблон сайта, `SiteId` в чтении через СДК, поведение при ошибке копирования, блоки.
27.10 (позже): ТР согласовано, код и тесты готовы в обеих ветках, не закоммичены. Дальше: коммит по одобрению, MR в price-formation и discount-cards (одна веха 26.6100), сообщить Лебедевой поля `DesignData.SiteId` и что сайт создаёт бэк; проверить `Frames.Copy` на стенде.
27.10 (вечер): пришло пожелание Лебедевой по QR/штрихкоду (раздел выше). Код по основной части не закоммичен; перед доработкой заданы вопросы Тимошенко о месте правила.
27.10 13:21: Лебедева ответила по QR (Code128, по умолчанию штрихкод, покупатель - через задачу Кузакова или оценку). Дальше: `BarcodeType: 0` в начальный дизайн промокода; найти задачу Кузакова или оценить показ у покупателя (СДК SabyGet + эл. образы).
