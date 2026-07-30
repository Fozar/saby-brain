---
type: meta
title: "Sources Index"
updated: 2026-07-29
tags:
  - meta
  - index
  - source
status: evergreen
related:
  - "[[index]]"
  - "[[log]]"
  - "[[entities/_index]]"
  - "[[Andrej Karpathy]]"
---

# Sources Index

Navigation: [[index]] | [[concepts/_index|Concepts]] | [[entities/_index|Entities]]

All source pages — summaries of ingested documents, transcripts, articles, and data.

---

## Transcripts

- [[zvonok-offer-bug-zlateks-2026-04-13]] — 2026-04-13 | Звонок: баг оффера у партнёра Златекс. client_id mismatch (77 vs 78), критический, дедлайн 2026-04-15

---

## Documentation Review

- [[reaktivaciya-neaktivnyh-klientov-morozov-2026-07-03]] — 2026-07-03 | Сценарий «Реактивация неактивных клиентов»: аннотированная версия (Морозов), 7 ревью-пометок, sibling к чистовику `.sabydoc.pdf`

---

## Articles

<!-- Add article source pages here -->

---

## Papers

<!-- Add paper source pages here -->

---

## SBIS / Price Formation

- [[linter-project-2026-05-18]] — 2026-05-18 | Проект подключения линтеров и SonarQube (5 docs: ТЗ, цель, план, отчёт, инструкция). Завершён 04.05.2026, перерасход +19.1% | 2 pages created
- [[report-prefetch-db-schema-2026-04-13]] — 2026-04-13 | Схема БД report-prefetch-service: 6 таблиц (SessionId/StoredReport/ReportPage/ReportData/Method/ShardsAmountHistory), 5 типовых выборок, таблица индексов | 1 page created, 1 page updated
- [[report-prefetch-service-2026-04-13]] — 2026-04-13 | Платформенный механизм кэширования отчётов (report-prefetch-service): Prefetch.List/Data/AppendBatch, микросессии, иерархия, сортировка+индексы, поиск, суммирование | 1 page created, 2 updated
- [[wasaby-infra-2026-04-12]] — 2026-04-12 | 13 Wasaby инфраструктурных docs (Хоттабыч/патчи/скрипты/права/cloud-ctrl/маршрутизация/дистрибутивы/стенды) | 8 pages created
- [[tests-new-readme-2026-04-11]] — 2026-04-11 | tests_new/README.md: unit test framework setup, three projects, test_manager.py, cmake/ninja, mocking patterns | 1 page created, 1 updated
- [[franchise-api-2026-04-10]] — 2026-04-10 | API Франшизы (FranchiseContract.* 12 methods) | 1 page created, 2 updated
- [[loyalty-db-franchise-2026-04-10]] — 2026-04-10 | База данных: loyalty DB schema changes for franchise (ВидЦеныЛица, ВидЦеныРасширение, ВидЦены, ВидКарты, CardType, Operation) | 1 page created, 1 updated
- [[loyalty-franchise-algorithms-2026-04-10]] — 2026-04-10 | Алгоритмы и процессы: БЛ Лояльности event subscriptions, franchise folder creation, FranchiseRole lifecycle | 1 page created, 2 updated
- [[franchise-loyalty-2026-04-10]] — 2026-04-10 | Описание: franchise loyalty business overview — Owner/Participant model, sync mechanism, unified customer base | 1 page created, 2 pages updated

---

- [[wasaby-bl-call-loop-user-switch-2026-06-04]] — 2026-06-04 | SBIS Forum: петля вызовов при смене пользователя в рамках одного аккаунта; решение: CreateMultitenantEndpointByClientId | 1 page created
- [[wasaby-cross-client-call-2026-06-04]] — 2026-06-04 | Форум wasaby.Backend: вызов БЛ-метода под другим клиентом+юзером без петли; AuthByClientAndUserId vs CreateMultitenantEndpointByClientId; Session.Set(icsSESSION_ID) | 1 page created, 1 updated

---

- [[db-conversion-2026-06-12]] — 2026-06-12 | 4 PDF: Описание + База данных + Организация кода + Параметры облака (Конвертация БД, Система обновлений) | 1 page created, 2 pages updated

---

## Диалоги SBIS — batch 2026-07-29 (10 источников)

- [[referral-crmthemeid-answers-2026-07-28]] (c-000221) — 2026-07-28 | CRMThemeId по реф. коду: Мусохранов/Ткачук закрывают 2 из 3 развилок (`@AdObject`, `null` при пустом результате), срок 4100/4200 | 1 page created, 1 question page updated
- [[bonus-report-getlist-limit-increase-2026-07-28]] (c-000216) — 2026-07-28 | Отчёт «Движение бонусов»: безопасность увеличения chunk-лимита `BonusOperationAdm.GetList` 100→1000/10000, курсорная пагинация + индекс | 2 pages created
- [[sabybank-rko-bug-partner-terminated-contract-2026-07-29]] (c-000214) — 2026-07-29 | РСС на РКО: расторгнутый договор виден клиенту → после правки инверсия (действующий не виден) | 2 pages created, 1 concept updated
- [[sabybank-rko-bug-applications-not-shown-sabynet-2026-07-28]] (c-000220) — 2026-07-28 | РСС на РКО: новые заявки не отображаются в ЛК SabyNet Владельца | 1 page created (+ агрегирующая [[SabyBank-RKO-Partner-Display-Bugs]])
- [[discount-card-type-settings-flaky-autotest-2026-07-29]] (c-000215) — 2026-07-29 | Флаки автотестов ДК: настройки типа не успевают прогрузиться; ожидание, что DWC починит — не подтверждено | 2 pages created
- [[dwc-card-events-rollout-status-2026-07-28]] (c-000218) — 2026-07-28 | Поручение включить `dwc_card` на всех — rollout не запланирован | 1 page created, 1 concept updated
- [[referral-leadperiodlist-koreshki-followup-2026-07-29]] (c-000213) — 2026-07-29 | Follow-up по отсутствию вознаграждений за 2026 в GetLeadPeriodList (стандартная программа, корешки без фичи) | 1 page created
- [[referral-loyalty-disk-access-task-closed-2026-07-28]] (c-000217) — 2026-07-28/29 | Закрытие 2-летней задачи: доступ к «Система лояльности» не влияет на реф. программу на СБИС.Диске | 1 page created
- [[partner-cabinet-source-mechanism-tz-2026-07-28]] (c-000219) — 2026-07-28 | ТЗ определения источника при заявке через ЛК партнёра — тонкий источник (1 реплика), задача на этапе Маркетинг | 1 page created
- [[zvonok-sveshnikov-timoshenko-stage-tracking-2026-07-29]] (c-000222) — 2026-07-29 | Звонок (ASR, низкая достоверность): статус сборки/переноса, контроль этапов задачи | 1 page created
- [[zvonok-tim-sveshnikov-referral-history-buttons-2026-07-29]] (c-000227) — 2026-07-29 | Звонок 1/2: постановка задачи «история изменений» по офферам/лидам/корешкам | 1 page created
- [[zvonok-tim-sveshnikov-mihel-referral-history-ui-2026-07-29]] (c-000228) — 2026-07-29 | Звонок 2/2 (+Витольд): дизайн-решение по кнопкам истории, вторая реф. сеть на бою | 1 page created, 1 entity created, 1 concept created
- [[referral-history-implementation-breakdown-2026-07-29]] (c-000230) — 2026-07-29 | Диалог: разбор реализации UI истории (3 пункта, распределение Тимошенко/Лебедева) | 1 page created, 1 entity created

## Add new sources here after each ingest.
