---
type: entity
title: "Выборки (Selections module)"
aliases:
  - "Selections module"
  - "Segmentation module"
tags:
  - entity
  - product
  - loyalty
  - customer-journey
  - segmentation
status: current
created: 2026-07-03
updated: 2026-07-03
related:
  - "[[Гаврилов-Михаил]]"
  - "[[LoyaltyScenarios-Marshruty-Architecture]]"
  - "[[LoyaltyScenario-ReactivationInactiveClients]]"
  - "[[Loyalty-CustomerJourney-Project]]"
  - "[[loyalty-scenario-reactivation-inactive-v1-2026-07-03]]"
---

# Выборки (Selections module)

A Saby/Tensor audience-segmentation component, owned by a separate team led by [[Гаврилов-Михаил]]. Supplies the client-condition builder UI (fields + И/ИЛИ boolean composition) and backend evaluation used by the [[LoyaltyScenarios-Marshruty-Architecture|Маршруты scenario engine]] to select the audience for a loyalty scenario.

## Role in the scenario engine

Confirmed (in-doc, green-highlighted): "Тут все понятно, это нам предоставят Выборки. Миша Гаврилов" — used for the Email-presence, Не покупали (hasn't purchased), and Когда (time-window) conditions in the [[LoyaltyScenario-ReactivationInactiveClients|reactivation scenario]] example.

## Known condition fields (from scenario start-condition dialog)

Покупали, Не покупали, Что, Где, Физлица (Пол, Возраст, День рождения), Владельцы карт, Без, Кол-во бонусов, Когда, Количество, Число покупок, Сумма, С последней покупки прошло, Есть телефон, Email.

Composed with И/ИЛИ (AND/OR) boolean logic groups.

## Open questions

- How the identifier of a saved selection + its metadata is persisted and handed off to the scenario dialog is unresolved as of v1 of the source document (see [[LoyaltyScenarios-Marshruty-Architecture]]).

## Sources

- [[loyalty-scenario-reactivation-inactive-v1-2026-07-03]] — only source mentioning this module so far.
