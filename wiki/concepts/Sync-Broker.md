---
type: concept
title: "Sync Broker (Wasaby Offline-Cloud Sync)"
updated: 2026-04-10
tags:
  - concept
  - wasaby
  - sync
  - offline
  - middleware
status: current
related:
  - "[[Wasaby-Framework]]"
  - "[[price-formation/_index]]"
  - "[[Sync-Broker-Architecture]]"
  - "[[Sync-Broker-Sharding]]"
  - "[[Sync-Broker-Reactive]]"
  - "[[Sync-Broker-Management]]"
  - "[[Wasaby-Sync-Broker]]"
created: 2026-04-10
---

# Sync Broker

System for simplifying, optimizing, and standardizing synchronization between offline app and cloud.

Components: cloud service `sync-broker` + client module `SyncBrokerClient` (offline side).

**Full platform docs:** https://online.sbis.ru/page/knowledge-bases/694fcc5c-abd7-4c2b-9c9b-761e1fdc92fb

---

## Core Principle

Broker answers: "What objects changed since last sync?" The broker stores only **identifiers** of changed objects. The applied cloud service builds the full data model from those IDs.

---

## Sync Types

### Primary Sync (first time)

1. `SyncBrokerClient` calls `FirstSyncMethod()` on online service
2. Online method calls `sbis.SyncBroker.Register(metadata, ...)` - registers client, fixes **start cursor**
3. Returns data portion + anchor for next iteration
4. After all data loaded, switches to regular sync using start cursor (captures changes during initial load)

### Regular Sync

1. `SyncBrokerClient` passes previous iteration metadata (cursor)
2. Online method calls `sbis.SyncBroker.GetObjectsWithFilter(info)` or `GetObjects(info)` - returns changed UUIDs
3. Online method loads data models for changed UUIDs, returns to client
4. `SyncBrokerClient` saves new metadata (cursor) for next iteration

---

## Key Classes (Offline)

### `AbstractSyncHandler`

```python
from sync_broker import AbstractSyncHandler, SyncBrokerClient
```

Required methods:

| Method | Returns | Description |
|--------|---------|-------------|
| `FirstSyncMethod()` | `str` | Online method name for primary sync |
| `RegularSyncMethod()` | `str` | Online method name for regular sync |
| `HistoryObject()` | `str` | Object type in broker; **must match** `object_type` in online metadata |
| `HistoryService()` | `str` | `'broker'` (direct) or `'history'` (history service, ~1 min delay) |
| `Service()` | `str` | Online service name |
| `Filter()` | `sbis.Record` | Filter passed to online method |
| `Limit()` | `int` | Batch size (records per iteration) |
| `AddObjects(records)` | - | Process added objects |
| `UpdObjects(records)` | - | Process changed objects |
| `DelObjects(ids)` | - | Process deleted objects |

### `SyncBrokerClient`

> [!key-insight] Critical: Process Singleton
> `SyncBrokerClient.Instance()` is a **process singleton**. Never call `Sync()` concurrently from multiple threads for different handlers - causes state races and sync corruption. All calls must be **sequential in one place**.

```python
SyncBrokerClient.Instance().Sync(MyHandler())      # run sync
SyncBrokerClient.Instance().ResetSync('MyObject')  # reset cursor for object
```

Stores cursor **separately per `HistoryObject`** in local DB.

---

## Sending Changes to Broker (Online Side)

### Via history service (~1 min delay)

```python
sbis.HistoryMsg("Message", "Action", "ObjectType", guid, sbis.Record({"a_sh": value}))
```

### Direct send

```python
import sync_broker_sender

broker_event = sync_broker_sender.BrokerEvent("ObjectType", uuid, "Author")
broker_event.SetShortAnalytic(1)   # a_sh
broker_event.SetBigAnalytic(1001)  # a_bg
broker_event.SetPublishPolicy(sync_broker_sender.PublicationPolicy.ppON_REQUEST_FINISH)
broker_event.Send()
```

---

## API Variants

| Method | Filter | Result |
|--------|--------|--------|
| `GetObjects(info)` | None | `Record` with `ids`, `metadata` |
| `GetObjectsWithFilter(info)` | By analytics (`a_sh`, `a_bg`, `a_st`) | `RecordSet` with `id`, `mark`, `outcome` |

---

## Usage in price-formation

| Sync Object | HistoryObject | Offline Handler | Online Methods |
|-------------|--------------|-----------------|----------------|
| Promo codes | `Промокоды` | `PromoCodeSync` | `PromoCode.FullSync` / `PromoCode.RegularSync` |
| Bonus settings | `BonusSettings` | `BonusSettingsSync` | `PFSync.BonusSettingsFirstSync` / `PFSync.BonusSettingsRegularSync` |

**Entry point:** `PFSync.BrokerSyncLoyalty` (`broker_sync_loyalty.py`) - single entry point for all loyalty broker syncs.
- Called on auth (`desktop.user-authenticated`, `desktop.local-user-authenticated`)
- Called by scheduler every 10 minutes
- Sequential order: bonus settings (if `lty_broker_bonus_set`) → promo codes → promotions (if `lty_broker_promotion`) → card emission (if `lty_broker_card`)

**Why single method:** SyncBrokerClient singleton + concurrent Sync() calls = state race = lost promo codes. Lesson learned.
- Конкретный пример: `lty_broker_bonus_set` включила `SyncLoyalty` → `Sync(BonusSettingsSync())` параллельно с `BrokerSyncLoyalty` → `Sync(PromoCodeSync())` → курсор промокодов сломан. Fix: [[BrokerLoyalty-BonusSettings-Race-Fix]].

**SyncManager framework:** `BrokerSyncLoyalty` использует `offlinesynchronizer.SyncManager` — гарантирует последовательную обработку зарегистрированных синхронизаторов (`AbstractSync`). `LoyaltySynchronizer(name)` реализует `AbstractSync`: `Pull(filters)` и `PullAll()` делегируют нужному handler'у по `name`. Регистрация при старте: `LoyaltySync.sync_init()` → `SyncManager.Instance().AddSync(...)`.

## Связанные страницы

- [[Wasaby-Sync-Broker]] — облачный брокер синхронизации (платформенная перспектива: факты изменений, STOMP-уведомления)
- [[Sync-Broker-Architecture]] — детальная архитектура: 4 компонента, primary/regular sync, PG→CH
- [[Sync-Broker-Sharding]] — шардирование: роутер, личные очереди, алгоритм кэша маршрутов
- [[Sync-Broker-Reactive]] — реактивная синхронизация: 3 типа STOMP (no-body/inline/loadable)
