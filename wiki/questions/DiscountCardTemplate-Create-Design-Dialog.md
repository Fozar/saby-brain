---
type: synthesis
address: c-000280
title: "DiscountCardTemplate.Create/Save — конструктор Дизайна ДК в диалоге создания дизайна"
created: 2026-09-10
updated: 2026-09-10
status: developing
tags:
  - loyalty
  - discount-cards
  - site-builder
  - price-formation
question: "Что доработать в БЛ price-formation, чтобы диалог создания Дизайна ДК открывался на новом конструкторе и сохранял его сайт?"
answer_quality: solid
related:
  - "[[DiscountCardType-Create-Design-Constructor]]"
  - "[[DiscountCard-Design-Constructor-Architecture]]"
  - "[[DiscountCard-Design-Constructor-Project]]"
  - "[[DiscountCard-Design-Constructor-WorkPlan]]"
  - "[[DiscountCard-Service-API]]"
  - "[[Ютман-Элина]]"
  - "[[Лебедева-Наталья]]"
---

# DiscountCardTemplate.Create/Save — конструктор Дизайна ДК в диалоге создания дизайна

Задача №06242714 (`019ef85f-f717-7757-b50e-4a057110edb5`), этап 5 проекта [[DiscountCard-Design-Constructor-Project|«Перевод дизайна дисконтных карт на конструктор»]], веха 26.5100 до 10.10.26. Соседняя по общему коду задача — [[DiscountCardType-Create-Design-Constructor]] (№06242691, диалог создания типа карты). Ветка `26.5100/feature/aatimoshenko/06242714` от `rc-26.5100`.

## Отдельного ТР нет: одно ТР на три задачи

Документ, на который ссылается Ютман 25.08 (`online.sbis.ru/shared/disk/68a8b956-51fa-4cf5-ab8c-9a092720ddca`), называется «ТР Внедрить новый конструктор Дизайна ДК **в диалоге создания типа карты**»: блок БЛ расписан под `DiscountCardType.Create`/`Init`, схема процесса — тоже про них. Для диалога создания Дизайна отдельного раздела в нём нет, и это не упущение — Лебедева 11.08 писала, что у трёх задач «суть примерно одна», а Михайленко 31.08 попросила «внедрить общий код в сценарии по всем трём задачам». То есть источники для нашего сценария — постановка задачи, ответы в переписке и уже влитый фронт, а ТР задаёт состав начальных значений.

Перенесённое из ТР без изменений: баннер, логотип и название — с точки продаж; блоки «Кэшбэк» → `[Кэшбэк]` и «Ваши бонусы» → `[Баланс бонусов]`; цвета не делаем; сайт на бэке не создаём; на фронт отдаём пустое поле `SiteId` («нужно только чтобы `SiteId` было в формате записи») и идентификатор шаблона. Пункт ТР про «новое поле `CardTemplateId`» для нашего метода не нужен: `DiscountCardTemplate.Create` уже возвращает `@Template`, а фронт читает `record.get('CardTemplateId') || record.get('@Template')` (`CreateDialog/PrefetchConfig.ts:71`).

## Что оказалось готово до начала работы

Августовские блокеры этой ветки работ сняты — проверено по коду, а не по обещаниям:

- **ПО ДизайнКарты реализовано.** Кузаков влил `LoyaltyCardDesign.Read`/`Write` (задачи №08301113 и №08301167, МР discount-cards 27769/27770 и price-formation 149186/149187). В `DiscountCard.aorx` у объекта теперь есть `Logo`, `Name`, `IsActive`, `Frame`; блок методов не пустой.
- **Формат записи известен.** `LoyaltyCardDesign.Read` (`dcservice/appobjectimpl/loyaltycarddesign/read.py`) читает `CardTemplate` по `@CardTemplate` и разворачивает `ViewDetails` поверх полей шаблона; `Frame` = `SiteId`. `Write` собирает `ViewDetails` обратно по ключам `DEFAULT_VIEW_DETAILS` и кладёт `SiteId` из `Frame`.
- **Фронт влит 14.08** (Лебедева, МР 148293/148294 и правки по ревью). Диалог создания дизайна — тот же компонент `CreateDialog`, источник `DiscountCardTemplate.Create`/`Save`, конструктор получает `readOnly: false` и читает ПО по `@Template`; перед сохранением фронт делает `record.set('SiteId', result.siteId)` — поэтому поле обязано быть в формате записи.
- **`SiteId` уже в контрактах** `DiscountCardTemplate.Read`/`Save` (`DCService.orx`) и в СДК (`CardTypeTemplate.Update`), так что отдельного кода на сохранение не потребовалось: `save()` прокидывает запись целиком.

## Решение

Один общий помощник на все сценарии — `init_design_template(template_id, card_type_id)` в `priceformationonline/discountcard/discountcarddesign/card_design.py`: пишет `build_view_details()` в шаблон СДК через `CardTypeTemplate.Update` и намеренно не передаёт `ThemeData`. `init_design_template_in_sdc` (диалог типа карты) теперь только находит `@Template` и делегирует сюда же.

| Метод | Под фичей `dc_design_new` | Без фичи |
|---|---|---|
| `DiscountCardTemplate.Create` | инициализирует дизайн, кладёт пустой `SiteId` в формат, **не читает** брендбук | читает `ThemeData` и `_OldData` как раньше |
| `DiscountCardTemplate.Save` | выбрасывает `ThemeData` из записи до отправки в СДК; `SiteId` уезжает вместе с записью | брендбук как раньше |
| `DiscountCardType.Init` | не зовёт `ThemeManager.Update` и `update_template_in_sdc` | как раньше |

## Почему `ThemeData` пришлось гасить

`CardTypeTemplate.Update` в СДК на непустой `ThemeData` **пересобирает `ViewDetails` из брендбука целиком** — `before_update` → `if theme_data: new_record.Set('ViewDetails', _format_view_details(theme_data))` (`www/DCService/dcservice/online/cardtypetemplate/update.py:89-92`, проверено на `rc-26.5100`, `c8e765b70` от 09.09). Это не мерж, а замена.

Порядок сохранения в диалоге такой: сначала конструктор пишет дизайн через `LoyaltyCardDesign.Write`, затем форма сохраняет карточку. Если в карточке осталась `ThemeData` (а она попадала туда прямо из `Create`), второй шаг затирал только что сохранённый дизайн. Фронт под фичей `ThemeData` не трогает, но и не удаляет — `prepareCardRecordBeforeSave` под `isNewDesign` просто проходит мимо.

**Решение согласовано.** Вопрос висел с 25.08 (Кузаков: «не могу ответить»), Михайленко 31.08: «с Элиной обсуди, я тоже не знаю». Ютман 31.08 14:23 ответила прямо: «Так если Дизайн на конструкторе, то ThemeData как раз будет пустым», фича — `dc_design_new`; про «момент» просила подробнее. Реализованный ответ на «момент»: `ThemeData` не появляется в записи с самого начала (её не читает `Create`), и всё равно отбрасывается на сохранении (`Save`, `Init`) — то есть переключение только флагом, без миграции.

Та же дыра была и в уже влитой соседней задаче: `DiscountCardType.Create` кладёт `DiscountCardThemeData` безусловно (`get_list.py:140`), а `Init` при непустой `DiscountCardThemeData` зовёт `update_template_in_sdc`. Закрыто здесь же, симметрично.

## Три сценария — один бэк

Пустое представление реестра (третья задача, `019ef861-4ff7-7b16-8a2c-0408eaca28a7`) отдельного бэка не требует: `_emptyTemplate/View.tsx:27` берёт тот же `getSource()` (create → `DiscountCardType.Create`, update → `DiscountCardType.Init`), а `EmptyTemplate/PrefetchConfig.ts:161` — тот же `ConstructorDataFactory`. Создание из карточки акции — тоже через `CreateDialog` (`Promotion/Form/_cardDesign/View.ts:391`). Значит сделанным закрыты все три сценария.

## Реализация

- `discountcarddesign/card_design.py` — `init_design_template` + формат `TEMPLATE_VIEW_DETAILS_FORMAT` (переехал из `discountcardtype/helpers.py`).
- `discountcardtemplate/create.py` — ветвление `_init_card_design` / `_init_brandbook_design`.
- `discountcardtemplate/save.py` — гашение `ThemeData` под фичей.
- `discountcardtype/init.py` — то же для диалога типа карты.
- `discountcardtype/helpers.py` — `init_design_template_in_sdc` делегирует в общий код.
- `DCService.orx` — `<return name="SiteId">` (UUID) в `DiscountCardTemplate.Create`.

Тесты: `discountcardtemplate` 17 OK, `discountcarddesign` 18 OK, все `create.py` из `tests_new/online/src` 48 OK, `init.py` 10 OK. pylint 10.00/10 по пяти изменённым продуктовым файлам. Закоммичено в `26.5100/feature/aatimoshenko/06242714` (`8af5b431a1`).

**Sonar упал на сложности, и не на пустом месте.** `DiscountCardType.Init` имела цикломатическую сложность C (20) — вплотную к порогу, и одно добавленное условие `and not check_feature(...)` перевело её в D (21): `radon-block-metric` завалил сборку. Вынесены два связных блока — `_setup_design` (анкета, дизайн карты, `SiteId`; B 6) и `_send_stamps_statistics` (метрика включения штампиков; A 4); `init` стала C (13), средняя по файлу A (4.25). Правило на будущее: прежде чем дописать условие в длинный метод этого модуля, смотреть `radon cc -s` — порог D начинается с 21, и «плюс одна строка» стоит красной сборки.

## Что проверяемо сейчас, а что после доброски фронта

Фронт сейчас не зовёт ни `DiscountCardTemplate.GetBackSideData`, ни `LoyaltyProgram.GetSalePointDesign` (grep по `client/` пуст), а в `ConstructorEditor.tsx` висит todo «нужна логика обновления прикладного объекта при изменении названия и обновление блоков обратной стороны».

Проверяется уже сейчас: создание дизайна и типа карты с начальными значениями, сохранение `SiteId`, переименование и публикация дизайна без слёта на дефолтный (страница «Дизайн» читает `ThemeData` из брендбука через `Read` — именно этот путь ловит guard в `Save`), несколько дизайнов у типа карты, регресс без фичи.

Только после доброски фронта: подстановка адреса и телефона на обратную сторону, обновление заголовка при смене названия, перезапрос баннера/логотипа/контактов при смене ТП, **правка существующего дизайна** — страница «Дизайн» под фичей открывает конструктор с `readOnly: true` (`Design/PrefetchConfig.ts:101`), редактируемый конструктор есть только в момент создания.

## Открытые вопросы

- **Образы и штампики.** В `LoyaltyCardDesign.Write` у Кузакова стоят TODO на обновление электронных образов, штампиков и реферальных ссылок. Значит после правки дизайна через конструктор Apple Wallet / Google Pay и SabyGet могут не обновиться — зона задачи реализации ПО, предупредить QA.
- **`Name` в `ViewDetails`.** `Read` разворачивает `ViewDetails` поверх полей шаблона, поэтому наш `ViewDetails['Name']` перебивает колонку `Name`; `Write` этот ключ отбрасывает (его нет в `DEFAULT_VIEW_DETAILS`). После первого сохранения имя остаётся только в колонке. Расхождение не наше, но заметное.
- **Тексты блоков** — `[Кэшбэк]`/`[Баланс бонусов]` из ТР против `[BonusDescr]`/`[BonusBalance]` из старого механизма (`get_draft_list.py:52`); код следует ТР, вопрос к проектированию не закрыт.
- **Отписать Ютман** формулировку «момента» отказа от `ThemeData`, чтобы вопрос закрылся письменно.

## Инструментальное

- **Крэш при чтении записи после БЛ-вызова.** Запись, пойманная моком `sbis.EndPoint(...).CardTypeTemplate.Update`, после возврата из `sbis.DiscountCardTemplate.Save(...)` уже нежива: `record.Get('SiteId')` в тесте валит процесс с 0xC0000005 (`-1073741819`), без трейсбэка. Лечится чтением полей **во время** вызова через `side_effect`, который возвращает обычные python-значения. Ещё одна форма антипаттерна «`rec` пережил владельца».
- `record.AddRecord(name, sbis.Record(...))` ждёт формат, а не запись — падает «No registered converter … from this Python object of type Record». Для поля-записи нужен `record.Put(name, value, sbis.FieldType.ftRECORD)`. Строку в поле `ftUUID` тоже лучше не класть — кладите `uuid.UUID`.
- **Запуск тестов на этом стенде — только из PowerShell.** В Git Bash `py_tests_runner.py` падает на `from sbis_root import loader` с `DLL load failed while importing wrap`. Плюс нужен `PYTHONPATH=<run>/modules/Python Core`, иначе `No module named 'sbis'`. Прогон пакета `discountcardtype` по директории даёт ложную ошибку импорта `tests_priceformationonline...` в `create.py` — гонять из корня `tests_new/online/src`.
- Транзакции claude-obsidian требуют POSIX-дескрипторов и `fcntl.flock` — на этой машине запускать через `wsl.exe`, из Git Bash apply не пройдёт.
