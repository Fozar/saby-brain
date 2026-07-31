---
type: source
address: c-000237
title: "Баг на стенде 14.07.26 от Лебедева Н.А.: GetStubList не возвращает записи у партнёра"
source_type: sbis_dialog
created: 2026-07-31
updated: 2026-07-31
tags:
  - price-formation
  - referral-program
  - bug
status: current
related:
  - "[[ReferralProgram-GetStubList-Bug-Partner-No-Records]]"
  - "[[ReferralProgram-GetStubList-Filter-Redesign]]"
  - "[[Лебедева-Наталья]]"
  - "[[Земцова-Анастасия]]"
---

# Баг: ReferralProgram.GetStubList не возвращает записи у партнёра

Источник: `raw/Диалоги SBIS/019f60a3-2774-7c37-845f-159b66e3b891.md` (theme_id `019f60a3-2774-7c37-845f-159b66e3b891`), баг заведён 2026-07-14, переписка о воспроизведении — 2026-07-31.

[[Лебедева-Наталья]] запросила у [[Земцова-Анастасия]] логин/пароль для проверки бага; Земцова дала доступ на стенде `pre`: владелец (конверт/Пароль123), партнёр (письма/Пароль123), плюс логин-пароль аккаунта.

Сама переписка не содержит анализа причины — только координация воспроизведения. Заголовок фиксирует симптом: `ReferralProgram.GetStubList` не возвращает записи корешков у партнёра. Тема пересекается с уже задокументированным редизайном фильтров метода — [[ReferralProgram-GetStubList-Filter-Redesign]] (2026-05-28: `Date`/`PartnerId`); не исключено, что баг — регрессия этого редизайна, прямого подтверждения в источнике нет.

Разбор — [[ReferralProgram-GetStubList-Bug-Partner-No-Records]].
