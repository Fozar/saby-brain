---
type: concept
title: "ФИО контактного лица не попадает в корешок из ЛК партнёра (№11026436)"
created: 2026-11-03
updated: 2026-11-03
tags:
  - price-formation
  - referral
  - bugfix
status: developing
related:
  - "[[ReferralProgram-Stub-Implementation]]"
  - "[[ReferralStub-ClientName-Phone-Transition-10266626]]"
  - "[[ReferralProgram-RefDealsConvert-Feature]]"
  - "[[Тимошенко А.А.]]"
---

# ФИО контактного лица не попадает в корешок из ЛК партнёра (№11026436)

## Задача

Ошибка на стенде №11026436 (SMOKE автотесты, «Ошибка на стенде», веха 26.5127, срок 05.11.2026):
https://online.sbis.ru/opendoc.html?guid=01a19b8a-9005-7863-abda-49ad75c963ce&client=3
Партнёр в ЛК открывает заявку (fix, «Оффер СО ВСЕМ», клиент «Соляр, АНО»): в корешке есть телефон
контактного лица, а ФИО пустое. Михель при переназначении: «`ReferralProgram.GetStubByPartner` не вернул
`ContactName`». Куимова просит ускорить — смоки не скипаются; просят включить в веху 26.5217.

## Где остановились

03.11: фикс и регрессионные тесты готовы в ветке `26.5127/bugfix/aatimoshenko/11026436`
(worktree `~/.local/share/opencode/worktree/642bc6/11026436`). Класс `CreateStubByLead`: до фикса
2 новых теста красные (`None != 'Соня'`, `None != 'Петрова Анна Ивановна'`), после фикса 15/15 OK,
pylint 10/10. Коммит `4e59603ea1`, MR документ [01a1a14c], GitLab !153534–!153540, переведено на проверку.

## Что выяснено по коду

- Клиентский лог (`fix-partners-02-11-2026_14-15-04-192.sbislogz`): заявка создана вызовом
  `ReferralProgram.CreateLeadByPartner`, в `FeedbackForm.ContactData` пришло `{Name: 'Соня', Phone: '+7 (926) 112-14-14'}`.
  Ответ `GetStubByPartner`: `ContactName: null`, `ContactPhone: +7 (926) 112-14-14`, `ClientName: 'Соляр, АНО'`.
- Серверные логи fix (uuid запроса `0a8c414f-7ae4-5e9c-a200-023511badbb1`):
  - штатный путь `_create_stub_for_lead` → `ReferralProgram.CreateStub` вызван с `ContactName: 'Соня'`,
    но получил `Warning: Корешок с идентификатором ... уже существует!` (create_stub.py:157) — корешок успели
    завести раньше через `ReferralProgram.HandleSourceChanged` (локальное событие `salessources.source_changed`
    от `CRMLead.insertRecord`, см. `on_event.py:24`).
  - в ответе `SourcesSales.GetLeadInfoV2` строка `CRMPreload.List` такая:
    `{ContactType: 'assignee', Contact: null, RowTitle: 'Соня', Assignee: {ФИО: 'Соня', Имя: 'Соня', Фамилия: ''}, AssigneeContacts: [{Type: 10, Value: '+7 (926) 112-14-14'}]}` —
    поля `FullName` в строке нет вообще.
  - `get_lead_contacts` (`loyaltyreferral/referralprogram/referralprogram/stub_helpers.py:119` в линии 26.51,
    `loyaltyreferral/core/stub.py:119` в 26.61) брал имя только из `FullName`, поэтому имя терялось,
    а телефон находился в `AssigneeContacts`. Отсюда «телефон есть, ФИО нет».
- Подтверждение, что корешок создал именно обработчик: в корешке `Description` = примечание сделки
  («Клиент: ... Партнёр: ...»), как пишет `create_stub_by_lead`, а не комментарий формы («123456»).
- Тот же хелпер используют `ReferralProgram.CreateStubsForExistingLeads` (`create_stubs_for_existing_leads.py:285`),
  `create_stub_by_lead` и `load_lead_contacts` — фикс в одном месте закрывает и ВНР по старым сделкам.

## Решения и почему

- Почему контакт в CRM имеет тип «представитель» (`assignee`), а не «контактное лицо»: `КонтактноеЛицо`
  формы создаётся CRM как представитель клиента (в логе — `_ClientAssigneeParser`), поэтому в `CRMPreload`
  ФИО лежит в `Assignee`, а не в `FullName`.
- Фикс: новый хелпер `_get_contact_name` — `FullName`, иначе `Assignee.ФИО`, иначе сборка из
  `Фамилия Имя Отчество`. `RowTitle` не используем: там может оказаться телефон безымянного контакта.
- Гонку `CreateLead` / `HandleSourceChanged` не трогаем: она задумана, дубль отсекает `CreateStub`,
  и после фикса оба пути пишут корректные контакты.

## Окружение стенда 26.51 (для прогона тестов)

- `py -3` указывал на Python 3.12, а SDK-шный test_framework на 3.12 падает (`ssl.match_hostname` убран,
  уходит в `backports`, которого нет). Лечится `%LOCALAPPDATA%\py.ini` → `python3=3.11-32` (старый файл рядом
  как `py.ini.bak`).
- Юнкция `D:\dev\price-formation` смотрела на `pf-26.61`; `Service.s3srv` тестового проекта 26.51 ищет модули
  по относительному пути `./../../../../../price-formation/...`, поэтому деплой не находил модули. Для прогона
  юнкция переставлялась на `pf-26.51` и возвращена обратно после.
- Стенд нужно держать живым: `tm -project online -restart=True` в интерактивном режиме ждёт Enter, а при EOF
  падает и удаляет тестовую БД. Обход — подать в stdin долгий процесс:
  `python -c "import time; time.sleep(7200)" | pwsh -File tm.ps1 -project online -restart=True`.
  Потом `py_tests_runner.py` из каталога `run` берёт имя БД из `sbis-rpc-service.ini`.

## Открытые вопросы

- Нужно ли задним числом править уже заведённые корешки на fix (для смок-теста) или достаточно новых.

## Roadmap

- [x] Анализ по клиентскому и серверному логам fix
- [x] Фикс `get_lead_contacts` + 2 регрессионных теста, pylint 10/10
- [x] Прогон: 2 красных до фикса, 15/15 зелёных после
- [x] Коммит `4e59603ea1`, MR [01a1a14c], GitLab !153534–!153540

## Ссылки

- Ошибка: https://online.sbis.ru/opendoc.html?guid=01a19b8a-9005-7863-abda-49ad75c963ce&client=3
- Стенд: https://fix-partners.saby.ru/190e9168-da54-4367-b855-58f7e3a212de/page/participant-deals?id=19&backButtonId=participant-offers
- Код: `stub_helpers.py` (`get_lead_contacts`), `create_lead.py`, `handle_source_changed.py`
- MR: https://online.sbis.ru/opendoc.html?guid=01a1a14c-2023-78f2-9625-f2e24cf2f02c&client=3
- Ветка: `26.5127/bugfix/aatimoshenko/11026436`, worktree `~/.local/share/opencode/worktree/642bc6/11026436`
- Похожая ошибка по клиенту: [[ReferralStub-ClientName-Phone-Transition-10266626]]
