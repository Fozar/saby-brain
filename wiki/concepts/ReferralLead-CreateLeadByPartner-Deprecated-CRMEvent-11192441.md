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
09:11:36.872–09:11:39.608). Причина найдена, правки не начаты — ждём выбора объёма фикса.

## Что выяснено по коду

- Метод отработал за 2.74 с. Три вызова `SourcesSales.GetLeadInfoV2` (advert-service) заняли 0.91 с (33%):
  1. 09:11:38.275–38.624 — обработчик `ReferralProgram.HandleSourceChanged` → `create_stub_by_lead`
     (`core/stub.py:224`).
  2. 09:11:38.842–39.149 — `ReferralProgram.CreateLead` (`referralprogram/create_lead.py:175`).
  3. 09:11:39.300–39.551 — `ReferralProgram.GetLead` (`referralprogram/get_lead.py:42`) из `GetLeadByPartner`.
- Каждый вызов `GetLeadInfoV2` уходит в advert-service, а тот дёргает
  `external_call('online', 'CRMEvent', 'listWithDocumentsEDO', ...)`
  (`crm/advert-service`, `AdvertHelper/advert_helper/sources_sales_api.py:364`). Получается online →
  marketing-apps → online: платформа пишет ERROR про устаревший метод и WARNING
  `[call loop] Функциональное_тестирование->Функциональное_тестирование`. Сам
  `CRMEvent.listWithDocumentsEDO` — метод модуля CRM (CRMActivity), объявлен deprecated.
- Вызовы 2 и 3 в нашем коде избыточны:
  - в `create_lead.py` от `lead_info` берутся LeadNum, LeadDate и Events. У только что созданной сделки
    итогового события нет — статус корешка в логе «В работе». Номер и дату сделки отдаёт
    `sbis.Лид.Прочитать` без обращения к advert-service.
  - `GetLeadByPartner` из `create_lead_by_partner.py:45` зовётся только ради LeadNum/LeadDate для истории
    партнёра; эти же значения на стороне владельца уже известны в `CreateLead` (там же пишется своя история).
- Вызов 1 (`create_stub_by_lead`) без advert-service не обойтись: там нужен `CRMPreload.List`
  (имя/телефон/email контакта) и `DealFace`. То же подтверждено задачей
  [[ReferralStub-ContactName-Assignee-CRMPreload-11026436]].
- В `handle_lead_state_changed.py` команда уже ушла с `GetLeadInfoV2` на
  `sbis.Лид.Прочитать(id, 'Лид.TinyWoContacts')` с `Лид.Переход.Название` / `Лид.Фаза.Название`
  (см. [[ReferralStub-Status-Description-Outcome-10284280]]) — готовый приём, который можно повторить.
- Дубль корешка: корешок успевает завести `HandleSourceChanged` (ловит локальное событие
  `salessources.source_changed` ещё внутри `CRMLead.insertRecord`), а `_create_stub_for_lead` затем
  получает «Корешок ... уже существует».

## Решения и почему

- Ошибку в логах порождает цепочка CRM/advert-service, а не наш код: мы `CRMEvent.listWithDocumentsEDO`
  напрямую не вызываем. Настоящее лечение — перевести `SourcesSales.GetLeadInfoV2` с deprecated-метода
  (владелец — Соков М.А., advert-service). Обойти это можно только убрав вызовы `GetLeadInfoV2` у себя.

## Открытые вопросы

- Какой объём фикса берём: убрать 2 из 3 вызовов (быстрее, но в логах остаётся одна ошибка) или все три
  (нужен источник контактов сделки вместо `CRMPreload`).
- Отдавать ли номер и дату сделки в ответе `ReferralProgram.CreateLead` (формат динамический,
  `allow_dynamic_return_format` = CRMLead.insertRecord) или заводить отдельный дешёвый метод.

## Roadmap

- [x] Прочитать задачу, ленту, вложения.
- [x] Снять серверные логи pre-test-online, разложить таймлайн вызовов.
- [x] Определить, чей код вызывает устаревший метод.
- [ ] Согласовать объём фикса.
- [ ] Реализовать + регрессионные тесты.
- [ ] MR.

## Ссылки

- Задача: https://online.sbis.ru/opendoc.html?guid=01a1f26f-45a8-7bff-ac4e-9410b3b52b71&client=3
- Логи стенда: https://pre-test-go.saby.ru/logs.zdA8T (uuid `075dcfbc-7702-aafe-cae4-922b360482a3`)
- Лог с ошибкой устаревшего метода: uuid `01a1f26e-9f8f-7b65-8307-67545297401c`
