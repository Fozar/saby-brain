---
type: source
title: "Sync Broker Deep Dive — Architecture, Sharding, Reactive Sync"
ingested: 2026-04-10
tags:
  - source
  - wasaby
  - sync
  - sharding
  - stomp
status: ingested
related:
  - "[[Sync-Broker]]"
  - "[[Sync-Broker-Architecture]]"
  - "[[Sync-Broker-Sharding]]"
  - "[[Sync-Broker-Reactive]]"
  - "[[Sync-Broker-Management]]"
created: 2026-04-10
updated: 2026-04-10
---

# Source: Sync Broker Deep Dive

**Batch:** 12 files from `raw/` — complete sync broker documentation set

## Files Ingested

| File | Content |
|------|---------|
| `Облачный брокер синхронизации.md` | Top-level overview of sync-broker |
| `Концепт решения и архитектура.md` | General system architecture (4 components, primary/regular sync) |
| `Подсистема шардирования брокера синхронизации.md` | Sharding subsystem overview |
| `Концепт решения и архитектура 1.md` | Sharding architecture: shards, router, personal queues, PG→CH |
| `Алгоритмы и процессы 1.md` | Routing cache algorithm (5-min local → Redis → DB), migration timing |
| `База данных 1.md` | `sync-broker-router` DB schema (historical object-queue bindings) |
| `Реактивная синхронизация.md` | Reactive sync overview |
| `Концепт решения и архитектура 2.md` | STOMP types: no-body / with-body / loadable-body |
| `Алгоритмы и процессы 2.md` | STOMP notification algorithms, PUSH with aggregation key |
| `База данных 2.md` | Shard DB: input queue → stomp_queue / task_stomp_exec_queue |
| `Как встраивать (API подсистемы).md` | Full integration API with C++ and Python examples |
| `Управление брокером синхронизации.md` | Admin UI, metrics, object migration, rate limiting |

## Key Insights

- **Three STOMP types** — no-body (reliable), inline-body (fast, lossy), loadable-body (recommended: serial processing guarantees correct ordering even with concurrent writes)
- **Routing timestamp** = change time + 10 min — ensures all router workers apply migration simultaneously
- **PostgreSQL 1hr → ClickHouse** — ops data fast in PG; long-term 8× compressed in CH
- **PUSH is coupled to broker write** — prevents push arriving before data is recorded
- **STOMP body limit**: 20KB; auto-degraded to no-body if exceeded
- **Shard `sync-broker`** = legacy monolith (old clients, `old-common-queue`)
- **Rate limiting** — emergency mechanism for sudden queue buildups; aggregates requests during limit
