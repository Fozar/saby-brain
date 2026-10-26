---
type: concept
title: "Карточка промокода, вкладка Дизайн: конструктор Дизайна ДК вместо брендбука"
created: 2026-10-07
updated: 2026-10-26
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

Заметки Тимошенко с совещания с текстом задачи ещё не сверены (26.10 заметок в вики и Obsidian не нашлось, запрошены у Тимошенко).

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

## Состояние

07.10: собран контекст, ТР выше. Заготовку кода не делал: постановка БЛ "не окончательная" (Ютман 05.10).
09.10: уточнено, что вся БЛ задачи на нас (`PromocodeTemplate.*`, `PromoCode.*`, СДК), пункт плана "В 26.6100 согласно требованиям", 2 дня. Слова Алябушева про "только ТР" относились к его команде. Ветка по плану `26.6100/feature/aatimoshenko/09234630` от `origin/rc-26.6100`. Объём правки в нашей зоне небольшой: `PromocodeTemplate.Save` (+ контракт), параметр блоков у `build_view_details`, `SiteId` в СДК `PromocodeTemplate.Read`.
26.10: прошло совещание по ТР, Лебедева обновила постановку (раздел «Редакция постановки на 26.10»). `SiteId` на верхнем уровне записи, `TemplateId` убран. Ждём заметки Тимошенко с совещания для сверки, затем решить место `SiteId` и начать код.
