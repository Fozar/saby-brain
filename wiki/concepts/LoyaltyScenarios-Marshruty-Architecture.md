---
type: concept
title: "Loyalty Scenarios / Маршруты Platform — Architecture"
aliases:
  - "Сценарии лояльности"
  - "Маршруты platform"
  - "Customer journey scenario engine"
tags:
  - loyalty
  - customer-journey
  - marshruty
  - marketing-automation
  - architecture
  - project
status: developing
created: 2026-07-03
updated: 2026-07-03
related:
  - "[[CustomerJourney-Scenarios-Project]]"
  - "[[LoyaltyScenario-ReactivationInactiveClients]]"
  - "[[Выборки-Module]]"
  - "[[Гаврилов-Михаил]]"
  - "[[Loyalty-Product-Overview]]"
  - "[[Loyalty-UI-Components]]"
  - "[[DWC-Distributed-Workflow-Coordinator]]"
  - "[[loyalty-scenario-reactivation-inactive-v1-2026-07-03]]"
---

# Loyalty Scenarios / Маршруты Platform — Architecture

A new UI section **«Сценарии»** ("Scenarios") is being added to the Лояльность (Loyalty) menu, alongside Бонусы / Промокоды / Реферальная система / Дисконтные карты. It lets an operator (in Розница/Presto) build automated, multi-step customer-journey scenarios — e.g. reactivation of inactive clients, abandoned-cart reminders, birthday greetings, welcome bonuses. The engine is built on a generic (non-loyalty-specific) platform called **Маршруты** ("Routes"), with **Лояльность** supplying loyalty-domain actions/conditions and **Выборки** supplying audience segmentation.

> [!note] Status of this page
> Extracted from an early internal design-discussion document ([[loyalty-scenario-reactivation-inactive-v1-2026-07-03]]) that is mostly a list of **open ownership questions**, not a settled spec. Ownership assignments below marked "assumed" are the document authors' working hypothesis, not a confirmed decision. A revised sibling document (Морозов edits) may resolve some of these — check for updates before relying on this as ground truth.

> [!warning] Duplicate/overlapping pages created by parallel batch-ingest agents
> Other agents ingesting sibling files from the same `.raw/Путь клиента/` folder concurrently created several overlapping pages describing the same underlying feature under different names: [[Route-Platform-Architecture]], [[Route-Platform-Architecture]], [[CustomerJourney-Scenario-Builder]], [[CustomerJourney-Scenarios-Project]]. This page was written independently and was **not reconciled** with those at creation time. The orchestrator should merge/dedupe this cluster in its cross-batch finalize pass rather than treating these as independent facts.

## Three-party component model

| Component | Believed to own | Confirmed? |
|---|---|---|
| **Лояльность** (this team, PriceFormation.Online) | Loyalty-domain actions (Начислить бонусы / Назначить скидку / Выдать промокод), general settings semantics (re-entry cooldown, quiet mode) — per authors | Not fully — see open questions |
| **Маршруты** (Routes/Customer Journey platform, separate/new) | Scenario card CRUD, flow-scheme (Схема) graph editor, block-type/action/event picker chrome, Проходы (run log) registry + pass-detail card, periodic scheduler/trigger, "авто-проходчик" (auto-walker) execution engine | **No** — assumed by authors, not confirmed by the Маршруты team |
| **Выборки** (Selections/segmentation module, team led by [[Гаврилов-Михаил]]) | Audience-condition builder UI components + backend evaluation (Покупали/Не покупали/Что/Где/Пол/Возраст/Email/etc.), returns matching client list | Yes — explicitly confirmed in-doc ("Тут все понятно, это нам предоставят Выборки. Миша Гаврилов") |

See [[Выборки-Module]] for the segmentation component in detail.

## Scenario types

Picked from a "+" menu when creating a scenario:

- **По событию** ("By event") — triggered by a client action (purchase, site visit, registration, etc.); event picked immediately in the creation menu.
- **Периодический** ("Periodic") — runs on a recurring schedule (e.g. daily at 12:00), each run re-evaluates a saved audience selection.
- **Разовый** ("One-off") — runs once against a manually chosen set of clients.

## General settings (defaults, apply to all scenario types)

Filled in by default; edited rarely ("донастройка"):

- **Re-entry cooldown**: "Клиент попадает в сценарий не чаще [N] дн" (default 30), toggle **Ограничить срабатывание**, on by default.
- **Режим тишины** ("Quiet mode"): pauses scenario firing during a configured time window, evaluated in the **client's own timezone**. Also on by default.

Open question: whether Лояльность or Маршруты owns the dialog + storage/read/apply logic for these settings (doc assumes Лояльность, since client-enrollment-via-selection is a Loyalty responsibility, but unconfirmed).

## Start-condition dialog ("Запуск сценария")

Two logically separate parts shown in one dialog:

- **Part A — Periodicity**: when the trigger fires (e.g. "Ежедневно 12:00"). Ownership unconfirmed.
- **Part B — Selection conditions**: audience filter built from Выборки condition primitives (И/ИЛИ boolean groups; fields: Покупали, Не покупали, Что, Где, Физлица→Пол/Возраст/День рождения, Владельцы карт, Без, Кол-во бонусов, Когда, Количество, Число покупок, Сумма, С последней покупки прошло, Есть телефон, Email). Confirmed as [[Выборки-Module]]'s domain.

After saving, the identifier of the saved selection + schedule metadata must be threaded into the next dialog (the scenario card) — the mechanism for this hand-off is an open question in v1.

## Scenario card

Tabs: **Описание** (start conditions + Цели/Goals block, read-only-ish summary) · **Этапы** · **Схема** (flow-graph editor) · **Проходы** (run log/registry) · **Статистика** (metrics — **not designed yet**, `новый макет` placeholder in v1).

CRUD ownership of the card itself is assumed to be Маршруты platform functionality ("В нашем понимании это функциональность платформы Маршрутов"), unconfirmed.

## Flow-graph editor ("Схема")

A node-based graph editor, opened after start-condition save, with a "+" node-type picker offering three node kinds:

1. **Действие** (Action) — one of: Начислить бонусы (accrue bonus points, amount configurable, expiration-date field **missing** in v1 mockup — flagged TODO), Назначить скидку, Выдать промокод, Отправить (send — channel e.g. e-mail, From/sender name, subject+body template), Перенести в папку, Добавить тег, Выполнить код.
2. **Условие** (Condition) — branching logic node (not elaborated in this document beyond the palette entry).
3. **Ожидание** (Wait) — pauses the client on this node for N days (или other unit), with И/ИЛИ branch conditions evaluated against named platform **events** (see below) plus an implicit "Время вышло" (timeout) branch.

Which team builds/owns this editor chrome, the action-type list, and each config sub-dialog is repeatedly flagged as an open question — the doc's authors note the action list itself must somehow be scoped to "the applied object bound to the route type," without a stated mechanism.

## Event catalog

Used to configure Wait-node branch conditions (and as the trigger source for По событию scenarios). Presented as a tree grouped by object:

- **Лояльность**
- **Клиент** — Оптовая покупка, Действия с карточкой клиента, **Розничная покупка**
- **Посетитель сайта** — Вход на сайт; **Корзина**: Добавлен товар, Брошенная корзина, Заказ создан/изменен, Продукт добавлен в избранное, Окончание сессии
- **Бронирование**
- **Запись**

Open question: how is this list scoped so only loyalty-relevant events appear, and who builds the picker window.

## Execution model (assumed, unconfirmed)

1. At the scheduled time, the Маршруты platform calls an **applied ("прикладной") BL method** — owned/registered by Лояльность — running online.
2. That method runs the Выборки-based selection and returns the list of matching clients.
3. New clients (not already enrolled) are placed at step 1 of the scenario.
4. An **"авто-проходчик"** (auto-walker) executes all consecutive non-Wait nodes for a client in one pass; the resulting batch of fired events is aggregated into a single **Проход** (pass/run) record on the Проходы tab.
5. Clicking a pass record opens a **pass detail card** showing a client-level timeline of every node the client passed through, with timestamps and event payload (e.g. purchase amount/items) — how Loyalty pushes such payload into Маршруты's storage/statistics ("через какое API?") is unresolved.

## Open ownership questions (representative, not exhaustive)

See the full annotated list in [[loyalty-scenario-reactivation-inactive-v1-2026-07-03]]. Categories: menu/nav ownership, general-settings ownership, scenario-card CRUD ownership, clients-registry (no mockup yet), Goals block ownership, selection-ID hand-off mechanism, flow-editor/picker-window ownership, event-catalog scoping, trigger-method contract (format/registration field), run-time metadata push API, auto-walker spec.

## Related concept

- [[LoyaltyScenario-ReactivationInactiveClients]] — the one concrete scenario this architecture was reverse-engineered from.
