---
type: source
address: c-000245
title: "Проверка переноса реферальных программ (MoveToAgentGroup) и подготовка тестовых данных"
source_type: sbis_dialog
created: 2026-07-31
updated: 2026-07-31
tags:
  - price-formation
  - referral-program
  - implementation
  - testing
status: current
related:
  - "[[ReferralProgram-MoveToAgentGroup]]"
  - "[[Земцова-Анастасия]]"
  - "[[Свешников-Андрей]]"
  - "[[Самарина-Ирина]]"
  - "[[Тимошенко А.А.]]"
---

# Проверка переноса реферальных программ (MoveToAgentGroup) и подготовка тестовых данных

Источник: `raw/Диалоги SBIS/79e80c8d-1cac-4435-be82-04ef943b4667.md` (theme_id `79e80c8d-1cac-4435-be82-04ef943b4667`), 2026-07-30.

Тимошенко торопит [[Земцова-Анастасия|Земцову А.]] — Свешников «очень переживает» по поводу проверки переноса. Земцова готовит тестовые данные, по ходу заводит 1 ошибку, обещает быть готова протестить через ~15 минут. Тимошенко публикует пример вызова метода из консоли:

```js
var params = {'ProgramId' : 0, 'TargetAgentGroupId' : ''};
new source.SbisService({
    endpoint: { address: '/service/', contract: 'ReferralProgram' },
}).call('MoveToAgentGroup', params)...
```

Также делится ссылкой на задачу (`dev.saby.ru/opendoc.html?...&client=3`). Земцова присылает две тестовые ссылки для сверки: ФОС-ссылку (`pre-test-site.sbis.ru/consultant-widget/...?utm_rfcid=202057373_8258027`) и реферальную ссылку (`pikabu.ru?utm_rfcid=202057373_8258027`) — оба с одним `utm_rfcid`, подтверждая связку источник↔тестовые данные для проверки переноса.

Метод и назначение параметров — [[ReferralProgram-MoveToAgentGroup]].
