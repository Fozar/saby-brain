---
type: source
address: c-000246
title: "Баг на стенде 30.07.26: CreateStubsForExistingLeads не находит сделки — включена в версию 4100"
source_type: sbis_dialog
created: 2026-07-31
updated: 2026-07-31
tags:
  - price-formation
  - referral-program
  - bug
  - migration
status: current
related:
  - "[[ReferralStub-Backfill-Service-Method]]"
  - "[[Тимошенко А.А.]]"
  - "[[Земцова-Анастасия]]"
  - "[[Migration-Console-First-Testing-Pattern]]"
---

# Баг: ReferralProgram.CreateStubsForExistingLeads не находит сделки

Источник: `raw/Диалоги SBIS/019fb20d-a75e-75c1-b116-982919ae574e.md` (theme_id `019fb20d-a75e-75c1-b116-982919ae574e`), 2026-07-30.

Тимошенко просит [[Земцова-Анастасия|Земцову А.]] включить в версию **4100** служебный метод создания корешков для существующих сделок (`ReferralProgram.CreateStubsForExistingLeads`, см. [[ReferralStub-Backfill-Service-Method]]). Через 16 минут переоформляет запрос как «ошибку на стенде» — то есть метод на тот момент не находит сделки, что заведено как баг для трекинга. Земцова подтверждает включение в 4100 через ~2.5 часа.

Источник не содержит анализа причины бага («не находит сделки») — только координацию включения в версию. Продолжает линию [[Migration-Console-First-Testing-Pattern|console-first проверки]]: метод по-прежнему обкатывается на реальных данных, а не сразу отдаётся в массовую ВНР-миграцию.
