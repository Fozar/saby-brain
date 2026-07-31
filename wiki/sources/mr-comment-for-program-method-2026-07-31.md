---
type: source
address: c-000239
title: "MR-комментарий 30.07.26: метод for_program в классе истории корешков"
source_type: sbis_dialog
created: 2026-07-31
updated: 2026-07-31
tags:
  - price-formation
  - referral-program
  - history
  - implementation
status: current
related:
  - "[[ReferralStub-History-Scope-Cut]]"
  - "[[mr-review-stub-history-call-2026-07-30]]"
  - "[[Мусохранов-Андрей-Владиславович]]"
  - "[[Тимошенко А.А.]]"
---

# MR-комментарий: метод for_program в классе истории корешков

Источник: `raw/Диалоги SBIS/44bd4968-7524-4f38-b55c-b4b829c84560.md` (theme_id `44bd4968-7524-4f38-b55c-b4b829c84560`), 2026-07-31 12:44.

Тимошенко: «Добавил метод `for_program` в класс истории корешков. Возвращает объект истории конкретного оффера. Адаптировал всю запись под использование этой механики.»

Однострочный MR-комментарий без ответа. По времени (12:44, тот же день) совпадает с уточнением имени объекта истории `ReferralStub_<ID>` в [[referral-history-implementation-breakdown-2026-07-29]] и следует за вопросом Мусохранова в ревью [[mr-review-stub-history-call-2026-07-30]] («как показать историю по корешкам только нужной программы») — трактуется как прямой ответ на этот вопрос реализацией. См. [[ReferralStub-History-Scope-Cut]] §«for_program».
