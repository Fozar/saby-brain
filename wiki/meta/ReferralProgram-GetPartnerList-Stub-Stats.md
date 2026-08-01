---
type: decision
address: c-000248
title: "GetPartnerList: статистика по заявкам на основе корешков"
created: 2026-07-31
updated: 2026-07-31
decision_date: 2026-07-31
status: active
tags:
  - price-formation
  - referral-program
  - implementation
related:
  - "[[ReferralProgram-GetPartnerList-Unjoined-Partners]]"
  - "[[ReferralStub-DealSum-Field]]"
  - "[[ReferralStub-Stats-Index-Questions]]"
  - "[[zvonok-musohranov-timoshenko-2026-07-23]]"
  - "[[getpartnerlist-stub-stats-2026-07-31]]"
  - "[[Тимошенко А.А.]]"
---

# GetPartnerList: статистика по заявкам на основе корешков

Navigation: [[SabyBank-RKO-Referral]] | [[ReferralProgram-GetPartnerList-Unjoined-Partners]]

Реализация части решения из ревью [[zvonok-musohranov-timoshenko-2026-07-23|23.07]]: `ReferralProgram.GetPartnerList` дополнен статистикой по количеству заявок (всех и успешных) на основе данных из корешков (`ВидЦеныДокумент`), сдано пунктом плана 2026-07-31 (source: [[getpartnerlist-stub-stats-2026-07-31]]).

## Отношение к соседним страницам

- [[ReferralProgram-GetPartnerList-Unjoined-Partners]] — более ранняя (2026-05-22) доработка того же метода: показ партнёров без реферального кода (`AcceptedPartners` LEFT JOIN). Это отдельная, ортогональная доработка того же БЛ-метода — не путать: та про **состав строк** реестра партнёров, эта — про **новые колонки статистики** в уже существующих строках.
- [[ReferralStub-DealSum-Field]] — решение хранить сумму по сделкам в поле «Сумма» `ВидЦеныДокумент`, `SUM` рядом с `COUNT`; на момент ревью 23.07 сумма писалась пусто. Эта задача закрывает **количество** заявок (`COUNT`); статус поля «Сумма» источник 2026-07-31 не переоткрывает — предположительно всё ещё не заполняется.
- [[ReferralStub-Stats-Index-Questions]] — открытые вопросы по фильтру `ТипСвязи`/индексам, поднятые на том же ревью, остаются открытыми; источник 2026-07-31 не подтверждает их закрытие.

## Демонстрация

Тимошенко показал на трёх существующих заявках-корешках, что реестр партнёров отображает соответствующие цифры (source: [[getpartnerlist-stub-stats-2026-07-31]]). Технические детали SQL/индексов источник не раскрывает — только факт сдачи пункта плана.

## Открытое

- [ ] Подтвердить статус поля «Сумма» (`ReferralStub-DealSum-Field`) — заполняется ли уже, или по-прежнему заглушка
- [ ] Индексное покрытие ([[ReferralStub-Stats-Index-Questions]]) — не проверено на большой БД по данным этого источника
