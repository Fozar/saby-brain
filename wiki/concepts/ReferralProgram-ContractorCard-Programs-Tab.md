---
type: concept
title: "Вкладка «Программы» в карточке контрагента (спринт №3)"
updated: 2026-08-06
tags:
  - price-formation
  - referral
  - sabynet
  - crm
  - bl-methods
status: developing
related:
  - "[[ReferralProgram-Part2-Project]]"
  - "[[ReferralProgram-GetPartnerList-Stub-Stats]]"
  - "[[ReferralStub-LeadSum-Implementation]]"
  - "[[ReferralProgram-Data-Model]]"
  - "[[Михель-Витольд]]"
address: c-000262
created: 2026-08-06
---

# Вкладка «Программы» в карточке контрагента (спринт №3)

Navigation: [[ReferralProgram-Part2-Project]] | [[ReferralProgram-GetPartnerList-Stub-Stats]] | [[ReferralProgram-Data-Model]]

Спринт **«Отображение статистики по программам в карточке Партнёра»**, концепт от 12.12.2025 ([[Самарина-Ирина|Самарина И.]]). Срок 30.04.26 (26.2x), под фичей 14.02, на всех 04.04.26. Объём — **35,5 дней** (17,5 работ + 18 технологических).

Цель: владелец видит эффективность каждого партнёра в разрезе программ за период — из карточки контрагента, а не только из детализации оффера.

---

## Новые БЛ-методы

### `ReferralProgram.GetListByContractor`

Список всех реф. программ, участником которых является партнёр.

**Путь выборки**: `Карта` по полю `Лицо` с признаком `IsReferral` → `ВидКарты` → `ВидЦеныВидКарты` → `ВидЦены`; статистика — методом `SalesSources.ReadStat` (сервис Маркетинга).

**Фильтры**: `ContractorId: number`, `Period: [Date, Date]`.

**Возвращаемые поля**: `AdObject`, `Name`, `PartnerId` (нужен для метода изменения персонального вознаграждения), `PricePerLead` + `IsCustomPricePerLead`, `PricePerVisitor` + `IsCustomPricePerVisitor`, `Price`, `LeadCount`, `PositiveLeadCount`, `LeadSum`, `PositiveLeadSum`, `CustomerCount`.

> [!note] Статистика через маркетинг здесь противоречит спринту №2
> `GetListByContractor` в редакции декабря 2025 берёт статистику через `SalesSources.ReadStat`, тогда как [[ReferralProgram-Folders-Priority-Sprint|спринт №2]] тем же декабрём фиксирует **отказ** от маркетинга в пользу корешков `ВидЦеныДокумент`. К моменту реализации метод, скорее всего, должен строиться на корешках — как это сделано в [[ReferralProgram-GetPartnerList-Stub-Stats]] и [[ReferralProgram-GetLeadPeriodList-Stub-Mode]]. Набор полей (`LeadSum`/`PositiveLeadSum`) совпадает с агрегатами корешков из [[ReferralStub-LeadSum-Implementation]].

### `ReferralProgram.ContractorHasPrograms`

Вход `ContractorId: number` → булево. Реализуется поверх `GetListByContractor` **с лимитом 1**: вернулась запись — программы есть.

Встраивается в существующий метод **`Контрагент.CRMNavigationPreload`**: если реф. программы есть, `CRMNavigationPreload` возвращает дополнительную запись, по которой UI контрагентов рисует вкладку.

---

## UI

- Вкладка «Программы» — **по умолчанию** при открытии карточки Партнёра. Колонки: посетители, заявки, продажи (сумма завершённых сделок), % завершённых, вознаграждение за лид, вознаграждение за посетителя, сумма вознаграждения партнёра по программе.
- Общий компонент списка офферов на основе `LoyaltyOnline/ReferralLead/partner:View` — переиспользуется и в реестре «Партнёры» в детализации оффера, и в карточке контрагента ([[Михель-Витольд|Михель В.]], 3д).
- Открытие карточки контрагента из виджета «Партнёры» (`LoyaltyWidgets/ReferralLead/summary:View`) — через `ContractorCard/popup.StackOpener.showCard`, тот же хелпер, что уже используется в реестре «Партнёры».

## Работы

БЛ лояльности — [[Тимошенко А.А.|Тимошенко А.]] (списочный метод + `ContractorHasPrograms`); БЛ контрагентов — доработка `CRMNavigationPreload`; UI лояльности — [[Лебедева-Наталья|Лебедева Н.]] 3д + 0,5д; UI контрагентов — Малышев К. А. 0,5д; компонент списка офферов — [[Михель-Витольд|Михель В.]] 3д; тестирование — [[Земцова-Анастасия|Земцова А.]] 6,5д.

Источник: [[referral-program-part2-attachments-2026-08-06]].
