---
type: decision
address: c-000013
title: "ReferralProgram Stub Implementation — CreateStub, UpdateStub, ReadStub"
created: 2026-05-08
updated: 2026-06-15
decision_date: 2026-05-08
status: active
tags:
  - price-formation
  - referral
  - sabybank
  - rko
  - implementation
related:
  - "[[SabyBank-RKO-Referral]]"
  - "[[ReferralProgram-Module]]"
  - "[[Loyalty-Database-Schema]]"
---

# ReferralProgram Stub Implementation — CreateStub, UpdateStub, ReadStub

Navigation: [[SabyBank-RKO-Referral]] | [[ReferralProgram-Module]]

Реализация трёх BL-методов для работы с корешками заявок на РКО в рамках [[SabyBank-RKO-Referral]]. CreateStub и UpdateStub вызываются банком-партнёром; ReadStub — клиентом (кабинет партнёра).

---

## Архитектурное решение: 3 отдельных метода

**`ReferralProgram.CreateStub`** — банк регистрирует факт получения заявки (первый вызов по RequestUUID).
**`ReferralProgram.UpdateStub`** — банк обновляет статус заявки (последующие вызовы).
**`ReferralProgram.ReadStub`** — чтение корешка по RequestUUID; возвращает данные заявки и историю событий.

**Почему Create и Update раздельны:** CreateStub принимает `ProgramId` + `Partner` (нужны для поиска карты участника `ВидЦеныВидКарты → Карта`). UpdateStub ищет только по `RequestUUID`. Объединять бессмысленно: разная семантика, разный обязательный набор параметров.

---

## Бизнес-сценарии

| # | Сценарий | Метод | Status | StatusDate |
|---|---------|-------|--------|------------|
| 1 | Банк получил заявку и берёт в обработку | CreateStub | 10 | NULL |
| 2 | Банк получил заявку и сразу вынес решение | CreateStub | 15 / 20 | дата решения |
| 3 | Банк одобрил/отклонил заявку после проверки | UpdateStub | 15 / 20 | дата решения |
| 4 | Банк отменил решение, вернул в обработку | UpdateStub | 10 | NULL (затереть) |

---

## Правило StatusDate

Применяется в обоих методах:

- `Status == 10` (в работе) → `EffectiveDate = NULL` всегда, даже если банк передал дату
- `Status == 15 / 20` (завершён) → `EffectiveDate = переданное значение`

Поле называется `StatusDate` в API (параметр Request), хранится в колонке `EffectiveDate` таблицы `ВидЦеныДокумент`.

`ДатаВремя` (дата создания заявки) заполняется только при создании через `CreatedAt` и никогда не изменяется.

---

## Хранение полей

Таблица `ВидЦеныДокумент`:

| Данные | Колонка |
|--------|---------|
| Status (ТипСвязи) | `ТипСвязи` INT |
| StatusDate | `EffectiveDate` TIMESTAMPTZ |
| CreatedAt | `ДатаВремя` TIMESTAMPTZ |
| RequestUUID | `OperationId` UUID |
| ClientName, Description, ContactName, ContactPhone, ContactEmail, StatusDescription | `Атрибуты` JSONB |

**Решение:** `Status` и `StatusDate` не дублируются в `Атрибуты` — они хранятся в выделенных колонках `ТипСвязи` и `EffectiveDate`. ReadStub читает их оттуда напрямую.

---

## ReadStub — структура ответа

```
RequestUUID    str      UUID заявки
ContractorId   int      идентификатор партнёра (@Лицо)
ContractorName str      название партнёра
ClientName     str      имя клиента заявки
Description    str|None описание заявки
ContactName    str|None имя контактного лица
ContactPhone   str|None телефон контактного лица
ContactEmail   str|None email контактного лица
Events         RecordSet список событий заявки
```

### Events RecordSet

Поля: `Статус` (INTEGER), `Дата` (DATE), `НазваниеПерехода` (STRING).

Правила формирования:
- Всегда есть элемент 1: `Статус=10`, `Дата=ДатаВремя::DATE`, `НазваниеПерехода=sbis.rk('Заявка создана')`
- Если `ТипСвязи != 10`: добавляется элемент 2 из `ТипСвязи`, `EffectiveDate::DATE`, `Атрибуты->>'StatusDescription'`
- Итого: 1 элемент при статусе 10, 2 элемента при финальном статусе 15/20

`sbis.rk('Заявка создана')` — локализуемая строка; английский перевод `"Application created"` добавлен в `lang/en.json`.

---

## Реализация

### Файлы

| Файл | Описание |
|------|---------|
| `priceformationonline/referralprogram/referralprogram/create_stub.py` | BL: CreateStub |
| `priceformationonline/referralprogram/referralprogram/update_stub.py` | BL: UpdateStub |
| `priceformationonline/referralprogram/referralprogram/read_stub.py` | BL: ReadStub |
| `PriceFormation.Online/ReferralProgram.orx` | Декларации методов |
| `PriceFormation.Online/lang/en.json` | Перевод 'Заявка создана' |
| `priceformationonline/core/price_entity_sale_doc.py` | `LinkType` константы |
| `tests/.../referralprogram/create_stub.py` | Тесты CreateStub |
| `tests/.../referralprogram/update_stub.py` | Тесты UpdateStub |
| `tests/.../referralprogram/read_stub.py` | Тесты ReadStub |

### LinkType константы

```python
REQUEST_IN_PROGRESS = 10  # заявка в работе
REQUEST_SUCCESS = 15       # успешно завершена
REQUEST_FAILURE = 20       # завершена с ошибкой
```

### Валидация Status

`one_of([LinkType.REQUEST_IN_PROGRESS, LinkType.REQUEST_SUCCESS, LinkType.REQUEST_FAILURE])` из `assert_param`. Блокирует любые значения кроме 10/15/20.

### SQL CreateStub

```sql
INSERT INTO "ВидЦеныДокумент" (
    "ВидЦены", "Карта", "ДатаВремя", "OperationId", "ТипСвязи", "Атрибуты", "EffectiveDate"
) VALUES ($1::INT, $2::INT, $3::TIMESTAMPTZ, $4::UUID, $5::INT, $6::JSONB, $7::TIMESTAMP WITH TIME ZONE)
```

`Атрибуты` JSONB: `RequestUUID`, `CreatedAt` (ISO), `ClientName`, `Description`, `ContactName`, `ContactPhone`, `ContactEmail`, `StatusDescription`.

### SQL UpdateStub

```sql
UPDATE "ВидЦеныДокумент"
SET
    "ТипСвязи" = $2::INT,
    "EffectiveDate" = $3::TIMESTAMP WITH TIME ZONE,
    "Атрибуты" = "Атрибуты"
        || CASE WHEN $4::TEXT IS NOT NULL THEN jsonb_build_object('ClientName', $4) ELSE '{}'::JSONB END
        || CASE WHEN $5::TEXT IS NOT NULL THEN jsonb_build_object('StatusDescription', $5) ELSE '{}'::JSONB END
WHERE "OperationId" = $1::UUID
RETURNING TRUE
```

### SQL ReadStub

Строковые поля из `Атрибуты` кастуются явно `::TEXT`. `Status` и `StatusDate` — из колонок `ТипСвязи` и `EffectiveDate::DATE`.

Дубль по `OperationId` при CreateStub → `sbis.Warning`. Несуществующий UUID при UpdateStub/ReadStub → `sbis.Warning`.

---

## Ревью MR (Мусохранов, 2026-06-24)

> [!key-insight] Риск регрессии: ранний корешок и старые рефералки
> Исторически корешок создавался только при *завершении* сделки. `CreateLead → CreateStub` создаёт его при *создании* (статус 10). Виджеты и реестры старой рефералки могут показывать этот корешок там, где ожидаются только завершённые — нужно явно покрыть регрессию.

**Запрошенные действия:**
1. Написать сценарии тестирования в явном виде в MR/задаче (оффер → метод → ожидаемый результат)
2. Добавить регрессионный сценарий: корешок создан в статусе 10 → сделка прошла все этапы → проверить виджеты, реестры старой рефералки
3. Код замечаний не имеет — только документирование сценариев

Источник: [[zvonok-musohranov-timoshenko-2026-06-24]]

---

## CreateLead → CreateStub Integration (задача 06152561, 2026-06-15)

`ReferralProgram.CreateLead` теперь автоматически создаёт корешок после создания CRM-сделки.

### Поток выполнения

```
CreateLead
  → sbis.CRMLead.insertRecord(...)        # создать сделку → result.Get('@Документ')
  → sbis.ReferralProgram.GetLead(program_id, doc_id, None, partner_id)  # КРИТИЧНЫЙ
  → _get_stub_status_from_events(events)   # маппинг статуса
  → [try] ReferralLeadHistory.commit_new_lead(...)  # НЕКРИТИЧНЫЙ (try/except)
  → _create_stub_for_lead(...)             # КРИТИЧНЫЙ
```

**Принцип**: GetLead и CreateStub — критичные операции, падение = падение метода. Запись в историю — некритичная, оборачивается в `try/except`.

### Маппинг статуса из CRM-событий

`sbis.ReferralProgram.GetLead` возвращает `Record` с полем `Events` (RecordSet от `SourcesSales.GetLeadInfoV2`). Сортировка: от новых к старым, `events[0]` — последнее событие.

Поле `Events.Статус` использует `TransitionResults`: `INWORK=0`, `POSITIVE=1`, `NEGATIVE=2`.

```python
def _get_stub_status_from_events(events) -> tuple[int, str | None]:
    if not events or events.Size() == 0:
        return LinkType.REQUEST_IN_PROGRESS, sbis.rk('В работе')

    last_event = events[0]
    crm_status = last_event.Get('Статус')
    transition_name = last_event.Get('НазваниеПерехода')

    if crm_status == 1:   # POSITIVE
        return LinkType.REQUEST_SUCCESS, str(transition_name) if transition_name else sbis.rk('Завершено положительно')
    if crm_status == 2:   # NEGATIVE
        return LinkType.REQUEST_FAILURE, str(transition_name) if transition_name else sbis.rk('Завершено отрицательно')
    return LinkType.REQUEST_IN_PROGRESS, str(transition_name) if transition_name else sbis.rk('В работе')
```

`НазваниеПерехода` — приоритетный источник `StatusDescription`. `sbis.rk(...)` — только fallback при пустом имени.

### SQL для UUID документа

```sql
SELECT "ИдентификаторДокумента"
FROM "Документ"
WHERE "@Документ" = $1
```

Используется в `_create_stub_for_lead` для получения UUID сделки (`RequestUUID` корешка). Если UUID не найден — `ValueError` (не `sbis.Warning`).

### SqlQueryScalar порядок вызовов в CreateLead

```python
# 1. is_referral_code_exists_for_partner  → True/False
# 2. SQL_GET_REFERRAL_CODE_IDENTIFIER     → referral_code_uuid
# 3. _SQL_GET_LEAD_UUID                   → lead_doc_uuid
```

При мокировании в тестах: `mock.patch('sbis.SqlQueryScalar', side_effect=[True, referral_code_uuid, lead_doc_uuid])`.

### Тестовый паттерн

Новый тест `test_create_lead_creates_stub`:
```python
mock.patch('sbis.ReferralProgram.GetLead') as mock_get_lead,
mock.patch('sbis.ReferralProgram.CreateStub') as mock_create_stub,
mock.patch('sbis.SqlQueryScalar', side_effect=[True, referral_code_uuid, lead_doc_uuid])
# ...
mock_get_lead.return_value = sbis.Record({'LeadNum': lead_num, 'LeadDate': None})
# Assertions:
request.Get('RequestUUID') == str(lead_doc_uuid)
request.Get('RequestNumber') == lead_num   # int, не str
request.Get('Status') == 10               # REQUEST_IN_PROGRESS
```

Остальные 5 тестов CreateLead — добавлены:
```python
mock.patch('sbis.ReferralProgram.GetLead') as mock_get_lead,
mock.patch('priceformationonline.referralprogram.referralprogram.create_lead._create_stub_for_lead')
# setup:
mock_get_lead.return_value = sbis.Record({'LeadNum': None, 'LeadDate': None})
```

---

## Тесты

### CreateStub
- `test_stub_created` — корешок создаётся в ВЦД
- `test_link_type_matches_status` — ТипСвязи соответствует статусу (10/15/20)
- `test_duplicate_operation_id_raises_warning` — дубль → Warning
- `test_partner_not_found_raises_warning` — партнёр не найден → Warning
- `test_status_date_stored_for_any_status` — StatusDate сохраняется для всех статусов
- `test_client_name_stored` — ClientName в Атрибуты
- `test_contact_and_description_fields_stored` — Description/ContactName/Phone/Email/StatusDescription в Атрибуты
- `test_partner_not_member_of_program_raises_warning` — нет карты → Warning

### UpdateStub
- `test_status_updated` — ТипСвязи меняется
- `test_bank_approves_application` — status=15, EffectiveDate сохраняется
- `test_bank_rejects_application` — status=20, EffectiveDate сохраняется
- `test_bank_rolls_back_decision` — откат, EffectiveDate затёрта
- `test_client_name_updated` — ClientName обновляется
- `test_client_name_not_changed_when_none` — None не затирает ClientName
- `test_status_description_updated_in_attributes` — StatusDescription → Events[1].НазваниеПерехода
- `test_not_found_raises_warning` — несуществующий UUID → Warning

### CreateLead (задача 06152561)
- `test_create_lead_creates_stub` — при создании сделки создаётся корешок с правильным RequestNumber (int) и RequestUUID
- Остальные 5 тестов CreateLead — добавлены моки `sbis.ReferralProgram.GetLead` и `_create_stub_for_lead`

### ReadStub
- `test_returns_request_uuid` — UUID заявки
- `test_returns_contractor_id/name` — данные партнёра
- `test_returns_client_name` — имя клиента
- `test_returns_description` — описание заявки
- `test_returns_contact_fields` — ContactName/Phone/Email
- `test_events_has_one_element_when_status_10` — 1 событие при статусе 10
- `test_events_first_element_is_creation` — первое событие: Статус=10, Дата=дата создания, НазваниеПерехода='Заявка создана'
- `test_events_has_two_elements_when_status_not_10` — 2 события при статусе 15/20
- `test_not_found_raises_warning` — несуществующий UUID → Warning
