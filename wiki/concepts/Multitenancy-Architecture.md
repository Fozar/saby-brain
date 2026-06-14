---
type: concept
title: "Multitenancy Architecture (Wasaby)"
updated: 2026-04-10
tags:
  - concept
  - wasaby
  - multitenancy
  - architecture
  - postgresql
status: current
related:
  - "[[Wasaby-Framework]]"
  - "[[price-formation/_index]]"
created: 2026-04-10
---

# Multitenancy Architecture (Wasaby)

One server instance serves one MT-application. That application simultaneously serves many client instances. Each instance belongs to one client. A client can have multiple users.

---

## Core Principles

| Requirement | Meaning |
|-------------|---------|
| Isolation | Client data and configs must not affect each other |
| Multi-versioning | Different clients can run different app versions |
| Scalability | Cheap to grow by load, data, functionality |
| Minimal downtime | Updates affect specific client, not all |
| Fault tolerance | Minimal non-redundant nodes |
| Dev compatibility | MT and personal modes must be close |

---

## Data Isolation Model

> [!key-insight] Fundamental rule
> **1 client = 1 PostgreSQL schema.** Isolation via `SET search_path = <user_schema>, public`.
> Cross-client foreign keys are **absolutely forbidden** - not a preference, a hard rule.

- Large client may get a dedicated DB.
- One DB can host many client schemas (count depends on client size).
- Do not create extra DBs without reason.

**Where to store client data:**
- In MT-DB client schema: data belongs to one client, accessed frequently, needs fast response
- In separate service: data relates to multiple clients, feature used by few clients, empty tables in every schema would be wasteful

---

## Request Flow

```
1. User authenticates
2. Session → Redis/keyDB
3. Dispatcher finds service by URL
4. By clientID + service → client route
5. Request → correct BL version
6. BL → PostgreSQL via pgBouncer
```

**Route** = link between `client -> service -> specific app version`. Route determines which app version and which DB a client uses.

**Session ID** contains: `clientID + userID + authID + rndID`

---

## Routing Concepts

- `service` - logical product for client
- `application` - specific service version (specific static, BL, DB versions)
- `route` - client-to-application binding

---

## Update Operations

| Operation | Steps |
|-----------|-------|
| Route change | Update routing table record; reset session cache entries. Atomic per client. |
| Static update | Deploy new static; update `staticID` in route and cache |
| BL update | Deploy new BL; update `BLID` in route and cache |
| Data conversion | Block `DBID` in routing; convert client schema; update `DBID` in route and cache |
| DB server migration | Create schema on new server; block client access; wait for sync; switch route |

---

## Cross-Client BL Calls

Calling a BL method in a different client account while maintaining user context requires explicit re-authentication — the user's session only grants access to their own schema.

> [!important] Пользователь имеет доступ только к схеме своего аккаунта
> Одного ID персоны недостаточно — нужно найти конкретный `userID` в целевой схеме и авторизоваться под ним.

**Паттерн:** `AuthByClientAndUserId(client_id_2, user_id_2)` → `EndPoint('online', auth_data=...)`

**Не использовать** `CreateMultitenantEndpointByClientId` напрямую — он не переключает пользователя.

Подробности, workarounds и проблема петель вызовов: [[Wasaby-Cross-Client-BL-Call]]
