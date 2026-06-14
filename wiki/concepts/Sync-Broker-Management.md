---
type: concept
title: "Sync Broker — Management & Admin Interface"
updated: 2026-04-10
tags:
  - concept
  - wasaby
  - sync
  - admin
  - operations
status: current
related:
  - "[[Sync-Broker]]"
  - "[[Sync-Broker-Sharding]]"
  - "[[Sync-Broker-Architecture]]"
created: 2026-04-10
---

# Sync Broker — Management & Admin Interface

Admin panel for monitoring and managing the sharded sync broker in "Управление облаком".

URL: `n.saby.ru/cloudctrl/knowledge`

---

## Interface Overview

Two-column registry with a chart. All metrics are calculated per a selected time interval: **Today / Week / Month**.

- Current interval value vs previous interval (+ delta)
- Chart groups by hour (Today) or day (Week/Month)
- Previous interval is capped at the current hour of day

---

## Shard Registry (left panel)

Hierarchy: **Service (shard) → Queue → Object**

Shows aggregate read count per element (shard = sum of all objects on it).

Selecting an element: chart shows read history for that element; right panel shows detailed stats for sub-elements.

---

## Object Registry (right panel)

Depends on selected element in shard registry:

| Selected | Shows |
|----------|-------|
| Shard | Queue → Object hierarchy |
| Queue | Objects in that queue |
| Object | Single object detail |

**Metrics per queue/object:**
- Write count (method call count, not change count)
- Read count
- Avg write time
- Avg read time

**Additional for objects:**
- Unique clients/users reading this object
- Date when object was moved to its personal queue

---

## When to Move Objects

No strict criteria — requires analysis. Consider moving when:
- Critical node/DB stress on one shard that can't be resolved with hardware
- Sharp or sustained increase in load (writes/reads) for an object
- Sharp or sustained increase in load on a shard or personal queue

**To move:** click the object name in the registry → choose target personal queue → confirm. Takes ~10 minutes.

**Movement rules:**
- Cannot move to `old_common_queue` (legacy shard)
- Cannot move to a queue the object was previously bound to
- Avoid moving from 180-day to 7-day retention without strong justification
- Movement history available via "История" button

> [!key-insight] Object migration is a serious operation. Misuse can cause major issues for many users. Only move with full confidence.

---

## Rate Limiting (Emergency Mechanism)

For sudden queue buildups: set a minimum sync interval (in seconds) per object.

**Behavior:**
1. After regular sync completes, a "no-sync-before" timestamp is set
2. New request arrives within limit → deferred; executes immediately after limit expires. Multiple requests during limit → aggregated into one
3. New request arrives after limit → executes immediately

Filter by "rate limited" objects is available in the admin panel.

---

## Personal Queue Naming

```
sbs{ShardNum}_d{RetentionDays}_{ArbitraryPart}
```

| Retention | Use case |
|-----------|----------|
| 180 days | Offline app synchronization |
| 7 days | Inter-service synchronization |

---

## Creating New Queues or Shards

The admin panel does NOT support creating/modifying shards, queues, or objects. Contact:
- **Юрий Думп** — `online.sbis.ru/person/beabaee7-4c56-4154-8010-0f637a1f50eb`
- **Евгений Логвинчук** — `online.sbis.ru/person/450c27e8-a060-41cc-bb9a-65cf29bc4987`

Also contact Логвинчук when you need broker to self-publish STOMP events for history-service-based objects.
