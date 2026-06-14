---
type: concept
address: c-000057
title: "ReferralProgram.GetPartnerList — партнёры без реферального кода"
created: 2026-05-22
updated: 2026-05-22
tags:
  - price-formation
  - referral-program
  - backend
  - sql
status: completed
related:
  - "[[ReferralDeals-System]]"
  - "[[ReferralProgram-Module]]"
  - "[[Price-Formation-Test-Runner]]"
  - "[[SabyBank-RKO-Referral]]"
  - "[[PostgreSQL-CTE-Cursor-Pushdown]]"
---

# ReferralProgram.GetPartnerList — партнёры без реферального кода

## Задача

На вкладке **Партнёры** детальной страницы реферальной программы отображались только партнёры, для которых уже был вызван `ReferralProgram.Join` (т.е. создан реферальный код в таблице `Карта`). Нужно показывать **всех**, кто принял приглашение в реферальную сеть (`InviteStatus=ACCEPTED`), — даже до вызова `Join`. Это позволяет задавать индивидуальные вознаграждения заранее.

**Файлы:** `referralprogram/referralprogram/get_partner_list.py`

---

## Ключевые решения

### 1. Источник "принятых" партнёров — AgentContract.ContractorList

```python
member_list = ReferralBusinessGroup(to_uuid(agent_group_id)).get_member_list(
    invite_status=MemberStatus.ACCEPTED
)
partner_id_to_name = {
    m.Get('Контрагент'): m.Get('Контрагент.Название')
    for m in member_list
    if m.Get('Контрагент') is not None
}
```

`Контрагент` = `@Лицо` в схеме клиента. Метод `get_member_list` вызывает `AgentContract.ContractorList` с `iterative_list=True`.

### 2. SearchString фильтруется в Python, а не в SQL

Причина: для партнёров без реферального кода имя не хранится в `Карта.Атрибуты` → SQL-фильтр `ILIKE` на `c."Атрибуты"` вернул бы NULL и исключил их.

```python
if search_string:
    search_lower = search_string.lower()
    partner_id_to_name = {pid: name for pid, name in partner_id_to_name.items()
                          if name and search_lower in name.lower()}
```

### 3. SQL: CTE AcceptedPartners + LEFT JOIN вместо INNER JOIN

**Было:** базовая таблица — `Карта` (только партнёры с кодом).

**Стало:**

```sql
WITH "AcceptedPartners" AS (
    SELECT unnest(!AllAcceptedPartnerIds::INT[]) AS "Лицо"
)
SELECT
    (c."Атрибуты"->'ReferralProgram'->>'AdObject')::INTEGER  "AdObject"
,   (c."Атрибуты"->'ReferralProgram'->>'PartnerName')::TEXT  "Name"
,   ap."Лицо"                                                "PartnerId"
,   coalesce(
        (c."Атрибуты"->'ReferralProgram'->>'PricePerLead')::NUMERIC(32,2),
        (pt."Атрибуты"->'ReferralProgram'->>'PricePerLead')::NUMERIC(32,2)
    )  "PricePerLead"
...
FROM "AcceptedPartners" ap
JOIN "ВидЦены" pt ON pt."@ВидЦены" = !ReferralProgramId::INTEGER
LEFT JOIN "ВидЦеныВидКарты" ptct ON ptct."ВидЦены" = !ReferralProgramId::INTEGER
LEFT JOIN "Карта" c
    ON c."Эмиссия" = ptct."ВидКарты"
    AND c."Лицо" = ap."Лицо"
    AND c."$Черновик" IS NULL
    AND c."Заблокировано" = false
```

Партнёры без кода: `c` = NULL, `AdObject` = NULL, цены берутся из `pt` (программа по умолчанию).

### 4. Курсор навигации: AdObject → PartnerId

Старый курсор `AdObject` не подходит для партнёров без кода (NULL). Новый:

```python
[NavField('ap."Лицо"', 'PartnerId', 'INTEGER')]
```

### 5. Заполнение Name из агентского договора (Python-постобработка)

```python
for record in result:
    if not record.Get('Name'):
        record.Set('Name', partner_id_to_name.get(record.Get('PartnerId')))
```

Безопасно: `record.Set()` не меняет формат RecordSet, ссылка `record` не передаётся в замыкание.

### 6. Фильтр DateEnd для партнёров без кода

```sql
{% item ifnotnull DateEnd %}
    (c."@Карта" IS NULL OR c."ДатаНач" <= !DateEnd::date)
{% enditem %}
```

`c."$Черновик" IS NULL` и `c."Заблокировано" = false` — перенесены в ON-условие LEFT JOIN (иначе отфильтровали бы строки с NULL `c`).

---

## Тесты

**Файл:** `tests/tests_priceformationonline/referralprogram/referralprogram/get_partner_list.py`

**Изменения:**
- В `setUp` добавлен мок `ReferralBusinessGroup` с хелпером `_set_accepted_partners([partner1, partner2, ...])`
- Во все тесты добавлены `AgentGroupId` в фильтр и вызов `_set_accepted_partners`
- Новый тест **`test_partner_without_referral_code`**: партнёр есть в ContractorList, но `Join` не вызывался → должен появиться в результате с `AdObject=NULL`, именем из агентского договора, ценами из программы

```
Ran 11 tests in 0.422s — OK
```

---

## Поля AgentContract.ContractorList (справка)

| Поле | Тип | Описание |
|------|-----|---------|
| `Контрагент` | Связь | `@Лицо` в схеме клиента |
| `Контрагент.Название` | Строка | Название |
| `ClientID` | Int32 | Облачный идентификатор |
| `Face` | Int32 | `@Лицо` (явный алиас) |
| `РП.InviteStatus.Status` | Int32 | 1=принял, 2=отправлено, 3=отклонил |

Фильтр `ФильтрПоМаске` — поиск по имени внутри ContractorList (не используется в этой задаче, т.к. SearchString обрабатывается в Python до вызова).
