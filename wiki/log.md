---
type: meta
title: "Operation Log"
updated: 2026-06-12
tags:
  - meta
  - log
status: evergreen
related:
  - "[[index]]"
---

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
