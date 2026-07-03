---
type: concept
title: "Путь клиента (Customer Journey) — проект Маршрутов лояльности"
aliases:
  - "Путь клиента"
  - "Customer Journey project"
tags:
  - loyalty
  - customer-journey
  - marshruty
  - project
status: developing
created: 2026-07-03
updated: 2026-07-03
related:
  - "[[LoyaltyScenarios-Marshruty-Architecture]]"
  - "[[LoyaltyScenario-ReactivationInactiveClients]]"
  - "[[Выборки-Module]]"
  - "[[Гаврилов-Михаил]]"
  - "[[Loyalty-Product-Overview]]"
  - "[[domains/price-formation/_index]]"
---

# Путь клиента (Customer Journey) — проект Маршрутов лояльности

Umbrella project (source folder `.raw/Путь клиента/`) building a new **marketing-automation / scenario engine** ("Маршруты") on top of the existing Лояльность subsystem — the ability to define multi-step, triggered customer journeys (reactivation, abandoned cart, birthday, welcome bonus, etc.) with conditions, wait periods, and actions (bonus accrual, discounts, promo codes, notifications).

## Status

Early architecture/design phase. First ingested document ([[loyalty-scenario-reactivation-inactive-v1-2026-07-03]]) is a walkthrough-style discussion doc dominated by unresolved ownership questions between Лояльность, the new Маршруты platform, and the Выборки segmentation module — see [[LoyaltyScenarios-Marshruty-Architecture]] for the extracted architecture and open-questions list.

## Documents in the project folder

Only one has been ingested so far. The rest are known to exist in `.raw/Путь клиента/` but **not yet ingested** — listed here as a map for future ingests:

- ✅ `Сценарий -Реактивация неактивных клиентов (давно не покупали)-.sabydoc.pdf` → [[loyalty-scenario-reactivation-inactive-v1-2026-07-03]]
- ⏳ `Сценарий _Реактивация неактивных клиентов (давно не покупали)_МОРОЗОВ правит.pdf` — revised/annotated version of the same scenario, being ingested in parallel as of 2026-07-03
- ⏳ `Блоки для сценариев лояльности.pdf` — likely the canonical action/condition block catalog
- ⏳ `Брошенная корзина.pdf` — abandoned-cart scenario (referenced as a scenario-list tile in the ingested doc)
- ⏳ `Инсталляционные цепочки.pdf`
- ⏳ `Конструкторы схем (Деев).pdf` — likely the flow-scheme editor spec, possibly clarifying Маршруты ownership questions
- ⏳ `Концептуальное решение.pdf`, `Концептуальное решение 2.pdf`, `Концептуальное решение 3 (Вопросы).pdf`
- ⏳ `План работ по проекту.pdf`
- ⏳ `План тестирования.pdf`
- ⏳ `Примеры различных сценариев со схемами.pdf`
- ⏳ `События-действия для сценариев лояльности.sabydoc.pdf` — likely the event/action catalog referenced in the ingested doc's Wait-block event picker
- ⏳ `Список УсловийДействий.pdf`
- ⏳ `Сравнение с конкурентами.pdf`
- ⏳ `Техническое задание.pdf` — likely the settled spec that resolves the open ownership questions
- ⏳ `Эксплуатация системы.pdf`

## Key people

- [[Гаврилов-Михаил]] — owns the Выборки (Selections/segmentation) module used for scenario audience targeting.

## Relationship to existing wiki content

This is the first ingest from the `Путь клиента` folder; no prior wiki pages covered "Маршруты" or scenario-builder concepts. Related existing domain content: [[Loyalty-Product-Overview]], [[Loyalty-UI-Components]], [[Loyalty-Database-Schema]] (the loyalty actions the scenario engine triggers — bonus accrual, discounts, promo codes — are the same core loyalty primitives documented there).
