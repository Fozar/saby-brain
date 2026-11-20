---
type: concept
title: "CreateLeadByPartner медленный и сыпет ошибку устаревшего CRMEvent (№11192441)"
created: 2026-11-20
updated: 2026-11-20
tags:
  - price-formation
  - referral
  - bug
status: analyzing
related:
  - "[[ReferralStub-Status-Description-Outcome-10284280]]"
  - "[[ReferralStub-ContactName-Assignee-CRMPreload-11026436]]"
  - "[[ReferralProgram-Stub-Implementation]]"
---

# CreateLeadByPartner медленный и сыпет ошибку устаревшего CRMEvent (№11192441)

## Задача

Ошибка на стенде №11192441 (Земцова А.В., 19.11.2026, веха 26.6100, срок 28.11.2026):
https://online.sbis.ru/opendoc.html?guid=01a1f26f-45a8-7bff-ac4e-9410b3b52b71&client=3

Симптом: в логах стенда ошибка `CRMEvent.listWithDocumentsEDO/4` — «Вызов устаревшего метода. Модули,
содержащие вызываемый метод: "CRMActivity"», и рядом предупреждение `[call loop]`.
`ReferralProgram.CreateLeadByPartner/3` отрабатывает ~3 с. Ожидается быстрый ответ без ошибок в логах.

Воспроизведение: авторизоваться под партнёром → портал РС → Офферы → оффер → Создать Лид →
заполнить обязательные поля → Отправить заявку.

## Где остановились

20.11: разобран серверный лог pre-test-online (uuid `075dcfbc-7702-aafe-cae4-922b360482a3`, 19.11.2026
09:11:36.872–09:11:39.608). Решение по объёму: правки в price-formation не делаем, задача передаётся
в advert-service с комментарием (кто зовёт устаревший метод). Готовится передача ответа Сокову М.А.

## Что выяснено по коду

- Метод отработал за 2.74 с. Три вызова `SourcesSales.GetLeadInfoV2` (advert-service) заняли 0.91 с (33%):
  1. 09:11:38.275–38.624 — обработчик `ReferralProgram.HandleSourceChanged` → `create_stub_by_lead`
     (`core/stub.py:224`).
  2. 09:11:38.842–39.149 — `ReferralProgram.CreateLead` (`referralprogram/create_lead.py:175`).
  3. 09:11:39.300–39.551 — `ReferralProgram.GetLead` (`referralprogram/get_lead.py:42`) из `GetLeadByPartner`.
- Каждый вызов `GetLeadInfoV2` уходит в advert-service, а тот дёргает
  `external_call('online', 'CRMEvent', 'listWithDocumentsEDO', ...)`
  (`crm/advert-service`, `AdvertHelper/advert_helper/sources_sales_api.py:364`, второй вызов —
  `Advert/ad_core/sources/sources_api.py:797`). Получается online → marketing-apps → online: платформа
  пишет ERROR про устаревший метод и WARNING
  `[call loop] Функциональное_тестирование->Функциональное_тестирование`.
- Сам `CRMEvent.listWithDocumentsEDO` — метод модуля CRM (CRMActivity), объявлен deprecated
  (`crm/core`, `CRMActivity.orx:2386`, владелец — Рыженко Д.А.). В price-formation его не зовём ни разу:
  в `www/service/Модули` совпадений нет, в `client` — только упоминание в комментарии
  (`client/LoyaltyOnline/ReferralLeadNew/Participant/DealCard/PrefetchConfig.ts`).
- У `SourcesSales` один владелец — Соков М.А. (AdvertHelper.orx:515, Advert.orx:19157,
  SalesSourcesOnline.orx:457), `person_id=24463724`.
- Наши вызовы `GetLeadInfoV2` (4 места: `core/stub.py:224`, `create_lead.py:175`, `get_lead.py:42`,
  `set_lead_price.py:112`) — не причина ошибки, но два из них в этом сценарии избыточны:
  - в `create_lead.py` от `lead_info` берутся LeadNum, LeadDate и Events. У только что созданной сделки
    итогового события нет — статус корешка в логе «В работе». Номер и дату сделки отдаёт
    `sbis.Лид.Прочитать` без обращения к advert-service.
  - `GetLeadByPartner` из `create_lead_by_partner.py:45` зовётся только ради LeadNum/LeadDate для истории
    партнёра; эти же значения на стороне владельца уже известны в `CreateLead`.
- Вызов `create_stub_by_lead` без advert-service не обойтись: там нужен `CRMPreload.List`
  (имя/телефон/email контакта) и `DealFace`. То же подтверждено задачей
  [[ReferralStub-ContactName-Assignee-CRMPreload-11026436]].
- В `handle_lead_state_changed.py` команда уже ушла с `GetLeadInfoV2` на
  `sbis.Лид.Прочитать(id, 'Лид.TinyWoContacts')` с `Лид.Переход.Название` / `Лид.Фаза.Название`
  (см. [[ReferralStub-Status-Description-Outcome-10284280]]) — готовый приём, если вернёмся к вопросу
  своих вызовов.
- Дубль корешка: корешок успевает завести `HandleSourceChanged` (ловит локальное событие
  `salessources.source_changed` ещё внутри `CRMLead.insertRecord`), а `_create_stub_for_lead` затем
  получает «Корешок ... уже существует».

## Решения и почему

- Устаревший метод `CRMEvent.listWithDocumentsEDO` вызывает advert-service, а не price-formation.
  По договорённости такие задачи передаются тому, кто зовёт метод: задача уходит в advert-service
  к Сокову М.А. с комментарием и разбором логов. Правки в price-formation по этой ошибке не делаем.
- Что нужно на стороне advert-service: заменить в `SourcesSales.GetLeadInfoV2` вызов устаревшего
  `CRMEvent.listWithDocumentsEDO` на актуальный метод (нужны `Events` в том же формате) либо согласовать
  замену с CRM (Рыженко Д.А. — владелец deprecated-метода).
- Отдельно (не в этой задаче): три вызова `GetLeadInfoV2` на одну заявку партнёра — расточительство
  даже после правки advert-service. Если будем сокращать, то сокращаем свои два избыточных вызова.

## Открытые вопросы

- Вернёмся ли к своим двум избыточным вызовам отдельной задачей (быстрее и меньше нагрузки на
  advert-service, но в логах ошибка всё равно останется, пока не починен advert-service).

## Roadmap

- [x] Прочитать задачу, ленту, вложения.
- [x] Снять серверные логи pre-test-online, разложить таймлайн вызовов.
- [x] Определить, чей код вызывает устаревший метод.
- [x] Согласовать объём: правки не делаем, передаём в advert-service.
- [ ] Передать задачу Сокову М.А. с комментарием и разбором логов.
- [ ] Проверка на стенде после правки advert-service.

## Ссылки

- Задача: https://online.sbis.ru/opendoc.html?guid=01a1f26f-45a8-7bff-ac4e-9410b3b52b71&client=3
- Логи стенда: https://pre-test-go.saby.ru/logs.zdA8T (uuid `075dcfbc-7702-aafe-cae4-922b360482a3`)
- Лог с ошибкой устаревшего метода: uuid `01a1f26e-9f8f-7b65-8307-67545297401c`
- Ответственный advert-service: Соков М.А. (`person_id=24463724`)
