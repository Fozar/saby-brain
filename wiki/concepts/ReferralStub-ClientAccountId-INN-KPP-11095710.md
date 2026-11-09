---
type: concept
title: "Идентификатор аккаунта клиента и реквизиты в корешке заявки (№11095710)"
status: testing
updated: 2026-11-09
related:
  - "[[SabyBank-RKO-Referral]]"
  - "[[ReferralProgram-Stub-Implementation]]"
---

# Идентификатор аккаунта клиента и реквизиты в корешке заявки

## Задача
Ошибка на стенде №11095710, веха 26.5134, срок 12.11.2026.
https://online.sbis.ru/opendoc.html?guid=01a1bf94-d853-7192-8491-e6631799aa44&client=3

## Где остановились
09.11: реализована поддержка ClientAccountId (идентификатор аккаунта клиента в облаке) в методах работы с корешками ReferralProgram.CreateStub и ReferralProgram.ReadStub, обновлены контракты в ReferralProgram.orx. Создан коммит 55c4cd9e31, отправлена ветка 26.5134/bugfix/aatimoshenko/11095710. Оформлен документ Merge request [01a1bfa7](https://online.sbis.ru/opendoc.html?guid=01a1bfa7-9cc9-755d-ab9e-f84565868f3b&client=3) (doc_id 636046675), GitLab !153816–!153824. 44 теста CreateStub и ReadStub OK, 452 теста пакета referralprogram OK.

## Что выяснено по коду
- В методе создания корешка ReferralProgram.CreateStub поля Inn и Kpp уже были предусмотрены, но со стороны интеграции банка (модуль buh/money, bank_applications/referral.py) они не передавались при вызове CreateStub.
- Также для идентификации клиента в карточке заявки потребовалось передавать идентификатор аккаунта клиента в облаке (ClientAccountId), чтобы не ограничиваться только именем.
- Поле ClientAccountId добавлено опциональным в Request метода CreateStub с валидацией типа, сохраняется в атрибуты корешка в БД (ВидЦеныДокумент.Атрибуты), а также извлекается и возвращается в ReadStub.

## Решения и почему
- Поле названо ClientAccountId (не ClientId), чтобы исключить путаницу с существующим параметром Partner.ClientId (аккаунт банка/партнёра).
- Тип поля — INTEGER (int | None), опциональное, с сохранением полной обратной совместимости.
- Поле возвращается в обеих перегрузках ReferralProgram.ReadStub для отображения в карточке заявки.

## Roadmap
- [x] Проверить контракт CreateStub и ReadStub на наличие полей ИНН/КПП/аккаунта.
- [x] Согласовать имя поля (ClientAccountId) и возврат в ReadStub.
- [x] Подготовить изолированную ветку 26.5134/bugfix/aatimoshenko/11095710 от origin/rc-26.5134 в ворктри.
- [x] Реализовать сохранение ClientAccountId в CreateStub и чтение в ReadStub (TDD, тесты зеленые).
- [x] Обновить контракт ReferralProgram.orx.
- [x] Создать коммит и оформить документ Merge request в СБИС с каскадом GitLab !153816–!153824.

## Ссылки
- Ошибка: https://online.sbis.ru/opendoc.html?guid=01a1bf94-d853-7192-8491-e6631799aa44&client=3
- Документ MR в СБИС: https://online.sbis.ru/opendoc.html?guid=01a1bfa7-9cc9-755d-ab9e-f84565868f3b&client=3
- GitLab MR: !153816–!153824
- Ветка: 26.5134/bugfix/aatimoshenko/11095710
