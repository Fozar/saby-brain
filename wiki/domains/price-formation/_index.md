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
- [[Franchise-Contract-API]] - 12 external `FranchiseContract.*` methods: lifecycle handlers (OnAccept/OnRestore/OnTerminate), operator CRUD, PointSalesList, AccessData
- [[Franchise-SabyNet-Subsystem]] - Saby Net franchise configuration: custom regulation (reduced fields), operator workflow, no KPI, shared bonus programs/акции across multi-account networks
- [[Franchise-Loyalty-Architecture]] - DB schema changes for franchise loyalty: FranchiseRole/FranchiseUUIDList on ВидЦены/ВидКарты/CardType; Operation.CardUUID+PriceEntityUUID in СДК
- [[Franchise-Loyalty-System]] - business overview: Owner/Participant model, sync mechanism (full-overwrite by UUID), unified customer base via Owner account, СДК as shared balance store

---

## Customer Journey / Marketing Automation (early-stage project)

> [!note] Несколько параллельных umbrella-страниц одного проекта
> Батч источников из папки `.raw/Путь клиента/` ингестировался несколькими параллельными агентами — см. [[CustomerJourney-Scenarios-Project]], [[CustomerJourney-Scenarios-Project]], [[CustomerJourney-Scenarios-Project]], [[Route-Platform-Architecture]] как разные точки входа в один и тот же проект. Не объединены на момент ингеста — требуется дедуп/merge оркестратором.

- [[CustomerJourney-Scenarios-Project]] — «Путь клиента»: ранний проект построения CDP-подобной системы триггерных сценариев лояльности, бенчмарк конкурента [[Mindbox]]
- [[AbandonedCart-Loyalty-Scenario]] — сценарий «Брошенная корзина»: условия, события, UX-анализ момента авторизации
- [[TriggerScenario-ConditionsActions-Reference]] — справочник условий/событий сценарного конструктора (снят с Mindbox)
- [[CustomerJourney-Scenarios-Project]] — умбрелла по `Примеры различных сценариев со схемами.pdf` + `Инсталляционные цепочки.pdf`
- [[CustomerJourney-Scenario-Builder]] — механика конструктора: типы узлов, race-паттерн ожидания, полные таблицы фильтров/действий/событий
- [[CustomerJourney-Scenario-Catalog]] — каталог 34 примеров сценариев в 8 категориях, разбор 9 диаграмм
- [[CustomerJourney-Installation-Chains]] — черновой список категорий предустановленных уведомительных цепочек
- [[CustomerJourney-Scenario-Model]] — понятийная модель + сравнение блоков схемы vs Mindbox/[[REES46]] + UI реестра/карточки сценария (из `Концептуальное решение 1-3.pdf` + `Блоки для сценариев лояльности.pdf`)
- [[CustomerJourney-WorkPlan]] — план работ 515 чд (этапы 1.1–2.5 + технологические), из `План работ по проекту.pdf`
- [[CustomerJourney-Route-Service-API]] — Сервис Маршрутов backend (`Route.*`, `AutoTrace.*`) из планового документа — см. предупреждение ниже про расхождение с методами `RouteService.*` из финального ТЗ
- [[CustomerJourney-Test-Plan]] — план тестирования, период 01.08–28.11.2026
- [[CustomerJourney-Events-Actions-Catalog]] — целевой (не-Mindbox) каталог событий/действий MVP, из `События-действия для сценариев лояльности.sabydoc.pdf`
- [[Saby-Scheme-Constructors]] — реестр 12 конструкторов схем Saby; «Путь клиента» — конструктор №12

### Техническое задание (согласованная финальная спецификация)

`Техническое задание.pdf` — в отличие от черновиков/бенчмарков выше, это **согласованный** документ (макеты помечены «Согласовано») с конкретным API, sequence-диаграммами и полной моделью данных:

- [[CustomerJourney-Scenarios-Project]] — цели, аудитория (~670 Presto-аккаунтов), 4 подсистемы-владельца ([[Route-Platform-Architecture]]/[[Trigger-System-Contract]]/Скрипты/Выборки), понятийная модель, лицензирование (полный тариф)
- [[Route-Platform-Architecture]] — Платформа Маршрутов: `RouteService.StartTrace/OnEvent`, `Route.Start/Stop/Status`, sequence-диаграммы запуска и авто-проходчика, модель Route/Trace/Events, DWC-пачки по 1000 клиентов, глобальная предфильтрация
- [[Trigger-System-Contract]] — Система триггеров: JSON-контракт (`triggers-data`/`base/actions`), каталог событий по приоритетам (1-3), каталог действий, `layout.Card`/`Trigger.Notify`
- [[CustomerJourney-UI-Decomposition]] — UI: реестр (мастер-деталь), карточка сценария (5 вкладок), карточка прохода, компоненты `Route/ScriptPage/*`

> [!contradiction] «Раннее исследование» vs «согласованное ТЗ»
> [[CustomerJourney-Scenarios-Project]] описывает проект как раннюю research-стадию («технического решения по своей архитектуре ещё нет»). `Техническое задание.pdf` — это уже принятое техническое решение с согласованными макетами. Раздел 6 ТЗ явно опирается на существующую (эксплуатируемую) Платформу Маршрутов как готовую инфраструктуру — согласуется с находкой про [[Route-Platform-Architecture]] в той же umbrella-странице. Также: [[CustomerJourney-Route-Service-API]] (из планового `План работ по проекту.pdf`) называет методы `AutoTrace.Start/Run/OnEvent`, тогда как финальное ТЗ фиксирует `RouteService.StartTrace/StartClientRoute/OnEvent` — вероятно переименование между планированием и финальным ТЗ, надо сверить при ингесте `Концептуальное решение*.pdf`. Также вероятный дубль сущности: [[Чусовитин-Александр]] (эта страница, из ТЗ) ≈ [[Чусовитин-Александр]] (из плана работ) — требует ручной проверки перед слиянием.
>
> **Подтверждающая деталь из `Концептуальное решение.pdf`** (самый ранний из документов батча, датировка неизвестна но по содержанию предшествует плану работ/ТЗ): формулировка открытого вопроса — *«Самое главное — не проработан механизм поддержки проходов сотни тысяч покупателей по тысячам маршрутов в аккаунтах **online**!»* — акцент на слове «online» подразумевает, что offline/Presto-версия сценариев (см. [[Route-Platform-Architecture]]) уже существует и работает; черновики этого батча описывают перенос/масштабирование существующего движка на облачную (online) платформу, а не создание системы с нуля. Также см. `Концептуальное решение 3 (Вопросы).pdf`: демо-скриншот реестра сценариев содержит реалистичные данные (счётчики покупателей 200/208/364/659/206/109/78/140/62, реальные Ф.И.О. ответственных) — похоже на скриншот уже существующего интерфейса, а не чистый мокап.

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

## Customer Journey / Маршруты (Путь клиента)

New marketing-automation / scenario engine ("Маршруты") built on top of Loyalty, allowing multi-step triggered customer journeys (reactivation, abandoned cart, birthday, welcome bonus). Early design phase — architecture inferred from a design-discussion doc dominated by open ownership questions between Лояльность, Маршруты, and the Выборки segmentation module.

- [[CustomerJourney-Scenarios-Project]] - project overview, folder map, sibling docs not yet ingested
- [[Route-Platform-Architecture]] - 3-party component model (Лояльность/Маршруты/Выборки), scenario types, flow-graph editor, event catalog, execution model, open ownership questions
- [[LoyaltyScenario-ReactivationInactiveClients]] - concrete example scenario: 30-day inactivity → 100 bonus points + email → 10-day wait → thank-you email
- [[Выборки-Module]] - audience segmentation module (owner: [[Гаврилов-Михаил]])

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
