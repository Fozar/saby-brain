---
type: meta
title: "Concepts Index"
updated: 2026-04-07
tags:
  - meta
  - index
  - concept
domain: knowledge-management
status: evergreen
related:
  - "[[index]]"
  - "[[dashboard]]"
  - "[[Hot Cache]]"
  - "[[LLM Wiki Pattern]]"
  - "[[Compounding Knowledge]]"
  - "[[LLM Wiki Pattern]]"
  - "[[Hot Cache]]"
  - "[[Compounding Knowledge]]"
---

# Concepts Index

Navigation: [[index]] | [[entities/_index|Entities]] | [[sources/_index|Sources]]

All concept pages — ideas, patterns, and frameworks extracted from sources.

---

## Knowledge Management

- [[LLM Wiki Pattern]] — the core architecture for persistent, compounding knowledge bases
- [[Hot Cache]] — ~500-word session context file, updated after every ingest
- [[Compounding Knowledge]] — why the wiki grows more valuable over time, unlike RAG

---

## Price Formation / Loyalty (SBIS/Saby)

- [[PriceFormation-Common-Helpers]] — shared helpers in priceformationcommon/helpers/: type conversion, logging, validation, datetime, record utils, list method utils, sales points, roles, JSON/string utils, locks, feature flags, cloud, franchise, price rounding (status: evergreen)
- [[LoyaltyPrograms-IterativeListLoading]] — ListWithCursor, ListWithCompositeCursor, IterativeBlockSizeEmaMixin, SaleListWithCursor: полная API-документация курсорной навигации и итеративной загрузки (status: current)
- [[PriceFormationOnline-Helpers]] — helpers specific to priceformationonline/helpers/: context storage (ContextVar), ConfirmWarning aggregation, licensing, business groups, sale points, nomenclature, marketing/CRM, short URLs/CDN, LRS, loyalty events, color/image utils (status: evergreen)
- [[PriceFormationOnline-Core]] — базовые модули priceformationonline/core/: history tracking (.hox hooks, ВидЦены), LinkType (7 типов документов), set_not_used (broker sync), sales_point_tree (security whitelist), cloud statistics (CloudStatsFunctional/Context/Action, SaleDataForStatistics, SQL CTE multi-join) (status: evergreen)
- [[DCCommon-Helpers]] — DCCommon utilities: barcode/QR generation, encryption, stand detection, digital wallet (Apple Wallet/GPay), card theming, bonus balance calculation algorithm (status: evergreen)
- [[PriceFormation-Test-Framework]] — три тестовых проекта (Desktop/Online/OnlineWithDiscountCore); test_manager.py; cmake/ninja сборка; мок методов/таблиц; @enable_features/@with_feature/@test_new_skip (status: current)
- [[Franchise-Contract-API]] — 12 external `FranchiseContract.*` methods; lifecycle handlers, operator management, PointSalesList, AccessData
- [[Franchise-SabyNet-Subsystem]] — Saby Net franchise: separate app config, custom regulation (reduced fields), operator workflow, no KPI, shared bonus programs/акции across multi-account networks
- [[Franchise-Loyalty-Architecture]] — franchise group support in loyalty DB: FranchiseRole Owner/Participant, UUID lists on ВидЦены/ВидКарты/CardType/Operation, cross-account activation
- [[Loyalty-Franchise-Mechanics]] — БЛ Лояльности event subscriptions for franchise lifecycle: 5 events, folder creation logic, FranchiseRole values, sync/bonus flows
- [[Franchise-Loyalty-System]] — business overview of franchise loyalty: Owner/Participant model, sync (full-overwrite by UUID), unified customer base via Owner account, СДК as shared balance store
- [[Saby-Loyalty-Scenarios-Engine]] — движок маркетинговых сценариев (customer journey) в Retail/Presto: типы (по событию/периодический/разовый), конструктор условий Если/И/ИЛИ, блоки Действие/Условие/Ожидание, ветвление по событию, Цели (status: developing)
- [[Loyalty-Scenario-Reactivation-Inactive-Clients]] — пример сценария «Давно не покупали»: 30д без покупки → 100Б + email → ожидание 10д → thank-you email; открытые вопросы ревью (status: current)
- [[CustomerJourney-Loyalty-Scenarios-Project]] — «Путь клиента»: раннее исследование/бенчмарк конкурента [[Mindbox]] для проектирования CDP-подобной системы сценариев; перечень документов проекта (status: developing)
- [[AbandonedCart-Loyalty-Scenario]] — сценарий «Брошенная корзина» (Mindbox-версия): условия, события, полная схема, UX-анализ момента авторизации (сайт «Мили» / SabyGet); ⚠️ пересекается с уже существующим шаблоном «Брошенная корзина» в [[Saby-Loyalty-Scenarios-Engine]] (status: developing)
- [[TriggerScenario-ConditionsActions-Reference]] — справочник событий/фильтров сценарного конструктора Mindbox (8 категорий, ~36 событий, построитель фильтров); общий словарь для сценарных документов проекта (status: developing)
- [[CustomerJourney-Project]] — «Путь клиента»: умбрелла-страница по `Примеры различных сценариев со схемами.pdf` + `Инсталляционные цепочки.pdf`; ⚠️ см. [[CustomerJourney-Loyalty-Scenarios-Project]]/[[CustomerJourney-Scenarios-Project]] — несколько параллельно созданных umbrella-страниц одного проекта, требуют слияния оркестратором (status: developing)
- [[CustomerJourney-Scenario-Builder]] — механика конструктора: типы узлов (старт/условие/действие/ожидание-race/цель), 2 типа старта (событие/выборка), полные таблицы фильтров/действий/событий с пометками MVP (status: developing)
- [[CustomerJourney-Scenario-Catalog]] — каталог 34 примеров сценариев в 8 категориях (приветствие/возврат/лояльные клиенты/бонусы/реферальная/праздники/сервис/разовые), разбор структуры 9 диаграмм (status: current)
- [[CustomerJourney-Installation-Chains]] — черновой список категорий предустановленных уведомительных цепочек (начисления/уведомления/карты/промокоды) (status: developing)

---

## Wasaby Platform Services

- [[Report-Prefetch-Service]] — платформенный механизм кэширования отчётов; Prefetch.List конвейер из 11 узлов; индексы (sorted slices) для поиска/фильтрации/сортировки без полного перебора (status: current)
- [[ReportPrefetch-DB-Schema]] — схема БД report-prefetch-service: 6 таблиц (SessionId/StoredReport/ReportPage/ReportData/Method/ShardsAmountHistory), 5 типовых выборок, таблица индексов (status: current)

---

## Wasaby BL Patterns

- [[Wasaby-BL-Call-Loop-Pattern]] — Петля вызовов: причины, `CreateMultitenantEndpointByClientId` как решение, антипаттерны `EndPoint+auth_data` в одном ClientID (status: current)

---

## Wasaby Infrastructure

- [[Хоттабыч-System]] — Система обновлений: дистрибутивы, патчи, скрипты, фазы обновления, агенты (status: current)
- [[UpdateSystem-ReleasePlans]] — Планы выпуска: 7 типов работ, ограничения запуска, архитектура release-manager/release-external, публичный API (4 метода), рабочий процесс тестировщика, автообновление fix (status: current)
- [[UpdateSystem-DBConversion]] — Конвертация БД: Kubernetes-сервис database-converter; 5 типов задач, Redis-очередь, jinnee, автомасштабирование, облачные параметры (status: current)
- [[Wasaby-Patches]] — Патчи: экстренная правка файлов дистрибутива; интерфейс vs БЛ; 4-шаговый процесс (status: current)
- [[Wasaby-Scripts]] — DeveloperScript: выполнение кода через DWC; .orx объект; архивирование; ВНР; результаты (status: current)
- [[Wasaby-Access-Control]] — Права доступа: участки (.uax), роли (.rlx), ограничения (Access Area), области видимости (status: current)
- [[Wasaby-Cloud-Management]] — cloud-ctrl: Приложения (структура облака), Очередь (мониторинг), Клиенты, Пользователи (status: current)
- [[Wasaby-Request-Routing]] — Маршрутизация HTTP/AMQP: nginx upstream, ?srv=1, кэш Varnish, x_version/x_module при обновлениях (status: current)
- [[Wasaby-Distribution-Schema]] — Схема дистрибутивов: online32/online/regional/Тензор/demo/try-account; правила добавления модулей (status: current)
- [[Wasaby-Local-Stand-Setup]] — Локальные стенды: файловая структура, тестовые домены, Genie, дистрибутив, SDK совместимость (status: current)

---

## Add new concepts here as they are extracted from sources.
