---
type: decision
address: c-000272
title: "ReferralProgram.GetLeadPeriodList — HasPrices не долетал от старого владельца"
created: 2026-08-07
updated: 2026-08-07
decision_date: 2026-08-07
status: resolved
tags:
  - price-formation
  - referral
  - compatibility
  - bugfix
related:
  - "[[ReferralProgram-GetLeadPeriodList-LeadCount-Source]]"
  - "[[ReferralProgram-GetLeadPeriodList-Stub-Mode]]"
  - "[[SabyBank-RKO-Referral]]"
---

# ReferralProgram.GetLeadPeriodList — HasPrices не долетал от старого владельца

Задача №080611736 (Земцова, стенд), помечена «ошибка совместимости»: владелец реф. сети на old, партнёр на 26.4100 — в мастер-фильтре по периоду у партнёра пропадала колонка вознаграждения.

**Причина**: `GetLeadPeriodList` выполняется на сервере **владельца** (`agent_group_decorator` → `CreateMultitenantEndpointByClientId`). В `rc-26.4100` метод пишет `result.SetMetadataBool('HasPrices', ...)`; фронт (`_dateFilter/View.tsx`) добавляет колонку `Price` в грид только если это метаданное есть. У владельца на old (веха `rc-26.3264`) этой строки не было — колонка не рисовалась, хотя данные считались верно.

**Фикс**: добавил `SetMetadataBool('HasPrices', ...)` в `get_lead_period_list.py` на ветке `26.3264/bugfix/aatimoshenko/080611736`, затем смержил в новую `26.4100/bugfix/aatimoshenko/080611736` (от `rc-26.4100`) — конфликт был только на переехавшем тестовом файле, сам фикс смержился как no-op (в 4100 уже было то же самое).

**Второй симптом тикета** («не видно этапов сделки в детализации») — НЕ баг совместимости и не price-formation: серверный ответ (`.sbislogz` + `cloud_get_logs`) показал, что `Events` от владельца приходит полным (3 события, включая финальный статус). Обрезает их фронт: `client/.../Participant/_dealCard/Footer.tsx` берёт `events.at(count - 1)` в расчёте на порядок «старое→новое», а массив приходит «новое→старое» — получает самое старое событие вместо актуального статуса. Не мой фикс (client/ не трогаю без запроса), сообщил отдельно.

**Инструментальное**: репозиторий был shallow-clone — `git merge` двух веток с независимыми shallow-историями падал с «refusing to merge unrelated histories»; помогло `git fetch --unshallow`.
