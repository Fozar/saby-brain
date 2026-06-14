---
type: concept
title: "Wasaby Framework"
updated: 2026-04-10
tags:
  - concept
  - wasaby
  - sbis
  - architecture
status: current
related:
  - "[[Multitenancy-Architecture]]"
  - "[[DWC-Distributed-Workflow-Coordinator]]"
  - "[[Sync-Broker]]"
  - "[[price-formation/_index]]"
created: 2026-04-10
---

# Wasaby Framework

Platform with cloud infrastructure, frontend framework, and service framework. Backend runs on C++ and Python. Client-server protocol: JSON-RPC.

---

## Project Structure (3 Levels)

| Level | File | Description |
|-------|------|-------------|
| Application | `.s3cld` | Full app; lists services in `<items>` |
| Service | `.s3srv` | BL-service or UI-service; can inherit from parent service |
| Module | `.s3mod` | Minimal functional unit; BL or UI |

**Internal links use UUID, not just names.**

Service inheritance: child service = its own modules + parent service modules.

---

## Resource Types

| Extension | Purpose |
|-----------|---------|
| `dicx` | DB tables (declarative, merged across modules) |
| `orx` | BL objects and methods |
| `trg` | Trigger functions |
| `cnv` | DB converter extensions |
| `uax`, `rlx` | Access zones and roles |
| `aorx` | Applied objects |
| `pagex` | UI pages |
| `navx` | Navigation |
| `feature` | Feature flags |
| `schedule` | Scheduler tasks |

> [!key-insight] Agent tip
> Look for the declarative resource description first, then find the code that implements or uses it.

**Module description merge strategies:**
- **Extension** - description supplements from other modules
- **Replace** - later description replaces earlier (typical for `orx`)
- **Prohibition** - merge forbidden (used in `dwc`)

---

## Service Module Details

- Minimum server-side functional unit. Usually C++ and/or Python. Described by `s3mod`.
- Binary libraries go in the module root directory. Main library declared in `Library` attribute.
- Dependencies: `depends` (hard) vs `load_after` (soft, order only).

**Lifecycle events:** `OnEndLoadModules`, `OnEndAllLoadModules`, `OnCleanup`, `OnCheck`, `OnUnload`

**BL method access levels:** Internal / Trusted Application Contract / Internal Application Contract / Service Contract / Public Service Contract

**Python in modules:** requires platform modules `Python`, `Python Core`, `BL Python`. Use `sbis.Config` for config parameters with hierarchical dot-separated names.

---

## Cloud Architecture

Three software layers:
1. System software (PostgreSQL, Redis, RabbitMQ, nginx)
2. Application services (code executed on demand)
3. Cloud management (structure inspection, clusters, logs, queues)

**Web service types:**
- `simple` - multiple equal nodes, 2 request pools (main + service with `?srv=1`)
- `multiversion` - one URL, multiple implementations (version groups with own `group-id`)
- `multitenancy` - multiversion variant; isolation by tenant; tenant-groups share nodes and serve multiple DBs

**Async calls:** via RabbitMQ. Main queue (ready) vs deferred queue (delayed). On dequeue, service checks version/route currency.

**Event subsystem:** producer / broker / consumer. Events via RabbitMQ. Sender does not need to know specific receiver - publishes to exchange, delivered via bindings. Queues: user (RAM) or BL (durable/transient).

---

## Distribution Scheme

Main service is `online`. Structure:
- `online32` + `online64` = `online` (base BL)
- `online-ps` = base UI
- Regional: `online-bl-ru` / `online-ui-ru`, `online-bl-kz` / `online-ui-kz`
- `online-ru` = `online` + `online-bl-ru`

**Rules:**
- Common modules go into `online32` or `online-ps`
- Country-specific modules go into `online-bl-ru` / `online-ui-ru` etc.
- Never add modules directly to `online[-ps]-ru` or `online[-ps]-kz`
- Tensor cabinet, demo, trial have their own special distributions - use those packages

---

## Useful Platform Services

| Service | Purpose |
|---------|---------|
| `dwc` | Distributed scenarios - see [[DWC-Distributed-Workflow-Coordinator]] |
| DB access | IStatement, SqlQuery, async queries, LISTEN/NOTIFY, bulk ops, SQL templates — see [[Wasaby-DB-Access-Patterns]] |
| `scheduler` | Scheduled tasks |
| `cache-service` | Cache |
| `history` / `input-history` | History |
| `parameters` | Multi-level parameters |
| `prefetch` | Save list method results |
| `event-aggregator` | Client event aggregation |
| `file-transfer` | Deliver method results as files |
