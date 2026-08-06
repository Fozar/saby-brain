---
type: domain-index
title: "Price Formation (SBIS/Saby)"
updated: 2026-04-10
tags:
  - domain
  - price-formation
  - sbis
  - wasaby
status: current
related:
  - "[[Wasaby-Framework]]"
  - "[[Multitenancy-Architecture]]"
  - "[[ReferralProgram-Module]]"
  - "[[DWC-Distributed-Workflow-Coordinator]]"
  - "[[Sync-Broker]]"
  - "[[Python-Code-Standards-SBIS]]"
  - "[[Python-Localization-rk]]"
  - "[[Loyalty-Database-Schema]]"
  - "[[Loyalty-Product-Overview]]"
  - "[[Loyalty-Cloud-Config]]"
  - "[[Loyalty-Public-API]]"
  - "[[Loyalty-UI-Components]]"
  - "[[Loyalty-In-Products]]"
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[DiscountCard-Service-API]]"
  - "[[DiscountCard-Algorithms-Processes]]"
  - "[[DiscountCard-UI-Specifics]]"
  - "[[PassUpdater-Service]]"
  - "[[DiscountCard-Diagnostic-Service]]"
  - "[[DiscountCard-Admin-Ops]]"
  - "[[Promocode-Subsystem-Overview]]"
  - "[[Promocode-Info-Model]]"
  - "[[ReferralDeals-System]]"
  - "[[SabyBank-RKO-Referral]]"
  - "[[RecruitmentReferral-Project]]"
  - "[[Franchise-Contract-API]]"
  - "[[Franchise-SabyNet-Subsystem]]"
  - "[[Franchise-Loyalty-Architecture]]"
  - "[[Franchise-Loyalty-System]]"
---

# Price Formation (SBIS/Saby) Domain

Loyalty and price formation system for the SBIS (Saby) platform. Manages discount programs, bonus systems, promotions, and pricing for online and retail/warehouse environments.

**Repo:** `price-formation` | **Branch pattern:** `rc-26.XXXX`

---

## Sub-domains

- **Online pricing** (`PriceFormation.Online`) - e-commerce pricing, referral programs
- **Offline/retail pricing** (`PriceFormation.Offline`) - warehouse/POS pricing
- **Common logic** (`PriceFormation.Common`) - shared business logic
- **DCCommon** - bonus balance, barcode, encryption, stand management

---

## Key Concepts

- [[PriceFormation-Backend-Architecture]] - полная карта Python-модулей: Common/Online/Offline/DCCommon; субпакеты, Wasaby-артефакты, паттерны
- [[Wasaby-Framework]] - platform architecture (s3cld/s3srv/s3mod, JSON-RPC, resource types)
- [[Multitenancy-Architecture]] - 1 client = 1 schema isolation model
- [[DWC-Distributed-Workflow-Coordinator]] - async complex scenario execution
- [[Sync-Broker]] - offline-cloud synchronization broker
- [[Python-Code-Standards-SBIS]] - PEP-8 + Wasaby-specific naming rules
- [[Python-Localization-rk]] - `rk()` function for string localization
- [[Loyalty-Database-Schema]] - DB tables: ВидЦены, Карта, ВидЦеныДокумент; promo code model
- [[Loyalty-Product-Overview]] - product goals, core entities (Акция, ДК, Промокод), subsystems
- [[Loyalty-Cloud-Config]] - DCService cloud params, anti-bot, scheduler tasks
- [[Loyalty-Public-API]] - Card, Promocode, SalePoint, Pass API; barcode types; Google Pay URL fix
- [[Loyalty-UI-Components]] - frontend component library: widgets, sale UI, conditions, charts
- [[Loyalty-In-Products]] - feature matrix per product; offline limitations; product owners
- [[DiscountCard-Subsystem-Overview]] - ДК types (personal/electronic/stored), СДК 5-part architecture, integrations
- [[DiscountCard-Service-API]] - Card.* and CardTemplate.* user + admin API; error codes
- [[DiscountCard-Algorithms-Processes]] - external access rights, confidential data handling, service interaction diagrams
- [[DiscountCard-UI-Specifics]] - card type registry UI, data loading patterns, master-detail
- [[PassUpdater-Service]] - Task/Request/MessageBox model; AW vs GPay processing; scheduler tasks
- [[DiscountCard-Diagnostic-Service]] - admin panel, promo concierge, DB indexes
- [[DiscountCard-Admin-Ops]] - inside.sbis.ru + ClickHouse monitoring; auto-update triggers; AW/GPay setup
- [[Promocode-Subsystem-Overview]] - 4 types (Общий/Индивидуальный/Партнёрский/ЗаАктивность); technically = ДК; SabyGet/profiles/DCService integration
- [[Promocode-Info-Model]] - PromoCode object hierarchy; 14 ConditionData fields; NumberFormat; PromoCodeEmission
- [[ReferralDeals-System]] - Owner/Partner deal referral; sabyReferralProgram.CreateLead; rewards=bonuses; 10 DB queries; 3 SabyNet widgets
- [[ReferralProgram-Part2-Project]] - проект «Реферальная программа (2 часть)»: ЛК Владельца/Партнёра в SabyNet, 10 спринтов; первоисточник перехода статистики на корешки `ВидЦеныДокумент`
- [[ReferralProgram-Folders-Priority-Sprint]] - спринт №2: папки офферов (`ВидЦены.Раздел`), `ReferralProgram.Move`, `IsJoined`, статистика в `GetList`, курсорная навигация заявок
- [[ReferralProgram-ContractorCard-Programs-Tab]] - спринт №3: `GetListByContractor`, `ContractorHasPrograms`, встраивание в `Контрагент.CRMNavigationPreload`
- [[ReferralProgram-SelfJoin]] - самостоятельное присоединение партнёра через `saby.ru/referral`, страница `/accept`, авто-акцепт приглашения, заявка «Агенты Saby»
- [[ReferralProgram-Offer-Visibility]] - доступность офферов «Всем кроме» + папки партнёров (`ВидЦеныРасширение.ТипПредоставления`)
- [[ReferralProgram-Leads-Section]] / [[ReferralProgram-SabyNet-Widgets-Redesign]] / [[ReferralProgram-Offer-Topics]] / [[ReferralProgram-SabyNet-Offer-Contract]] - разделы «Лиды», виджеты разводящей, темы офферов, «Оферта SabyNet»
- [[Franchise-Contract-API]] - 12 external `FranchiseContract.*` methods: lifecycle handlers (OnAccept/OnRestore/OnTerminate), operator CRUD, PointSalesList, AccessData
- [[Franchise-SabyNet-Subsystem]] - Saby Net franchise configuration: custom regulation (reduced fields), operator workflow, no KPI, shared bonus programs/акции across multi-account networks
- [[Franchise-Loyalty-Architecture]] - DB schema changes for franchise loyalty: FranchiseRole/FranchiseUUIDList on ВидЦены/ВидКарты/CardType; Operation.CardUUID+PriceEntityUUID in СДК
- [[Franchise-Loyalty-System]] - business overview: Owner/Participant model, sync mechanism (full-overwrite by UUID), unified customer base via Owner account, СДК as shared balance store

---

## Customer Journey / Маршруты (Путь клиента)

Новый движок маркетинговой автоматизации / customer journey orchestration («Маршруты»), строится поверх существующей системы лояльности: визуальный конструктор триггерных сценариев (реактивация, брошенная корзина, день рождения, приветственный бонус) с условиями, ожиданием и действиями. Источник — 17 PDF из `.raw/Путь клиента/`, ингестированных 2026-07-03 шестью параллельными агентами; страницы ниже — результат дедуп-прохода оркестратора (см. [[CustomerJourney-Scenarios-Project]] за детали слияния).

- [[CustomerJourney-Scenarios-Project]] — канонический обзор проекта (из **согласованного** `Техническое задание.pdf`): цели, аудитория (~670 Presto-аккаунтов), 4 подсистемы-владельца, понятийная модель, лицензирование (полный тариф)
- [[Route-Platform-Architecture]] — канонической архитектура Платформы Маршрутов: `RouteService.StartTrace/OnEvent`, `Route.Start/Stop/Status`, sequence-диаграммы запуска и авто-проходчика, модель Route/Trace/Events, DWC-пачки по 1000 клиентов, глобальная предфильтрация, 3-party ownership (Лояльность/Маршруты/Выборки)
- [[Trigger-System-Contract]] — Система триггеров: JSON-контракт (`triggers-data`/`base/actions`), каталог событий по приоритетам (1-3), каталог действий, `layout.Card`/`Trigger.Notify`
- [[CustomerJourney-UI-Decomposition]] — UI: реестр (мастер-деталь), карточка сценария (5 вкладок), карточка прохода, компоненты `Route/ScriptPage/*`
- [[CustomerJourney-Scenario-Model]] — понятийная модель + сравнение блоков схемы vs Mindbox/[[REES46]] + UI реестра/карточки сценария (из `Концептуальное решение 1-3.pdf` + `Блоки для сценариев лояльности.pdf`)
- [[CustomerJourney-Scenario-Builder]] — механика конструктора: типы узлов, race-паттерн ожидания, полные таблицы фильтров/действий/событий
- [[CustomerJourney-Scenario-Catalog]] — каталог 34 примеров сценариев в 8 категориях, разбор 9 диаграмм
- [[CustomerJourney-Installation-Chains]] — черновой список категорий предустановленных уведомительных цепочек
- [[LoyaltyScenario-ReactivationInactiveClients]] — канонический пример сценария «Давно не покупали»: 30-дневная неактивность → 100 бонусов + email → ожидание 10 дней → thank-you email; открытые вопросы ревью Морозова
- [[AbandonedCart-Loyalty-Scenario]] — сценарий «Брошенная корзина»: условия, события, UX-анализ момента авторизации; уже существует как шаблон по умолчанию
- [[TriggerScenario-ConditionsActions-Reference]] — справочник условий/событий сценарного конструктора (снят с Mindbox, использован как эталон)
- [[CustomerJourney-Events-Actions-Catalog]] — целевой (не-Mindbox) каталог событий/действий MVP, из `События-действия для сценариев лояльности.sabydoc.pdf`
- [[CustomerJourney-WorkPlan]] — план работ 515 чд (этапы 1.1–2.5 + технологические), из `План работ по проекту.pdf`
- [[CustomerJourney-Route-Service-API]] — ранний вариант Сервиса Маршрутов backend (`Route.*`, `AutoTrace.*`) из планового документа — методы переименованы в финальном ТЗ, см. [[Route-Platform-Architecture]] (`RouteService.*`)
- [[CustomerJourney-Test-Plan]] — план тестирования, период 01.08–28.11.2026
- [[Saby-Scheme-Constructors]] — реестр 12 конструкторов схем Saby; «Путь клиента» — конструктор №12
- [[Выборки-Module]] — модуль сегментации аудитории (владелец [[Гаврилов-Михаил]])

> [!key-insight] Разрешённое противоречие: «раннее исследование» vs «уже существует» — это один и тот же мокап, увиденный на разных стадиях
> Несколько черновиков батча (Mindbox-бенчмарк, ранний open-questions документ) читались как описание independent research-стадии, тогда как другой документ (ревью Морозова, скриншоты с демо-статистикой «8276 проходов») выглядел как описание уже эксплуатируемой в проде системы. После сведения всех 17 источников: это **один и тот же новый продукт** («Путь клиента» / «Сценарии лояльности» / Маршруты), задокументированный на разных стадиях проектирования — от конкурентного бенчмарка и открытых архитектурных вопросов до высокоточных мокапов с демо-данными и, наконец, согласованного ТЗ с sequence-диаграммами. Скриншоты с «демо-статистикой» — это мокапы с плейсхолдер-данными для дизайн-ревью, а не живой прод. Открытый вопрос про «сотни тысяч покупателей по тысячам маршрутов в аккаунтах online» (из `Концептуальное решение.pdf`) о масштабировании остаётся нерешённым на момент ТЗ.
>
> Также разрешено расхождение имён методов: [[CustomerJourney-Route-Service-API]] (`AutoTrace.Start/Run/OnEvent`, из планового `План работ по проекту.pdf`) — черновая нотация раннего этапа планирования; финальное согласованное ТЗ ([[Route-Platform-Architecture]]) фиксирует `RouteService.StartTrace/StartClientRoute/OnEvent` — это переименование между стадиями, а не два разных API.

---

## Common Infrastructure

- [[CursorNavigation-Mechanism]] — курсорная пагинация: `NavField`, `NavigationParams`, `get_list_by_cursor`, `get_nav_expressions`, `add_cursor_params`; варианты `List[NavField]` (современный) и `str` (устаревший); поддержка ndFORWARD/ndBACKWARD/ndBOTHWAYS

---

## Platform Caching

- [[Report-Prefetch-Service]] — платформенный кэш отчётов (`report-prefetch-service`): Prefetch.List/Data/AppendBatch; микросессии; иерархия (уровни, разворот, мультинавигация); сортировка + индексы; поиск; суммирование PrefetchSelection
- [[ReportPrefetch-DB-Schema]] — схема БД: 6 таблиц (SessionId/StoredReport/ReportPage/ReportData/Method/ShardsAmountHistory); 5 типовых выборок; таблица индексов

---

## Testing

- [[PriceFormation-Test-Framework]] — три проекта (Desktop/Online/OnlineWithDiscountCore), `test_manager.py`, cmake/ninja, PyCharm-конфигурации, мок методов/таблиц через `TestLoyalty.orx`/`.dicx`, `@enable_features`, `@with_feature`, `@test_new_skip`

---

## Key Entities

- [[ReferralProgram-Module]] - partner referral system with leads, stats, invoices

---

## Sources Ingested

- [[price-formation-docs-2026-04-10]] - 12 docs from `docs/` folder (2026-04-10)
- [[loyalty-knowledge-base-2026-04-10]] - 6 docs from `raw/` (loyalty DB, product, API, UI, cloud) (2026-04-10)
- [[discount-cards-batch-2026-04-10]] - 10 docs from `raw/` (СДК subsystem: description, API, algorithms, UI, pass-updater, diagnostic, admin ops) (2026-04-10)
- [[promocodes-referral-deals-2026-04-10]] - 12 docs from `raw/` (Промокоды + Реферальная система сделок) (2026-04-10)
- [[franchise-api-2026-04-10]] - 1 doc from `raw/` (FranchiseContract API, 12 methods) (2026-04-10)
- [[franchise-sabynet-2026-04-10]] - 1 doc from `raw/` (Франшиза subsystem description: config, regulation, KPI, shared loyalty) (2026-04-10)
- [[loyalty-db-franchise-2026-04-10]] - 1 doc from `raw/` (loyalty DB schema changes for franchise: ВидЦеныЛица, ВидЦеныРасширение, ВидЦены, ВидКарты, CardType, Operation) (2026-04-10)
- [[franchise-loyalty-2026-04-10]] - 1 doc from `raw/` (Описание: franchise loyalty business overview, sync mechanism, unified customer base) (2026-04-10)
- [[report-prefetch-service-2026-04-13]] - 1 doc from `raw/` (Платформенный механизм кэширования отчётов: Prefetch.List/Data/AppendBatch, микросессии, иерархия, сортировка+индексы, поиск, суммирование) (2026-04-13)
- [[report-prefetch-db-schema-2026-04-13]] - 1 doc from `raw/` (Схема базы данных: SessionId/StoredReport/ReportPage/ReportData/Method/ShardsAmountHistory, 5 выборок, индексы) (2026-04-13)
- [[put-klienta-abandoned-cart-2026-07-03]] - 1 doc from `.raw/Путь клиента/` (сценарий «Брошенная корзина», бенчмарк Mindbox) (2026-07-03)
- [[put-klienta-conditions-actions-2026-07-03]] - 1 doc from `.raw/Путь клиента/` (справочник условий/событий сценарного конструктора Mindbox) (2026-07-03)
- [[loyalty-scenario-reactivation-inactive-v1-2026-07-03]] - 1 doc from `.raw/Путь клиента/` (сценарий «Реактивация неактивных клиентов (давно не покупали)», v1; Маршруты/Выборки ownership questions) (2026-07-03)
- [[customer-journey-tz-2026-07-03]] - 1 PDF (51 стр.) из `.raw/Путь клиента/` — согласованное ТЗ проекта «Путь клиента»: цели, Платформа Маршрутов, Система триггеров, UI-декомпозиция (2026-07-03)
- [[put-klienta-koncept-reshenie-1-2026-07-03]], [[put-klienta-koncept-reshenie-2-mindbox-2026-07-03]], [[put-klienta-koncept-reshenie-3-voprosy-2026-07-03]] - 3 PDF из `.raw/Путь клиента/` — итерации концептуального решения (понятийная модель, UI-мокапы реестра/карточки сценария) (2026-07-03)
- [[put-klienta-bloki-scenariev-2026-07-03]] - 1 PDF из `.raw/Путь клиента/` — типы блоков схемы vs Mindbox/REES46 (2026-07-03)
- [[put-klienta-konstruktory-shem-deev-2026-07-03]] - 1 PDF из `.raw/Путь клиента/` — реестр 12 конструкторов схем Saby (2026-07-03)
- [[put-klienta-plan-rabot-2026-07-03]] - 1 PDF из `.raw/Путь клиента/` — план работ 515 чд (2026-07-03)
- [[put-klienta-plan-testirovaniya-2026-07-03]] - 1 PDF из `.raw/Путь клиента/` — план тестирования (2026-07-03)
- [[put-klienta-sobytiya-deystviya-2026-07-03]] - 1 PDF из `.raw/Путь клиента/` — целевой каталог событий/действий MVP (2026-07-03)
- [[put-klienta-sravnenie-konkurentami-shablon-2026-07-03]], [[put-klienta-ekspluatatsiya-shablon-2026-07-03]] - 2 PDF из `.raw/Путь клиента/` — незаполненные корпоративные шаблоны, без проектного контента (2026-07-03)
