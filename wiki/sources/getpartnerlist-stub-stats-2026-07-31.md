---
type: source
address: c-000236
title: "Пункт плана: статистика по заявкам в реестре партнёров на основе корешков"
source_type: sbis_dialog
created: 2026-07-31
updated: 2026-07-31
tags:
  - price-formation
  - referral-program
  - implementation
status: current
related:
  - "[[ReferralProgram-GetPartnerList-Stub-Stats]]"
  - "[[Тимошенко А.А.]]"
  - "[[Свешников-Андрей]]"
  - "[[ReferralStub-DealSum-Field]]"
---

# Пункт плана: статистика по заявкам в реестре партнёров на основе корешков

Источник: `raw/Диалоги SBIS/27e85adc-2350-430c-9d7b-18b7d67f4694.md` (theme_id `27e85adc-2350-430c-9d7b-18b7d67f4694`, 2026-07-31), адресат — [[Свешников-Андрей]].

Тимошенко сдаёт пункт плана: `ReferralProgram.GetPartnerList` теперь отображает в реестре партнёров статистику по количеству заявок (всех и успешных) на основе данных из корешков (`ВидЦеныДокумент`). Демонстрация: 3 существующие заявки-корешка → в реестре партнёров показываются соответствующие цифры.

Детали — [[ReferralProgram-GetPartnerList-Stub-Stats]]. Это реализация части решения из [[zvonok-musohranov-timoshenko-2026-07-23|ревью 23.07]] (подсчёт по количеству заявок); сумма по сделкам (поле «Сумма») по-прежнему числится как отложенная — см. [[ReferralStub-DealSum-Field]].
