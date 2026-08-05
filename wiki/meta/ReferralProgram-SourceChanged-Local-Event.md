---
type: decision
title: "ReferralProgram-SourceChanged-Local-Event"
created: 2026-08-05
updated: 2026-08-05
tags:
  - loyalty
  - referral
  - events
  - price-formation
  - crm
  - wasaby
status: active
decision_date: 2026-08-05
related:
  - "[[ReferralDeals-System]]"
  - "[[ReferralProgram-Module]]"
  - "[[Server-Events-Bus]]"
  - "[[Wasaby-Module-System]]"
  - "[[Wasaby-MQ]]"
sources:
  - "logs/pre-test-online-05-08-2026_11-58-54-578.sbislogz"
---

# ReferralProgram-SourceChanged-Local-Event

Navigation: [[price-formation/_index]] | [[ReferralDeals-System]] | [[Server-Events-Bus]]

## Задача

№07222426: корешок реферальной программы сейчас создаётся только при создании новой сделки (`create_lead.py`). Нужно создавать его и при смене источника у **существующей** сделки на реферальный — для этого требуется событие смены источника со стороны сервиса сделок, на которое можно подписаться.

## Находка: `salessources.source_changed` публикуется в пуле `online`, том же, где живёт LoyaltyReferral

Смена источника у сделки в UI (Деловые линии → «Птица-Синица, ООО») — это `SalesSources.ManualPick` (`crm-service`/`advert-service`, host `pre-test-marketing-apps-bl4...`). Внутри него — асинхронный вызов `SourcesSales.InstalledOnLead`, который выполняется **не в advert-service**, а в пуле `online` (host `sbis-online-a2-0X.pre-test-online-ru-01.svc...`) — том же BL-пуле, где упакован `LoyaltyReferral` (см. `tests_new/online/clouds/Online/Online.s3cld`, `Service.s3srv` включает `LoyaltyReferral.s3mod`). Косвенное подтверждение — роутинг: `SourcesSales.*` (`HasChildren`, `InstalledOnLead`) идёт через `/service/` (online), а `SalesSources.*` (`SelectionList`, `ManualPick`) — через `/crm-service/service/` (отдельный физический сервис).

Внутри `SourcesSales.InstalledOnLead` публикуются два **локальных** события (модуль `event`, лог-маркер `[event][local][start/finish]`):

```json
"salessources.source_changed": {
  "ObjectId": "245",          // id сделки (Лид), строка
  "TypeName": "Лид",
  "Place": 5829748,            // id нового источника (AdObject/Place нового SalesSource)
  "AdObject": null,
  "OldSourceId": "5829748/5829748"
}
```

```json
"sourcessales.name_changed": {
  "ObjectId": "245",
  "SrcName": "Птица-Синица, ООО",
  "Type": 0,
  "TypeName": "Лид",
  "FirstInstall": false,
  "HowInstalled": "Manual pick by place"
}
```

Сразу после публикации `SourcesSales.InstalledOnLead` рассылает межсервисные async-вызовы уже существующим подписчикам (это же событие, доставленное дальше подписчикам, которые НЕ находятся в том же пуле): `Lead.ExecuteCallbackHandler` (хендлер `_WriteHistoryChangeSourceHndl`), `ClientsListCallbacks.AddHistoryMessageByChangeSource`, `ClientsListCallbacks.TriggerNotifyByChangeSource`, `RecruitmentHandler.OnSyncCandidateSource`, `RecruitmentHandler.OnCandidateWriteHistory`, `Accommodation.SourceNameChangeHistory`, `KPIDoc.NeedCalculateOnSourceChange`.

## «Local» ≠ недоступно — важное уточнение

Изначальный вывод («local» = внутрипроцессное событие, для подписки требуется доработка со стороны CRM, добавляющая новый async-вызов в список выше) был **неверным**. По [[Server-Events-Bus]]: «Можно публиковать и обрабатывать событие в одном рабочем процессе — брокер не участвует» — то есть `[event][local]` в логе означает just то, что в конкретный момент подписчик оказался в том же воркере, что и издатель, а не то, что событие в принципе недоступно снаружи процесса, публикующего его.

Прямое подтверждение — в `price-formation` уже есть работающий прецедент того же паттерна: `www/service/Модули/LoyaltyReferral/on_event.py:16-20` подписывает `ReferralProgram.HandleLeadStateChanged` на `Lead.StateChanged` через `event.SetLocalCallback(...)`, и это уже работает в проде ([[ReferralDeals-System]] §«При смене статуса сделки»). `Lead.StateChanged`, судя по всему, тоже публикуется в пуле `online`.

## Решение

Доработка **только на стороне price-formation**, без правок CRM/advert-service. В `on_event.py` добавить:

```python
event.SetLocalCallback(
    'salessources.source_changed',
    'ReferralProgram.HandleSourceChanged',
    event.Placeholder(),
)
```

В обработчике `ReferralProgram.HandleSourceChanged(ObjectId, TypeName, Place, AdObject, OldSourceId)`:
1. По `Place` проверить через `get_source_by_ext_id`/`SourceType.REFERRAL_CODE` (`priceformationonline/helpers/marketing.py`), реферальный ли новый источник.
2. Если да — создать корешок тем же путём, что `_create_stub_for_lead` в `create_lead.py:310` (`www/service/Модули/LoyaltyReferral/loyaltyreferral/referralprogram/referralprogram/create_lead.py`), включая защиту от дублей через `is_stub_exists`.

**Не проверено на практике**: что `salessources.source_changed` реально долетает до `SetLocalCallback`-регистра price-formation так же надёжно, как `Lead.StateChanged` (оба, предположительно, публикуются в пуле `online`, но это не проверено прямым тестом). Перед полной реализацией стоит повесить тестовый обработчик с логированием и убедиться, что он реально срабатывает на стенде при смене источника.

## Методология поиска

Восстановлено по клиентскому `.sbislogz` (конвертирован через `mcp__sbislog-parser__convert_log_to_json`) + серверным логам облака (`mcp__sbis__cloud_get_logs`), сцепленным по `uuid` асинхронного вызова через всю цепочку: `SalesSources.ManualPick` (request `uuid`) → `[async call]SourcesSales.InstalledOnLead ... uuid:X` → повторный запрос `cloud_get_logs(uuid=X)` вскрыл полную трассу внутри `SourcesSales.InstalledOnLead`, включая публикацию событий и рассылку подписчикам.

**Грабли инструмента**: `cloud_get_logs.from_dt/to_dt` без явного смещения часового пояса трактуются как локальное время **хоста MCP-сервера** (в данном случае UTC+7 — никак не связано с московским временем и не с UTC клиентского лога). Три первых попытки запроса промахнулись мимо окна логов из-за этого. Описание параметров в `sbis-mcp/src/sbis_mcp/server.py` (`cloud_get_logs`) поправлено — теперь явно указывает на риск и просит передавать смещение явно.

## Связанные страницы

- [[ReferralDeals-System]] — общая архитектура реферальной системы сделок, `Lead.StateChanged` как существующий прецедент подписки
- [[ReferralProgram-Module]] — модуль ReferralProgram
- [[Server-Events-Bus]] — шина серверных событий Wasaby, объясняет семантику `[event][local]`
- [[Wasaby-Module-System]] — `on_event.py`, `event.SetLocalCallback` vs `event.Subscription` (облачная подписка с брокером)
