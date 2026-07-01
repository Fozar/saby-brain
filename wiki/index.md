---
type: meta
title: "Wiki Index"
updated: 2026-04-07
tags:
  - meta
  - index
status: evergreen
related:
  - "[[overview]]"
  - "[[log]]"
  - "[[hot]]"
  - "[[dashboard]]"
  - "[[concepts/_index]]"
  - "[[entities/_index]]"
  - "[[sources/_index]]"
  - "[[LLM Wiki Pattern]]"
  - "[[Hot Cache]]"
  - "[[Compounding Knowledge]]"
  - "[[Andrej Karpathy]]"
---

# Wiki Index

Last updated: 2026-06-24 | Total pages: 336 | Sources ingested: 187

Navigation: [[overview]] | [[log]] | [[hot]] | [[dashboard]] | [[getting-started]]

---

## Система обновлений — Concepts

- [[Хоттабыч-System]] (c-000092) — облачное приложение vm.sbis.ru: управление обновлениями, дистрибутивами, патчами/скриптами на Wasaby Framework; фазы обновления, агенты (status: current)
- [[UpdateSystem-UpdateTypes]] (c-000085) — таксономия 13 типов обновлений: лёгкое/полное/легкая конвертация/посхемное/мастер-реплика/патчи/скрипты/кластеры/внешние + сводная таблица (status: current)
- [[UpdateSystem-MetadataRegistration]] (c-000082) — регистрация метаданных: сервис metadata-registrator; критичная/отложенная/упрощённая (ExtCollector); методы Prepare/Update/Commit/Rollback; RegisterAtOnce (status: current)
- [[UpdateSystem-DistributionStorage]] (c-000078) — хранилище дистрибутивов: задачи, saby-пакеты, архитектура, права, public distribution storage (status: current)
- [[UpdateSystem-UpdateSabyRu]] (c-000084) — CDN update.saby.ru: API MASTER/SHAPER/SYNCER/UPDATE серверы; провайдеры EdgeCenter/CDNNOW; стенды TEST/FIX/PROD (status: current)
- [[UpdateSystem-DBConversion]] (c-000077) — Конвертация БД: stateless K8s service database-converter, jinnee-utility, Redis-очередь, автомасштабирование; 5 типов задач конвертации (status: current)
- [[UpdateSystem-ReleasePlans]] (c-000083) — ТД Планы выпуска: release-manager/release-external архитектура, публичное API (4 метода), 7 типов работ, ограничения запуска, рабочий процесс (status: current)
- [[ReleasePlans-System]] (c-000076) — Планы выпуска: оркестрация релизов через fix/fix-kz стенды, кирпич, авто-обновление, ответственности тестировщика (status: current)
- [[UpdateSystem-WorkRegistry]] (c-000088) — реестр работ и планы выпуска: полное описание связки приложений (status: current)
- [[UpdateSystem-WorkRegistryApp]] (c-000089) — приложение «Реестр работ»: UI и функциональность (status: current)
- [[UpdateSystem-WorkTypes]] (c-000090) — типы работ: таксономия (status: current)
- [[UpdateSystem-WorkAnalysis]] (c-000087) — анализ выполненных работ: инструкция (status: current)
- [[UpdateSystem-Glossary]] (c-000081) — глоссарий системы обновлений: термины и определения (status: current)
- [[UpdateSystem-ExportIsolatedClouds]] (c-000079) — экспорт планов выпуска в изолированные облака (status: current)
- [[UpdateSystem-VersionControl-Apps]] (c-000086) — приложения семейства Version Control, необходимые для планов выпуска (status: current)
- [[UpdateSystem-FAQ]] (c-000080) — FAQ системы обновлений: ошибки и решения (status: current)
- [[Wasaby-Scripts]] (c-000091) — скрипты Wasaby: создание, структура, применение через Хоттабыч (status: current)
- [[UpdateSystem-Patches]] (c-000101) — патчи: UI (Jenkins/MR) vs BL (ручной zip); metainfo ревизии; CP866/7-Zip; техническая реализация внутри Хоттабыча (status: current)
- [[UpdateSystem-VersionControl-TD]] (c-000102) — ТД Управление версиями: МАО, 12 типов задач, 7 фаз, скрипты (DeveloperScriptExecuteAll), агент, sbis-update-exec, схема БД, расписание (status: current)
- [[UpdateSystem-DistributionStorage-DB]] (c-000103) — схема БД хранилища дистрибутивов: сущности (Продукт/ВерсияПродукта/Сервис/Модуль/Образ/ФайлХранилища), md5-дедупликация, ref-counting удаление, индексы (status: current)

## Система обновлений — Sources

- [[sistema-obnovleniy-2026-06-12]] (c-000099) — 2026-06-12 | обзор «Система обновлений»: Хоттабыч, update.saby.ru, Конвертация БД, Планы выпуска, Регистрация метаданных, Реестр работ, Хранилище дистрибутивов
- [[db-conversion-2026-06-12]] (c-000093) — 2026-06-12 | Конвертация БД: 4 PDF, database-converter stateless K8s, Redis-only, jinnee, автомасштабирование
- [[distribution-storage-overview-2026-06-12]] (c-000095) — 2026-06-12 | Хранилище дистрибутивов: обзор, задачи, термины
- [[distribution-storage-db-2026-06-12]] (c-000094) — 2026-06-12 | Хранилище дистрибутивов: схема БД
- [[distribution-storage-technical-2026-06-12]] (c-000096) — 2026-06-12 | Хранилище дистрибутивов: архитектура saby-пакетов, алгоритмы, ТД
- [[release-plans-2026-06-12]] (c-000097) — 2026-06-12 | Планы выпуска: принципы, зависимости, статусы, фильтры, ТД (7 PDF)
- [[release-plans-registry-2026-06-12]] (c-000098) — 2026-06-12 | Реестр работ / Планы выпуска: алгоритм работы, структура плана, создание нового плана, ТД
- [[update-system-work-registry-2026-06-12]] (c-000100) — 2026-06-12 | Реестр работ: реестр, типы работ, термины, экспорт в изолированные облака

---

## Price Formation — Concepts

- [[LoyaltyReferral-Module-Extraction]] — выделение рефералки в отдельный СБИС-модуль LoyaltyReferral: план Андрея (4 этапа), зависимости (mirror KZ, rightcheck→Rights-Py, user_service_cloud→UserServiceCloud-Py), регистрация в online32.s3srv:454, симлинки tests_new→tests, echo-метод, грабли test_manager (задача 05256826) (status: developing)
- [[ReferralProgram-SetPrice-Record-Return]] — SetStubPrice/SetLeadPrice возвращают Record(AccruedCount, NotAccruedCount) вместо int; «скольким начислено / нет» как в DiscountCard.BatchDeleteOrLock (задача 04307161, saby bank) (status: developing)
- [[ReferralProgram-Data-Model]] — модель данных реф. программ: ВидЦены→Раздел→БизнесГруппа, AdObject-источники, access_data_guid, utm_rfcid, миграция между Реф. Сетями (задача 06096778) (status: developing)

## Price Formation — Decisions

- [[Loyalty-IterativeLoading-TD-CommonSolutions]] — ТД итеративной загрузки (пункт 594287653): мастер в Бонусах + ссылки из ДК/Промокодов/Реферальной; иерархия классов на 4100 (не-итеративные базы удалены, `GetClientListWithStats` де-итеративизирован); предложение раздела БЗ «Общие решения» (status: active)
- [[Feature-Flag-Removal-LOYALTY-IT-NAV]] — удалены фичи `loyalty_it_nav` и `bonus_it_navigation`: итеративная навигация стала постоянной, OLD path оставлен только для `GetClientListWithStats` (status: active)
- [[ReferralProgram-GetLeadPeriodList-LeadCount-Source]] — источник LeadCount: для стандартных программ — `get_sales_sources_stats` (маркетинг), для SabyBank — ВЦД по `ДатаВремя`; `ВЦД` ≠ таблица лидов (задача №04307081) (status: active)
- [[ReferralProgram-GetStubList-Filter-Redesign]] — редизайн фильтров GetStubList: два периода → единый `Date` (по дате создания или статуса в зависимости от `Status`), добавлен `PartnerId` (status: active)

## Price Formation — Analysis

- [[Bonus-GetTotalBalance-Franchise-Performance]] — задача 05292113: виджет «Бонусы» не строится на франшизном аккаунте (~80k персональных счетов), GetTotalBalance ~4.5 с; узкое место — поимённый `Card.GetBonusBalanceByCards` (передача 80k UUID + возврат 79943 строк), сам SQL по индексу 461 мс; решение — агрегат SUM на стороне СДК (status: developing)
- [[DiscountRegistry-Revive-Performance]] — оживление реестра «Скидки» offline (2567→<2300 мс): GetSaleList проксируется в облако, BL ~15% времени; первая страница идёт Seq Scan по ВидЦеныДокумент (нет индекса EffectiveDate); push-down/индекс конфликтует с EMA → выбран вариант C (UNION ALL + тюнинг _MAX_BLOCK/_K), остаток фронту (status: developing)
- [[ReferralProgram-ZeroReward-Lead-Filter-Bug]] — баг №05265686: лиды с нулевым/NULL вознаграждением не видны в фильтре «Завершено положительно»; fix: убрать `Бонусы > 0` из query + разрешить ВЦД-запись при price=0 (status: fixed)
- [[CardEmission-FullResync-PK-Conflict-Fix]] — полная пересинхронизация выпусков карт падала на duplicate key: upsert вставлял уже существующие неизменённые записи (`Updated IS NULL` ловит их, т.к. UPDATE отбирает только DISTINCT); фикс — `AND NOT EXISTS (... ВидКарты ...)` в CTE Inserted (status: fixed)
- [[PromoCode-Generation-Memory-Optimization]] — генерация промокодов без выгрузки всех существующих номеров в память: батчевая проверка кандидатов через индекс CaseInsensitiveUniqueNumber (`upper("Номер") = ANY(...)`); `filter_taken` callback; `_skip_license` паттерн для устранения дублей лицензии (status: fixed)
- [[Bonus-GetSaleList-Duplicate-W-Records-Iterative-Block-Bug]] — дубли W-записей при итеративной загрузке: СУ-документ с двумя ВЦД разных EffectiveDate разрезался границей блока → появлялся в двух API-ответах; фикс: SuspectWarehouseDocs/SuspectSaleIds CTE (status: fixed)
- [[GetClientListWithStatsTotals-Franchise-WelcomeBonus-Double-Bug]] — двойной учёт приветственных бонусов франшизной ДК в итогах реестра: is_totals-SQL не имел `AND "CardTypeUUID" IS NULL`, карта попадала в оба UUID-списка (status: fixed)
- [[GetClientListWithStats-PA-NavCondition-Duplicate-Bug]] — дубли CardId при скроллинге: pa_nav_condition фильтровал только personal_accounts, не cards_only → клиент с двумя картами дублировался (status: fixed)
- [[GetIndividualBatch-AttachPersonId-Timeout-Fix]] — таймаут рассылки SabyGet: CRMClients.AttachPersonId ~5с×100 получателей; фикс — вынос привязки персон в фоновый DWC `one_task="0"` (повтор Варианта A с исправлением рассинхрона one_task); rc-26.3211 (status: fixed)
- [[PromoCode-NotifyGenerated-DWC-Ordering]] — регресс таймаут-фикса: синхронный notify SabyGet после фоновой привязки слал пустой PersonID; фикс — `NotifyGenerated` финальной задачей того же DWC-сценария (барьер «notify после attach»; `AddTask` без parallel-block = последовательно); распространяется на все типы генерации (status: developing)
- [[SabyBank-Application-Card-Conversation-2026-05-25]] — обсуждение карточки заявки SabyBank: хранить vs тянуть данные, принадлежность телефона, API-подход; уточнить у Свешникова (status: current)
- [[soveshanie-sdacha-td-itload-2026-06-23]] (c-000146) — 2026-06-23 | ревью ТД итеративной загрузки Федько: диаграмма иерархии бракована, EMA упростить под спойлер, согласовать с [[Ютман-Элина]]
- [[zvonok-musohranov-timoshenko-2026-06-24]] (c-000144) — 2026-06-24 | ревью MR-ов CreateLead→CreateStub и GetLeadPeriodList; запрет цикла по источникам; регрессионные риски корешка при статусе 10
- [[zvonok-musohranov-timoshenko-2026-06-30]] (c-000148) — 2026-06-30 | сдача задачи корешков: миграция существующих сделок реализована, проверка невозможна до версии 400; GUI не готов; сдавать как есть с декларацией планов

## Concepts

- [[LLM Wiki Pattern]] — the pattern for building persistent, compounding knowledge bases using LLMs (status: mature)
- [[Hot Cache]] — ~500-word session context file, updated after every ingest and session (status: mature)
- [[Compounding Knowledge]] — why wiki knowledge grows more valuable over time, unlike RAG (status: mature)
- [[DragonScale Memory]] — DragonScale Architecture: 3 mechanisms (hot/fold/tiling), deterministic page addresses (status: developing)
- [[Persistent Wiki Artifact]] — wiki page as session-independent artifact; lifecycle, staleness model (status: developing)
- [[Query-Time Retrieval]] — structured retrieval over LLM wikis; why it outperforms embeddings at human scale (status: developing)
- [[Source-First Synthesis]] — synthesis pattern: source→concept with full provenance; anti-hallucination discipline (status: developing)
- [[cherry-picks]] — prioritized feature backlog from ecosystem research; 13 features to add to claude-obsidian (status: current)
- [[Wasaby-Framework]] — Wasaby platform architecture: s3cld/s3srv/s3mod, JSON-RPC, resource types, cloud services (status: current)
- [[Wasaby-Service-Architecture]] — процессная модель: монитор/координатор/эталонный/рабочий; 14 шагов запуска; файловая структура сервиса (status: current)
- [[Wasaby-Module-System]] — плагинная архитектура: 5 фаз загрузки, события модулей, API-доступность (Internal/SC/PSC), бинарные библиотеки, s3cld/s3srv/s3mod, стандарт именования, схема мульти-страна (status: current)
- [[Wasaby-Platform-Modules]] — платформенные модули: sbis (Python API), sbis_root (скрипты/debug), Image (sbis-img/Magick++), IPC Storage (shared memory KV), XML-Py (sbis-xml/xerces) (status: current)
- [[Wasaby-DB-Access-Patterns]] — IStatement/SqlQuery sync, async IAsyncQueryResult, LISTEN/NOTIFY, ITableCopier bulk ops, SQL Templates (status: current)
- [[Wasaby-SharedFuture]] — параллельные удалённые запросы: FutureInvoke (Python/C++), ParallelTasks, лимит 16 потоков, синхронный fallback, отдельная транзакция (status: current)
- [[Wasaby-Data-Types]] — FieldType enum (35+ types), temporal types with TZ handling, Decimal/Money vs double, JSON/HashTable (C++/PG/Python/JS) (status: current)
- [[Wasaby-RecordSet-Join]] — in-memory RecordSet joining: InnerJoin/LeftJoin/RightJoin, field selection, JKey aliasing, cascade joins (status: current)
- [[Multitenancy-Architecture]] — 1 client = 1 PostgreSQL schema; isolation, routing, update ops (status: current)
- [[Wasaby-Cross-Client-BL-Call]] — вызов БЛ-метода под другим клиентом+пользователем без петли: AuthByClientAndUserId, Session.Set(icsSESSION_ID), запланированный CreateMultitenantEndpointByClientAndUserId (status: current)
- [[DWC-Distributed-Workflow-Coordinator]] — DWC v2 full API: WorkflowBuilder, Sender, Task, .dwc metadata, merge policies, errbacks (status: current)
- [[DWC-Card-Events-Migration]] — миграция Card-событий на DWC; 2/4 сценариев реализовано: HandleChangeData, HandleChangeBonusBalance (status: developing)
- [[DWC-Client-Library-v1]] — DWC v1 deprecated API (workflow module, WorkflowService.Instance) (status: deprecated)
- [[Sync-Broker]] — offline-cloud sync broker; cursor-based, singleton caution (status: current)
- [[Sync-Broker-Architecture]] — full distributed architecture: 4 components, primary/regular sync, PG→CH data flow (status: current)
- [[Sync-Broker-Sharding]] — sharding subsystem: shards, router, personal queues, routing cache algorithm, migration timing (status: current)
- [[Sync-Broker-Reactive]] — reactive sync: 3 STOMP types (no-body/inline/loadable), PUSH notifications, integration API with examples (status: current)
- [[Sync-Broker-Management]] — admin interface: shard registry, metrics, object migration, rate limiting, naming conventions (status: current)
- [[Linter-Standarization-Project]] — проект подключения SonarQube+СТАН+pre-commit хуков к 10 репозиториям Лояльности и Транспорта ВИС; завершён 04.05.2026, перерасход +19.1% (status: completed)
- [[SonarQube-Stan-Linter-Setup]] — пошаговая инструкция: TSLint→ESLint, report, исправление, pre-commit хуки, SonarQube sonar2 (status: current)
- [[Price-Formation-Test-Runner]] — запуск тестов по классу/файлу/директории; пути run/, py_tests_runner, sbis_root, таймауты, /run-tests skill (status: current)
- [[PriceFormation-Test-Framework]] — фреймворк юнит-тестирования price-formation (status: current)
- [[ReferralProgram-GetPartnerList-Unjoined-Partners]] — GetPartnerList: CTE+LEFT JOIN вместо INNER JOIN, курсор PartnerId, SearchString в Python, партнёры без реферального кода через AgentContract (status: completed)
- [[BonusChart-IterativeBlock-Bug-Fix]] — итеративный блок (10K ВЦД DESC) обрезал данные графика до конца месяца; фикс: 2B limit + skip EMA при WithoutResults=True (status: developing)
- [[PostgreSQL-CTE-Cursor-Pushdown]] — проталкивание курсора пагинации внутрь CTE до GROUP BY; 3-4x ускорение без индекса; паттерн корректности для 1-к-1 CTE (status: current)
- [[JSONB-Array-Containment-Optimization]] — PostgreSQL: замена EXISTS+jsonb_array_elements_text на @> оператор; устраняет SubPlan, снижает время с ~435ms до ~1ms (status: current)
- [[Python-Code-Standards-SBIS]] — PEP-8 + Wasaby exceptions: 120 chars, CamelCase for platform methods (status: current)
- [[Tensor-TechDoc-Standards]] — when/what/how to write ТД: structure, audience matrix, formatting rules, anti-patterns (status: current)
- [[Python-Localization-rk]] — rk() function rules: no static vars, no concatenation, plurals (status: current)
- [[Bonus-GetSaleTotals-Timeout-Fix]] — bugfix: таймаут заголовка реестра Бонусы/Покупки; MIN(EffectiveDate) без фильтра → 17s/3M строк; fix: новый индекс BonusSaleEffectiveDate (ВидЦены, EffectiveDate) (status: active)
- [[ReferralBonus-GetSaleList-Iterative-Ordering-Bug]] — bugfix реестра рефералки: (1) дубли SaleId → GROUP BY Sale + MAX(EffectiveDate) + ORDER BY SaleId; (2) хаотичный порядок при скролле вверх → backward даёт ASC, фронт разворачивает; инверсия вставки графиков/итогов в общем `add_graphic_data` по `navigation.Direction()` (status: fixed)
- [[FranchiseCard-Import-POS-SaleValidation-Bug]] — баг: импортированные карты участника франшизы блокируются на POS; root cause: SkipServiceNotification пропускает DCS-нотификацию; fix: async_notify_changed_cards в _process_card_item (status: fixed)
- [[ImportDiscountCard-Franchise-Client-Import]] — архитектура импорта клиентов из Excel для франшизных карт: Client/Card классы, два пути CRM (CreateCustomerWithConfirmedPerson vs GetCustomerOrCreate), различие get_or_create_personal_card_ext vs attach_person_to_client (status: developing)
- [[ImportDiscountCard-DCS-Counter-Bug]] — баг: счётчик карт в реестре не обновлялся после импорта; root cause: return value `_extract_cards_from_data` не присваивался; fix: однострочное исправление + убран дублирующий вызов в franchise-ветке (status: resolved)
- [[Loyalty-Database-Schema]] — ВидЦены/Карта/ВидЦеныДокумент schema; all loyalty events in one table (status: current)
- [[Loyalty-Product-Overview]] — Акция + ДК + Промокод core entities; subsystems; integrations (status: current)
- [[Loyalty-Cloud-Config]] — DCService cloud params, anti-bot config, 4 scheduler tasks (status: current)
- [[Loyalty-Public-API]] — Card, Promocode, SalePoint, Pass, LoyaltyProgram API; barcode types (status: current)
- [[Loyalty-UI-Components]] — component library: widgets, sale UI, condition editor, charts, import (status: current)
- [[Loyalty-In-Products]] — feature matrix per product; Retail/Presto/СУ/SabyDocs offline limitations (status: current)
- [[RetailPresto-Offline-Debug-Setup]] — подмена BL-модулей для отладки офлайн-приложений: отключение автообновления, MainService.s3srv, sbis-config.ini, user_data; только Debug-версия (c-000074) (status: current)
- [[Bonus-Programs-Architecture]] — bonus accrual flows, balance calculation, supplementary accrual, offline limits (status: current)
- [[Bonus-GetTotalBalance]] — Bonus.GetTotalBalance BL method: local SQL + SDK franchise balance; IsFranchise SQL patterns; review fixes (status: current)
- [[BonusDecRule-Info-Model]] — BonusDecRule (Type=40) full data model: Benefit, ThresholdConditions, TriggerConditions (status: current)
- [[Bonus-Deduction-Algorithm]] — 3-priority deduction plan, 0%-as-blocker rule, bonus calculator formulas (status: current)
- [[DiscountCard-Subsystem-Overview]] — ДК types, СДК 5-part architecture, service decomposition, integrations (status: current)
- [[DiscountCard-Service-API]] — Card.* and CardTemplate.* user/admin API; error codes 1000–1150 (status: current)
- [[DiscountCard-Algorithms-Processes]] — external access rights, confidential data encryption, inter-service diagrams (status: current)
- [[DiscountCard-UI-Specifics]] — card type registry UI, data loading sequences, master-detail structure (status: current)
- [[PassUpdater-Service]] — Task/Request/MessageBox model; AW vs GPay; EntryPoint queue; scheduler tasks (status: current)
- [[DiscountCard-Diagnostic-Service]] — admin panel for tasks/requests, promo concierge, DB indexes (status: current)
- [[DiscountCard-Admin-Ops]] — inside.sbis.ru ClickHouse monitoring; auto-update triggers; AW/GPay infra setup
- [[DiscountCardType-GetListSimple-FranchiseGroupId-Bug]] — баг 4283565: пустой список типов карт в офлайне из-за FranchiseGroupId="retail" в SQL-фильтре (status: current)
- [[EntitySP-UniqueId-Migration]] — entity_sp: конвертация @Лицо→UniqueId на READ-стороне; паттерн ConvertFaceIdsToUniqueIds; тест-паттерн с @with_feature (status: current)
- [[Promocode-Subsystem-Overview]] — 4 promo code types (Общий/Индивидуальный/Партнёрский/ЗаАктивность); technically = discount card (status: current)
- [[Promocode-Info-Model]] — PromoCode object hierarchy; PromoCodeEmission/Item; ConditionData fields; NumberFormat (status: current)
- [[ReferralDeals-System]] — Owner/Partner deal referral system; sabyReferralProgram.CreateLead; reward via bonuses; 10 DB queries; 3 widgets (status: current) (status: current)
- [[Акции-Subsystem-Overview]] — базовая сущность лояльности; терминология скидок, наценок; ограничения применения (status: current)
- [[Акции-Info-Model]] — Promotion/Discount объектная модель; Conditions 15+ полей; Profit/Threshold структуры (status: current)
- [[Акции-Architecture]] — конкурс скидок 3-приоритетный; суммируемые скидки; комплектные; алгоритм округления; OOP Discount hierarchy (status: current)
- [[Акции-UI]] — LoyaltyOnline/Promotion/registry:Browser; promoRegistry:Base мастер-деталь; компоненты карусели/баннера/продаж (status: current)
- [[SabyBank-RKO-Referral]] — проект рефералки в заявках на РКО; корешки ВЦД, 3 API, 4 этапа, выпуск 18.08.26 (status: current)
- [[SabyBank-RKO-TZ]] — полное ТЗ: API-методы, схема хранения, выборки БД с индексами, UI-декомпозиция (status: current)
- [[SabyBank-RKO-WorkPlan]] — план работ 166,5 дня: этапы, сроки, исполнители по каждой задаче (status: current)
- [[SetLeadPrice-SABYBANK-Stub-Branch]] — ветвление SetLeadPrice по ProgramType.SABYBANK: корешки фильтруются по ТипСвязи IS NOT NULL (status: current)
- [[SabyBank-Stub-Rewards-Calculation]] — GetLeadPeriodList и sql_get_price_stats (GetStats/GetStatsByPartner) переведены на корешки для SabyBank; SQL-паттерн `<> 1 OR ТипСвязи IS NOT NULL`; IsSabyBank Python-флаг (status: current) — ветвление SetLeadPrice по ProgramType.SABYBANK: корешки фильтруются по @ВидЦеныДокумент+ТипСвязи IS NOT NULL вместо Документ; история не пишется (status: current) — проект: рефералка для банковских заявок на РКО по API; корешки ВЦД, 3 API метода, 4 этапа, срок 18.08.26 (status: current)
- [[Loyalty-React-Migration-Project]] — проект: перевод 5 разделов лояльности на React; 147,5 чд, дедлайн 27.02.26; новый Bonus.GetBaseSettings, курсорная навигация, порционная загрузка (status: active)
- [[AT-Coverage-ReferralDeals-Project]] — проект АТ-покрытия реферальной системы сделок: 0%→95% МК, 9 этапов, дедлайн 31.05.26 (status: current)
- [[DWC-Migration-SDK]] — проект: перевод СДК с событий на DWC; 76 дней, 14 событий→задач, приоритеты по нагрузке, дедлайн 30.07.26 (status: current)
- [[Loyalty-Desktop-Broker-Migration]] — проект: перевод sync лояльности Desktop Розница/Presto (~29 000 копий) на брокер; 5 сущностей, feature flag lty_broker_card_type, ~60д (status: developing)
- [[DWC-Promocode-Events-Migration]] — реализация этапа «Промокоды→DWC»: 4 события, 9 файлов, feature flag `dwc_promocode`, паттерн publish_*/DWC (status: developing)
- [[DWC-Card-Events-Migration]] — реализация этапа «Карты→DWC»: 4 сценария, feature flag `dwc_card`; задача 1 Card.HandleChangeData реализована (status: developing)
- [[DWC-BonusSettings-Events-Migration]] — реализация этапа «Настройки бонусов→DWC»: 2 события, feature flag `dwc_bonus_settings`, 4 файла (status: developing)
- [[BrokerLoyalty-BonusSettings-Race-Fix]] — bugfix: гонка SyncBrokerClient при lty_broker_bonus_set → сломанный курсор промокодов; fix: BonusSettings перенесён в BrokerSyncLoyalty/SyncManager (status: active)
- [[BonusSettings-Sync-Restart-Bug]] — bugfix: при lty_broker_bonus_set настройки бонусов не обновлялись при рестарте; fix: PullAll→re_sync (reset cursor→FirstSync), в shelf (status: shelved)
- [[ReferralProgram-DetachPartner-Implementation]] — `ReferralProgram.DetachPartner` для AT: удаление реферального кода партнёра (Карта+CRM+ВидЦеныДокумент), защита от боя, OWNER_MODERATOR (status: active)
- [[ReferralProgram-Stub-Implementation]] — `ReferralProgram.CreateStub` + `UpdateStub`: 2 метода, 4 бизнес-сценария, StatusDate/EffectiveDate правило, LinkType константы, SQL+тесты; ревью Мусохранова 2026-06-24 (status: active)
- [[ReferralProgram-GetLeadPeriodList-LeadCount-Source]] (c-000145) — решение: LeadCount/RewardSum из одного запроса к ВидЦеныДокумент, без цикла по источникам через marketing-API (status: active)
- [[ReferralStub-TargetAction-Pattern]] — паттерн целевого действия корешков: TargetAction, StatusDate, FilterByStatus (status: current)
- [[LRS-Long-Request-Service]] — LRS надстройка над DWC: фоновые операции, прогресс, результаты, история 90д, шардированная БД, бесшовное обновление (status: current)
- [[Loyalty-Sale-Application]] — подсистема применения лояльности на продаже: задачи, C++ ядро CalcDiscount, цикл расчёта, скидки/подарки/бонусы/штампики, режим оферты, организация кода (status: current)
- [[Profiles-Service]] — Сервис Профилей: Персона-UUID, 3 контура (RW/RO-any/RO-spec), bi-directional sync, local-first стратегия (status: current)
- [[Saby-Feature-Toggles-API]] — Feature class API: IsOn/GetValue/FlagsIsTrue для C++/Python/JS/mobile/offline; mock, stub, bitmap, accordion (status: current)
- [[Saby-Service-Config]] — параметры сервисов vs переключатели функционала: сравнение, именование, выбор инструмента (status: current)
- [[Referral-Bonus-Program]] — реферальная бонусная программа (ВидЦены.Тип=9): начисление за рекомендации, 3 уровня иерархии, SabyGet UI (status: current)
- [[Prompts-Cashier-Hints]] — подсказки кассиру (ВидЦены.Тип=18): popup hints at POS, conditions, benefit types, controller session cache, API, DB schema (status: current)
- [[Markup-Subsystem]] — Наценка (ВидЦены.Тип=32): гибкая надбавка к цене, авто/ручная, Сервисный сбор, RetailSaleDoc.CalculateDiscount(WithMarkup), права «Каталог и Цены» (status: current)
- [[ExternalLoyalty-Integrations]] — UDS + PremiumBonus + iikoCard: алгоритмы, архитектура, ограничения, возвраты, обработка ошибок (status: current)
- [[ExternalLoyalty-iiko-Integration]] — iikoCard детали: алгоритм продажи, 6 API методов, отладка (24ч файл), DB schema, тех. скидки (status: current)
- [[ExternalLoyalty-Info-Model]] — объектная модель: ВнешняяБонуснаяСистема 4 метода; ПрименениеКарты/Скидки/Бонусов; КартаЛояльности (status: current)
- [[PriceFormation-Backend-Architecture]] — карта Python-модулей репо: Common/Online/Offline/DCCommon; субпакеты, .orx/.dicx/.hox/.dwc артефакты, паттерн «1 файл = 1 метод» (status: current)
- [[PriceFormationOnline-Core]] — PriceFormationOnline core module: statistics, history, online price computation (status: evergreen)
- [[PriceFormationOnline-Helpers]] — PriceFormationOnline helpers: request dispatch, apply-loyalty, list adapters (status: evergreen)
- [[PriceFormation-Common-Helpers]] — cross-package price formation utilities and shared helpers (status: evergreen)
- [[DCCommon-Helpers]] — DCCommon shared helpers for the discount card subsystem (status: evergreen)
- [[Loyalty-Franchise-Mechanics]] — алгоритмы событий лояльности для франшизных сценариев (status: current)
- [[Franchise-Contract-API]] — API договоров франшизы: методы FranchiseContract.* (status: current)
- [[Franchise-Loyalty-Architecture]] — архитектура лояльности франшизы (status: current)
- [[Franchise-Loyalty-System]] — система лояльности франшизы (status: current)
- [[Franchise-SabyNet-Subsystem]] — подсистема Saby Net для франшизы (status: current)
- [[Wasaby-BL-Call-Loop-Pattern]] — петля вызовов БЛ: причины (EndPoint+auth_data в одном ClientID), решение: CreateMultitenantEndpointByClientId; антипаттерны TenantContext (status: current)
- [[Wasaby-BL-Methods]] — таксономия методов БЛ; 7 типов; доступность Service Contract/Internal; наследование; перекрытие по имени (status: current)
- [[Wasaby-BL-CRUD]] — Create/Read/Update/Delete/Copy/Merge/DeleteSelected/Sync: сигнатуры, алгоритмы, обработчики (status: current)
- [[Wasaby-BL-List-Methods]] — декларативный + ручной список; ДопПоля/Фильтр/Сортировка/Навигация; типы фильтра Free/Linked/Hierarchical; DoS-защита ≤100 записей (status: current)
- [[Wasaby-BL-List-Advanced]] — расширенные паттерны: курсорная/мульти навигация, порционная загрузка, ListIterator, ShowMarked, MoveToFolder, Sum.ByMethod, TranslitListCall, ListWithParents (status: current)
- [[CursorNavigation-Mechanism]] — механизм курсорной навигации (status: evergreen)
- [[Wasaby-Dev-Standards]] (c-000105) — стандарты разработки бэкенда Wasaby: Python/C++/SQL; Radon/Pylint инструменты; формула code review score (status: current)
- [[Wasaby-SQL-Standard]] (c-000106) — стандарт SQL: PascalCase, 3-пробела, запятые после поля, именование @PK/rTable-Field/iTable-Index (status: current)
- [[Wasaby-Python-Standard]] (c-000107) — стандарт Python: PEP-8 + 120 символов, CamelCase для методов БЛ, антипаттерны (Божественный объект, хелперы) (status: current)
- [[Wasaby-Cpp-String-Standard]] (c-000108) — C++ строки: StringView/String/StackString выбор, StringBuilder, Format/ToString/FromString (status: current)
- [[Wasaby-Service-Framework]] (c-000109) — сервисный фреймворк: архитектура слоёв, сервис-контракт, сервер приложений, EndPoint (status: current)
- [[Wasaby-BL-Calls]] (c-000110) — паттерны вызова БЛ: синхронный/асинхронный/удалённый, протоколы (AMQP/RBC/HTTP), политики auth, Huge Payload (status: current)
- [[Wasaby-BL-Objects]] (c-000111) — объекты бизнес-логики: иерархия, типы методов (CRUD/List/File/Remote), наследование, Is always permitted (status: current)
- [[Wasaby-Unit-Testing]] (c-000112) — юнит-тестирование: test_framework, pytest/unittest, структура проекта, mock_service (Python/C++), monkeypatch EndPoint (status: current)
- [[Wasaby-SQL-DBA]] (c-000113) — дайджест Habr-статей Тензора: explain.tensor.ru, антипаттерны PostgreSQL, SQL HowTo, DBA (status: current)
- [[Wasaby-Long-Running-Operations]] (c-000114) — LRS: WorkflowBuilder, SetCustomData, ResultLink/ResultTmpl, LongRequestNotify, прогресс (status: current)
- [[Wasaby-Task-Queue]] (c-000115) — plugin-task-queue: Task.Create/GetByDestinationList/Processing/ErrorProcessed; лимит 256/вызов (status: current)
- [[Wasaby-Service-Node-Architecture]] (c-000116) — архитектура узла: монитор/координатор/эталонный/рабочий процесс, конфиг (процессы/потоки/очередь/память), QoS (status: current)
- [[Wasaby-i18n]] (c-000117) — i18n/l10n: rk() Python/C++, словари переводов (@@/plural#), локаль lang-COUNTRY, правила (no concat, no static) (status: current)
- [[Wasaby-Third-Party-Libraries]] (c-000118) — сторонние библиотеки: pip-repo + s3mod resource (Python), Conan + CMakeLists sbis_conan_run/sbis_use_library (C++) (status: current)
- [[Wasaby-Parameters-Service]] (c-000119) — сервис параметров: scopes (GLOBAL/USER/ACCOUNT/DEVICE), Parameter.Read/Set/Erase, ConfigLoader JS API (status: current)
- [[Wasaby-Distributed-Locks]] (c-000120) — distributed-locks: ReadLock/WriteLock, ResourceId (class+key+shard), Acquire/TryAcquire/AcquireImmediatelyOrThrow, DetachedRef (status: current)
- [[Wasaby-ClickHouse]] (c-000121) — ClickHouse OLAP: Dbi Clickhouse Py, GetConnectedDatabase, TableCopier.AddRecord/Flush, EscapeIdentifier, ALTER ON CLUSTER (status: current)
- [[Wasaby-FTS]] (c-000122) — полнотекстовый поиск Elasticsearch: sbis_fts.Object, Upsert/List/Aggregation, ListParams (searchString/filter/exactMatch), highlight (status: current)
- [[Wasaby-File-Transfer]] (c-000123) — file-transfer: FileTransferUpload/Download/Delete (RpcFile), хранилища excel/huge_payload_storage, REST /file-transfer/service/<storage>/<id> (status: current)
- [[Wasaby-Memray]] (c-000124) — профилировщик памяти Python (Bloomberg): memray_script.sh record/flamegraph, --no-symbols/--symbols/--non-aggregated, режимы: flamegraph/table/tree/summary/stats (status: current)
- [[Wasaby-Perforator]] (c-000125) — профилировщик CPU (Яндекс), требует RHEL9+, perforator_script.py, заказ через ЦОД, UI perforator.sbis.ru, flamegraph/pprof (status: current)
- [[Wasaby-Python-Debug]] (c-000126) — отладка Python: VSCode через sbis_root/sbis.AuthByUserID/Session.Set; PyCharm Remote Debug pydevd-pycharm (≤2022.3.3), settrace() (status: current)
- [[Wasaby-History-Service]] (c-000127) — сервис истории изменений (ClickHouse): HistoryMsg/HistoryMsgSet, @override_*, История.History_Common_Object, хранение 3 года (status: current)
- [[Wasaby-MQ]] (c-000128) — RabbitMQ шины: серверные события + AsyncInvoke (MessageBroker/sbis-msg-broker), 2 слоя Proxy+Main, Huge Payload Protocol >100KB → file-transfer (status: current)
- [[Wasaby-Request-Broker]] (c-000129) — брокер async-вызовов с гарантией: отслеживание статуса по ID, backup-сервис с компенсацией, для DWC/Scheduler (status: current)
- [[Wasaby-Scheduler]] (c-000130) — планировщик задач: расписание (интервал/ежедневно/еженедельно/ежемесячно), Genie, итеративные задачи, приоритеты параметров (status: current)
- [[Wasaby-Report-Prefetch]] (c-000131) — кэширование больших отчётов: Prefetch.List, PrefetchMethod/Pages/SessionId, иерархия, сортировка на стороне Prefetch, fallback при ошибке (status: current)
- [[Report-Prefetch-Service]] — сервис предварительного расчёта отчётов: архитектура, интеграция (status: current)
- [[ReportPrefetch-DB-Schema]] — схема БД Report Prefetch: таблицы и индексы (status: current)
- [[Wasaby-HTML-Converter]] (c-000132) — HTML→PDF: converter_html/PdfConverter.ConvertHtml/ConvertUrl/ConvertHtmlToFileTransfer, webshot/ImageConverter, delayed print (status: current)
- [[Wasaby-Informers]] (c-000133) — информеры/счётчики: Redis-кэш, Counters.Set, Informers.GetJoinData, восстановление через планировщик 100мс (status: current)
- [[Wasaby-Multimedia-Loader]] (c-000134) — загрузка файлов из интернета по URL: Get/1/2, GetWithPipeline/2; pipeline: Antivirus/MimeTypes/ToFileTransfer/ToSbisDisk (status: current)
- [[Wasaby-PDF-Transformer]] (c-000135) — конвертация PDF→PDF/A: ConvertPDFToPDFA/2 и /3; Conformance Level1A–Level4F (status: current)
- [[Wasaby-Profiles-Service]] (c-000136) — централизованный сервис профилей пользователей: Персона/UUID, три контура RW/RO-any/RO-spec, двусторонняя синхронизация (status: current)
- [[Wasaby-DWC]] (c-000137) — Distributed Workflow Coordinator: граф задач, rate limiting, merge/dedup вызовов, отложенное исполнение (status: current)
- [[Wasaby-Image-Service]] (c-000138) — img-remote: stateful сервис обработки изображений (ImageMagick); сессия = один BL-вызов; использовать только через Image-BL модуль (status: current)
- [[Wasaby-Conan]] (c-000139) — Conan C++ package manager: 1 lib=1 recipe=1 repo, Jenkins builds, conan-server, local_build.py, версия = версия платформы (status: current)
- [[Wasaby-STOMP]] (c-000140) — STOMP bus: BL→AMQP→Route→Web→WebSocket клиент; exchange !web-entrypoint; области доставки user/client/global (status: current)
- [[Wasaby-Mass-Mailings]] (c-000141) — сервис массовых рассылок: md_client.MassDistribution, SetReceiver/DelReceiver/Commit; задачи выполняются через DWC per subscriber (status: current)
- [[Wasaby-Sync-Broker]] (c-000142) — облачный брокер синхронизации: хранит факты изменений, реактивная синхронизация через STOMP-уведомления (status: current)
- [[LoyaltyPrograms-IterativeListLoading]] — ListWithCursor, ListWithCompositeCursor, IterativeBlockSizeEmaMixin, SaleListWithCursor: итеративная порционная загрузка реестров покупок (status: current)
- [[Wasaby-BL-Advanced]] — кэширование, таймауты (Call/Execution/SetTimeout), Antibot (Frequent call protection), Access area, Handlers, Custom method, ConfidentialOutput/Scope, Proxy/HTTP, File methods (status: current)
- [[Wasaby-Python-Patterns]] — sbis.Error/Warning; `with CreateTransaction`; работа с файлами через with (status: current)
- [[Wasaby-CPP-Python-Integration]] — три анти-паттерна крэша при работе с C++-объектами Record/RecordSet из Python (status: current)
- [[Wasaby-RecordSet-Performance]] — оптимизация Record/RecordSet из Python: Fill/AddRow/ToListOf/SqlQueryOf/ToList/ToDict/GroupBy; избегать IField churn и лишних bridge-переходов (status: current)
- [[Wasaby-Performance-Budget]] — бюджет производительности Wasaby: метрики VR/TTI/REQ/Size/BL/Leak, пороги по типажам, правила, Perfalyze (status: current)
- [[Wasaby-App-Optimization]] — обзор уровней оптимизации: UI / middleware / БЛ / СУБД; карта инструментов (status: current)
- [[Хоттабыч-System]] — Система обновлений Хоттабыч: дистрибутивы, патчи, скрипты, агенты, фазы обновления (status: current)
- [[Wasaby-Patches]] — Патчи: экстренная правка файлов дистрибутива без пересборки; 4-шаговый процесс для интерфейса и БЛ (status: current)
- [[Wasaby-Scripts]] — DeveloperScript: произвольный код на сервисе через DWC, .orx, ВНР, анализ логов (status: current)
- [[Wasaby-Access-Control]] — Права: участки системы (.uax), роли (.rlx), ограничения/Access Area, наследование, разрешающая политика (status: current)
- [[SBIS-Access-Request-API]] — `rightcheck` модуль: 5 Python-хэлперов для HTTP 403 с данными запроса доступа; CheckRights API; JS `createAccessDeniedError` (status: current)
- [[Saby-External-API-Auth]] — внешний JSON-RPC API: аутентификация по логину/паролю и ЭП; сессии X-SBISSessionID; лимиты 300/мин; SMS 2FA; СБИС.Выход; СБИС.ИнформацияОТекущемПользователе (status: current)
- [[Saby-External-API-Tasks]] — СБИС.СписокЗадач: список документов «На мне»/«От меня»; структура документа; курсорная пагинация по ДатаВремя (status: current)
- [[Saby-API-Error-Codes]] — справочник classid ошибок: 1FA... (фатальные), 1AA... (нефатальные); rate limit, auth errors, retry strategy (status: current)
- [[SBIS-Record-Format]] — колоночный формат f/d/s: типы структур (recordset/record/empty), типы данных, Python-хелпер, Фильтр/Навигация как record-объекты (status: current)
- [[SBIS-Internal-API-Methods]] — внутренние методы: ПунктПлана.СписокПунктов, СлужЗап.*, Документ.*, паттерн ПрочитатьДляУчастника, поля фильтра и ответа (status: current)
- [[SBIS-DocumentMessage-ListForEDO]] — `DocumentMessage.ListForEDO`: получение диалогов задачи; формат запроса/ответа; pairMessages; rich text парсинг; пагинация через m.d.nextPosition; реализация MCP-инструмента sbis_list_task_messages (status: current)
- [[SBIS-Browser-to-API-Conversion]] — рецепт преобразования браузерного SBIS запроса (Protocol 7, массивы) в API-вызов (Protocol 1/2, объекты): d+s→dict, убрать _type/f, вложенные Запись-поля не трогать, шпаргалка (status: current)
- [[Saby-API-Protocol]] — транспортный уровень: HTTP-структура, JSON-RPC 2.0, эндпоинты, типы данных (строка/объект/массив), форматы строк (status: current)
- [[Saby-API-Document-Object]] — объект «Документ»: 30+ полей верхнего уровня, вложения+ЭП+МЧД, этапы, ссылки, ограничения на хранение в ИС (status: current)
- [[Saby-API-Navigation-Object]] — объект «Навигация»: стандартная пагинация (0–200 записей), упрощённая (СБИС.СписокИзменений), типовой паттерн обхода (status: current)
- [[Wasaby-Cloud-Management]] — cloud-ctrl: Приложения (структура облака), Очередь (мониторинг сервисов), Клиенты, Пользователи (status: current)
- [[Wasaby-Request-Routing]] — Маршрутизация HTTP/AMQP: nginx upstream, ?srv=1 (служебный пул), Varnish кэш, x_version при обновлениях (status: current)
- [[Wasaby-Distribution-Schema]] — Схема дистрибутивов online: online32/online → regional (ru/kz) → Тензор; правила добавления модулей (status: current)
- [[Wasaby-Local-Stand-Setup]] — Локальный стенд: файловая структура, тестовые домены и логины, Genie, SDK совместимость (status: current)
- [[Wasaby-RabbitMQ]] — RabbitMQ базовые концепции: exchange типы (fanout/direct/topic/headers), durability, QoS, Publish Confirms (status: current)
- [[STOMP-Events-Bus]] — Шина клиентских событий: 2 слоя (Route/Web), WebSocket+STOMP, сегментирование по CID, 3 диапазона публикации (status: current)
- [[Wasaby-MQ]] — RabbitMQ шины: асинхронные вызовы (AsyncInvoke) + серверные события + STOMP; 2 слоя (Proxy/Main), именование очередей, Huge Payload >100 КБ (c-000128) (status: current)
- [[Wasaby-BL-AsyncInvoke]] — Invoke/AsyncInvoke API: локальный/удалённый вызов, EndPoint, аутентификация, гарантии доставки (AMQP/RBC), callbacks/errbacks, SetAsyncPriority (c-000073) (status: current)
- [[Server-Events-Bus]] — Шина серверных событий: pub-sub между БЛ, гарантия через durable флаг, Proxy+Main (status: current)
- [[Request-Broker-Service]] — request-broker: трекинг статуса async-запросов для DWC/Scheduler; 3 компонента, berkeley-db, backup-компенсация (status: current)
- [[Parameters-Service]] — Сервис параметров: 6 типов scope, шардирована, TTL 30/180 дней, Permanent/Synchronizable, parameters-constants (status: current)
- [[Parameters-API]] — Parameters API: клиентское (ParametersWebAPI/Scope), серверное (Parameter.*), 12+ методов (status: current)
- [[SabyDisk-Platform]] — Платформа SabyDisk / Saby Space: 12+ сервисов, SWIFT/CEPH, горячий кэш, циклическая запись (status: current)
- [[FileStorage-Service]] — FileStorage: внутреннее хранилище файлов сервисов; REST API; шардированная БД, утилизация метаданных (status: current)
- [[File-Transfer-Service]] — file-transfer: временные файлы (TTL); LRS-результаты + Huge Payload Protocol; API Upload/Download/Delete (status: current)
- [[Binary-Storage-Options]] — Выбор хранилища: SabyDisk vs FileStorage vs file-transfer — сравнительная таблица (status: current)
- [[AVIF-to-PNG-Windows-Conversion]] — конвертация AVIF→PNG на Windows: `py` + Pillow; почему WIC и `python3` не работают (status: current)
- [[Claude-Code-VseGPT-Provider]] — переключение Claude Code на VseGPT как альтернативный API-провайдер: ANTHROPIC_BASE_URL, токен, маппинг моделей (status: current)
- [[SabyGet-Product-Overview]] — Saby Get агрегатор заведений: функции, аудитория, платформы, разделы сайта по ролям (status: current)
- [[SabyGet-Landing-Page]] — разводящая страница: flow региона, алгоритм весов каруселей, data architecture Карты/Бонусы/Промокоды (status: current)
- [[SabyGet-Loyalty-Subsystems]] — Карты / Бонусы / Промокоды на SabyGet: BL-методы, UI, реферальная программа (status: current)
- [[Pro Hub Challenge]] — open-source community challenge for AI marketing hubs with Claude SEO (status: evergreen)
- [[SEO Drift Monitoring]] — SERP change detection and content drift monitoring (status: evergreen)
- [[Search Experience Optimization]] — SXO: search UX, SERP analysis, user intent signals (status: evergreen)
- [[Semantic Topic Clustering]] — content strategy: semantic topic clusters for SEO (status: evergreen)
- [[SVG Diagram Style Guide]] — SVG brand and diagram standards for claude-obsidian (status: evergreen)

---

## Concepts

- [[Tensor-Culture]] — 8 принципов + правила поведения компании Тензор; культура вокруг человека, простоты, действия (status: current)
- [[Tensor-Glossary]] — корпоративный словарь: 12 ключевых терминов Tензор/Saby (status: current)
- [[Saby-Product-Lineup]] — полный каталог продуктов Saby по вертикалям с ответственными лицами (status: current)
- [[Saby-Naming-Guide]] — официальные правила написания названий: СБИС → Saby; 25+ продуктов, 18 мобильных приложений (status: current)
- [[Loyalty-System-Teams]] — оргструктура направления «Система лояльности»: 4 команды, org-chart, руководители (c-000043) (status: current)
- [[Transport-VIS-Platform]] — платформа взаимодействия с ВИС: 10M+ RPS, маркировка, маркетплейсы, балансировка, ЦОД-метрики (c-000044) (status: current)

## Entities

- [[Тимошенко А.А.]] — инженер-программист 2+, Тензор; BL loyalty/price-formation, SabyBank RKO Referral, DWC-промокоды (status: current)
- [[Tensor-Company]] — Тензор: федеральный IT-холдинг, Saby/СБИС, 4.5M+ клиентов, №1 ЭДО в России (status: current)
- [[Мусохранов-Андрей-Владиславович]] — руководитель направления 2+, Система лояльности + Транспорт ВИС (c-000036) (status: current)
- [[Ютман-Элина]] — разработчик, ответственная за систему бонусов PriceFormation.Online; итеративная загрузка (c-000147) (status: current)
- [[Федько-Юрий-Сергеевич]] — руководитель направления 2, Система лояльности; интеграции UDS/PremimBonus/iikoCard (c-000037) (status: current)
- [[Алябушев-Александр-Александрович]] — ведущий разработчик 3+, Акции и бонусы / механика скидок (backend) (c-000038) (status: current)
- [[Омельяненко-Егор-Анатольевич]] — ведущий разработчик 3+, Дисконтные карты / лояльность на продаже (backend); руководитель Тимошенко А.А. (c-000039) (status: current)
- [[Курников-Михаил-Сергеевич]] — ведущий разработчик 3+, Система лояльности (frontend); цены, бонусные программы, очереди задач (c-000040) (status: current)
- [[Дюднева-Светлана-Андреевна]] — ведущий тестировщик 3+, QA Система лояльности; куратор Маренин И. (c-000041) (status: current)
- [[Чумакин-Андрей-Андреевич]] — ведущий разработчик 2, Транспорт ВИС; 10M+ RPS, маркировка, маркетплейсы (c-000042) (status: current)
- [[Andrej Karpathy]] — AI researcher, creator of the LLM Wiki pattern, former Tesla AI director (status: developing)
- [[ReferralProgram-Module]] — partner referral system in PriceFormation.Online; leads, rewards, stats, SabyBank extension (status: current)
- [[Ar9av-obsidian-wiki]] — multi-agent compatible LLM Wiki plugin; delta tracking manifest (status: current)
- [[Nexus-claudesidian-mcp]] — native Obsidian plugin + MCP bridge; workspace memory, task management (status: current)
- [[ballred-obsidian-claude-pkm]] — goal cascade PKM; auto-commit hooks, /adopt command (status: current)
- [[rvk7895-llm-knowledge-bases]] — 3-depth query system, Marp slides, parallel deep research (status: current)
- [[kepano-obsidian-skills]] — official skills from Obsidian creator; defuddle, obsidian-bases (status: current)
- [[Claudian-YishenTu]] — native Obsidian plugin embedding Claude Code; plan mode, @mention (status: current)
- [[Claude SEO]] — open-source SEO intelligence tool built on Claude Code; semantic clustering, SERP analysis (status: evergreen)

---

## Sources

- [[retail-presto-offline-dev-2025]] — 2026-06-11 | 2 docs: инструкция по разработке в офлайне + диалог о подмене модулей | 1 concept created (c-000074) (status: current)
- [[loyalty-vis-org-2026-05-26]] — 2026-05-26 | пasted text: оргструктура «Система лояльности + Транспорт ВИС» | 9 pages created (c-000036..c-000045)
- [[tensor-company-docs-2026-04-12]] — 2026-04-12 | 4 docs: company culture, principles, rules, glossary | 3 pages created
- [[messaging-middleware-2026-04-12]] — 2026-04-12 | 5 docs: RabbitMQ + STOMP + async/server buses + request-broker | 5 pages created
- [[parameters-service-2026-04-12]] — 2026-04-12 | 4 docs: parameters service + declarative + API + constants | 2 pages created
- [[storage-services-2026-04-12]] — 2026-04-12 | 5 docs: SabyDisk + FileStorage + file-transfer + хранение | 4 pages created
- [[wasaby-list-advanced-2026-04-14]] — 2026-04-14 | 10 docs: Wasaby BL list advanced patterns | 1 page created, 1 updated
- [[loyalty-react-migration-2026-04-14]] — 2026-04-14 | 3 docs: цель, ТЗ, план работ проекта перевода лояльности на React | 2 pages created
- [[at-coverage-referral-deals-2026-04-12]] — 2026-04-12 | 2 docs: план работ + ТЗ проекта АТ-покрытия | 1 page created
- [[wasaby-bl-docs-2026-04-10]] — 2026-04-10 | 37 Wasaby BL Framework docs | 6 pages created
- [[external-loyalty-2026-04-10]] — 2026-04-10 | 6 External Loyalty docs (UDS/PB/iiko) | 3 pages created, 1 updated
- [[markup-subsystem-2026-04-10]] — 2026-04-10 | 4 Наценка docs from raw/ | 1 page created, 1 updated
- [[prompts-subsystem-2026-04-10]] — 2026-04-10 | 4 Подсказки docs from raw/ | 1 page created, 1 updated
- [[sabybank-rko-referral-2026-04-10]] — 2026-04-10 | 4 SabyBank RKO docs from raw/ | 1 page created
- [[wasaby-db-access-2026-04-10]] — 2026-04-10 | 5 Wasaby DB docs from raw/ | 1 page created
- [[claude-obsidian-ecosystem-research]] — 2026-04-08 | web research across 16+ repos | 8 wiki pages created
- [[price-formation-docs-2026-04-10]] — 2026-04-10 | 12 docs from price-formation/docs/ | 8 wiki pages created
- [[loyalty-knowledge-base-2026-04-10]] — 2026-04-10 | 6 docs from raw/ | 6 wiki pages created
- [[bonus-subsystem-2026-04-10]] — 2026-04-10 | 6 Бонусы docs from raw/ | 3 pages created, 1 updated
- [[discount-cards-batch-2026-04-10]] — 2026-04-10 | 10 docs from raw/ | 7 pages created, 3 updated
- [[promocodes-referral-deals-2026-04-10]] — 2026-04-10 | 12 docs from raw/ | 3 pages created, 2 updated
- [[акции-subsystem-2026-04-10]] — 2026-04-10 | 5 Акции docs from raw/ | 4 pages created
- [[lrs-docs-2026-04-10]] — 2026-04-10 | 4 LRS docs from raw/ | 1 page created
- [[loyalty-sale-profiles-2026-04-10]] — 2026-04-10 | 4 docs: loyalty-on-sale + profiles service | 2 pages created
- [[loyalty-desktop-broker-migration-2026-04-10]] — 2026-04-10 | 3 docs: project + TZ + WIP notes | 1 page created
- [[franchise-api-2026-04-10]] — 2026-04-10 | franchise contract API docs
- [[franchise-loyalty-2026-04-10]] — 2026-04-10 | franchise loyalty system docs
- [[franchise-sabynet-2026-04-10]] — 2026-04-10 | franchise SabyNet subsystem docs
- [[loyalty-franchise-algorithms-2026-04-10]] — 2026-04-10 | franchise loyalty algorithms
- [[loyalty-db-franchise-2026-04-10]] — 2026-04-10 | loyalty DB franchise schema docs
- [[sync-broker-deep-dive-2026-04-10]] — 2026-04-10 | sync broker deep-dive docs
- [[report-prefetch-conceptual-2026-04-13]] — 2026-04-13 | report-prefetch conceptual overview
- [[report-prefetch-db-schema-2026-04-13]] — 2026-04-13 | report-prefetch DB schema
- [[report-prefetch-service-2026-04-13]] — 2026-04-13 | report-prefetch service internals
- [[report-prefetch-subsystems-2026-04-13]] — 2026-04-13 | report-prefetch subsystems
- [[saby-naming-guide-2026-04-12]] — 2026-04-12 | official Saby product naming rules
- [[saby-products-lineup-2026-04-12]] — 2026-04-12 | full Saby product catalog
- [[tensor-techdoc-standards-2026-04-12]] — 2026-04-12 | Tensor tech doc standards
- [[wasaby-infra-2026-04-12]] — 2026-04-12 | Wasaby infrastructure docs
- [[tests-new-readme-2026-04-11]] — 2026-04-11 | test framework README
- [[zvonok-offer-bug-zlateks-2026-04-13]] — 2026-04-13 | Zlateks offer bug investigation
- [[zvonok-zlateks-followup-2026-04-14]] — 2026-04-14 | Zlateks follow-up analysis
- [[linter-project-2026-05-18]] — 2026-05-18 | SonarQube+СТАН linter project docs
- [[sabyget-docs-2026-05-18]] — 2026-05-18 | 10 docs: SabyGet product + subsystems + data architecture | 3 pages created
- [[sbis-access-request-2026-05-19]] — 2026-05-19 | 2 docs: API запросов доступа + Поддержка | 1 page created
- [[saby-api-docs-2026-05-21]] — 2026-05-21 | Saby API Docs: аутентификация и задачи (СБИС.СписокЗадач, error codes)
- [[sbis-api-sbis-mcp-2026-05-21]] — 2026-05-21 | SBIS API reference для sbis-mcp: методы, форматы, протокол
- [[sbis-jsonrpc-protocol-format]] — формат протокола JSON-RPC (wasaby.Backend)
- [[saby-api-docs-objects-2026-05-21]] — 2026-05-21 | 6 docs: Документ + Навигация + протокол + типы данных + строки | 3 pages created
- [[wasaby-sharedfuture-2026-05-22]] — 2026-05-22 | параллельные удалённые запросы: Shared Future, FutureInvoke, ParallelTasks
- [[sveshnikov-stub-creation-thoughts-2026-05-28]] — 2026-05-28 | мысли Свешникова: создание корешков и реферальные сценарии
- [[wasaby-cross-client-call-2026-06-04]] — 2026-06-04 | Форум wasaby.Backend: вызов БЛ-метода под другим клиентом+юзером без петли; AuthByClientAndUserId vs CreateMultitenantEndpointByClientId | 1 page created, 1 updated
- [[wasaby-bl-call-loop-user-switch-2026-06-04]] — 2026-06-04 | SBIS Forum: петля вызовов при смене пользователя, одном ClientID; CreateMultitenantEndpointByClientId как решение | 1 page created
- [[sbis-plan-june-2026]] — 2026-06-09 | SBIS план работ «Система лояльности» июнь 2026: 19 пунктов, 37.3ч; SabyBank RKO Referral, корешки, DWC внедрение, удаление фич | 1 page created
- [[wasaby-bl-async-invoke-2026-06-11]] — 2026-06-11 | Sync/async BL call API: EndPoint, Invoke/AsyncInvoke, delivery guarantees, callbacks, Huge Payload | 1 page created

---

## Questions

- [[How does the LLM Wiki pattern work]] — how the pattern works and why it outperforms RAG at human scale (status: developing)

---

## Comparisons

- [[Wiki vs RAG]] — when to use a wiki knowledge base versus RAG; verdict: wiki wins at <1000 pages
- [[claude-obsidian-ecosystem]] — feature matrix of 16+ Claude+Obsidian projects; where claude-obsidian wins and gaps

---

## Indexes

- [[concepts/_index]] — all concept pages by domain
- [[entities/_index]] — all entity pages
- [[sources/_index]] — all ingested sources

## Domains

- [[domains/price-formation/_index]] — loyalty and price formation system for SBIS/Saby platform; Wasaby backend, referral programs, sync

---

## Folds

- [[fold-k4-from-2026-05-21-to-2026-06-05-n16]] — k4 fold of 16 entries (2026-05-21 to 2026-06-05): ReferralProgram stub BL, Wasaby multitenancy, DWC Card migration, org structure
- [[fold-k4-from-2026-04-13-to-2026-05-18-n16]] — k4 fold of 16 entries (2026-04-13 to 2026-05-18): DWC migration, bug fixes, Wasaby/linter ingests
- [[fold-k3-from-2026-04-23-to-2026-04-24-n8]] — k3 fold of 8 entries (2026-04-23 to 2026-04-24)

---

## Canvases

- [[main]] — main vault canvas overview
- [[welcome]] — getting started visual guide
- [[youtube-explainer]] — visual explainer for presentations
- [[claude-obsidian-presentation]] — presentation canvas (standalone)
