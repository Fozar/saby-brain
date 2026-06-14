---
type: concept
title: "Sync Broker — System Architecture"
updated: 2026-04-10
tags:
  - concept
  - wasaby
  - sync
  - offline
  - architecture
status: current
related:
  - "[[Sync-Broker]]"
  - "[[Sync-Broker-Sharding]]"
  - "[[Sync-Broker-Reactive]]"
  - "[[Wasaby-Framework]]"
created: 2026-04-10
---

# Sync Broker — System Architecture

Full distributed architecture of the SBIS offline-cloud synchronization system (since v23.3000).

---

## System Components

```
┌─────────────────────────────────────────────────────────┐
│  Cloud                                                  │
│  ┌──────────────┐   ┌─────────────────────────────────┐ │
│  │ Cloud Service│   │  sync-broker (sync-broker-router│ │
│  │ + SDK sender │──▶│  + sync-broker-shard[1..N])     │ │
│  └──────────────┘   └─────────────────────────────────┘ │
│  ┌──────────────┐           │                           │
│  │History Service│──────────┘ (legacy/alternative path) │
│  └──────────────┘                                       │
└─────────────────────────┬───────────────────────────────┘
                          │ STOMP / regular sync
┌─────────────────────────▼───────────────────────────────┐
│  Offline App                                            │
│  SyncBrokerClient + Applied Synchronizer                │
└─────────────────────────────────────────────────────────┘
```

### 1. Облачный брокер синхронизации (`sync-broker`)

Central node for receiving, storing, and distributing change events.

- **Receives**: facts of object changes (not the data itself)
- **Gives out**: identifiers of objects changed since last sync

> [!key-insight] The broker stores only **facts** of changes, NOT the changed data.

### 2. Cloud Service (`+ Sync Broker SDK`)

- Executes business logic (CRUD on sync'd objects)
- Sends change events to broker via `sync_broker_sender.BrokerEvent`
- On sync request: calls broker for changed IDs → loads data models → returns to client

### 3. History Service (legacy path)

Alternative delivery path when there's a large existing codebase already sending to history service. **Deprecated — avoid for new integrations.** ~1 min delay.

### 4. Offline App (`SyncBrokerClient`)

- Module `SyncBrokerClient` orchestrates one-way cloud→offline sync
- See [[Sync-Broker]] for `AbstractSyncHandler` interface

---

## Sync Procedure

Synchronization is **logical replication**: only data relevant to the specific user is synced (not all company documents, only recent/relevant ones).

### Phase 1 — Primary Sync

Goal: initial fill of offline DB.

1. `SyncBrokerClient` calls `FirstSyncMethod()` on online service
2. Online method calls `sbis.SyncBroker.Register(metadata, ...)` — fixes **start cursor**
3. Returns data batch + anchor for next iteration
4. After full load, switches to regular sync from start cursor (captures changes during load)

### Phase 2 — Regular (Incremental) Sync

Goal: keep data current after primary sync.

1. `SyncBrokerClient` passes previous cursor (metadata)
2. Online method calls `sbis.SyncBroker.GetObjectsWithFilter(info)` or `GetObjects(info)` — returns changed UUIDs
3. Online service loads data models for changed UUIDs, returns to client
4. `SyncBrokerClient` saves new cursor for next iteration

---

## Data Architecture

```
Sync object (UUID)
  └─ assigned to personal queue on a shard
       └─ changes stored in PostgreSQL (1 hour, fast)
       └─ then moved to ClickHouse (long-term, 8× compression)
```

Object-to-queue binding is tracked by `sync-broker-router` (object map).

---

## Distributed Architecture (v23.3000+)

Before v23.3000: monolithic single service.
After v23.3000: sharded architecture for horizontal scaling.

Key concepts:
- **Shards** (`sync-broker-shard[1..N]`): nearly identical services, each handles a set of personal queues
- **Router** (`sync-broker-router`): routes requests to the correct shard based on config
- **Personal queues**: isolate objects, reducing mutual interference. Each has its own ClickHouse table.
- **Object map** (on router): history of object movements — enables seamless data loading without copying on shard migration

Regional deployments: `ru-cloud` has max configuration; regional clouds have only one shard (resource saving).

See [[Sync-Broker-Sharding]] for sharding details.
See [[Sync-Broker-Reactive]] for STOMP/PUSH reactive notifications.
See [[Sync-Broker-Management]] for admin interface.
See [[Loyalty-Desktop-Broker-Migration]] for a live migration project using this architecture (Desktop Розница/Presto, ~29 000 copies).
