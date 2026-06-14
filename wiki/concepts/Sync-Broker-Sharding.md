---
type: concept
title: "Sync Broker — Sharding Subsystem"
updated: 2026-04-10
tags:
  - concept
  - wasaby
  - sync
  - sharding
  - architecture
status: current
related:
  - "[[Sync-Broker]]"
  - "[[Sync-Broker-Architecture]]"
  - "[[Sync-Broker-Reactive]]"
  - "[[Sync-Broker-Management]]"
created: 2026-04-10
---

# Sync Broker — Sharding Subsystem

Horizontal scaling subsystem for `sync-broker`. Introduced in v23.3000.

---

## Problem

Originally sync-broker was a monolithic service. As object count and event volume grew, the system hit DB performance limits.

---

## Solution: Sharded Architecture

Objects are distributed across **shards** (`sync-broker-shard[1..N]`). For any given object, the shard is always known → minimal load per shard → linear scalability via adding shards.

```
sync-broker-router
    ├── sync-broker-shard-1
    │       ├── personal-queue-A  (PostgreSQL + ClickHouse)
    │       └── personal-queue-B
    ├── sync-broker-shard-2
    │       ├── personal-queue-C
    │       └── personal-queue-D
    └── sync-broker-shard-N
            └── ...
```

---

## Key Architecture Points

- **Personal queues** isolate objects: each queue processes only its bound objects independently
- **PostgreSQL** stores operational data (~1 hour, fast writes/reads)
- **ClickHouse** stores long-term data (8× less memory, much faster for large selects)
- **Object map** (on router): historical binding of objects to queues — enables seamless reads without copying on migration

---

## Routing

### Configuration

- Each router worker has a **local cache** updated every 5 minutes
- Cache loaded from **Redis**; Redis loaded/updated from **router DB**
- When object binding changes: a **timestamp** is set = change time + **10 minutes**
  - This guarantees all workers apply the migration simultaneously

### Write Routing

Router determines the target shard for any incoming write based on the current config.

### Read Routing with Migration History

Thanks to the object map, the router can construct queries spanning multiple shards (before and after migration), loading data without copying.

---

## Router Database Schema

**Service:** `sync-broker-router`

Stores historical binding of sync objects to personal queues. Allows computing where to find changes for a specific object over a specific time interval.

---

## Personal Queue Naming Convention

```
sbs{ShardNum}_d{RetentionDays}_{ArbitraryPart}
```

Examples:
- `sbs1_d180_purchases` — shard 1, 180-day retention
- `sbs2_d7_interservice` — shard 2, 7-day retention

**Retention rules:**
- Offline sync objects: **180 days**
- Inter-service sync objects: **7 days**

> [!key-insight] Always check retention when moving objects between queues. Moving from 180-day to 7-day queue without good reason is undesirable.

---

## Admin Interface

See [[Sync-Broker-Management]] for:
- Shard registry (hierarchy: shard → queue → object)
- Read/write statistics per object
- Object migration between personal queues
- Rate limiting for regular sync

---

## Special Shard: `sync-broker`

The legacy monolithic service still exists as the `sync-broker` shard with a single fictitious queue `old-common-queue`. Contains objects that can't yet be migrated due to old offline clients. Will be decommissioned when old clients die off.
