---
type: concept
title: "Sync Broker — Reactive Sync & STOMP/PUSH"
updated: 2026-04-10
tags:
  - concept
  - wasaby
  - sync
  - stomp
  - push
  - reactive
status: current
related:
  - "[[Sync-Broker]]"
  - "[[Sync-Broker-Architecture]]"
  - "[[Sync-Broker-Sharding]]"
created: 2026-04-10
---

# Sync Broker — Reactive Sync & STOMP/PUSH

Reactive synchronization: immediate notification of offline apps about cloud changes, minimizing latency.

---

## Overview

As soon as a change is recorded in the cloud broker, the system immediately sends a **STOMP notification** to connected offline apps. This triggers near-instant sync instead of waiting for the next polling interval.

Benefits:
- Saves device resources (battery, CPU)
- Reduces network traffic
- Reduces cloud infrastructure load (fewer polling requests)

---

## Three STOMP Notification Types

### Type 1: Without Body (no-body)

- Contains only the **fact** of a change
- Client broker triggers **regular sync** on receipt
- **Pro**: simple, reliable, near-zero data loss
- **Con**: high cloud load — all consumers hit the cloud for data simultaneously

### Type 2: With Body (inline payload)

- Contains the fact **and the changed data** (payload)
- Client broker applies changes directly to local DB; skips those objects in subsequent regular sync
- **Pro**: data applied immediately, no cloud roundtrip; much lower cloud load
- **Con**: no delivery guarantee; no ordering guarantee
  - Client broker handles out-of-order via object markers, but can't recover lost notifications
  - Periodic regular sync still required

> [!key-insight] Max STOMP body size: **20 KB**. If payload exceeds this, STOMP is sent without body.

### Type 3: With Loadable Body (recommended)

Best of both worlds. Instead of embedding the payload at write time, the **broker itself loads** the data model via a specified BL method after registering the change.

**Problem it solves** (Type 2 race condition):
```
Thread 1: loads data model v1 → sends to broker → queued
Thread 2: loads data model v2 → sends to broker → queued
Result: broker may apply v2 then v1 → wrong state!
```

**Type 3 solution**: broker processes the queue serially per object instance → always loads latest state → assigns correct marker → no ordering issues.

Additional benefits:
- No need to build payload at write time
- Single data model load for multiple changes with same params
- Batch loading supported; auto-splits if too large

---

## Broker Queue DB (Personal Queue Shard)

Input flow through a shard:

```
Incoming changes
    └─► personal queue input (PostgreSQL)
              ├─► STOMP without body       ──► stomp_queue
              ├─► STOMP with inline body   ──► stomp_queue
              └─► STOMP with loadable body ──► task_stomp_exec_queue
                                                    (pipeline: load data model → stomp_queue)
```

---

## Service Interaction Diagrams

### STOMP without body
Cloud → broker registers change → publishes STOMP → client triggers regular sync → cloud loads data

### STOMP with body
Cloud → broker registers change + payload → publishes STOMP with data → client applies directly

### STOMP with loadable body
Cloud → broker registers change + BL method reference → broker loads data → publishes STOMP with data → client applies directly

---

## Integration API

### Sending Changes with STOMP Event

Use `sync_broker_sender.EventTemplate` alongside `BrokerEvent`.

**Constructor parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `name` | str | Event name = STOMP channel name |
| `payload` | Record | `{add: RecordSet, upd: RecordSet, del: ArrayUuid}` |
| `visibility` | `event.Visibility` | `evCLIENT_ONLY` / `evSERVER_ONLY` / `evALL` |
| `application` | str | Target application |
| `applications` | list | Target applications |
| `sites` | list | Take from `Config("Ядро.Асинхронные сообщения.СайтыПодпискиНаСобытия")` |
| `user` | list | User IDs |
| `clients` | list | Client IDs |
| `persons` | list | Profile service person IDs |

Recipients can also be set via `BrokerEvent` methods:
- `SetPublishPerson(UUID)` / `SetPublishPersons([UUIDs])`
- `SetPublishUser(Int64)` / `SetPublishUsers([Int64])`
- `SetPublishClient(Int64)` / `SetPublishClients([Int64])`

### STOMP without body (Python)

```python
import sync_broker_sender
broker_event = sync_broker_sender.BrokerEvent("ObjectType", uuid, "Author")
event_tmpl = sync_broker_sender.EventTemplate(
    name="my_channel.change_object",
    visibility=event.Visibility.evCLIENT_ONLY,
    persons=[person_id],
    sites=sbis.Config.Instance().GetArrayString("Ядро.Асинхронные сообщения.СайтыПодпискиНаСобытия", [])
)
broker_event.SetEvent(event_tmpl)
broker_event.Send()
```

### STOMP with inline payload (Python)

```python
event_tmpl = sync_broker_sender.EventTemplate(
    name="purchases.change_purchase_broker",
    visibility=event.Visibility.evCLIENT_ONLY,
    persons=[person_id],
    application="mobile",
    sites=sbis.Config.Instance().GetArrayString(...),
    payload=payload  # Record with add/upd/del fields
)
broker_event.SetEvent(event_tmpl)
broker_event.Send()
```

### STOMP with loadable body (Python)

```python
event_tmpl = sync_broker_sender.EventTemplate(
    name="test_event.change_object",
    payload_method="ByBLObject.GetPayload",   # BL method to load payload
    payload_service="my-service",              # optional, defaults to sending service
    visibility=event.Visibility.evCLIENT_ONLY,
    ...
)
```

BL method signature for payload loading:
- **Input**: `Record` with `IdObjects` (ArrayUUID)
- **Output**: `Record` with fields matching the payload schema

---

## PUSH Notifications

PUSH and broker change writes are **coupled**: PUSH must not arrive before the change is written to the broker. Use `SetPushConfig(Record)` to define PUSH inline with the change.

```python
push_config = sbis.Record({
    "Type": 1,
    "Канал": sbis.Record({"EMAIL": False, "SMS": False, "STOMP": False, "PUSH": True}),
    "Params": {
        "PlainText": "...",
        "PushMessage": "...",
    }
})
broker_event.SetPushConfig(push_config)
```

### PUSH Aggregation

When multiple methods produce the same PUSH for one functional event, use `AggregationKey`:

```python
push_config = sbis.Record({
    "Type": 1,
    ...,
    "AggregationKey": "my_aggregation_key"
})
```

The aggregation key is excluded from the push record on sending.

---

## Client-Side Rules

When implementing STOMP processing in offline app:

1. Target microservice does NOT process STOMP notifications itself — the client broker part does
2. Microservice registers STOMP channel name with broker client at init
3. Broker client decides whether to trigger regular sync based on:
   - Primary sync for this history object is complete
   - No regular sync currently in progress for this object
   - Sync marker in notification is newer than current context
4. For mass notifications (hundreds+ devices): random delay, max determined by sender
5. While primary or regular sync is running: STOMP notifications for that object are ignored

---

## Use Cases

Most useful for apps that want **partial change filtering** — subscribe only to your channel, react only to your changes. Set specific clients/users/persons as event recipients.
