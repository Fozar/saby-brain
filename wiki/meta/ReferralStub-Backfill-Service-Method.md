---
type: decision
address: c-000206
title: "CreateStubsForExistingLeads — миграция корешков как служебный метод вместо ВНР"
created: 2026-07-23
updated: 2026-07-31
decision_date: 2026-07-23
status: active
tags:
  - price-formation
  - referral
  - sabybank
  - migration
  - implementation
related:
  - "[[Migration-Console-First-Testing-Pattern]]"
  - "[[SabyBank-RKO-Referral]]"
  - "[[ReferralProgram-Stub-Implementation]]"
  - "[[ReferralStub-TargetAction-Pattern]]"
  - "[[zvonok-musohranov-timoshenko-2026-07-22]]"
  - "[[createstubsforexistingleads-bug-4100-2026-07-30]]"
  - "[[Земцова-Анастасия]]"
---

# CreateStubsForExistingLeads — миграция корешков как служебный метод вместо ВНР

Navigation: [[SabyBank-RKO-Referral]] | [[Migration-Console-First-Testing-Pattern]]

Реализация [[Migration-Console-First-Testing-Pattern|console-first паттерна]] на задаче №06155143 («Создать корешки для старых заявок по реферальным программам»). Единый ВНР-скрипт переработан: ядро миграции вынесено в служебный БЛ-метод по **одной** реферальной программе, ВНР сведена к перебору программ.

---

## Решение

**Было:** вся логика в `LoyaltyReferral/developer_script.py` — ВНР ходила по всем стандартным (не SabyBank) реферальным программам аккаунта и создавала корешки. Отладить можно было только прогоном ВНР целиком.

**Стало:** `ReferralProgram.CreateStubsForExistingLeads(ProgramId, DryRun)` — служебный метод (`is_service=1`), одна программа за вызов, вызывается из консоли. ВНР осталась тонкой обёрткой: выбирает программы аккаунта и в цикле зовёт метод, агрегируя статистику в лог/Redis; ошибка по одной программе не роняет остальные.

Файлы (репозиторий `price-formation`, ветка задачи):
- `www/service/Модули/LoyaltyReferral/loyaltyreferral/referralprogram/referralprogram/create_stubs_for_existing_leads.py` — метод
- `ReferralProgram.orx` — декларация (`access_mode=0`, `returns=RECORD`, `call_timeout=600000`, `category=Stub`)
- `developer_script.py` + `DeveloperScript.orx` — тонкая ВНР

## Контракт метода

Вход: `ProgramId` (`@ВидЦены`), `DryRun` (BOOLEAN, необязательный).

Выход — запись:

| Поле | Смысл |
|------|-------|
| `ProgramId` | идентификатор программы |
| `LeadsFound` | сколько сделок просмотрено |
| `StubsCreated` | сколько корешков создано (при `DryRun` — сколько было бы) |
| `SkippedDuplicates` | корешок по сделке уже есть (анти-дубль по `OperationId`) |
| `SkippedNoCard` | источник сделки не сопоставлен с картой участника |
| `Errors` | количество ошибок |
| `Stubs` | RecordSet: `LeadId`, `OperationId`, `CardId`, `LinkType`, `Bonus` |

> [!key-insight] `Stubs` и `DryRun` — это и есть механика проверки
> `DryRun=true` ничего не пишет в БД и возвращает состав будущих корешков. Возврат `Stubs` даёт то, чего требовал [[Мусохранов-Андрей-Владиславович|Мусохранов]] — сверку **по количеству и идентификаторам**, а не «на глаз»: dry-run → сверка со `SELECT` по `ВидЦеныДокумент` → запись → повторный вызов должен дать `StubsCreated = 0` и всё в `SkippedDuplicates`.

## Механика миграции

Сделки программы читаются постранично (`_PAGE_SIZE = 100`) через `sbis.EndPoint('crm-service').SourcesSales.GetRawDocs` — тот же путь вызова ЦРМ, что в боевом реестре сделок (аргумент Тимошенко против опасения «ЦРМ вернёт что попало»). Три прохода по статусам, каждый маппится в `ТипСвязи` корешка:

| Статус сделки (`_LeadStatus`) | `LinkType` |
|---|---|
| `COMPLETED_SUCCESS` | `REQUEST_SUCCESS` |
| `COMPLETED_FAILED` | `REQUEST_FAILURE` |
| `IN_WORK`, `NEW` | `REQUEST_IN_PROGRESS` |

Атрибуты корешка собираются как в [[ReferralProgram-Stub-Implementation|CreateStub]] (номер, даты, описание, контакты из `SourcesSales.GetLeadInfoV2`, ИНН/КПП), `EffectiveDate` = дата фазы для любого статуса, `Бонусы` переносятся из существующих строк начислений. `OperationId` = `ИдентификаторДокумента` (UUID) сделки — он же ключ идемпотентности.

Запись — пачками по 500, каждая пачка в своей `sbis.CreateTransaction(READ_COMMITTED, WRITE)`: прерванный прогон дозапускается, уже вставленное отсеется по `OperationId`.

## Права

Метод добавлен только в служебную роль `PF-Discount` (`ReferralProgram.uax`), **не** в публичную `PF-ReferralLead-PUB` — иначе миграцию мог бы запустить пользователь с правами «Маркетинг».

## Порядок сдачи

1. Доброска метода (подзадача поручения №06155143) на стенд.
2. Обкатка из консоли на **одном** оффере: dry-run → сверка в БД → запись → проверка идемпотентности.
3. Только после этого — запуск ВНР по всем стандартным программам и передача [[Настя-QA|Насте]] с явным сценарием проверки БД.

## Открытые пункты

- [ ] Выбрать программу-фикстуру для обкатки (нужно несколько сделок, часть с начисленным вознаграждением)
- [ ] Юнит-тестов на метод нет — сознательно: миграция одноразовая, проверка идёт через dry-run на реальных данных