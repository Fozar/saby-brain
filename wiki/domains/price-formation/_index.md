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
