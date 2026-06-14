---
type: synthesis
address: c-000005
title: "Franchise Card Import — POS SaleValidation Bug"
created: 2026-05-14
updated: 2026-05-14
tags:
  - price-formation
  - discount-card
  - franchise
  - import
  - bugfix
  - dcs
  - pos
status: fixed
related:
  - "[[ImportDiscountCard-Franchise-Client-Import]]"
  - "[[DiscountCard-Subsystem-Overview]]"
  - "[[PriceFormation-Backend-Architecture]]"
---

# Franchise Card Import — POS SaleValidation Bug

## Симптом

После импорта клиентов через `ImportDiscountCard.ProcessFile` (тип карты с `FranchiseRole=2`, эмиссия участника франшизы) — попытка провести продажу на POS участника блокируется с ошибкой:

> «Владелец карты не подтвердил номер телефона»

Лог `GetCardInfo` на POS: `CardId=null`, `ClientId=null`, `FranchiseCardExists=false`, `FranchiseRole=2`, `SaleValidation.Result=false`.

---

## Root Cause

`_process_card_item` вызывает `sbis.DiscountCard.Создать` с флагом `SkipServiceNotification: True` (строка `_create_card` в `process_file.py:697`). Этот флаг предназначен для подавления лишних уведомлений при batch-импорте, но у него есть побочный эффект:

```python
# after_create → create.py:126-127
if not options.SkipServiceNotification and not is_greeting_applied:
    async_notify_changed_cards([created_record.Get('@Карта')])  # ← НЕ вызывается!
```

В итоге сервис `discount-cards` (DCS) на аккаунте **владельца** франшизы никогда не узнаёт о создании карты.

**Цепочка при продаже на POS:**

1. POS → `GetCardInfo` → `get_account_franchise()` возвращает `FranchiseRole=FRANCHISEE`
2. `_import_card_from_franchise()` → `Card.GetInfo` в DCS владельца → карта не найдена
3. `FranchiseCardExists=false`, `CardId=null`, `ClientId=null`
4. SaleValidation: `FranchiseRole is not None AND InCloud AND NOT (ClientId AND PersonUUID)` → блокировка

---

## Fix

**Файл:** `priceformationonline/discountcard/importdiscountcard/process_file.py`

**Место:** `_process_card_item`, после `card.save_client()` и `get_or_create_personal_card_ext`, перед `return card.card_id` (строки 1979–1980).

```python
if card.franchise_role:
    async_notify_changed_cards([card.card_id])
```

`async_notify_changed_cards` уже импортирована (строка 29). `card.card_id` гарантированно не `None` в этой точке (ранний `return None` на строке 1963).

**Почему `async`, а не `sync_notify_changed_cards`:** синхронная версия запрещена в синхронных методах (цикличное обращение в онлайн). Асинхронная публикует событие `'online.loyalty-card.card-data.changed'` в шину → DCS обрабатывает через `Card.HandleChangeData` → создаёт карту в DCS через `ServiceDiscountCard.GetCardPartialInfo`.

---

## Восстановленная цепочка после фикса

1. `card.save()` — карта сохранена в БД онлайн-сервиса
2. `card.save_client()` — клиент привязан к карте
3. `get_or_create_personal_card_ext` — персональный счёт создан
4. **наш фикс** → событие → DCS получает карту
5. POS: `_import_card_from_franchise()` → `Card.GetInfo` в DCS → карта найдена → `cache()` → `CardId` и `ClientId` установлены
6. SaleValidation: `ClientId AND PersonUUID` выполнено → продажа разрешена ✅

---

## Побочное наблюдение: мёртвый код в `_parse_data`

В `_parse_data` (строка 1624-1625) есть вызов `async_notify_changed_cards(cards_id_list)` для batch-нотификации. Он никогда не выполняется, потому что `cards_id_list` инициализируется как `[]` (строка 1583) и результат `_extract_cards_from_data` не присваивается:

```python
self._extract_cards_from_data(data)  # return value discarded!
```

Должно быть: `cards_id_list = self._extract_cards_from_data(data)`. Это отдельный баг — исправлять осторожно, т.к. затронет нотификацию для всех импортируемых карт.

---

## Условия применимости фикса

- `async_notify_changed_cards` возвращается сразу если `not is_cloud_with_dcs()` (строка 45 `notify_changed.py`) — на desktop/offline среде не выполняется
- Фикс применяется для ЛЮБОГО ненулевого `franchise_role` (не только `FRANCHISEE=2`)
- Работает и при создании (`created=True`), и при обновлении (`created=False`) карты

---

## Файлы

| Файл | Роль |
|------|------|
| `priceformationonline/discountcard/importdiscountcard/process_file.py` | **Место фикса** — строки 1979-1980 |
| `priceformationonline/dcservice/servicediscountcard/notify_changed.py` | `async_notify_changed_cards` |
| `priceformationonline/discountcard/discountcard/create.py` | `after_create` — строка 126-127, где `SkipServiceNotification` блокирует нотификацию |
| `priceformationcommon/discountcard/discountcard/get_card_info.py` | `_import_card_from_franchise` — строки 1257-1335 |
