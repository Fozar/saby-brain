---
type: concept
title: "LoyaltyReferral и ТЗ рефакторинга: сверка области «Реферальная программа сделок»"
created: 2026-10-06
updated: 2026-10-23
status: developing
tags:
  - referral-program
  - price-formation
  - module-architecture
  - refactoring
related:
  - "[[LoyaltyReferral-Module-Extraction]]"
  - "[[Мусохранов-Андрей-Владиславович]]"
---

# LoyaltyReferral и ТЗ рефакторинга: сверка области «Реферальная программа сделок»

Поручение №09152329 ([ссылка](https://online.sbis.ru/opendoc.html?guid=01a0a3b2-c8b9-742c-88a7-d6c2e799f0e5&client=3)) от Голубя Ф.С. от 15.09.2026. Исполнитель Тимошенко, проверяет Голубь, срок 31.10.2026. Текст поручения: модуль готов, проверить, что он соответствует ТЗ проекта, и согласовать с Мусохрановым. Отдельный пункт рефакторинга: на уровне корневого python-пакета модуля выделить `core` и `helpers` (пакетами или сразу модулями). Критерий приёмки: границы согласованы с Мусохрановым, инструкция по переносу передана.

Поручение входит в этап «Выделение функциональной области "Реферальная программа сделок"» (план на декабрь 2026) проекта «[Технический] Рефакторинг backend модулей лояльности» ([проект](https://online.sbis.ru/opendoc.html?guid=8ee7a761-acf9-4006-846d-34d9584ae850&client=3), руководитель Мусохранов, срок 31.01.2027). Проект разносит лояльность по модулям `Loyalty*`, у каждой функциональной области (ФО) свой модуль, ответственный и API. В итоге `PriceFormation.Common/Online/Offline` должны быть удалены.

В том же этапе есть задача Голубя №09081016 «Перенести функционал области "Реферальная программа сделок" в новые модули» ([ссылка](https://online.sbis.ru/opendoc.html?guid=01a07f0d-8542-7890-8df5-f6708122e685&client=3)): срок 31.12.2026, веха 27.1100. На 07.10 в ней только заголовок, переписки нет. Порядок по ТЗ: в поручении ответственный за ФО разбирает код и согласует границы, перенос делается после согласования. У самого поручения вехи нет.

## Что требует ТЗ

ТЗ лежит в файлах проекта («Техническое задание», `.sabydoc`). Текст достаётся парсингом `index.site` из zip: штатный конвертер теряет форматированные фрагменты.

**Раздел 6.0.13.** ФО уже выделена в модуль БЛ `LoyaltyReferral`, его нужно привести к требованиям раздела 6.0.1. Целевое имя модуля `LoyaltyRefProgramOnline`, пакет `loyaltyrefprogramonline/`.

**Раздел 6.0.1 (общие правила):**
- имя модуля с префиксом `Loyalty`, контейнеры внутри модуля без него;
- python-пакеты раскладываются так: контейнер, внутри объект БЛ, внутри файл метода; имена методов и объектов БЛ не меняются;
- на любом уровне ниже корня пакета можно заводить `core`, `helpers`, `const`;
- синхронизация конкретных сущностей живёт рядом со своей ФО;
- последний шаг выделения: «Декларация API модуля БЛ - в s3mod описать API модуля». Формат не задан;
- если другая ФО использует код переносимого модуля, этот код оформляется как API и вызывается через него;
- к концу работ не должно остаться зависимостей, которые мешают удалить `PriceFormation.*`.

Раздел 6.3 «Описание API» содержит только «Без изменений». Это про методы БЛ, к s3mod он отношения не имеет.

## Сверка модуля (ветки rc-26.6100 и rc-26.6200, модуль в них одинаковый)

**Совпадает с ТЗ:** контейнер `ReferralProgram.orx` (объекты `ReferralProgram` и `sabyReferralProgram`, около 50 методов), пакет `loyaltyreferral/referralprogram/referralprogram/<метод>.py` и `saby_referralprogram/`, по одному файлу на метод. Обработчики событий (`on_event.py`: `Lead.StateChanged`, `salessources.source_changed`), история (`ReferralProgram.hox`), права (`.rlx`, `.uax`) уже в модуле. В s3mod ответственный Тимошенко, компонент тот же, что у `PriceFormation.Online`.

**Расходится:**
1. Имя: `LoyaltyReferral` / `loyaltyreferral` вместо `LoyaltyRefProgramOnline` / `loyaltyrefprogramonline`.
2. В папке объекта `referralprogram/referralprogram/` кроме файлов методов лежат шесть служебных модулей: `core.py` (688 строк), `helpers.py` (122), `stub_helpers.py` (251), `get_stats_helpers.py` (429), `program_history.py` (444), `stub_history.py` (196). Поручение просит поднять core и helpers в корень пакета.
3. В s3mod нет описания API.
4. 19 модулей `priceformationcommon` / `priceformationonline` импортируются в 54 из 60 python-файлов модуля (таблица ниже).
5. В `PriceFormation.*` остался код, который нужен только рефералке сделок (ниже, раздел про границы).

**Снято при проверке:**
- `DeveloperScript.orx`, `developer_script.py` и пустой `fix_cloud_clients` в корне модуля в git не отслеживаются: это локальные остатки ВНР.
- Виджеты `PriceFormation.Online/ui/Referral/` и `ui/ReferralLead/`, пакет `priceformationonline/loyaltyprograms/referralbonus/`, `PriceEntityType.REFERRAL_BONUS`, `ReferralActionType` относятся к реферальной бонусной программе (другая ФО), не к сделкам.

**Про API в s3mod.** Ни в одном из 21 s3mod репозитория блока API нет. Блок `<externals>` есть только у `PriceFormation.Common/Online/Offline`, и в нём наоборот перечислены чужие методы, которые модуль вызывает сам. Python-код `loyaltyreferral` снаружи никто не импортирует (grep по репозиторию и saby-search по rc-26.6100: имя модуля встречается только в своём s3mod, двух тестовых `Service.s3srv` и боевом `online/inside: online-inside/s3srv/bl/online32.s3srv`). Значит API модуля сейчас только методы `ReferralProgram.*`.

## Согласование с Мусохрановым

Вопросы отправлены 06.10.2026 в обсуждение поручения:
1. Переименование в `LoyaltyRefProgramOnline` делать в задаче на перенос у Голубя?
2. Зависимости от `PriceFormation.Common/Online` переключаем, когда появится общий модуль `Loyalty[Common/Online]`?
3. Что значит «в s3mod описать API модуля», где и в каком виде это описывать?

**07.10 ответа нет.** Проверено: обсуждение и лента поручения (одно сообщение, наше), задача №09081016 (пустая), диалоги с Мусохрановым, поиск по диалогам и встречам: «реферал», «core helpers», «LoyaltyRefProgramOnline», «s3mod API». Последнее от Мусохранова по рефералке: 01.10 приём пункта плана про объединение `GetSabyBankPartners` и `GetPartners`, к поручению не относится.

## Границы ФО (предложение)

В область входит всё, что сейчас лежит в `LoyaltyReferral`. Кроме того, в `PriceFormation.*` есть код, которым пользуется только рефералка сделок. По правилу 6.0.1 (после выделения `PriceFormation.*` удаляются) его стоит забрать в модуль:

| Что | Где сейчас | Кто использует |
|---|---|---|
| `CloudStatsReferralAction`, `_REFERRAL_ACTION_CONTEXTS`, `send_referral_program_to_cloud_statistics`, значения `CloudStatsFunctional.REFERRAL_PROGRAM*` и `CloudStatsContext.LEAD/REFERRAL_LEAD` | `PriceFormation.Online/priceformationonline/core/statistics.py` (стр. 95-120, 252-283, 597-625) | только 7 файлов модуля |
| `add_ad_objects_to_referral_code` | `PriceFormation.Online/priceformationonline/helpers/marketing.py:134` | только `update.py` модуля |
| фича `ref_deals_convert` (`Feature.REF_DEALS_CONVERT`) | `PriceFormation.Common/priceformationcommon/helpers/feature.py:36`, объявление в `PriceFormation.Online/PriceFormation.feature:16` | только `get_lead_period_list.py`, `get_partner_list.py`, `get_stats_helpers.py`; фича временная, можно не переносить, а дождаться удаления |
| `Feature.REFERRAL_TEST`, `Feature.REFERRAL_BANK` | `feature.py:22, 35`, `PriceFormation.feature:20, 24` | в Python никто не использует, кандидаты на удаление |

Остаётся общим (рефералка только читает): значения перечислений общих таблиц `PriceEntityType.REFERRAL_LEAD = 37`, `ItemType.REFERRAL_LEAD`, `ItemNumberType.REFERRAL_CODE`, `LinkType.REQUEST_*` в `price_entity_sale_doc.py` (по этому классу ещё 14 файлов других ФО). Таблицы `ВидЦены`, `ВидЦеныДокумент`, `Карта` своих `.dicx` в модуле не получают.

## Инструкция по переносу (черновик для Голубя)

### Можно делать сейчас (прямо следует из поручения и ТЗ)

**Шаг 1. Поднять core и helpers в корень пакета** (делает Тимошенко в рамках поручения, после ответа по вопросу 1). Методы, `.orx`, `.hox` не трогаем: в `ReferralProgram.orx` нет ни одного импорта служебных модулей, только файлы методов. Варианты раскладки:

- **А. Минимальный.** `core.py` и `helpers.py` переезжают в `loyaltyreferral/core.py` и `loyaltyreferral/helpers.py`, остальные четыре служебных модуля остаются в папке объекта. Плюсы: мало правок (импорт `core` в 42 файлах, `helpers` в 4). Минусы: в папке объекта остаются файлы, которые не являются методами.
- **Б. Пакет core (рекомендую).** `loyaltyreferral/core/` с модулями `referral_program.py` (бывший `core.py`), `stub.py` (`stub_helpers.py`), `stats.py` (`get_stats_helpers.py`), `program_history.py`, `stub_history.py`; `loyaltyreferral/helpers.py` (бывший `helpers.py`, там только форматирование ссылок, дат и денег). Плюсы: в папке объекта остаются только файлы методов, как требует 6.0.1. Минусы: больше правок (импорты в 44 файлах модуля, 61 путь в моках тестов).

Что поправить при переносе (по rc-26.6100):
- импорты внутри модуля: `...referralprogram.core` в 42 файлах, `.stub_helpers` в 7, `.program_history` в 6, `.stub_history` в 5, `.helpers` в 4, `.get_stats_helpers` в 3;
- пути в `patch(...)` тестов `tests/tests_loyaltyreferral/referralprogram/referralprogram/`: `core` 47 мест в 21 файле, `stub_helpers` 9 в 4, `program_history` 3 в 2, `stub_history` 2 в 2;
- тестовые файлы `stub_helpers.py`, `program_history.py`, `stub_history.py` переложить вслед за модулями (`tests/tests_loyaltyreferral/core/`), симлинк `tests_new/online/src/tests_loyaltyreferral` при этом не меняется.

**Шаг 2. Забрать из `PriceFormation.*` код, нужный только рефералке** (таблица в разделе про границы): статистика рефералки и `add_ad_objects_to_referral_code` переезжают в `core` модуля, в `PriceFormation.Online` их удалить.

### Отложено по ответу Мусохранова (12.10)

Ответы получены: переименование и развязка импортов делаются отдельными задачами, API в s3mod пока только выделяем. В рамках поручения остаётся шаг 1.

**Шаг 3. Переименование в `LoyaltyRefProgramOnline`** (вопрос 1: кто и когда). Объём: имя в s3mod (id модуля прежний), папка модуля и пакета, ~50 импортов в телах `ReferralProgram.orx`, все импорты пакета, папка тестов `tests/tests_loyaltyreferral` и симлинк в `tests_new/online/src/`, имя в `tests_new/online/clouds/Online/Service.s3srv` и `tests_new/online_with_discount_core/clouds/OnlineWithDiscountCore/Service.s3srv`, отдельной доброской имя в `online/inside: online-inside/s3srv/bl/online32.s3srv`. Если переименование будет, шаг 1 лучше делать до него или в той же ветке, чтобы не править пути дважды.

**Шаг 4. Развязать импорты из `PriceFormation.*`** (вопрос 2: куда и когда). Полный список на rc-26.6100 (RP = `loyaltyreferral/referralprogram/referralprogram/`):

Инфраструктура, кандидат в `Loyalty[Common]`:

| Модуль | Что берётся | Файлов |
|---|---|---|
| `priceformationcommon.helpers.logging` | `logging`, `log`, `warning` | 49 (почти все) |
| `priceformationcommon.helpers.common` | `to_uuid` | 23 |
| `priceformationcommon.helpers.assert_param` | `assert_param`, валидаторы | 15 (+ `saby_referralprogram/create_lead.py`) |
| `priceformationcommon.helpers.record` | `create_record*`, `set_table` | 7 |
| `priceformationcommon.helpers.dict_utils` | `deepget`, `to_json` | 4: RP/core, delete, update, calculate_visitor_price |
| `priceformationcommon.helpers.money` | `to_money`, `to_decimal` | 4 |
| `priceformationcommon.helpers.feature` | `Feature`, `check_feature` | 3: get_lead_period_list, get_partner_list, get_stats_helpers |
| `priceformationcommon.helpers.wrappers` | `handle_exceptions` | 2: handle_lead_state_changed, handle_source_changed |
| `priceformationcommon.helpers.lock` | `advisory_lock` | 1: create_stub |
| `priceformationcommon.core.cursor_navigation` | `NavField`, `get_list_by_cursor`, `add_cursor_params` | 4: get_list, get_partner_list, get_lead_period_list, get_stub_list |
| `priceformationcommon.core.types` | `Money`, `RecordType` | 2: handle_lead_state_changed, program_history |
| `priceformationcommon.core.history_object` | `HistoryObject`, `Action` | 2: program_history, stub_history |

Общие сущности лояльности (перечисления общих таблиц, общий модуль):

| Модуль | Что берётся | Файлов |
|---|---|---|
| `priceformationcommon.core.price_entity` | `PriceEntityType`, `PriceEntityState`, `ClientType` | 10 |
| `priceformationonline.core.price_entity_sale_doc` | `LinkType` | 12 |
| `priceformationcommon.discountcard.emission.const` | `ItemNumberType`, `ItemType` | 4: core, create, create_stubs_for_existing_leads, join |
| `priceformationcommon.core.doc` | `Doc`, `Type`, `w_doc` | 2: create_invoice, handle_lead_state_changed |

Код других ФО, по ТЗ вызывать через их API:

| Модуль | Что берётся | Файлов | Чья область |
|---|---|---|---|
| `priceformationonline.helpers.business_group` | `BusinessGroup`, `MemberStatus`, `BusinessGroupRole`, `Socnet`, `PriceEntityBusinessGroupFolder` | 16 | бизнес-группы / агентские сети |
| `priceformationonline.loyaltyprograms.loyaltyprogram.agent_group` | `agent_group_decorator` | 7: get_list, get_lead_list, get_lead_period_list, get_joinable_list, get_stats, get_stub_list и др. | агентские сети |
| `priceformationonline.helpers.marketing` | обёртки над `SalesSources` (`get_or_create_source`, `get_source_detail`, `get_sales_sources_*`, ...) | 15 | общий (маркетинг, внешний сервис) |
| `priceformationonline.core.statistics` | статистика рефералки | 7 | переезжает к нам (шаг 2) |
| `priceformationonline.discountcard.discountcard.create_ecard` | `set_electronic_emission_range`, `ItemNumberRange`, `get_available_card_number` | 2: create, join | дисконтные карты |
| `priceformationcommon.discount.core.calcdiscount.apply` | `save_bonus_processing`, `BonusOperation` | 2: create_invoice, handle_lead_state_changed | расчёт скидок / бонусы |
| `priceformationcommon.discount.core.saledoc.doc` | `set_sale_state` | 1: handle_lead_state_changed | расчёт скидок |
| `priceformationcommon.discount.core.calcdiscount.preparedata.price_entity` | `get_image_info` | 3: get_list, get_stats, read | расчёт скидок |

После шага 4 в `<depends>` `LoyaltyReferral.s3mod` убрать `PriceFormation.Common` и `PriceFormation.Online` и поставить новые модули.

**Шаг 5. API в s3mod** (вопрос 3: формат). Готовых образцов нет. Если речь про перечень методов, которые модуль отдаёт наружу, это `ReferralProgram.*` и `sabyReferralProgram.CreateLead`; Python-кода модуля снаружи никто не импортирует.

## Состояние

- 07.10: ответа Мусохранова нет, поэтому подъём core/helpers не начат, ветки и worktree нет.
- Черновик инструкции для Голубя выше; передавать после ответа на вопросы 1-3.
- 12.10: Мусохранов ответил на все три вопроса. 1) переименование будет в рамках отдельной задачи 01a07f0d-8542-7890-8df5-f6708122e685, итоговое имя и нужен ли постфикс online ещё обсуждают; 2) переключение зависимостей с PriceFormation.Common/Online на общий модуль Loyalty - да, когда он появится; 3) API в s3mod: сейчас только выделяем API, оформление вторично.
- 23.10: ответа Голубю нет, ветки и worktree нет, `core`/`helpers` всё ещё в `referralprogram/referralprogram/`. Следующий шаг у Тимошенко: шаг 1 (подъём core и helpers в корень пакета, вариант Б), потом отчитаться Голубю до срока 31.10.
- 23.10: выбран вариант Б. Заведена подзадача №10231432 (https://online.sbis.ru/opendoc.html?guid=01a16751-ff54-7518-9113-fab46c720c88&client=3), срок 28.11. Сделано в worktree `D:/dev/wt09152329`, ветка `26.6100/feature/aatimoshenko/10231432` от `rc-26.6100`: в `loyaltyreferral/core/` лежат `referral_program`, `stub`, `stats`, `program_history`, `stub_history`, рядом `helpers.py`; тесты переложены в `tests/tests_loyaltyreferral/core/`. Импорты и пути в `patch` поправлены в 71 файле, статическая проверка путей чистая. Тесты не прогнаны: стенда под этот worktree нет, нужна сборка `tm -project online`. Не закоммичено, ждёт одобрения.

## Решения и открытые вопросы (23.10)

- Решение: раскладка по варианту Б (пакет `core/` плюс `helpers.py` в корне). Подзадача №10231432 заведена как отдельная, чтобы у рефакторинга был свой MR и своя ветка, а не правки внутри поручения.
- Решение: переименование модуля и развязку импортов от `PriceFormation.*` в этот MR не берём (ответ Мусохранова 12.10).
- Открыто: веха подзадачи и база ветки. У поручения вехи нет, взяли `rc-26.6100`, потому что на ней делался разбор; нужно подтвердить.
- Открыто: прогнать `tests_loyaltyreferral` после сборки стенда под `D:/dev/wt09152329`, затем коммит и MR после одобрения.
- После MR: отчитаться Голубю в поручении №09152329 (границы согласованы, core и helpers вынесены, переименование и зависимости отдельными задачами).
