---
type: concept
title: "Сценарий «Реактивация неактивных клиентов (давно не покупали)»"
aliases:
  - "Давно не покупали"
  - "Reactivation of inactive clients scenario"
tags:
  - loyalty
  - customer-journey
  - marshruty
  - scenario-design
status: developing
created: 2026-07-03
updated: 2026-07-03
related:
  - "[[Route-Platform-Architecture]]"
  - "[[CustomerJourney-Scenarios-Project]]"
  - "[[Выборки-Module]]"
  - "[[loyalty-scenario-reactivation-inactive-v1-2026-07-03]]"
---

# Сценарий «Реактивация неактивных клиентов (давно не покупали)»

The first concrete scenario used to design the [[Route-Platform-Architecture|Маршруты scenario engine]]. Also appears as the "Давно не покупали" tile in the scenario list example.

## Business rule

> Ежедневно отбираем клиентов, кто не покупал последние 30 дней. Начисляем 100 бонусов и отправляем письмо, ждём покупки до 10 дней; если есть покупка — отправляем письмо «спасибо».

## Configured instance (v1 walkthrough)

- **Type:** Периодический ("По расписанию"), trigger **Ежедневно 12:00**.
- **Selection condition** (built via [[Выборки-Module]]): Физлица → Есть Email **AND** Не было покупок → За последние **30** дн.
  - > [!question] Gap flagged by the doc's own authors
    > "В идеале ещё выбрать Покупали" — i.e. the condition as configured selects clients who simply haven't purchased in 30 days, **including clients who never purchased at all**. The intended audience is presumably "used to purchase, has gone quiet" — an explicit "Покупали" (has purchased, ever/before window) filter is a known missing piece, not yet added in v1.
- **Step 1 — Action «Начислить бонусы»**: accrue **100** bonus points. Expiration-date field noted as missing in the mockup ("надо добавить срок сгорания").
- **Step 1 — Action «Отправить» (e-mail)**: channel "Отправить по e-mail", From: *Ресторан Мили* (sample/demo tenant name, not a real Tensor entity), body: *"Заберите ваши бонусы! Подарок от нас: 100 бонусов уже ждут вас в личном кабинете!"*
- **Step 2 — Ожидание («Wait»)**: "Ожидание покупки 10 дней" — branches: event **Розничная покупка** (client purchased) vs. **Время вышло** (10-day timeout, no explicit follow-up action shown for the timeout branch in v1).
- **Step 3 — Action «Отправить» (thank-you e-mail)**, fired on the Розничная покупка branch: *"Спасибо, что выбираете нас! Поделиться впечатлением на magazin.ru"*.
- **Цели (Goals):** left empty at build time ("Без целей пока"); once launched, sample placeholder goals appear on the card ("Промо-акция сработала", "Отказался от покупки") — origin/ownership of these defaults is unclear (Маршруты platform default, per architecture page).

## Sample run observed in mockup (client: Загребова Елена)

Illustrates the pass-detail timeline described in [[Route-Platform-Architecture]]:

1. **19 авг** — «Клиент отобран» (matched: Физлица Есть Email, Не было покупок за последние 30 дн)
2. Действие: «Начислить 100Б, отправить Email»
3. «Ожидание покупки 10 дней» starts
4. **20 авг** — «Есть покупка»: order **9 247 ₽** (items: "GUESS NOELLE 8 TOP ZIP" 3 499 ₽ + "Туфли Dino Ricci Select 39 Коричневый" 5 748 ₽)
5. Действие: «Отправить Email» (thank-you)
6. «Промо-акция сработала за 1 д» (goal fired)

Other sample (mock/synthetic) clients enrolled in the same run: Олег, Екатерина, Александрова Николай, Егор, Обручев Сергей, Наталия, Новосельцев Валентин.

## Statistics requirements (not yet designed)

The document explicitly lists required metrics for the Статистика tab, marked "новый макет" (new mockup needed, not yet built):

- Кол-во помещённых / прошедших / купивших клиентов
- Сумма начисленных баллов
- Кол-во отправленных писем
- Кол-во и сумма покупок

## Provenance & revision note

Extracted from v1 of the design doc: [[loyalty-scenario-reactivation-inactive-v1-2026-07-03]]. A sibling document with edits/comments from **Морозов** covers the same scenario and was ingested in parallel as [[reaktivaciya-neaktivnyh-klientov-morozov-2026-07-03]], which produced its own overlapping concept page [[LoyaltyScenario-ReactivationInactiveClients]] (near-duplicate of this page, different name). A third overlapping description of the same example ("Покупатель не активен (30 дней)") exists at [[CustomerJourney-Scenario-Model]] from yet another parallel source. All three describe the same business scenario from different documents in the same batch — **not reconciled at write time**; merge/dedupe is left to the orchestrator's cross-batch finalize pass.
