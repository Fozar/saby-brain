---
type: question
address: c-000212
title: "Метод получения CRMThemeId по реф. коду партнёра — открытые развилки"
created: 2026-07-28
updated: 2026-07-29
tags:
  - price-formation
  - referral-program
  - loyalty-referral
  - autoregistration
  - open-question
status: open
related:
  - "[[ReferralProgram-Data-Model]]"
  - "[[ReferralProgram-Module]]"
  - "[[LoyaltyReferral-Module-Extraction]]"
  - "[[Wasaby-BL-Call-Loop-Pattern]]"
---

# CRMThemeId по реф. коду партнёра (задача №07164990)

Задача [№07164990](https://online.sbis.ru/opendoc.html?guid=019f6a41-14ec-7092-b0ac-98e0b96f8c4a&client=3) (автор и ответственный — Маранов В.Ф., срок 12.01.2027, оценка 0.5 дня): *«реализовать метод для получения целочисленного кода темы отношений по реф коду партнера»*. Родитель — проект **«Авторегистрация для Alfa ID и СберБизнес»** (doc_id=565654086, объём 123 ч/дн, отв. Краснокутский В.В.), план работ «Система лояльности», июль 2026.

Исполнитель — [[Тимошенко А.А.]]. На 2026-07-28 постановщикам заданы уточняющие вопросы, ответа нет; реализация не начата.

## Что такое «тема отношений» в рефералке

`CRMThemeId` — целочисленный идентификатор темы отношений CRM, хранится в атрибутах реф. программы:

```
ВидЦены.Атрибуты -> 'ReferralProgram' ->> 'CRMThemeId'   (INTEGER)
```

- Маппинг: `ReferralProgramField.CRM_THEME_ID` и `extract_rp_record_data` — `core.py:37,113`; свойство `ReferralProgram.theme_id` — `core.py:182`.
- Единственный боевой потребитель: `create_lead.py:148` кладёт `theme_id` в поле `Регламент` записи, которая уходит в `sbis.CRMLead.insertRecord`. То есть тема отношений определяет, в какой регламент CRM ляжет сделка.
- В API объекта поле уже отдаётся как `CRMThemeId` в `Read`/`GetList`/`Create`/`Update` (`ReferralProgram.orx`, ~6 объявлений).

Всё это после [[LoyaltyReferral-Module-Extraction|выделения модуля]] живёт в `www/service/Модули/LoyaltyReferral/`, пакет `loyaltyreferral/referralprogram/referralprogram/`.

## Путь от реф. кода до CRMThemeId

Разворачивается по уже существующей модели ([[ReferralProgram-Data-Model]]):

```
utm_rfcid = {ClientID владельца}_{@AdObject партнёрского источника}
                                        │
Карта  (Атрибуты->'ReferralProgram'->>'AdObject' = @AdObject)
  └── Эмиссия ──> ВидЦеныВидКарты.ВидКарты
                    └── ВидЦены = реф. программа
                          Атрибуты->'ReferralProgram'->>'CRMThemeId'
```

Готовые SQL-шаблоны этого джойна (в обратную сторону — от программы+партнёра к карте) уже лежат в `core.py:495-561`: `SQL_GET_REFERRAL_CODE_SOURCE_IDS`, `SQL_GET_REFERRAL_CODE_IDENTIFIER`, `SQL_GET_REFERRAL_CODE_CARD`. Новый метод — тот же джойн, но точка входа `Карта.Атрибуты->AdObject` вместо пары (`ВидЦены`, `Лицо`).

Сборка кода — `compute_referral_link` (`core.py:564`), `referral_code = f'{account_number}_{source_id}'`, где `account_number = sbis.Session.ClientID()` **владельца** программы (`get_referral_link.py:42`).

## Что даёт ТЗ проекта (и чего не даёт)

Из вложения «Техническое задание» проекта 565654086:

- Регистрационный флоу зовёт `ReferralProgram.CreateLeadByPartner(AgentGroupId, ReferralProgramId, FeedbackForm)` — сделка создаётся **до** создания аккаунта, её `@Документ` уходит в `Billing.CreateAccount` / `PromoAccount.Connect` как `CRMLead`.
- Идентификаторы бизнес-группы и реф. программы — **фиксированные для каждого партнёра**, лежат в параметрах облака / настройках провайдера на `external-access-provider` (`PartnerId`, `AgentGroupId`, `Application.docs.ReferalId`).
- В `Billing.CreateAccount` и `PromoAccount.Connect` есть строковый параметр **`КодПартнера`** — но в price-formation такого понятия нет (grep по репозиторию пуст), это биллинговый код точки продаж, не обязательно равный `utm_rfcid`.
- Метода «по реф. коду → тема отношений» в ТЗ **нет** — задача добавлена позже, поверх ТЗ.

Репозитории проекта: `billing/billing`, `middleware/auth`, `middleware/external-access-provider`.

## Открытые вопросы (заданы, ответа нет)

1. **Формат входа.** Что именно называется «реф кодом партнёра»:
   - строка `utm_rfcid` целиком (`3_25770347`), метод сам её парсит;
   - только `@AdObject` (INTEGER);
   - `Карта.Идентификатор` (UUID) — то, чем оперирует `create_lead.py:126` через `get_source_by_ext_id`.
2. **Контекст вызова.** Зовущий (auth / online-reg / external-access-provider) уже находится в аккаунте владельца программы — или метод сам должен уйти туда через `multitenancy.CreateMultitenantEndpointByClientId` по первой части `utm_rfcid`, как это делает `get_referral_link_by_partner.py:25` ([[Wasaby-BL-Call-Loop-Pattern]])? От ответа зависит, нужна ли пара методов `GetX` / `GetXByPartner` по образцу `GetReferralLink` / `GetReferralLinkByPartner`.
3. **Пустой результат.** Кода нет / у программы `CRMThemeId` пуст — возвращать `0`/NULL или кидать `sbis.Warning` (как `create_lead.py:116`)? Для регистрационного флоу падение нежелательно.

## Права (куда добавлять метод)

`ReferralProgram.uax`: читающие методы объявлены в `PF-Discount-RO` (служебная) и `PF-ReferralLead-PUB` (публичная роль «Реферальные программы», `access="allowed"`). Внешний вызов из auth-контура, вероятно, потребует ЮАКС-уровня — уточняется вместе с вопросом 2.

## Открытые пункты

- [ ] Дождаться ответа Маранова В.Ф. по формату входа и контексту вызова
- [ ] После ответа — тех. решение и реализация (новый файл в `loyaltyreferral/referralprogram/referralprogram/` + объявление в `LoyaltyReferral/ReferralProgram.orx` + `.uax`)
- [ ] Тесты в `tests_new` (моки — `TestLoyalty.orx`)
