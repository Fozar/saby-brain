---
type: concept
address: c-000006
title: "ImportDiscountCard — Franchise Client Import Architecture"
created: 2026-05-14
updated: 2026-05-14
tags:
  - price-formation
  - discount-card
  - franchise
  - import
  - persona
status: developing
related:
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[Loyalty-Desktop-Broker-Migration]]"
  - "[[PriceFormation-Backend-Architecture]]"
  - "[[Wasaby-Python-Patterns]]"
  - "[[FranchiseCard-Import-POS-SaleValidation-Bug]]"
  - "[[ImportDiscountCard-DCS-Counter-Bug]]"
---

# ImportDiscountCard — Franchise Client Import Architecture

Entry point: `ImportDiscountCard.ProcessFile` → `FileParser` в  
`priceformationonline/discountcard/importdiscountcard/process_file.py`

---

## Key Classes

**`Item`** (namedtuple) — одна строка Excel: `key, fio, mobile_phone, email, address, gender, birth_day, card, card_date, bonus, amount, visits`

**`Client`** — клиент (ЧастноеЛицо):
- `__slots__`: `id_`, `fio`, `mobile_phone`, `old`, `new`, `_old_mobile_phone`
- `get_instance(fio, mobile_phone)` → `CRMClients.GetCustomerByParams`; возвращает `Client` (с `id_=None` если не найден)
- `save()` → создаёт/обновляет клиента в CRM

**`Card`** — карта (запись таблицы `Карта`):
- `__slots__`: `card_id`, `number`, `emission`, `franchise_role`, `old`, `new`
- `get_instance(number)` → `DiscountCard.GetCardInfo` с `IncludedData=['Card','Type','Client','Bonus','SaleStats','Franchise']` и `IsRawInput=True`
- `franchise_role` приходит напрямую из результата `GetCardInfo` — определяется по эмиссии, даже если карта ещё не существует в БД

---

## `_parse_client` flow (lines 1866–1905)

```
Client.get_instance(fio, phone)         # ищем по ФИО+телефон
  → не найден → get_instance(fio, None)  # ищем только по ФИО
    → если найденный клиент без телефона → используем его + добавляем телефон
client.update(email/address/gender/birth_day)
client.save()                           # создаём/обновляем в CRM
```

В `Client.save()` два пути:

| Условие | Метод CRM | Создаёт персону? |
|---------|-----------|-----------------|
| `mobile_phone` + `FranchiseBusinessGroup.get_list()` не пуст + не demo | `CRMClients.CreateCustomerWithConfirmedPerson` | Да (подтверждённая) |
| Иначе | `CRMClients.GetCustomerOrCreate` с `CreatePersonUUID=True` | Да (обычная) |

Оба метода возвращают `SearchResult.CustomerID` — так устанавливается `client.id_`.

---

## `_parse_card` flow (lines 1907–1983)

```
Card.get_instance(item.card)            # GetCardInfo; franchise_role из DB
if not card.emission → ошибка "без эмиссии"

# Франшизный guard:
if card.franchise_role:
    if not client → ошибка "нет клиента"
    if not client.mobile_phone → ошибка "нет телефона"  # ← ранний выход!

card.update(bonus/client/amount/visits/date)
card.save()                             # создаём/обновляем карту
card.save_client()                      # привязываем клиента к карте

# Создание персонального счёта для франшизных карт:
if card.franchise_role and client and client.id_:
    get_or_create_personal_card_ext(client.id_)
```

---

## Различие: персональная карта vs CRM-персона

| Функция | Что создаёт |
|---------|------------|
| `get_or_create_personal_card_ext(client_id)` | Персональный счёт в price-formation (`Карта` с типом PersonalCard) |
| `attach_person_to_client(client_id)` → `CRMClients.AttachPersonId` | CRM-персона (ЧастноеЛицо → PersonId в sbis-admin-api) |

Для обычного импорта персона создаётся через `CreateCustomerWithConfirmedPerson` или `GetCustomerOrCreate(CreatePersonUUID=True)`.  
Для франшизного импорта — через `CreateCustomerWithConfirmedPerson`.  
`get_or_create_personal_card_ext` в `_parse_card` создаёт только loyalty-счёт, CRM-персону не трогает.

---

## Файлы

| Файл | Роль |
|------|------|
| `priceformationonline/discountcard/importdiscountcard/process_file.py` | Основная логика импорта |
| `priceformationonline/discountcard/discountcard/set_for_client.py` | `attach_person_to_client`, `AttachPersonId` |
| `priceformationcommon/discountcard/personalcard/core/core.py` | `get_or_create_personal_card_ext` |
| `priceformationonline/loyaltyprograms/loyaltyprogram/agent_group.py` | `FranchiseBusinessGroup.get_list()` |
| `tests/tests_priceformationonline/discountcard/importdiscountcard/process_file.py` | Тесты (ClientTest, ProcessFileNew) |

---

## Тестовое покрытие

- `test_franchise_triggers_personal_ext` — проверяет что `get_or_create_personal_card_ext` вызывается при `FranchiseRole=1`; использует уже существующего клиента (`id_=123`)
- `ClientTest` — тесты `Client.save()` с mock'ами `CreateCustomerWithConfirmedPerson` и `GetCustomerOrCreate`

---

## Известный баг: карта недоступна на POS после импорта

После импорта франшизной карты (`franchise_role != None`) продажа на POS участника блокируется («не подтвердил номер телефона»).

**Root cause:** `SkipServiceNotification: True` в `_create_card()` блокирует `async_notify_changed_cards` → DCS владельца не знает о карте → `_import_card_from_franchise()` на POS возвращает `FranchiseCardExists=false`.

**Fix (строки 1979-1980):** добавить явный вызов после `save_client()`:
```python
if card.franchise_role:
    async_notify_changed_cards([card.card_id])
```

Подробности: [[FranchiseCard-Import-POS-SaleValidation-Bug]]

---

## Потенциальная проблема (наблюдение, не подтверждённый баг)

При `CreateCustomerWithConfirmedPerson` в логах профилирования наблюдался:
```
Transaction is aborted!  (×2)
ROLLBACK TO SAVEPOINT "Before create link Type_folder=1"
```

Savepoint откатывает создание связи с папкой типа (Type_folder=1), но не создание самого клиента и не внешний RPC `User.CreatePrivatePerson`. Итог: клиент создаётся, private person создаётся во внешнем сервисе, но локальная связь (PersonId в ЧастноеЛицо) может отсутствовать. При воспроизведении бага оказалось, что проверка проводилась на другом стенде — баг не подтверждён.