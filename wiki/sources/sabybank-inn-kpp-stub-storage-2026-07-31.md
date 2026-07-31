---
type: source
address: c-000235
title: "Пункт плана: сохранение ИНН/КПП в корешках заявок SabyBank"
source_type: sbis_dialog
created: 2026-07-31
updated: 2026-07-31
tags:
  - price-formation
  - referral-program
  - sabybank
  - implementation
status: current
related:
  - "[[SabyBank-Stub-INN-KPP-Storage]]"
  - "[[Тимошенко А.А.]]"
  - "[[Свешников-Андрей]]"
  - "[[SabyBank-RKO-Referral]]"
  - "[[ReferralProgram-Stub-Implementation]]"
---

# Пункт плана: сохранение ИНН/КПП в корешках заявок SabyBank

Источник: `raw/Диалоги SBIS/971c21aa-af1c-416f-8a1d-275e2cb5648b.md` (theme_id `971c21aa-af1c-416f-8a1d-275e2cb5648b`, 2026-07-31), адресат — [[Свешников-Андрей]].

Тимошенко сдаёт пункт плана: реализовано сохранение ИНН и КПП клиента в корешках заявок SabyBank. На интерфейсе значения пока нигде не отображаются — это чисто бэкенд-хранение. Демонстрация: создание заявки → открытие корешка → метод корешка возвращает те же значения ИНН/КПП, что были у исходного клиента при создании заявки.

Детали и модель хранения — [[SabyBank-Stub-INN-KPP-Storage]].
