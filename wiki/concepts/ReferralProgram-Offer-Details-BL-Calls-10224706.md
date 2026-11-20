---
address: c-000284
type: concept
title: "Оптимизация вызовов БЛ в детализации офферов — №10224706"
created: 2026-11-09
updated: 2026-11-18
status: developing
related:
  - "[[Loyalty-November-2026-WorkPlan]]"
  - "[[zvonok-matyushev-timoshenko-plan-2026-11-09]]"
  - "[[ReferralProgram-RefDealsConvert-Feature]]"
---

# Оптимизация вызовов БЛ в детализации офферов

## Задача

№10224706: https://online.sbis.ru/opendoc.html?guid=01a16285-8faa-74b3-ac75-65cf88cd21c3&client=3

Ноябрьский план №606980697, пункт `634624790`. Срок пункта: **2026-11-28**; срок карточки: **2026-11-28**. Плановая оценка: 1.5 ч (как возвращено СБИС, не переоценивалась).

Веха: **27.1100** (подтверждено Михелем и Мусохрановым 18.11.2026; локально открыт чистый `rc-27.1100`).

## Где остановились

18.11.2026: контекст собран, код изучен, ждутся ответы на уточняющие вопросы (scope, имя поля, место работы). Реализация не начата.

Финальная договорённость из переписки (Михель, 18.11): «сделаем вызов GetPersonBGRoleInAgents неблокирующим — вызываем GetPersonBGRoleInAgents, результат возвращаем в отдельном поле, и всё. Остальные данные возвращаем всегда, даже если пользователь не участник бизнес группы». Возражение Мусохранова (рефералка без сабигета) снимается именно неблокирующим вариантом: Read не отказывает, а отдаёт пустое поле.

## Постановка и критерий

По анализу в карточке: убрать лишний ReferralProgram.GetPartnerList из фильтра партнёров на странице «Лиды»; перенести получение роли PriceFormation.GetPersonBGRoleInAgents внутрь ReferralProgram.Read; вызывать GetLeadPeriodList параллельно с Read, беря ID из URL. На странице «Партнёры» также убрать зависимость GetLeadPeriodList от Read. SiteNavigation.ListNew нужен; зависимости списков от периода и роли сохраняются.

## Что выяснено по коду

- Наша часть (бэкенд): только ReferralProgram.Read. Файл `www/service/Модули/LoyaltyReferralOnline/loyaltyreferralonline/referralprogram/referralprogram/read.py` — формат ответа динамический (метод уже динамически кладёт Link, PhotoRecord, ClientId, AnnouncementIdList через Put), править .orx не нужно.
- PriceFormation.GetPersonBGRoleInAgents — инлайн-метод в `PriceFormation.Online/Core.orx`: берёт `ParticipantGroupId` из `sbis.NavConfiguration.CurrentAppWithConfig()`, при отсутствии — WarningMsg и None; иначе `sbis.EndPoint('socnet-service').BusinessGroup.GetPersonRoleInAgents(group_id)`. Возвращает запись с полем `Role` (UUID роли: админ/модератор/участник).
- Фронт сейчас читает из ответа только `Role` (`client/LoyaltyOnline/ReferralLeadNew/RoleInAgentsFactory.ts`): `role`, `hasRole = !!role`, `hasEditPermission = админ или модератор`.
- Тесты: `tests/tests_loyaltyreferralonline/referralprogram/referralprogram/read.py` (класс Read, TransactionTestCase). Мокировать роль можно как `mock.patch` на `sbis.PriceFormation.GetPersonBGRoleInAgents` — по аналогии с уже существующим моком `sbis.AgentContract.ContractorList` в setUp.

## Решения и почему

- Разделить бэкенд-часть роли в Read и фронтенд-часть оптимизации запросов. Не убирать необходимые проверки прав и периода.
- Предложение по контракту: в ответ Read добавить поле `PersonBGRole` (ftRECORD — та же запись, что возвращает GetPersonBGRoleInAgents, читается `result.get('PersonBGRole')?.get('Role')`). Неблокирующе: исключение/None → поле пустое, остальные данные отдаются всегда.

## Открытые вопросы

- Scope: только бэкенд (Read + поле), фронт у Михеля отдельно?
- Имя и формат поля (`PersonBGRole`-record vs плоское строковое поле).
- Где работаем: ветка в текущей папке (на rc-27.1100) или отдельный worktree.

## Roadmap

- [ ] Согласовать контракт поля Read с Михелем/Лебедевой.
- [ ] Перенести получение роли и убрать лишние ожидания/вызов.
- [ ] Проверить страницы «Лиды» и «Партнёры» для разных ролей и сохранённого периода.

## Ссылки

- План: [[Loyalty-November-2026-WorkPlan]].
- Встреча: [[zvonok-matyushev-timoshenko-plan-2026-11-09]].
- Извлечённые поля СБИС: [.raw/captured/4ea60b369322e83b8ab05e1f92cfaae2c15c0ac12653c5d7382b81b69e465b7b.json](../../.raw/captured/4ea60b369322e83b8ab05e1f92cfaae2c15c0ac12653c5d7382b81b69e465b7b.json).
- MR, ветка и worktree: при ingest не проверялись.

## Реализация 18.11.2026

Пользователь согласовал техрешение; scope — только договорённость с Витольдом.
В ветке `27.1100/bugfix/aatimoshenko/10224706` добавлено поле PersonBGRole и получение роли с обработкой исключения.
Добавлены три теста: роль получена, None, исключение. Фронт и существующие проверки доступа не менялись.
Pylint: рабочий код без замечаний, в тестах 6 замечаний на прежних строках; git diff --check без ошибок.
Тесты не запущены: сборка основной папки SDK 266100, ветка требует 271000.
Нужна полная сборка online пользователем, затем прогон класса Read. Коммитов и MR нет.

## MR и исправление сборки 18.11.2026

После попытки сборки SDK 271000 jinnee отклонил тип RECORD у PersonBGRole.
В обеих перегрузках исправлен тип на RECREFERENCE по образцу PhotoRecord; Python остаётся ftRECORD.
В контракт добавлено недостающее PriceDescription после PricePerVisitor. Обе перегрузки содержат 26 полей.
Проверены XML, порядок и отсутствие дублей; git diff --check чисто, pylint рабочего кода 10/10.
Повторная сборка и тесты после исправления не запускались, нужна проверка SDK 271000.
Пользователь разрешил коммит и пуш. Коммит `2eda819b05`, ветка `27.1100/bugfix/aatimoshenko/10224706` запушена.
Документ MR: https://online.sbis.ru/opendoc.html?guid=01a1ed89-86f1-704e-b3e1-0bcfdeaaa22a&client=3
GitLab !154708 → rc-27.1100, !154709 → rc-27.1200; обе ветки назначения проверены по API.
Инструмент создания назвал веху «26.6100: вынесенные ошибки», но фактические цели MR соответствуют 27.1100/1200.

## Асинхронное получение роли 18.11.2026

По предложению пользователя запрос роли запускается через FutureInvoke в начале Read,
результат забирается через get в конце. Пользователь выбрал два try-блока прямо в Read,
без helper-функций и контекстного менеджера. Ошибки запуска и ожидания не прерывают ответ.
В тестах мокается только BLObject.FutureInvoke, а не конструктор BLObject:
подмена конструктора ломала обычные БЛ-вызовы, в том числе PriceFormation.InCloud.
Проверены порядок start → чтение программы → фото → get и ошибки обеих стадий.
SDK сборки совпал с 271000; 11 тестов Read OK, 387 тестов пакета referralprogram/referralprogram OK.
Pylint: новое R0915 (56 операторов при лимите 50) принято как известное замечание,
подавление не добавлялось; ещё 6 прежних замечаний в тестах. git diff --check чисто.
Коммит обновлён amend до 0602ef4b68 и запушен force-with-lease в те же MR !154708–!154709.
Полная online suite не запускалась.
