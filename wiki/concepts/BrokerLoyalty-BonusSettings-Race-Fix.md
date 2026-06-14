---
type: decision
title: "BrokerLoyalty BonusSettings Race Fix"
created: 2026-04-13
updated: 2026-04-13
decision_date: 2026-04-13
status: active
tags:
  - decision
  - loyalty
  - sync
  - offline
  - bugfix
related:
  - "[[Sync-Broker]]"
  - "[[Loyalty-Desktop-Broker-Migration]]"
  - "[[PriceFormation-Backend-Architecture]]"
  - "[[BonusSettings-Sync-Restart-Bug]]"
  - "[[DWC-BonusSettings-Events-Migration]]"
---

# BrokerLoyalty BonusSettings Race Fix

**Task:** https://online.sbis.ru/opendoc.html?guid=b80229fd-d555-41d3-8d0e-3c77eaa0d4ab&client=3

---

## Bug

При включённой фиче `lty_broker_bonus_set` (`Feature.LTY_BROKER_BONUS_SETTINGS`) промокоды, созданные в онлайне, не появлялись в офлайне после «Синхронизации с облаком».

**Воспроизведение:** Розница офлайн 26.2200 → создать промокод в онлайне → «Синхронизация с облаком» в каталоге → панель скидок → поиск промокода → **не найден**.

---

## Root Cause

Гонка на C++ процессном синглтоне `SyncBrokerClient.Instance()`.

Два независимых пути вызывали `SyncBrokerClient.Instance().Sync()` одновременно:

| Триггер | Путь | Что вызывается |
|---------|------|----------------|
| «Синхронизация с облаком» в каталоге | `PFSync.SyncLoyalty` → `_sync_bonus_settings()` | `SyncBrokerClient.Instance().Sync(BonusSettingsSync())` |
| Расписание / авторизация | `PFSync.BrokerSyncLoyalty` → SyncManager | `SyncBrokerClient.Instance().Sync(PromoCodeSync())` |

Конкурентные вызовы `Sync()` разрушали внутренний курсор промокодов. После этого `PromoCode.Sync` не загружал новые записи даже при последующих плановых запусках.

До включения `lty_broker_bonus_set`: `SyncLoyalty` не трогал `SyncBrokerClient` → гонки не было.

**Исторический контекст:** Commit `2651036cd6` создал `BrokerSyncLoyalty` и перенёс `_sync_promocodes()` в него, но `_sync_bonus_settings()` ошибочно оставил в `sync_loyalty.py`. Это нарушило принцип единой точки входа.

---

## Decision

Перенести синхронизацию настроек бонусов из `sync_loyalty.py` целиком в `broker_sync_loyalty.py` (единую точку входа через SyncManager).

**Принцип-правило (вытекает из архитектуры `SyncBrokerClient`):**
> Все вызовы `SyncBrokerClient.Instance().Sync()` для лояльности ДОЛЖНЫ идти только через `PFSync.BrokerSyncLoyalty` / SyncManager. Любой прямой вызов вне SyncManager — потенциальная гонка.

---

## Changes

### `broker_sync_loyalty.py`

- Добавлен импорт `sync as sync_bonus_settings, re_sync as re_sync_bonus_settings`
- `LoyaltyEntity.BONUS_SETTINGS = 'BonusSettings'` (уже был как строка в SyncManager)
- Добавлена функция `_sync_bonus_settings()` с try/except + re_sync
- `LoyaltySynchronizer.PullSync()` обрабатывает `BONUS_SETTINGS`
- `LoyaltySync.sync_init()` регистрирует `LoyaltySynchronizer(LoyaltyEntity.BONUS_SETTINGS)` первым
- `run_broker_sync_loyalty()`: `AddCompletePullRequest(BONUS_SETTINGS)` перед `PROMOCODE`

### `sync_loyalty.py`

- Удалён импорт `bonus_settings_sync`
- Удалён блок `if check_feature(Feature.LTY_BROKER_BONUS_SETTINGS): _sync_bonus_settings()`
- Удалена вспомогательная функция `_sync_bonus_settings()`

### Порядок синхронизации в `BrokerSyncLoyalty` (восстановлен)

```
BonusSettings (if lty_broker_bonus_set)
  → PromoCode
  → Promotion (if lty_broker_promotion)
  → CardEmission (if lty_broker_card)
```

Все четыре обрабатываются последовательно через SyncManager — гонка исключена.

---

## SyncManager Framework

`BrokerSyncLoyalty` использует `offlinesynchronizer.SyncManager` — платформенный фреймворк последовательной офлайн-синхронизации.

```python
from offlinesynchronizer import SyncManager, AbstractSync

# Регистрация (при старте, LoyaltySync.sync_init()):
SyncManager.Instance().AddSync(LoyaltySynchronizer('BonusSettings'))
SyncManager.Instance().AddSync(LoyaltySynchronizer('PromoCode'))
...

# Запуск (в broker_sync_loyalty):
SyncManager.Instance().AddCompletePullRequest('BonusSettings')  # PullAll()
SyncManager.Instance().AddPullRequest('Promotion', filters)      # Pull(filters)
```

`AbstractSync` — интерфейс синхронизатора:
- `Name() → str` — уникальный ключ регистрации
- `Pull(filters: sbis.Record)` — частичная синхронизация (по фильтру)
- `PullAll()` — полная синхронизация

`LoyaltySynchronizer` реализует `AbstractSync` и делегирует каждой сущности:
- `BONUS_SETTINGS` → `sync_bonus_settings()` / `re_sync_bonus_settings()`
- `PROMOCODE` → `sbis.PromoCode.Sync()` / `sbis.PromoCode.ReSync()`
- `PROMOTION` → `sbis.PFSync.PriceEntitySync()` / `sbis.PFSync.PriceEntityReSync()`
- `CARD_EMISSION` → `sbis.PFSync.CardEmissionSync()` / `sbis.PFSync.CardEmissionReSync()`

Документация SyncManager: https://wi.sbis.ru/docs/py/offlinesynchronizer/SyncManager
