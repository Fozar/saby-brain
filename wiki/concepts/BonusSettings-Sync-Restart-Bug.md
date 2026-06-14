---
type: decision
address: c-000050
title: "BonusSettings Sync Restart Bug"
created: 2026-05-18
updated: 2026-05-18
decision_date: 2026-05-18
status: shelved
tags:
  - decision
  - loyalty
  - sync
  - offline
  - bugfix
related:
  - "[[Sync-Broker]]"
  - "[[BrokerLoyalty-BonusSettings-Race-Fix]]"
  - "[[Loyalty-Desktop-Broker-Migration]]"
---

# BonusSettings Sync Restart Bug

**Task:** https://online.sbis.ru/opendoc.html?guid=d80dabab-4d71-49ed-a8c0-54d08c246e0c&client=3
**Feature flag:** `lty_broker_bonus_set` / `Feature.LTY_BROKER_BONUS_SETTINGS`
**Status:** fix готов, в shelf (не закоммичен)

---

## Bug

При включённой фиче `lty_broker_bonus_set` после закрытия и повторного открытия офлайн Desktop Розница `Discount.GetBonusSettings` возвращает устаревшие данные (данные первого входа).

**Работает:** без флага; с флагом пока приложение открыто (STOMP реактивная синхронизация).
**Не работает:** только на перезапуске приложения.

---

## Root Cause

`AddCompletePullRequest(BONUS_SETTINGS)` → `PullAll()` → `PullSync(filters=None)` → `_sync_bonus_settings()` → `sync_bonus_settings()` — **обычный delta-sync**.

Delta-sync с существующим курсором вызывает `BonusSettingsRegularSync` → `GetObjects(info)` → возвращает данные только если в брокере есть события после курсора. Если изменение произошло пока приложение было закрыто и STOMP-уведомление пропущено при reconnect — брокер вернёт пустой список → локальная БД не обновится.

**Асимметрия с PROMOTION:** для PROMOTION `PullAll()` → `PriceEntityReSync()` — сбрасывает курсор → `SyncBrokerClient` видит отсутствие курсора → вызывает `FirstSyncMethod()` → `BonusSettingsFirstSync` → `sbis.Bonus.ReadSettings()` **безусловно** → всегда актуальные данные. BONUS_SETTINGS лишён этой семантики.

---

## Decision

При `PullAll()` (полная синхронизация, вызывается на рестарте) — сбрасывать курсор через `re_sync()`. При `Pull(filters)` (дельта) — оставить `sync()`.

---

## Changes

**`broker_sync_loyalty.py`** — единственный изменённый файл (`sync_settings.py` не трогаем):

### 1. Новая функция `_re_sync_bonus_settings()`

```python
def _re_sync_bonus_settings():
    """Сбросить курсор и пересинхронизировать настройки бонусов"""
    try:
        re_sync_bonus_settings()
    except Exception:
        sbis.ErrorMsg(traceback.format_exc())
```

### 2. `LoyaltySynchronizer.PullSync` — дифференциация PullAll vs Pull

```python
# БЫЛО:
if self.name == LoyaltyEntity.BONUS_SETTINGS:
    _sync_bonus_settings()

# СТАЛО:
if self.name == LoyaltyEntity.BONUS_SETTINGS:
    if filters is None:
        _re_sync_bonus_settings()   # PullAll → reset cursor → FirstSync → всегда свежие данные
    else:
        _sync_bonus_settings()      # Pull → delta
```

`re_sync_bonus_settings` уже импортирован (строка 39–40).

### 3. Тест (`tests_priceformationoffline/sync/pfsync/broker_sync_loyalty.py`)

```python
self._full_sync_methods[LoyaltyEntity.BONUS_SETTINGS] = f'{_IMPL_PATH}.re_sync_bonus_settings'
```

---

## Pattern

Симметрия с PROMOTION после фикса:

| Entity | Pull(filters) | PullAll() |
|--------|---------------|-----------|
| BONUS_SETTINGS | `sync_bonus_settings()` — delta | `re_sync_bonus_settings()` — reset + FirstSync |
| PROMOTION | `PriceEntitySync()` | `PriceEntityReSync()` |
| PROMOCODE | `PromoCode.Sync()` | `PromoCode.Sync()` (не дифференцирован) |
| CARD_EMISSION | `CardEmissionSync()` | `CardEmissionSync()` (не дифференцирован) |
