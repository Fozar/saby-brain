---
type: meta
title: "Hot Cache"
updated: 2026-06-12
tags:
  - meta
  - hot-cache
status: evergreen
related:
  - "[[index]]"
  - "[[log]]"
  - "[[overview]]"
---

# Recent Context

## 2026-06-14 — Batch ingest: wasaby.Backend (2 новые страницы, c-000132..133)

| Страница | Адрес | Тема |
|---|---|---|
| [[Wasaby-HTML-Converter]] | c-000132 | HTML→PDF (PdfConverter.*), URL→PNG (ImageConverter.*), delayed print |
| [[Wasaby-Informers]] | c-000133 | Redis-счётчики/информеры, Counters.Set, восстановление 100мс |

**Важно**: `delayedPrint=true` → JS должен вызывать `window.tensor.waitPrint()` каждые ≤5с + `startPrint()` по готовности; иначе конвертация прервётся через 30с.

## 2026-06-14 — Batch ingest: wasaby.Backend (8 новых страниц, c-000124..131)

| Страница | Адрес | Тема |
|---|---|---|
| [[Wasaby-Memray]] | c-000124 | Профилировщик памяти Python (Bloomberg): memray_script.sh record/flamegraph |
| [[Wasaby-Perforator]] | c-000125 | Профилировщик CPU (Яндекс): RHEL9+, perforator_script.py, UI perforator.sbis.ru |
| [[Wasaby-Python-Debug]] | c-000126 | VSCode (sbis_root) + PyCharm Remote Debug pydevd-pycharm (≤2022.3.3) |
| [[Wasaby-History-Service]] | c-000127 | HistoryMsg/HistoryMsgSet, История.History_Common_Object, 3 года хранения |
| [[Wasaby-MQ]] | c-000128 | RabbitMQ шины: серверные события + AsyncInvoke, sbis-msg-broker, Huge Payload |
| [[Wasaby-Request-Broker]] | c-000129 | Async-вызовы с гарантией + статусом (для DWC/Scheduler) vs RabbitMQ fire-and-forget |
| [[Wasaby-Scheduler]] | c-000130 | Планировщик задач: расписание через Genie/Управление облаком, итеративные задачи |
| [[Wasaby-Report-Prefetch]] | c-000131 | Кэш отчётов: Prefetch.List, PrefetchPages (50/500), PrefetchPreSort обязателен |

**Важно**:
- `PyCharm` для отладки: максимальная версия **2022.3.3** (нет лицензий JetBrains для новых)
- `Prefetch.List`: **PrefetchPreSort обязателен** для иерархических отчётов (платформенное требование)
- `request-broker` vs RabbitMQ: request-broker = гарантия доставки + статус запроса; RabbitMQ = скорость (fire-and-forget)
- Huge Payload Protocol: >100KB AsyncInvoke → автоматически через file-transfer (с платформы 3.18.150+)

## 2026-06-14 — Batch ingest: wasaby.Backend (ещё 8 страниц, c-000116..123)

| Страница | Адрес | Тема |
|---|---|---|
| [[Wasaby-Service-Node-Architecture]] | c-000116 | Монитор/координатор/рабочий процесс, QoS (mem/timeout/tx/hang) |
| [[Wasaby-i18n]] | c-000117 | rk() Python/C++, словари @@/plural#, локаль lang-COUNTRY |
| [[Wasaby-Third-Party-Libraries]] | c-000118 | pip-repo + s3mod (Python); Conan + CMake (C++) |
| [[Wasaby-Parameters-Service]] | c-000119 | scopes: GLOBAL/USER/ACCOUNT/DEVICE; Parameter.Read/Set; ConfigLoader |
| [[Wasaby-Distributed-Locks]] | c-000120 | ReadLock/WriteLock, Acquire/TryAcquire, DetachedRef; ключ без account! |
| [[Wasaby-ClickHouse]] | c-000121 | OLAP: GetConnectedDatabase, TableCopier.AddRecord/Flush, ALTER ON CLUSTER |
| [[Wasaby-FTS]] | c-000122 | Elasticsearch: sbis_fts.Object, Upsert/List/Aggregation, highlight |
| [[Wasaby-File-Transfer]] | c-000123 | FileTransferUpload/Download/Delete, хранилища excel/huge_payload_storage |

**Важно**:
- `distributed-locks`: ResourceId не содержит account/user — добавлять самому в multitenant-системах
- `ClickHouse`: INSERT через SqlQuery — запрещён, только TableCopier; альтернативный EscapeIdentifier/EscapeLiteral
- `file-transfer`: файл живёт до таймаута (не удаляется после первого скачивания); limit имени — 512 символов



| Страница | Адрес | Тема |
|---|---|---|
| [[Wasaby-Service-Node-Architecture]] | c-000116 | Монитор/координатор/рабочий процесс, QoS (mem/timeout/tx/hang) |
| [[Wasaby-i18n]] | c-000117 | rk() Python/C++, словари @@/plural#, локаль lang-COUNTRY |
| [[Wasaby-Third-Party-Libraries]] | c-000118 | pip-repo + s3mod (Python); Conan + CMake (C++) |
| [[Wasaby-Parameters-Service]] | c-000119 | scopes: GLOBAL/USER/ACCOUNT/DEVICE; Parameter.Read/Set; ConfigLoader |
| [[Wasaby-Distributed-Locks]] | c-000120 | ReadLock/WriteLock, Acquire/TryAcquire, DetachedRef; ключ без account! |

**Важно для distributed-locks**: `ResourceId` не включает account/user автоматически — в мультитенантных системах нужно добавить их в `resource_key` самостоятельно.

**Конфигурация рабочих процессов**: формула памяти `limit = (RAM - 0.5) * 0.8 * 1024 / (workers + 1)`. QoS автоматически перезапускает процессы при утечках транзакций (немедленно, аварийно), превышении памяти (graceful) или зависании (ping timeout 2 мин).

## 2026-06-14 — Batch ingest: wasaby.Backend (11 новых страниц, c-000105..115)

**Создано 11 wiki-страниц** из `.raw/wasaby.Backend/`:

| Страница | Адрес | Тема |
|---|---|---|
| [[Wasaby-Dev-Standards]] | c-000105 | Обзор стандартов разработки |
| [[Wasaby-SQL-Standard]] | c-000106 | SQL: PascalCase, 3-пробела, именование |
| [[Wasaby-Python-Standard]] | c-000107 | Python: PEP-8+120 символов, code review score |
| [[Wasaby-Cpp-String-Standard]] | c-000108 | C++: StringView/String/StackString |
| [[Wasaby-Service-Framework]] | c-000109 | Архитектура сервисного фреймворка |
| [[Wasaby-BL-Calls]] | c-000110 | Sync/Async/Remote вызов БЛ, auth политики |
| [[Wasaby-BL-Objects]] | c-000111 | Иерархия объектов, типы методов |
| [[Wasaby-Unit-Testing]] | c-000112 | test_framework, pytest, mock_service |
| [[Wasaby-SQL-DBA]] | c-000113 | Дайджест Habr-статей + explain.tensor.ru |
| [[Wasaby-Long-Running-Operations]] | c-000114 | LRS: WorkflowBuilder, прогресс, ResultLink |
| [[Wasaby-Task-Queue]] | c-000115 | plugin-task-queue: Task.Create/Processing |

**Важно**: файлы SQL/DBA — это Habr-дайджесты, не внутренняя доки.
**sabydoc-extract.py** — скрипт для чтения .sabydoc (ZIP с index.site JSON).

## 2026-06-13 — ВНР сбора данных: sbis.Record API + паттерн статистики

Обновлён [[Wasaby-Scripts]] (c-000091): добавлены правильные методы `sbis.Record` (`AddInt64`/`AddInt32`/`AddString`/`AddBool` — не `AddInteger`!) и паттерн скрипта сбора статистики с `LogRedis`.

**Конкретный пример** (поручение №06035683, баг №04228789): скрипт считает безымянные ДК (`Карта.Лицо IS NULL`) на боевых аккаунтах, чтобы оценить масштаб бага «продажи по анонимной карте не попадают в виджет бонусов».

**Фильтры запроса**: `ТипКарты = 0` (только ДК, не промокоды), `Эмиссия IS NOT NULL` (без персональных счетов), `Лицо IS NULL` = не привязана к физику.

## 2026-06-12 — Инжест: Async/Sync BL вызовы в облаке (сессия 7)

**Создана страница** [[Wasaby-BL-Async-Sync-Cloud-Calls]] (c-000105).

**Ключевые API:**
- Локальный вызов: `BLObject('Obj').Invoke('M', ...)` / `BLObject('Obj').AsyncInvoke('M', ...)`
- Удалённый: `BLObject('Obj', EndPoint('svc')).Invoke(...)` — `EndPoint` обязателен
- Новый стиль: `EndPoint('svc').MyObj.MyMethod(param1, param2)`
- Auth в EndPoint: `AuthByClientID`, `AuthByExtID`, `AuthByUserID`, `AuthByLogin`

**Приоритеты:**
- Все `AsyncInvoke` → всегда `rpLOW` (служебный пул), нельзя изменить
- `ep.SetAsyncPriority(0-9)` — позиция в очереди брокера (по умолчанию 2; если `SetPriority(rpNORMAL)` то = 5)
- Читать внутри метода: `Session.GetHeader("X-AsyncPriority")` (None для sync, строка для async)

**Гарантированная доставка:**
- AMQP (по умолчанию, RabbitMQ) или RBC: `ep.SetTransportProtocol('Async Request Broker', sbis.InteractionKind.AsyncInvokeWithGuarantee)`
- `ep.SetRepeatCnt(N)` — число повторов при ошибке
- **Лимит тела: 100 КБ** (100 КБ–1 МБ = warning, >1 МБ = запрещено)

**HugePayload Protocol** (для данных >100 КБ):
```python
import hugepayload
e = EndPoint('service_name')
e.SetProtocol(hugepayload.GetHugePayloadRpcProtocol())
BLObject('object', e).AsyncInvoke('method', big_data)
```

**Специализированный брокер:**
```python
rbc_settings = sbisrequestbrokerclient.RbcTransportProtocolSettings()
rbc_settings.BrokerName = 'custom_broker_name'
rbc_settings.HighDeliveryGuarantee = True
ep.SetTransportProtocol(rbc_settings, sbis.InteractionKind.AsyncInvokeWithGuarantee)
```
Подписка в `OnEndAllLoadModules`: `sbisrequestbrokerclient.AddBrokerToListen('custom_broker_name')`

**Callbacks:**
```python
obj.AsyncInvoke('M', p, callbacks=('Obj.OnSuccess', 'Obj.OnError', '{"id":42}'))
```
- Параметры обработчика: `(Метод, Параметры, Результат/Ошибка)`. В `Метод.request_uuid` — ID запроса, в `Метод.context` — переданный контекст.

**Очереди брокера:** `{UUID_Облака}.{ИдГруппыСерверов}` / ошибки: `#error` / отложенные: `#delay{время}`

**Источники .raw/ завершены** (все 3 md-файла в корне `.raw/` проверены и покрыты):
- `Синхронный и асинхронный вызов метода БЛ в облаке.md` → c-000105 (создан)
- `Скрипты.md` → уже в Wasaby-Scripts
- `Как разрабатывать в RetailPresto-offline 2025.md` + диалог о подмене → c-000074 (уже comprehensive)

**Полный ingest всех .raw/ источников завершён.**

## 2026-06-12 — Инжест: Система обновлений — финальная сессия (сессия 6)

Завершён полный ingest всех developer-релевантных PDF из `.raw/Система обновлений/`.

**Добавлено в** [[UpdateSystem-ReleasePlans]] (c-000083):
- Задачи планировщика: `WorkRunAllWaitingWorks` (раз в 30 сек), `PlanMassRecalcDivergence` (3 раза/день), `PlanClearArchivedPlans` + `PlanClearOldActiveTaskStatus` (ежедневно в 03:00)
- **CloudWorkStatus population**: по умолчанию True; если приложение отсутствует в облаке → False; если ВНР снял флаг для региона → False; связи на пропущенные работы игнорируются (транзитивность не работает)
- **Автономные планы**: клонирование (структура идентична, без настроек/статусов другого облака) + синхронизация кнопкой
- `feature-ctrl.FeatureCommit(feature_id)` — API вызов для работы «Включение нового функционала»
- Кластеры: запуск только на уровне папок, волна = max волна среди точек доступа
- Реестр работ: иерархия (тип работы → версия), при создании обязательна Дата → план ищется/создаётся автоматически

**Добавлено в** [[UpdateSystem-DistributionStorage]] (c-000078):
- Схема БД: 16 таблиц (Продукт, ВерсияПродукта, Модуль, ModuleVersion, ServicePart, Image, ФайлХранилища, DistrClient, SabyPacketDependencies и др.)
- Ключевые индексы: `ФайлХранилища(md)`, `Module(Name,Type,Revision)`, `ModuleVersion(VersionHash,Name,Type) UNIQUE`, `Image(Url)`
- Алгоритм: MD5-дедупликация файлов при загрузке; ref-counting при удалении

**Подтверждены как уже comprehensive** (без изменений): Wasaby-Scripts, UpdateSystem-Patches, UpdateSystem-UpdateTypes, UpdateSystem-MetadataRegistration, UpdateSystem-DBConversion

## 2026-06-12 — Инжест: Система обновлений — продолжение (сессия 5)

Дочитаны все оставшиеся технические PDF из `.raw/Система обновлений/`. Основные страницы уже были comprehensive, добавлены пропущенные детали.

**Обновлено** [[UpdateSystem-VersionControl-TD]] (c-000102):
- `VersionManagerCommandToAgent(Agents: Json, Operation: Json) → Record` — API вызова операций на агентах из Управления облаком. Операции: `bl_reboot | bl_stop | bl_start | bl_invoke | agent_update`
- Серверные события: `versionmanager:agent_operation_changed` (Status, Error), `versionmanager:agent_operation_server_changed` (Host, Port, Directory, DaemonName, Message), `versionmanager:agent_operation_journal_changed`
- C++ классы sbis-update-generic: `AbstractSvcPartsManager`, `ServiceHash`, `ServiceFilesMover`. `FastMove`: rename → при ошибке (разные FS) fallback на copy+remove_all
- Новые типы кластеров: Custom Resources в K8s → Datacenter код → настройки helm → сборка с json-образами `{"helm": {...}, "images": {...}}`
- `modules.json` формат (устаревший): `bl_modules`/`ui_modules`: `{link, revision, version}` — для инкрементального обновления только изменённых модулей

**Обновлено** [[UpdateSystem-DistributionStorage]] (c-000078):
- Зависимости: `DiskClient`, `Workflow Coordinator Client`, `PermissionChecker`
- GIT уточнён: `https://git.sbis.ru/orchestration/admin.git`

**Проверены и уже comprehensive** (не обновлялись): [[UpdateSystem-MetadataRegistration]], [[UpdateSystem-UpdateSabyRu]], [[UpdateSystem-DBConversion]].

## 2026-06-12 — Инжест: Система обновлений — продолжение (сессия 3)

**Новые страницы:**
- [[UpdateSystem-DistributionStorage-DB]] (c-000103) — схема БД хранилища дистрибутивов. Алгоритм загрузки: клиент считает md5 → ищет в `ФайлХранилища(md5)`, при наличии — только ссылка, без повторной загрузки. Удаление: ref-counting, при 0 ссылок → физическое удаление + запрос в filestorage. Уникальность модуля: `Module(Name, Type, Revision)`. Образы: `Image(Url) UNIQUE`. Установленные версии: составной индекс с CASE WHEN Статус=1.

**Обновлённые страницы:**
- [[UpdateSystem-UpdateSabyRu]] (c-000084) — добавлены API master-сервера: `GET /api/sync/{id}` (статус 0–100%), `POST /api/sync/{id}` (установить rate / начать sync / начать очистку с `clear:1`). GIT-репозитории: sbis-update-master/web/balancer/syncer/nginx/shaper (все `git.sbis.ru/ha/`), HELM `git.sbis.ru/ha/charts/sbis-docker-update-balancer`. update.sbis.ru не контролирует целостность файла при передаче.
- [[UpdateSystem-ReleasePlans]] (c-000083) — добавлены: авто-заполнение полей для 7 типов работ, схема БД с индексами, 28 облачных параметров. Ключевые: `Предел нагрузки плана`=100, `ВесБаза данных`=2, `ВесБизнес логика`=1, `ПриложенияПервойВолны`, `Дистрибутивы основного сервиса`=["ext","ext-demo","ext-partners","inside","ca","standard"].

## 2026-06-12 — Инжест: Система обновлений — продолжение (сессия 2)

Глубокий re-ingest: ТД Управления версиями (62 стр), Патчи, компоненты ХД.

**Новые страницы:**
- [[UpdateSystem-Patches]] (c-000101) — патчи UI vs BL: получение ревизии из metainfo, MR на git.sbis.ru, ВНР, zip-архив BL; техническая реализация: копия дистрибутива (по ссылкам), замена только изменённых модулей через `zip`, jinnee для rebuild resources/, нельзя патчить .so/.dll/.dicx/.dpack
- [[UpdateSystem-VersionControl-TD]] (c-000102) — МАО: DAG в БД (Task+TaskRelationship), 12 типов задач (PFT/SPT/RUT/CT/ScriptTask и др.), 7 фаз; скрипты: DeveloperScriptExecuteAll(UpdateID, ClientDatabaseID, VersionManagerService, Guid, Personal, DoneMethods), аварийный RabbitMQ-режим; sbis-update-exec: ServiceFilesMover(FastMove), ServiceHash(MD5); схема БД (Task, ClientDatabase, ScriptMessage, ScriptHistory, ИсторияОперацийПродукта и др.); 6 задач планировщика

**Обновлённые страницы:**
- [[UpdateSystem-MetadataRegistration]] — добавлены API методы, схема БД с индексами, ExtCollector алгоритм, специальный режим при ошибке чтения дерева
- [[UpdateSystem-DistributionStorage]] — saby-package generation (парсер/вычисление версий/версионирование), публикация (heartbeat+callback, PublicHost), загрузка автономными облаками (mIsProtected ссылки, DistrVersion.Copy()/GetFullStructure())

**Ключевой факт:** patch техническая реализация — копия дистрибутива делается по ссылкам мгновенно (не копируются файлы), только изменённые модули скачиваются и переписываются через `zip`.

## 2026-06-12 — Инжест: Система обновлений Saby (80+ PDF)

Массовый инжест документации «Система обновлений» — платформенной подсистемы Saby/SBIS для управления обновлениями ПО. 25 новых страниц (c-000076..c-000100).

**Ключевые новые страницы:**
- [[Хоттабыч-System]] (c-000092) — hub: vm.sbis.ru, фазы обновления, термины, архитектура компонентов
- [[UpdateSystem-UpdateTypes]] (c-000085) — 13 типов обновлений: от лёгкого (zero-downtime) до полного (блокировка); посхемное для tenant-приложений; мастер-реплика
- [[UpdateSystem-MetadataRegistration]] (c-000082) — metadata-registrator: критичная (Prepare/Update/Commit), отложенная (RegisterAtOnce), упрощённая (ExtCollector)
- [[UpdateSystem-DBConversion]] (c-000077) — database-converter: stateless K8s (Redis-only), jinnee-utility, автомасштабирование Pod'ов
- [[UpdateSystem-DistributionStorage]] (c-000078) — хранилище дистрибутивов: saby-пакеты, права, public distribution storage
- [[UpdateSystem-UpdateSabyRu]] (c-000084) — CDN update.sbis.ru: API MASTER/SHAPER/SYNCER; EdgeCenter/CDNNOW; TLS Минцифры
- [[UpdateSystem-ReleasePlans]] (c-000083) — ТД Планы выпуска: release-manager/release-external, 7 типов работ, публичное API (4 метода)

**Ключевой факт (database-converter):** stateless Kubernetes-сервис без собственной БД (только Redis для очереди задач). Автомасштабирование блокирует новые задачи во время scale-down — критическая точка координации при rolling updates.

**Ключевой факт (metadata-registrator):** кэширует метаданные дистрибутива — повторное обновление на ту же версию значительно быстрее даже для других приложений на том же дистрибутиве.

## 2026-06-11 — ТД итеративной загрузки реестров + предложение «Общие решения»

[[Loyalty-IterativeLoading-TD-CommonSolutions]]. Пункт плана 594287653 (поручение 05145004, проект [[Loyalty-React-Migration-Project]]): описать механизм итеративной (порционной) загрузки в Промокодах/ДК/Бонусах/Реферальной.

**Решение (совещание 10.06):** описать **один раз** — мастер в **Бонусы / Алгоритмы и процессы**, из остальных подсистем ссылки + особенности (ДК → Алгоритмы и процессы, Промокоды → API подсистемы Промокоды, Реферальная → API подсистем). Артефакт: `price-formation/docs/loyalty/_ТД Итеративная загрузка/` (мастер-md, 3 ссылочных md, README, 3 drawio-схемы), стиль под PDF БЗ.

**Иерархия на rc-26.4100** (фича `loyalty_it_nav` выпилена, см. [[Feature-Flag-Removal-LOYALTY-IT-NAV]]): не-итеративные базы удалены — `BonusSaleListIterative(IterativeBlockSizeEmaMixin, ListWithCompositeCursor, SaleListWithCursor)`, `ReferralBonusSaleListWithCursorIterative(BonusSaleListIterative)`, `PromoCodeSaleListIterative`, `DiscountCardListWithCursorIterative`. **`Bonus.GetClientListWithStats` отказался от итеративности** → курсорная навигация `get_list_by_cursor`. Концепт [[LoyaltyPrograms-IterativeListLoading]] обновлён заметкой.

**Предложение Федько:** раздел БЗ «Подсистемы Лояльности / Общие решения» под сквозные механизмы (итеративная загрузка, курсорная навигация, обогащение Розница/СУ, конфиденциальность реестров; под вопрос — ВЦД+EffectiveDate, брокер-синхронизация, DWC). Название/расположение — на встрече.

## 2026-06-10 — ReferralProgram: лиды с нулевым вознаграждением не видны в фильтре «Завершено положительно»

[[ReferralProgram-ZeroReward-Lead-Filter-Bug]]. Баг №05265686 (стенд): в РСС лиды с нулевым или незаданным бонусом не отображались при фильтре «Завершено положительно».

**Причина (два места):** (1) `handle_lead_state_changed.py`: условие `if not (price is None or price > 0)` → ранний выход при price=0, ВЦД-запись не создаётся, EffectiveDate не устанавливается. (2) `get_lead_list.py`: `_SQl_GET_COMPLETED_SUCCESS_LEAD_IDS` содержал `AND ptd."Бонусы" > 0` — исключал bonuses=0 и bonuses=NULL. **Фикс:** условие → `if price is not None and price < 0`; убрана строка `AND ptd."Бонусы" > 0` из запроса. EffectiveDate — правильный маркер завершения, Бонусы — нет. Исторические лиды не подтянутся (принято). Ветка `26.4100/bugfix/aatimoshenko/06087022`.

## 2026-06-10 — CardEmission: полная пересинхронизация падала на duplicate key

[[CardEmission-FullResync-PK-Conflict-Fix]]. Баг №06084819 (стенд, фича `lty_broker_sync`): принудительная полная пересинхронизация выпусков карт (`PFSync.CardEmissionReSync`) падала, если часть выпусков уже синхронизирована.

**Причина:** upsert `_sql_upsert_card_emissions` (таблица `ВидКарты`). UPDATE отбирает только строки с `IS DISTINCT` → существующая **неизменённая** запись проходит `Updated IS NULL` и уходит в INSERT → конфликт PK. **Фикс:** `AND NOT EXISTS (SELECT NULL FROM "ВидКарты" WHERE "@ВидКарты" = Data."@ВидКарты")` в CTE Inserted (диагноз+фикс от автора файла Михайленко Е.А.). Регресс-тест `test_resync_unchanged_record`. Ветка `26.4100/bugfix/aatimoshenko/06087022`, также в 3218 (offline).

**Внимание:** правка прод-кода была откачена после внесения (тест остался) — уточнить, нужно ли применить заново.

## 2026-06-10 — Таймаут рассылки промокодов SabyGet: ИСПРАВЛЕНО

[[GetIndividualBatch-AttachPersonId-Timeout-Fix]] закрыт. Баг #04295801: `PromoCode.GetIndividualBatch` синхронно вызывал `CRMClients.AttachPersonId` (~5с/клиент) → таймаут (~300с) при 100+ получателях → статус «Не хватает данных для формирования подстановок».

**Фикс:** привязка персон вынесена в фоновый DWC. Причина отката 08–09.06 — рассинхрон `one_task`: воркфлоу был `one_task="1"`, а код добавлял N задач → `Error` на `Commit`. Теперь `IndividualPromoCodeEmission.AttachPersons` объявлен **`one_task="0"`** (`kind="background"`), задача маппится напрямую на `CRMClients.AttachPersonId`. В `generate.py`: убран ParallelTasks из транзакции, после коммита — `_start_attach_persons_dwc(persons_ids)`. Без чанков, без фича-флага. Тесты 8/8, pylint 10/10.

**Ветка:** `26.3211/bugfix/aatimoshenko/04295801_2` (НЕ rc-26.4100). При переносе конфликт `.dwc`: `Promocode.HandleApply` в rc-26.3211 ещё `kind="user" one_task="1"` — оставлен как есть.

**Урок:** при `one_task="1"` — ОДНА задача со списком + обработчик-цикл; при N задачах — `one_task="0"`.

## 2026-06-11 — Инжест: Offline Dev Setup для Retail/Presto

[[RetailPresto-Offline-Debug-Setup]] (c-000074). Инструкция по подмене BL-модулей в офлайн-приложениях Saby Retail/Presto для отладки.

**Ключевые факты:** С v25.6218 ресурсы предкомпилированы → простая замена файлов не работает. Нужно: (1) удалить MetaMainService из `service/meta/MainService.s3srv`, (2) переключить `sbis-config.ini` → `Модули=meta/RetailCore.s3srv`, (3) очистить `user_data`, (4) при новых файлах — удалить `files.index`/`folders.index`. Только **Debug-версия** (Release: .s3mod скомпилированы в бинарники). Альтернативно: удалить `bl_module_library="meta_main_service"` из `MetaMainService.s3mod`. Пути данных: `C:\ProgramData\Saby Retail` / `C:\ProgramData\Saby Presto`.

## 2026-06-11 — PromoCode: notify SabyGet после привязки персон (DWC)

[[PromoCode-NotifyGenerated-DWC-Ordering]]. Регресс [[GetIndividualBatch-AttachPersonId-Timeout-Fix]]: после выноса `AttachPersonId` в фоновый DWC синхронный notify SabyGet в `generate.py` слал **пустой PersonID** (`ИдентификаторФизЛица` ещё не проставлен).

**Фикс:** уведомление — финальная задача того же DWC-сценария `AttachPersons`. Новый BL-метод `IndividualPromoCodeEmission.NotifyGenerated(PromoCodeIds: INT4[])` (`returns="NONE"`, голый массив, не Record) перечитывает коды из `Карта` и делает `GetClientInfo` в момент выполнения — после привязки. `error_policy` сценария `abort→continue`. Барьер «notify после attach» = DWC, не AsyncInvoke (порядок не гарантирован). `AddTask` без `OpenParallelBlock` исполняется строго последовательно. Чанк notify-задач = 1000 промокодов (payload < 100 КБ). **Распространяется на все типы генерации** (для AUTO привязок нет, но notify тоже через DWC; синхронный `_get_promo_codes_data_for_notify` удаляется). Реализация MAIL проверена (13/13), затем .dwc/тесты откачены в рабочем дереве на шаге расширения на all-types.

## 2026-06-11 — Инжест: Sync/Async вызов метода БЛ

[[Wasaby-BL-AsyncInvoke]] (c-000073). Официальная документация Wasaby по `Invoke`/`AsyncInvoke`.

**Ключевые факты:** `AsyncInvoke` всегда идёт на служебный пул (rpLOW), порядок не гарантирован — цепочка через callbacks. Два типа доставки: HTTP (at-most-once) и AMQP/RBC (at-least-once, с `SetRepeatCnt`). Специализированный RBC-брокер (`SetBrokerName`) для изоляции критичных запросов. Приоритет в очереди брокера: `SetAsyncPriority` 0–9, default 2; 5 = «пользователь ждёт». Лимит тела 100 КБ → Huge Payload Protocol через [[File-Transfer-Service]]. Callbacks принимают `(Метод, Параметры, Результат/Ошибка)` + `КонтекстОперации` (3-й param).

## 2026-06-11 — Генерация промокодов без выгрузки в память: РЕАЛИЗОВАНО

[[PromoCode-Generation-Memory-Optimization]]. Баг #06104810: `IndividualPromoCodeEmission.Generate/1` занимал 5.689с. Три fix'а:

1. **`sql_filter_existing_numbers`** заменила `sql_get_existing_numbers` — батчевая проверка кандидатов через `upper("Номер") = ANY($1::text[])` по индексу `CaseInsensitiveUniqueNumber`. O(chunk·logN) вместо O(все карты).
2. **`_skip_license: bool = False`** в `update()` — устраняет дублирование `License().process_for_sale_point_full()` при внутреннем Python-вызове из `generate()`. Паттерн: внутренний bool-параметр недоступен через БЛ-фреймворк, безопасно для фронта.
3. **Откат `ParallelTasks`** — изменение attach вне транзакции откатили; будет в отдельной задаче.

Ветка `rc-26.4100`, тесты 13/13 ✓.

## 2026-06-09 — Прогресс плана июнь 2026

[[sbis-plan-june-2026]]: 19 пунктов, 37.3ч план / **47.4ч факт**.

**Смержено:** `bonus_it_navigation` (#05144829), `entity_sp` (#05144878), валюта прод-код (#05133949), ReadStub (#05293691). Ветка `05133949_2` (Mock-файлы) ещё не слита.

**Предстоит (SabyBank BL):** #04307161 SetLeadPrice+корешки (2ч), #04307047 GetStubList (1.3ч), #04307067 карточка (1.6ч), #04307081 лиды (1ч), #05216996 источник (1.2ч).

**Открытые вопросы:** GetStubList поля ClientName/City, количество лидов (все vs с вознаграждением), данные карточки заявки, лицензия ДК по компакт-ключу.

---

## Price Formation Domain

SBIS/Saby loyalty + price formation, ветка `rc-26.3211`.
- Wasaby: 3-level (s3cld/s3srv/s3mod), JSON-RPC, declarative resources
- DB: `ВидЦеныДокумент` (события лояльности), `Карта` (ДК/промокод)
- DWC: `workflow2`. Python: 120 chars, CamelCase ok, no wildcard imports

## Active Threads

- **Loyalty Desktop Broker Migration**: [[Loyalty-Desktop-Broker-Migration]] — feature flag `lty_broker_card_type`, ~60д
- **SabyBank RKO Referral**: [[SabyBank-RKO-Referral]] — релиз 18.08.2026

---

Navigation: [[index]] | [[log]] | [[overview]]
