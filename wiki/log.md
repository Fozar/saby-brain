---
type: meta
title: "Operation Log"
updated: 2026-08-11
tags:
  - meta
  - log
status: evergreen
related:
  - "[[index]]"
---

## [2026-08-11] ingest | Скрипты (полная статья) + визуализация зависимостей БЛ-модулей (Graphviz)

- Type: ingest (2 root-файла `.raw/`, отсутствовали в `.raw/.manifest.json`)
- File 1: `.raw/Скрипты.md` → wiki/sources/skripty-2026-06-12.md (c-000274)
  - Pages created: none (тема уже покрыта существующей канонической страницей)
  - Pages updated: [[Wasaby-Scripts]] (+ «Отчёт выполнения скрипта», +«Файлы со списком клиентов по стендам», +файл `services`, +прямое соединение с БД для схемы public/pgbouncer, +лимит 300 000 DWC-сценариев)
  - Key insight: диапазон «Ограничение одновременного выполнения» — 0–999, а не 0–100 (более ранний частичный клиппинг вводил в заблуждение); отмечено `> [!contradiction]`
- File 2: `.raw/Визуализация зависимостей модулей БЛ дистрибутива онлайна с помощью Graphviz.md` → wiki/sources/graphviz-bl-dependency-viz-2026-08-10.md (c-000275)
  - Pages created: [[BL-Module-Dependency-Graphviz]] (c-000276), [[Садомов-А.А.]] (c-000277)
  - Pages updated: [[Wasaby-Module-System]] (+раздел «Инструментарий: визуализация зависимостей»)
  - Key insight: первый прецедент в вики инструментария для визуализации s3mod-графа зависимостей (sandbox-инструмент `S3modToGraphviz`, DOT/Graphviz); мотивирующий кейс — рефакторинг `Cadres → ЗиК` в `Cadres → SalaryCore`
- Pages updated (both): [[index]], [[hot]], [[concepts/_index]], [[entities/_index]], [[sources/_index]]
- Manifest: оба файла записаны в `.raw/.manifest.json` (hash, ingested_at, pages_created, pages_updated)

## [2026-08-10] save | Внешние потребители событий лояльности + забытые точки DWC-миграции

- Type: save (concept)
- Location: wiki/concepts/Loyalty-Events-External-Consumers.md (c-000273)
- Ключевое: из 14 событий, удалённых в №03266097, два имеют подписчиков вне СДК — `sabyget/core` (`Tasks.EventUpdateBonusFlag`) и `saby-forms` (`Survey.UpdatePromocode`); обе подписки ломаются молча. Решение — не DWC, а re-publish собственного события из discount-cards (прецедент `discount-cards.card-type.changed` из `notify_changes`); добавлен аналог `discount-cards.promocode-type.changed` с `application='saby-forms'`. Отдельно №08106197 (4200) добирает две забытые публикующие точки: `async_notify_changed_cards` и `BonusOperationEventQueue.publish`; при DWC батчинг по 50 снимается из-за `one_task="1"` + ключа ограничения по ClientID.
- Pages updated: [[Loyalty-Events-External-Consumers]] (new), [[DWC-Card-Events-Migration]], [[index]], [[hot]]

## [2026-08-07] save | Задача №080611736 — HasPrices не долетал от старого владельца в GetLeadPeriodList

- Type: save (decision)
- Location: wiki/concepts/ReferralProgram-GetLeadPeriodList-HasPrices-Compat.md (c-000272)
- Root cause: `HasPrices`-метаданное для колонки вознаграждения в мастер-фильтре ставится только в `rc-26.4100`; у владельца на old его нет → фронт партнёра колонку не рисует. Фикс — на `26.3264/bugfix/aatimoshenko/080611736`, смержен в `26.4100/bugfix/aatimoshenko/080611736`. Второй симптом тикета (этапы сделки) — баг фронта (`Footer.tsx`), не наш.
- Pages updated: [[ReferralProgram-GetLeadPeriodList-HasPrices-Compat]], [[ReferralProgram-GetLeadPeriodList-LeadCount-Source]], [[hot]]

## [2026-08-06] ingest | Вложения проекта «Реферальная программа (2 часть)» — продуктовая обвязка над корешками

- Type: ingest
- Location: wiki/sources/referral-program-part2-attachments-2026-08-06.md (c-000271)
- Also created: 8 concepts (c-000260..c-000268), 2 entities — [[Тихонов-Илья]] (c-000269), [[Кулешов-Дмитрий]] (c-000270)
- From: карточка проекта `project.sbis.ru/uuid/15d9be83-4971-4f44-987f-023d063ec191` → `doc_id=544981304`, 11 вложений верхнего уровня / 6 папок / 14 разобранных документов
- Key insight: проект — **продуктовая обвязка над тем реферальным ядром, которое вики знала только со стороны БЛ**. Главная находка: тех. реализация [[ReferralProgram-Folders-Priority-Sprint|спринта №2]] (декабрь 2025) дословно ставит переход статистики на `ВидЦеныДокумент` и **отказ от сервиса Маркетинга** с оценкой 7 дней — это первоисточник всей линии [[ReferralProgram-Stub-Implementation]] → [[ReferralStub-Backfill-Service-Method]] → [[ReferralProgram-RefDealsConvert-Feature]], растянувшейся далеко за оценку. Второе: реализованное сегодня поле `LeadSum` ([[ReferralStub-LeadSum-Implementation]]) заказано этим проектом **ещё в двух методах** — `ReferralProgram.GetList` (спринт №2) и `GetListByContractor` (спринт №3), то есть выдача суммы наружу закрыта не полностью. Третье: три не заведённых в вики БЛ-метода — `ReferralProgram.Move` (по сигнатуре платформенного `IndexNumber.Move`), `GetListByContractor` (цепочка Карта→ВидКарты→ВидЦеныВидКарты→ВидЦены), `ContractorHasPrograms` (тот же список с лимитом 1, встраивается в `Контрагент.CRMNavigationPreload`); плюс `Folder`/`FolderName` и фильтр `IsJoined` (участие определяется **по наличию `AdObject`**). Папки офферов схему БД не трогают — иерархия `ВидЦены.Раздел` уже есть; доступность «Всем кроме» кладётся в `ВидЦеныРасширение.ТипПредоставления` по аналогии с доступностью скидки по клиентам, вариант с отдельными бизнес-группами отвергнут (рост числа порталов). Самый свежий спринт — [[ReferralProgram-SelfJoin|самоприсоединение партнёра]] (31.07–03.08.2026, 45 дней): страница `partners.saby.ru/<ИД группы>/accept`, признак автоподключения на группе через ВНР, авто-создание и акцепт приглашения + заявка «Агенты Saby»; только ЮЛ, физлица — после отдельного проекта. Масштаб продукта скромный: 30 аккаунтов-партнёров, 5–7 владельцев
- Pages updated: [[index]], [[hot]], [[domains/price-formation/_index]], [[ReferralStub-LeadSum-Implementation]], [[ReferralDeals-System]]
- Отрицательный результат: «Сравнение с конкурентами» и «Эксплуатация системы» — снова незаполненные корпоративные шаблоны (`lastEditDate` февраль 2025), как и в проекте «Дизайн ДК на конструкторе»; лежат «голым» JSON, а не zip — `convert_sabydoc_to_markdown` на них падает. Пусты также концепты спринта №3 «Приоритеты и папки группировки» и (почти) спринта №5 «Ручное изменение суммы вознаграждения»
- Not processed: две плановые сметы `.pdf`, скриншоты `.png`, `.url`-ярлыки на Figma

## [2026-08-06] save | Сумма сделки в корешке — поле LeadSum

- Type: decision
- Location: wiki/meta/ReferralStub-LeadSum-Implementation.md (c-000259)
- From: conversation on price-formation — задача №08052776 («Записывать в корешок сумму сделки + в методе конвертации исторических данных. Сообщить Артемьеву Даниилу»), реализация + 11 тестов
- Key insight: колонка `Сумма` `ВидЦеныДокумент` уже год как агрегируется в `GetPartnerList` (`SUM("Сумма")` → `LeadSum`/`PositiveLeadSum`), но не заполнялась ни одним путём создания корешка — задача закрывает отложенный пункт 3 решения [[ReferralStub-DealSum-Field]]. Поле API названо `LeadSum` (одноимённо колонке-агрегату; варианты `Amount`/`RequestSum` отклонены, `RequestSum` был реализован и переименован до коммита). Ключевое разграничение: `LeadSum` обновляется **при любом статусе и без прав OWNER_ADMIN**, в отличие от соседнего `Price` (только Status=15 + OWNER_ADMIN) — сумма сделки внешний факт, вознаграждение управленческое решение; в историю корешка не пишется. Третий путь наполнения (`HandleLeadStateChanged` → `UpdateStub`) добавлен сверх постановки: у обычных реферальных сделок корешок создаётся в момент создания сделки, когда суммы ещё нет, иначе она осталась бы пустой навсегда. **Опровергнута собственная первая редакция**: `ДокументРасширение.Сумма` входит в стандартный формат `SourcesSales.GetRawDocs`, доп. поле запрашивать не нужно — доказательство в `get_lead_list.py:131`, где по этому полю делается `Set` (а не `Put`), то есть поле уже в формате, при том что фронт реестра доп. полей не передаёт. Переиспользуемо: `Set` vs `Put` у потребителя — доказательство состава формата чужого сервиса без доступа к его исходникам. Побочно: алиас `unnest` в bulk-insert назван `lead_sum`, а не `sum` (конфликт с ключевым словом). 293/293 тестов OK, pylint 10.00/10, не закоммичено
- Pages updated: [[ReferralStub-DealSum-Field]] (planned → resolved), [[index]], [[hot]]
- Открыто: сообщить Артемьеву Даниилу (до этого корешки SabyBank с пустой суммой); доброска уже созданных корешков — миграция идемпотентна по `OperationId` и их пропускает

## [2026-08-06] ingest | Вложения проекта «Дизайн ДК на конструкторе» — команда, план тестирования, два пустых шаблона

- Type: ingest
- Location: wiki/sources/discount-card-design-constructor-attachments-2026-08-06.md (c-000256)
- Also created: wiki/entities/Черных-Константин-Евгеньевич.md (c-000257), wiki/entities/Куимова-Наталья-Владимировна.md (c-000258)
- From: карточка проекта `project.sbis.ru/uuid/27bc0552-…`, 13 вложений через MCP `sbis`
- Key insight: вложения проекта достаются в два вызова — `sbis_resolve_url` для типа «Проект» отдельного ридера не имеет, но возвращает `doc_id=552551747`, а `sbis_list_attachments` по нему работает штатно. Закрыт пробел ингеста 2026-07-03 («3 из 6 документов»): **«Сравнение с конкурентами» и «Эксплуатация системы» — незаполненные корпоративные шаблоны**, содержательного текста нет (отрицательный результат, перечитывать незачем). Полезного добавилось три: (1) состав команды и роли из плановой сметы — план работ содержал только `person/UUID`, теперь 31 участник поимённо, техрук [[Ютман-Элина|Ютман]] 51 чд, БЛ Лояльность [[Омельяненко-Егор-Анатольевич|Омельяненко]] 36,5 + Кузаков 18, менеджер [[Черных-Константин-Евгеньевич|Черных]], согласование прикладного объекта — Агафонцев (существенно, проект вводит 2 новых ПО); финансовые поля сметы намеренно не переносились; (2) концептуальный план тестирования ([[Куимова-Наталья-Владимировна|Куимова Н. В.]], с 01.07.2026, выпуск под фичей 26.6100) — скоуп ровно повторяет 13 экранов Этапа 3 плюс обе конвертации; (3) `Сравнение.xlsx` — рабочая сверка автора: план 252,5 чд vs смета 251,5 чд, расхождения по 8 участникам и 7 отсутствующих в смете отработаны до подписания. Побочно: смета даёт ФИО «Матюшев **Данила** Сергеевич» при существующей странице [[Матюшев-Дмитрий]], где имя было раскрыто из инициала и источником не подтверждалось — помечено `> [!warning]`
- Pages updated: [[DiscountCard-Design-Constructor-WorkPlan]] (+§Команда и роли, +§План тестирования), [[DiscountCard-Design-Constructor-Project]] (+§Команда, ссылка на карточку проекта), [[Матюшев-Дмитрий]], [[index]], [[hot]]
- Not processed: `Дисконтные карты.mp4`, `Мотивационное соглашение`, три `.url`-ярлыка, sabydoc-версии уже заингестированных ТЗ/Описания БП

## [2026-08-06] save | Bonus.GetClientListWithStats — франшизные персональные счета с BonusBalance=0 в СДК

- Type: synthesis
- Location: wiki/questions/GetClientListWithStats-Franchise-PersonalAccount-Zero-Balance-SDK.md
- From: разбор задачи №08041679 (/bug stand) — реестр Бонусы\Клиенты не показывает баланс части физлиц после расторжения франшизного договора; две гипотезы опровергнуты логами cloud_get_logs, root cause найден прямым SQL-запросом к БД discount-cards (BonusBalance=0 у 4 из 6 франшизных персональных счетов) — вывод: не наш баг, передано на discount-cards

## [2026-08-06] save | Bonus.GetTotalBalance — замеры на стенде, франшизная развилка, частичный индекс

- Type: synthesis (обновление существующей страницы)
- Location: wiki/questions/Bonus-GetTotalBalance-Local-Card-Scan-Memory.md (c-000207)
- Also created: wiki/concepts/Card-IsBonus-Flag.md (c-000255)
- From: conversation on price-formation — задача 07208958 «Ошибка на стенде», разбор EXPLAIN + замеры на `test-master-db1` + локальная валидация индекса
- Key insight: «1 ГБ памяти за итерацию» из explain.sbis — это **обращения к shared buffers** (136 348 × 8 КБ), а не work_mem; сортировка под `ARRAY_AGG(DISTINCT)` стоит всего 1539 КБ. Главная методическая находка: `!has_franchise` подставляется **связанным параметром**, поэтому замерять «до» подстановкой литерала нельзя — при литерале `false` PostgreSQL сворачивает FILTER в константу, `IsFranchise` становится неиспользуемой колонкой и планировщик **сам удаляет** `LEFT JOIN "ЧастноеЛицо"` (38 970 вместо 136 348), то есть получается план, которого в бою нет; воспроизведено через `WITH param AS MATERIALIZED`. Отсюда же следствие: оптимизация обязана убирать джойн **текстом шаблона**, а не расчётом на constant folding. Условный шаблон даёт 136 348 → 38 938 (3.5x, тесты 10/10), но **открытый вопрос закрыт — аккаунт франшизный**, и этому тикету шаг 1 не помогает. Во франшизной ветке отвергнуты: денормализованный признак (колонок нет, ключ `Client` с франшизностью не коррелирует), отсечение нулевых балансов (73 из 23 994), хэш-джойн (меньше буферов, но 47 018 чтений с диска + пролив в temp, 230 мс I/O). Прежний тезис вики «`Карта` — зона `dccommon`/СДК» **опровергнут**: таблица наша, `PriceFormation.Online.dicx:1773`, партиальные индексы там уже есть; `ЧастноеЛицо` действительно внешняя (`:55`, `CEXTENSION`). Частичный индекс `BonusCardEmission` (предикат дословно повторяет фильтр; условие в предикате, а не в выражении — индекс <1% таблицы; колонка `Эмиссия`, потому что по ней джойн; побочно чинится оценка кардинальности, ошибавшаяся в 97 раз) валидирован локально: 13 998 → 1 098. Локальный бенчмарк был бы бессмысленным без подгонки **ширины строки** — с дефолтной таблица занимала 1 166 страниц, планировщик брал Seq Scan и эффекта не было вовсе
- Pages updated: [[index]], [[hot]], [[Bonus-GetTotalBalance]] (связи + починен устаревший `_get_balance_by_cards`)

## [2026-08-05] save | GetLeadPeriodList — мастер-фильтр заявок на корешках под ref_deals_convert

- Type: decision
- Location: wiki/meta/ReferralProgram-GetLeadPeriodList-Stub-Mode.md (c-000254)
- From: conversation on price-formation — задача №07294792 (этап «Реестр "Заявки" на данных из "корешков"»), реализация + тесты
- Key insight: постановка «считать заявки по корешкам под фичей» уже была выполнена для `LeadCount` (коммит `4f0b9b8983`, 17.06.26 — `ТипСвязи IS NOT NULL` безусловно); реально не работал `Price`, потому что миграция (`create_stubs_for_existing_leads.py:411`) создаёт корешок **без** `"Документ"`, а ветка `IsStubMode = "0"` ловит только `Документ IS NOT NULL` либо `Документ IS NULL AND OperationId IS NULL` — корешок сделки не подходит ни под одно условие. Решение: `IsStubMode = SabyBank OR check_feature(REF_DEALS_CONVERT)` (тот же гейт, что в `GetPartnerList`/`GetStats`) + новый признак `IsSabyBank`, сохраняющий вознаграждения за посетителей у обычных программ. Маркетинговой ветки в этом методе нет и быть не может: `SalesSources.ReadStat` агрегирует за один интервал без разбивки по месяцам, а фильтр запрашивает до 40 периодов за страницу. Побочно зафиксировано расхождение признаков корешка: `GetStubList` — по `OperationId`, `LeadCount` — по `ТипСвязи`; закрыто коррелирующим тестом
- Pages updated: [[index]], [[hot]], [[ReferralProgram-RefDealsConvert-Feature]]

## [2026-08-05] save | ExportDiscountCard.PrepareFile — выгрузка карт в Excel без памяти

- Type: synthesis
- Location: wiki/questions/ExportDiscountCard-Excel-Memory-Optimization.md (c-000253)
- From: conversation on price-formation — задача №07076892 (регламент «Ошибка», инцидент 6a4cd630aff653d23a7b7db5 от 07.07.2026, prod12/online-ru-09, утилизация памяти 50.53, метод 2166 с). Серверные логи недоступны (retention 3 суток), разбор целиком по коду
- Key insight: БЛ-метод `Excel.SaveToFile` непригоден для больших выгрузок — `RecordSetToExcel.__init__` (`rs_printer.py:77`) зовёт `self.options.get("RoundFields", None)` на пришедшем `sbis.Record`, у которого `get()` объявлен без аргументов и «ничего не делает» (`Record.pyi:736`) → `TypeError` на любом непустом `Options`; с `Options=None` включается `in_memory=True` и книга опять целиком в памяти. Корректно разбирают `Options` только `Excel.Save`/`SaveList` через `save_custom` (`options.as_dict()`), но им нужен списочный БЛ-метод. Отсюда прямой импорт `excel.light_printer.LightPrinter`. Побочно: `ms_excel` делал все ячейки текстом (`str(value)`), переход на `Excel` это чинит; `ExportPersonalBalance._lrs_task_method` указывает на чужой экспорт (не фикшено); причина `@test_new_skip` у `TestExportPromocode` (зависимости CAOnline) отпала
- Pages updated: [[index]], [[hot]]

## [2026-08-05] save | Событие смены источника у сделки — локальная подписка вместо доработки CRM

- Type: decision
- Location: wiki/meta/ReferralProgram-SourceChanged-Local-Event.md
- From: conversation on price-formation — задача №07222426 (корешок при смене источника у существующей сделки). Разбор клиентского `.sbislogz` + серверных логов облака `pre-test-online`, сцепленных по `uuid` асинхронного вызова через `SalesSources.ManualPick` (advert-service) → `SourcesSales.InstalledOnLead` (пул `online`)
- Key insight: `SourcesSales.InstalledOnLead` публикует локальные события `salessources.source_changed`/`sourcessales.name_changed` **в пуле `online`**, том же, где упакован `LoyaltyReferral` — начальный вывод «local = нужна доработка CRM» был неверным; в `on_event.py` уже есть рабочий прецедент того же паттерна (`Lead.StateChanged` → `event.SetLocalCallback`). Побочно поправлено описание параметров `cloud_get_logs` в `sbis-mcp/src/sbis_mcp/server.py` — naive `from_dt`/`to_dt` трактуются как локальное время хоста MCP-сервера (UTC+7), не UTC и не московское.
- Pages updated: [[index]], [[hot]]

## [2026-07-31] batch ingest | 15 диалогов SBIS — история корешков (for_program), перенос программ, GetCRMThemeId проверен

- Type: batch ingest (15 источников `raw/Диалоги SBIS/`, 2026-07-30/31; 1 из них — обновление ранее ингестированного файла)
- Sources: `019f1c60...` (update, +2 msg), `206d1fba...`, `971c21aa...`, `27e85adc...`, `019f60a3...`, `65e0d9ad...`, `44bd4968...`, `019fb1d0...`, `3067c623...`, `186b7743...`, `4c01a23b...`, `019f18d1...`, `79e80c8d...`, `019fb20d...`, `019fb25a...`
- Pages created (source, 14): [[crm-license-request-local-stand-2026-07-31]] (c-000234), [[sabybank-inn-kpp-stub-storage-2026-07-31]] (c-000235), [[getpartnerlist-stub-stats-2026-07-31]] (c-000236), [[getstublist-bug-no-records-2026-07-31]] (c-000237), [[ref-deals-convert-feature-enable-2026-07-31]] (c-000238), [[mr-comment-for-program-method-2026-07-31]] (c-000239), [[mr-review-stub-history-call-2026-07-30]] (c-000240), [[crmthemeid-plan-item-verified-2026-07-31]] (c-000241), [[release-error-analysis-2026-07-31]] (c-000242), [[updatestub-status-check-2026-07-31]] (c-000243), [[referral-transfer-hide-plan-item-2026-07-31]] (c-000244), [[movetoagentgroup-test-data-2026-07-30]] (c-000245), [[createstubsforexistingleads-bug-4100-2026-07-30]] (c-000246), [[zvonok-history-button-placement-2026-07-30]] (c-000247)
- Pages created (concept/decision, 5): [[ReferralProgram-GetPartnerList-Stub-Stats]] (c-000248), [[SabyBank-Stub-INN-KPP-Storage]] (c-000249), [[ReferralProgram-GetStubList-Bug-Partner-No-Records]] (c-000250), [[ReferralProgram-RefDealsConvert-Feature]] (c-000251), [[ReferralProgram-MoveToAgentGroup]] (c-000252)
- Pages created (entity, 1): [[Самарина-Ирина]] (c-000233)
- Entity merge: [[Настя-QA]] → [[Земцова-Анастасия]] (address c-000205 carried over) — identity confirmed across 5 of the 15 sources (miration/QA testing role matches)
- Pages updated: [[referral-history-implementation-breakdown-2026-07-29]] (naming clarification `ReferralStub`/`ReferralStub_<ID>`), [[ReferralStub-History-Scope-Cut]] (§for_program, MR review call), [[ReferralStub-DealSum-Field]] (COUNT implemented, SUM still pending), [[ReferralStub-Backfill-Service-Method]] (bug fixed, enabled in 4100), [[ReferralProgram-History-UI-Design]] (button placement decision), [[ReferralProgram-CRMThemeId-By-Referral-Code]] (status: open → resolved), [[Свешников-Андрей]], [[Лебедева-Наталья]], [[Мусохранов-Андрей-Владиславович]], [[Тимошенко А.А.]], [[entities/_index]], [[concepts/_index]], [[sources/_index]], [[index]], [[hot]]
- Key insight: `ReferralProgram.GetCRMThemeId` (задача №07164990) реализован в 26.4200 и практически проверен в целевом контексте («на схеме тензора») — первая полностью закрытая развилка из открытых вопросов batch 2026-07-29. Параллельно ревью Мусохранова на MR истории корешков ([[ReferralStub-History-Scope-Cut]]) вскрыло пробел в исходном объёме («истории по программе нет вообще») и потребовало доработки методом `for_program` в тот же день.
- Contradictions: `[!contradiction]` добавлен в [[mr-review-stub-history-call-2026-07-30]] — исходная формулировка объёма [[ReferralStub-History-Scope-Cut]] («истории по корешкам программы нет, только по отдельности») вызвала возражение ревьюера и была расширена методом `for_program`, а не отменена

## [2026-07-30] save | Урезание объёма задачи истории реф. программы до истории корешков

- Type: decision
- Location: wiki/meta/ReferralStub-History-Scope-Cut.md (c-000232)
- From: conversation on price-formation — задача №07012946, ветка `26.4200/feature/aatimoshenko/07012946`: из трёх пунктов постановки [[ReferralProgram-History-UI-Design]] в ветке оставлен только бэкенд истории корешка; `ReferralProgram.GetHistoryList` (2 коммита) и проваливание из истории оффера удалены, `history_object.py`/`price_entity.py` возвращены к `rc-26.4200`; reset + force-push → один коммит `0813f6d628`, MR !147258
- Key insight: в историю оффера события по корешкам не пишутся **вообще** — усиление относительно исходной постановки, где «создание корешков» оставалось в истории оффера. Побочный регресс-риск: проверка «корешок не найден» в `update_stub` теперь срабатывает всегда, а не только при переданном `Price`. Механизм отложенного проваливания задокументирован для будущей задачи (префикс `@event_` обязателен, на чтении приходит в `Attributes` без него).
- Pages updated: [[ReferralProgram-History-UI-Design]] (раздел «Ревизия объёма», related), [[index]], [[hot]]

## [2026-07-30] save | Повторное удаление фичи entity_sp (backend, price-formation)

- Type: synthesis (update)
- Location: wiki/questions/entity-sp-deletion-order-2026-06-15.md (status: developing → resolved)
- From: conversation on price-formation — откат отката: `git revert fa95ca0235` (revert июньского удаления `1fb3ffbd1c`) на ветке `26.5100/bugfix/aatimoshenko/05144878_feature_del` от `rc-26.5100`, 2 конфликта разрешены вручную (код мутировал за 1.5 месяца), закоммичено `930d0b1dc9`
- Key insight: блокер удаления был не в price-formation, а в нестабильности `entity_sp` на стороне другой команды; объём повтора сознательно ограничен исходными 35 файлами — новые `check_feature(ENTITY_SP)` в отчётах/markup/promotion/license.py вне скоупа
- Pages updated: [[entity-sp-deletion-order-2026-06-15]], [[index]], [[hot]]

## [2026-07-30] dialogs-scan | Разбор реализации UI истории реф. программы (1 сообщение)

- Type: ingest (1 источник, sbis-dialogs-scan за 2026-07-29 12:46 → 2026-07-30)
- Source: `raw/Диалоги SBIS/019f1c60-d761-7b2b-95fa-3ab61865088c.md` (theme_id 019f1c60-d761-7b2b-95fa-3ab61865088c, сообщение Тимошенко → Лебедева Наталья, 2026-07-29 16:20)
- Pages created (2): [[referral-history-implementation-breakdown-2026-07-29]] (c-000230), [[Лебедева-Наталья]] (c-000231)
- Pages updated: [[ReferralProgram-History-UI-Design]] (c-000229 — раздел «Разбор реализации», related), [[index]], [[hot]]
- Key insight: постановка [[ReferralProgram-History-UI-Design]] от 07-29 получила конкретное разделение работ — Лебедева делает кнопку истории корешка, Тимошенко — клик-колбэк из истории оффера и фильтрацию БЛ-метода `GetHistoryList` по реф. сети. Реализация не подтверждена завершённой.
- Scan noise filtered (3): auto-код безопасности «Безопасность» 06:01(30.07), уведомление публикации статьи базы знаний «Подсистема распределения прав», рассылка «Просрочка ИЮЛЬ» (16 участников, без реплик по существу)

## [2026-07-29] batch ingest | 2 звонка SBIS — дизайн UI истории изменений (оферы/лиды/корешки)

- Type: batch ingest (2 источника, продолжение раннего скана того же дня — предыдущие 2 попытки прочитать эти theme_id падали с ошибкой SBIS `Поле "Position" имеет тип строка отличный от запись`; баг устранён на стороне SBIS, перечитано успешно с одной попытки)
- Sources: `raw/Диалоги SBIS/{019fad14-31da-7092-a5e4-fc22e5e463ee, 019fad37-dc88-790c-97bc-76cf7086ecea}.md`
- Pages created (4): [[zvonok-tim-sveshnikov-referral-history-buttons-2026-07-29]] (c-000227), [[zvonok-tim-sveshnikov-mihel-referral-history-ui-2026-07-29]] (c-000228), [[ReferralProgram-History-UI-Design]] (c-000229), [[Михель-Витольд]] (c-000226)
- Pages updated: [[Свешников-Андрей]] (c-000048 — related + ключевое решение 2026-07-29, ранее не был в [[index]] — добавлен), [[ReferralProgram-Data-Model]] (related-ссылка), [[index]], [[sources/_index]]
- Cross-reference pass:
  - Оба звонка — один непрерывный разговор (11:53–12:00, затем 12:32–12:46 с подключением Витольда) → одна concept-страница [[ReferralProgram-History-UI-Design]] вместо двух изолированных, source-страницы ссылаются друг на друга как части 1/2 и 2/2.
  - [[Свешников-Андрей]] уже документировал роль «со-ответственный за реф. сеть на бою (вместе с Михель В.)» (страница от 2026-05-28) — сегодняшнее «создал вторую реферальную сеть на бою» прямое исполнение этой роли, а не новый факт с нуля.
  - Топически связано с [[ReferralProgram-Data-Model]] §«Миграция между Реф. Сетями» (задача 06096778) — **не объединено** с этой задачей: источник не подтверждает, что вторая сеть создана именно под неё, только совпадение по теме/времени. Помечено как несвязанное предположение на странице источника.
- Key insight: Дизайн-решение по UI истории — раздельные кнопки для оффера и для корешка, явный отказ от объединения в одну общую историю («двумя историями точно нельзя»). Побочно всплыл нерешённый вопрос: похожая группировка с разворачиванием, ожидаемая по аналогии с историей дисконтных карт, на практике не найдена («мне казалось... но почему-то нет») — не проверено в коде, зафиксировано как открытый вопрос, не факт.

---

## [2026-07-29] batch ingest | 10 диалогов SBIS (raw/Диалоги SBIS/) — CRMThemeId отвечен, кластер багов РСС на РКО, chunk-лимит бонусов, флаки ДК

- Type: batch ingest (10 источников, режим Batch Ingest — единая cross-reference запись)
- Sources: `raw/Диалоги SBIS/{05fa821f-254d-4c51-a808-91c1f1070750, edefef17-381e-450f-9613-c3c4fa885357, a3ea0b39-7e9a-4707-8ccf-7fa3da46ae83, c89da1fa-3bc7-4099-8e69-6aa865fcc16b, 3e1911a7-c5fa-41cb-9d86-7b7fe8c062d9, 870d5121-7ea3-4f52-bf36-1b279e3665f2, 598adac5-b76b-4345-a0a9-a28f7914a1f3, 019f9405-44ba-7032-b837-4482688479c3, 019f6a41-14ec-7092-b0ac-98e0b96f8c4a, 019facd1-e05f-7990-a482-ac9c533c216a}.md`
- Pages created (13): [[referral-leadperiodlist-koreshki-followup-2026-07-29]] (c-000213), [[sabybank-rko-bug-partner-terminated-contract-2026-07-29]] (c-000214), [[discount-card-type-settings-flaky-autotest-2026-07-29]] (c-000215), [[bonus-report-getlist-limit-increase-2026-07-28]] (c-000216), [[referral-loyalty-disk-access-task-closed-2026-07-28]] (c-000217), [[dwc-card-events-rollout-status-2026-07-28]] (c-000218), [[partner-cabinet-source-mechanism-tz-2026-07-28]] (c-000219), [[sabybank-rko-bug-applications-not-shown-sabynet-2026-07-28]] (c-000220), [[referral-crmthemeid-answers-2026-07-28]] (c-000221), [[zvonok-sveshnikov-timoshenko-stage-tracking-2026-07-29]] (c-000222), [[SabyBank-RKO-Partner-Display-Bugs]] (c-000223), [[BonusOperationAdm-GetList-Chunk-Limit-Increase]] (c-000224), [[DiscountCardType-Settings-Async-Load-Flaky-Autotest]] (c-000225)
- Pages updated: [[ReferralProgram-CRMThemeId-By-Referral-Code]] (c-000212 — 2 из 3 развилок закрыты, чеклист обновлён), [[DWC-Card-Events-Migration]] (c-000004 — секция rollout-статуса), [[SabyBank-RKO-Referral]] (секция «Известные баги на стенде»), [[index]], [[hot]], [[sources/_index]]
- Cross-reference pass (после всех 10 источников):
  - [[referral-crmthemeid-answers-2026-07-28]] прямо отвечает на 2 из 3 развилок в ранее созданном (2026-07-28, тот же день) [[ReferralProgram-CRMThemeId-By-Referral-Code]] — question-страница обновлена ответами, а не создана заново.
  - Оба бага РСС на РКО ([[sabybank-rko-bug-partner-terminated-contract-2026-07-29]], [[sabybank-rko-bug-applications-not-shown-sabynet-2026-07-28]]) — один репортёр (Земцова А.В.), одна дата ошибки (24.07.26), одна фаза тестирования [[SabyBank-RKO-Referral]] → объединены под [[SabyBank-RKO-Partner-Display-Bugs]] вместо двух изолированных source-заметок.
  - [[discount-card-type-settings-flaky-autotest-2026-07-29]] (флаки ДК) ссылается на [[DWC-Card-Events-Migration]] («проект DWC должен был это полечить»); отдельно [[dwc-card-events-rollout-status-2026-07-28]] показывает, что массовый rollout `dwc_card` не запланирован — связаны через новый `> [!gap]` на странице DWC-Card-Events-Migration (флаг мог быть просто выключен на затронутом стенде).
  - [[referral-leadperiodlist-koreshki-followup-2026-07-29]] — не новое знание, а живое подтверждение уже задокументированного решения [[ReferralProgram-GetLeadPeriodList-LeadCount-Source]] §«Будущее» (обычные программы пока не считаются по корешкам).
- Key insight: Единственная содержательная контр-находка — **флип бага РСС на РКО** (см. `> [!contradiction]` на [[sabybank-rko-bug-partner-terminated-contract-2026-07-29]] и на агрегирующей странице): фикс исходной жалобы («расторгнутый договор виден») обернулся противоположным дефектом («действующий договор не виден») — похоже на инвертированный фильтр статуса, диагностика не завершена.
- Known issue (окружение, не вики): `scripts/wiki-lock.sh` использует `flock`, отсутствующий в Windows Git Bash этого чекаута (`flock: command not found`, meta-lock не берётся). При единственном писателе в рамках этой сессии продолжили запись напрямую через filesystem-транспорт (документированный «last floor»); при параллельном ingest в этом окружении блокировка сейчас **не работает** — нужно либо ставить `flock` (WSL/Cygwin), либо явно документировать Windows-хост как single-writer-only до фикса.
- Data note: [[598adac5|partner-cabinet-source-mechanism-tz-2026-07-28]] и [[019facd1|zvonok-sveshnikov-timoshenko-stage-tracking-2026-07-29]] — тонкие источники (1 реплика / зашумлённый ASR); зафиксированы с пометками `[!gap]`/`[!note]` о низкой информационной плотности, не форсировано в полноценные concept-страницы.

## [2026-07-28] save | Задача №07164990: CRMThemeId по реф. коду партнёра — контекст собран, вопросы заданы
- Type: question
- Location: wiki/questions/ReferralProgram-CRMThemeId-By-Referral-Code.md (c-000212)
- From: разбор задачи №07164990 (проект «Авторегистрация для Alfa ID и СберБизнес») — SBIS-задача, тред оценки, ТЗ проекта, код `LoyaltyReferral`
- Pages created: [[ReferralProgram-CRMThemeId-By-Referral-Code]] (c-000212)
- Pages updated: [[index]], [[hot]]
- Key insight: «тема отношений» = `CRMThemeId` в `ВидЦены.Атрибуты->ReferralProgram`, единственный боевой потребитель — `create_lead.py:148` (поле `Регламент` для `CRMLead.insertRecord`). Путь от реф. кода: `Карта.Атрибуты->AdObject` → `Эмиссия` → `ВидЦеныВидКарты` → `ВидЦены` — тот же джойн, что в `SQL_GET_REFERRAL_CODE_*` (`core.py:495-561`), но с другой точкой входа. **ТЗ проекта метод не описывает** — задача добавлена поверх; в ТЗ есть только строковый `КодПартнера` для `Billing.CreateAccount`, которого в price-formation нет вообще. Три развилки закрыть без постановщика нельзя: формат входа (`utm_rfcid` целиком / `@AdObject` / UUID карты), нужен ли `CreateMultitenantEndpointByClientId` по первой части кода, и Warning vs 0 при пустом результате. Реализация не начата.

## [2026-07-28] save | Bonus.GetSaleList — фикс SuspectSaleIds реализован и замерен (14 530 → 225 мс)
- Type: synthesis (обновление)
- Location: wiki/questions/Bonus-GetSaleList-SuspectSaleIds-Hash-Regression.md (c-000211)
- From: реализация фикса задачи №06244326 + замер на `test-osr-db19/load-ext-4`, схема `_01216129`
- Pages created: —
- Pages updated: [[Bonus-GetSaleList-SuspectSaleIds-Hash-Regression]], [[index]], [[hot]]
- Key insight: барьером оптимизатора взят **`OFFSET 0`, а не `AS MATERIALIZED`** — стенд на **PostgreSQL 10.21**, где `MATERIALIZED` (PG12+) это синтаксическая ошибка; признак старой версии виден в самом плане (одноразовые CTE показаны как `CTE Scan`, PG12+ их бы заинлайнил). Замер: 14 530 → 225 мс (~53×), buffers 2.42 млн → 70 тыс., спил хеша на диск исчез; `SuspectSaleIds` Hash Join → **Nested Loop Semi Join** 13 287 → 118 мс с `Index Cond: "Sale" = bs."Sale"` по `iВидЦеныДокумент-Retail`. Тесты 41 OK. **Проверка эквивалентности на живых данных вырождена** — оба множества пусты, т.к. на аккаунте нет продаж с бонусными движениями более чем на одну `EffectiveDate` (последние — 30.09.2025); опора на логику преобразования + `test_8` (розничной симметрии в тестах нет). Планы сохранены в `logs/explain-06244326/`. Инструментальное: `psycopg` недоступен (SSL-инспекция ломает pip), EXPLAIN снят через датасурсы PyCharm с постраничным `fetch_query_result(offset=…)` — вывод режется до 10 строк.

## [2026-07-27] save | Bonus.GetSaleList — 13 секунд в SuspectSaleIds (hash semi-join по всей истории)
- Type: synthesis
- Location: wiki/questions/Bonus-GetSaleList-SuspectSaleIds-Hash-Regression.md (c-000211)
- From: разбор задачи №06244326 (ошибка на стенде, реестр «Бонусы/Покупки», test-online) — вопрос [[Ютман-Элина]] о 16–17 с БЛ
- Pages created: [[Bonus-GetSaleList-SuspectSaleIds-Hash-Regression]] (c-000211)
- Pages updated: [[Bonus-GetSaleList-Duplicate-W-Records-Iterative-Block-Bug]], [[index]], [[hot]]
- Key insight: `EXPLAIN (ANALYZE, BUFFERS)` — 13 287 из 13 325 мс в CTE `SuspectSaleIds`, который возвращает **rows=0**. Планировщик разворачивает коррелированный `EXISTS` в hash semi-join и строит хеш по всей истории бонусов клиента (7 `ВидЦены` × 428 779 = 3 001 450 строк, 2.42 млн buffers, `Batches: 16 (originally 1)`), промашка оценки в 900 раз. Отвергнуты три версии: размер блока/EMA (выборка блока 32.8 мс), отсутствие индексов (есть, выбираются), «доработка только в 4100» (`Suspect*` с `rc-26.3211`, на бою `rc-26.3248` текст CTE побайтово тот же). Масштабируется по числу бонусных движений **клиента**, а не по объёму `ВидЦеныДокумент` → на бою латентно, не отсутствует. Опровергнут раздел «Индексы — проверено безопасно» исходной страницы: проверять надо форму плана, а не наличие индекса. Фикс (`MATERIALIZED` + `BlockSales` + nested loop по `Retail (Sale, ДатаВремя)`) не реализован.

## [2026-07-23] ingest | Звонок 2026-07-23: Мусохранов — Тимошенко (ревью подсчёта статистики по корешкам)
- Source: `.raw/Совещания/Звонок 2026-07-23 100252. Мусохранов Андрей, Тимошенко Александр.md`
- Summary: [[zvonok-musohranov-timoshenko-2026-07-23]] (c-000210)
- Pages created: [[zvonok-musohranov-timoshenko-2026-07-23]] (c-000210), [[ReferralStub-DealSum-Field]] (c-000208), [[ReferralStub-Stats-Index-Questions]] (c-000209)
- Pages updated: [[SabyBank-Stub-Rewards-Calculation]], [[Мусохранов-Андрей-Владиславович]], [[Тимошенко А.А.]], [[index]], [[hot]]
- Key insight: корешок несёт только статус+вознаграждение, а `GetPartnerList` показывает сумму по сделкам → решено хранить сумму в свободном поле «Сумма» `ВидЦеныДокумент` и считать `SUM` рядом с `COUNT` в том же подзапросе (пока писать пусто — функционал не реализован). Открытые вопросы, помеченные «странное»: нужен ли фильтр по `ТипСвязи` при подсчёте всех статусов (перестраховка vs влияние на индекс) и покрытие индексами `(Карта, EffectiveDate)`.

## [2026-07-23] save | Bonus.GetTotalBalance — локальный скан «Карта» как источник 1 ГБ/итерация
- Type: synthesis
- Location: wiki/questions/Bonus-GetTotalBalance-Local-Card-Scan-Memory.md (c-000207)
- From: разбор задачи 07208958 (ошибка на стенде, `LoyaltyWidgets.GetBonusesNew`, test-inside)
- Pages created: [[Bonus-GetTotalBalance-Local-Card-Scan-Memory]] (c-000207)
- Pages updated: [[Bonus-GetTotalBalance-Franchise-Performance]], [[index]], [[hot]]
- Key insight: не новая деградация, а **отложенный хвост** 05292113 — локальный скан `Карта` (~943 мс) тогда пометили вторичным, и после починки СДК-ветки коммитом `1be452e6e2` он остался единственным крупным потребителем и всплыл отдельным багом. Разбор FILTER в финальном `SELECT` показал, что оба дорогих джойна (`ЧастноеЛицо` ~750 МБ, `ВидКарты EP` ~210 МБ) вычисляют `IsFranchise`, который влияет на результат только при `has_franchise=True` → для не-франшизных аккаунтов это чистые накладные расходы, снимаются условными блоками шаблона. Фикс НЕ реализован: открыт вопрос, франшизный ли аккаунт на стенде (от этого зависит, закрывает ли правка именно этот тикет).

## [2026-07-23] save | CreateStubsForExistingLeads — миграция корешков как служебный метод
- Type: decision
- Location: wiki/meta/ReferralStub-Backfill-Service-Method.md (c-000206)
- From: сессия разработки по поручению №06155143 (переработка ВНР миграции корешков + текст подзадачи на доброску)
- Pages created: [[ReferralStub-Backfill-Service-Method]] (c-000206)
- Pages updated: [[index]], [[hot]]
- Key insight: [[Migration-Console-First-Testing-Pattern]] применён на практике — ядро миграции вынесено в служебный `ReferralProgram.CreateStubsForExistingLeads(ProgramId, DryRun)` по одной программе, ВНР сведена к перебору программ. Проверяемость обеспечивают две вещи: `DryRun` (ничего не пишет) и возврат `Stubs` (`LeadId/OperationId/CardId/LinkType/Bonus`) — сверка по количеству и идентификаторам вместо «на глаз». Идемпотентность — по `OperationId` = UUID сделки, вставка пачками по 500 в отдельных транзакциях. Права — только служебная роль `PF-Discount`.

## [2026-07-22] ingest | Звонок Мусохранов — Тимошенко: как тестировать ВНР миграции корешков
- Source: `.raw/Совещания/Звонок 2026-07-22 130258. Мусохранов Андрей, Тимошенко Александр.md`
- Summary: [[zvonok-musohranov-timoshenko-2026-07-22]]
- Pages created: [[zvonok-musohranov-timoshenko-2026-07-22]] (c-000203), [[Migration-Console-First-Testing-Pattern]] (c-000204), [[Настя-QA]] (c-000205)
- Pages updated: [[SabyBank-RKO-Referral]], [[Мусохранов-Андрей-Владиславович]], [[Тимошенко А.А.]], [[index]], [[hot]]
- Key insight: продолжение [[zvonok-musohranov-timoshenko-2026-06-30|сдачи корешков]] — ВНР миграции существующих реф. сделок на корешки уже гоняет [[Настя-QA]] (~200 заявок, 3 бизнес-группы, ~20 программ), но выборочная проверка 5 программ не доказывает корректность остального. Мусохранов сформулировал методологию ([[Migration-Console-First-Testing-Pattern]]): отладить ядро миграции как **метод из консоли** на контролируемой фикстуре (сверка по количеству/идентификаторам `ВидЦены`), ловить-чинить ошибки итеративно, и только потом оборачивать в ВНР и отдавать QA с явным сценарием. ВНР — «комбайн» (много согласований), спихивать сплошную проверку сложной миграции на QA неправильно.

## [2026-07-22] ingest | QA-тред кластер «петля вызовов БЛ» (4 форумных треда)
- Source: `.raw/QA/` (4 md: SetPool у Endpoint; другой схеме того же сервиса; под другим клиентом и юзером; смена пользователя)
- Summary: [[wasaby-bl-call-loop-setpool-2026-07-22]], [[wasaby-bl-call-loop-setpool-ext-registration-2026-07-22]]
- Pages created: [[wasaby-bl-call-loop-setpool-2026-07-22]] (c-000201), [[wasaby-bl-call-loop-setpool-ext-registration-2026-07-22]] (c-000202)
- Pages updated: [[Wasaby-BL-Call-Loop-Pattern]], [[index]], [[hot]]
- Уже были в вики (пропущены как дубли): тред Черемисина 10.07.25 → [[wasaby-cross-client-call-2026-06-04]]; тред Разговорова 05.08.25 → [[wasaby-bl-call-loop-user-switch-2026-06-04]].
- Key insight: все 4 треда — один кластер (23.06.25 Лемешко → 08.07.25 Тимошенко → 10.07.25 Черемисин → 05.08.25 Разговоров) с единым решением `CreateMultitenantEndpointByClientId`. Новое из необработанных тредов: (1) служебный пул / `SetPool` — интуитивный, но НЕ каноничный обход петли; (2) `TenantContext` избыточен — `CreateMultitenantEndpointByClientId` заменяет его. Основная масса каждого файла — секции «Похожие темы» (форумный шум), не ингестированы.

## [2026-07-21] ingest | Реферальная система в подборе персонала — «Приведи друга» (ТЗ + План работ)
- Source: `.raw/Реферальная система в подборе персонала/` (2 md: `Техническое задание...md`, `План работ по проекту.md`)
- Summary: [[recruitment-referral-2026-07-21]]
- Pages created: [[RecruitmentReferral-Project]] (c-000197), [[RecruitmentReferral-TZ]] (c-000198), [[RecruitmentReferral-WorkPlan]] (c-000199), [[recruitment-referral-2026-07-21]] (c-000200)
- Pages updated: [[index]], [[hot]], [[domains/price-formation/_index]], [[SabyBank-RKO-Referral]], [[ReferralDeals-System]], [[ReferralStub-TargetAction-Pattern]]
- Key insight: третья реферальная вертикаль на едином ядре `ReferralProgram.*` + корешки `ВидЦеныДокумент` — после [[ReferralDeals-System|сделок]] и [[SabyBank-RKO-Referral|SabyBank РКО]]. Здесь целевой документ = «Кандидат на вакансию», партнёр = сотрудник аккаунта (без приглашения/договоров), вознаграждение может быть в рублях / вирт. валюте / бейдже. Применяется [[ReferralStub-TargetAction-Pattern]]: корешок создаётся целевым документом (кандидатом/откликом). Ранняя редакция: концепт связи «рефералка↔вакансия» не согласован, все оценки «? дней», много открытых развилок (где хранить источник — в отклике/кандидате; алгоритм соответствия вакансия→программа с иерархией организаций; наименование «Карьера» vs «Вакансии»). Мокапы UI (site-builder previewer + битые File.png) недоступны за авторизацией — не транскрибированы.
- Images: не ингестированы — скриншоты за SBIS-авторизацией + плейсхолдеры; интерактивные прототипы в Axure.

## [2026-07-20] save | DCQuestionary: не проставляется дата рождения существующему клиенту
- Type: decision
- Location: wiki/meta/DCQuestionary-BirthDay-Existing-Client-Bug.md
- From: баг №0625711 (регламент «Ошибка на стенде»), фикс в price-formation
- Key insight: собственная регрессия — апрельский MR !141867 фиксил перезапись BirthDay существующего клиента, убрав поле из `UpdateFields` целиком, и заодно исключил возможность впервые проставить ДР. `CRMClients.GetCustomerOrCreate` не поддерживает «update if empty» — переиспользуемый обходной путь (от ответственного за метод): `NeedSearchResult=True` → читать `SearchResult.<Field>` → точечный `CRMClients.SaveCustomer`, если пусто. Урок ревью: guard на пустоту поля должен быть fail-closed (`search_result and not search_result.Get(...)`), а не просто `not search_result.Get(...)` — иначе `SearchResult=None` воспроизводит тот же баг. Смежные находки (не фикшены): та же безусловная перезапись BirthDay в `helpers.py`/`process_file.py`.
- Pages created: [[DCQuestionary-BirthDay-Existing-Client-Bug]]
- Pages updated: [[index]], [[hot]]

## [2026-07-03] ingest | Перевод дизайна дисконтных карт на конструктор — 3 PDF
- Source: `.raw/Перевод дизайна дисконтных карт на конструктор/` (выборочно: `Техническое задание.pdf`, `Описание бизнес-процессов.pdf`, `План работ по проекту.pdf`; из 6 файлов папки — `План тестирования.pdf`, `Сравнение с конкурентами.pdf`, `Эксплуатация системы.pdf` не читались по решению пользователя)
- Summary: [[discount-card-design-constructor-2026-07-03]] — дизайн дисконтных карт (Wallet/GPay/оборотная сторона) переезжает с сервиса «Брендбук» на конструктор сайтов (site-builder), новый тип конструктора с прикладными объектами ПО ДизайнКарты и ПО КартаЛояльности, жёсткие Apple/Google-регламентированные слоты вместо свободного DnD
- Pages created: [[discount-card-design-constructor-2026-07-03]], [[DiscountCard-Design-Constructor-Project]], [[DiscountCard-Design-Constructor-Architecture]], [[DiscountCard-Design-Constructor-WorkPlan]]
- Pages updated: [[DiscountCard-Subsystem-Overview]], [[Ютман-Элина]], [[index]], [[hot]]
- Key insight: проект явно предписывает удалить настройки дизайна ДК с сервиса Брендбук после массовой конвертации (этап «Конвертация дизайна карты из брендбука», срок 01.07.2026–05.12.2026) — противоречие с существующей [[DiscountCard-Subsystem-Overview]] (описывает Брендбук как текущий источник настроек) отмечено `> [!contradiction]` на обеих страницах. Срок всего проекта 252,5 чд, финал 20.02.2027.

## [2026-07-03] ingest | Путь клиента — 17 PDF, новый движок сценариев лояльности (Маршруты)
- Source: `.raw/Путь клиента/` (17 PDF: Техническое задание, план работ, план тестирования, 3 итерации концептуального решения, 2 версии сценария «Реактивация неактивных клиентов», Брошенная корзина, Список УсловийДействий, Примеры сценариев со схемами, Блоки для сценариев лояльности, Конструкторы схем, Инсталляционные цепочки, События-действия, Сравнение с конкурентами (пусто), Эксплуатация системы (пусто))
- Method: 6 параллельных wiki-ingest агентов (без блокировок на страницы — `scripts/wiki-lock.sh`/`wiki-mode.py` не установлены в этом чекауте вопреки инструкциям скилла), затем orchestrator finalize pass (дедуп + address backfill + index/log/hot)
- Summary: [[CustomerJourney-Scenarios-Project]] — новый визуальный конструктор триггерных маркетинговых сценариев («Путь клиента» / Маршруты), строится поверх системы лояльности; конкурентный бенчмарк Mindbox/REES46 → согласованное ТЗ с API (`RouteService.*`), sequence-диаграммами, UI-декомпозицией
- Pages created: 17 source-страниц, 16 concept-страниц (10 канонических + 6 редиректов после дедупа), 12 entity-страниц (10 канонических + 2 редиректа) — полный список в [[domains/price-formation/_index]] §Customer Journey
- Pages updated: [[index]], [[concepts/_index]], [[entities/_index]], [[domains/price-formation/_index]], [[Loyalty-Product-Overview]], [[hot]]
- Dedup: параллельный ингест без локов породил 4 дублирующихся umbrella-страницы проекта (→ [[CustomerJourney-Scenarios-Project]]), 4 дублирующихся страницы архитектуры (→ [[Route-Platform-Architecture]]), 2 дублирующихся страницы сценария реактивации (→ [[LoyaltyScenario-ReactivationInactiveClients]]), 2 пары дублирующихся сущностей (Морозов/Морозов-Алексей-Васильевич, Чусовитин-А/Чусовитин-Александр). Все сведены в канонические страницы; дубликаты превращены в `status: merged` редиректы; ~120 wikilink-ссылок по вики переведены на канонические имена.
- Key insight: разрешено кажущееся противоречие «раннее исследование vs уже эксплуатируемая система» — это один и тот же новый продукт на разных стадиях мокапа (конкурентный бенчмарк → open-questions черновик → высокоточный мокап с демо-данными → согласованное ТЗ), а не два разных движка. Продуктовый гэп: сценарий «Брошенная корзина» требует авторизации клиента, но авторизация в SabyGet/сайтах-клиентах запрашивается поздно в воронке — окно анонимных действий не может быть привязано к клиенту.

## [2026-07-01] save | DiscountRegistry: убраны «пустые» запросы + корректировка про индексы
- Type: synthesis (обновление существующей страницы)
- Location: wiki/questions/DiscountRegistry-Revive-Performance.md
- From: реализация фикса hasMore в Promotion.GetSaleList (задача 12221993, 2-я итерация)
- Key insight: CTE `SaleDateBound` = точный MIN(EffectiveDate) LATERAL per-id (Index-Only-Scan, 8.5мс «Все» / 0.11мс узкая) обрывает итерацию на последней продаже. Правила: только LATERAL per-id (иначе backward-scan 47с), без tight-фильтров (9с). Индексы EffectiveDateSale/EffectiveDateDocument/EffectiveDate ЕСТЬ в PricingRetailOnline.dicx (проверено на стенде) — прежний тезис об их отсутствии опровергнут.
- Pages updated: [[DiscountRegistry-Revive-Performance]], [[index]], [[hot]]

## [2026-06-30] ingest | Звонок: Мусохранов — Тимошенко (сдача задачи корешков)
- Source: `.raw/Совещания/Звонок 2026-06-30 121753. Мусохранов Андрей, Тимошенко Александр.md`
- Summary: [[zvonok-musohranov-timoshenko-2026-06-30]]
- Pages created: [[zvonok-musohranov-timoshenko-2026-06-30]]
- Pages updated: [[wiki/index.md]], [[hot]]
- Key insight: Миграция корешков для существующих сделок — реализована, но проверка невозможна до выхода версии 400 (согласовано с Пиреновым); GUI не готов; сдавать как есть с декларацией планов.

## [2026-06-25] ingest | Совещание 23.06.26 — Сдача ТД: итеративная загрузка
- Source: `.raw/Совещания/Совещание 23.06.26 Сдача ТД.md`
- Summary: [[soveshanie-sdacha-td-itload-2026-06-23]]
- Pages created: [[soveshanie-sdacha-td-itload-2026-06-23]], [[Ютман-Элина]]
- Pages updated: [[Loyalty-IterativeLoading-TD-CommonSolutions]]
- Key insight: Второй итерационный ревью ТД по итеративной загрузке (Федько). Принято с замечаниями: переделать диаграмму иерархии классов (нечитаема), заменить «PriceFormation» на «BL» в архитектурной схеме, упростить описание EMA (формулу — под спойлер), добавить в документацию идею самоадаптации EMA. Согласование финального варианта — [[Ютман-Элина]].

## [2026-06-24] ingest | Звонок: Мусохранов — Тимошенко (ревью MR-ов)
- Source: `.raw/Совещания/Звонок 2026-06-24 093221. Мусохранов Андрей, Тимошенко Александр.md`
- Summary: [[zvonok-musohranov-timoshenko-2026-06-24]]
- Pages created: [[zvonok-musohranov-timoshenko-2026-06-24]], [[ReferralProgram-GetLeadPeriodList-LeadCount-Source]]
- Pages updated: [[ReferralProgram-Stub-Implementation]]
- Key insight: Цикл по источникам в GetLeadPeriodList запрещён — один запрос к ВидЦеныДокумент считает и LeadCount, и RewardSum; CreateLead→CreateStub требует регрессионных сценариев для старых рефералок.

## [2026-06-17] save | Bonus.GetTotalBalance — деградация на франшизе (~80k карт)
- Type: synthesis
- Location: wiki/questions/Bonus-GetTotalBalance-Franchise-Performance.md
- From: разбор задачи 05292113 (виджет «Бонусы» не строится, GetTotalBalance ~4.5 с)

## [2026-06-17] save | LoyaltyReferral Module Extraction
- Type: concept
- Location: wiki/concepts/LoyaltyReferral-Module-Extraction.md
- From: сессия по задаче 05256826 — заведение модуля LoyaltyReferral, зависимости, регистрация в сборках, echo-метод + тест, симлинки tests_new

## [2026-06-16] save | ReferralProgram SetPrice Record Return
- Type: concept
- Location: wiki/concepts/ReferralProgram-SetPrice-Record-Return.md
- From: доработка ReferralProgram.SetStubPrice/SetLeadPrice — возврат Record(AccruedCount, NotAccruedCount) по образцу DiscountCard.BatchDeleteOrLock (задача 04307161)

## [2026-06-16] save | DiscountRegistry Revive Performance
- Type: synthesis
- Location: wiki/questions/DiscountRegistry-Revive-Performance.md
- From: задача №12221993 — оптимизация оживления реестра «Скидки» Retail offline; вывод что BL ~15% времени (GetSaleList проксируется в облако, ~3 round-trip), конфликт push-down/индекс с EMA, выбран вариант C (UNION ALL + тюнинг блока)

## [2026-06-16] save | ReferralProgram GetLeadPeriodList — LeadCount источник
- Type: decision
- Location: wiki/meta/ReferralProgram-GetLeadPeriodList-LeadCount-Source.md
- From: задача №04307081 — `LeadCount` показывал только лиды с вознаграждением; для стандартных программ источник перенесён в маркетинг (`get_sales_sources_stats`), для SabyBank — ВЦД по `ДатаВремя`

## [2026-06-16] save | ReferralProgram Data Model
- Type: concept
- Location: wiki/concepts/ReferralProgram-Data-Model.md
- From: анализ задачи 06096778 (миграция оффера Т-банк между Реф. Сетями) — модель данных, access_data_guid, utm_rfcid, оценка задач

## [2026-06-15] save | Баг: удаление фичи entity_sp до полного раскатывания
- Type: synthesis
- Location: wiki/questions/entity-sp-deletion-order-2026-06-15.md
- From: bugfix #06108231 — не подтягивается точка продаж в диалог создания типа ДК на 26.4100; откат `1fb3ffbd1c` (35 файлов); ключевой принцип: фича удаляется только после 100% раскатки

## [2026-06-14] ingest | wasaby.Backend — Conan / STOMP / Mailings / Sync Broker / DWC full API / i18n extras (продолжение 9)
- Sources: 5 файлов (Conan, STOMP, массовые рассылки, облачный брокер синхронизации, DWC API)
- Pages created: [[Wasaby-Conan]] (c-000139), [[Wasaby-STOMP]] (c-000140), [[Wasaby-Mass-Mailings]] (c-000141), [[Wasaby-Sync-Broker]] (c-000142)
- Pages updated: [[Wasaby-DWC]] (full WorkflowBuilder/Sender API, .dwc metadata, merge policies), [[Wasaby-i18n]] (контекст перевода, роли ИмяРоли@@, системные секции ИмяУчасткаСистемы@@)
- Key insight: STOMP bus — 2-layer RabbitMQ: Route (AMQP from BL) → Web (WebSocket клиентам); Sync Broker хранит ФАКТЫ изменений, а не сами данные; MassDistribution = DWC per subscribed user

## [2026-06-14] ingest | wasaby.Backend batch — ЗАВЕРШЁН (итог)
- Sources: 557 файлов просмотрено; ~60 обработано; ~497 пропущено (ops/archived/roadmaps/training links/internal arch)
- Pages created: c-000105..c-000138 (34 новые страницы; [[Wasaby-Dev-Standards]], [[Wasaby-SQL-Standard]], [[Wasaby-Python-Standard]], [[Wasaby-Cpp-String-Standard]], [[Wasaby-Service-Framework]], [[Wasaby-BL-Calls]], [[Wasaby-BL-Objects]], [[Wasaby-Unit-Testing]], [[Wasaby-SQL-DBA]], [[Wasaby-Long-Running-Operations]], [[Wasaby-Task-Queue]], [[Wasaby-Service-Node-Architecture]], [[Wasaby-i18n]], [[Wasaby-Third-Party-Libraries]], [[Wasaby-Parameters-Service]], [[Wasaby-Distributed-Locks]], [[Wasaby-ClickHouse]], [[Wasaby-FTS]], [[Wasaby-File-Transfer]], [[Wasaby-Memray]], [[Wasaby-Perforator]], [[Wasaby-Python-Debug]], [[Wasaby-History-Service]], [[Wasaby-MQ]], [[Wasaby-Request-Broker]], [[Wasaby-Scheduler]], [[Wasaby-Report-Prefetch]], [[Wasaby-HTML-Converter]], [[Wasaby-Informers]], [[Wasaby-Multimedia-Loader]], [[Wasaby-PDF-Transformer]], [[Wasaby-Profiles-Service]], [[Wasaby-DWC]], [[Wasaby-Image-Service]])
- Key insight: Batch охватывает всё разработческое API Wasaby backend: от стандартов и фреймворка до middleware (MQ, брокеры, планировщик, кэш отчётов, конвертеры, информеры, профилировщики, отладка)

## [2026-06-14] ingest | wasaby.Backend batch — финализация (продолжение 8)
- Source: `.raw/wasaby.Backend/` — 3 файла (informers display, parameters-constants, prefetch arch)
- Pages created: none
- Pages updated: [[Wasaby-Informers]] (display config: excludesNames/includesNames + список стандартных), [[Wasaby-Parameters-Service]] (раздел parameters-constants)
- Key insight: informers отображением можно управлять через contentConfig страницы; parameters-constants = parameters без автоочистки + API для выборки по периоду действия

## [2026-06-14] ingest | wasaby.Backend batch — DWC / Image / Memray FAQ (продолжение 7)
- Source: `.raw/wasaby.Backend/` — 4 файла (img-remote, Memray FAQ, Perforator FAQ, DWC)
- Pages created: [[Wasaby-DWC]] (c-000137), [[Wasaby-Image-Service]] (c-000138)
- Pages updated: [[Wasaby-Memray]] (FAQ секция — 4 известные ошибки)
- Key insight: img-remote stateful — сессия = один BL вызов, нет публичного API, только через Image-BL; DWC = async граф задач с rate limiting

## [2026-06-14] ingest | wasaby.Backend batch — DWC + Profiles + MockService (продолжение 6)
- Source: `.raw/wasaby.Backend/` — 3 файла (DWC, Сервис Профилей, Моки внешних ресурсов)
- Pages created: [[Wasaby-Profiles-Service]] (c-000136), [[Wasaby-DWC]] (c-000137)
- Pages updated: [[Wasaby-Unit-Testing]] (полная таблица type hints для MockService + C++ тест с сервисом)
- Key insight: DWC = граф задач с rate-limiting и merge/dedup; Персона = UUID физлица (пользователь = 64-bit Client<<32|Лицо); MockService type hints — 28 типов Python→Saby

## [2026-06-14] ingest | wasaby.Backend batch — Multimedia-Loader / PDF-Transformer (продолжение 5)
- Source: `.raw/wasaby.Backend/Middleware/` — 2 файла
- Pages created: [[Wasaby-Multimedia-Loader]] (c-000134), [[Wasaby-PDF-Transformer]] (c-000135)
- Key insight: Multimedia Loader поддерживает пользовательские pipeline с операциями Antivirus/MimeTypes/ToFileTransfer; PDF Transformer конвертирует PDF→PDF/A с 11 уровнями соответствия (Level1A..Level4F)

## [2026-06-14] ingest | wasaby.Backend batch — Сервисы общего назначения (продолжение 4)
- Source: `.raw/wasaby.Backend/Сервисы общего назначения/` — 5 файлов
- Pages created: [[Wasaby-HTML-Converter]] (c-000132), [[Wasaby-Informers]] (c-000133)
- Key insight: HTML Converter поддерживает delayed print — JS должен вызывать waitPrint()/startPrint(); Informers хранят данные в Redis и имеют механизм восстановления через планировщик (100мс)

## [2026-06-14] ingest | wasaby.Backend batch — Отладка/Профилирование/MQ/Middleware (продолжение 3)
- Source: `.raw/wasaby.Backend/` — 17 файлов из 4 разделов (Отладка, Middleware)
- Pages created: [[Wasaby-Memray]] (c-000124), [[Wasaby-Perforator]] (c-000125), [[Wasaby-Python-Debug]] (c-000126), [[Wasaby-History-Service]] (c-000127), [[Wasaby-MQ]] (c-000128), [[Wasaby-Request-Broker]] (c-000129), [[Wasaby-Scheduler]] (c-000130), [[Wasaby-Report-Prefetch]] (c-000131)
- Pages updated: [[Wasaby-Unit-Testing]] (C++ CMakeLists mock setup)
- Key insight: PyCharm Remote Debug ограничен версией 2022.3.3 (нет лицензий JetBrains); Prefetch.List должен содержать PrefetchPreSort иначе иерархия ломается; request-broker в отличие от RabbitMQ позволяет отследить статус конкретного запроса

## [2026-06-14] ingest | wasaby.Backend batch — Конфигурация сервиса/i18n/Инструменты/Middleware (продолжение)
- Source: `.raw/wasaby.Backend/` — 14 файлов из 5 разделов
- Pages created: [[Wasaby-Service-Node-Architecture]] (c-000116), [[Wasaby-i18n]] (c-000117), [[Wasaby-Third-Party-Libraries]] (c-000118), [[Wasaby-Parameters-Service]] (c-000119), [[Wasaby-Distributed-Locks]] (c-000120)
- Key insight: distributed-locks ключ ресурса не содержит account/user — разработчик обязан добавить их самостоятельно во избежание пересечений в мультитенантном окружении

## [2026-06-14] ingest | wasaby.Backend batch — Стандарты/Сервисный фреймворк/Отладка/SQL DBA/Middleware
- Source: `.raw/wasaby.Backend/` — 27 файлов из 5 разделов
- Pages created: [[Wasaby-Dev-Standards]] (c-000105), [[Wasaby-SQL-Standard]] (c-000106), [[Wasaby-Python-Standard]] (c-000107), [[Wasaby-Cpp-String-Standard]] (c-000108), [[Wasaby-Service-Framework]] (c-000109), [[Wasaby-BL-Calls]] (c-000110), [[Wasaby-BL-Objects]] (c-000111), [[Wasaby-Unit-Testing]] (c-000112), [[Wasaby-SQL-DBA]] (c-000113), [[Wasaby-Long-Running-Operations]] (c-000114), [[Wasaby-Task-Queue]] (c-000115)
- Key insight: SQL/DBA/Antipatterns/HowTo файлы — дайджесты статей Habr, не внутренняя документация. Ключевой инструмент: explain.tensor.ru

## [2026-06-13] save | Wasaby-Scripts — sbis.Record API и паттерн сбора данных
- Type: concept update
- Location: wiki/concepts/Wasaby-Scripts.md
- From: ВНР для анализа безымянных ДК (поручение №06035683, баг №04228789); уточнены методы sbis.Record (AddInt64/AddInt32/AddString/AddBool, не AddInteger); добавлен паттерн скрипта сбора статистики

## [2026-06-12] ingest | Async/Sync BL вызовы в облаке — сессия 7
- Source: `.raw/Синхронный и асинхронный вызов метода БЛ в облаке.md`
- Created: [[Wasaby-BL-Async-Sync-Cloud-Calls]] (c-000105) — BLObject/EndPoint/AsyncInvoke API, auth (AuthByClientID/ExtID/UserID/Login), приоритеты (rpNORMAL/rpLOW, SetAsyncPriority 0-9), гарантированная доставка (AMQP/RBC), HugePayload Protocol, callbacks (callback+errback+context), очереди брокера, SetRepeatCnt
- No changes: `.raw/Скрипты.md` (already covered by Wasaby-Scripts), `.raw/Как разрабатывать в RetailPresto-offline 2025.md` + `.raw/Просмотр диалога по инструкции с подменой модулей.md` (already comprehensive in RetailPresto-Offline-Debug-Setup c-000074)

## [2026-06-12] ingest | Система обновлений — продолжение (сессия 6)
- Source: `.raw/Система обновлений/` — Планы выпуска ТД (25 стр), ХД sub-docs (Алгоритмы/Архитектура/Организация/БД/Параметры), Конвертация БД sub-docs, Типы обновлений (Лёгкое/Полное/Патчи/Скрипты/Кластеры), Регистрация метаданных sub-docs, Реестр работ, Экспорт в изолированные облака
- Updated: [[UpdateSystem-ReleasePlans]] (c-000083) — scheduler task methods (WorkRunAllWaitingWorks/PlanMassRecalcDivergence/PlanClearArchivedPlans/PlanClearOldActiveTaskStatus), автономные планы (clone/sync), признак исполнения в облаке (CloudWorkStatus logic), `FeatureCommit(feature_id)`, обновление кластеров (волна/папка), реестр работ, зависимости с пропущенными работами
- Updated: [[UpdateSystem-DistributionStorage]] (c-000078) — схема БД (16 таблиц с описаниями, ключевые индексы, алгоритм дедупликации и ref-counting)
- No changes: Wasaby-Scripts, UpdateSystem-Patches, UpdateSystem-UpdateTypes, UpdateSystem-MetadataRegistration, UpdateSystem-DBConversion — already comprehensive
- Confirmed as user-facing docs with no developer content: Реестр работ.pdf, Экспорт планов.pdf, Разворот данных.pdf, Развертывание.pdf, Общие БД.pdf

## [2026-06-12] ingest | Система обновлений — продолжение (сессия 5)
- Source: `.raw/Система обновлений/` — Хранилище дистрибутивов ТД (5 PDF), Конвертация БД ТД (3 PDF), Управление версиями ТД (62 стр), update.saby.ru ТД (7 стр), Регистрация метаданных ТД (6 стр)
- Updated: [[UpdateSystem-VersionControl-TD]] (c-000102) — VersionManagerCommandToAgent API, agent events, FastMove, ServiceFilesMover, AbstractSvcPartsManager, modules.json format, кластерный update (Custom Resources)
- Updated: [[UpdateSystem-DistributionStorage]] (c-000078) — Организация кода (DiskClient, Workflow Coordinator Client, PermissionChecker), уточнён GIT-репозиторий
- No new pages created (existing pages already comprehensive)
- Key additions: VersionManagerCommandToAgent JSON format (Agents/Operation params), server events versionmanager:agent_operation_*, FastMove C++ algorithm (rename → copy fallback), modules.json struct (bl_modules/ui_modules: link/revision/version)

## [2026-06-12] ingest | Система обновлений — продолжение (сессия 3)
- Source: `.raw/Система обновлений/` — update.saby.ru ТД, Планы выпуска ТД (25 стр), ХД схема БД
- Created: [[UpdateSystem-DistributionStorage-DB]] (c-000103)
- Updated: [[UpdateSystem-UpdateSabyRu]] (c-000084) — API master-сервера (GET/POST /api/sync/{id}), GIT-репозитории 7 компонентов
- Updated: [[UpdateSystem-ReleasePlans]] (c-000083) — автозаполнение (7 типов работ), схема БД (индексы), 28 облачных параметров (Предел нагрузки, ПриложенияПервойВолны, ВесБаза данных=2 и др.)
- Key additions: md5-дедупликация загрузки, ref-counting удаления, ModuleVersion uniqueness (Name,Type,Revision), балансировщик в K8s (HELM-чарт)

## [2026-06-12] ingest | Система обновлений — продолжение (сессия 2)
- Source: `.raw/Система обновлений/` — глубокий re-ingest Управление версиями ТД (62 стр), Патчи, ХД-компоненты
- Created: [[UpdateSystem-Patches]] (c-000101), [[UpdateSystem-VersionControl-TD]] (c-000102)
- Updated: [[UpdateSystem-MetadataRegistration]] (c-000082), [[UpdateSystem-DistributionStorage]] (c-000078)
- Key additions: МАО task graph (12 типов, 7 фаз), DeveloperScriptExecuteAll params, saby-package generation, publication heartbeat/callback, cross-cloud loading

## [2026-06-12] ingest | Система обновлений Saby — массовый инжест (80+ PDF)
- Source: `.raw/Система обновлений/` — 8 подсистем: Хоттабыч, update.saby.ru, Конвертация БД, Планы выпуска, Регистрация метаданных, Реестр работ, Управление версиями, Хранилище дистрибутивов
- Created: 17 concept pages (c-000076..c-000092), 8 source pages (c-000093..c-000100)
- Key pages: [[Хоттабыч-System]], [[UpdateSystem-UpdateTypes]], [[UpdateSystem-MetadataRegistration]], [[UpdateSystem-DBConversion]], [[UpdateSystem-DistributionStorage]], [[UpdateSystem-UpdateSabyRu]], [[UpdateSystem-ReleasePlans]]
- Method: 10 parallel wiki-ingest agents + orchestrator PDF extraction (pypdf) + manual page writing

## [2026-06-11] save | Loyalty Iterative Loading — ТД и предложение «Общие решения»
- Type: decision
- Location: wiki/meta/Loyalty-IterativeLoading-TD-CommonSolutions.md
- From: написание ТД итеративной загрузки (пункт 594287653); решение по размещению (мастер в Бонусах + ссылки), факты иерархии классов на 4100, предложение раздела БЗ «Общие решения» для Федько
- Updated: [[LoyaltyPrograms-IterativeListLoading]] (заметка про иерархию 4100)

## [2026-06-11] ingest | Как разрабатывать в RetailPresto-offline [2025] + диалог о подмене модулей
- Source: `raw/Как разрабатывать в RetailPresto-offline 2025.md`, `raw/Просмотр диалога по инструкции с подменой модулей.md`
- Summary: [[retail-presto-offline-dev-2025]]
- Pages created: [[RetailPresto-Offline-Debug-Setup]] (c-000074), [[retail-presto-offline-dev-2025]] (c-000075)
- Pages updated: [[Loyalty-In-Products]], [[index]], [[log]], [[hot]]
- Key insight: С v25.6218 ресурсы офлайн-приложений предкомпилируются — нужна явная подмена через MainService.s3srv + sbis-config.ini; только Debug-версия.

## [2026-06-11] save | PromoCode-NotifyGenerated-DWC-Ordering
- Type: synthesis
- Location: wiki/questions/PromoCode-NotifyGenerated-DWC-Ordering.md
- From: разбор регресса таймаут-фикса — синхронный notify SabyGet слал пустой PersonID после выноса AttachPersonId в фоновый DWC
- Key insight: зависимость «notify после attach» = барьер → DWC (а не AsyncInvoke); `NotifyGenerated` финальной задачей того же сценария; `AddTask` без `OpenParallelBlock` = строго последовательно; распространяется на все типы генерации
- Pages updated: [[index]], [[hot]], [[GetIndividualBatch-AttachPersonId-Timeout-Fix]]

## [2026-06-11] ingest | Синхронный и асинхронный вызов метода БЛ в облаке
- Source: `.raw/Синхронный и асинхронный вызов метода БЛ в облаке.md`
- Summary: [[wasaby-bl-async-invoke-2026-06-11]]
- Pages created: [[Wasaby-BL-AsyncInvoke]] (c-000073)
- Pages updated: [[Async-Calls-Bus]], [[index]], [[hot]]
- Key insight: `AsyncInvoke` всегда rpLOW + служебный пул; гарантированная доставка AMQP/RBC может повторить вызов; лимит тела 100 КБ (Huge Payload Protocol для большего).

## [2026-06-11] save | PromoCode-Generation-Memory-Optimization — РЕАЛИЗОВАНО
- Type: synthesis update (status developing → fixed)
- Location: wiki/concepts/PromoCode-Generation-Memory-Optimization.md
- From: баг #06104810 (стенд dev.sbis.ru) — `IndividualPromoCodeEmission.Generate/1` 5.689с
- Key: (1) `sql_filter_existing_numbers` — `ANY($1::text[])` по индексу вместо full scan; (2) `filter_taken: Callable` callback в `PromoCodesGenerator`; (3) `_skip_license: bool = False` в `update()` — устраняет дублирование лицензионной проверки при внутреннем вызове из Python; ParallelTasks-изменение откатили — отдельная задача. 13 тестов ✓.
- Pages updated: [[PromoCode-Generation-Memory-Optimization]], [[index]], [[hot]]

## [2026-06-10] save | CardEmission-FullResync-PK-Conflict-Fix
- Type: synthesis
- Location: wiki/questions/CardEmission-FullResync-PK-Conflict-Fix.md
- From: баг №06084819 «Ошибка на стенде», фича lty_broker_sync — принудительная полная пересинхронизация выпусков карт падала на duplicate key
- Key: upsert `_sql_upsert_card_emissions` (ВидКарты): UPDATE отбирает только DISTINCT строки → существующая неизменённая запись проходит `Updated IS NULL` и уходит в INSERT → конфликт PK. Фикс — `AND NOT EXISTS (SELECT NULL FROM "ВидКарты" WHERE "@ВидКарты" = Data."@ВидКарты")` в CTE Inserted (диагноз и фикс от автора файла Михайленко Е.А.). Регресс-тест test_resync_unchanged_record.
- Pages updated: [[CardEmission-FullResync-PK-Conflict-Fix]], [[index]], [[hot]]

## [2026-06-10] save | GetIndividualBatch-AttachPersonId-Timeout-Fix — РЕШЕНО
- Type: question update (status developing → fixed)
- Location: wiki/questions/GetIndividualBatch-AttachPersonId-Timeout-Fix.md
- From: реализация фикса бага #04295801 в price-formation
- Key: привязка персон вынесена в фоновый DWC `IndividualPromoCodeEmission.AttachPersons` с **one_task="0"** (устраняет рассинхрон, ронявший попытку 08–09.06 при one_task="1"); задача маппится на CRMClients.AttachPersonId напрямую; generate.py — _start_attach_persons_dwc после транзакции вместо ParallelTasks. Без чанков, без фича-флага. Ветка rc-26.3211 → 26.3211/bugfix/aatimoshenko/04295801_2. Тесты 8/8, pylint 10/10.
- Pages updated: [[GetIndividualBatch-AttachPersonId-Timeout-Fix]], [[hot]], [[index]]

## [2026-06-10] save | PromoCode-Generation-Memory-Optimization
- Type: synthesis
- Location: wiki/concepts/PromoCode-Generation-Memory-Optimization.md
- From: проектирование в price-formation — как генерировать промокоды с учётом существующих без выгрузки всей «Карта» в память; решение: батчевая проверка кандидатов одним индексным запросом (CaseInsensitiveUniqueNumber); реализация отложена

## [2026-06-09] save | Прогресс плана июнь 2026 — вечер 09.06
- Type: source update
- Location: wiki/sources/sbis-plan-june-2026.md (добавлена секция «Прогресс на 09.06.2026»)
- From: автоматический loop-анализ плана в 22:20; данные SBIS API + git log
- Key: 3 задачи смержены (entity_sp/bonus_it_nav/Валюта), ReadStub расширен; факт-часы 47.4ч (+6.3ч); текущая ветка 05133949_2; совещания 10.06 по #05216996 и #05145004

## [2026-06-09] ingest | SBIS: План работ Система лояльности июнь 2026
- Source: SBIS API (plan_id=580667071, ПланРабот.СписокПланов + ПунктПлана.*)
- Summary: [[sbis-plan-june-2026]]
- Pages created: [[sbis-plan-june-2026]]
- Pages updated: [[index]], [[hot]]
- Key insight: 19 пунктов / 37.3ч план; основные темы — SabyBank RKO Referral (Свешников), переход реферальной системы на корешки (Мусохранов), DWC внедрение, удаление фич entity_sp/loyalty_it_nav.

## [2026-06-09] save | Claude-Code-VseGPT-Provider
- Type: concept
- Location: wiki/concepts/Claude-Code-VseGPT-Provider.md
- From: конфигурация Claude Code для работы через VseGPT (vsegpt.ru): ANTHROPIC_BASE_URL, токен, маппинг Haiku/Sonnet/Opus на moonshotai/kimi-k2.5

## [2026-06-08] save | Bonus-GetSaleList-Duplicate-W-Records-Iterative-Block-Bug
- Type: synthesis
- Location: wiki/concepts/Bonus-GetSaleList-Duplicate-W-Records-Iterative-Block-Bug.md
- From: bug fix — дубли Id="W37328" в реестре Бонусы/Покупки; root cause: BonusSaleListIterative разрезает СУ-документ с двумя ВЦД по границе итеративного блока; фикс: SuspectWarehouseDocs + SuspectSaleIds CTE; тест test_8; 49/49 зелёных

## [2026-06-05] fold | batch-exponent-k4 rollup of 16 entries
- Location: wiki/folds/fold-k4-from-2026-05-21-to-2026-06-05-n16.md
- Range: 2026-05-21 to 2026-06-05
- Children: 16 log entries

## [2026-06-05] save | GetClientListWithStatsTotals-Franchise-WelcomeBonus-Double-Bug
- Type: synthesis
- Location: wiki/concepts/GetClientListWithStatsTotals-Franchise-WelcomeBonus-Double-Bug.md
- From: bug fix — двойной учёт приветственных бонусов франшизной ДК в итогах Бонусы\Клиенты; root cause в is_totals-ветке SQL; один коммит 2fd6bbff исправил только standalone-путь
## [2026-06-05] decision | Feature-Flag-Removal-LOYALTY-IT-NAV
- Type: decision
- Location: wiki/meta/Feature-Flag-Removal-LOYALTY-IT-NAV.md
- From: удаление фич `loyalty_it_nav` / `bonus_it_navigation`; итеративная навигация стала постоянной; слияние классов, фикс тестов; связано с [[Loyalty-React-Migration-Project]]

## [2026-06-04] ingest | Вызов БЛ-метода под другим клиентом+юзером без петли (SBIS Forum wasaby.Backend, 10.07.2025)
- Source: [[wasaby-cross-client-call-2026-06-04]]
- Pages created: [[Wasaby-Cross-Client-BL-Call]]
- Pages updated: [[Multitenancy-Architecture]], [[sources/_index]]
- Key insight: AuthByClientAndUserId — правильный способ вызвать подметод в аккаунте 2 под нужным пользователем; CreateMultitenantEndpointByClientId только переключает клиента, не пользователя; Session.Set(icsSESSION_ID) как альтернативный workaround.

## [2026-06-04] ingest | Петля вызовов при смене пользователя (SBIS Forum, 05.08.2025)
- Source: [[wasaby-bl-call-loop-user-switch-2026-06-04]]
- Pages created: [[Wasaby-BL-Call-Loop-Pattern]]
- Pages updated: [[concepts/_index]], [[sources/_index]], [[index]]
- Key insight: При вызове БЛ-метода под другим пользователем того же аккаунта (тот же ClientID) через `sbis.EndPoint+auth_data` образуется петля; решение — `CreateMultitenantEndpointByClientId`. `TenantContext` петлю НЕ устраняет.

## [2026-06-04] update | ReferralProgram Stub Implementation — ReadStub расширен, Events RecordSet
- Pages updated: [[ReferralProgram-Stub-Implementation]]
- Source: задача 05293691 — добавление полей в ReadStub, CreateStub, UpdateStub
- Key changes: ReadStub возвращает Description/ContactName/ContactPhone/ContactEmail + Events RecordSet (1–2 элемента: создание + финальный статус). Status/StatusDate не дублируются в Атрибуты — только в ТипСвязи/EffectiveDate. sbis.rk('Заявка создана') + перевод en.json. Все 26 тестов зелёные.

## [2026-05-28] save | ReferralProgram.GetStubList — редизайн фильтров
- Type: decision
- Location: wiki/meta/ReferralProgram-GetStubList-Filter-Redesign.md
- From: редизайн контракта GetStubList — единый Date-фильтр, PartnerId, обновление orx и тестов

## [2026-05-28] ingest | Свешников А. — мысли о создании корешков в классической рефералке
- Source: pasted message (Свешников Андрей, 2026-05-28)
- Summary: [[sveshnikov-stub-creation-thoughts-2026-05-28]]
- Pages created: [[sveshnikov-stub-creation-thoughts-2026-05-28]], [[ReferralStub-TargetAction-Pattern]], [[Свешников-Андрей]]
- Pages updated: [[SabyBank-RKO-Referral]]
- Key insight: Корешок должен создаваться документом с целевым действием (заявкой в ЦРМ/банке/кандидатом), а не кнопкой партнёра — кнопка создаёт только заявку с правильным источником.

## [2026-05-27] update | DWC-Card-Events-Migration — удалён HandleChangeBonusBalance, cherry-pick rc-26.4100
- Pages updated: [[DWC-Card-Events-Migration]]
- Source: сессия cherry-pick + ревью Лены (Михайленко Е.А.)
- Key insight: Отдельный `Card.HandleChangeBonusBalance` удалён — `notify_bonus_balance_changed` делегирует в `notify_card_data_changed` → `Card.HandleChangeData`. Все 4 события карты перенесены в rc-26.4100 (коммиты ab540e63, 7ee44e16, 9bd14b6e, 3b8cb1e0).

## [2026-05-26] update | Wasaby-Scripts.md — структура ВНР-архивов из реальных примеров
- Pages updated: [[Wasaby-Scripts]]
- Source: 5 реальных архивов `s_timoshenkoaa_*.zip` из `PriceFormation.Online/`
- Key insight: Основной Python-файл всегда `developer_script.py` с entry point `run_script()`; файлы `*_cloud_clients` (plain text, один ClientID) для per-environment dispatch; `access_mode="1"` для клиентоспецифичных скриптов; паттерн `is_local_stand` + `DeveloperScriptAPI.LogMsg`. Шаблоны выведены из боевых архивов, не претендуют на идеал.

## [2026-05-26] save | Backward-фикс порядка графиков/итогов (04297958 → 04307024)
- Type: concept (update)
- Location: wiki/concepts/ReferralBonus-GetSaleList-Iterative-Ordering-Bug.md
- From: сессия фикса хаотичного порядка при скролле вверх в реестре «Реферальная система/Покупки»
- Key insight: backward → ASC-данные, фронт разворачивает их при prepend; `add_graphic_data` (общий метод) вставляла график/итоги по DESC-логике. Фикс: для `navigation.Direction()==ndBACKWARD` зеркалить вставку (итоги ДО FirstId, график ПОСЛЕ LastId). Инвариант теста: `reversed(backward)==forward`. Покрывает Bonus/PromoCode/Promotion/Referral сразу. Реализовано Opus 4.7.

## [2026-05-26] ingest | Оргструктура: Система лояльности, Транспорт ВИС
- Source: pasted text (корпоративный портал СБИС)
- Summary: [[loyalty-vis-org-2026-05-26]]
- Pages created: [[Мусохранов-Андрей-Владиславович]] (c-000036), [[Федько-Юрий-Сергеевич]] (c-000037), [[Алябушев-Александр-Александрович]] (c-000038), [[Омельяненко-Егор-Анатольевич]] (c-000039), [[Курников-Михаил-Сергеевич]] (c-000040), [[Дюднева-Светлана-Андреевна]] (c-000041), [[Чумакин-Андрей-Андреевич]] (c-000042), [[Loyalty-System-Teams]] (c-000043), [[Transport-VIS-Platform]] (c-000044)
- Pages updated: [[Тимошенко А.А.]], [[Tensor-Company]], [[index]]
- Key insight: Зафиксирована полная оргструктура направления — 4 backend/frontend/QA команды под [[Федько-Юрий-Сергеевич]], всё направление + [[Transport-VIS-Platform]] под [[Мусохранов-Андрей-Владиславович]]; [[Омельяненко-Егор-Анатольевич]] — непосредственный руководитель [[Тимошенко А.А.]].

## [2026-05-25] entity | Тимошенко А.А. — создана страница разработчика
- Page created: [[Тимошенко А.А.]]
- Pages updated: [[entities/_index]], [[index]], [[SabyBank-RKO-Referral]], [[DWC-Migration-SDK]], [[DWC-Promocode-Events-Migration]], [[DWC-BonusSettings-Events-Migration]], [[Linter-Standarization-Project]], [[AT-Coverage-ReferralDeals-Project]], [[Loyalty-React-Migration-Project]]
- Key insight: Тимошенко А.А. — инженер-программист 2+, Тензор; команда лояльности на продаже (backend), руководитель Омельяненко Е.А.; ответственный за BL SabyBank RKO Referral и все промокодные задачи DWC-Migration.

## [2026-05-25] ingest | Batch — 5 sources (2 new, 3 updated)
- Sources: `.raw/Звонок 25.05.2026 16-06.md`, `.raw/Летучка 22.05.26.md`, `.raw/Объект «Навигация» в API.md`, `.raw/Формат протокола JSON-RPC.md`, `.raw/Эффективная работа с удаленными запросами. Shared future.md`
- Pages created: [[SabyBank-Application-Card-Conversation-2026-05-25]] (c-000035)
- Pages updated: [[SabyBank-RKO-Referral]], [[GetIndividualBatch-AttachPersonId-Timeout-Fix]], [[SBIS-Record-Format]]
- Key insight: Мусохранов делегировал Тимошенко полное владение задачей карточки заявки; открытые вопросы по данным ожидают ответа Свешникова. Омельяненко подтвердил DWC-подход для AttachPersonId на летучке 22.05.

## [2026-05-25] save | GetClientListWithStats-PA-NavCondition-Duplicate-Bug
- Type: bugfix
- Location: wiki/concepts/GetClientListWithStats-PA-NavCondition-Duplicate-Bug.md
- Key: pa_nav_condition (оптимизация из [[PostgreSQL-CTE-Cursor-Pushdown]]) давала дубли CardId при скроллинге — предфильтр курсора только в personal_accounts, но не в cards_only → клиент с личной+номерной картой с разными датами появлялся на двух страницах. Фикс: убрана оптимизация целиком. 28 тестов OK.

## [2026-05-25] save | GetIndividualBatch-AttachPersonId-Timeout-Fix
- Type: synthesis (developing)
- Location: wiki/questions/GetIndividualBatch-AttachPersonId-Timeout-Fix.md
- From: анализ таймаута PromoCode.GetIndividualBatch; два варианта DWC-решения, вариант B (вся генерация в DWC) обсуждается

## [2026-05-22] save | ReferralProgram-GetPartnerList-Unjoined-Partners
- Type: project implementation
- Location: wiki/ReferralProgram-GetPartnerList-Unjoined-Partners.md
- Key: GetPartnerList переписан с INNER JOIN Карта → CTE AcceptedPartners (unnest) + LEFT JOIN; курсор PartnerId; SearchString в Python; Name из AgentContract для незаджойненных; 11 тестов OK

## 2026-05-22 ingest | Эффективная работа с удаленными запросами. Shared future
- Source: `.raw/Эффективная работа с удаленными запросами. Shared future.md`
- Summary: [[wasaby-sharedfuture-2026-05-22]]
- Pages created: [[Wasaby-SharedFuture]], [[wasaby-sharedfuture-2026-05-22]]
- Pages updated: [[Wasaby-App-Optimization]]
- Key insight: `FutureInvoke` / `ParallelTasks` снижает суммарное время N параллельных DB-запросов до времени самого долгого; лимит 16 потоков, при превышении — синхронный fallback.

## [2026-05-21] save | SBIS Browser-to-API Conversion
- Type: concept
- Location: wiki/concepts/SBIS-Browser-to-API-Conversion.md
- From: реализация DocumentMessage.ListForEDO в sbis-mcp — паттерн преобразования браузерных запросов

## [2026-05-21] save | SBIS DocumentMessage.ListForEDO
- Type: concept
- Location: wiki/concepts/SBIS-DocumentMessage-ListForEDO.md
- From: реализация MCP-инструмента sbis_list_task_messages в проекте sbis-mcp

## 2026-05-21 ingest | Формат протокола JSON-RPC (wasaby.Backend)
- Source: `.raw/Формат протокола JSON-RPC.md`
- Summary: [[sbis-jsonrpc-protocol-format]]
- Pages created: [[sbis-jsonrpc-protocol-format]]
- Pages updated: [[SBIS-Record-Format]]
- Key insight: Protocol 1/2 использует `d`/`s` как JSON-объекты; Protocol 3+ (включая 7) — массивы. Ошибка "Блок данных должен быть объектом" = несоответствие версий протокола.
  - "[[hot]]"
  - "[[overview]]"
  - "[[sources/_index]]"
---

## [2026-05-21] ingest | Saby External API — объекты, протокол, типы данных (8 sources)
- Source: `.raw/Объект «Документ» в API.md`, `.raw/Объект «Навигация» в API.md`, `.raw/Структура данных API-интерфейса.md`, `.raw/Типы данных в API Saby.md`, `.raw/Формат протокола JSON-RPC в API.md`, `.raw/Форматы строк API.md` (новые); `.raw/Поддержка запроса прав доступа.md`, `.raw/Справочник кодов ошибок API Saby...md` (re-hash)
- Summary: [[saby-api-docs-objects-2026-05-21]]
- Pages created: [[Saby-API-Document-Object]] (c-000028), [[Saby-API-Navigation-Object]] (c-000029), [[Saby-API-Protocol]] (c-000030), [[saby-api-docs-objects-2026-05-21]] (c-000031)
- Pages updated: [[index]], [[hot]]
- Key insight: Объект «Документ» — центральный объект EDI API; идентификаторы участников нестабильны (хранить только `СсылкаДляКонтрагент`); `details` в JSON-RPC ошибке — только для лога, не для UI; реквизиты формализованного документа передавать полным набором.

## [2026-05-21] ingest | SBIS API Reference — sbis-mcp project (docs/sbis-api.md)
- Source: `C:/Users/aa.timoshenko/PycharmProjects/sbis-mcp/docs/sbis-api.md`
- Summary: [[sbis-api-sbis-mcp-2026-05-21]]
- Pages created: [[SBIS-Record-Format]] (c-000025), [[SBIS-Internal-API-Methods]] (c-000026), [[sbis-api-sbis-mcp-2026-05-21]] (c-000027)
- Pages updated: [[index]]
- Key insight: Внутренний SBIS API использует колоночный формат f/d/s для всех структур данных (включая Фильтр/Навигация); `ПунктПлана.СписокПунктов` принципиально отличается от внешнего `СБИС.СписокЗадач` — другие параметры, другой формат ответа с 93+ полями.

## [2026-05-21] ingest | Saby External API — Auth & Tasks (6 sources)
- Source: `.raw/Пройти аутентификацию с помощью API...md`, `.raw/СБИС.Аутентифицировать.md`, `.raw/СБИС.Выход.md`, `.raw/СБИС.ИнформацияОТекущемПользователе.md`, `.raw/СБИС.СписокЗадач.md`, `.raw/Справочник кодов ошибок API Saby...md`
- Summary: [[saby-api-docs-2026-05-21]]
- Pages created: [[Saby-External-API-Auth]], [[Saby-External-API-Tasks]], [[Saby-API-Error-Codes]], [[saby-api-docs-2026-05-21]]
- Pages updated: [[index]]
- Key insight: Внешний API Saby использует сессионную аутентификацию (`X-SBISSessionID`); SMS 2FA через classid `1FA000001002`; `СБИС.СписокЗадач` с курсорной пагинацией по unix-timestamp.

## [2026-05-20] save | SabyBank-Stub-Rewards-Calculation
- Type: concept
- Location: wiki/concepts/SabyBank-Stub-Rewards-Calculation.md
- From: переход GetLeadPeriodList и sql_get_price_stats (GetStats/GetStatsByPartner) на калькуляцию по корешкам (ТипСвязи IS NOT NULL) для программ SabyBank; SQL-паттерн `<> 1 OR ТипСвязи IS NOT NULL`; тесты с двухшаговым PriceEntitySaleDoc+PriceEntityRetailSaleDoc паттерном

## [2026-05-20] save | BonusChart-IterativeBlock-Bug-Fix
- Type: synthesis
- Location: wiki/questions/BonusChart-IterativeBlock-Bug-Fix.md
- From: фикс бага с кривыми данными графика продаж при loyalty_it_nav — итеративный блок ВЦД обрезал данные до конца месяца

# Operation Log

## [2026-05-20] save | Price-Formation Test Runner
- Type: concept
- Location: wiki/concepts/Price-Formation-Test-Runner.md
- From: conversation о запуске тестов price-formation на уровне класса/файла/модуля, инфраструктуре test_framework и создании /run-tests skill

Navigation: [[index]] | [[hot]] | [[overview]]

Append-only. New entries go at the TOP. Never edit past entries.

## [2026-05-19] save | SetLeadPrice-SABYBANK-Stub-Branch
- Type: concept
- Location: wiki/concepts/SetLeadPrice-SABYBANK-Stub-Branch.md
- From: доработка ReferralProgram.SetLeadPrice — для программ типа SABYBANK вознаграждение записывается в корешок (@ВидЦеныДокумент) вместо документа сделки (Документ); новый SQL, ветвление по ProgramType, обновление .orx, тест test_2_sabybank_stub

## [2026-05-19] save | Bonus GetSaleTotals Timeout Fix
- Type: bugfix / investigation
- Location: wiki/concepts/Bonus-GetSaleTotals-Timeout-Fix.md
- From: таймаут Bonus.GetSaleTotals на больших аккаунтах; root cause: _get_first_sale_date → MIN(EffectiveDate) без фильтра по дате → 17s / 3M строк / 5ГБ; нет подходящего индекса; два варианта: новый индекс (ВидЦены, EffectiveDate) vs bounded loop 24 мес; реализован вариант 2, в shelf, на согласовании

## [2026-05-19] save | ReferralBonus GetSaleList Iterative Ordering Bug
- Type: synthesis
- Location: wiki/concepts/ReferralBonus-GetSaleList-Iterative-Ordering-Bug.md
- From: расследование бага порядка записей в ReferralBonus.GetSaleList (loyalty_it_nav); GROUP BY (Sale, EffectiveDate) → дубли; missing secondary sort; fix + тест

## [2026-05-19] ingest | SBIS Access Request API
- Source: `.raw/API Запросы доступа.md`, `.raw/Поддержка запроса прав доступа.md`
- Summary: [[sbis-access-request-2026-05-19]]
- Pages created: [[SBIS-Access-Request-API]] (c-000019), [[sbis-access-request-2026-05-19]] (c-000020)
- Pages updated: [[Wasaby-Access-Control]]
- Key insight: `rightcheck` модуль — 5 Python-хэлперов для 403 с данными запроса доступа; платформа автоматически создаёт ЭДО-документ и выдаёт права.

## [2026-05-19] save | PostgreSQL CTE Cursor Pushdown
- Type: concept
- Location: wiki/concepts/PostgreSQL-CTE-Cursor-Pushdown.md
- From: оптимизация Bonus.GetClientListWithStats — cursor pushdown в personal_accounts CTE, 400ms → 110ms

## [2026-05-19] save | JSONB Array Containment Optimization
- Type: concept
- Location: wiki/concepts/JSONB-Array-Containment-Optimization.md
- From: оптимизация запроса LoyaltyProgram.HasApplicableBenefitsBySalesPoint — EXISTS+unnest → @> оператор

## [2026-05-18] ingest | AVIF to PNG Conversion on Windows
- Source: session insight (2026-05-18)
- Summary: [[AVIF-to-PNG-Windows-Conversion]]
- Pages created: [[AVIF-to-PNG-Windows-Conversion]]
- Key insight: `python3` на Windows — заглушка; используй `py` + Pillow; WIC CopyPixels даёт 0xC00D5212 без GPU.

## [2026-05-18] ingest | SabyGet Documentation Batch
- Source: `raw/` — 10 files (Описание продукта ×2, Описание подсистемы ×4, Архитектура данных ×4)
- Summary: [[sabyget-docs-2026-05-18]]
- Pages created: [[SabyGet-Product-Overview]], [[SabyGet-Landing-Page]], [[SabyGet-Loyalty-Subsystems]], [[domains/sabyget/_index]]
- Key insight: SabyGet — потребительская витрина лояльности Tensor; proxy-архитектура через online.sbis.ru; сортировка каруселей по формуле Избранное×1 + Клиент×10 + Затраты×100

## [2026-05-18] save | ImportDiscountCard-DCS-Counter-Bug
- Type: concept
- Location: wiki/concepts/ImportDiscountCard-DCS-Counter-Bug.md
- From: bugfix session — счётчик карт не обновлялся после импорта ДК

## [2026-05-18] fold | batch-exponent-k4 rollup of 16 entries
- Location: wiki/folds/fold-k4-from-2026-04-13-to-2026-05-18-n16.md
- Range: 2026-04-13 to 2026-05-18
- Children: 16 log entries

## [2026-05-18] batch-ingest | Linter Standarization Project (5 docs)
- Source: `raw/Цель и идея проекта.md`, `raw/Техническое задание.md`, `raw/Отчет по проекту.md`, `raw/План работ по проекту.md`, `raw/Инструкция по подключению линтеров.md`
- Summary: [[linter-project-2026-05-18]]
- Pages created: [[Linter-Standarization-Project]], [[SonarQube-Stan-Linter-Setup]], [[linter-project-2026-05-18]]
- Pages updated: [[index]], [[hot]], [[sources/_index]]
- Key insight: Проект завершён 04.05.2026 (перерасход +19.1%). SonarQube режим — sonar2 (не lint). Тимошенко А.А. участвовал в price-formation back (4 дня).

## [2026-05-14] update | DWC-Card-Events-Migration
- Type: concept (update)
- Location: wiki/concepts/DWC-Card-Events-Migration.md
- From: реализация Card.HandleMerge (personalcard/merge.py); инсайт о SimpleRecordMatcher (полное сравнение, не частичное); заметка о task.priority

## [2026-05-14] save | FranchiseCard-Import-POS-SaleValidation-Bug
- Type: synthesis
- Location: wiki/concepts/FranchiseCard-Import-POS-SaleValidation-Bug.md
- From: баг — импортированная карта участника франшизы не проходит SaleValidation на POS; полный root cause analysis + фикс `async_notify_changed_cards` в `_process_card_item`

## [2026-05-14] save | ImportDiscountCard-Franchise-Client-Import
- Type: concept
- Location: wiki/concepts/ImportDiscountCard-Franchise-Client-Import.md
- From: расследование приёмочного бага «не добавляется персона при франшизном импорте клиента» (оказалось — проверяли не на том стенде); в процессе глубоко изучена архитектура ImportDiscountCard.ProcessFile

## [2026-05-14] save | PromoCode SafeDelete — Sabyget notification bug
- Type: session
- Location: wiki/meta/PromoCode-SafeDelete-Sabyget-Bug.md
- From: расследование бага — индивидуальный промокод остаётся в Sabyget после удаления по крестику; фикс `disable_promo_codes` + откат `get_earned_list.py`; не закоммичено

## [2026-05-13] save | DWC-Card-Events-Migration (concept page)
- Type: concept
- Location: wiki/concepts/DWC-Card-Events-Migration.md
- From: реализация Card.HandleChangeBonusBalance — второй этап DWC Card events migration; документирует оба реализованных сценария + паттерн + оставшиеся задачи

## [2026-05-13] save | DWC Card Events Migration — Card.HandleChangeData
- Type: session
- Location: wiki/meta/DWC-Card-Events-Migration.md
- From: декомпозиция 4 сценариев событий карт → DWC; реализация Card.HandleChangeData (feature flag, .dwc, notify.py, тесты)

## [2026-05-08] save | ReferralProgram Stub Implementation
- Type: decision
- Location: wiki/meta/ReferralProgram-Stub-Implementation.md
- From: реализация CreateStub/UpdateStub для SabyBank RKO — бизнес-сценарии, StatusDate логика, LinkType константы, тесты

## [2026-04-14] ingest | LoyaltyPrograms IterativeListLoading
- Source: codebase (`helpers.py:46–611,953–1045`, `get_sale_list.py`)
- Summary: [[LoyaltyPrograms-IterativeListLoading]]
- Pages created: [[LoyaltyPrograms-IterativeListLoading]]
- Pages updated: [[Wasaby-BL-List-Advanced]], [[index]], [[hot]]
- Key insight: `IterativeBlockSizeEmaMixin` адаптирует `_iterative_block_size` через EMA коэффициента разреженности; `ListWithCompositeCursor` возвращает `nextPosition` как `[{key:val}]` вместо `[val]`; итеративный SQL использует `!param` вместо `{param}`.

## [2026-04-14] ingest | Wasaby BL List Advanced Patterns (10 docs)
- Source: `raw/Навигация по курсору.md`, `raw/Множественная навигация.md`, `raw/Порционная загрузка данных.md`, `raw/Массовая отметка записей.md`, `raw/Показать отмеченные.md`, `raw/Как перенести записи в папку.md`, `raw/Суммировать.md`, `raw/Стандартные параметры фильтрации.md`, `raw/TranslitListCall.md`, `raw/ListWithParents.md`
- Summary: [[wasaby-list-advanced-2026-04-14]]
- Pages created: [[Wasaby-BL-List-Advanced]], [[wasaby-list-advanced-2026-04-14]]
- Pages updated: [[Wasaby-BL-List-Methods]], [[index]], [[hot]]
- Key insight: Курсорная навигация — основа для 4 из 10 паттернов; декларативный метод поддерживает ИдО/СписокИдО/Раздел из коробки.

## [2026-04-14] ingest | Перевод страниц лояльности на React — проектная документация
- Source: `raw/Цель и идея проекта.md`, `raw/ТЗ по проекту...md`, `raw/План работ...md`
- Summary: [[loyalty-react-migration-2026-04-14]]
- Pages created: [[Loyalty-React-Migration-Project]], [[loyalty-react-migration-2026-04-14]]
- Pages updated: [[index]], [[hot]]
- Key insight: Новый проект 147,5 чд до 27.02.2026: перевод 5 разделов лояльности на React + новый API Bonus.GetBaseSettings + курсорная навигация в Promotion.GetList.

## [2026-04-14] ingest | Звонок — Follow-up баг Златекс (статус и доступ)
- Source: `raw/Звонок 2026-04-14 09-33-24.md`
- Summary: [[zvonok-zlateks-followup-2026-04-14]]
- Pages created: [[zvonok-zlateks-followup-2026-04-14]]
- Pages updated: [[hot]], [[log]]
- Key insight: «Соглашение Шрёдингера» — документ фактически **принят**, но в реестре партнёров статус отображается как «отправлено» (затуп на проде, реестр не обновился). Симаков расследует. Новый баг: `account.service.login` падает при входе на новый портал (→ Егор Платонов).

## [2026-04-13] ingest | Звонок — Баг оффера у партнёра Златекс
- Source: `raw/Звонок 2026-04-13 141126.md`
- Summary: [[zvonok-offer-bug-zlateks-2026-04-13]]
- Pages created: [[zvonok-offer-bug-zlateks-2026-04-13]]
- Pages updated: [[hot]], [[log]], [[index]]
- Key insight: client_id mismatch (77 vs 78) при открытии раздела оффера партнёром; критический баг, дедлайн 2026-04-15, расследует Саша.

## [2026-04-13] ingest | Feature workflow rule
- Source: user insight (inline)
- Pages updated: [[Saby-Feature-Toggles-API]]
- Key insight: При создании новой фичи **первый шаг** — объявить её в `.feature` файле, до любого кода-потребителя.

## [2026-04-13] ingest | Wasaby Service Module Architecture (17 docs)
- Source: `raw/Архитектура типового узла web-сервиса.md`, `raw/Порядок загрузки модулей.md`, `raw/Параметры конфигурации сервисного модуля.md`, `raw/Описание API сервисного модуля.md`, `raw/Бинарные библиотеки сервисного модуля.md`, `raw/События сервисного модуля и их обработчики.md`, `raw/Структура проекта приложения.md`, `raw/Стандарт именования приложений и сервисов.md`, `raw/Типы сущностей, описываемых в s3srv-файлах.md`, `raw/Описание схемы дистрибутива и проектных файлов прочего сервиса.md`, `raw/Сервисный модуль BL Core.md`, `raw/Сервисный модуль Image. Библиотека sbis-img для обработки изображений.md`, `raw/Сервисный модуль Interprocess Storage. Локальное хранилище данных.md`, `raw/Сервисный модуль XML-Py. Библиотека sbis-xml для обработки XML.md`, `raw/Python-модуль sbis.md`, `raw/Утилита sbis_root.md`, `raw/Разработка собственного модуля Python и его внедрение в состав модуля БЛ.md`
- Pages created: [[Wasaby-Service-Architecture]], [[Wasaby-Module-System]], [[Wasaby-Platform-Modules]]
- Pages updated: [[index]], [[hot]], [[log]], [[sources/_index]]
- Key insight: Wasaby — плагинная архитектура. Координатор + эталонные + рабочие процессы. 5 фаз загрузки. API-доступность: Internal/TAC/IAC/SC/PSC. xml.dom/xml.sax запрещены → sbis-xml (xerces). sbis_root — только для скриптов/отладки, нельзя на сервисе.

## [2026-04-13] save | BrokerLoyalty BonusSettings Race Fix
- Type: decision
- Location: wiki/meta/BrokerLoyalty-BonusSettings-Race-Fix.md
- From: bugfix session — промокоды не синхронизировались в офлайн при `lty_broker_bonus_set`; гонка на SyncBrokerClient singleton; перенос BonusSettings в BrokerSyncLoyalty через SyncManager

## [2026-04-12] ingest | Tensor TechDoc Standards (5 docs)
- Source: `raw/Правила оформления технической документации.md`, `raw/Правила оформления технической документации 1.md`, `raw/Когда создавать новую ТД.md`, `raw/Кто читает техническую документацию.md`, `raw/Учимся писать ТД.md`
- Pages created: [[Tensor-TechDoc-Standards]], [[tensor-techdoc-standards-2026-04-12]]
- Pages updated: [[index]], [[hot]], [[log]]
- Key insight: ТД is iterative and per-product/subsystem (never per-project). ТЗ ≠ ТД. Audience matrix: 6 reader types with different section needs. Key anti-patterns: circular descriptions, ТЗ copy-paste, inconsistent diagrams, clutter on schemas.

## [2026-04-12] ingest | Wasaby Optimization (4 docs)
- Source: `raw/Бюджет.md`, `raw/Как долго перебрать RecordSet.md`, `raw/Оптимизация приложений.md`, `raw/Работаем с RecordSet. Часть 2.md`
- Pages created: [[Wasaby-Performance-Budget]], [[Wasaby-App-Optimization]]
- Pages updated: [[Wasaby-RecordSet-Performance]]
- Key insight: `rs.ToList(fields)` в ~3× быстрее ручного перебора; Perfalyze-бюджеты задают конкретные пороги VR/TTI по типажам.

## [2026-04-12] save | ReferralProgram.DetachPartner Implementation
- Type: decision
- Location: wiki/meta/ReferralProgram-DetachPartner-Implementation.md
- From: реализация BL-метода для AT-повторяемости сценариев присоединения партнёра к офферу; анализ FK-зависимостей ВидЦеныДокумент; 4 файла изменены/созданы

## 2026-04-12 | ingest | AT Coverage — Referral Deals (2 docs)
- Sources: `raw/План работ по проекту «Покрытие АТ Реферальная система сделок».md`, `raw/ТЗ по проекту «Покрытие АТ Реферальная система сделок».md`
- Summary: [[at-coverage-referral-deals-2026-04-12]]
- Pages created: [[AT-Coverage-ReferralDeals-Project]]
- Pages updated: [[index]], [[hot]]
- Key insight: Проект АТ-покрытия реферальной системы сделок: 0%→95% МК, дедлайн 31.05.26, 9 этапов, команда Земцова/Клочкова/Рыбкин + Тимошенко 0.5д в Этапе 6.

## [2026-04-12] save | DWC BonusSettings Events Migration
- Type: session
- Location: wiki/meta/DWC-BonusSettings-Events-Migration.md
- From: реализация перевода 2 событий настроек бонусов на DWC (`holidays.changed` и `promotion.enabled`), feature flag `dwc_bonus_settings`, 4 изменённых файла

## 2026-04-12 | ingest | Saby Product Lineup + Naming Guide (2 docs)
- Sources: `raw/Продукты разработки.md`, `raw/Руководство по неймингу.md`
- Summaries: [[saby-products-lineup-2026-04-12]], [[saby-naming-guide-2026-04-12]]
- Pages created: [[Saby-Product-Lineup]], [[Saby-Naming-Guide]]
- Pages updated: [[Tensor-Company]], [[index]]
- Key insight: Полный каталог 30+ продуктов Saby с ответственными + официальная таблица переименований СБИС→Saby (25 продуктов, 18 мобильных приложений).

## 2026-04-12 | ingest | Tensor Company Culture (4 docs)
- Source: `raw/О компании.md`, `raw/Миссия и Принципы.md`, `raw/Правила Тензора.md`, `raw/Словарь компании «Тензор».md`
- Summary: [[tensor-company-docs-2026-04-12]]
- Pages created: [[Tensor-Company]], [[Tensor-Culture]], [[Tensor-Glossary]]
- Pages updated: [[index]], [[hot]], [[log]]
- Key insight: Тензор — IT-холдинг, 4.5M+ клиентов Saby, №1 по ЭДО; культура строится на 8 принципах (человек важнее статуса, простота, действие, долгосрочные отношения).

## 2026-04-12 | ingest | Wasaby Middleware Services (14 docs)
- Source: `raw/` — MQ, STOMP bus, async bus, server events bus, request-broker, parameters service, parameters API, parameters-constants, declarative params, Saby Space, SabyDisk overview, FileStorage, binary storage, file-transfer
- Summary: [[messaging-middleware-2026-04-12]], [[parameters-service-2026-04-12]], [[storage-services-2026-04-12]]
- Pages created: [[Wasaby-RabbitMQ]], [[STOMP-Events-Bus]], [[Async-Calls-Bus]], [[Server-Events-Bus]], [[Request-Broker-Service]], [[Parameters-Service]], [[Parameters-API]], [[SabyDisk-Platform]], [[FileStorage-Service]], [[File-Transfer-Service]], [[Binary-Storage-Options]]
- Pages updated: [[index]], [[hot]], [[log]]
- Key insight: Всё messaging СБИС строится на RabbitMQ; request-broker — его замена для DWC/Scheduler с отслеживанием статуса запросов; file-transfer связан с обоими (Huge Payload + LRS-результаты).

## 2026-04-12 | ingest | Wasaby Infrastructure Docs (13 docs)
- Source: `raw/` — Хоттабыч, Патчи, Скрипты, Роли, Участок системы, Ограничения, Приложения, Руководство пользователя, Пользователи облака, Клиенты, Маршрутизация, Схема дистрибутивов, Python (локальные стенды)
- Summary: [[wasaby-infra-2026-04-12]]
- Pages created: [[Хоттабыч-System]], [[Wasaby-Patches]], [[Wasaby-Scripts]], [[Wasaby-Access-Control]], [[Wasaby-Cloud-Management]], [[Wasaby-Request-Routing]], [[Wasaby-Distribution-Schema]], [[Wasaby-Local-Stand-Setup]]
- Pages updated: [[concepts/_index]], [[sources/_index]], [[index]], [[hot]], [[log]]
- Key insight: Права доступа в Wasaby — трёхуровневая система (участок→роль→пользователь) с разрешающей политикой (объединение = максимальный доступ). Патчи применяются на ВСЕ сервисы приложения, без возможности выбора конкретного.

## 2026-04-10 | ingest | PriceFormation Backend Architecture
- Source: `www/service/Модули/` (live codebase exploration)
- Pages created: [[PriceFormation-Backend-Architecture]]
- Pages updated: [[domains/price-formation/_index]]
- Key insight: Online — главный модуль (~20 субпакетов), Common — базовые классы/хелперы, Offline — минимальный набор для POS/касс; паттерн «один файл = один метод БЛ».

## 2026-04-10 | ingest | Loyalty Desktop Broker Migration (3 docs)
- Sources: `raw/Проект Перевод синхронизации лояльности...md`, `raw/Техническое задание.md`, `raw/WIP Решение.md`
- Summary: [[loyalty-desktop-broker-migration-2026-04-10]]
- Pages created: [[Loyalty-Desktop-Broker-Migration]]
- Pages updated: [[Sync-Broker-Architecture]]
- Key insight: ~29 000 Desktop копий переводятся со старого scheduled-sync на брокер; 5 сущностей; feature flag `lty_broker_card_type`; bugfix лимитов партнёрских промокодов.

## 2026-04-10 | ingest | Паттерны эффективной работы с Record и RecordSet в Python
- Source: `raw/Паттерны эффективной работы с Record и RecordSet в Python.md`
- Pages created: [[Wasaby-RecordSet-Performance]]
- Pages updated: [[Wasaby-Python-Patterns]]
- Key insight: rec.Fill({...}) and rs.AddRow() (no-arg) are key patterns to avoid IField temp-object churn; SqlQueryOf bypasses RecordSet entirely for calculation code.

## 2026-04-10 | ingest | Возможные проблемы в интеграции C++ и Python кода
- Source: `raw/Возможные проблемы в интеграции C++ и Python кода.md`
- Pages created: [[Wasaby-CPP-Python-Integration]]
- Pages updated: [[Wasaby-Python-Patterns]]
- Key insight: Three crash-causing (not exception-raising) anti-patterns when holding Python references to C++-backed Record/RecordSet objects.

## 2026-04-10 | ingest | Wasaby BL Framework (37 docs)
- Source: `raw/Методы бизнес-логики.md`, `raw/Объекты бизнес-логики.md`, `raw/Сервис контракт.md`, `raw/Справочник объектов.md`, `raw/Справочник задач планировщика.md`, `raw/Как сервис БЛ взаимодействует с БД.md`, `raw/Автогенерируемые методы (CRUD).md`, `raw/Создать.md`, `raw/Прочитать.md`, `raw/Записать.md`, `raw/Удалить.md`, `raw/Копировать.md`, `raw/Объединить.md`, `raw/Удалить отмеченные.md`, `raw/Sync.md`, `raw/Черновик.md`, `raw/Списочные методы.md`, `raw/Декларативный списочный метод.md`, `raw/Реализуемый вручную.md`, `raw/Типы фильтра.md`, `raw/Диалог редактирования параметров.md`, `raw/Кэширование методов БЛ.md`, `raw/Таймаут.md`, `raw/Контроль частоты вызова.md`, `raw/Обработчики.md`, `raw/Область видимости.md`, `raw/Метод с произвольным количеством параметров.md`, `raw/Удаленные вызовы.md`, `raw/HTTP-запрос.md`, `raw/Proxy-метод.md`, `raw/Работа с файлами.md`, `raw/Прочитать (Read file).md`, `raw/Загрузить.md`, `raw/Загрузить с прикреплением.md`, `raw/Список по UUID.md`, `raw/Работа с исключениями в Python.md`, `raw/Работа с критически важными ресурсами.md`
- Summary: [[wasaby-bl-docs-2026-04-10]]
- Pages created: [[Wasaby-BL-Objects]], [[Wasaby-BL-Methods]], [[Wasaby-BL-CRUD]], [[Wasaby-BL-List-Methods]], [[Wasaby-BL-Advanced]], [[Wasaby-Python-Patterns]]
- Pages updated: (none)
- Key insight: Списочные методы без навигации — DoS-уязвимость; Sync устарел; `CreateTransaction` только с `with`

## 2026-04-10 | ingest | External Loyalty Integrations (UDS / PremiumBonus / iikoCard)
- Source: `raw/Интеграции с внешними системами лояльности.md`, `raw/Интеграция с iiko.md`, `raw/Информационная модель.md`, `raw/Концепт решения и архитектура.md`, `raw/API подсистемы.md`, `raw/База данных.md`
- Summary: [[external-loyalty-2026-04-10]]
- Pages created: [[ExternalLoyalty-Integrations]], [[ExternalLoyalty-iiko-Integration]], [[ExternalLoyalty-Info-Model]]
- Pages updated: [[Loyalty-Database-Schema]] (added КодыЛиц + ВидКарты.Тип=2 section)
- Key insight: Все три внешних ЛС (UDS/PB/iikoCard) работают через IntegrationProxy; iikoCard имеет проблему задержки обновления баланса и уникальные требования (идентификация строго по карте, требует связи с облаком).

## 2026-04-10 | ingest | Наценка (Markup) Subsystem
- Sources: `raw/Описание.md`, `raw/База данных.md`, `raw/API подсистемы Наценка.md`, `raw/Подсистема распределения прав.md`
- Summary: [[markup-subsystem-2026-04-10]]
- Pages created: [[Markup-Subsystem]]
- Pages updated: [[Loyalty-Database-Schema]] (added Тип=32)
- Key insight: Наценка — ВидЦены.Тип=32, скидка с типом MARKUP_*. Авто/ручная. Спец.номенклатура «Сервисный сбор». Рассчитывается после скидок/бонусов, до округления.

## 2026-04-10 | ingest | Подсказки (Cashier Hints Subsystem)
- Sources: `raw/Описание.md`, `raw/API подсистемы.md`, `raw/База данных.md`, `raw/Подсистема распределения прав.md`
- Summary: [[prompts-subsystem-2026-04-10]]
- Pages created: [[Prompts-Cashier-Hints]]
- Pages updated: [[Loyalty-Database-Schema]] (added Тип=18)
- Key insight: Подсказки — ВидЦены.Тип=18, popup hints for cashiers. Reuse full promotions data model. Session storage deduplication (1h TTL).

## 2026-04-10 | ingest | Реферальная бонусная программа
- Sources: `raw/Описание.md`, `raw/Концепт решения и архитектура.md`, `raw/Реферальная бонусная программа.md`
- Pages created: [[Referral-Bonus-Program]]
- Pages updated: [[Bonus-Programs-Architecture]]
- Key insight: Реферальная бонусная программа — ВидЦены.Тип=9. Не путать с [[ReferralDeals-System]] (B2B). Начисление: за ссылку / регистрацию / первую покупку + % от покупок друзей (до 3 уровней).

## 2026-04-10 | save | DWC Promocode Events Migration
- Type: session
- Location: wiki/meta/DWC-Promocode-Events-Migration.md
- From: реализация перевода 4 событий промокодов (applied/unapplied/changed/deleted) с event.Publish на DWC-задачи; 9 файлов; feature flag `dwc_promocode`

## 2026-04-10 | ingest | API управления функционалом + Параметры сервисов vs переключатели
- Sources: `raw/API управления функционалом.md`, `raw/Параметры сервисов vs переключатели функционалов.md`
- Pages created: [[Saby-Feature-Toggles-API]], [[Saby-Service-Config]]
- Key insight: Переключатели функционала — временные (удалять после вывода), параметры — постоянные. Рекомендуемый вызов: `IsOn(client_id, user_id)`. Ключ переключателя: ≤20 символов, строчная латиница.

## 2026-04-10 | batch ingest | Loyalty Sale Application + Profiles Service (4 docs)
- Source: `raw/Применение лояльности на продаже - Описание.md`, `raw/Применение лояльности на продаже - Алгоритмы и процессы.md`, `raw/Применение лояльности на продаже - Организация кода.md`, `raw/Сервис Профилей.md`
- Pages created: [[Loyalty-Sale-Application]], [[Profiles-Service]], [[loyalty-sale-profiles-2026-04-10]]
- Pages updated: [[index]], [[hot]]
- Key insight: Подсистема лояльности на продаже — «консультант»: возвращает рекомендации, не меняет продажу. C++ ядро (CalcDiscount) единое для всех платформ. Режим оферты: в цепочке документов следствие не пересчитывает акции. Штампики = целочисленное накопление. Сервис Профилей вводит Персона-UUID для кросс-клиентской идентификации; local-first стратегия запросов.

## 2026-04-10 | batch ingest | Sync Broker Deep Dive (12 docs)
- Source: `raw/Облачный брокер синхронизации.md`, `raw/Концепт решения и архитектура.md`, `raw/Подсистема шардирования брокера синхронизации.md`, `raw/Концепт решения и архитектура 1.md`, `raw/Алгоритмы и процессы 1.md`, `raw/База данных 1.md`, `raw/Реактивная синхронизация.md`, `raw/Концепт решения и архитектура 2.md`, `raw/Алгоритмы и процессы 2.md`, `raw/База данных 2.md`, `raw/Как встраивать (API подсистемы).md`, `raw/Управление брокером синхронизации.md`
- Pages created: [[Sync-Broker-Architecture]], [[Sync-Broker-Sharding]], [[Sync-Broker-Reactive]], [[Sync-Broker-Management]], [[sync-broker-deep-dive-2026-04-10]]
- Pages updated: [[Sync-Broker]], [[index]], [[hot]]
- Key insight: Три типа STOMP-уведомлений — «без тела» (надёжно), «с телом» (быстро, ненадёжно), «с загружаемым телом» (рекомендуется: брокер загружает дата-модель сам, гарантируя правильный порядок). Роутинг: локальный кэш 5 мин → Redis → БД; метка миграции = момент изменения + 10 мин.

## 2026-04-10 | batch ingest | LRS Long Request Service (4 docs)
- Source: `raw/Длительные операции.md`, `raw/Поиск в логах сервиса длительных операций.md`, `raw/Работа с длительными операциями на бизнес-логике.md`, `raw/Техническая документация.md`
- Pages created: [[LRS-Long-Request-Service]], [[lrs-docs-2026-04-10]]
- Pages updated: [[index]], [[hot]]
- Key insight: LRS — тонкий слой поверх DWC, добавляющий UX-прогресс, результаты (ResultLink/ResultTmpl), историю 90 дней, шардированную БД (64 вирт. шарда), бесшовное обновление через redis. UUID-цепочки в логах не сохраняются — поиск по log_id: отдельно.

## 2026-04-10 | batch ingest | DWC v1 & v2 Client Library (2 docs)
- Source: `raw/Описание первой версии клиентской библиотеки DWC.md` (new), `raw/Сервис DWC.md` (new)
- Pages created: [[DWC-Client-Library-v1]]
- Pages updated: [[DWC-Distributed-Workflow-Coordinator]], [[index]], [[hot]]
- Key insight: DWC v2 использует паттерн строитель (WorkflowBuilder+Sender) и конфигурацию через .dwc-файлы вместо кодовых вызовов v1. v1 (`workflow` module) устарела, актуальна только v2 (`workflow2`). Ключевые отличия: нет `issuer` в конструкторе, метаданные в .dwc вместо SetResponsible/SetErrorPolicy, SetDelayedUntil вместо SetDelay, CreateTask вместо Task().

## 2026-04-10 | batch ingest | DWC Migration SDK (3 docs)
- Source: `raw/Идея решения.md` (new), `raw/План работ по проекту.md` (updated), `raw/Техническое задание.md` (updated)
- Pages created: [[DWC-Migration-SDK]]
- Pages updated: [[index]], [[hot]]
- Key insight: Проект заменяет event-шину Онлайн→СДК на DWC-задачи для устранения очередей, порядка обработки и управления нагрузкой. Тимошенко А. ответственен за все задачи по промокодам (7 дней). Дедлайн разработки: 30.04.2026, выпуск на всех: 30.06.2026.

## 2026-04-10 | batch ingest | SabyBank RKO Referral (4 docs)
- Source: `raw/Бизенс-процесс...md`, `raw/Концептуальное решение.md`, `raw/План работ по проекту.md`, `raw/Техническое задание.md`
- Summary: [[sabybank-rko-referral-2026-04-10]]
- Pages created: [[SabyBank-RKO-Referral]]
- Pages updated: [[index]], [[hot]]
- Key insight: "Корешок" — запись `ВидЦеныДокумент` с `ТипСвязи`=10/11/12, единственный источник данных для статистики и вознаграждений по банковским заявкам. Вознаграждение назначается вручную менеджером Тензора. Тимошенко А. — ответственный за весь BL и тех. долг.

## 2026-04-10 | batch ingest | Wasaby Data Types (6 docs)
- Source: `raw/` (JSON, RecordSet, Темпоральные типы данных, Типы полей в Record, Числовые поля, API LISTENNOTIFY [updated])
- Summary: [[wasaby-db-access-2026-04-10]]
- Pages created: [[Wasaby-Data-Types]], [[Wasaby-RecordSet-Join]]
- Pages updated: [[index]], [[hot]]
- Key insight: `ftDECIMAL` (Money) — никогда не используй double для финансовых данных. Decimal serializes as double by default — нужен флаг Large decimal для чисел >15 знаков. Temporal types: DateTime с TZ хранится как UTC в PG, конвертируется на каждом слое (сервер→клиент); без TZ — без преобразований. RecordSet.Join — in-memory SQL-like joins без обращения к БД.

## 2026-04-10 | batch ingest | Wasaby DB Access Patterns (5 docs)
- Source: `raw/` (Выполнение запросов в БД, Асинхронные запросы в БД, API LISTENNOTIFY, Массовая выборка и вставка записей в БД, Шаблоны SQL-запросов)
- Summary: [[wasaby-db-access-2026-04-10]]
- Pages created: [[Wasaby-DB-Access-Patterns]]
- Pages updated: [[Wasaby-Framework]], [[index]], [[hot]]
- Key insight: SQL Templates (`Template` + `TemplateExecutor`) — рекомендуемый способ построения запросов: named params, conditional blocks, WHERE/SET lists. Async queries lock the connection for duration — never save IAsyncQueryResult across BL method boundaries. SQLite не поддерживает async и ITableCopier Get/Put.

## 2026-04-10 | batch ingest | Акции subsystem (5 docs)
- Source: `raw/` (Акции — Описание, Концепт, Информационная модель, Алгоритмы, Интерфейс)
- Summary: [[акции-subsystem-2026-04-10]]
- Pages created: [[Акции-Subsystem-Overview]], [[Акции-Info-Model]], [[Акции-Architecture]], [[Акции-UI]]
- Pages updated: [[index]], [[hot]]
- Key insight: Акция — корневая сущность системы лояльности (ВидЦены). Конкурс скидок: 3 приоритета (высокий/средний/низкий), несуммируемые → суммируемые. Порядок расчёта: подарки → скидки → бонусы → наценка → округление. ООП: `Discount` + паттерн Стратегия.

## 2026-04-10 | batch ingest | Промокоды + Реферальная система сделок (12 docs)
- Source: `raw/` (5 Промокоды docs + 7 Реферальная система сделок docs)
- Summary: [[promocodes-referral-deals-2026-04-10]]
- Pages created: [[Promocode-Subsystem-Overview]], [[Promocode-Info-Model]], [[ReferralDeals-System]]
- Pages updated: [[price-formation/_index]], [[index]]
- Key insight: Промокод технически = Дисконтная карта (Карта/ВидКарты таблицы). Вознаграждение Партнёра в реферальной системе сделок = бонусные баллы (ВидЦеныДокумент). 4 типа промокодов: Общий(5)/Индивидуальный(6)/Партнёрский(7)/ЗаАктивность(8). Реферальная система сделок — не коробочная, внедрение по проектам.

## 2026-04-10 | batch ingest | Bonus Programs Subsystem (6 docs)
- Source: `raw/` (Бонусы — Описание, Концепт, База данных, Информационная модель, Алгоритмы, Калькулятор)
- Summary: [[bonus-subsystem-2026-04-10]]
- Pages created: [[Bonus-Programs-Architecture]], [[BonusDecRule-Info-Model]], [[Bonus-Deduction-Algorithm]]
- Pages updated: [[Loyalty-Database-Schema]] (added ВидЦены Type=5/40), [[index]]
- Key insight: Accrual (Type=5) and deduction (Type=40) are separate ВидЦены objects. BONUS_DEC_RULE=40 has 3-priority plan (targeted → "на весь чек" → global). 0% rules block lower-priority rules. Calculator: 2 modes (fixed/tiered), кэшбэк formula rounds down, лимит rounds up to multiple of 5.

## 2026-04-10 | batch ingest | Discount Cards Subsystem (10 docs)
- Source: `raw/` (Описание, API подсистемы, Алгоритмы и процессы, Особенности интерфейса, Права, Пользовательская документация, Сервис Диагностика, pass-updater, База данных, Параметры облака)
- Summary: [[discount-cards-batch-2026-04-10]]
- Pages created: [[DiscountCard-Subsystem-Overview]], [[DiscountCard-Service-API]], [[DiscountCard-Algorithms-Processes]], [[DiscountCard-UI-Specifics]], [[PassUpdater-Service]], [[DiscountCard-Diagnostic-Service]], [[DiscountCard-Admin-Ops]]
- Pages updated: [[Loyalty-Database-Schema]] (added СДК service DB section), [[Loyalty-Cloud-Config]] (confirmed), [[price-formation/_index]], [[index]]
- Key insight: СДК = 5-part service. pass-updater uses EntryPoint queue → cannot use master-replica updates. AW образы async via APN; GPay образы sync + TaskDeliveryProcessor. inside.sbis.ru мониторинг через ClickHouse с "фейковым" UUID брокера.

Entry format: `## [YYYY-MM-DD] operation | Title`

Parse recent entries: `grep "^## \[" wiki/log.md | head -10`

---

## [2026-04-10] ingest | Loyalty Knowledge Base (raw/)
- Source: `raw/` (6 files: База данных, Описание продукта, Параметры облака, Публичное API, Справочник компонентов, Справочник лояльности в продуктах)
- Summary: [[loyalty-knowledge-base-2026-04-10]]
- Pages created: [[Loyalty-Database-Schema]], [[Loyalty-Product-Overview]], [[Loyalty-Cloud-Config]], [[Loyalty-Public-API]], [[Loyalty-UI-Components]], [[Loyalty-In-Products]]
- Pages updated: [[price-formation/_index]], [[index]]
- Key insight: Full loyalty system knowledge — DB schema (ВидЦеныДокумент as unified stats table), complete public API surface, UI component library, and product compatibility matrix.

## [2026-04-10] ingest | Price Formation Docs (docs/ folder)
- Source: `C:/Users/aa.timoshenko/PycharmProjects/price-formation/docs/` (12 files)
- Summary: [[price-formation-docs-2026-04-10]]
- Pages created: [[price-formation/_index]], [[Wasaby-Framework]], [[Multitenancy-Architecture]], [[DWC-Distributed-Workflow-Coordinator]], [[Sync-Broker]], [[Python-Code-Standards-SBIS]], [[Python-Localization-rk]], [[ReferralProgram-Module]]
- Pages updated: [[index]]
- Key insight: price-formation is a Wasaby/SBIS loyalty system; SyncBrokerClient is a process singleton (concurrent Sync() = state race); ReferralProgram is unrelated to loyaltyprograms/referralbonus

## [2026-04-08] save | claude-obsidian v1.4 Release Session
- Type: session
- Location: wiki/meta/claude-obsidian-v1.4-release-session.md
- From: full release cycle covering v1.1 (URL/vision/delta tracking, 3 new skills), v1.4.0 (audit response, multi-agent compat, Bases dashboard, em dash scrub, security history rewrite), and v1.4.1 (plugin install command hotfix)
- Key lessons: plugin install is 2-step (marketplace add then install), allowed-tools is not valid frontmatter, Bases uses filters/views/formulas not Dataview syntax, hook context does not survive compaction, git filter-repo needs 2 passes for full scrub

## [2026-04-08] ingest | Claude + Obsidian Ecosystem Research
- Type: research ingest
- Source: `.raw/claude-obsidian-ecosystem-research.md`
- Queries: 6 parallel web searches + 12 repo deep-reads
- Pages created: [[claude-obsidian-ecosystem]], [[cherry-picks]], [[claude-obsidian-ecosystem-research]], [[Ar9av-obsidian-wiki]], [[Nexus-claudesidian-mcp]], [[ballred-obsidian-claude-pkm]], [[rvk7895-llm-knowledge-bases]], [[kepano-obsidian-skills]], [[Claudian-YishenTu]]
- Key finding: 16+ active Claude+Obsidian projects; 13 cherry-pick features identified for v1.3.0+
- Top gap confirmed: no delta tracking, no URL ingestion, no auto-commit

## [2026-04-07] session | Full Audit, System Setup & Plugin Installation
- Type: session
- Location: wiki/meta/full-audit-and-system-setup-session.md
- From: 12-area repo audit, 3 fixes, plugin installed to local system, folder renamed

## [2026-04-07] session | claude-obsidian v1.2.0 Release Session
- Type: session
- Location: wiki/meta/claude-obsidian-v1.2.0-release-session.md
- From: full build session — v1.2.0 plan execution, cosmic-brain→claude-obsidian rename, legal/security audit, branded GIFs, PDF install guide, dual GitHub repos


- Source: `.raw/` (first ingest)
- Pages updated: [[index]], [[log]], [[hot]], [[overview]]
- Key insight: The wiki pattern turns ephemeral AI chat into compounding knowledge — one user dropped token usage by 95%.

## [2026-04-07] setup | Vault initialized

- Plugin: claude-obsidian v1.1.0
- Structure: seed files + first ingest complete
- Skills: wiki, wiki-ingest, wiki-query, wiki-lint, save, autoresearch
